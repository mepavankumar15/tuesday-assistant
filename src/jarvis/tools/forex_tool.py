"""Forex tool — wraps ExchangeRate-API for live currency rates."""
import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential


class ForexInput(BaseModel):
    base_currency: str = Field(..., description="Source currency code, e.g. 'USD'")
    target_currency: str = Field(..., description="Target currency code, e.g. 'INR'")
    amount: float = Field(default=1.0, description="Amount in base currency to convert")


class ForexTool(BaseTool):
    name: str = "ForexTool"
    description: str = (
        "Fetches live currency exchange rates and converts amounts between currencies. "
        "Use currency ISO codes like USD, EUR, INR, GBP, JPY."
    )
    args_schema: type[BaseModel] = ForexInput

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    def _run(self, base_currency: str, target_currency: str, amount: float = 1.0) -> dict:
        api_key = os.environ["FOREX_API_KEY"]
        base = base_currency.upper()
        target = target_currency.upper()

        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base}/{target}/{amount}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("result") != "success":
            raise ValueError(f"Forex API error: {data.get('error-type', 'Unknown error')}")

        rate = data["conversion_rate"]
        converted = data["conversion_result"]

        return {
            "base": base,
            "target": target,
            "rate": rate,
            "amount": amount,
            "converted": round(converted, 4),
            "timestamp": data.get("time_last_update_utc", ""),
            "trend_note": f"1 {base} = {rate} {target}",
        }
