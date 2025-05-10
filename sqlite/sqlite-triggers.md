# SQLite triggers

I wrote a script, [triggers.py](triggers.py), to help me understand what data is available to SQLite triggers for which operations.

SQLite triggers are [documented here](https://www.sqlite.org/lang_createtrigger.html). The key triggers are before and after for insert, update and delete. I have not explored [instead of triggers](https://www.sqlite.org/lang_createtrigger.html#instead_of_triggers) yet, since those only apply to SQL views.

This section shows the output of running my `triggers.py` script. The triggers it uses are displayed at the bottom of the page.

<!-- [[[cog
import cog
import triggers
print("```")
triggers.main()
print("```")
]]] -->
```
create table no_pk (value text) 
create table single_pk (id integer primary key, value text) 
create table compound_pk (id1 integer, id2 integer, value text, primary key (id1, id2)) 

insert into no_pk (value) values (?) ('no_pk_value',)
  before insert on no_pk:
    {
      "action": "insert",
      "new": {
        "value": "no_pk_value"
      }
    }
  after insert on no_pk:
    {
      "action": "insert",
      "new": {
        "value": "no_pk_value"
      }
    }

insert into single_pk (id, value) values (?, ?) (1, 'single_pk_value')
  before insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "single_pk_value"
      }
    }
  after insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "single_pk_value"
      }
    }

insert or ignore:

insert or ignore into single_pk (id, value) values (?, ?) (1, 'single_pk_value_ignored')
  before insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "single_pk_value_ignored"
      }
    }

insert or ignore into single_pk (id, value) values (?, ?) (2, 'single_pk_value_not_ignored')
  before insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 2,
        "value": "single_pk_value_not_ignored"
      }
    }
  after insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 2,
        "value": "single_pk_value_not_ignored"
      }
    }

insert or replace:

insert or replace into single_pk (id, value) values (?, ?) (1, 'single_pk_value')
  before insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "single_pk_value"
      }
    }
  after insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "single_pk_value"
      }
    }

insert or replace into single_pk (id, value) values (?, ?) (1, 'single_pk_value_replaced')
  before insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "single_pk_value_replaced"
      }
    }
  after insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "single_pk_value_replaced"
      }
    }

insert ... on conflict set (aka upsert):

insert into single_pk (id, value) values (?, ?) on conflict(id) do update set value=? (1, 'conflict_value', 'updated_on_conflict')
  before insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 1,
        "value": "conflict_value"
      }
    }
  before update on single_pk:
    {
      "action": "update",
      "new": {
        "id": 1,
        "value": "updated_on_conflict"
      },
      "old": {
        "id": 1,
        "value": "single_pk_value_replaced"
      }
    }
  after update on single_pk:
    {
      "action": "update",
      "new": {
        "id": 1,
        "value": "updated_on_conflict"
      },
      "old": {
        "id": 1,
        "value": "single_pk_value_replaced"
      }
    }

insert into single_pk (id, value) values (?, ?) on conflict(id) do update set value=? (3, 'new_value', 'this_wont_be_used')
  before insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 3,
        "value": "new_value"
      }
    }
  after insert on single_pk:
    {
      "action": "insert",
      "new": {
        "id": 3,
        "value": "new_value"
      }
    }

insert into compound_pk (id1, id2, value) values (?, ?, ?) (1, 2, 'compound_pk_value')
  before insert on compound_pk:
    {
      "action": "insert",
      "new": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value"
      }
    }
  after insert on compound_pk:
    {
      "action": "insert",
      "new": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value"
      }
    }

update no_pk set value = ? where rowid = ? ('no_pk_value_updated', 1)
  before update on no_pk:
    {
      "action": "update",
      "new": {
        "value": "no_pk_value_updated"
      },
      "old": {
        "value": "no_pk_value"
      }
    }
  after update on no_pk:
    {
      "action": "update",
      "new": {
        "value": "no_pk_value_updated"
      },
      "old": {
        "value": "no_pk_value"
      }
    }

update single_pk set value = ? where id = ? ('single_pk_value_updated', 1)
  before update on single_pk:
    {
      "action": "update",
      "new": {
        "id": 1,
        "value": "single_pk_value_updated"
      },
      "old": {
        "id": 1,
        "value": "updated_on_conflict"
      }
    }
  after update on single_pk:
    {
      "action": "update",
      "new": {
        "id": 1,
        "value": "single_pk_value_updated"
      },
      "old": {
        "id": 1,
        "value": "updated_on_conflict"
      }
    }

update compound_pk set value = ? where id1 = ? and id2 = ? ('compound_pk_value_updated', 1, 2)
  before update on compound_pk:
    {
      "action": "update",
      "new": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value_updated"
      },
      "old": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value"
      }
    }
  after update on compound_pk:
    {
      "action": "update",
      "new": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value_updated"
      },
      "old": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value"
      }
    }

delete from no_pk where rowid = ? (1,)
  before delete on no_pk:
    {
      "action": "delete",
      "old": {
        "value": "no_pk_value_updated"
      }
    }
  after delete on no_pk:
    {
      "action": "delete",
      "old": {
        "value": "no_pk_value_updated"
      }
    }

delete from single_pk where id = ? (1,)
  before delete on single_pk:
    {
      "action": "delete",
      "old": {
        "id": 1,
        "value": "single_pk_value_updated"
      }
    }
  after delete on single_pk:
    {
      "action": "delete",
      "old": {
        "id": 1,
        "value": "single_pk_value_updated"
      }
    }

delete from compound_pk where id1 = ? and id2 = ? (1, 2)
  before delete on compound_pk:
    {
      "action": "delete",
      "old": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value_updated"
      }
    }
  after delete on compound_pk:
    {
      "action": "delete",
      "old": {
        "id1": 1,
        "id2": 2,
        "value": "compound_pk_value_updated"
      }
    }

```
<!-- [[[end]]] -->

## The triggers it uses

<!-- [[[cog
import sqlite3
print("```sql")
db = sqlite3.connect(":memory:")
triggers.create_tables(db, hide_logs=True)
triggers.create_triggers(db, "no_pk", [], ["value"])
triggers.create_triggers(db, "single_pk", ["id"], ["value"])
triggers.create_triggers(db, "compound_pk", ["id1", "id2"], ["value"])
for row in db.execute('select sql from sqlite_master where type=?', ['trigger']):
    print(row[0] + ';\n')
print("```")
]]] -->
```sql
CREATE TRIGGER no_pk_bi
    before insert on no_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before insert', 'no_pk', json_object('action', 'insert', 'new', json_object('value', NEW.value)));
    end;

CREATE TRIGGER no_pk_ai
    after insert on no_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after insert', 'no_pk', json_object('action', 'insert', 'new', json_object('value', NEW.value)));
    end;

CREATE TRIGGER no_pk_bu
    before update on no_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before update', 'no_pk', json_object('action', 'update', 'new', json_object('value', NEW.value), 'old', json_object('value', OLD.value)));
    end;

CREATE TRIGGER no_pk_au
    after update on no_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after update', 'no_pk', json_object('action', 'update', 'new', json_object('value', NEW.value), 'old', json_object('value', OLD.value)));
    end;

CREATE TRIGGER no_pk_bd
    before delete on no_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before delete', 'no_pk', json_object('action', 'delete', 'old', json_object('value', OLD.value)));
    end;

CREATE TRIGGER no_pk_ad
    after delete on no_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after delete', 'no_pk', json_object('action', 'delete', 'old', json_object('value', OLD.value)));
    end;

CREATE TRIGGER single_pk_bi
    before insert on single_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before insert', 'single_pk', json_object('action', 'insert', 'new', json_object('id', NEW.id, 'value', NEW.value)));
    end;

CREATE TRIGGER single_pk_ai
    after insert on single_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after insert', 'single_pk', json_object('action', 'insert', 'new', json_object('id', NEW.id, 'value', NEW.value)));
    end;

CREATE TRIGGER single_pk_bu
    before update on single_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before update', 'single_pk', json_object('action', 'update', 'new', json_object('id', NEW.id, 'value', NEW.value), 'old', json_object('id', OLD.id, 'value', OLD.value)));
    end;

CREATE TRIGGER single_pk_au
    after update on single_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after update', 'single_pk', json_object('action', 'update', 'new', json_object('id', NEW.id, 'value', NEW.value), 'old', json_object('id', OLD.id, 'value', OLD.value)));
    end;

CREATE TRIGGER single_pk_bd
    before delete on single_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before delete', 'single_pk', json_object('action', 'delete', 'old', json_object('id', OLD.id, 'value', OLD.value)));
    end;

CREATE TRIGGER single_pk_ad
    after delete on single_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after delete', 'single_pk', json_object('action', 'delete', 'old', json_object('id', OLD.id, 'value', OLD.value)));
    end;

CREATE TRIGGER compound_pk_bi
    before insert on compound_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before insert', 'compound_pk', json_object('action', 'insert', 'new', json_object('id1', NEW.id1, 'id2', NEW.id2, 'value', NEW.value)));
    end;

CREATE TRIGGER compound_pk_ai
    after insert on compound_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after insert', 'compound_pk', json_object('action', 'insert', 'new', json_object('id1', NEW.id1, 'id2', NEW.id2, 'value', NEW.value)));
    end;

CREATE TRIGGER compound_pk_bu
    before update on compound_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before update', 'compound_pk', json_object('action', 'update', 'new', json_object('id1', NEW.id1, 'id2', NEW.id2, 'value', NEW.value), 'old', json_object('id1', OLD.id1, 'id2', OLD.id2, 'value', OLD.value)));
    end;

CREATE TRIGGER compound_pk_au
    after update on compound_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after update', 'compound_pk', json_object('action', 'update', 'new', json_object('id1', NEW.id1, 'id2', NEW.id2, 'value', NEW.value), 'old', json_object('id1', OLD.id1, 'id2', OLD.id2, 'value', OLD.value)));
    end;

CREATE TRIGGER compound_pk_bd
    before delete on compound_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before delete', 'compound_pk', json_object('action', 'delete', 'old', json_object('id1', OLD.id1, 'id2', OLD.id2, 'value', OLD.value)));
    end;

CREATE TRIGGER compound_pk_ad
    after delete on compound_pk
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after delete', 'compound_pk', json_object('action', 'delete', 'old', json_object('id1', OLD.id1, 'id2', OLD.id2, 'value', OLD.value)));
    end;

```
<!-- [[[end]]] -->

## Rebuilding this page

This page uses [Cog](https://cog.readthedocs.io/) to include the output of the `triggers.py` script. To rebuild this page after modifying the script, run this:

```bash
cog -P -r sqlite-triggers.md
```

