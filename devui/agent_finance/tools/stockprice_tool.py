import json
import yfinance as yf
from typing import Annotated

# Retrieve Tesla's stock price data from January 2024 to the current date
def get_stock_price_range(
        stock_ticker: Annotated[str, "The stock ticker symbol to fetch data for."], 
        start_date: Annotated[str, "The start date for the data retrieval (YYYY-MM-DD)."], 
        end_date: Annotated[str, "The end date for the data retrieval (YYYY-MM-DD). If None, defaults to the current date."] = None) -> str:
    """
    Fetches the stock price data for a given stock ticker within a specified date range.

    :param stock_ticker: The stock ticker symbol to fetch data for.
    :param start_date: The start date for the data retrieval (YYYY-MM-DD).
    :param end_date: The end date for the data retrieval (YYYY-MM-DD). If None, defaults to the current date.
    :return: A string containing the stock price data.
    """
    print(f"tool: getting stock price for {stock_ticker} from {start_date} to {end_date}")

    tesla_data = yf.download(stock_ticker, start=start_date, end=end_date)

    try:
        
        body = []
        #body.append("date,open,high,low,close,volume")
        #for index, row in tesla_data.iterrows():
        #    body.append(f"{index.date()},{row['Open'][0]:.6f},{row['High'][0]:.6f},{row['Low'][0]:.6f},{row['Close'][0]:.6f},{row['Volume'][0]:.6f}")
        body.append("date,open,close")
        for index, row in tesla_data.iterrows():
            body.append(f"{index.date()},{row['Open'][0]:.6f},{row['Close'][0]:.6f}")
        body_str = "\n".join(body)
        return body_str
    
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

def get_stock_price_current(
        stock_ticker: Annotated[str, "The stock ticker symbol to fetch data for."]
    ) -> str:
    """
    Fetches the current stock price data for a given stock ticker.

    :param stock_ticker: The stock ticker symbol to fetch data for.
    :return: A string containing the current stock price data.
    """
    print(f"tool: getting current stock price for {stock_ticker}")

    stock_data = yf.Ticker(stock_ticker)

    try:

        return json.dumps({"stock_symbol": stock_ticker, "current_price": stock_data.info["currentPrice"]})

    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

def get_currency_rate_current(
        currency_pair: Annotated[str, "The currency pair to fetch data for (e.g., \"USDKRW, EURUSD, USDJPY\")."]
    ) -> str:
    """
    Fetches the current currency exchange rate for a given currency pair.

    :param currency_pair: The currency pair to fetch data for (e.g., "USDKRW, EURUSD, USDJPY").
    :return: A string containing the current currency exchange rate.
    """
    print(f"tool: getting current currency rate for {currency_pair}")

    currency_data = yf.Ticker(f"{currency_pair}=X")

    try:

        return json.dumps({"currency_pair": currency_pair, "current_rate": currency_data.info["open"]})

    except Exception as e:
        return f"Error fetching currency data: {str(e)}"


if __name__ == "__main__":
    #print(get_stock_price_range("TSLA", "2024-05-01"))

    print(get_stock_price_current("TSLA"))
    
    print(get_currency_rate_current("USDKRW"))