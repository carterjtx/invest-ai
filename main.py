#!/usr/bin/env python3
"""
Invest AI Assistant - Main Entry Point

A Python desktop application for tracking investment portfolios,
providing AI-powered investment education, and visualizing portfolio performance.

This application is for EDUCATIONAL PURPOSES ONLY and should not be
considered financial advice.

Usage:
    python main.py

Requirements:
    See requirements.txt for full list of dependencies.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


def check_dependencies():
    """
    Check if required dependencies are installed.
    Returns a list of missing packages.
    """
    missing = []
    optional_missing = []

    # Required packages
    required = [
        ("tkinter", "tkinter"),  # Usually comes with Python
    ]

    # Optional but recommended packages
    optional = [
        ("yfinance", "yfinance"),
        ("requests", "requests"),
        ("anthropic", "anthropic"),
        ("matplotlib", "matplotlib"),
    ]

    for import_name, package_name in required:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    for import_name, package_name in optional:
        try:
            __import__(import_name)
        except ImportError:
            optional_missing.append(package_name)

    return missing, optional_missing


def setup_logging():
    """Configure application logging."""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "invest_ai.log"),
            logging.StreamHandler(),
        ],
    )


def main():
    """Main entry point for the application."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Check dependencies
    missing, optional_missing = check_dependencies()

    if missing:
        print("Error: Missing required dependencies:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease install them with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

    if optional_missing:
        print("Note: Some optional dependencies are not installed:")
        for pkg in optional_missing:
            print(f"  - {pkg}")
        print("\nFor full functionality, install them with:")
        print(f"  pip install {' '.join(optional_missing)}")
        print()

    # Import and run the application
    try:
        import tkinter as tk
        from src.gui.main_window import MainWindow

        logger.info("Starting Invest AI Assistant")
        print("Starting Invest AI Assistant...")
        print("=" * 50)

        # Create the root window
        root = tk.Tk()

        # Create the main application
        app = MainWindow(root)

        # Start the main loop
        root.mainloop()

        logger.info("Application closed")

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"\nError: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Application error: {e}")
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
