# Using just with Django

Jeff Triplett [convinced me](https://twitter.com/webology/status/1532860591307726851) to take a look at [just](https://github.com/casey/just) as a command automation tool - sort of an alternative to Make, except with a focus on commands rather than managing build dependencies.

I really like it, and I've started using it for my own Django projects.

## Installing with Homebrew

Installing just on my Mac was easy:

    brew install just

The tool is written in Rust and provides binaries for basically everything - there are [plenty more ways](https://github.com/casey/just/blob/master/README.md#installation) to install it.

## Writing a Justfile

The `Justfile` defines which commands `just` makes available. When you run `just` it looks for a `Justfile` in the current or any parent directory.

Commands in that file are run as if the working directory was the directory containing the `Justfile`.

Here's the file I've built so far for my current Django project. The project already uses `pipenv` and has some slightly convoluted environment requirements - just is a perfect tool for patching over those so I don't have to think about them any more. 

I added some comments to help explain what's going on:

```
# Using export here causes this DATABASE_URL to be made available as an
# environment variable for any command run by Just
export DATABASE_URL := "postgresql://localhost/myproject"

# The first command is the default if you run "just" with no options.
# I used *options to allow this to accept options, which means I can run:
#
#    just test -k auth --pdb
#
# To pass the "-k auth --pdb" options to pytest

@test *options:
  pipenv run pytest {{options}}

# This starts the Django development server with an extra environment variable
# I also print out a URL to the console so I can click on it without
# remembering which extra item I configured in /etc/hosts for this project
@server:
  echo "Starting http://myapp.local:8000/"
  DJANGO_SETTINGS_MODULE="config.localhost" pipenv run ./manage.py runserver

# I added this so I could run things like "just manage migrate" to run migrations
@manage *options:
  DJANGO_SETTINGS_MODULE="config.localhost" pipenv run ./manage.py {{options}}
```
The `@` before a command name causes that command to NOT output each line to the console before it is executed, which I found is usually what I wanted.

Here's what that example looks like without the comments: it's pretty succinct.

```
export DATABASE_URL := "postgresql://localhost/myproject"

@test *options:
  pipenv run pytest {{options}}

@server:
  echo "Starting http://myapp.local:8000/"
  DJANGO_SETTINGS_MODULE="config.localhost" pipenv run ./manage.py runserver

@manage *options:
  DJANGO_SETTINGS_MODULE="config.localhost" pipenv run ./manage.py {{options}}
```

## What this lets me do

To list all options:
```
% just --list
Available recipes:
    manage *options
    server
    test *options
```

To run all of my tests:

    just

To run specific tests

    just test -k name

To run tests, stopping at the first error and opening a debugger:

    just test -x --pdb

To start my development server running:

    just server

To run migrations:

    just manage migrate

To run `./manage.py shell`:

    just manage shell

## More examples

I found Jeff's [scripts-to-rule-them-all](https://github.com/jefftriplett/scripts-to-rule-them-all) example really helpful in learning how to use `just`.

The [official README](https://github.com/casey/just/blob/master/README.md) is excellent.
