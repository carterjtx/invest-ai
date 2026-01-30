"""
News service for Invest AI Assistant.

Fetches financial news headlines using NewsAPI.
Provides context for price changes in portfolio holdings.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import threading
import json

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Container for a news article."""

    title: str
    description: str
    source: str
    url: str
    published_at: str
    image_url: Optional[str]

    @property
    def published_date(self) -> str:
        """Get formatted publication date."""
        try:
            dt = datetime.fromisoformat(self.published_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            return self.published_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "url": self.url,
            "published_at": self.published_at,
            "image_url": self.image_url,
        }


@dataclass
class CachedNews:
    """Cached news with expiration."""

    articles: List[NewsArticle]
    fetched_at: datetime
    expires_at: datetime


class NewsService:
    """
    Service for fetching financial news.

    Uses NewsAPI for news headlines.
    Implements caching to reduce API calls.
    """

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str, cache_duration_seconds: int = 900):
        """
        Initialize the news service.

        Args:
            api_key: NewsAPI API key
            cache_duration_seconds: How long to cache news (default 15 min)
        """
        self.api_key = api_key
        self.cache_duration = timedelta(seconds=cache_duration_seconds)
        self._cache: Dict[str, CachedNews] = {}
        self._lock = threading.Lock()

        if not REQUESTS_AVAILABLE:
            logger.warning(
                "requests library not installed. News fetching will not work. "
                "Install with: pip install requests"
            )

    def is_available(self) -> bool:
        """Check if the news service is available and configured."""
        return (
            REQUESTS_AVAILABLE
            and self.api_key
            and self.api_key != "your_newsapi_key_here"
        )

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Make a request to NewsAPI.

        Args:
            endpoint: API endpoint (e.g., 'everything', 'top-headlines')
            params: Query parameters

        Returns:
            Response JSON or None if failed
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return None

        if not self.api_key or self.api_key == "your_newsapi_key_here":
            logger.warning("NewsAPI key not configured")
            return None

        try:
            url = f"{self.BASE_URL}/{endpoint}"
            params["apiKey"] = self.api_key

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 401:
                logger.error("Invalid NewsAPI key")
                return None

            if response.status_code == 429:
                logger.warning("NewsAPI rate limit exceeded")
                return None

            if response.status_code != 200:
                logger.error(f"NewsAPI error: {response.status_code}")
                return None

            return response.json()

        except requests.RequestException as e:
            logger.error(f"News request failed: {e}")
            return None

    # =========================================================================
    # NEWS FETCHING
    # =========================================================================

    def get_news_for_symbol(
        self,
        symbol: str,
        company_name: Optional[str] = None,
        max_articles: int = 5,
        force_refresh: bool = False,
    ) -> List[NewsArticle]:
        """
        Get news articles related to a stock symbol.

        Args:
            symbol: Ticker symbol
            company_name: Company name for better search results
            max_articles: Maximum number of articles to return
            force_refresh: Ignore cache and fetch fresh data

        Returns:
            List of NewsArticle objects
        """
        cache_key = f"symbol_{symbol.upper()}"

        # Check cache
        if not force_refresh:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached[:max_articles]

        # Build search query
        # Use company name if provided, otherwise use symbol
        query = company_name if company_name else symbol

        # Search for news
        articles = self._search_news(query, max_articles)

        # Cache results
        if articles:
            self._add_to_cache(cache_key, articles)

        return articles

    def get_market_news(
        self,
        max_articles: int = 10,
        force_refresh: bool = False,
    ) -> List[NewsArticle]:
        """
        Get general market news.

        Args:
            max_articles: Maximum number of articles to return
            force_refresh: Ignore cache and fetch fresh data

        Returns:
            List of NewsArticle objects
        """
        cache_key = "market_news"

        # Check cache
        if not force_refresh:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached[:max_articles]

        # Fetch top business headlines
        articles = self._get_top_headlines("business", max_articles)

        # Cache results
        if articles:
            self._add_to_cache(cache_key, articles)

        return articles

    def get_crypto_news(
        self,
        max_articles: int = 10,
        force_refresh: bool = False,
    ) -> List[NewsArticle]:
        """
        Get cryptocurrency news.

        Args:
            max_articles: Maximum number of articles to return
            force_refresh: Ignore cache and fetch fresh data

        Returns:
            List of NewsArticle objects
        """
        cache_key = "crypto_news"

        # Check cache
        if not force_refresh:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached[:max_articles]

        # Search for crypto news
        articles = self._search_news(
            "cryptocurrency OR bitcoin OR ethereum",
            max_articles,
        )

        # Cache results
        if articles:
            self._add_to_cache(cache_key, articles)

        return articles

    def _search_news(
        self,
        query: str,
        max_articles: int = 10,
        days_back: int = 7,
    ) -> List[NewsArticle]:
        """
        Search for news articles.

        Args:
            query: Search query
            max_articles: Maximum articles to return
            days_back: How many days back to search

        Returns:
            List of NewsArticle objects
        """
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        params = {
            "q": query,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": max_articles,
        }

        response = self._make_request("everything", params)

        if not response or response.get("status") != "ok":
            return []

        return self._parse_articles(response.get("articles", []))

    def _get_top_headlines(
        self,
        category: str = "business",
        max_articles: int = 10,
        country: str = "us",
    ) -> List[NewsArticle]:
        """
        Get top headlines for a category.

        Args:
            category: News category (business, technology, etc.)
            max_articles: Maximum articles to return
            country: Country code for headlines

        Returns:
            List of NewsArticle objects
        """
        params = {
            "category": category,
            "country": country,
            "pageSize": max_articles,
        }

        response = self._make_request("top-headlines", params)

        if not response or response.get("status") != "ok":
            return []

        return self._parse_articles(response.get("articles", []))

    def _parse_articles(self, articles_data: List[Dict]) -> List[NewsArticle]:
        """
        Parse raw article data into NewsArticle objects.

        Args:
            articles_data: Raw article data from API

        Returns:
            List of NewsArticle objects
        """
        articles = []
        for article in articles_data:
            try:
                news_article = NewsArticle(
                    title=article.get("title", "No title"),
                    description=article.get("description", "") or "",
                    source=article.get("source", {}).get("name", "Unknown"),
                    url=article.get("url", ""),
                    published_at=article.get("publishedAt", ""),
                    image_url=article.get("urlToImage"),
                )
                articles.append(news_article)
            except Exception as e:
                logger.warning(f"Failed to parse article: {e}")
                continue

        return articles

    # =========================================================================
    # PORTFOLIO NEWS
    # =========================================================================

    def get_portfolio_news(
        self,
        holdings: List[Dict[str, str]],
        max_articles_per_holding: int = 3,
    ) -> Dict[str, List[NewsArticle]]:
        """
        Get news for all holdings in a portfolio.

        Args:
            holdings: List of dicts with 'symbol' and 'name' keys
            max_articles_per_holding: Max articles per holding

        Returns:
            Dictionary mapping symbols to news articles
        """
        news_by_symbol = {}

        for holding in holdings:
            symbol = holding.get("symbol", "")
            name = holding.get("name", "")

            articles = self.get_news_for_symbol(
                symbol=symbol,
                company_name=name,
                max_articles=max_articles_per_holding,
            )

            if articles:
                news_by_symbol[symbol] = articles

        return news_by_symbol

    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================

    def _get_from_cache(self, key: str) -> Optional[List[NewsArticle]]:
        """Get news from cache if valid."""
        with self._lock:
            if key in self._cache:
                cached = self._cache[key]
                if datetime.now() < cached.expires_at:
                    return cached.articles
                else:
                    del self._cache[key]
        return None

    def _add_to_cache(self, key: str, articles: List[NewsArticle]) -> None:
        """Add news to cache."""
        with self._lock:
            now = datetime.now()
            self._cache[key] = CachedNews(
                articles=articles,
                fetched_at=now,
                expires_at=now + self.cache_duration,
            )

    def clear_cache(self) -> None:
        """Clear all cached news."""
        with self._lock:
            self._cache.clear()


