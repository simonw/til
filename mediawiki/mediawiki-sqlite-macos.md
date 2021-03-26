# How to run MediaWiki with SQLite on a macOS laptop

Today I [got curious](https://twitter.com/simonw/status/1368414296888070146) about how MediaWiki records page history, so I started digging around and in the process figured out how to run it against a SQLite database on my macOS laptop!

## Requirements: PHP

To run MediaWiki you need PHP and the SQLite drivers. I was surprised to find out I had PHP already (if not I would have tried installing through Homebrew). It turns out it comes pre-installed on your Mac!

    ~ % php --version
    PHP 7.3.11 (cli) (built: Jun  5 2020 23:50:40) ( NTS )
    Copyright (c) 1997-2018 The PHP Group
    Zend Engine v3.3.11, Copyright (c) 1998-2018 Zend Technologies

To see version information, do this:

    % cd /tmp
    % echo '<? phpinfo(); ?>' > index.php
    % php -S localhost:8000
    PHP 7.3.11 Development Server started at Sat Mar  6 20:50:32 2021
    Listening on http://localhost:8000
    Document root is /private/tmp
    Press Ctrl-C to quit.

`php -S localhost:8000` runs PHP's built-in development server, saving you from having to configure Apache.

Then visit http://localhost:8000 to view the PHP info page.

I searched that page for `sqlite` and found that it had the `pdo_sqlite` driver installed already. So that should be everything I need to run MediaWiki.

## Downloading MediaWiki

I downloaded the latest version of MediaWiki from [their downloads page](https://www.mediawiki.org/wiki/Download), unzipped it, ran `php -S localhost:8000` and got this error message:

<img width="664" alt="MediaWiki_1_35" src="https://user-images.githubusercontent.com/9599/110229420-1d932280-7ebe-11eb-98f3-eb13fa7f07c7.png">

Turns out the latest MediaWiki requires PHP 7.3.19, but the version bundled with my laptop was 7.3.11.

I didn't want to mess around with upgrading PHP, so I used the [compatibility page](https://www.mediawiki.org/wiki/Compatibility#PHP) to figure out the most recent MediaWiki version that would work with PHP 7.3.11. I decided to try MediaWiki 1.31, which can be downloaded from <https://releases.wikimedia.org/mediawiki/1.31/?C=S;O=D>

Here's what worked for me:

    % mkdir ~/wiki
    % cd ~/wiki
    % wget https://releases.wikimedia.org/mediawiki/1.31/mediawiki-1.31.12.zip
    % unzip mediawiki-1.31.12.zip
    % cd mediawiki-1.31.12
    % php -S localhost:8000
    PHP 7.3.11 Development Server started at Sat Mar  6 20:58:21 2021
    Listening on http://localhost:8000
    Document root is /Users/simon/wiki/mediawiki-1.31.12

Now visiting http://localhost:8000 gave me the interactive setup tool.

I clicked through their wizard, selected SQLite for the database option and told it where I wanted the database to live:

<img width="856" alt="MediaWiki_1_31_12_installation" src="https://user-images.githubusercontent.com/9599/110229508-e4a77d80-7ebe-11eb-9a71-70ba16e25f92.png">

At the end of the wizard it gave me a `LocalSettings.php` file to drop into my root `~/wiki/mediawiki-1.31.12` directory... and I was done! Didn't even need to restart the PHP process (because PHP).

I created a page and then ran Datasette against the SQLite databases it was using like this:

    % datasette ~/wiki/data/*.sqlite
