"""
Custom widgets for Invest AI Assistant.

Includes tooltips, styled buttons, and other reusable UI components.
These widgets help create a beginner-friendly interface with helpful hints.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any

# Import tooltip definitions
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.constants import INVESTING_TERMS


class ToolTip:
    """
    Create a tooltip for a given widget.

    Tooltips appear when the user hovers over a widget,
    providing helpful explanations of investing terms.
    """

    def __init__(
        self,
        widget: tk.Widget,
        text: str,
        delay: int = 500,
        wrap_length: int = 300,
    ):
        """
        Initialize tooltip.

        Args:
            widget: The widget to attach the tooltip to
            text: The tooltip text to display
            delay: Delay in milliseconds before showing tooltip
            wrap_length: Maximum line width for wrapping
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wrap_length = wrap_length
        self.tooltip_window = None
        self.schedule_id = None

        # Bind events
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Button>", self._on_leave)

    def _on_enter(self, event=None):
        """Schedule tooltip to appear."""
        self._cancel_schedule()
        self.schedule_id = self.widget.after(self.delay, self._show_tooltip)

    def _on_leave(self, event=None):
        """Cancel scheduled tooltip and hide if visible."""
        self._cancel_schedule()
        self._hide_tooltip()

    def _cancel_schedule(self):
        """Cancel any scheduled tooltip."""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None

    def _show_tooltip(self):
        """Display the tooltip."""
        if self.tooltip_window:
            return

        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Create tooltip content
        frame = ttk.Frame(tw, relief="solid", borderwidth=1)
        frame.pack(fill="both", expand=True)

        label = ttk.Label(
            frame,
            text=self.text,
            justify="left",
            wraplength=self.wrap_length,
            padding=(8, 6),
            background="#ffffd0",
            foreground="#000000",
        )
        label.pack()

    def _hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tooltip(widget: tk.Widget, term_key: str) -> Optional[ToolTip]:
    """
    Add a tooltip to a widget using a predefined investing term.

    Args:
        widget: The widget to attach the tooltip to
        term_key: Key from INVESTING_TERMS dictionary

    Returns:
        The created ToolTip, or None if term not found
    """
    if term_key in INVESTING_TERMS:
        return ToolTip(widget, INVESTING_TERMS[term_key])
    return None


def create_tooltip(widget: tk.Widget, text: str) -> ToolTip:
    """
    Create a tooltip with custom text.

    Args:
        widget: The widget to attach the tooltip to
        text: Custom tooltip text

    Returns:
        The created ToolTip
    """
    return ToolTip(widget, text)


class InfoLabel(ttk.Frame):
    """
    A label with an info icon that shows a tooltip.

    Useful for displaying investing terms with explanations.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        tooltip_key: Optional[str] = None,
        tooltip_text: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize info label.

        Args:
            parent: Parent widget
            text: Label text
            tooltip_key: Key from INVESTING_TERMS for tooltip
            tooltip_text: Custom tooltip text (overrides tooltip_key)
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        # Main label
        self.label = ttk.Label(self, text=text)
        self.label.pack(side="left")

        # Info icon (if tooltip provided)
        tooltip = tooltip_text or INVESTING_TERMS.get(tooltip_key, "")
        if tooltip:
            self.info_label = ttk.Label(
                self,
                text=" (?)",
                foreground="#2563eb",
                cursor="question_arrow",
            )
            self.info_label.pack(side="left")
            ToolTip(self.info_label, tooltip)


class ValueDisplay(ttk.Frame):
    """
    Display a value with optional color coding for gains/losses.
    """

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        value: str = "",
        tooltip_key: Optional[str] = None,
        is_currency: bool = True,
        show_change: bool = False,
        **kwargs,
    ):
        """
        Initialize value display.

        Args:
            parent: Parent widget
            label: Label text
            value: Initial value to display
            tooltip_key: Key from INVESTING_TERMS for tooltip
            is_currency: Whether to format as currency
            show_change: Whether to color code based on +/-
        """
        super().__init__(parent, **kwargs)

        self.is_currency = is_currency
        self.show_change = show_change

        # Label
        label_frame = ttk.Frame(self)
        label_frame.pack(fill="x")

        self.label_widget = ttk.Label(label_frame, text=label, font=("Segoe UI", 9))
        self.label_widget.pack(side="left")

        if tooltip_key and tooltip_key in INVESTING_TERMS:
            info = ttk.Label(
                label_frame,
                text=" (?)",
                foreground="#2563eb",
                cursor="question_arrow",
                font=("Segoe UI", 8),
            )
            info.pack(side="left")
            ToolTip(info, INVESTING_TERMS[tooltip_key])

        # Value
        self.value_var = tk.StringVar(value=value)
        self.value_label = ttk.Label(
            self,
            textvariable=self.value_var,
            font=("Segoe UI", 12, "bold"),
        )
        self.value_label.pack(anchor="w")

    def set_value(self, value: float, format_str: str = "${:,.2f}"):
        """
        Set the displayed value.

        Args:
            value: Numeric value to display
            format_str: Format string for the value
        """
        formatted = format_str.format(value) if value is not None else "N/A"

        # Add + sign for positive changes
        if self.show_change and value is not None and value > 0:
            if "%" in format_str:
                formatted = f"+{formatted}"
            else:
                formatted = formatted.replace("$", "+$")

        self.value_var.set(formatted)

        # Color coding for gains/losses
        if self.show_change and value is not None:
            if value > 0:
                self.value_label.configure(foreground="#16a34a")  # Green
            elif value < 0:
                self.value_label.configure(foreground="#dc2626")  # Red
            else:
                self.value_label.configure(foreground="#64748b")  # Gray

    def set_text(self, text: str):
        """Set raw text value."""
        self.value_var.set(text)
        self.value_label.configure(foreground="#1e293b")  # Default color


class StyledButton(ttk.Button):
    """
    A styled button with optional tooltip.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[Callable] = None,
        tooltip: Optional[str] = None,
        style: str = "TButton",
        **kwargs,
    ):
        """
        Initialize styled button.

        Args:
            parent: Parent widget
            text: Button text
            command: Click handler
            tooltip: Tooltip text
            style: ttk style name
        """
        super().__init__(parent, text=text, command=command, style=style, **kwargs)

        if tooltip:
            ToolTip(self, tooltip)


