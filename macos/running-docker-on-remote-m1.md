# Running Docker on a remote M1 Mac

I was trying to figure out how to get a development environment for a Django project running inside Docker in a M1 Mac.

Since I don't have an M1 Mac, I decided to rent one. AWS haven't launched this yet (at least anywhere I could find it), and Scaleway were out of stock on their machines which you can rent by the day, so I tried using a $109/month M1 Mac Mini [from MacStadium](https://www.macstadium.com/m1-mini).

The machine became available within a minute of me entering the card details, and gave me an IP address I could connect to plus an administrator account username and password. These worked for both VNC and SSH.

For VNC, navigating to `vnc://ip.address.here` in Safari opened the macOS Screen Sharing app and prompted me to connect. For SSH, `ssh administrator@ip.addresse.here` and then entering the password did the trick.

## Installing Homebrew and Docker

First, most important lesson: do _not_ attempt to install these large pieces of software over SSH! Both of these had points within the install process that triggered desktop UI interactions of some sort, and trying to start them over SSH lead to a bewildering array of permission errors. I ended up having to turn the machine off through the MacStadium web interface, waiting a while and then turning it back on again in order to clear the errors (a soft reboot didn't help).

So be sure to open a terminal in the Screen Sharing app over VNC and run the install commands there.

Pasting in the installation command from https://brew.sh/ did the trick. I then installed Docker using `brew install --cask docker`. These both needed to be done not over SSH.

Docker for Mac required Rosetta 2 - thankfully installing that is a case of running `softwareupdate --install-rosetta` - which for me only took a couple of seconds and displayed an error message which appeared not to matter at all, since Docker for Mac then started working fine.

When I tried to run Docker containers with mounted volumes I ran into an issue where a UI prompt displayed on the macOS desktop stating that Docker wanted access to my filesystem - another reason to run the first set of commands over VNC rather than SSH.

Eventually I got to a point where `docker run` commands were safe to run via SSH instead of a terminal over VNC.

## Editing files with VS Code

Not unique to remote macOS but this was the first time I used the VS Code [Remote Development using SSH](https://code.visualstudio.com/docs/remote/ssh) extension and it worked flawlessly - I gave it the IP address, username and password that I had used over SSH and I was able to edit files on the remote Mac in the same way I edit files on my local machine. Fantastic.

## And then I gave up

Getting things to work in Docker on an M1 is really, really hard. Python dependencies using wheels such as `psycopg2-binary` failed to install. `apt-get install ...` inside a Docker container seemed to work for most packages - I upgraded to `FROM python:3.9-buster` as my base image and was able to run `apt-get install python-psycopg2` to talk to PostgreSQL.

The I ran into this error on container startup:

```
docker run -it -v "$(pwd):/app" vial_web bash
root@a9ae5a2956a5:/app/vaccinate# python -i ./manage.py runserver 0.0.0.0:3000
Performing system checks...
free(): invalid pointer
Traceback (most recent call last):
  File "./manage.py", line 29, in <module>
    main()
  File "./manage.py", line 25, in main
    execute_from_command_line(sys.argv)
  File "/usr/local/lib/python3.8/site-packages/django/core/management/__init__.py", line 419, in execute_from_command_line
    utility.execute()
  File "/usr/local/lib/python3.8/site-packages/django/core/management/__init__.py", line 413, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "/usr/local/lib/python3.8/site-packages/django/core/management/base.py", line 354, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/usr/local/lib/python3.8/site-packages/django/core/management/commands/runserver.py", line 61, in execute
    super().execute(*args, **options)
  File "/usr/local/lib/python3.8/site-packages/django/core/management/base.py", line 398, in execute
    output = self.handle(*args, **options)
  File "/usr/local/lib/python3.8/site-packages/django/core/management/commands/runserver.py", line 96, in handle
    self.run(**options)
  File "/usr/local/lib/python3.8/site-packages/django/core/management/commands/runserver.py", line 103, in run
    autoreload.run_with_reloader(self.inner_run, **options)
  File "/usr/local/lib/python3.8/site-packages/django/utils/autoreload.py", line 640, in run_with_reloader
    sys.exit(exit_code)
SystemExit: -6
```
That `free(): invalid pointer` error completely stumped me, since it didn't come with a detailed enough stacktrace that I could figure out which dependency (I have a hunch it was caused by a C deopendency) was causing it, and I couldn't figure out debugging techniques from searching the internet.

Armin Ronacher [said on Twitter](https://twitter.com/mitsuhiko/status/1397266788262584325):

> M1 macs add a whole new world of crazy to Python. Apple Python and homebrew Python and the different types of pyenv pythons and different cpu archs add completely new sources of frustration and errors. I still get random compiler errors from macos version mismatches on big sur.

Which made me feel a little bit better about being defeated!
