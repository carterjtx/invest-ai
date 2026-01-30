"""
Constants and investing term definitions for Invest AI Assistant.

This file contains constant values, enumerations, and educational
definitions of investing terms used throughout the application.
"""

from enum import Enum
from typing import Dict

# =============================================================================
# ENUMERATIONS
# =============================================================================


class AssetType(Enum):
    """Types of assets that can be held in a portfolio."""
    STOCK = "stock"           # Individual company shares
    ETF = "etf"               # Exchange-Traded Funds
    CRYPTO = "crypto"         # Cryptocurrencies
    MUTUAL_FUND = "mutual_fund"  # Mutual Funds
    BOND = "bond"             # Bonds


class TransactionType(Enum):
    """Types of transactions that can be recorded."""
    BUY = "buy"               # Purchase of an asset
    SELL = "sell"             # Sale of an asset
    DIVIDEND = "dividend"     # Dividend payment received


class RiskLevel(Enum):
    """Portfolio risk assessment levels."""
    LOW = "low"               # Conservative, well-diversified
    MODERATE = "moderate"     # Balanced risk/reward
    HIGH = "high"             # Aggressive, concentrated
    VERY_HIGH = "very_high"   # Extreme concentration


# =============================================================================
# INVESTING TERM DEFINITIONS
# =============================================================================
# These definitions are used for tooltips throughout the application
# to help beginners understand investing concepts.

INVESTING_TERMS: Dict[str, str] = {
    # Portfolio Basics
    "portfolio": (
        "A collection of investments owned by an individual or organization. "
        "A well-diversified portfolio typically includes different types of "
        "assets to spread risk."
    ),
    "holding": (
        "An individual investment within your portfolio, such as shares of "
        "a specific stock or units of a cryptocurrency."
    ),
    "position": (
        "The amount of a particular security or asset you own. Your position "
        "size affects both potential gains and potential losses."
    ),

    # Price and Value
    "current_price": (
        "The most recent trading price for an asset. For stocks, this is "
        "the last price at which shares were bought or sold on an exchange."
    ),
    "market_value": (
        "The total worth of your holdings calculated as: "
        "Number of shares × Current price per share."
    ),
    "cost_basis": (
        "The original price you paid for an investment, including any fees. "
        "Used to calculate gains or losses when you sell."
    ),
    "average_cost": (
        "Your average purchase price per share, calculated by dividing "
        "total amount invested by total shares owned."
    ),

    # Gains and Losses
    "unrealized_gain": (
        "Paper profit or loss - the difference between current value and "
        "cost basis. It's 'unrealized' because you haven't sold yet."
    ),
    "realized_gain": (
        "Actual profit or loss that occurs when you sell an investment. "
        "This is what gets reported for tax purposes."
    ),
    "total_return": (
        "The complete return on an investment including price appreciation "
        "and any dividends or distributions received."
    ),
    "percent_change": (
        "The percentage increase or decrease in value, calculated as: "
        "((Current Value - Cost Basis) / Cost Basis) × 100"
    ),

    # Diversification
    "diversification": (
        "The practice of spreading investments across different assets, "
        "sectors, and geographies to reduce risk. 'Don't put all your "
        "eggs in one basket.'"
    ),
    "sector": (
        "A segment of the economy containing similar businesses. Examples: "
        "Technology, Healthcare, Energy, Financial Services."
    ),
    "allocation": (
        "How your investment money is distributed across different assets "
        "or asset classes. For example: 60% stocks, 30% bonds, 10% crypto."
    ),
    "concentration_risk": (
        "The risk that comes from having too much of your portfolio in "
        "a single investment or sector. If that one area declines, your "
        "whole portfolio suffers."
    ),

    # Risk Metrics
    "volatility": (
        "A measure of how much an investment's price fluctuates. Higher "
        "volatility means bigger price swings (both up and down)."
    ),
    "risk_assessment": (
        "An evaluation of how risky your portfolio is based on factors "
        "like diversification, volatility, and concentration."
    ),
    "beta": (
        "A measure of how much a stock moves relative to the overall market. "
        "Beta > 1 means more volatile than the market; < 1 means less volatile."
    ),

    # Dividends
    "dividend": (
        "A payment made by a company to its shareholders, usually from "
        "profits. Dividends provide regular income from your investments."
    ),
    "dividend_yield": (
        "The annual dividend payment divided by the stock price, expressed "
        "as a percentage. A 3% yield means you receive $3 per year for "
        "every $100 invested."
    ),
    "ex_dividend_date": (
        "The date by which you must own a stock to receive its upcoming "
        "dividend payment. Buy before this date to get the dividend."
    ),

    # Benchmarks
    "benchmark": (
        "A standard or reference point used to measure portfolio performance. "
        "The S&P 500 is a common benchmark for U.S. stock portfolios."
    ),
    "sp500": (
        "The S&P 500 is an index of 500 large U.S. companies. It's widely "
        "used as a benchmark for the overall U.S. stock market."
    ),
    "index": (
        "A measurement of a section of the stock market, calculated from "
        "the prices of selected stocks. Examples: S&P 500, NASDAQ, Dow Jones."
    ),
    "alpha": (
        "The excess return of an investment relative to its benchmark. "
        "Positive alpha means you're outperforming; negative means underperforming."
    ),

    # Asset Types
    "stock": (
        "A share of ownership in a company. When you buy stock, you become "
        "a partial owner and may receive dividends and voting rights."
    ),
    "etf": (
        "Exchange-Traded Fund - A basket of securities (like stocks or bonds) "
        "that trades on an exchange like a single stock. ETFs offer instant "
        "diversification."
    ),
    "crypto": (
        "Cryptocurrency - Digital or virtual currency that uses cryptography "
        "for security. Examples: Bitcoin (BTC), Ethereum (ETH). Highly volatile."
    ),
    "mutual_fund": (
        "A pooled investment vehicle managed by professionals. Investors buy "
        "shares of the fund, which holds a diversified portfolio of securities."
    ),
    "bond": (
        "A loan you make to a government or corporation. They pay you regular "
        "interest and return your principal at maturity. Generally lower risk "
        "than stocks."
    ),

    # Trading Terms
    "ticker_symbol": (
        "A unique series of letters representing a publicly traded company "
        "or asset. Examples: AAPL (Apple), MSFT (Microsoft), BTC-USD (Bitcoin)."
    ),
    "market_cap": (
        "Market Capitalization - The total value of a company's outstanding "
        "shares. Calculated as: Share price × Total shares outstanding."
    ),
    "volume": (
        "The number of shares or units traded during a specific period. "
        "High volume often indicates strong investor interest."
    ),
}

