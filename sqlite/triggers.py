import textwrap
import sqlite3
import json


def execute(db, sql, params=None):
    logs_before = db.execute("select * from log").fetchall()
    print(sql, params or "")
    if params is None:
        result = db.execute(sql)
    else:
        result = db.execute(sql, params)
    logs_after = db.execute("select * from log").fetchall()
    if len(logs_after) > len(logs_before):
        rows = [dict(row) for row in logs_after[len(logs_before) :]]
        for row in rows:
            print(
                f"  {row['trigger_name']} on {row['table_name']}:\n{textwrap.indent(json.dumps(json.loads(row['details']), indent=2), '    ')}"
            )
        print()
    return result


def create_triggers(db, table, pk_cols, non_pk_cols):
    # Adds before/after triggers for all operations
    # which log what happened, including JSON of NEW and OLD
    json_object_new = (
        "json_object("
        + ", ".join(f"'{col}', NEW.{col}" for col in pk_cols + non_pk_cols)
        + ")"
    )
    json_object_old = (
        "json_object("
        + ", ".join(f"'{col}', OLD.{col}" for col in pk_cols + non_pk_cols)
        + ")"
    )
    # before insert
    db.execute(
        f"""
    create trigger {table}_bi
    before insert on {table}
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before insert', '{table}', json_object('action', 'insert', 'new', {json_object_new}));
    end;
    """,
    )
    # after insert
    db.execute(
        f"""
    create trigger {table}_ai
    after insert on {table}
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after insert', '{table}', json_object('action', 'insert', 'new', {json_object_new}));
    end;
    """,
    )

    # before update
    db.execute(
        f"""
    create trigger {table}_bu
    before update on {table}
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before update', '{table}', json_object('action', 'update', 'new', {json_object_new}, 'old', {json_object_old}));
    end;
    """,
    )
    # after update
    db.execute(
        f"""
    create trigger {table}_au
    after update on {table}
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after update', '{table}', json_object('action', 'update', 'new', {json_object_new}, 'old', {json_object_old}));
    end;
    """,
    )
    # before delete
    db.execute(
        f"""
    create trigger {table}_bd
    before delete on {table}
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('before delete', '{table}', json_object('action', 'delete', 'old', {json_object_old}));
    end;
    """,
    )
    # after delete
    db.execute(
        f"""
    create trigger {table}_ad
    after delete on {table}
    for each row
    begin
      insert into log (trigger_name, table_name, details)
      values ('after delete', '{table}', json_object('action', 'delete', 'old', {json_object_old}));
    end;
    """,
    )


def create_tables(db, hide_logs=False):
    # logs table
    db.execute(
        "create table log (id integer primary key, trigger_name text, table_name text, details text)"
    )
    if hide_logs:
        method = db.execute
    else:
        method = lambda sql: execute(db, sql)
    # Three tables: a rowid table, a single pk table, a compound pk table
    method("create table no_pk (value text)")
    method("create table single_pk (id integer primary key, value text)")
    method("create table compound_pk (id1 integer, id2 integer, value text, primary key (id1, id2))")


def main():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    create_tables(db)
    print()
    create_triggers(db, "no_pk", [], ["value"])
    create_triggers(db, "single_pk", ["id"], ["value"])
    create_triggers(db, "compound_pk", ["id1", "id2"], ["value"])
    # Exercise the triggers a bit
    execute(db, "insert into no_pk (value) values (?)", ("no_pk_value",))
    execute(
        db, "insert into single_pk (id, value) values (?, ?)", (1, "single_pk_value")
    )
    print("insert or ignore:\n")
    execute(
        db, "insert or ignore into single_pk (id, value) values (?, ?)", (1, "single_pk_value_ignored")
    )
    execute(
        db, "insert or ignore into single_pk (id, value) values (?, ?)", (2, "single_pk_value_not_ignored")
    )
    print("insert or replace:\n")
    execute(
        db, "insert or replace into single_pk (id, value) values (?, ?)", (1, "single_pk_value")
    )
    execute(
        db, "insert or replace into single_pk (id, value) values (?, ?)", (1, "single_pk_value_replaced")
    )
    print("insert ... on conflict set (aka upsert):\n")
    execute(
        db, "insert into single_pk (id, value) values (?, ?) on conflict(id) do update set value=?", 
        (1, "conflict_value", "updated_on_conflict")
    )
    execute(
        db, "insert into single_pk (id, value) values (?, ?) on conflict(id) do update set value=?", 
        (3, "new_value", "this_wont_be_used")
    )

    execute(
        db,
        "insert into compound_pk (id1, id2, value) values (?, ?, ?)",
        (1, 2, "compound_pk_value"),
    )
    execute(
        db, "update no_pk set value = ? where rowid = ?", ("no_pk_value_updated", 1)
    )
    execute(
        db,
        "update single_pk set value = ? where id = ?",
        ("single_pk_value_updated", 1),
    )
    execute(
        db,
        "update compound_pk set value = ? where id1 = ? and id2 = ?",
        ("compound_pk_value_updated", 1, 2),
    )
    execute(db, "delete from no_pk where rowid = ?", (1,))
    execute(db, "delete from single_pk where id = ?", (1,))
    execute(db, "delete from compound_pk where id1 = ? and id2 = ?", (1, 2))


if __name__ == "__main__":
    main()
