# Running a MySQL server using Homebrew

First, install MySQL like so:

    brew install mysql

This installs the server but doesn't run it. You  can run it in the background like this:
```
% mysql.server start
Starting MySQL
.. SUCCESS! 
%
```
Then later on you can stop it like so:
```% mysql.server stop 
Shutting down MySQL
. SUCCESS! 
%
```
While it's running it defaults to having a root account that only accepts connections from localhost with no password:
```
% mysql -u root       
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
...
mysql> 
```
Running `mysql_secure_installation` runs a wizard that helps set up a password.

When you first install it, Homebrew says:
```
To have launchd start mysql now and restart at login:
  brew services start mysql
```
You can re-display that message by running `brew reinstall mysql`.

## Installing the mysqlclient Python library

This took me a long time to figure out. Eventually this worked:

    MYSQLCLIENT_CFLAGS=`pkg-config mysqlclient --cflags` \
      MYSQLCLIENT_LDFLAGS=`pkg-config mysqlclient --libs` \
      pip install mysqlclient
