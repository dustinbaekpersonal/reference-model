import httpx
import polars as pl
from bs4 import BeautifulSoup

from .general_vendor import GeneralVendorApi


class OpenFigiApi(GeneralVendorApi):
    def __init__(self, base_url: str, api_key: str | None = None):
        super().__init__(base_url, api_key)
        if self.api_key:
            self.header |= {"X-OPENFIGI-APIKEY": self.api_key}

    @staticmethod
    def get_available_symbol_types() -> pl.DataFrame:
        """
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