# =============================================================================
# RISK THRESHOLDS
# =============================================================================

# Concentration thresholds for risk assessment
CONCENTRATION_THRESHOLDS = {
    "single_holding_warning": 0.25,    # Warn if one holding > 25% of portfolio
    "single_holding_danger": 0.40,     # Danger if one holding > 40%
    "single_sector_warning": 0.40,     # Warn if one sector > 40%
    "single_sector_danger": 0.60,      # Danger if one sector > 60%
    "min_holdings_diversified": 5,     # Need at least 5 holdings for diversification
    "min_sectors_diversified": 3,      # Need at least 3 sectors for diversification
}

# =============================================================================
# CRYPTO SYMBOLS MAPPING
# =============================================================================
# Common cryptocurrency symbols and their Yahoo Finance tickers

CRYPTO_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "SOL": "SOL-USD",
    "DOT": "DOT-USD",
    "MATIC": "MATIC-USD",
    "SHIB": "SHIB-USD",
    "LTC": "LTC-USD",
    "AVAX": "AVAX-USD",
    "LINK": "LINK-USD",
    "UNI": "UNI-USD",
    "ATOM": "ATOM-USD",
}

# =============================================================================
# TIME PERIODS
# =============================================================================

# Historical data periods for charts
TIME_PERIODS = {
    "1D": "1d",     # 1 day
    "1W": "5d",     # 1 week (5 trading days)
    "1M": "1mo",    # 1 month
    "3M": "3mo",    # 3 months
    "6M": "6mo",    # 6 months
    "1Y": "1y",     # 1 year
    "5Y": "5y",     # 5 years
    "MAX": "max",   # Maximum available
}

# Date format for display
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# SECTORS
# =============================================================================

# Sector categories for portfolio analysis
SECTORS = [
    "Technology",
    "Healthcare",
    "Financial Services",
    "Consumer Cyclical",
    "Consumer Defensive",
    "Energy",
    "Utilities",
    "Industrials",
    "Basic Materials",
    "Real Estate",
    "Communication Services",
    "Crypto",
    "Other",
]

# =============================================================================
# BENCHMARK INDEXES
# =============================================================================

# Popular benchmark indexes for comparison
BENCHMARK_INDEXES = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Russell 2000": "^RUT",
    "Total Market (VTI)": "VTI",
}
