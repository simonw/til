# Creating a minimal SpatiaLite database with Python

When writing a test for [datasette-leaflet-freedraw](https://github.com/simonw/datasette-leaflet-freedraw) I realized I didn't have a simple tiny recipe for creating an in-memory SpatiaLite database in Python. I came up with this:

```python
import sqlite3

SPATIALITE = "/usr/local/lib/mod_spatialite.dylib"

db = sqlite3.connect(":memory:")
db.enable_load_extension(True)
db.execute("SELECT load_extension(?)", [SPATIALITE])
db.execute("SELECT InitSpatialMetadata(1)")
db.execute("CREATE TABLE places_spatialite (id integer primary key, name text)")
db.execute(
    "SELECT AddGeometryColumn('places_spatialite', 'geometry', 4326, 'POINT', 'XY');"
)
# Then to add a spatial index:
db.execute(
    "SELECT CreateSpatialIndex('places_spatialite', 'geometry');"
)
```
Datasette and `sqlite-utils` both have `find_spatialite()` utility functions. Here's how to call the Datasette one as a one-liner:
```
% python -c 'import datasette.utils; print(datasette.utils.find_spatialite())'
/usr/local/lib/mod_spatialite.dylib
```
I also remembered I have this script: [build_small_spatialite_db.py](https://github.com/simonw/datasette/blob/main/tests/build_small_spatialite_db.py)
