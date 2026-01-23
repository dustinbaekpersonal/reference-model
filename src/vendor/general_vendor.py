from abc import ABC

class GeneralVendorApi(ABC):
    """
    Api for general vendor that handles header and etc.
    """

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
        self.header = {"Content-Type": "application/json"}
    
    