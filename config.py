"""
Configuration file for Invest AI Assistant.

This file contains API keys and configuration settings.
For security, consider using environment variables in production.

IMPORTANT: Never commit real API keys to version control!
"""

import os
from pathlib import Path

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Application name and version
APP_NAME = "Invest AI Assistant"
APP_VERSION = "1.0.0"

# Base directory for the application
BASE_DIR = Path(__file__).parent.absolute()

# Data directory for storing portfolio and historical data
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# =============================================================================
# API KEYS
# =============================================================================
#
# To use this application, you'll need to obtain API keys from:
# 1. NewsAPI: https://newsapi.org/ (free tier available)
# 2. Anthropic (Claude): https://console.anthropic.com/ (requires account)
#
# You can set these as environment variables or replace the defaults below.
# Environment variables are more secure and recommended for production use.
# =============================================================================

# NewsAPI key for fetching financial news headlines
# Sign up at: https://newsapi.org/register
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "your_newsapi_key_here")

# Anthropic API key for Claude AI assistant
# Sign up at: https://console.anthropic.com/
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your_anthropic_key_here")

# =============================================================================
# API ENDPOINTS
# =============================================================================

# Yahoo Finance API (free, no key required)
# We use yfinance library which handles this automatically
YAHOO_FINANCE_ENABLED = True

# NewsAPI endpoint
NEWS_API_BASE_URL = "https://newsapi.org/v2"

# =============================================================================
# RATE LIMITING SETTINGS
# =============================================================================

# Maximum API calls per minute (to avoid rate limiting)
MAX_PRICE_CALLS_PER_MINUTE = 5
MAX_NEWS_CALLS_PER_MINUTE = 10

# Cache duration in seconds
PRICE_CACHE_DURATION = 60  # 1 minute for real-time prices
NEWS_CACHE_DURATION = 900  # 15 minutes for news

# =============================================================================
# DEFAULT PORTFOLIO SETTINGS
# =============================================================================

# Default currency for portfolio valuation
DEFAULT_CURRENCY = "USD"

# Supported asset types
ASSET_TYPES = ["stock", "etf", "crypto", "mutual_fund", "bond"]

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

# =============================================================================
# SECTOR MAPPINGS
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
# UI SETTINGS
# =============================================================================

# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 600

# Color scheme (light theme)
COLORS = {
    "primary": "#2563eb",      # Blue
    "secondary": "#64748b",    # Slate
    "success": "#16a34a",      # Green
    "danger": "#dc2626",       # Red
    "warning": "#d97706",      # Amber
    "background": "#f8fafc",   # Light gray
    "surface": "#ffffff",      # White
    "text": "#1e293b",         # Dark slate
    "text_secondary": "#64748b", # Medium slate
    "border": "#e2e8f0",       # Light border
}

# Font settings
FONTS = {
    "heading": ("Segoe UI", 14, "bold"),
    "subheading": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "monospace": ("Consolas", 10),
}

# =============================================================================
# DISCLAIMER
# =============================================================================

DISCLAIMER = """
IMPORTANT DISCLAIMER:

This application is for EDUCATIONAL PURPOSES ONLY and should NOT be
considered financial advice.

- Past performance does not guarantee future results
- All investments carry risk, including potential loss of principal
- Always consult with a qualified financial advisor before making
  investment decisions
- The creators of this application are not responsible for any
  financial losses incurred

By using this application, you acknowledge that you understand these
risks and agree to use it at your own discretion.
"""
