"""
Financial calculations utility module for Invest AI Assistant.

Provides functions for portfolio analysis, risk assessment,
and financial metrics.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

from .constants import CONCENTRATION_THRESHOLDS, RiskLevel


@dataclass
class RiskAssessment:
    """
    Results of a portfolio risk assessment.

    Attributes:
        risk_level: Overall risk level (low, moderate, high, very_high)
        score: Numeric risk score (0-100, higher = more risky)
        warnings: List of specific risk warnings
        recommendations: Educational suggestions
    """

    risk_level: str
    score: float
    warnings: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_level": self.risk_level,
            "score": self.score,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


def calculate_portfolio_value(
    holdings: List[Dict[str, Any]],
) -> Tuple[float, float, float]:
    """
    Calculate total portfolio value, cost, and gain.

    Args:
        holdings: List of holding dictionaries with quantity, average_cost,
                  and current_price fields

    Returns:
        Tuple of (total_value, total_cost, unrealized_gain)
    """
    total_value = 0.0
    total_cost = 0.0

    for holding in holdings:
        quantity = holding.get("quantity", 0)
        avg_cost = holding.get("average_cost", 0)
        current_price = holding.get("current_price")

        cost = quantity * avg_cost
        total_cost += cost

        if current_price is not None:
            total_value += quantity * current_price
        else:
            # Use cost basis if no current price
            total_value += cost

    unrealized_gain = total_value - total_cost
    return total_value, total_cost, unrealized_gain


def calculate_percent_change(current: float, original: float) -> Optional[float]:
    """
    Calculate percentage change between two values.

    Args:
        current: Current value
        original: Original/base value

    Returns:
        Percentage change, or None if original is zero
    """
    if original == 0:
        return None
    return ((current - original) / original) * 100


def calculate_allocation(
    holdings: List[Dict[str, Any]],
    group_by: str = "sector",
) -> Dict[str, float]:
    """
    Calculate portfolio allocation by a given category.

    Args:
        holdings: List of holding dictionaries
        group_by: Field to group by (sector, asset_type, etc.)

    Returns:
        Dictionary mapping category names to percentages
    """
    group_values: Dict[str, float] = {}
    total_value = 0.0

    for holding in holdings:
        # Use market value if available, otherwise cost basis
        quantity = holding.get("quantity", 0)
        price = holding.get("current_price") or holding.get("average_cost", 0)
        value = quantity * price

        category = holding.get(group_by, "Other")
        group_values[category] = group_values.get(category, 0) + value
        total_value += value

    if total_value == 0:
        return {}

    # Convert to percentages
    return {
        category: (value / total_value) * 100
        for category, value in group_values.items()
    }


def calculate_holding_weights(
    holdings: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Calculate the weight (percentage) of each holding in the portfolio.

    Args:
        holdings: List of holding dictionaries

    Returns:
        Dictionary mapping symbols to weight percentages
    """
    weights: Dict[str, float] = {}
    total_value = 0.0

    # Calculate total value
    for holding in holdings:
        quantity = holding.get("quantity", 0)
        price = holding.get("current_price") or holding.get("average_cost", 0)
        value = quantity * price
        symbol = holding.get("symbol", "UNKNOWN")
        weights[symbol] = value
        total_value += value

    if total_value == 0:
        return {}

    # Convert to percentages
    return {
        symbol: (value / total_value) * 100
        for symbol, value in weights.items()
    }


