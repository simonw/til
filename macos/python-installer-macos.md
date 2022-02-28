# Installing Python on macOS with the official Python installer

I usually use Homebrew on macOS, but I decided to try using the official Python installer based on [this Twitter conversation](https://twitter.com/rtpg_/status/1498115527465914371).

My big fear was that it would add Yet Another Python to my system in a way that made the [XKCD 1987](https://xkcd.com/1987/) situation even worse!

I downloaded the installer using the prompt on the Python.org homepage (in the "Downloads" menu):

<img width="967" alt="image" src="https://user-images.githubusercontent.com/9599/156053747-0cad53c1-6646-4398-a36d-582179bf4a93.png">

After running the installer and accepting the default options, a Python 3.10 folder was added to my `/Applications` folder:

<img width="540" alt="image" src="https://user-images.githubusercontent.com/9599/156053911-a9f9d28a-ed1c-43c9-a5ce-098444b30fd3.png">

More importantly though, running `python3` in my terminal now runs the version of Python that was installed by the installer - which lives in `/Library/Frameworks/Python.framework/`:
```
~ % which python3
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3
~ % python3
Python 3.10.2 (v3.10.2:a58ebcc701, Jan 13 2022, 14:50:16) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
```
I was confused as to how it had added itself to my path - a tip [from Ned Deily](https://twitter.com/baybryj/status/1498388515742224387) (a Python release manager) helped me figure that out:

```
~ % grep -d skip '3.10' ~/.*
/Users/simon/.zprofile:# Setting PATH for Python 3.10
/Users/simon/.zprofile:PATH="/Library/Frameworks/Python.framework/Versions/3.10/bin:${PATH}"
```
So the installer added a line to my `.zprofile` file adding the `bin` directory for that release to my path.

Running `python3.10` is the most specific way to execute that version of Python. I can install new command-line tools into that `bin` directory like so:

    % python3.10 -m pip install google-drive-to-sqlite
    Collecting google-drive-to-sqlite
      Downloading google_drive_to_sqlite-0.4-py3-none-any.whl (20 kB)
    ...
    % google-drive-to-sqlite --version
    google-drive-to-sqlite, version 0.4
    % which google-drive-to-sqlite
    /Library/Frameworks/Python.framework/Versions/3.10/bin/google-drive-to-sqlite

