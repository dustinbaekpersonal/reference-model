import os

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def main():
    api_key = os.environ.get("marketstack_api_key")
    logger.info("Hello from reference-model!")
    logger.debug(f"API key: {api_key}")


if __name__ == "__main__":
    main()