def assess_portfolio_risk(
    holdings: List[Dict[str, Any]],
    sector_allocation: Optional[Dict[str, float]] = None,
) -> RiskAssessment:
    """
    Assess the risk level of a portfolio based on diversification.

    Args:
        holdings: List of holding dictionaries
        sector_allocation: Pre-calculated sector allocation (optional)

    Returns:
        RiskAssessment object with risk level and details
    """
    warnings = []
    recommendations = []
    risk_score = 0  # Start at 0, add points for risk factors

    num_holdings = len(holdings)

    # Calculate weights if needed
    weights = calculate_holding_weights(holdings)

    # Calculate sector allocation if not provided
    if sector_allocation is None:
        sector_allocation = calculate_allocation(holdings, "sector")

    # =========================================================================
    # Check number of holdings
    # =========================================================================
    min_holdings = CONCENTRATION_THRESHOLDS["min_holdings_diversified"]

    if num_holdings == 0:
        risk_score = 0
        return RiskAssessment(
            risk_level="N/A",
            score=0,
            warnings=["Portfolio is empty"],
            recommendations=["Add holdings to begin tracking your portfolio"],
        )

    if num_holdings == 1:
        risk_score += 40
        warnings.append("Only 1 holding - portfolio is highly concentrated")
        recommendations.append(
            "Consider diversifying across multiple investments to spread risk"
        )
    elif num_holdings < min_holdings:
        risk_score += 20
        warnings.append(
            f"Only {num_holdings} holdings - portfolio may benefit from more diversification"
        )
        recommendations.append(
            f"Many experts suggest holding at least {min_holdings} positions for basic diversification"
        )

    # =========================================================================
    # Check individual holding concentration
    # =========================================================================
    warning_threshold = CONCENTRATION_THRESHOLDS["single_holding_warning"] * 100
    danger_threshold = CONCENTRATION_THRESHOLDS["single_holding_danger"] * 100

    for symbol, weight in weights.items():
        if weight > danger_threshold:
            risk_score += 30
            warnings.append(
                f"{symbol} is {weight:.1f}% of portfolio - very high concentration"
            )
        elif weight > warning_threshold:
            risk_score += 15
            warnings.append(
                f"{symbol} is {weight:.1f}% of portfolio - moderate concentration"
            )

    if any(w > warning_threshold for w in weights.values()):
        recommendations.append(
            "Consider whether any single position is larger than you're comfortable with"
        )

    # =========================================================================
    # Check sector concentration
    # =========================================================================
    num_sectors = len(sector_allocation)
    min_sectors = CONCENTRATION_THRESHOLDS["min_sectors_diversified"]
    sector_warning = CONCENTRATION_THRESHOLDS["single_sector_warning"] * 100
    sector_danger = CONCENTRATION_THRESHOLDS["single_sector_danger"] * 100

    if num_sectors < min_sectors and num_sectors > 0:
        risk_score += 15
        warnings.append(
            f"Only {num_sectors} sectors represented - limited sector diversification"
        )
        recommendations.append(
            "Investing across different sectors can help reduce sector-specific risk"
        )

    for sector, pct in sector_allocation.items():
        if pct > sector_danger:
            risk_score += 25
            warnings.append(
                f"{sector} sector is {pct:.1f}% of portfolio - very high sector concentration"
            )
        elif pct > sector_warning:
            risk_score += 10
            warnings.append(
                f"{sector} sector is {pct:.1f}% of portfolio - moderate sector concentration"
            )

    # =========================================================================
    # Check for high-risk asset types
    # =========================================================================
    type_allocation = calculate_allocation(holdings, "asset_type")

    crypto_pct = type_allocation.get("crypto", 0)
    if crypto_pct > 30:
        risk_score += 25
        warnings.append(
            f"Cryptocurrency is {crypto_pct:.1f}% of portfolio - highly volatile asset class"
        )
        recommendations.append(
            "Cryptocurrency is highly volatile - ensure this aligns with your risk tolerance"
        )
    elif crypto_pct > 10:
        risk_score += 10
        warnings.append(
            f"Cryptocurrency is {crypto_pct:.1f}% of portfolio - volatile asset class"
        )

    # =========================================================================
    # Determine overall risk level
    # =========================================================================
    risk_score = min(risk_score, 100)  # Cap at 100

    if risk_score < 20:
        risk_level = RiskLevel.LOW.value
    elif risk_score < 45:
        risk_level = RiskLevel.MODERATE.value
    elif risk_score < 70:
        risk_level = RiskLevel.HIGH.value
    else:
        risk_level = RiskLevel.VERY_HIGH.value

    # Add general recommendation if none yet
    if not recommendations:
        recommendations.append(
            "Your portfolio appears reasonably diversified. Continue monitoring and rebalancing as needed."
        )

    return RiskAssessment(
        risk_level=risk_level,
        score=risk_score,
        warnings=warnings,
        recommendations=recommendations,
    )


