users_table_create_template = """
    CREATE TABLE IF NOT EXISTS {prefix}{table_name} (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    pwd_hash TEXT NOT NULL);
    """


def get_create_drop_stmts(creation_template, table_name, mode=None):
    """
    Return the statements for safely creating and dropping a db table.
    """
    prefix = "" if mode is None else "{}_".format(mode)
    return (
        creation_template.format(prefix=prefix, table_name=table_name),
        """DROP TABLE IF EXISTS {prefix}{table_name};""".format(
            prefix=prefix, table_name=table_name
        ),
    )
