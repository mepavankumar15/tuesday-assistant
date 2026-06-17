"""
LangChain @tool functions for ExchangeRate-API.
Provides live rates and direct currency conversion.
"""
from langchain_core.tools import tool
from config.settings import settings
from utils.logger import logger
import requests


@tool
def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """
    Get the live exchange rate between two ISO 4217 currency codes.

    Args:
        from_currency: Source code e.g. 'USD', 'EUR', 'GBP'
        to_currency:   Target code e.g. 'INR', 'JPY', 'AED'
    """
    try:
        url = (f"{settings.forex_base_url}/{settings.forex_api_key}"
               f"/pair/{from_currency.upper()}/{to_currency.upper()}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        d = resp.json()
        if d.get("result") == "success":
            return {
                "from": from_currency.upper(),
                "to": to_currency.upper(),
                "rate": d["conversion_rate"],
                "last_updated": d["time_last_update_utc"],
            }
        return {"error": d.get("error-type", "API error")}
    except Exception as e:
        logger.error(f"[ForexTool] get_exchange_rate: {e}")
        return {"error": str(e)}


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    Convert a specific monetary amount between two currencies using live rates.

    Args:
        amount:        Amount to convert (e.g. 100.0)
        from_currency: Source currency code (e.g. 'USD')
        to_currency:   Target currency code (e.g. 'INR')
    """
    try:
        url = (f"{settings.forex_base_url}/{settings.forex_api_key}"
               f"/pair/{from_currency.upper()}/{to_currency.upper()}/{amount}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        d = resp.json()
        if d.get("result") == "success":
            return {
                "original_amount": amount,
                "from": from_currency.upper(),
                "to": to_currency.upper(),
                "converted_amount": round(d["conversion_result"], 4),
                "rate": d["conversion_rate"],
                "last_updated": d["time_last_update_utc"],
            }
        return {"error": d.get("error-type", "API error")}
    except Exception as e:
        logger.error(f"[ForexTool] convert_currency: {e}")
        return {"error": str(e)}
