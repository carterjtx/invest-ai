"""
Portfolio model for Invest AI Assistant.

The Portfolio is the central data model that contains all holdings,
transactions, and historical snapshots for tracking performance over time.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from .holding import Holding
from .transaction import Transaction


@dataclass
class PortfolioSnapshot:
    """
    A snapshot of portfolio value at a specific point in time.
    Used for tracking historical performance.
    """

    timestamp: str  # ISO format datetime
    total_value: float  # Total portfolio value at this time
    total_cost: float  # Total cost basis at this time
    holdings_count: int  # Number of holdings
    cash_value: float = 0.0  # Any uninvested cash

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "total_value": self.total_value,
            "total_cost": self.total_cost,
            "holdings_count": self.holdings_count,
            "cash_value": self.cash_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PortfolioSnapshot":
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            total_value=data["total_value"],
            total_cost=data["total_cost"],
            holdings_count=data["holdings_count"],
            cash_value=data.get("cash_value", 0.0),
        )


@dataclass
class DividendRecord:
    """
    Record of dividend payment for tracking dividend income.
    """

    symbol: str
    amount: float
    date: str  # ISO format date
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "symbol": self.symbol,
            "amount": self.amount,
            "date": self.date,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DividendRecord":
        """Create from dictionary."""
        return cls(
            symbol=data["symbol"],
            amount=data["amount"],
            date=data["date"],
            notes=data.get("notes", ""),
        )


@dataclass
class Portfolio:
    """
    Main portfolio class containing all investment data.

    Attributes:
        name: Name of the portfolio (e.g., 'My Retirement Portfolio')
        holdings: Dictionary of holdings keyed by symbol
        transactions: List of all buy/sell/dividend transactions
        snapshots: Historical value snapshots for charting
        dividends: List of dividend payments received
        created_at: When the portfolio was created
        last_modified: When the portfolio was last modified
        notes: Optional portfolio-level notes
    """

    # Portfolio metadata
    name: str = "My Portfolio"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

    # Core data
    holdings: Dict[str, Holding] = field(default_factory=dict)
    transactions: List[Transaction] = field(default_factory=list)
    snapshots: List[PortfolioSnapshot] = field(default_factory=list)
    dividends: List[DividendRecord] = field(default_factory=list)

    # Cash tracking
    cash_balance: float = 0.0

    def _update_modified(self) -> None:
        """Update the last modified timestamp."""
        self.last_modified = datetime.now().isoformat()

    # =========================================================================
    # HOLDING MANAGEMENT
    # =========================================================================

    def add_holding(
        self,
        symbol: str,
        name: str,
        asset_type: str,
        quantity: float,
        price_per_unit: float,
        sector: str = "Other",
        notes: str = "",
        record_transaction: bool = True,
    ) -> Holding:
        """
        Add a new holding or add to an existing holding.

        Args:
            symbol: Ticker symbol (e.g., 'AAPL')
            name: Full name (e.g., 'Apple Inc.')
            asset_type: Type of asset (stock, etf, crypto, etc.)
            quantity: Number of shares to buy
            price_per_unit: Purchase price per share
            sector: Market sector
            notes: Optional notes
            record_transaction: Whether to record this as a transaction

        Returns:
            The created or updated Holding
        """
        symbol = symbol.upper()

        if symbol in self.holdings:
            # Add to existing holding
            holding = self.holdings[symbol]
            holding.add_shares(quantity, price_per_unit)
            if notes:
                holding.notes = notes
        else:
            # Create new holding
            holding = Holding(
                symbol=symbol,
                name=name,
                asset_type=asset_type,
                quantity=quantity,
                average_cost=price_per_unit,
                sector=sector,
                notes=notes,
            )
            self.holdings[symbol] = holding

        # Record the transaction
        if record_transaction:
            transaction = Transaction.create_buy(
                symbol=symbol,
                quantity=quantity,
                price=price_per_unit,
                notes=notes,
            )
            self.transactions.append(transaction)

        self._update_modified()
        return holding

    def sell_holding(
        self,
        symbol: str,
        quantity: float,
        price_per_unit: float,
        notes: str = "",
    ) -> Tuple[float, float]:
        """
        Sell shares from a holding.

        Args:
            symbol: Ticker symbol to sell
            quantity: Number of shares to sell
            price_per_unit: Sale price per share
            notes: Optional notes

        Returns:
            Tuple of (proceeds, realized_gain)

        Raises:
            KeyError: If holding doesn't exist
            ValueError: If trying to sell more than owned
        """
        symbol = symbol.upper()

        if symbol not in self.holdings:
            raise KeyError(f"No holding found for symbol: {symbol}")

        holding = self.holdings[symbol]
        cost_basis = holding.remove_shares(quantity)
        proceeds = quantity * price_per_unit
        realized_gain = proceeds - cost_basis

        # Record the transaction
        transaction = Transaction.create_sell(
            symbol=symbol,
            quantity=quantity,
            price=price_per_unit,
            notes=notes,
        )
        self.transactions.append(transaction)

        # Remove holding if fully sold
        if holding.quantity == 0:
            del self.holdings[symbol]

        self._update_modified()
        return proceeds, realized_gain

    def remove_holding(self, symbol: str) -> Optional[Holding]:
        """
        Completely remove a holding from the portfolio.

        Args:
            symbol: Ticker symbol to remove

        Returns:
            The removed Holding, or None if not found
        """
        symbol = symbol.upper()
        holding = self.holdings.pop(symbol, None)
        if holding:
            self._update_modified()
        return holding

    def get_holding(self, symbol: str) -> Optional[Holding]:
        """
        Get a specific holding by symbol.

        Args:
            symbol: Ticker symbol

        Returns:
            The Holding if found, None otherwise
        """
        return self.holdings.get(symbol.upper())

    def get_all_holdings(self) -> List[Holding]:
        """
        Get all holdings as a list, sorted by market value descending.

        Returns:
            List of Holdings sorted by value
        """
        holdings = list(self.holdings.values())
        # Sort by market value (or cost basis if price not available)
        holdings.sort(
            key=lambda h: h.market_value if h.market_value else h.cost_basis,
            reverse=True,
        )
        return holdings

    def get_symbols(self) -> List[str]:
        """
        Get list of all holding symbols.

        Returns:
            List of ticker symbols
        """
        return list(self.holdings.keys())

    # =========================================================================
    # DIVIDEND MANAGEMENT
    # =========================================================================

    def record_dividend(
        self,
        symbol: str,
        amount: float,
        date: Optional[str] = None,
        notes: str = "",
    ) -> DividendRecord:
        """
        Record a dividend payment received.

        Args:
            symbol: Ticker symbol that paid the dividend
            amount: Dividend amount received
            date: Date of payment (defaults to today)
            notes: Optional notes

        Returns:
            The created DividendRecord
        """
        symbol = symbol.upper()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        record = DividendRecord(
            symbol=symbol,
            amount=amount,
            date=date,
            notes=notes,
        )
        self.dividends.append(record)

        # Also record as a transaction
        transaction = Transaction.create_dividend(
            symbol=symbol,
            amount=amount,
            notes=notes,
            date=date,
        )
        self.transactions.append(transaction)

        self._update_modified()
        return record

    def get_total_dividends(self, symbol: Optional[str] = None) -> float:
        """
        Get total dividend income, optionally filtered by symbol.

        Args:
            symbol: Optional symbol to filter by

        Returns:
            Total dividend amount
        """
        if symbol:
            symbol = symbol.upper()
            return sum(d.amount for d in self.dividends if d.symbol == symbol)
        return sum(d.amount for d in self.dividends)

    def get_annual_dividend_income(self, year: Optional[int] = None) -> float:
        """
        Get total dividend income for a specific year.

        Args:
            year: Year to calculate (defaults to current year)

        Returns:
            Total dividend income for the year
        """
        if year is None:
            year = datetime.now().year

        total = 0.0
        for dividend in self.dividends:
            div_year = datetime.fromisoformat(dividend.date).year
            if div_year == year:
                total += dividend.amount
        return total

    # =========================================================================
    # PORTFOLIO VALUE CALCULATIONS
    # =========================================================================

    @property
    def total_cost_basis(self) -> float:
        """
        Calculate total cost basis of all holdings.

        Returns:
            Sum of all holdings' cost basis
        """
        return sum(h.cost_basis for h in self.holdings.values())

    @property
    def total_market_value(self) -> Optional[float]:
        """
        Calculate total market value of all holdings.

        Returns:
            Sum of all holdings' market value, or None if any price unavailable
        """
        total = 0.0
        for holding in self.holdings.values():
            if holding.market_value is None:
                return None
            total += holding.market_value
        return total

    @property
    def total_unrealized_gain(self) -> Optional[float]:
        """
        Calculate total unrealized gain/loss.

        Returns:
            Total gain/loss or None if prices unavailable
        """
        market_value = self.total_market_value
        if market_value is None:
            return None
        return market_value - self.total_cost_basis

    @property
    def total_unrealized_gain_percent(self) -> Optional[float]:
        """
        Calculate total unrealized gain/loss as percentage.

        Returns:
            Percentage gain/loss or None if prices unavailable
        """
        cost = self.total_cost_basis
        if cost == 0:
            return None
        gain = self.total_unrealized_gain
        if gain is None:
            return None
        return (gain / cost) * 100

    @property
    def holdings_count(self) -> int:
        """Get number of holdings in portfolio."""
        return len(self.holdings)

    # =========================================================================
    # SECTOR ANALYSIS
    # =========================================================================

    def get_sector_allocation(self) -> Dict[str, float]:
        """
        Calculate portfolio allocation by sector.

        Returns:
            Dictionary mapping sector names to percentage allocation
        """
        sector_values: Dict[str, float] = {}
        total_value = 0.0

        for holding in self.holdings.values():
            value = holding.market_value or holding.cost_basis
            sector = holding.sector or "Other"
            sector_values[sector] = sector_values.get(sector, 0) + value
            total_value += value

        if total_value == 0:
            return {}

        # Convert to percentages
        return {
            sector: (value / total_value) * 100
            for sector, value in sector_values.items()
        }

    def get_asset_type_allocation(self) -> Dict[str, float]:
        """
        Calculate portfolio allocation by asset type.

        Returns:
            Dictionary mapping asset types to percentage allocation
        """
        type_values: Dict[str, float] = {}
        total_value = 0.0

        for holding in self.holdings.values():
            value = holding.market_value or holding.cost_basis
            asset_type = holding.asset_type or "other"
            type_values[asset_type] = type_values.get(asset_type, 0) + value
            total_value += value

        if total_value == 0:
            return {}

        # Convert to percentages
        return {
            asset_type: (value / total_value) * 100
            for asset_type, value in type_values.items()
        }

    # =========================================================================
    # HISTORICAL TRACKING
    # =========================================================================

    def take_snapshot(self) -> PortfolioSnapshot:
        """
        Take a snapshot of current portfolio value.

        Returns:
            The created PortfolioSnapshot
        """
        snapshot = PortfolioSnapshot(
            timestamp=datetime.now().isoformat(),
            total_value=self.total_market_value or self.total_cost_basis,
            total_cost=self.total_cost_basis,
            holdings_count=self.holdings_count,
            cash_value=self.cash_balance,
        )
        self.snapshots.append(snapshot)
        self._update_modified()
        return snapshot

    def get_snapshots_in_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PortfolioSnapshot]:
        """
        Get snapshots within a date range.

        Args:
            start_date: Start of range (inclusive)
            end_date: End of range (inclusive)

        Returns:
            List of snapshots in the range
        """
        filtered = []
        for snapshot in self.snapshots:
            snap_date = datetime.fromisoformat(snapshot.timestamp)
            if start_date and snap_date < start_date:
                continue
            if end_date and snap_date > end_date:
                continue
            filtered.append(snapshot)
        return filtered

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert portfolio to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the portfolio
        """
        return {
            "name": self.name,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "notes": self.notes,
            "cash_balance": self.cash_balance,
            "holdings": {
                symbol: holding.to_dict()
                for symbol, holding in self.holdings.items()
            },
            "transactions": [t.to_dict() for t in self.transactions],
            "snapshots": [s.to_dict() for s in self.snapshots],
            "dividends": [d.to_dict() for d in self.dividends],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        """
        Create a Portfolio instance from a dictionary.

        Args:
            data: Dictionary containing portfolio data

        Returns:
            A new Portfolio instance
        """
        portfolio = cls(
            name=data.get("name", "My Portfolio"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_modified=data.get("last_modified", datetime.now().isoformat()),
            notes=data.get("notes", ""),
            cash_balance=data.get("cash_balance", 0.0),
        )

        # Load holdings
        holdings_data = data.get("holdings", {})
        for symbol, holding_dict in holdings_data.items():
            portfolio.holdings[symbol] = Holding.from_dict(holding_dict)

        # Load transactions
        transactions_data = data.get("transactions", [])
        portfolio.transactions = [
            Transaction.from_dict(t) for t in transactions_data
        ]

        # Load snapshots
        snapshots_data = data.get("snapshots", [])
        portfolio.snapshots = [
            PortfolioSnapshot.from_dict(s) for s in snapshots_data
        ]

        # Load dividends
        dividends_data = data.get("dividends", [])
        portfolio.dividends = [
            DividendRecord.from_dict(d) for d in dividends_data
        ]

        return portfolio

    def __str__(self) -> str:
        """String representation of the portfolio."""
        value = self.total_market_value
        value_str = f"${value:,.2f}" if value else "N/A"
        return f"Portfolio '{self.name}': {self.holdings_count} holdings, Value: {value_str}"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"Portfolio(name='{self.name}', holdings={self.holdings_count}, "
            f"transactions={len(self.transactions)})"
        )
