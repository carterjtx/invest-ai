"""
Main window for Invest AI Assistant.

The main application window that contains the tab-based navigation
and coordinates all the different views.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import logging
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import configuration
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
from src.models.portfolio import Portfolio
from src.services.data_service import DataService
from src.services.price_service import PriceService
from src.services.news_service import NewsService, MockNewsService
from src.services.ai_service import AIService, MockAIService


class MainWindow:
    """
    Main application window.

    Manages the overall application state, coordinates services,
    and provides the tabbed interface.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.

        Args:
            root: The Tkinter root window
        """
        self.root = root
        self.root.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)

        # Set window icon if available
        try:
            # You could add an icon file here
            pass
        except Exception:
            pass

        # Initialize services
        self._init_services()

        # Load portfolio data
        self.portfolio = self._load_portfolio()

        # Set up the UI
        self._setup_ui()

        # Show disclaimer on first run
        self._show_disclaimer()

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Schedule initial data refresh
        self.root.after(1000, self._refresh_prices)

    def _init_services(self):
        """Initialize all services."""
        # Data service for persistence (must be first to load settings)
        self.data_service = DataService(config.DATA_DIR)

        # Load saved API keys from settings (override config.py defaults)
        settings = self.data_service.load_settings()
        self._anthropic_key = settings.get("anthropic_api_key", "").strip()
        self._news_key = settings.get("news_api_key", "").strip()

        # Fall back to config.py if no saved keys
        if not self._anthropic_key:
            self._anthropic_key = config.ANTHROPIC_API_KEY
        if not self._news_key:
            self._news_key = config.NEWS_API_KEY

        # Price service for stock/crypto prices
        self.price_service = PriceService(
            cache_duration_seconds=config.PRICE_CACHE_DURATION
        )

        # Initialize news and AI services
        self._init_news_service()
        self._init_ai_service()

        logger.info("Services initialized")

    def _init_news_service(self):
        """Initialize or reinitialize the news service."""
        if self._news_key and self._news_key != "your_newsapi_key_here":
            self.news_service = NewsService(
                api_key=self._news_key,
                cache_duration_seconds=config.NEWS_CACHE_DURATION,
            )
            logger.info("News service initialized with API key")
        else:
            logger.info("Using mock news service (NewsAPI key not configured)")
            self.news_service = MockNewsService()

    def _init_ai_service(self):
        """Initialize or reinitialize the AI service."""
        if self._anthropic_key and self._anthropic_key != "your_anthropic_key_here":
            self.ai_service = AIService(api_key=self._anthropic_key)
            logger.info("AI service initialized with API key")
        else:
            logger.info("Using mock AI service (Anthropic key not configured)")
            self.ai_service = MockAIService()

    def reinitialize_services(self):
        """Reinitialize services after API key changes."""
        # Reload settings
        settings = self.data_service.load_settings()
        self._anthropic_key = settings.get("anthropic_api_key", "").strip()
        self._news_key = settings.get("news_api_key", "").strip()

        # Fall back to config.py if no saved keys
        if not self._anthropic_key:
            self._anthropic_key = config.ANTHROPIC_API_KEY
        if not self._news_key:
            self._news_key = config.NEWS_API_KEY

        # Reinitialize services
        self._init_news_service()
        self._init_ai_service()

        # Update status bar
        self._update_status_bar()

        # Refresh chat tab to show updated AI status
        if hasattr(self, 'chat_tab'):
            self.chat_tab._add_welcome_message()

        logger.info("Services reinitialized with updated API keys")

    def _load_portfolio(self) -> Portfolio:
        """Load portfolio from disk or create new one."""
        portfolio = self.data_service.load_portfolio()
        if portfolio is None:
            portfolio = Portfolio()
            logger.info("Created new portfolio")
        else:
            logger.info(f"Loaded portfolio with {portfolio.holdings_count} holdings")
        return portfolio

    def _setup_ui(self):
        """Set up the user interface."""
        # Configure style
        self._setup_styles()

        # Create main container
        self.main_container = ttk.Frame(self.root, padding=10)
        self.main_container.pack(fill="both", expand=True)

        # Create header
        self._create_header()

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True, pady=(10, 0))

        # Create tabs (imported lazily to avoid circular imports)
        self._create_tabs()

        # Create status bar
        self._create_status_bar()

    def _setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()

        # Try to use a modern theme
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass  # Use default theme

        # Configure colors
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TEntry", padding=5)

        # Heading styles
        style.configure("Heading.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Subheading.TLabel", font=("Segoe UI", 12, "bold"))

        # Value display styles
        style.configure("Positive.TLabel", foreground="#16a34a")
        style.configure("Negative.TLabel", foreground="#dc2626")
        style.configure("Neutral.TLabel", foreground="#64748b")

        # Card style
        style.configure("Card.TFrame", relief="solid", borderwidth=1)

    def _create_header(self):
        """Create the application header."""
        header = ttk.Frame(self.main_container)
        header.pack(fill="x", pady=(0, 5))

        # App title
        title = ttk.Label(
            header,
            text=config.APP_NAME,
            style="Heading.TLabel",
        )
        title.pack(side="left")

        # Right side buttons
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side="right")

        # Refresh button
        self.refresh_btn = ttk.Button(
            btn_frame,
            text="Refresh Prices",
            command=self._refresh_prices,
        )
        self.refresh_btn.pack(side="left", padx=5)

        # Save button
        save_btn = ttk.Button(
            btn_frame,
            text="Save",
            command=self._save_portfolio,
        )
        save_btn.pack(side="left", padx=5)

        # Settings button
        settings_btn = ttk.Button(
            btn_frame,
            text="Settings",
            command=self._show_settings,
        )
        settings_btn.pack(side="left")

    def _create_tabs(self):
        """Create the main application tabs."""
        # Import tab classes
        from .portfolio_tab import PortfolioTab
        from .analysis_tab import AnalysisTab
        from .chat_tab import ChatTab

        # Portfolio tab
        self.portfolio_tab = PortfolioTab(self.notebook, self)
        self.notebook.add(self.portfolio_tab, text="  Portfolio  ")

        # Analysis tab
        self.analysis_tab = AnalysisTab(self.notebook, self)
        self.notebook.add(self.analysis_tab, text="  Analysis  ")

        # AI Chat tab
        self.chat_tab = ChatTab(self.notebook, self)
        self.notebook.add(self.chat_tab, text="  AI Assistant  ")

    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_bar = ttk.Frame(self.main_container)
        self.status_bar.pack(fill="x", pady=(10, 0))

        # Status message - preserve existing value if recreating
        current_status = "Ready"
        if hasattr(self, 'status_var'):
            current_status = self.status_var.get()
        self.status_var = tk.StringVar(value=current_status)

        status_label = ttk.Label(
            self.status_bar,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
        )
        status_label.pack(side="left")

        # API status indicators
        api_frame = ttk.Frame(self.status_bar)
        api_frame.pack(side="right")

        # Price API status
        price_status = "OK" if self.price_service.is_available() else "N/A"
        price_color = "#16a34a" if self.price_service.is_available() else "#dc2626"
        ttk.Label(
            api_frame,
            text=f"Prices: {price_status}",
            foreground=price_color,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=10)

        # News API status
        news_status = "OK" if self.news_service.is_available() else "Demo"
        news_color = "#16a34a" if self.news_service.is_available() else "#d97706"
        ttk.Label(
            api_frame,
            text=f"News: {news_status}",
            foreground=news_color,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=10)

        # AI status
        ai_status = "OK" if self.ai_service.is_available() else "Demo"
        ai_color = "#16a34a" if self.ai_service.is_available() else "#d97706"
        ttk.Label(
            api_frame,
            text=f"AI: {ai_status}",
            foreground=ai_color,
            font=("Segoe UI", 9),
        ).pack(side="left")

    def _show_disclaimer(self):
        """Show the disclaimer on first run."""
        settings = self.data_service.load_settings()
        if not settings.get("disclaimer_accepted"):
            result = messagebox.showinfo(
                "Important Disclaimer",
                config.DISCLAIMER,
                icon="warning",
            )
            # Save that disclaimer was shown
            settings["disclaimer_accepted"] = True
            self.data_service.save_settings(settings)

    def _refresh_prices(self):
        """Refresh prices for all holdings."""
        if not self.portfolio.holdings:
            self.set_status("No holdings to refresh")
            return

        self.set_status("Refreshing prices...")
        self.refresh_btn.configure(state="disabled")

        def refresh_thread():
            try:
                symbols = list(self.portfolio.holdings.keys())
                prices = self.price_service.get_prices_batch(symbols, force_refresh=True)

                # Update holdings with new prices
                for symbol, price_data in prices.items():
                    if price_data and symbol in self.portfolio.holdings:
                        self.portfolio.holdings[symbol].update_price(price_data.current_price)

                # Update UI on main thread
                self.root.after(0, self._on_prices_refreshed)

            except Exception as e:
                logger.error(f"Price refresh failed: {e}")
                self.root.after(0, lambda: self.set_status(f"Price refresh failed: {e}"))
                self.root.after(0, lambda: self.refresh_btn.configure(state="normal"))

        thread = threading.Thread(target=refresh_thread, daemon=True)
        thread.start()

    def _on_prices_refreshed(self):
        """Handle completion of price refresh."""
        self.set_status("Prices updated")
        self.refresh_btn.configure(state="normal")

        # Refresh the UI
        self.portfolio_tab.refresh()
        self.analysis_tab.refresh()

        # Take a portfolio snapshot for historical tracking
        self.portfolio.take_snapshot()

    def _save_portfolio(self):
        """Save portfolio to disk."""
        self.set_status("Saving portfolio...")
        if self.data_service.save_portfolio(self.portfolio):
            self.set_status("Portfolio saved successfully")
        else:
            self.set_status("Failed to save portfolio")
            messagebox.showerror("Error", "Failed to save portfolio data")

    def _show_settings(self):
        """Show settings dialog."""
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.root, self)
        self.root.wait_window(dialog)

    def _update_status_bar(self):
        """Update the status bar API indicators."""
        # Recreate the status bar to update indicators
        if hasattr(self, 'status_bar'):
            self.status_bar.destroy()
        self._create_status_bar()

    def _on_close(self):
        """Handle window close event."""
        # Auto-save before closing
        self.data_service.save_portfolio(self.portfolio, create_backup=False)
        self.root.destroy()

    def set_status(self, message: str):
        """Update the status bar message."""
        self.status_var.set(message)
        logger.info(f"Status: {message}")

    def get_portfolio_summary(self) -> str:
        """Get a text summary of the portfolio for AI context."""
        if not self.portfolio.holdings:
            return "Portfolio is empty."

        lines = [f"Portfolio: {self.portfolio.name}"]
        lines.append(f"Holdings: {self.portfolio.holdings_count}")

        total_value = self.portfolio.total_market_value
        if total_value:
            lines.append(f"Total Value: ${total_value:,.2f}")

        total_cost = self.portfolio.total_cost_basis
        if total_cost:
            lines.append(f"Total Cost: ${total_cost:,.2f}")

        gain = self.portfolio.total_unrealized_gain
        if gain is not None:
            gain_pct = self.portfolio.total_unrealized_gain_percent or 0
            lines.append(f"Unrealized Gain: ${gain:,.2f} ({gain_pct:+.1f}%)")

        # Add holdings summary
        lines.append("\nHoldings:")
        for holding in self.portfolio.get_all_holdings():
            value = holding.market_value or holding.cost_basis
            lines.append(f"  - {holding.symbol}: {holding.quantity} shares, ${value:,.2f}")

        return "\n".join(lines)


def run_app():
    """Run the application."""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
