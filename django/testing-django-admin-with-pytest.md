# Writing tests for the Django admin with pytest-django

I'm using [pytest-django](https://pytest-django.readthedocs.io/) on a project and I wanted to write a test for a Django admin create form submission. Here's the pattern I came up with:

```python
from .models import Location
import pytest


def test_admin_create_location_sets_public_id(client, admin_user):
    client.force_login(admin_user)
    assert Location.objects.count() == 0
    response = client.post(
        "/admin/core/location/add/",
        {
            "name": "hello",
            "state": "13",
            "location_type": "1",
            "latitude": "0",
            "longitude": "0",
            "_save": "Save",
        },
    )
    # 200 means the form is being re-displayed with errors
    assert response.status_code == 302
    location = Location.objects.order_by("-id")[0]
    assert location.name == "hello"
    assert location.public_id == "lc"
```
The trick here is to use the `client` and `admin_user` pytest-django fixtures ([documented here](https://pytest-django.readthedocs.io/en/latest/helpers.html#fixtures)) to get a configured test client and admin user object, then use `client.force_login(admin_user)` to obtain a session where that user is signed-in to the admin. Then write tests as normal.

## Using the admin_client fixture

Even better: use the `admin_client` fixture provided by `pytest-django 
` which is already signed into the admin:

```python
def test_admin_create_location_sets_public_id(admin_client):
    response = admin_client.post(
        "/admin/core/location/add/",
    # ...
```

Before finding out that this was included I implemented my own version of it:

```python
import pytest


@pytest.fixture()
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client

# Then write tests like this:
def test_admin_create_location_sets_public_id(admin_client):
    response = admin_client.post(
        "/admin/core/location/add/",
    # ...
```
