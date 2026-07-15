import os
import httpx
from langchain_core.tools import tool

@tool
def get_forex_rate(query: str) -> str:
    """
    Get live foreign exchange rate between two currencies.
    Input: natural language like 'USD to INR', 'EUR to GBP', '100 USD to JPY'.
    Returns: current exchange rate and converted amount if specified.
    Common currency codes: USD, EUR, GBP, INR, JPY, AUD, CAD, CHF, CNY, SGD, AED.
    """
    try:
        # Parse currency codes from the query
        query_upper = query.upper()
        words = query_upper.split()
        
        # Find currency codes (3-letter codes)
        codes = [w for w in words if len(w) == 3 and w.isalpha()]
        amount = 1.0
        for w in words:
            try:
                amount = float(w)
                break
            except ValueError:
                continue
        
        if len(codes) < 2:
            return "Please specify two currency codes, e.g. 'USD to INR' or '100 EUR to GBP'."
        
        base, target = codes[0], codes[1]
        
        api_key = os.getenv("EXCHANGERATE_API_KEY")
        
        # Try ExchangeRate-API (free endpoint doesn't need key, paid does)
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        rates = data.get("rates", {})
        if target not in rates:
            return f"Currency code '{target}' not found. Use standard 3-letter codes like USD, EUR, INR."
        
        rate = rates[target]
        converted = amount * rate
        
        return (
            f"Exchange rate: 1 {base} = {rate:.4f} {target}. "
            f"{amount:,.2f} {base} = {converted:,.2f} {target}. "
            f"(Rates updated: {data.get('date', 'today')})"
        )
    except httpx.HTTPStatusError as e:
        return f"Forex API error: {str(e)}"
    except Exception as e:
        return f"Error fetching forex rate: {str(e)}"
