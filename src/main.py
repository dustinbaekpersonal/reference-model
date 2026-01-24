import polars as pl
from loguru import logger

from .db.postgres import PgConnector
from .vendor.open_figi import OpenFigiApi


def main():
    # # available symbol types
    # avail_df = OpenFigiApi.get_available_symbol_types()
    # symbol_df = avail_df.with_columns(
    #         pl.Series(
    #             "instrument_type_id",
    #             [2] + [3] * 4 + [2] * 2 + [3] * 7 + [2] + [3] * 4 + [2] + [3] * 6,
    #             dtype=pl.Int16,
    #         )
    #     ).select(
    #         pl.col("instrument_type_id"),
    #         pl.col("symbol").alias("name"),
    #         pl.lit(1).alias("vendor_id").cast(pl.Int16),
    #     )

    # symbol details
    avail_df = OpenFigiApi.get_available_symbol_types()
    avail_df = avail_df.select(
        pl.col("symbol").alias("name"),
        pl.col("description", "example")
    )
    with PgConnector("reference") as ref_pg:
        symbol_df = ref_pg.execute("SELECT * FROM symbols;")
    
    symbol_details_df = avail_df.join(
        symbol_df,
        on="name",
        how="inner",
        validate="1:1",
        maintain_order="left"
    ).select(
        pl.col("symbol_id", "description", "example")
    )
    
    # # instrument types
    # df = pl.DataFrame(
    #     {
    #         "instrument_type_id": list(range(1, 4)),
    #         "name": ["Company", "Equity", "EquityListing"],
    #     },
    #     schema={"instrument_type_id": pl.Int16, "name": pl.String},
    # )
    with PgConnector("reference") as ref_pg:
        ref_pg.write(symbol_details_df, "symbol_details", "append")


if __name__ == "__main__":
    main()