def calculate_dividend_metrics(
    dividends: List[Dict[str, Any]],
    total_portfolio_value: float,
) -> Dict[str, float]:
    """
    Calculate dividend-related metrics.

    Args:
        dividends: List of dividend records
        total_portfolio_value: Current total portfolio value

    Returns:
        Dictionary with dividend metrics
    """
    if not dividends:
        return {
            "total_received": 0,
            "annual_income": 0,
            "portfolio_yield": 0,
            "monthly_average": 0,
        }

    total_received = sum(d.get("amount", 0) for d in dividends)

    # Calculate annual income (last 12 months)
    one_year_ago = datetime.now() - timedelta(days=365)
    annual_income = sum(
        d.get("amount", 0)
        for d in dividends
        if datetime.fromisoformat(d.get("date", "2000-01-01")) >= one_year_ago
    )

    # Calculate portfolio yield
    portfolio_yield = 0
    if total_portfolio_value > 0:
        portfolio_yield = (annual_income / total_portfolio_value) * 100

    # Calculate monthly average (over all time)
    if dividends:
        dates = [
            datetime.fromisoformat(d.get("date", "2000-01-01"))
            for d in dividends
        ]
        first_date = min(dates)
        months = max(1, (datetime.now() - first_date).days / 30)
        monthly_average = total_received / months
    else:
        monthly_average = 0

    return {
        "total_received": total_received,
        "annual_income": annual_income,
        "portfolio_yield": portfolio_yield,
        "monthly_average": monthly_average,
    }


def calculate_performance_vs_benchmark(
    portfolio_values: List[Tuple[str, float]],
    benchmark_values: List[Tuple[str, float]],
) -> Dict[str, Any]:
    """
    Calculate portfolio performance compared to a benchmark.

    Args:
        portfolio_values: List of (date, value) tuples for portfolio
        benchmark_values: List of (date, value) tuples for benchmark

    Returns:
        Dictionary with performance comparison metrics
    """
    if not portfolio_values or not benchmark_values:
        return {
            "portfolio_return": 0,
            "benchmark_return": 0,
            "alpha": 0,
            "outperforming": False,
        }

    # Normalize both to start at 100
    portfolio_start = portfolio_values[0][1]
    portfolio_end = portfolio_values[-1][1]
    benchmark_start = benchmark_values[0][1]
    benchmark_end = benchmark_values[-1][1]

    if portfolio_start == 0 or benchmark_start == 0:
        return {
            "portfolio_return": 0,
            "benchmark_return": 0,
            "alpha": 0,
            "outperforming": False,
        }

    portfolio_return = ((portfolio_end - portfolio_start) / portfolio_start) * 100
    benchmark_return = ((benchmark_end - benchmark_start) / benchmark_start) * 100
    alpha = portfolio_return - benchmark_return

    return {
        "portfolio_return": portfolio_return,
        "benchmark_return": benchmark_return,
        "alpha": alpha,
        "outperforming": alpha > 0,
    }


def format_currency(amount: float, include_sign: bool = False) -> str:
    """
    Format a number as currency.

    Args:
        amount: The amount to format
        include_sign: Whether to include + for positive numbers

    Returns:
        Formatted currency string
    """
    if include_sign and amount > 0:
        return f"+${amount:,.2f}"
    elif amount < 0:
        return f"-${abs(amount):,.2f}"
    else:
        return f"${amount:,.2f}"


def format_percent(value: float, include_sign: bool = True) -> str:
    """
    Format a number as a percentage.

    Args:
        value: The percentage value
        include_sign: Whether to include + for positive numbers

    Returns:
        Formatted percentage string
    """
    if include_sign and value > 0:
        return f"+{value:.2f}%"
    else:
        return f"{value:.2f}%"


def format_large_number(value: float) -> str:
    """
    Format large numbers with K, M, B suffixes.

    Args:
        value: The number to format

    Returns:
        Formatted string (e.g., "1.5M", "250K")
    """
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.2f}K"
    else:
        return f"${value:.2f}"
