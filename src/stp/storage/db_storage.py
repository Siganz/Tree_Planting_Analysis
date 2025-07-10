"""Database helpers."""

from sqlalchemy import create_engine


def get_postgis_engine(db_config: dict):
    """Return a SQLAlchemy engine if config is complete."""
    if not db_config.get("enabled", False):
        return None
    driver = db_config.get("driver")
    user = db_config.get("user")
    password = db_config.get("password")
    host = db_config.get("host")
    port = db_config.get("port")
    database = db_config.get("database")
    if not all((driver, user, password, host, port, database)):
        return None
    url = f"{driver}://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url)
