"""
Data service for Invest AI Assistant.

Handles saving and loading portfolio data to/from JSON files.
Provides automatic backup and data integrity features.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from ..models.portfolio import Portfolio

# Set up logging
logger = logging.getLogger(__name__)


class DataService:
    """
    Service for persisting portfolio data to JSON files.

    Features:
    - Save/load portfolio data
    - Automatic backups before saving
    - Data validation
    - Error recovery
    """

    def __init__(self, data_dir: Path):
        """
        Initialize the data service.

        Args:
            data_dir: Directory where data files will be stored
        """
        self.data_dir = Path(data_dir)
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.backup_dir = self.data_dir / "backups"
        self.settings_file = self.data_dir / "settings.json"

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # PORTFOLIO OPERATIONS
    # =========================================================================

    def save_portfolio(self, portfolio: Portfolio, create_backup: bool = True) -> bool:
        """
        Save the portfolio to a JSON file.

        Args:
            portfolio: The Portfolio object to save
            create_backup: Whether to backup existing file first

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup of existing file
            if create_backup and self.portfolio_file.exists():
                self._create_backup()

            # Convert portfolio to dictionary
            data = portfolio.to_dict()

            # Add metadata
            data["_metadata"] = {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "app": "Invest AI Assistant",
            }

            # Write to file with pretty formatting
            with open(self.portfolio_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Portfolio saved successfully to {self.portfolio_file}")
            return True

        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to save portfolio: {e}")
            return False

    def load_portfolio(self) -> Optional[Portfolio]:
        """
        Load the portfolio from a JSON file.

        Returns:
            Portfolio object if successful, None otherwise
        """
        if not self.portfolio_file.exists():
            logger.info("No existing portfolio file found, creating new portfolio")
            return Portfolio()

        try:
            with open(self.portfolio_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Remove metadata before loading (it's not part of Portfolio)
            data.pop("_metadata", None)

            # Create Portfolio from dictionary
            portfolio = Portfolio.from_dict(data)
            logger.info(f"Portfolio loaded successfully: {portfolio.holdings_count} holdings")
            return portfolio

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse portfolio file: {e}")
            return self._try_recover_from_backup()

        except (IOError, KeyError, ValueError) as e:
            logger.error(f"Failed to load portfolio: {e}")
            return self._try_recover_from_backup()

    def portfolio_exists(self) -> bool:
        """Check if a portfolio file exists."""
        return self.portfolio_file.exists()

    # =========================================================================
    # BACKUP OPERATIONS
    # =========================================================================

    def _create_backup(self) -> Optional[Path]:
        """
        Create a backup of the current portfolio file.

        Returns:
            Path to the backup file, or None if failed
        """
        if not self.portfolio_file.exists():
            return None

        try:
            # Create timestamp-based backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"portfolio_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename

            # Copy file to backup location
            shutil.copy2(self.portfolio_file, backup_path)

            # Clean up old backups (keep last 10)
            self._cleanup_old_backups(keep_count=10)

            logger.info(f"Backup created: {backup_path}")
            return backup_path

        except IOError as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def _cleanup_old_backups(self, keep_count: int = 10) -> None:
        """
        Remove old backup files, keeping only the most recent ones.

        Args:
            keep_count: Number of backups to keep
        """
        try:
            # Get all backup files sorted by modification time
            backups = sorted(
                self.backup_dir.glob("portfolio_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            # Remove old backups
            for backup in backups[keep_count:]:
                backup.unlink()
                logger.debug(f"Removed old backup: {backup}")

        except IOError as e:
            logger.error(f"Failed to cleanup backups: {e}")

    def _try_recover_from_backup(self) -> Optional[Portfolio]:
        """
        Attempt to recover portfolio from the most recent backup.

        Returns:
            Portfolio if recovery successful, None otherwise
        """
        try:
            # Find the most recent backup
            backups = sorted(
                self.backup_dir.glob("portfolio_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            if not backups:
                logger.warning("No backups available for recovery")
                return None

            most_recent = backups[0]
            logger.info(f"Attempting recovery from: {most_recent}")

            with open(most_recent, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.pop("_metadata", None)
            portfolio = Portfolio.from_dict(data)
            logger.info("Portfolio recovered from backup successfully")
            return portfolio

        except Exception as e:
            logger.error(f"Recovery from backup failed: {e}")
            return None

    def get_backup_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available backups with metadata.

        Returns:
            List of dictionaries with backup info
        """
        backups = []
        for backup_path in self.backup_dir.glob("portfolio_backup_*.json"):
            try:
                stat = backup_path.stat()
                backups.append({
                    "filename": backup_path.name,
                    "path": str(backup_path),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            except IOError:
                continue

        # Sort by modification time, newest first
        backups.sort(key=lambda x: x["modified"], reverse=True)
        return backups

    def restore_from_backup(self, backup_path: str) -> Optional[Portfolio]:
        """
        Restore portfolio from a specific backup file.

        Args:
            backup_path: Path to the backup file

        Returns:
            Portfolio if successful, None otherwise
        """
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.pop("_metadata", None)
            portfolio = Portfolio.from_dict(data)
            logger.info(f"Portfolio restored from: {backup_path}")
            return portfolio

        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return None

    # =========================================================================
    # SETTINGS OPERATIONS
    # =========================================================================

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save application settings to a JSON file.

        Args:
            settings: Dictionary of settings to save

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def load_settings(self) -> Dict[str, Any]:
        """
        Load application settings from a JSON file.

        Returns:
            Dictionary of settings, or empty dict if file doesn't exist
        """
        if not self.settings_file.exists():
            return {}

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load settings: {e}")
            return {}

    # =========================================================================
    # EXPORT OPERATIONS
    # =========================================================================

    def export_portfolio_csv(self, portfolio: Portfolio, filepath: Path) -> bool:
        """
        Export portfolio holdings to a CSV file.

        Args:
            portfolio: The Portfolio to export
            filepath: Path for the CSV file

        Returns:
            True if successful, False otherwise
        """
        try:
            import csv

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    "Symbol",
                    "Name",
                    "Type",
                    "Sector",
                    "Quantity",
                    "Average Cost",
                    "Current Price",
                    "Cost Basis",
                    "Market Value",
                    "Unrealized Gain",
                    "Gain %",
                ])

                # Write holdings
                for holding in portfolio.get_all_holdings():
                    writer.writerow([
                        holding.symbol,
                        holding.name,
                        holding.asset_type,
                        holding.sector,
                        holding.quantity,
                        f"{holding.average_cost:.2f}",
                        f"{holding.current_price:.2f}" if holding.current_price else "N/A",
                        f"{holding.cost_basis:.2f}",
                        f"{holding.market_value:.2f}" if holding.market_value else "N/A",
                        f"{holding.unrealized_gain:.2f}" if holding.unrealized_gain else "N/A",
                        f"{holding.unrealized_gain_percent:.2f}%" if holding.unrealized_gain_percent else "N/A",
                    ])

            logger.info(f"Portfolio exported to CSV: {filepath}")
            return True

        except IOError as e:
            logger.error(f"Failed to export CSV: {e}")
            return False

    def export_transactions_csv(self, portfolio: Portfolio, filepath: Path) -> bool:
        """
        Export transaction history to a CSV file.

        Args:
            portfolio: The Portfolio to export
            filepath: Path for the CSV file

        Returns:
            True if successful, False otherwise
        """
        try:
            import csv

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    "Date",
                    "Type",
                    "Symbol",
                    "Quantity",
                    "Price",
                    "Fees",
                    "Total",
                    "Notes",
                ])

                # Write transactions
                for tx in portfolio.transactions:
                    writer.writerow([
                        tx.date_formatted,
                        tx.transaction_type.upper(),
                        tx.symbol,
                        tx.quantity,
                        f"{tx.price_per_unit:.2f}",
                        f"{tx.fees:.2f}",
                        f"{tx.total_amount:.2f}",
                        tx.notes,
                    ])

            logger.info(f"Transactions exported to CSV: {filepath}")
            return True

        except IOError as e:
            logger.error(f"Failed to export transactions CSV: {e}")
            return False
