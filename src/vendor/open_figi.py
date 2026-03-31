import httpx
import polars as pl
from bs4 import BeautifulSoup
from loguru import logger

from .general_vendor import GeneralVendorApi


class OpenFigiApi(GeneralVendorApi):
    BASE_URL = r"https://api.openfigi.com/v{}/"

    def __init__(self, version: int = 3, api_key: str | None = None):
        self.base_url = OpenFigiApi.BASE_URL.format(version)
        super().__init__(self.base_url, api_key)
        if self.api_key:
            self.header |= {"X-OPENFIGI-APIKEY": self.api_key}

    @staticmethod
    def get_available_symbol_types() -> pl.DataFrame:
        """
        TODO: 2026/03/31, turns out at least available idTypes can be fetched from
        get_mapping_values("idType").

        Get available symbol types provided by OpenFigi.

        This webscrapes the OpenFigi website to get the available symbol types.

        Returns:
            pl.DataFrame: A Polars DataFrame containing the available symbol types.
        """
        url = "https://www.openfigi.com/api/documentation#v3-id-type-values"

        with httpx.Client(timeout=10) as client:
            response = client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Find the header for "idType Values"
        header = soup.find("h3", string=lambda s: s and "idType Values" in s)
        if header is None:
            raise RuntimeError(
                "Could not find 'idType Values' section."
                + f" Please check if the URL is correct: {url}"
            )

        # The table immediately follows this header
        table = header.find_next("table")

        rows = table.find("tbody").find_all("tr")

        results = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) != 2:
                continue

            symbol = cols[0].get_text(strip=True)
            detail = cols[1].get_text(" ", strip=True)
            desc, example = detail.split("Example:")

            results.append(
                {
                    "symbol": symbol,
                    "description": desc.strip(),
                    "example": example.strip(),
                }
            )

        results = pl.DataFrame(results)
        return results

    def get_mapping_values(self, key: str) -> pl.DataFrame:
        """
        Get the current list of values for the enum-like properties on Mapping Jobs.

        Args:
            key (str): The key to fetch values for.

        Returns:
            pl.DataFrame: A Polars DataFrame containing the values for the specified key.
        """
        if key not in (
            allowed_keys := {
                "idType",
                "exchCode",
                "micCode",
                "currency",
                "marketSecDes",
                "securityType",
                "securityType2",
                "stateCode",
            }
        ):
            raise ValueError(f"Invalid key: {key}. Allowed keys: {allowed_keys}")

        with httpx.Client() as client:
            res = client.get(self.base_url + f"mapping/values/{key}")
            res.raise_for_status()
            res = res.json()

        logger.info(f"Mapping values for {key}: {len(res)}")
        return pl.DataFrame(res).rename({"values": key})

    def search_symbols(self, payload: dict, start: str | None = None) -> tuple[pl.DataFrame, str | None]:
        """"""
        with httpx.Client() as client:
            res = client.post(
                self.base_url + "search",
                json=payload | {"start": start} if start else payload,
            )
            res.raise_for_status()
            res = res.json()

        res, nxt = res["data"], res["next"]
        logger.info(f"Search symbols: {len(res)}" + f" Next: {nxt}" if nxt else "")

        return pl.DataFrame(res), nxt
            

            