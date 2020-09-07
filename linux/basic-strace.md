# Basic strace to see what a process is doing

I had a long-running process and I wanted to check that it was at least doing _something_.

I know its PID (32425 in this case) - here's how to use `strace` to see what it's doing right now. This command outputs a lot of lines very quickly - hit `Ctrl+C` to stop it.
```
$ sudo strace -p 32425
strace: Process 32425 attached
lseek(4, 923287936, SEEK_SET)           = 923287936
write(4, "\r\0\0\0\1\0\"\0\0\"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
lseek(3, 919687168, SEEK_SET)           = 919687168
read(3, "\r\0\0\0\1\0\"\0\0\"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
lseek(4, 923292032, SEEK_SET)           = 923292032
write(4, "\0\3kf\0\0\0\0\265\17I\247\326\307U\263xF\34\305\336\231\352a", 24) = 24
lseek(4, 923292056, SEEK_SET)           = 923292056
```
So at least there's stuff happining!

Running `strace -c` does a count of syscalls and provides a summary. The command appears not to do anything, but when you hit `Ctrl+C` after a few seconds it will dump out the counts so far:
```
$ sudo strace -c -p 32425
strace: Process 32425 attached
^Cstrace: Process 32425 detached
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 56.67    0.048823          28      1741           write
 29.60    0.025496          10      2613           lseek
 13.73    0.011828          14       871           read
------ ----------- ----------- --------- --------- ----------------
100.00    0.086147                  5225           total
```
The `-k` option adds stack traces to each syscall which give a better idea of where in the code the syscalls are being made from:
```
$ sudo strace -k -p 32425
strace: Process 32425 attached
lseek(4, 974466576, SEEK_SET)           = 974466576
 > /lib/x86_64-linux-gnu/libc-2.27.so(llseek+0x7) [0x110327]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(unixWrite+0x5d) [0x393cd]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(pagerWalFrames+0x5e5) [0xa8e75]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(pagerStress+0x13f) [0xa9cff]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(getPageNormal+0x33a) [0xadeea]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(backupOnePage.isra.666+0x102) [0xa86c2]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(sqlite3_backup_step+0x2f2) [0xb7a12]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(sqlite3RunVacuum+0x95c) [0x10534c]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(sqlite3VdbeExec+0x1dbf) [0xe230f]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(sqlite3_step+0x210) [0xec3d0]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(pysqlite_step+0x1e) [0x23fae]
 > /home/ubuntu/datasette-venv/lib/python3.6/site-packages/pysqlite3/_sqlite3.cpython-36m-x86_64-linux-gnu.so(_pysqlite_query_execute+0x359) [0x22309]
 > /usr/bin/python3.6(PyCFunction_Call+0x52) [0x1670e2]
 > /usr/bin/python3.6(PyObject_Call+0x3e) [0x19fe1e]
```
