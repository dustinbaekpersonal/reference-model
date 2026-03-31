import polars as pl
from loguru import logger

from .db.postgres import PgConnector
from .vendor.open_figi import OpenFigiApi


def _fetch_existing_if_not_insert(
    df: pl.DataFrame, db_name: str, table_name: str
) -> pl.DataFrame:
    """
    Insert a Polars DataFrame to a table in the database if the table is empty.
    """
    read_stmt = f"SELECT * FROM {table_name};"
    with PgConnector(db_name) as pg_conn:
        existing_df = pg_conn.execute(read_stmt)
        if existing_df.is_empty():
            pg_conn.write(df, table_name, "replace")
            logger.info(f"Inserted {df.shape} DataFrame to table {table_name}")
            new_df = pg_conn.execute(read_stmt)
            return new_df

        common_cols = set(df.columns) & set(existing_df.columns)
        only_in_existing_df = existing_df.join(df, on=common_cols, how="anti")
        if not only_in_existing_df.is_empty():
            logger.warning(
                f"Table {table_name} already exists with different data. Please check."
            )
    return existing_df


def _check_all_ref_tables():
    # available symbol types
    avail_df = OpenFigiApi.get_available_symbol_types().rename({"symbol": "name"})

    # symbols
    symbol_df = avail_df.with_columns(
        pl.Series(
            "instrument_type_id",
            [2] + [3] * 4 + [2] * 2 + [3] * 7 + [2] + [3] * 4 + [2] + [3] * 6,
            dtype=pl.Int16,
        )
    ).select(
        pl.col("instrument_type_id", "name"),
        pl.lit(1).alias("vendor_id").cast(pl.Int16),
    )
    existing_symbol_df = _fetch_existing_if_not_insert(
        symbol_df, "reference", "symbols"
    )

    # symbol details
    symbol_details_df = avail_df.join(
        existing_symbol_df,
        on="name",
        how="inner",
        validate="1:1",
        maintain_order="left",
    ).select(pl.col("symbol_id", "description", "example"))
    _fetch_existing_if_not_insert(symbol_details_df, "reference", "symbol_details")

    # instrument types
    instrument_types_df = pl.DataFrame(
        {
            "instrument_type_id": list(range(1, 4)),
            "name": ["Company", "Equity", "EquityListing"],
        },
        schema={"instrument_type_id": pl.Int16, "name": pl.String},
    )
    _fetch_existing_if_not_insert(instrument_types_df, "reference", "instrument_types")


def main():
    open_figi = OpenFigiApi()
    open_figi.get_mapping_values("stateCode")


if __name__ == "__main__":
    main()
