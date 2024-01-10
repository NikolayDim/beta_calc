import yfinance as yf
import pandas as pd


def get_stock_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    if isinstance(data, pd.Series):
        data = pd.DataFrame(data, columns=[tickers])
    return data


def calculate_individual_beta(stock_data, index_data):
    combined_data = pd.concat([stock_data, index_data], axis=1)
    combined_data = combined_data.dropna()
    returns = combined_data.pct_change().dropna()
    covariance = returns.cov().iloc[0, 1]
    variance = returns.iloc[:, 1].var()
    beta = covariance / variance
    return beta


def calculate_portfolio_beta(stock_tickers, stock_weights, start_date, end_date, index_ticker):
    stock_data = get_stock_data(stock_tickers + [index_ticker], start_date, end_date)
    index_data = stock_data[index_ticker]
    portfolio_beta = 0

    for i, ticker in enumerate(stock_tickers):
        individual_stock_data = stock_data[ticker]
        beta = calculate_individual_beta(individual_stock_data, index_data)
        weighted_beta = beta * stock_weights[i]
        portfolio_beta += weighted_beta

    return portfolio_beta


def get_current_prices(tickers):
    data = yf.download(tickers, period='1d')['Adj Close'].iloc[-1]
    return data


def calculate_portfolio_weights(tickers, shares):
    if len(tickers) == 1:
        return [1.0]
    else:
        current_prices = get_current_prices(tickers)
        total_value = sum(current_prices[ticker] * shares[i] for i, ticker in enumerate(tickers))
        weights = [(current_prices[ticker] * shares[i]) / total_value for i, ticker in enumerate(tickers)]
        return weights


def main():
    try:
        index_options = {
            '1': '^GSPC',  # S&P 500
            '2': '^DJI',  # Dow Jones Industrial Average
            '3': '^IXIC',  # NASDAQ Composite
            '4': '^FTSE',  # FTSE 100
            '5': '^N225',  # Nikkei 225
            '6': 'other'  # Custom Ticker
        }

        print("Select the index to compare with:")
        for key, value in index_options.items():
            print(f"{key}: {value}")

        index_choice = input("Enter your choice (1-6): ")

        # Validation for index choice
        while index_choice not in index_options:
            print("Invalid choice. Please enter a number between 1 and 6.")
            index_choice = input("Enter your choice (1-6): ")

        if index_choice == '6':
            index_ticker = input("Enter the custom ticker to compare with: ").upper()
        else:
            index_ticker = index_options[index_choice]

        print("\nEnter the lookback period for beta calculation in the format 'YYYY-MM-DD'.")
        start_date = input("Start date (e.g., 2020-01-01): ")
        end_date = input("End date (e.g., 2021-01-01): ")

        n = int(input("\nEnter the number of stocks in your portfolio: "))
        tickers = []
        shares = []

        for _ in range(n):
            ticker = input("Enter stock ticker: ").upper()
            share = float(input("Enter number of shares owned: "))
            tickers.append(ticker)
            shares.append(share)

        weights = calculate_portfolio_weights(tickers, shares)
        portfolio_beta = calculate_portfolio_beta(tickers, weights, start_date, end_date, index_ticker)

        # Display output
        if len(tickers) == 1:
            print(f"\nBeta of {tickers[0]} (compared to {index_ticker}): {portfolio_beta}")
        else:
            print(f"\nPortfolio Beta (compared to {index_ticker}): {portfolio_beta}")
            for ticker, weight in zip(tickers, weights):
                print(f"{ticker}: Weight {weight:.2%}")

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    main()
