"""
Portfolio tab for Invest AI Assistant.

Displays portfolio holdings and allows users to add, edit, and remove
investments. Shows real-time values and gains/losses.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, TYPE_CHECKING
import logging

from .widgets import (
    ToolTip,
    ValueDisplay,
    ScrollableFrame,
    create_tooltip,
)
from ..utils.constants import INVESTING_TERMS, SECTORS

if TYPE_CHECKING:
    from .main_window import MainWindow

logger = logging.getLogger(__name__)


class AddHoldingDialog(tk.Toplevel):
    """Dialog for adding a new holding to the portfolio."""

    def __init__(self, parent, main_window: "MainWindow", edit_symbol: Optional[str] = None):
        """
        Initialize add/edit holding dialog.

        Args:
            parent: Parent window
            main_window: Reference to main window
            edit_symbol: If provided, edit this existing holding
        """
        super().__init__(parent)

        self.main_window = main_window
        self.edit_symbol = edit_symbol
        self.result = None

        # Configure dialog
        self.title("Edit Holding" if edit_symbol else "Add Holding")
        self.geometry("450x500")
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")

        self._create_widgets()

        # If editing, populate fields
        if edit_symbol:
            self._populate_for_edit()

    def _create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Title
        title_text = "Edit Holding" if self.edit_symbol else "Add New Holding"
        ttk.Label(frame, text=title_text, style="Heading.TLabel").pack(anchor="w", pady=(0, 20))

        # Form fields
        form = ttk.Frame(frame)
        form.pack(fill="x")

        # Symbol
        row = ttk.Frame(form)
        row.pack(fill="x", pady=5)
        label = ttk.Label(row, text="Symbol:", width=15)
        label.pack(side="left")
        create_tooltip(label, INVESTING_TERMS["ticker_symbol"])

        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(row, textvariable=self.symbol_var, width=15)
        self.symbol_entry.pack(side="left")
        if self.edit_symbol:
            self.symbol_entry.configure(state="disabled")

        ttk.Label(row, text="  (e.g., AAPL, MSFT, BTC-USD)", foreground="#64748b").pack(side="left")

        # Name
        row = ttk.Frame(form)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Name:", width=15).pack(side="left")
        self.name_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.name_var, width=30).pack(side="left")

        # Asset Type
        row = ttk.Frame(form)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Asset Type:", width=15).pack(side="left")
        self.type_var = tk.StringVar(value="stock")
        type_combo = ttk.Combobox(
            row,
            textvariable=self.type_var,
            values=["stock", "etf", "crypto", "mutual_fund", "bond"],
            state="readonly",
            width=15,
        )
        type_combo.pack(side="left")

        # Sector
        row = ttk.Frame(form)
        row.pack(fill="x", pady=5)
        label = ttk.Label(row, text="Sector:", width=15)
        label.pack(side="left")
        create_tooltip(label, INVESTING_TERMS["sector"])

        self.sector_var = tk.StringVar(value="Other")
        sector_combo = ttk.Combobox(
            row,
            textvariable=self.sector_var,
            values=SECTORS,
            state="readonly",
            width=20,
        )
        sector_combo.pack(side="left")

        # Separator
        ttk.Separator(form).pack(fill="x", pady=15)

        # Quantity
        row = ttk.Frame(form)
        row.pack(fill="x", pady=5)
        label = ttk.Label(row, text="Quantity:", width=15)
        label.pack(side="left")
        create_tooltip(label, "Number of shares or units you own")

        self.quantity_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.quantity_var, width=15).pack(side="left")

        # Price
        row = ttk.Frame(form)
        row.pack(fill="x", pady=5)
        label = ttk.Label(row, text="Purchase Price:", width=15)
        label.pack(side="left")
        create_tooltip(label, INVESTING_TERMS["cost_basis"])

        ttk.Label(row, text="$").pack(side="left")
        self.price_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.price_var, width=15).pack(side="left")
        ttk.Label(row, text="  per share", foreground="#64748b").pack(side="left")

        # Notes
        row = ttk.Frame(form)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Notes:", width=15).pack(side="left", anchor="n")
        self.notes_text = tk.Text(row, height=3, width=30)
        self.notes_text.pack(side="left")

        # Lookup button
        if not self.edit_symbol:
            ttk.Separator(form).pack(fill="x", pady=15)
            lookup_frame = ttk.Frame(form)
            lookup_frame.pack(fill="x")

            ttk.Label(
                lookup_frame,
                text="Enter a symbol and click Lookup to auto-fill details:",
                foreground="#64748b",
            ).pack(side="left")

            ttk.Button(
                lookup_frame,
                text="Lookup",
                command=self._lookup_symbol,
            ).pack(side="right")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
        ).pack(side="right")

        ttk.Button(
            btn_frame,
            text="Save" if self.edit_symbol else "Add",
            command=self._save,
        ).pack(side="right", padx=10)

    def _lookup_symbol(self):
        """Look up symbol information from price service."""
        symbol = self.symbol_var.get().strip().upper()
        if not symbol:
            messagebox.showwarning("Missing Symbol", "Please enter a symbol first")
            return

        self.main_window.set_status(f"Looking up {symbol}...")

        try:
            # Get stock info
            info = self.main_window.price_service.get_stock_info(symbol)
            if info:
                self.name_var.set(info.name)
                self.sector_var.set(info.sector if info.sector else "Other")

                # Set asset type based on symbol
                if "-USD" in symbol or symbol in ["BTC", "ETH", "DOGE"]:
                    self.type_var.set("crypto")
                elif info.sector:
                    self.type_var.set("stock")

                # Get current price
                price_data = self.main_window.price_service.get_price(symbol)
                if price_data:
                    self.price_var.set(f"{price_data.current_price:.2f}")

                self.main_window.set_status(f"Found: {info.name}")
            else:
                self.main_window.set_status(f"Could not find info for {symbol}")
                messagebox.showwarning(
                    "Symbol Not Found",
                    f"Could not find information for '{symbol}'.\n"
                    "You can still add it manually.",
                )

        except Exception as e:
            logger.error(f"Symbol lookup failed: {e}")
            self.main_window.set_status("Lookup failed")

    def _populate_for_edit(self):
        """Populate fields when editing an existing holding."""
        holding = self.main_window.portfolio.get_holding(self.edit_symbol)
        if holding:
            self.symbol_var.set(holding.symbol)
            self.name_var.set(holding.name)
            self.type_var.set(holding.asset_type)
            self.sector_var.set(holding.sector)
            self.quantity_var.set(str(holding.quantity))
            self.price_var.set(f"{holding.average_cost:.2f}")
            self.notes_text.insert("1.0", holding.notes)

    def _save(self):
        """Save the holding."""
        # Validate inputs
        symbol = self.symbol_var.get().strip().upper()
        name = self.name_var.get().strip()
        asset_type = self.type_var.get()
        sector = self.sector_var.get()
        notes = self.notes_text.get("1.0", "end-1c").strip()

        try:
            quantity = float(self.quantity_var.get().strip())
            price = float(self.price_var.get().strip())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid numbers for quantity and price.",
            )
            return

        if not symbol:
            messagebox.showerror("Missing Symbol", "Please enter a symbol.")
            return

        if not name:
            name = symbol  # Use symbol as name if not provided

        if quantity <= 0:
            messagebox.showerror("Invalid Quantity", "Quantity must be greater than 0.")
            return

        if price < 0:
            messagebox.showerror("Invalid Price", "Price cannot be negative.")
            return

        # Store result
        self.result = {
            "symbol": symbol,
            "name": name,
            "asset_type": asset_type,
            "sector": sector,
            "quantity": quantity,
            "price": price,
            "notes": notes,
        }

        self.destroy()


class RecordDividendDialog(tk.Toplevel):
    """Dialog for recording a dividend payment."""

    def __init__(self, parent, main_window: "MainWindow"):
        """Initialize dividend dialog."""
        super().__init__(parent)

        self.main_window = main_window
        self.result = None

        self.title("Record Dividend")
        self.geometry("350x250")
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Record Dividend Payment", style="Heading.TLabel").pack(
            anchor="w", pady=(0, 20)
        )

        # Symbol selection
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Symbol:", width=12).pack(side="left")

        symbols = list(self.main_window.portfolio.holdings.keys())
        self.symbol_var = tk.StringVar()
        symbol_combo = ttk.Combobox(
            row,
            textvariable=self.symbol_var,
            values=symbols,
            state="readonly" if symbols else "disabled",
            width=15,
        )
        symbol_combo.pack(side="left")

        # Amount
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=5)
        label = ttk.Label(row, text="Amount:", width=12)
        label.pack(side="left")
        create_tooltip(label, INVESTING_TERMS["dividend"])

        ttk.Label(row, text="$").pack(side="left")
        self.amount_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.amount_var, width=15).pack(side="left")

        # Date
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Date:", width=12).pack(side="left")
        self.date_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.date_var, width=15).pack(side="left")
        ttk.Label(row, text="  (YYYY-MM-DD)", foreground="#64748b").pack(side="left")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(20, 0))

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(btn_frame, text="Record", command=self._save).pack(side="right", padx=10)

    def _save(self):
        """Save the dividend record."""
        symbol = self.symbol_var.get()
        date = self.date_var.get().strip()

        try:
            amount = float(self.amount_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid amount.")
            return

        if not symbol:
            messagebox.showerror("Missing Symbol", "Please select a symbol.")
            return

        if amount <= 0:
            messagebox.showerror("Invalid Amount", "Amount must be greater than 0.")
            return

        self.result = {
            "symbol": symbol,
            "amount": amount,
            "date": date if date else None,
        }

        self.destroy()


class PortfolioTab(ttk.Frame):
    """
    Portfolio management tab.

    Displays all holdings and allows adding, editing, and removing investments.
    """

    def __init__(self, parent, main_window: "MainWindow"):
        """
        Initialize portfolio tab.

        Args:
            parent: Parent notebook widget
            main_window: Reference to main window
        """
        super().__init__(parent, padding=10)

        self.main_window = main_window

        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """Create tab widgets."""
        # Top section - Portfolio summary
        self._create_summary_section()

        # Middle section - Action buttons
        self._create_action_buttons()

        # Main section - Holdings list
        self._create_holdings_list()

    def _create_summary_section(self):
        """Create the portfolio summary section."""
        summary_frame = ttk.LabelFrame(self, text="Portfolio Summary", padding=10)
        summary_frame.pack(fill="x", pady=(0, 10))

        # Summary grid
        grid = ttk.Frame(summary_frame)
        grid.pack(fill="x")

        # Total Value
        col1 = ttk.Frame(grid)
        col1.pack(side="left", fill="both", expand=True)

        self.total_value = ValueDisplay(
            col1,
            label="Total Value",
            tooltip_key="market_value",
        )
        self.total_value.pack(anchor="w", pady=5)

        self.total_cost = ValueDisplay(
            col1,
            label="Total Cost",
            tooltip_key="cost_basis",
        )
        self.total_cost.pack(anchor="w", pady=5)

        # Gains
        col2 = ttk.Frame(grid)
        col2.pack(side="left", fill="both", expand=True)

        self.total_gain = ValueDisplay(
            col2,
            label="Unrealized Gain/Loss",
            tooltip_key="unrealized_gain",
            show_change=True,
        )
        self.total_gain.pack(anchor="w", pady=5)

        self.total_gain_pct = ValueDisplay(
            col2,
            label="Return %",
            tooltip_key="percent_change",
            show_change=True,
        )
        self.total_gain_pct.pack(anchor="w", pady=5)

        # Holdings count and dividends
        col3 = ttk.Frame(grid)
        col3.pack(side="left", fill="both", expand=True)

        self.holdings_count = ValueDisplay(
            col3,
            label="Holdings",
            tooltip_key="holding",
        )
        self.holdings_count.pack(anchor="w", pady=5)

        self.total_dividends = ValueDisplay(
            col3,
            label="Dividends Received",
            tooltip_key="dividend",
        )
        self.total_dividends.pack(anchor="w", pady=5)

    def _create_action_buttons(self):
        """Create action buttons."""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        # Add holding button
        add_btn = ttk.Button(
            btn_frame,
            text="+ Add Holding",
            command=self._add_holding,
        )
        add_btn.pack(side="left", padx=(0, 10))
        create_tooltip(add_btn, "Add a new stock, ETF, or crypto to your portfolio")

        # Record dividend button
        div_btn = ttk.Button(
            btn_frame,
            text="Record Dividend",
            command=self._record_dividend,
        )
        div_btn.pack(side="left", padx=(0, 10))
        create_tooltip(div_btn, INVESTING_TERMS["dividend"])

        # Separator
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)

        # Sort options
        ttk.Label(btn_frame, text="Sort by:").pack(side="left", padx=(0, 5))
        self.sort_var = tk.StringVar(value="value")
        sort_combo = ttk.Combobox(
            btn_frame,
            textvariable=self.sort_var,
            values=["value", "symbol", "gain", "gain %"],
            state="readonly",
            width=10,
        )
        sort_combo.pack(side="left")
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_holdings())

    def _create_holdings_list(self):
        """Create the holdings list section."""
        list_frame = ttk.LabelFrame(self, text="Holdings", padding=10)
        list_frame.pack(fill="both", expand=True)

        # Create scrollable frame
        self.scroll_frame = ScrollableFrame(list_frame)
        self.scroll_frame.pack(fill="both", expand=True)

        # Holdings will be added here
        self.holdings_container = self.scroll_frame.inner_frame

    def refresh(self):
        """Refresh all data in the tab."""
        self._refresh_summary()
        self._refresh_holdings()

    def _refresh_summary(self):
        """Refresh the summary section."""
        portfolio = self.main_window.portfolio

        # Update summary values
        total_value = portfolio.total_market_value
        total_cost = portfolio.total_cost_basis
        total_gain = portfolio.total_unrealized_gain
        total_gain_pct = portfolio.total_unrealized_gain_percent

        if total_value is not None:
            self.total_value.set_value(total_value)
        else:
            self.total_value.set_text("Updating...")

        self.total_cost.set_value(total_cost)

        if total_gain is not None:
            self.total_gain.set_value(total_gain)
        else:
            self.total_gain.set_text("--")

        if total_gain_pct is not None:
            self.total_gain_pct.set_value(total_gain_pct, "{:.2f}%")
        else:
            self.total_gain_pct.set_text("--")

        self.holdings_count.set_text(str(portfolio.holdings_count))

        total_divs = portfolio.get_total_dividends()
        self.total_dividends.set_value(total_divs)

    def _refresh_holdings(self):
        """Refresh the holdings list."""
        # Clear existing holdings
        for widget in self.holdings_container.winfo_children():
            widget.destroy()

        holdings = self.main_window.portfolio.get_all_holdings()

        if not holdings:
            # Show empty state
            empty_frame = ttk.Frame(self.holdings_container)
            empty_frame.pack(fill="both", expand=True, pady=50)

            ttk.Label(
                empty_frame,
                text="No holdings yet",
                font=("Segoe UI", 12),
                foreground="#64748b",
            ).pack()

            ttk.Label(
                empty_frame,
                text='Click "+ Add Holding" to add your first investment',
                foreground="#64748b",
            ).pack(pady=10)

            return

        # Sort holdings
        sort_by = self.sort_var.get()
        if sort_by == "symbol":
            holdings.sort(key=lambda h: h.symbol)
        elif sort_by == "gain":
            holdings.sort(key=lambda h: h.unrealized_gain or 0, reverse=True)
        elif sort_by == "gain %":
            holdings.sort(key=lambda h: h.unrealized_gain_percent or 0, reverse=True)
        # Default is by value (already sorted)

        # Create holding cards
        for holding in holdings:
            self._create_holding_row(holding)

    def _create_holding_row(self, holding):
        """Create a row for a single holding."""
        row = ttk.Frame(self.holdings_container, relief="solid", borderwidth=1)
        row.pack(fill="x", pady=2)

        # Inner frame with padding
        inner = ttk.Frame(row, padding=10)
        inner.pack(fill="x")

        # Left section - Symbol and name
        left = ttk.Frame(inner)
        left.pack(side="left", fill="y")

        ttk.Label(
            left,
            text=holding.symbol,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        name_text = holding.name if len(holding.name) < 25 else holding.name[:22] + "..."
        ttk.Label(
            left,
            text=name_text,
            font=("Segoe UI", 9),
            foreground="#64748b",
        ).pack(anchor="w")

        # Middle section - Quantity and cost
        mid = ttk.Frame(inner)
        mid.pack(side="left", padx=30, fill="y")

        ttk.Label(
            mid,
            text=f"{holding.quantity:,.4f} shares",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        ttk.Label(
            mid,
            text=f"Avg: ${holding.average_cost:,.2f}",
            font=("Segoe UI", 9),
            foreground="#64748b",
        ).pack(anchor="w")

        # Price section
        price_frame = ttk.Frame(inner)
        price_frame.pack(side="left", padx=30, fill="y")

        if holding.current_price:
            ttk.Label(
                price_frame,
                text=f"${holding.current_price:,.2f}",
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")
        else:
            ttk.Label(
                price_frame,
                text="Loading...",
                font=("Segoe UI", 10),
                foreground="#64748b",
            ).pack(anchor="w")

        # Value section
        value_frame = ttk.Frame(inner)
        value_frame.pack(side="left", padx=30, fill="y")

        if holding.market_value:
            ttk.Label(
                value_frame,
                text=f"${holding.market_value:,.2f}",
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")

            # Gain/loss
            gain = holding.unrealized_gain
            gain_pct = holding.unrealized_gain_percent

            if gain is not None:
                color = "#16a34a" if gain >= 0 else "#dc2626"
                sign = "+" if gain >= 0 else ""
                ttk.Label(
                    value_frame,
                    text=f"{sign}${gain:,.2f} ({sign}{gain_pct:.1f}%)",
                    font=("Segoe UI", 9),
                    foreground=color,
                ).pack(anchor="w")
        else:
            ttk.Label(
                value_frame,
                text="--",
                font=("Segoe UI", 10),
                foreground="#64748b",
            ).pack(anchor="w")

        # Action buttons (right side)
        actions = ttk.Frame(inner)
        actions.pack(side="right")

        edit_btn = ttk.Button(
            actions,
            text="Edit",
            width=5,
            command=lambda s=holding.symbol: self._edit_holding(s),
        )
        edit_btn.pack(side="left", padx=2)

        del_btn = ttk.Button(
            actions,
            text="X",
            width=3,
            command=lambda s=holding.symbol: self._delete_holding(s),
        )
        del_btn.pack(side="left", padx=2)

    def _add_holding(self):
        """Open dialog to add a new holding."""
        dialog = AddHoldingDialog(self, self.main_window)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.main_window.portfolio.add_holding(
                    symbol=dialog.result["symbol"],
                    name=dialog.result["name"],
                    asset_type=dialog.result["asset_type"],
                    quantity=dialog.result["quantity"],
                    price_per_unit=dialog.result["price"],
                    sector=dialog.result["sector"],
                    notes=dialog.result["notes"],
                )

                # Refresh price for new holding
                price_data = self.main_window.price_service.get_price(dialog.result["symbol"])
                if price_data:
                    holding = self.main_window.portfolio.get_holding(dialog.result["symbol"])
                    if holding:
                        holding.update_price(price_data.current_price)

                self.main_window.set_status(f"Added {dialog.result['symbol']}")
                self.refresh()

            except Exception as e:
                logger.error(f"Failed to add holding: {e}")
                messagebox.showerror("Error", f"Failed to add holding: {e}")

    def _edit_holding(self, symbol: str):
        """Open dialog to edit an existing holding."""
        dialog = AddHoldingDialog(self, self.main_window, edit_symbol=symbol)
        self.wait_window(dialog)

        if dialog.result:
            try:
                holding = self.main_window.portfolio.get_holding(symbol)
                if holding:
                    holding.name = dialog.result["name"]
                    holding.asset_type = dialog.result["asset_type"]
                    holding.sector = dialog.result["sector"]
                    holding.quantity = dialog.result["quantity"]
                    holding.average_cost = dialog.result["price"]
                    holding.notes = dialog.result["notes"]

                    self.main_window.set_status(f"Updated {symbol}")
                    self.refresh()

            except Exception as e:
                logger.error(f"Failed to update holding: {e}")
                messagebox.showerror("Error", f"Failed to update holding: {e}")

    def _delete_holding(self, symbol: str):
        """Delete a holding from the portfolio."""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to remove {symbol} from your portfolio?\n\n"
            "This will delete the holding but preserve transaction history.",
        )

        if result:
            self.main_window.portfolio.remove_holding(symbol)
            self.main_window.set_status(f"Removed {symbol}")
            self.refresh()

    def _record_dividend(self):
        """Open dialog to record a dividend payment."""
        if not self.main_window.portfolio.holdings:
            messagebox.showinfo(
                "No Holdings",
                "Add some holdings first before recording dividends.",
            )
            return

        dialog = RecordDividendDialog(self, self.main_window)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.main_window.portfolio.record_dividend(
                    symbol=dialog.result["symbol"],
                    amount=dialog.result["amount"],
                    date=dialog.result["date"],
                )
                self.main_window.set_status(
                    f"Recorded ${dialog.result['amount']:.2f} dividend from {dialog.result['symbol']}"
                )
                self.refresh()

            except Exception as e:
                logger.error(f"Failed to record dividend: {e}")
                messagebox.showerror("Error", f"Failed to record dividend: {e}")