class MockNewsService(NewsService):
    """
    Mock news service for testing and demo purposes.

    Returns sample news articles without making API calls.
    """

    def __init__(self):
        """Initialize mock service (no API key needed)."""
        super().__init__(api_key="mock", cache_duration_seconds=60)

    def is_available(self) -> bool:
        """Mock service is always available."""
        return True

    def _search_news(
        self,
        query: str,
        max_articles: int = 10,
        days_back: int = 7,
    ) -> List[NewsArticle]:
        """Return mock news articles."""
        return [
            NewsArticle(
                title=f"Market Update: {query} Shows Strong Performance",
                description=f"Investors are watching {query} closely as the market continues to evolve.",
                source="Mock Financial News",
                url="https://example.com/news/1",
                published_at=datetime.now().isoformat(),
                image_url=None,
            ),
            NewsArticle(
                title=f"Analysts Weigh In on {query} Outlook",
                description=f"Financial experts share their predictions for {query} in the coming months.",
                source="Mock Investment Daily",
                url="https://example.com/news/2",
                published_at=(datetime.now() - timedelta(hours=5)).isoformat(),
                image_url=None,
            ),
        ][:max_articles]

    def _get_top_headlines(
        self,
        category: str = "business",
        max_articles: int = 10,
        country: str = "us",
    ) -> List[NewsArticle]:
        """Return mock headlines."""
        return [
            NewsArticle(
                title="Markets Rally on Economic Data",
                description="Stock markets showed strength today following positive economic indicators.",
                source="Mock Business News",
                url="https://example.com/news/market",
                published_at=datetime.now().isoformat(),
                image_url=None,
            ),
            NewsArticle(
                title="Fed Signals Policy Direction",
                description="Federal Reserve officials provided guidance on future monetary policy.",
                source="Mock Financial Times",
                url="https://example.com/news/fed",
                published_at=(datetime.now() - timedelta(hours=3)).isoformat(),
                image_url=None,
            ),
        ][:max_articles]
