def get_db_path(basedir, mode=None):
    """
    Return the path to the database.
    """
    return basedir.joinpath(
        "{prefix}db.sqlite3".format(prefix="" if mode is None else "{}_".format(mode))
    )


def get_table_fullname(table_name, mode=None):
    """
    Return the full prefixed name of a database table.
    """
    return "{prefix}{table_name}".format(
        prefix="" if mode is None else "{}_".format(mode), table_name=table_name
    )