class HoldingCard(ttk.Frame):
    """
    A card-style display for a single portfolio holding.
    """

    def __init__(
        self,
        parent: tk.Widget,
        symbol: str,
        name: str,
        quantity: float,
        avg_cost: float,
        current_price: Optional[float],
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        **kwargs,
    ):
        """
        Initialize holding card.

        Args:
            parent: Parent widget
            symbol: Ticker symbol
            name: Company name
            quantity: Number of shares
            avg_cost: Average cost per share
            current_price: Current market price
            on_edit: Edit button callback
            on_delete: Delete button callback
        """
        super().__init__(parent, relief="solid", borderwidth=1, **kwargs)

        self.symbol = symbol
        self.configure(padding=10)

        # Header row with symbol and name
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 5))

        ttk.Label(
            header,
            text=symbol,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        ttk.Label(
            header,
            text=f"  {name}",
            font=("Segoe UI", 10),
            foreground="#64748b",
        ).pack(side="left")

        # Action buttons
        if on_delete:
            del_btn = ttk.Button(
                header,
                text="X",
                width=3,
                command=lambda: on_delete(symbol),
            )
            del_btn.pack(side="right")
            ToolTip(del_btn, "Remove this holding")

        if on_edit:
            edit_btn = ttk.Button(
                header,
                text="Edit",
                width=5,
                command=lambda: on_edit(symbol),
            )
            edit_btn.pack(side="right", padx=5)
            ToolTip(edit_btn, "Edit holding details")

        # Details grid
        details = ttk.Frame(self)
        details.pack(fill="x")

        # Quantity and cost
        col1 = ttk.Frame(details)
        col1.pack(side="left", fill="both", expand=True)

        ttk.Label(col1, text="Shares:", font=("Segoe UI", 9)).pack(anchor="w")
        ttk.Label(col1, text=f"{quantity:,.4f}", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )

        ttk.Label(col1, text="Avg Cost:", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))
        ttk.Label(col1, text=f"${avg_cost:,.2f}", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )

        # Current price and value
        col2 = ttk.Frame(details)
        col2.pack(side="left", fill="both", expand=True)

        ttk.Label(col2, text="Price:", font=("Segoe UI", 9)).pack(anchor="w")
        price_text = f"${current_price:,.2f}" if current_price else "Loading..."
        ttk.Label(col2, text=price_text, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        # Market value and gain/loss
        cost_basis = quantity * avg_cost
        if current_price:
            market_value = quantity * current_price
            gain = market_value - cost_basis
            gain_pct = (gain / cost_basis * 100) if cost_basis else 0

            ttk.Label(col2, text="Value:", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))
            value_label = ttk.Label(
                col2,
                text=f"${market_value:,.2f}",
                font=("Segoe UI", 10, "bold"),
            )
            value_label.pack(anchor="w")

            # Gain/loss with color
            col3 = ttk.Frame(details)
            col3.pack(side="left", fill="both", expand=True)

            ttk.Label(col3, text="Gain/Loss:", font=("Segoe UI", 9)).pack(anchor="w")
            gain_color = "#16a34a" if gain >= 0 else "#dc2626"
            gain_sign = "+" if gain >= 0 else ""
            gain_label = ttk.Label(
                col3,
                text=f"{gain_sign}${gain:,.2f}",
                font=("Segoe UI", 10, "bold"),
                foreground=gain_color,
            )
            gain_label.pack(anchor="w")

            ttk.Label(
                col3,
                text=f"({gain_sign}{gain_pct:.2f}%)",
                font=("Segoe UI", 9),
                foreground=gain_color,
            ).pack(anchor="w")


class ScrollableFrame(ttk.Frame):
    """
    A frame that can be scrolled vertically.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize scrollable frame."""
        super().__init__(parent, **kwargs)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )

        # Create inner frame for content
        self.inner_frame = ttk.Frame(self.canvas)

        # Configure canvas scrolling
        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw",
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # Make inner frame resize with canvas
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        """Resize inner frame to match canvas width."""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _bind_mousewheel(self, event):
        """Bind mouse wheel when mouse enters."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Unbind mouse wheel when mouse leaves."""
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class LoadingSpinner(ttk.Frame):
    """
    A simple loading indicator.
    """

    def __init__(self, parent: tk.Widget, text: str = "Loading...", **kwargs):
        """Initialize loading spinner."""
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=text, font=("Segoe UI", 10))
        self.label.pack(pady=20)

        self.dots = 0
        self.base_text = text.rstrip(".")
        self._animate()

    def _animate(self):
        """Animate the loading dots."""
        self.dots = (self.dots + 1) % 4
        self.label.configure(text=self.base_text + "." * self.dots)
        self.after_id = self.after(300, self._animate)

    def stop(self):
        """Stop the animation."""
        if hasattr(self, "after_id"):
            self.after_cancel(self.after_id)

    def destroy(self):
        """Clean up when destroyed."""
        self.stop()
        super().destroy()
