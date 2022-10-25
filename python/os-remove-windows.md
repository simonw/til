# os.remove() on Windows fails if the file is already open

I puzzled over this one for [quite a while](https://github.com/simonw/sqlite-utils/issues/503) this morning. I had this test that was failing with Windows on Python 3.11:

```python
@pytest.mark.parametrize(
    "use_path,file_exists", [(True, True), (True, False), (False, True), (False, False)]
)
def test_recreate(tmpdir, use_path, file_exists):
    filepath = str(tmpdir / "data.db")
    if use_path:
        filepath = pathlib.Path(filepath)
    if file_exists:
        Database(filepath)["t1"].insert({"foo": "bar"})
        assert ["t1"] == Database(filepath).table_names()
    Database(filepath, recreate=True)["t2"].insert({"foo": "bar"})
    assert ["t2"] == Database(filepath).table_names()
```
The test checks that the `recreate=True` option to my `Database()` constructor deletes and re-creates the file.

Here's [the implementation](https://github.com/simonw/sqlite-utils/blob/9cbe19ac0547031f3b626d9d18ef05c0d193bf79/sqlite_utils/db.py#L320-L323) of that `recreate=True` option:
```python
elif isinstance(filename_or_conn, (str, pathlib.Path)):
    if recreate and os.path.exists(filename_or_conn):
        os.remove(filename_or_conn)
    self.conn = sqlite3.connect(str(filename_or_conn))
```
On Windows I was getting the following exception:
```
FAILED tests/test_recreate.py::test_recreate[True-True] - 
  PermissionError: [WinError 32] The process cannot access the file because it is being used by another process:
  'C:\\Users\\runneradmin\\AppData\\Local\\Temp\\pytest-of-runneradmin\\pytest-0\\test_recreate_True_True_0\\data.db'
```
Eventually I spotted the problem: my call on this line was opening a SQLite connection to the `data.db` file:

```python
Database(filepath)["t1"].insert({"foo": "bar"})
```
But it wasn't explicitly closing the SQLite connection. It turns out that leaves the database file open - and since the file is still open Windows raised an exception when `os.remove()` was called against it.

I fixed the error by closing the SQLite3 connection in my test, like this:

```python
db = Database(filepath)
db["t1"].insert({"foo": "bar"})
assert ["t1"] == db.table_names()
db.conn.close()
```
