import io
from typing import Self

import psycopg
import polars as pl
from loguru import logger

from .utils import raise_if_not_connected


class PgConnector:
    _pg_to_pl_dtype = {
        16: pl.Boolean,  # bool
        20: pl.Int64,  # bigint
        21: pl.Int16,  # smallint
        23: pl.Int32,  # int
        25: pl.String,
        700: pl.Float32,  # real
        701: pl.Float64,  # double precision
        1_043: pl.String,  # character varying
        1_082: pl.Date,  # date
        1_114: pl.Datetime,  # timestamp without timezone
        1_184: pl.Datetime,  # timestamp with timezone
        1_700: pl.Float64,  # numeric / decimal
        # Add more as needed
    }
    _pl_to_pg_dtype = {v: k for k, v in _pg_to_pl_dtype.items()}

    def __init__(self, db: str):
        self._host = "localhost"
        self._port = 5432
        self._user = "user"
        self._password = "password"
        self._db = db
        self._conn: psycopg.Connection | None = None
        self._conn_uri = f"postgresql://{self._user}:{self._password}@{self._host}:{self._port}/{self._db}"

    def __enter__(self) -> Self:
        """
        Create a connection to the Postgres database.

        Returns:
            PgConnector: An instance of PgConnector.
        """
        self._conn = self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the connection to the Postgres database.
        """
        if self._conn:
            self._conn.close()
            self._conn = None

    def _connect(self) -> psycopg.Connection:
        """
        Connect to the Postgres database.

        Returns:
            psycopg.Connection: A connection to the database.
        """
        return psycopg.connect(
            host=self._host,
            port=self._port,
            dbname=self._db,
            user=self._user,
            password=self._password,
        )

    @raise_if_not_connected
    def execute(self, sql: str, lazy: bool = False) -> pl.DataFrame | None:
        """
        Run a SQL query on the Postgres database.

        If INSERT, UPDATE, or DELETE, commit the transaction.
        Otherwise, return the result as a Polars DataFrame.

        If lazy is True, return a LazyFrame instead of a DataFrame.

        Args:
            sql (str): The SQL query to run.
            lazy (bool, optional): Whether to return a LazyFrame instead of a DataFrame. Defaults to False.

        Returns:
            pl.DataFrame | None: The result of the query as a Polars DataFrame.

        Raises:
            RuntimeError: If not connected to the database.
        """
        with self._conn.cursor() as cur:
            cur.execute(sql)
            if descs := cur.description:
                schema = {
                    desc.name: self._convert_dtype_pg_to_pl(desc.type_code)
                    for desc in descs
                }
                rows = cur.fetchall()
                df = pl.DataFrame(rows, schema=schema)
                return df.lazy() if lazy else df
            else:
                self._conn.commit()
                logger.info(f"Executed query: {sql}")
                return None

    def _convert_dtype_pg_to_pl(self, pg_dtype: int) -> pl.DataType | None:
        """
        Convert a Postgres data type to a Polars data type.

        Args:
            pg_dtype (int): The Postgres data type.

        Returns:
            pl.DataType | None: The corresponding Polars data type.
        """
        return self._pg_to_pl_dtype.get(pg_dtype)

    @raise_if_not_connected
    def copy(self, df: pl.DataFrame, table_name: str) -> None:
        """
        Copy a Polars DataFrame to a table in the database.

        Args:
            df (pl.DataFrame): The DataFrame to copy.
            table_name (str): The name of the table to copy to.

        Raises:
            RuntimeError: If not connected to the database.
        """
        buffer = io.StringIO()
        df.write_csv(buffer, include_header=True)
        buffer.seek(0)

        with self._conn.cursor() as cur:
            stmt = f"""
            COPY {table_name} ({", ".join(df.columns)})
            FROM STDIN WITH (FORMAT CSV, HEADER)
            """
            cur.copy(stmt, buffer)
            logger.info(f"Copied {df.shape} DataFrame to table {table_name}")
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            logger.warning(f"Row count after COPY (before commit): {count}")
        self._conn.commit()

    @raise_if_not_connected
    def write(self, df: pl.DataFrame, table_name: str, insert_mode: str) -> None:
        """
        Write a Polars DataFrame to a table in the database.

        Args:
            df (pl.DataFrame): The DataFrame to write.
            table_name (str): The name of the table to write to.

        Raises:
            RuntimeError: If not connected to the database.
        """
        ret = df.write_database(
            table_name=table_name,
            connection=self._conn_uri,
            engine="adbc",
            if_table_exists=insert_mode,
        )
        logger.info(
            f"Written {df.shape} DataFrame to table {table_name} with {insert_mode} mode"
            + f" Return value: {ret}"
        )
        return None
