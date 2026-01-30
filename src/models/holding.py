"""
Holding model for Invest AI Assistant.

A Holding represents an individual investment position in the portfolio,
such as shares of a stock or units of cryptocurrency.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..utils.constants import AssetType


@dataclass
class Holding:
    """
    Represents a single investment holding in the portfolio.

    Attributes:
        symbol: The ticker symbol (e.g., 'AAPL', 'BTC-USD')
        name: The full name of the asset (e.g., 'Apple Inc.')
        asset_type: The type of asset (stock, etf, crypto, etc.)
        quantity: Number of shares/units owned
        average_cost: Average purchase price per share/unit
        sector: The market sector (e.g., 'Technology')
        current_price: Most recent market price (updated by price service)
        last_updated: When the price was last updated
        notes: Optional user notes about this holding
    """

    # Required fields
    symbol: str
    name: str
    asset_type: str  # Using string instead of enum for JSON serialization
    quantity: float
    average_cost: float

    # Optional fields with defaults
    sector: str = "Other"
    current_price: Optional[float] = None
    last_updated: Optional[str] = None
    notes: str = ""

    # Calculated fields (not stored, computed on access)
    # These are computed properties, not stored in JSON

    def __post_init__(self):
        """
        Validate and normalize data after initialization.
        """
        # Ensure symbol is uppercase
        self.symbol = self.symbol.upper()

        # Ensure quantity and cost are positive
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if self.average_cost < 0:
            raise ValueError("Average cost cannot be negative")

    @property
    def cost_basis(self) -> float:
        """
        Calculate the total cost basis (amount invested).

        Returns:
            Total amount paid for this holding (quantity × average cost)
        """
        return self.quantity * self.average_cost

    @property
    def market_value(self) -> Optional[float]:
        """
        Calculate current market value of the holding.

        Returns:
            Current value if price is available, None otherwise
        """
        if self.current_price is None:
            return None
        return self.quantity * self.current_price

    @property
    def unrealized_gain(self) -> Optional[float]:
        """
        Calculate unrealized gain/loss (paper profit/loss).

        Returns:
            Gain/loss amount if price is available, None otherwise
        """
        market_value = self.market_value
        if market_value is None:
            return None
        return market_value - self.cost_basis

    @property
    def unrealized_gain_percent(self) -> Optional[float]:
        """
        Calculate unrealized gain/loss as a percentage.

        Returns:
            Percentage gain/loss if price is available, None otherwise
        """
        if self.cost_basis == 0:
            return None
        gain = self.unrealized_gain
        if gain is None:
            return None
        return (gain / self.cost_basis) * 100

    @property
    def is_profitable(self) -> Optional[bool]:
        """
        Check if this holding is currently profitable.

        Returns:
            True if profitable, False if not, None if price unavailable
        """
        gain = self.unrealized_gain
        if gain is None:
            return None
        return gain > 0

    def update_price(self, price: float) -> None:
        """
        Update the current price and timestamp.

        Args:
            price: The new current price
        """
        self.current_price = price
        self.last_updated = datetime.now().isoformat()

    def add_shares(self, quantity: float, price_per_share: float) -> None:
        """
        Add more shares to this holding (buying more).
        Recalculates the average cost.

        Args:
            quantity: Number of shares to add
            price_per_share: Price paid per share
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price_per_share < 0:
            raise ValueError("Price cannot be negative")

        # Calculate new average cost
        total_old_cost = self.quantity * self.average_cost
        total_new_cost = quantity * price_per_share
        total_quantity = self.quantity + quantity

        self.average_cost = (total_old_cost + total_new_cost) / total_quantity
        self.quantity = total_quantity

    def remove_shares(self, quantity: float) -> float:
        """
        Remove shares from this holding (selling).
        Returns the cost basis of the sold shares.

        Args:
            quantity: Number of shares to remove

        Returns:
            The cost basis of the removed shares

        Raises:
            ValueError: If trying to remove more shares than owned
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.quantity:
            raise ValueError(f"Cannot sell {quantity} shares, only own {self.quantity}")

        cost_of_sold = quantity * self.average_cost
        self.quantity -= quantity
        return cost_of_sold

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert holding to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the holding
        """
        return {
            "symbol": self.symbol,
            "name": self.name,
            "asset_type": self.asset_type,
            "quantity": self.quantity,
            "average_cost": self.average_cost,
            "sector": self.sector,
            "current_price": self.current_price,
            "last_updated": self.last_updated,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Holding":
        """
        Create a Holding instance from a dictionary.

        Args:
            data: Dictionary containing holding data

        Returns:
            A new Holding instance
        """
        return cls(
            symbol=data["symbol"],
            name=data["name"],
            asset_type=data["asset_type"],
            quantity=data["quantity"],
            average_cost=data["average_cost"],
            sector=data.get("sector", "Other"),
            current_price=data.get("current_price"),
            last_updated=data.get("last_updated"),
            notes=data.get("notes", ""),
        )

    def __str__(self) -> str:
        """String representation of the holding."""
        value_str = f"${self.market_value:,.2f}" if self.market_value else "N/A"
        return f"{self.symbol}: {self.quantity} shares @ ${self.average_cost:.2f} = {value_str}"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"Holding(symbol='{self.symbol}', name='{self.name}', "
            f"quantity={self.quantity}, avg_cost={self.average_cost}, "
            f"current_price={self.current_price})"
        )
