#-------------------------------------------
# Creating SQLite db to store scorecard metadata
#-------------------------------------------

import sqlite3
from datetime import datetime
from typing import Union, get_args, get_origin

from pydantic import BaseModel
from pydantic_schema import ScorecardRow

#-------------------------------------------
# Variables
#-------------------------------------------

table_name = "scorecard"
py_schema = ScorecardRow

def _retrieve_rows(py_schema: type[BaseModel]):
    """
    Parses pydantic schema into a dictionary
"""

    schema_dict = py_schema.model_fields

    return schema_dict

def _create_statement(table_name:str, py_schema: type[BaseModel]):
    """
    Constructs create statement based on pydantic schema
    """

    schema_dict = _retrieve_rows(py_schema)

    type_map = {str: "TEXT", int: "INTEGER", float: "REAL", datetime: "TEXT"}

    cols = []
    for field, fieldInfo in schema_dict.items():
        annotation = fieldInfo.annotation

        # unwrap Optional[X] (i.e. Union[X, None]) to get the underlying type
        if get_origin(annotation) is Union:
            args = [a for a in get_args(annotation) if a is not type(None)]
            annotation = args[0] if args else annotation

        is_primary_key = (fieldInfo.json_schema_extra or {}).get("primary_key", False)

        if is_primary_key:
            cols.append(f"{field} INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            cols.append(f"{field} {type_map.get(annotation, 'TEXT')}")

    create_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n" + ",\n".join(cols) + "\n)"

    return create_statement

def _insert_statement(row: BaseModel, py_schema: type[BaseModel]):
    """
    Constructs insert statement based on pydantic schema
    """

    # drop unset fields (e.g. an omitted optional primary key) so the db can auto-generate them
    provided = [(field, value) for field, value in row if value is not None]

    fields = [field for field, value in provided]
    values = [value.isoformat() if isinstance(value, datetime) else value for field, value in provided]
    fields_str = ','.join(fields)
    placeholders = ','.join('?' for _ in fields)

    set_fields = [field for field in _retrieve_rows(py_schema)]

    # assertions
    assert all(f in set_fields for f in fields), "Missing a field"

    insert_statement = f"""insert into {table_name} (
    {fields_str})
    values ({placeholders}
    )
    """

    return insert_statement, values

def _select_statement(table_name:str, py_schema: type[BaseModel], where: str = None):
    """
    Constructs select statement based on pydantic schema
    """

    schema_dict = _retrieve_rows(py_schema)

    col_sql = ', '.join(schema_dict.keys())

    select_statement = f"SELECT {col_sql} FROM {table_name}"

    if where:
        select_statement += f" WHERE {where}"

    return select_statement

def db_connection(table_name:str) -> sqlite3.connect:
    """
    Connecting to SQLite db
    Returns db connection
    """

    if not table_name.endswith('.db'):
        table_name = table_name + '.db'

    try:
        conn = sqlite3.connect(table_name)
        print(f"Successfully connected to table: {table_name}")
        return conn

    except Exception as e:
        print(f"Was not able to connect to table: {e}")
        raise

def create_table(table_name:str, py_schema: type[BaseModel]):
    """
    Creating create table query from pydantic schema
    """

    conn = db_connection(table_name)
    cursor = conn.cursor()

    create_statement = _create_statement(table_name, py_schema)

    cursor.execute(create_statement)
    conn.commit()
    conn.close()

def insert_row(row: BaseModel, table_name:str, py_schema: type[BaseModel]):
    """
    Constructing query to insert new score card row
    """

    conn = db_connection(table_name)
    cursor = conn.cursor()

    insert_statement, values = _insert_statement(row, py_schema)

    cursor.execute(insert_statement, values)
    conn.commit()
    conn.close()

def select_rows(table_name:str, py_schema: type[BaseModel], where: str = None, params: tuple = ()):
    """
    Retrieving rows from db, filtered by an optional WHERE clause
    Returns a list of dicts, one per row
    """

    conn = db_connection(table_name)
    cursor = conn.cursor()

    select_statement = _select_statement(table_name, py_schema, where)

    cursor.execute(select_statement, params)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    conn.close()

    return [dict(zip(columns, row)) for row in rows]



    











    