# Using tree-sitter with Python

[tree-sitter](https://tree-sitter.github.io/tree-sitter/) is a "parser generator tool and an incremental parsing library". It has a very good reputation these days.

Two useful posts by Douglas Creager: [Getting started with tree-sitter](https://dcreager.net/2021/06/getting-started-with-tree-sitter/) and [A map of the tree-sitter ecosystem](https://dcreager.net/2021/06/tree-sitter-map/).

I want to be able to parse SQLite SQL - in particular I want to be able to parse `CREATE TABLE` statements, because SQLite stores those directly in its `sqlite_master` metadata table as the main source of truth about a table, and I want to be able to introspect them beyond what's possible with `pragma table_info()` and friends.

It turns out there are tree-sitter grammars for a huge array of languages, including one for SQLite SQL hosted at [github.com/dhcmrlchtdj/tree-sitter-sqlite](https://github.com/dhcmrlchtdj/tree-sitter-sqlite).

## Compiling a grammer using Python

tree-sitter grammars need to be compiled - they generate C code, which should then be compiled into a `.so` library file.

[py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter) provides Python bindings for tree-sitter that can both work with compiled grammars AND manage the compilation process.

Here's how I compiled the SQLite grammar:

```bash
git clone https://github.com/dhcmrlchtdj/tree-sitter-sqlite
pipenv shell
python -m pip install tree_sitter
python
```
```pycon
>>> from tree_sitter import Language, Parser
>>> Language.build_library('/tmp/sqlite.so', ['/tmp/tree-sitter-sqlite'])
True
````
This gave me a `/tmp/sqlite.so` file - 1.1MB in size.

## Parsing text using Python

Here's how to use that from Python:

```python
from tree_sitter import Language, Parser
language = Language('/tmp/sqlite.so', 'sqlite')
parser = Parser()
parser.set_language(language)
sql = b"""CREATE TABLE _datasette_auth_tokens (
   id INTEGER PRIMARY KEY,
   secret TEXT,
   description TEXT,
   permissions TEXT,
   actor_id TEXT,
   created_timestamp INTEGER,
   last_used_timestamp INTEGER,
   expires_after_seconds INTEGER
);"""
tree = parser.parse(sql)
print(tree.root_node.sexp())
```
Which outputs:

`(sql_stmt_list (sql_stmt (create_table_stmt (CREATE) (TABLE) (identifier) (column_def (identifier) (type_name (identifier)) (column_constraint (PRIMARY) (KEY))) (column_def (identifier) (type_name (identifier))) (column_def (identifier) (type_name (identifier))) (column_def (identifier) (type_name (identifier))) (column_def (identifier) (type_name (identifier))) (column_def (identifier) (type_name (identifier))) (column_def (identifier) (type_name (identifier))) (column_def (identifier) (type_name (identifier))))))`

I explored the tree structure a bit in Python as well:

```pycon
>>> n = tree.root_node
>>> dir(n)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'child_by_field_id', 'child_by_field_name', 'child_count', 'children', 'children_by_field_id', 'children_by_field_name', 'end_byte', 'end_point', 'field_name_for_child', 'has_changes', 'has_error', 'id', 'is_missing', 'is_named', 'named_child_count', 'named_children', 'next_named_sibling', 'next_sibling', 'parent', 'prev_named_sibling', 'prev_sibling', 'sexp', 'start_byte', 'start_point', 'text', 'type', 'walk']
>>> n.text
b'CREATE TABLE _datasette_auth_tokens (\n   id INTEGER PRIMARY KEY,\n   secret TEXT,\n   description TEXT,\n   permissions TEXT,\n   actor_id TEXT,\n   created_timestamp INTEGER,\n   last_used_timestamp INTEGER,\n   expires_after_seconds INTEGER\n);'
>>> n.children
[<Node type=sql_stmt, start_point=(0, 0), end_point=(9, 1)>, <Node type=";", start_point=(9, 1), end_point=(9, 2)>]
>>> n.children[0]
<Node type=sql_stmt, start_point=(0, 0), end_point=(9, 1)>
>>> n.children[0].children
[<Node type=create_table_stmt, start_point=(0, 0), end_point=(9, 1)>]
>>> n.children[0].children[0]
<Node type=create_table_stmt, start_point=(0, 0), end_point=(9, 1)>
>>> n.children[0].children[0].children
[<Node type=CREATE, start_point=(0, 0), end_point=(0, 6)>,
 <Node type=TABLE, start_point=(0, 7), end_point=(0, 12)>,
 <Node type=identifier, start_point=(0, 13), end_point=(0, 35)>,
 <Node type="(", start_point=(0, 36), end_point=(0, 37)>,
 <Node type=column_def, start_point=(1, 3), end_point=(1, 25)>,
 <Node type=",", start_point=(1, 25), end_point=(1, 26)>,
 <Node type=column_def, start_point=(2, 3), end_point=(2, 14)>,
 <Node type=",", start_point=(2, 14), end_point=(2, 15)>,
 <Node type=column_def, start_point=(3, 3), end_point=(3, 19)>,
 <Node type=",", start_point=(3, 19), end_point=(3, 20)>,
 <Node type=column_def, start_point=(4, 3), end_point=(4, 19)>,
 <Node type=",", start_point=(4, 19), end_point=(4, 20)>,
 <Node type=column_def, start_point=(5, 3), end_point=(5, 16)>,
 <Node type=",", start_point=(5, 16), end_point=(5, 17)>,
 <Node type=column_def, start_point=(6, 3), end_point=(6, 28)>,
 <Node type=",", start_point=(6, 28), end_point=(6, 29)>,
 <Node type=column_def, start_point=(7, 3), end_point=(7, 30)>,
 <Node type=",", start_point=(7, 30), end_point=(7, 31)>,
 <Node type=column_def, start_point=(8, 3), end_point=(8, 32)>,
 <Node type=")", start_point=(9, 0), end_point=(9, 1)>]
>>> n.children[0].children[0].text
b'CREATE TABLE _datasette_auth_tokens (\n   id INTEGER PRIMARY KEY,\n   secret TEXT,\n   description TEXT,\n   permissions TEXT,\n   actor_id TEXT,\n   created_timestamp INTEGER,\n   last_used_timestamp INTEGER,\n   expires_after_seconds INTEGER\n)'
```
I've only just started exploring tree-sitter - the Python documentation [has more details](https://github.com/tree-sitter/py-tree-sitter#walking-syntax-trees) on ways to walk the tree, plus a description of tree-sitter's [pattern matching language](https://github.com/tree-sitter/py-tree-sitter#pattern-matching) which looks like it may be the key to using it effectively.
