import requests
import yaml
import logging
import os
from pathlib import Path
from hyperliquid import Client

logger = logging.getLogger(__name__)

# Load secrets from config/secrets.yaml
secrets_path = Path(__file__).parent.parent / "config" / "secrets.yaml"
if secrets_path.is_file():
    with open(secrets_path, "r") as f:
        secrets = yaml.safe_load(f)
        HL_API_KEY = secrets.get("HL_API_KEY", "")
        HL_API_SECRET = secrets.get("HL_API_SECRET", "")
        CG_API_KEY = secrets.get("CG_API_KEY", "")
else:
    # If no secrets.yaml found, set to empty or environment variables
    HL_API_KEY = os.getenv("HL_API_KEY", "")
    HL_API_SECRET = os.getenv("HL_API_SECRET", "")
    CG_API_KEY = os.getenv("CG_API_KEY", "")


class DataFetcher:
    def __init__(self):
        # Initialize HyperLiquid client
        self.hl_client = Client(api_key=HL_API_KEY, secret=HL_API_SECRET)

    def get_hl_orderbook(self, market="BTC-USDT-PERP"):
        """
        Fetch current order book data from HyperLiquid.
        """
        try:
            orderbook = self.hl_client.get_orderbook(market)
            return orderbook
        except Exception as e:
            logger.error(f"Error fetching HL orderbook: {e}")
            return None

    def get_hl_ticker(self, market="BTC-USDT-PERP"):
        """
        Get ticker info (price, etc.) from HyperLiquid.
        """
        try:
            ticker = self.hl_client.get_ticker(market)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching HL ticker: {e}")
            return None

    def get_coingecko_history(self, coin_id="bitcoin", vs_currency="usd", days=30):
        """
        Fetch historical data from Coingecko.
        'days' can be 1,7,14,30,90,180,365, or 'max'.
        """
        base_url = "https://api.coingecko.com/api/v3/"
        endpoint = f"coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        headers = {}

        if CG_API_KEY:
            # If you have a Coingecko Pro API key
            headers["x-cg-pro-api-key"] = CG_API_KEY

        try:
            resp = requests.get(base_url + endpoint, params=params, headers=headers)
            data = resp.json()
            return data
        except Exception as e:
            logger.error(f"Error fetching Coingecko data: {e}")
            return None
