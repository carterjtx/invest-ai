"""
Analysis tab for Invest AI Assistant.

Provides charts, sector allocation analysis, risk assessment,
benchmark comparison, and news integration.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, TYPE_CHECKING, List, Dict, Any
import logging
import threading
from datetime import datetime, timedelta

# Import matplotlib for charts
try:
    import matplotlib

    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .widgets import (
    create_tooltip,
    ValueDisplay,
    ScrollableFrame,
)
from ..utils.constants import INVESTING_TERMS, BENCHMARK_INDEXES
from ..utils.calculations import (
    assess_portfolio_risk,
    calculate_allocation,
    calculate_dividend_metrics,
    format_currency,
    format_percent,
)

if TYPE_CHECKING:
    from .main_window import MainWindow

logger = logging.getLogger(__name__)


class AnalysisTab(ttk.Frame):
    """
    Analysis and visualization tab.

    Shows portfolio charts, sector allocation, risk assessment,
    news, and benchmark comparison.
    """

    def __init__(self, parent, main_window: "MainWindow"):
        """
        Initialize analysis tab.

        Args:
            parent: Parent notebook widget
            main_window: Reference to main window
        """
        super().__init__(parent, padding=10)

        self.main_window = main_window

        self._create_widgets()

    def _create_widgets(self):
        """Create tab widgets."""
        # Create a notebook for sub-tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Overview sub-tab
        self.overview_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.overview_frame, text="  Overview  ")
        self._create_overview_tab()

        # Charts sub-tab
        self.charts_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.charts_frame, text="  Charts  ")
        self._create_charts_tab()

        # News sub-tab
        self.news_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.news_frame, text="  News  ")
        self._create_news_tab()

        # Dividends sub-tab
        self.dividends_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.dividends_frame, text="  Dividends  ")
        self._create_dividends_tab()

    def _create_overview_tab(self):
        """Create the overview sub-tab with allocation and risk."""
        # Create two columns
        left_col = ttk.Frame(self.overview_frame)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_col = ttk.Frame(self.overview_frame)
        right_col.pack(side="left", fill="both", expand=True)

        # LEFT COLUMN
        # Sector Allocation
        sector_frame = ttk.LabelFrame(left_col, text="Sector Allocation", padding=10)
        sector_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.sector_canvas_frame = ttk.Frame(sector_frame)
        self.sector_canvas_frame.pack(fill="both", expand=True)

        # Asset Type Allocation
        type_frame = ttk.LabelFrame(left_col, text="Asset Type Allocation", padding=10)
        type_frame.pack(fill="both", expand=True)

        self.type_canvas_frame = ttk.Frame(type_frame)
        self.type_canvas_frame.pack(fill="both", expand=True)

        # RIGHT COLUMN
        # Risk Assessment
        risk_frame = ttk.LabelFrame(right_col, text="Risk Assessment", padding=10)
        risk_frame.pack(fill="x", pady=(0, 10))

        self.risk_container = ttk.Frame(risk_frame)
        self.risk_container.pack(fill="x")

        # Top Holdings
        top_frame = ttk.LabelFrame(right_col, text="Top Holdings", padding=10)
        top_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.top_holdings_container = ttk.Frame(top_frame)
        self.top_holdings_container.pack(fill="both", expand=True)

        # Benchmark Comparison
        bench_frame = ttk.LabelFrame(right_col, text="Performance vs Benchmark", padding=10)
        bench_frame.pack(fill="both", expand=True)

        self.benchmark_container = ttk.Frame(bench_frame)
        self.benchmark_container.pack(fill="both", expand=True)

    def _create_charts_tab(self):
        """Create the charts sub-tab."""
        # Controls
        controls = ttk.Frame(self.charts_frame)
        controls.pack(fill="x", pady=(0, 10))

        ttk.Label(controls, text="Time Period:").pack(side="left")

        self.period_var = tk.StringVar(value="1M")
        period_combo = ttk.Combobox(
            controls,
            textvariable=self.period_var,
            values=["1W", "1M", "3M", "6M", "1Y"],
            state="readonly",
            width=8,
        )
        period_combo.pack(side="left", padx=5)
        period_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_charts())

        ttk.Button(
            controls,
            text="Refresh Chart",
            command=self._refresh_charts,
        ).pack(side="left", padx=10)

        # Chart area
        self.chart_frame = ttk.Frame(self.charts_frame)
        self.chart_frame.pack(fill="both", expand=True)

        # Placeholder if matplotlib not available
        if not MATPLOTLIB_AVAILABLE:
            ttk.Label(
                self.chart_frame,
                text="Charts require matplotlib. Install with: pip install matplotlib",
                foreground="#dc2626",
            ).pack(pady=50)

    def _create_news_tab(self):
        """Create the news sub-tab."""
        # Controls
        controls = ttk.Frame(self.news_frame)
        controls.pack(fill="x", pady=(0, 10))

        ttk.Button(
            controls,
            text="Refresh News",
            command=self._refresh_news,
        ).pack(side="left")

        self.news_status_var = tk.StringVar(value="Click 'Refresh News' to load headlines")
        ttk.Label(
            controls,
            textvariable=self.news_status_var,
            foreground="#64748b",
        ).pack(side="left", padx=20)

        # News list (scrollable)
        self.news_scroll = ScrollableFrame(self.news_frame)
        self.news_scroll.pack(fill="both", expand=True)

        self.news_container = self.news_scroll.inner_frame

        # Initial message
        ttk.Label(
            self.news_container,
            text="Click 'Refresh News' to load financial headlines for your holdings",
            foreground="#64748b",
        ).pack(pady=30)

    def _create_dividends_tab(self):
        """Create the dividends sub-tab."""
        # Summary section
        summary_frame = ttk.LabelFrame(self.dividends_frame, text="Dividend Summary", padding=10)
        summary_frame.pack(fill="x", pady=(0, 10))

        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill="x")

        # Metrics
        self.div_total = ValueDisplay(summary_grid, "Total Dividends Received", tooltip_key="dividend")
        self.div_total.pack(side="left", padx=20)

        self.div_annual = ValueDisplay(summary_grid, "Annual Income (Last 12 Mo)")
        self.div_annual.pack(side="left", padx=20)

        self.div_yield = ValueDisplay(summary_grid, "Portfolio Yield", tooltip_key="dividend_yield")
        self.div_yield.pack(side="left", padx=20)

        self.div_monthly = ValueDisplay(summary_grid, "Monthly Average")
        self.div_monthly.pack(side="left", padx=20)

        # Dividend history
        history_frame = ttk.LabelFrame(self.dividends_frame, text="Dividend History", padding=10)
        history_frame.pack(fill="both", expand=True)

        self.div_scroll = ScrollableFrame(history_frame)
        self.div_scroll.pack(fill="both", expand=True)

        self.div_container = self.div_scroll.inner_frame

    def refresh(self):
        """Refresh all analysis data."""
        self._refresh_allocation()
        self._refresh_risk()
        self._refresh_top_holdings()
        self._refresh_benchmark()
        self._refresh_dividends()

    def _refresh_allocation(self):
        """Refresh allocation pie charts."""
        # Clear existing
        for widget in self.sector_canvas_frame.winfo_children():
            widget.destroy()
        for widget in self.type_canvas_frame.winfo_children():
            widget.destroy()

        portfolio = self.main_window.portfolio

        if not portfolio.holdings:
            ttk.Label(
                self.sector_canvas_frame,
                text="No holdings to analyze",
                foreground="#64748b",
            ).pack(pady=20)
            return

        # Get allocation data
        sector_alloc = portfolio.get_sector_allocation()
        type_alloc = portfolio.get_asset_type_allocation()

        if MATPLOTLIB_AVAILABLE:
            # Create sector pie chart
            self._create_pie_chart(self.sector_canvas_frame, sector_alloc, "Sector")

            # Create type pie chart
            self._create_pie_chart(self.type_canvas_frame, type_alloc, "Asset Type")
        else:
            # Text-based allocation display
            self._create_text_allocation(self.sector_canvas_frame, sector_alloc, "Sector")
            self._create_text_allocation(self.type_canvas_frame, type_alloc, "Type")

    def _create_pie_chart(self, parent, data: Dict[str, float], title: str):
        """Create a pie chart."""
        if not data:
            return

        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        labels = list(data.keys())
        sizes = list(data.values())

        # Colors
        colors = [
            "#2563eb",
            "#16a34a",
            "#d97706",
            "#dc2626",
            "#8b5cf6",
            "#06b6d4",
            "#ec4899",
            "#84cc16",
            "#f59e0b",
            "#6366f1",
        ]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors[: len(labels)],
            startangle=90,
        )

        ax.axis("equal")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _create_text_allocation(self, parent, data: Dict[str, float], title: str):
        """Create text-based allocation display (fallback)."""
        for name, pct in sorted(data.items(), key=lambda x: -x[1]):
            row = ttk.Frame(parent)
            row.pack(fill="x", pady=2)

            ttk.Label(row, text=name, width=20).pack(side="left")

            # Progress bar
            progress = ttk.Progressbar(row, length=100, mode="determinate")
            progress["value"] = min(pct, 100)
            progress.pack(side="left", padx=5)

            ttk.Label(row, text=f"{pct:.1f}%").pack(side="left")

    def _refresh_risk(self):
        """Refresh risk assessment."""
        # Clear existing
        for widget in self.risk_container.winfo_children():
            widget.destroy()

        portfolio = self.main_window.portfolio

        if not portfolio.holdings:
            ttk.Label(
                self.risk_container,
                text="Add holdings to see risk assessment",
                foreground="#64748b",
            ).pack(pady=10)
            return

        # Calculate risk
        holdings_data = [h.to_dict() for h in portfolio.get_all_holdings()]
        sector_alloc = portfolio.get_sector_allocation()

        assessment = assess_portfolio_risk(holdings_data, sector_alloc)

        # Risk level display
        level_frame = ttk.Frame(self.risk_container)
        level_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(level_frame, text="Risk Level:", font=("Segoe UI", 10, "bold")).pack(side="left")

        level_colors = {
            "low": "#16a34a",
            "moderate": "#d97706",
            "high": "#dc2626",
            "very_high": "#991b1b",
        }
        level_color = level_colors.get(assessment.risk_level, "#64748b")

        ttk.Label(
            level_frame,
            text=f"  {assessment.risk_level.upper()}",
            foreground=level_color,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        ttk.Label(
            level_frame,
            text=f"  (Score: {assessment.score:.0f}/100)",
            foreground="#64748b",
        ).pack(side="left")

        # Warnings
        if assessment.warnings:
            ttk.Label(
                self.risk_container,
                text="Warnings:",
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", pady=(5, 0))

            for warning in assessment.warnings[:3]:  # Show top 3
                warning_frame = ttk.Frame(self.risk_container)
                warning_frame.pack(fill="x", pady=2)

                ttk.Label(
                    warning_frame,
                    text="!",
                    foreground="#d97706",
                    font=("Segoe UI", 9, "bold"),
                ).pack(side="left")

                ttk.Label(
                    warning_frame,
                    text=f"  {warning}",
                    foreground="#64748b",
                    wraplength=300,
                ).pack(side="left")

        # Recommendations
        if assessment.recommendations:
            ttk.Label(
                self.risk_container,
                text="Insights:",
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", pady=(10, 0))

            for rec in assessment.recommendations[:2]:  # Show top 2
                ttk.Label(
                    self.risk_container,
                    text=f"• {rec}",
                    foreground="#64748b",
                    wraplength=300,
                ).pack(anchor="w", pady=2)

    def _refresh_top_holdings(self):
        """Refresh top holdings display."""
        # Clear existing
        for widget in self.top_holdings_container.winfo_children():
            widget.destroy()

        holdings = self.main_window.portfolio.get_all_holdings()[:5]  # Top 5

        if not holdings:
            ttk.Label(
                self.top_holdings_container,
                text="No holdings yet",
                foreground="#64748b",
            ).pack(pady=10)
            return

        total_value = self.main_window.portfolio.total_market_value or self.main_window.portfolio.total_cost_basis

        for holding in holdings:
            value = holding.market_value or holding.cost_basis
            pct = (value / total_value * 100) if total_value else 0

            row = ttk.Frame(self.top_holdings_container)
            row.pack(fill="x", pady=3)

            ttk.Label(row, text=holding.symbol, font=("Segoe UI", 9, "bold"), width=8).pack(side="left")

            # Progress bar for allocation
            progress = ttk.Progressbar(row, length=80, mode="determinate")
            progress["value"] = min(pct, 100)
            progress.pack(side="left", padx=5)

            ttk.Label(row, text=f"{pct:.1f}%", width=8).pack(side="left")
            ttk.Label(row, text=f"${value:,.0f}", foreground="#64748b").pack(side="left")

    def _refresh_benchmark(self):
        """Refresh benchmark comparison."""
        # Clear existing
        for widget in self.benchmark_container.winfo_children():
            widget.destroy()

        portfolio = self.main_window.portfolio

        if not portfolio.holdings:
            ttk.Label(
                self.benchmark_container,
                text="Add holdings to compare with benchmarks",
                foreground="#64748b",
            ).pack(pady=10)
            return

        # Calculate portfolio return if we have snapshots
        if len(portfolio.snapshots) >= 2:
            first = portfolio.snapshots[0]
            last = portfolio.snapshots[-1]

            if first.total_value > 0:
                port_return = ((last.total_value - first.total_value) / first.total_value) * 100

                ttk.Label(
                    self.benchmark_container,
                    text=f"Portfolio Return: {port_return:+.2f}%",
                    font=("Segoe UI", 10, "bold"),
                    foreground="#16a34a" if port_return >= 0 else "#dc2626",
                ).pack(anchor="w", pady=5)

                # Note about benchmark
                ttk.Label(
                    self.benchmark_container,
                    text="(Based on portfolio snapshots since tracking began)",
                    foreground="#64748b",
                    font=("Segoe UI", 8),
                ).pack(anchor="w")
        else:
            ttk.Label(
                self.benchmark_container,
                text="Performance tracking will begin after prices are refreshed.",
                foreground="#64748b",
            ).pack(pady=5)

        # Benchmark reference info
        ttk.Separator(self.benchmark_container).pack(fill="x", pady=10)

        ttk.Label(
            self.benchmark_container,
            text="Common Benchmarks:",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        for name, symbol in list(BENCHMARK_INDEXES.items())[:3]:
            ttk.Label(
                self.benchmark_container,
                text=f"• {name} ({symbol})",
                foreground="#64748b",
            ).pack(anchor="w", pady=1)

    def _refresh_charts(self):
        """Refresh historical charts."""
        if not MATPLOTLIB_AVAILABLE:
            return

        # Clear existing
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        portfolio = self.main_window.portfolio

        if not portfolio.snapshots:
            ttk.Label(
                self.chart_frame,
                text="No historical data yet. Portfolio value is tracked each time prices are refreshed.",
                foreground="#64748b",
            ).pack(pady=50)
            return

        # Create figure
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Extract data
        dates = [datetime.fromisoformat(s.timestamp) for s in portfolio.snapshots]
        values = [s.total_value for s in portfolio.snapshots]

        # Plot
        ax.plot(dates, values, "b-", linewidth=2)
        ax.fill_between(dates, values, alpha=0.3)

        ax.set_xlabel("Date")
        ax.set_ylabel("Portfolio Value ($)")
        ax.set_title("Portfolio Value Over Time")

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        fig.autofmt_xdate()

        # Add grid
        ax.grid(True, alpha=0.3)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _refresh_news(self):
        """Refresh news for holdings."""
        # Clear existing
        for widget in self.news_container.winfo_children():
            widget.destroy()

        self.news_status_var.set("Loading news...")

        # Show loading indicator
        loading = ttk.Label(
            self.news_container,
            text="Fetching news headlines...",
            foreground="#64748b",
        )
        loading.pack(pady=30)

        def fetch_news():
            try:
                news_service = self.main_window.news_service
                portfolio = self.main_window.portfolio

                # Get market news
                market_news = news_service.get_market_news(max_articles=5)

                # Get news for each holding
                holdings = [
                    {"symbol": h.symbol, "name": h.name}
                    for h in portfolio.get_all_holdings()[:5]  # Top 5 holdings
                ]
                holding_news = news_service.get_portfolio_news(holdings, max_articles_per_holding=2)

                # Update UI on main thread
                self.after(0, lambda: self._display_news(market_news, holding_news))

            except Exception as e:
                logger.error(f"Failed to fetch news: {e}")
                self.after(0, lambda: self._show_news_error(str(e)))

        thread = threading.Thread(target=fetch_news, daemon=True)
        thread.start()

    def _display_news(self, market_news: List, holding_news: Dict):
        """Display fetched news."""
        # Clear loading
        for widget in self.news_container.winfo_children():
            widget.destroy()

        self.news_status_var.set(f"Last updated: {datetime.now().strftime('%H:%M')}")

        # Market news section
        if market_news:
            ttk.Label(
                self.news_container,
                text="Market News",
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=(0, 5))

            for article in market_news:
                self._create_news_card(article)

            ttk.Separator(self.news_container).pack(fill="x", pady=15)

        # Holdings news
        if holding_news:
            ttk.Label(
                self.news_container,
                text="News for Your Holdings",
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=(0, 5))

            for symbol, articles in holding_news.items():
                ttk.Label(
                    self.news_container,
                    text=symbol,
                    font=("Segoe UI", 10, "bold"),
                    foreground="#2563eb",
                ).pack(anchor="w", pady=(10, 5))

                for article in articles:
                    self._create_news_card(article)

        if not market_news and not holding_news:
            ttk.Label(
                self.news_container,
                text="No news available. Try again later.",
                foreground="#64748b",
            ).pack(pady=30)

    def _create_news_card(self, article):
        """Create a news article card."""
        card = ttk.Frame(self.news_container, relief="solid", borderwidth=1)
        card.pack(fill="x", pady=3)

        inner = ttk.Frame(card, padding=8)
        inner.pack(fill="x")

        # Title
        title_label = ttk.Label(
            inner,
            text=article.title,
            font=("Segoe UI", 9, "bold"),
            wraplength=600,
            cursor="hand2",
        )
        title_label.pack(anchor="w")

        # Description
        if article.description:
            desc_text = article.description[:150] + "..." if len(article.description) > 150 else article.description
            ttk.Label(
                inner,
                text=desc_text,
                foreground="#64748b",
                wraplength=600,
            ).pack(anchor="w", pady=(2, 0))

        # Source and date
        meta_frame = ttk.Frame(inner)
        meta_frame.pack(fill="x", pady=(5, 0))

        ttk.Label(
            meta_frame,
            text=f"{article.source} • {article.published_date}",
            foreground="#94a3b8",
            font=("Segoe UI", 8),
        ).pack(side="left")

    def _show_news_error(self, error: str):
        """Show news loading error."""
        for widget in self.news_container.winfo_children():
            widget.destroy()

        self.news_status_var.set("Failed to load news")

        ttk.Label(
            self.news_container,
            text=f"Failed to load news: {error}",
            foreground="#dc2626",
        ).pack(pady=30)

    def _refresh_dividends(self):
        """Refresh dividends display."""
        # Clear existing
        for widget in self.div_container.winfo_children():
            widget.destroy()

        portfolio = self.main_window.portfolio
        dividends = portfolio.dividends

        # Calculate metrics
        total_value = portfolio.total_market_value or portfolio.total_cost_basis or 1

        metrics = calculate_dividend_metrics(
            [d.to_dict() for d in dividends],
            total_value,
        )

        # Update summary
        self.div_total.set_value(metrics["total_received"])
        self.div_annual.set_value(metrics["annual_income"])
        self.div_yield.set_value(metrics["portfolio_yield"], "{:.2f}%")
        self.div_monthly.set_value(metrics["monthly_average"])

        # Show dividend history
        if not dividends:
            ttk.Label(
                self.div_container,
                text="No dividends recorded yet.\n\nUse 'Record Dividend' in the Portfolio tab to track dividend payments.",
                foreground="#64748b",
            ).pack(pady=30)
            return

        # Header
        header = ttk.Frame(self.div_container)
        header.pack(fill="x", pady=(0, 5))

        ttk.Label(header, text="Date", width=12, font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(header, text="Symbol", width=10, font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(header, text="Amount", width=12, font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(header, text="Notes", font=("Segoe UI", 9, "bold")).pack(side="left")

        ttk.Separator(self.div_container).pack(fill="x", pady=5)

        # Dividend rows (newest first)
        for div in sorted(dividends, key=lambda d: d.date, reverse=True):
            row = ttk.Frame(self.div_container)
            row.pack(fill="x", pady=2)

            ttk.Label(row, text=div.date[:10], width=12).pack(side="left")
            ttk.Label(row, text=div.symbol, width=10).pack(side="left")
            ttk.Label(row, text=f"${div.amount:.2f}", width=12, foreground="#16a34a").pack(side="left")
            ttk.Label(row, text=div.notes or "-", foreground="#64748b").pack(side="left")
