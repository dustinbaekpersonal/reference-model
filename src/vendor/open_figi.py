
from .general_vendor import GeneralVendorApi

class OpenFigiApi(GeneralVendorApi):
    def __init__(self, base_url: str, api_key: str | None = None):
        super().__init__(base_url, api_key)
        if self.api_key:
            self.header |= {"X-OPENFIGI-APIKEY": self.api_key}

    
    