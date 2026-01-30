"""
Transaction model for Invest AI Assistant.

A Transaction represents a buy, sell, or dividend event in the portfolio.
These are stored for historical tracking and performance analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from ..utils.constants import TransactionType
import uuid


@dataclass
class Transaction:
    """
    Represents a single transaction (buy, sell, or dividend).

    Attributes:
        id: Unique identifier for the transaction
        symbol: The ticker symbol of the asset
        transaction_type: Type of transaction (buy, sell, dividend)
        quantity: Number of shares/units involved
        price_per_unit: Price per share/unit at time of transaction
        date: Date and time of the transaction
        fees: Any transaction fees or commissions paid
        notes: Optional notes about the transaction
    """

    # Required fields
    symbol: str
    transaction_type: str  # 'buy', 'sell', or 'dividend'
    quantity: float
    price_per_unit: float

    # Optional fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    fees: float = 0.0
    notes: str = ""

    def __post_init__(self):
        """
        Validate and normalize data after initialization.
        """
        # Ensure symbol is uppercase
        self.symbol = self.symbol.upper()

        # Validate transaction type
        valid_types = ["buy", "sell", "dividend"]
        if self.transaction_type.lower() not in valid_types:
            raise ValueError(f"Transaction type must be one of: {valid_types}")
        self.transaction_type = self.transaction_type.lower()

        # Ensure quantity is positive
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Price can be 0 for dividends (recorded as shares), but not negative
        if self.price_per_unit < 0:
            raise ValueError("Price cannot be negative")

        # Fees cannot be negative
        if self.fees < 0:
            raise ValueError("Fees cannot be negative")

    @property
    def total_amount(self) -> float:
        """
        Calculate the total amount of the transaction.

        Returns:
            Total value (quantity × price) plus/minus fees
        """
        base_amount = self.quantity * self.price_per_unit

        if self.transaction_type == "buy":
            # For buys, fees are added to cost
            return base_amount + self.fees
        elif self.transaction_type == "sell":
            # For sells, fees are subtracted from proceeds
            return base_amount - self.fees
        else:
            # For dividends, just return the amount
            return base_amount

    @property
    def is_buy(self) -> bool:
        """Check if this is a buy transaction."""
        return self.transaction_type == "buy"

    @property
    def is_sell(self) -> bool:
        """Check if this is a sell transaction."""
        return self.transaction_type == "sell"

    @property
    def is_dividend(self) -> bool:
        """Check if this is a dividend payment."""
        return self.transaction_type == "dividend"

    @property
    def date_object(self) -> datetime:
        """
        Get the transaction date as a datetime object.

        Returns:
            The transaction date as a datetime
        """
        return datetime.fromisoformat(self.date)

    @property
    def date_formatted(self) -> str:
        """
        Get the transaction date in a readable format.

        Returns:
            Formatted date string (e.g., '2024-01-15')
        """
        return self.date_object.strftime("%Y-%m-%d")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the transaction
        """
        return {
            "id": self.id,
            "symbol": self.symbol,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "price_per_unit": self.price_per_unit,
            "date": self.date,
            "fees": self.fees,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """
        Create a Transaction instance from a dictionary.

        Args:
            data: Dictionary containing transaction data

        Returns:
            A new Transaction instance
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            symbol=data["symbol"],
            transaction_type=data["transaction_type"],
            quantity=data["quantity"],
            price_per_unit=data["price_per_unit"],
            date=data.get("date", datetime.now().isoformat()),
            fees=data.get("fees", 0.0),
            notes=data.get("notes", ""),
        )

    @classmethod
    def create_buy(
        cls,
        symbol: str,
        quantity: float,
        price: float,
        fees: float = 0.0,
        notes: str = "",
        date: Optional[str] = None,
    ) -> "Transaction":
        """
        Factory method to create a buy transaction.

        Args:
            symbol: Ticker symbol
            quantity: Number of shares to buy
            price: Price per share
            fees: Transaction fees
            notes: Optional notes
            date: Optional transaction date (defaults to now)

        Returns:
            A new buy Transaction
        """
        return cls(
            symbol=symbol,
            transaction_type="buy",
            quantity=quantity,
            price_per_unit=price,
            fees=fees,
            notes=notes,
            date=date if date else datetime.now().isoformat(),
        )

    @classmethod
    def create_sell(
        cls,
        symbol: str,
        quantity: float,
        price: float,
        fees: float = 0.0,
        notes: str = "",
        date: Optional[str] = None,
    ) -> "Transaction":
        """
        Factory method to create a sell transaction.

        Args:
            symbol: Ticker symbol
            quantity: Number of shares to sell
            price: Price per share
            fees: Transaction fees
            notes: Optional notes
            date: Optional transaction date (defaults to now)

        Returns:
            A new sell Transaction
        """
        return cls(
            symbol=symbol,
            transaction_type="sell",
            quantity=quantity,
            price_per_unit=price,
            fees=fees,
            notes=notes,
            date=date if date else datetime.now().isoformat(),
        )

    @classmethod
    def create_dividend(
        cls,
        symbol: str,
        amount: float,
        notes: str = "",
        date: Optional[str] = None,
    ) -> "Transaction":
        """
        Factory method to create a dividend transaction.

        For dividends, we record the total amount as price_per_unit
        with quantity = 1 for simplicity.

        Args:
            symbol: Ticker symbol
            amount: Total dividend amount received
            notes: Optional notes
            date: Optional transaction date (defaults to now)

        Returns:
            A new dividend Transaction
        """
        return cls(
            symbol=symbol,
            transaction_type="dividend",
            quantity=1,  # Use 1 as a multiplier
            price_per_unit=amount,  # Total dividend amount
            fees=0.0,
            notes=notes,
            date=date if date else datetime.now().isoformat(),
        )

    def __str__(self) -> str:
        """String representation of the transaction."""
        type_str = self.transaction_type.upper()
        return (
            f"{self.date_formatted}: {type_str} {self.quantity} {self.symbol} "
            f"@ ${self.price_per_unit:.2f} = ${self.total_amount:.2f}"
        )

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"Transaction(id='{self.id[:8]}...', symbol='{self.symbol}', "
            f"type='{self.transaction_type}', qty={self.quantity}, "
            f"price={self.price_per_unit})"
        )
