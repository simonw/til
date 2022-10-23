# Simple load testing with Locust

I've been using [Locust](https://locust.io/) recently to run some load tests - most significantly [these tests](https://github.com/simonw/django_sqlite_benchmark/issues?q=is%3Aissue+is%3Aclosed) against SQLite running with Django and [this test](https://github.com/simonw/datasette-gunicorn/issues/1) exercising Datasette and Gunicorn.

## A really basic test

Locust tests are defined in a `locustfile.py` file. Here's the most basic possible test, which sends requests to the `/` page of a web application:

```python
from locust import HttpUser, task

class Page(HttpUser):
    @task
    def index(self):
        self.client.get("/")
```

## The web interface

With this saved as `locustfile.py` you can run it in two ways. You can start a web interface to Locust like this:

    locust

This opens a web server on http://0.0.0.0:8089/ (by default) which offers an interface for starting a new test:

<img width="484" alt="A form with fields for number of users (peak concurrency), spawn rate (users started/second) and host (the URL to start the tests at)" src="https://user-images.githubusercontent.com/9599/197367313-8b4c85b9-cd0e-45ed-adc2-789116687cb5.png">

You can run this for as long as you like, and it will produce both statistics on the load test and some pleasing charts:

<img width="1049" alt="Charts for total requests per second over time and response times in ms" src="https://user-images.githubusercontent.com/9599/197367351-03735a41-00cb-4bbf-a13d-cb22bbaf6e3b.png">

## Using the command-line

You can also run tests without the web server at all. I tend to use this option as it's quicker to repeat a test, and you can easily copy and paste the results into a GitHub issue thread.

    locust --headless --users 4 --spawn-rate 2 -H http://127.0.0.1:8001

This runs the tests in the current `locustfile.py` against `http://127.0.0.1:8001`, with four concurrent users and ramping up at 2 users every second (so taking two seconds to ramp up to full concurrency).

Hit `Ctrl+C` to end the test. It will end up producing something like this:

```
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /fixtures/sortable                                                               475     0(0.00%) |    169     110     483    170 |   23.58        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       475     0(0.00%) |    169     110     483    170 |   23.58        0.00

Response time percentiles (approximated)
Type     Name                                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
GET      /fixtures/sortable                                                                    170    170    180    180    190    200    210    250    480    480    480    475
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                            170    170    180    180    190    200    210    250    480    480    480    475
```

## More complicated tests

Locust tests can get a lot more complex than this. The documentation [provides this example](https://docs.locust.io/en/stable/writing-a-locustfile.html):

```python
import time
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def hello_world(self):
        self.client.get("/hello")
        self.client.get("/world")

    @task(3)
    def view_items(self):
        for item_id in range(10):
            self.client.get(f"/item?id={item_id}", name="/item")
            time.sleep(1)

    def on_start(self):
        self.client.post("/login", json={"username":"foo", "password":"bar"})
```
This illustrates some neat concepts. Each "user" will constantly pick a task at random, where a task is a method decorated with the `@task` decorator. `@task(3)` here gives that task a weight of three, so it's three times more likely to be accepted.

The `self.client` can maintain cookie state between requests, with each user getting a separate copy. `on_start` is used here to log the user in, but also demonstrates how POST requests can work against APIs that accept JSON.
