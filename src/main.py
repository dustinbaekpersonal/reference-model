import polars as pl
from loguru import logger

from .db.postgres import PgConnector
from .vendor.open_figi import OpenFigiApi


def main():
    # avail_df = OpenFigiApi.get_available_symbol_types()
    # df = avail_df.select(
    #     pl.lit(1).alias("instrument_type_id"),
    #     pl.col("symbol").alias("name"),
    #     pl.lit(1).alias("vendor_id").cast(pl.Int16)
    # )
    df = pl.DataFrame(
        {
            "instrument_type_id": list(range(1, 4)),
            "name": ["Company", "Equity", "EquityListing"],
        },
        schema={"instrument_type_id": pl.Int16, "name": pl.String},
    )
    with PgConnector("reference") as ref_pg:
        # ref_pg.copy(df, "instrument_types")
        ref_pg.write(df, "instrument_types", "replace")


if __name__ == "__main__":
    main()
