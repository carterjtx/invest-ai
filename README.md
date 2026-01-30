# Invest AI Assistant

A Python desktop application for tracking investment portfolios with AI-powered educational assistance.

> **DISCLAIMER**: This application is for **EDUCATIONAL PURPOSES ONLY** and should not be considered financial advice. Always consult with a qualified financial advisor before making investment decisions.

## Features

### Core Portfolio Management
- **Portfolio Tracker**: Track stocks, ETFs, cryptocurrencies, mutual funds, and bonds
- **Real-time Prices**: Automatic price updates via Yahoo Finance
- **Gains/Losses**: Calculate unrealized gains and losses with percentage changes
- **Transaction History**: Record buy, sell, and dividend transactions

### Analysis & Visualization
- **Sector Allocation**: Pie charts showing portfolio breakdown by sector
- **Asset Type Allocation**: View distribution across different asset classes
- **Risk Assessment**: Automated diversification analysis with warnings
- **Historical Charts**: Track portfolio value over time
- **Benchmark Comparison**: Compare performance against S&P 500 and other indexes

### Dividend Tracking
- **Record Dividends**: Log dividend payments received
- **Yield Calculation**: Calculate portfolio dividend yield
- **Annual Income**: Project yearly dividend income
- **Payment History**: View complete dividend history

### News Integration
- **Market Headlines**: Stay updated with general market news
- **Holding-specific News**: Get news for your specific investments
- **Contextual Updates**: Understand price movements with relevant news

### AI Assistant
- **Investment Education**: Learn about investing concepts
- **Portfolio Analysis**: Get AI-powered insights on your portfolio
- **Term Explanations**: Understand investing terminology
- **Diversification Advice**: Educational guidance on spreading risk

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone or download the repository**
   ```bash
   cd invest-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys** (optional but recommended)

   Edit `config.py` or set environment variables:
   ```bash
   # For news headlines
   export NEWS_API_KEY="your_newsapi_key"

   # For AI assistant
   export ANTHROPIC_API_KEY="your_anthropic_key"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## API Keys

The application works with or without API keys, but some features require them:

### Required for Full Functionality

| API | Purpose | Get Key |
|-----|---------|---------|
| Yahoo Finance | Stock/crypto prices | No key needed (uses yfinance) |
| NewsAPI | Financial news headlines | [newsapi.org](https://newsapi.org/register) (free tier) |
| Anthropic (Claude) | AI investment assistant | [console.anthropic.com](https://console.anthropic.com/) |

### Setting Up API Keys

**Option 1: Environment Variables** (recommended for security)
```bash
export NEWS_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
```

**Option 2: Edit config.py**
```python
NEWS_API_KEY = "your_key_here"
ANTHROPIC_API_KEY = "your_key_here"
```

## Usage Guide

### Adding Holdings

1. Go to the **Portfolio** tab
2. Click **"+ Add Holding"**
3. Enter the ticker symbol (e.g., AAPL, MSFT, BTC-USD)
4. Click **"Lookup"** to auto-fill company details
5. Enter your quantity and purchase price
6. Click **"Add"**

### Viewing Analysis

1. Go to the **Analysis** tab
2. View sector and asset type allocation charts
3. Check risk assessment and warnings
4. View top holdings by weight

### Getting News

1. Go to **Analysis** > **News** sub-tab
2. Click **"Refresh News"**
3. View market headlines and holding-specific news

### Using AI Assistant

1. Go to the **AI Assistant** tab
2. Type your question or use quick action buttons
3. Ask about:
   - Investment concepts
   - Your portfolio analysis
   - Term definitions
   - Diversification strategies

### Recording Dividends

1. Go to the **Portfolio** tab
2. Click **"Record Dividend"**
3. Select the symbol, enter amount and date
4. View dividend history in **Analysis** > **Dividends**

## Project Structure

```
invest-ai/
├── main.py                 # Application entry point
├── config.py               # Configuration and API keys
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── data/                   # Data storage
│   ├── portfolio.json      # Portfolio data
│   ├── settings.json       # User settings
│   └── backups/            # Automatic backups
│
├── logs/                   # Application logs
│
└── src/
    ├── models/             # Data models
    │   ├── portfolio.py    # Portfolio model
    │   ├── holding.py      # Individual holding
    │   └── transaction.py  # Transaction record
    │
    ├── services/           # Business logic
    │   ├── data_service.py # JSON persistence
    │   ├── price_service.py # Yahoo Finance API
    │   ├── news_service.py # NewsAPI integration
    │   └── ai_service.py   # Claude AI integration
    │
    ├── gui/                # User interface
    │   ├── main_window.py  # Main application window
    │   ├── portfolio_tab.py # Portfolio management
    │   ├── analysis_tab.py # Charts and analysis
    │   ├── chat_tab.py     # AI chat interface
    │   └── widgets.py      # Custom UI components
    │
    └── utils/              # Utilities
        ├── constants.py    # Constants and definitions
        └── calculations.py # Financial calculations
```

## Supported Asset Types

- **Stocks**: Individual company shares (AAPL, MSFT, etc.)
- **ETFs**: Exchange-traded funds (SPY, QQQ, VTI, etc.)
- **Cryptocurrencies**: Digital currencies (BTC-USD, ETH-USD, etc.)
- **Mutual Funds**: Investment funds (use ticker symbol)
- **Bonds**: Fixed-income securities

## Data Storage

- Portfolio data is stored locally in `data/portfolio.json`
- Automatic backups are created before each save
- Export to CSV available for spreadsheet analysis
- No data is sent to external servers (except for API calls)

## Troubleshooting

### "No module named 'tkinter'"
Install tkinter for your Python version:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **macOS**: Usually included with Python from python.org
- **Windows**: Included with standard Python installation

### "yfinance not working"
Update to the latest version:
```bash
pip install --upgrade yfinance
```

### "Charts not showing"
Install matplotlib:
```bash
pip install matplotlib
```

### "News not loading"
- Check your NEWS_API_KEY in config.py
- Free tier has rate limits (1000 requests/day)

## Contributing

This is an educational project. Contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Disclaimer

**This application is for EDUCATIONAL PURPOSES ONLY.**

- Past performance does not guarantee future results
- All investments carry risk, including potential loss of principal
- Always consult with a qualified financial advisor
- The creators are not responsible for any financial losses
- Information provided should not be considered investment advice

---

Built with Python, Tkinter, and Claude AI
