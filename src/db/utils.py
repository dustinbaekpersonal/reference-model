from typing import Self

import psycopg
import polars as pl

class PgConnector:
    _pg_to_pl_dtype = {
        16: pl.Boolean,  # bool
        20: pl.Int64,    # bigint
        21: pl.Int16,    # smallint
        23: pl.Int32,    # int
        700: pl.Float32, # real
        701: pl.Float64, # double precision
        1_043: pl.String, # character varying
        1_082: pl.Date,   # date
        1_114: pl.Datetime, # timestamp without timezone
        1_184: pl.Datetime, # timestamp with timezone
        1_700: pl.Float64,  # numeric / decimal
        # Add more as needed
    }
    _pl_to_pg_dtype = {
        v: k for k, v in _pg_to_pl_dtype.items()
    }

    def __init__(self, db: str):
        self._host = "localhost"
        self._port = 5432
        self._user = "user"
        self._password = "password"
        self._db = db
        self._conn: psycopg.Connection | None = None

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
            breakpoint()
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
            password=self._password
        )       
    
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
        if not self._conn:
            raise RuntimeError("Not connected to database")

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
    

if __name__ == "__main__":
    with PgConnector("reference") as conn:
        query = "SELECT * FROM test.symbols;"
        print(conn.execute(query))



