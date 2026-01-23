import abc

import polars as pl


class GeneralVendorApi(abc.ABC):
    """
    Api for general vendor that handles header and etc.
    """

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
        self.header = {"Content-Type": "application/json"}

    @abc.abstractmethod
    def get_available_symbol_types(self) -> pl.DataFrame:
        """
        Get available symbol types provided by the vendor.
        """
