"""
Price service for Invest AI Assistant.

Fetches real-time and historical price data using Yahoo Finance (yfinance).
Includes caching to reduce API calls and improve performance.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import threading
import time

# yfinance is imported lazily to handle installation issues gracefully
try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Container for price data from an API call."""

    symbol: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    day_high: float
    day_low: float
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    timestamp: str

    @property
    def is_positive(self) -> bool:
        """Check if the price change is positive."""
        return self.change >= 0


@dataclass
class StockInfo:
    """Container for detailed stock information."""

    symbol: str
    name: str
    sector: str
    industry: str
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    beta: Optional[float]
    description: str


@dataclass
class CachedPrice:
    """Cached price data with expiration."""

    data: PriceData
    fetched_at: datetime
    expires_at: datetime


class PriceService:
    """
    Service for fetching stock and cryptocurrency prices.

    Uses Yahoo Finance (yfinance) for price data.
    Implements caching to reduce API calls.
    """

    def __init__(self, cache_duration_seconds: int = 60):
        """
        Initialize the price service.

        Args:
            cache_duration_seconds: How long to cache prices (default 60s)
        """
        self.cache_duration = timedelta(seconds=cache_duration_seconds)
        self._price_cache: Dict[str, CachedPrice] = {}
        self._info_cache: Dict[str, StockInfo] = {}
        self._lock = threading.Lock()

        if not YFINANCE_AVAILABLE:
            logger.warning(
                "yfinance not installed. Price fetching will not work. "
                "Install with: pip install yfinance"
            )

    def is_available(self) -> bool:
        """Check if the price service is available."""
        return YFINANCE_AVAILABLE

    # =========================================================================
    # PRICE FETCHING
    # =========================================================================

    def get_price(self, symbol: str, force_refresh: bool = False) -> Optional[PriceData]:
        """
        Get current price for a symbol.

        Args:
            symbol: Ticker symbol (e.g., 'AAPL', 'BTC-USD')
            force_refresh: Ignore cache and fetch fresh data

        Returns:
            PriceData object or None if fetch failed
        """
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance not available")
            return None

        symbol = symbol.upper()

        # Check cache first
        if not force_refresh:
            cached = self._get_from_cache(symbol)
            if cached:
                return cached

        try:
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or "regularMarketPrice" not in info:
                # Try fast_info for basic data
                fast_info = ticker.fast_info
                if hasattr(fast_info, "last_price") and fast_info.last_price:
                    price_data = PriceData(
                        symbol=symbol,
                        current_price=fast_info.last_price,
                        previous_close=getattr(fast_info, "previous_close", fast_info.last_price),
                        change=fast_info.last_price - getattr(fast_info, "previous_close", fast_info.last_price),
                        change_percent=((fast_info.last_price - getattr(fast_info, "previous_close", fast_info.last_price))
                                        / getattr(fast_info, "previous_close", fast_info.last_price) * 100)
                                        if getattr(fast_info, "previous_close", None) else 0,
                        volume=getattr(fast_info, "last_volume", 0) or 0,
                        market_cap=getattr(fast_info, "market_cap", None),
                        day_high=getattr(fast_info, "day_high", fast_info.last_price) or fast_info.last_price,
                        day_low=getattr(fast_info, "day_low", fast_info.last_price) or fast_info.last_price,
                        fifty_two_week_high=getattr(fast_info, "year_high", None),
                        fifty_two_week_low=getattr(fast_info, "year_low", None),
                        timestamp=datetime.now().isoformat(),
                    )
                    self._add_to_cache(symbol, price_data)
                    return price_data
                else:
                    logger.warning(f"No price data available for {symbol}")
                    return None

            # Extract price data from info
            current_price = info.get("regularMarketPrice", 0)
            previous_close = info.get("regularMarketPreviousClose", current_price)

            price_data = PriceData(
                symbol=symbol,
                current_price=current_price,
                previous_close=previous_close,
                change=info.get("regularMarketChange", 0),
                change_percent=info.get("regularMarketChangePercent", 0),
                volume=info.get("regularMarketVolume", 0) or 0,
                market_cap=info.get("marketCap"),
                day_high=info.get("regularMarketDayHigh", current_price),
                day_low=info.get("regularMarketDayLow", current_price),
                fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
                fifty_two_week_low=info.get("fiftyTwoWeekLow"),
                timestamp=datetime.now().isoformat(),
            )

            # Add to cache
            self._add_to_cache(symbol, price_data)

            return price_data

        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return None

    def get_prices_batch(
        self, symbols: List[str], force_refresh: bool = False
    ) -> Dict[str, Optional[PriceData]]:
        """
        Get prices for multiple symbols efficiently.

        Args:
            symbols: List of ticker symbols
            force_refresh: Ignore cache and fetch fresh data

        Returns:
            Dictionary mapping symbols to PriceData (or None if failed)
        """
        results: Dict[str, Optional[PriceData]] = {}
        symbols_to_fetch = []

        # Check cache for each symbol
        for symbol in symbols:
            symbol = symbol.upper()
            if not force_refresh:
                cached = self._get_from_cache(symbol)
                if cached:
                    results[symbol] = cached
                    continue
            symbols_to_fetch.append(symbol)

        # Fetch remaining symbols
        if symbols_to_fetch:
            for symbol in symbols_to_fetch:
                results[symbol] = self.get_price(symbol, force_refresh=True)
                # Small delay to avoid rate limiting
                time.sleep(0.1)

        return results

    # =========================================================================
    # HISTORICAL DATA
    # =========================================================================

    def get_historical_prices(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get historical price data for charting.

        Args:
            symbol: Ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max)
            interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)

        Returns:
            List of dictionaries with date and OHLCV data
        """
        if not YFINANCE_AVAILABLE:
            return None

        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return None

            # Convert to list of dictionaries
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.isoformat(),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"],
                })

            return data

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            return None

    def get_benchmark_comparison(
        self,
        symbols: List[str],
        benchmark: str = "^GSPC",
        period: str = "1y",
    ) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """
        Get normalized price data for comparison against a benchmark.

        Args:
            symbols: List of ticker symbols to compare
            benchmark: Benchmark symbol (default S&P 500)
            period: Time period for comparison

        Returns:
            Dictionary with normalized price series for each symbol
        """
        if not YFINANCE_AVAILABLE:
            return None

        try:
            all_symbols = [s.upper() for s in symbols] + [benchmark]
            results = {}

            for symbol in all_symbols:
                hist = self.get_historical_prices(symbol, period=period)
                if hist and len(hist) > 0:
                    # Normalize to start at 100
                    first_close = hist[0]["close"]
                    results[symbol] = [
                        {
                            "date": item["date"],
                            "value": (item["close"] / first_close) * 100,
                        }
                        for item in hist
                    ]

            return results if results else None

        except Exception as e:
            logger.error(f"Failed to fetch benchmark comparison: {e}")
            return None

    # =========================================================================
    # STOCK INFORMATION
    # =========================================================================

    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """
        Get detailed information about a stock.

        Args:
            symbol: Ticker symbol

        Returns:
            StockInfo object or None if not found
        """
        if not YFINANCE_AVAILABLE:
            return None

        symbol = symbol.upper()

        # Check cache
        if symbol in self._info_cache:
            return self._info_cache[symbol]

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            stock_info = StockInfo(
                symbol=symbol,
                name=info.get("longName", info.get("shortName", symbol)),
                sector=info.get("sector", "Other"),
                industry=info.get("industry", "Unknown"),
                market_cap=info.get("marketCap"),
                pe_ratio=info.get("trailingPE"),
                dividend_yield=info.get("dividendYield"),
                beta=info.get("beta"),
                description=info.get("longBusinessSummary", ""),
            )

            # Cache the info
            self._info_cache[symbol] = stock_info

            return stock_info

        except Exception as e:
            logger.error(f"Failed to fetch info for {symbol}: {e}")
            return None

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """
        Search for a symbol by name or partial symbol.

        Note: Yahoo Finance doesn't have a great search API,
        so this is a basic implementation.

        Args:
            query: Search query

        Returns:
            List of matching symbols with names
        """
        if not YFINANCE_AVAILABLE:
            return []

        # For now, just try to get info for the query as a symbol
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info and "shortName" in info:
                return [{
                    "symbol": query.upper(),
                    "name": info.get("shortName", query),
                    "type": info.get("quoteType", "EQUITY"),
                }]
        except Exception:
            pass

        return []

    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================

    def _get_from_cache(self, symbol: str) -> Optional[PriceData]:
        """Get price from cache if valid."""
        with self._lock:
            if symbol in self._price_cache:
                cached = self._price_cache[symbol]
                if datetime.now() < cached.expires_at:
                    return cached.data
                else:
                    # Cache expired, remove it
                    del self._price_cache[symbol]
        return None

    def _add_to_cache(self, symbol: str, data: PriceData) -> None:
        """Add price data to cache."""
        with self._lock:
            now = datetime.now()
            self._price_cache[symbol] = CachedPrice(
                data=data,
                fetched_at=now,
                expires_at=now + self.cache_duration,
            )

    def clear_cache(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._price_cache.clear()
            self._info_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "price_cache_size": len(self._price_cache),
                "info_cache_size": len(self._info_cache),
                "cached_symbols": list(self._price_cache.keys()),
            }
