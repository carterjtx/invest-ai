"""
Settings dialog for Invest AI Assistant.

Allows users to configure API keys and other settings directly in the app.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from typing import TYPE_CHECKING, Dict, Any, Optional

if TYPE_CHECKING:
    from .main_window import MainWindow


class APIKeySettingsDialog(tk.Toplevel):
    """
    Dialog for configuring API keys.

    Users can enter their NewsAPI and Anthropic API keys here
    instead of editing config files.
    """

    def __init__(self, parent, main_window: "MainWindow"):
        """
        Initialize the API key settings dialog.

        Args:
            parent: Parent window
            main_window: Reference to main window for saving settings
        """
        super().__init__(parent)

        self.main_window = main_window
        self.result = None

        # Configure dialog
        self.title("API Key Settings")
        self.geometry("550x480")
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._load_current_keys()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="API Key Configuration",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main_frame,
            text="Enter your API keys below. Keys are saved locally and never shared.",
            foreground="#64748b",
            wraplength=500,
        ).pack(anchor="w", pady=(5, 15))

        # =====================================================================
        # Anthropic API Key Section
        # =====================================================================
        anthropic_frame = ttk.LabelFrame(
            main_frame,
            text="Anthropic API Key (for AI Assistant)",
            padding=10,
        )
        anthropic_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            anthropic_frame,
            text="Powers the AI investment assistant for educational Q&A",
            foreground="#64748b",
        ).pack(anchor="w")

        # Key entry
        key_frame = ttk.Frame(anthropic_frame)
        key_frame.pack(fill="x", pady=(10, 5))

        ttk.Label(key_frame, text="API Key:").pack(side="left")

        self.anthropic_key_var = tk.StringVar()
        self.anthropic_entry = ttk.Entry(
            key_frame,
            textvariable=self.anthropic_key_var,
            width=45,
            show="*",  # Hide the key by default
        )
        self.anthropic_entry.pack(side="left", padx=10)

        # Show/hide toggle
        self.show_anthropic_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            key_frame,
            text="Show",
            variable=self.show_anthropic_var,
            command=lambda: self._toggle_show(self.anthropic_entry, self.show_anthropic_var),
        ).pack(side="left")

        # Get key link
        link_frame = ttk.Frame(anthropic_frame)
        link_frame.pack(anchor="w", pady=(5, 0))

        ttk.Label(link_frame, text="Don't have a key?").pack(side="left")

        get_key_btn = ttk.Button(
            link_frame,
            text="Get Anthropic API Key",
            command=self._open_anthropic_signup,
        )
        get_key_btn.pack(side="left", padx=10)

        ttk.Label(
            anthropic_frame,
            text="Free tier available with usage limits",
            foreground="#16a34a",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(5, 0))

        # =====================================================================
        # NewsAPI Key Section
        # =====================================================================
        news_frame = ttk.LabelFrame(
            main_frame,
            text="NewsAPI Key (for Financial News)",
            padding=10,
        )
        news_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            news_frame,
            text="Provides market news and headlines for your holdings",
            foreground="#64748b",
        ).pack(anchor="w")

        # Key entry
        key_frame2 = ttk.Frame(news_frame)
        key_frame2.pack(fill="x", pady=(10, 5))

        ttk.Label(key_frame2, text="API Key:").pack(side="left")

        self.news_key_var = tk.StringVar()
        self.news_entry = ttk.Entry(
            key_frame2,
            textvariable=self.news_key_var,
            width=45,
            show="*",
        )
        self.news_entry.pack(side="left", padx=10)

        # Show/hide toggle
        self.show_news_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            key_frame2,
            text="Show",
            variable=self.show_news_var,
            command=lambda: self._toggle_show(self.news_entry, self.show_news_var),
        ).pack(side="left")

        # Get key link
        link_frame2 = ttk.Frame(news_frame)
        link_frame2.pack(anchor="w", pady=(5, 0))

        ttk.Label(link_frame2, text="Don't have a key?").pack(side="left")

        get_news_btn = ttk.Button(
            link_frame2,
            text="Get NewsAPI Key",
            command=self._open_newsapi_signup,
        )
        get_news_btn.pack(side="left", padx=10)

        ttk.Label(
            news_frame,
            text="Free tier: 1000 requests/day",
            foreground="#16a34a",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(5, 0))

        # =====================================================================
        # Status Section
        # =====================================================================
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding=10)
        status_frame.pack(fill="x", pady=(0, 15))

        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill="x")

        # Anthropic status
        ttk.Label(status_grid, text="AI Assistant:").grid(row=0, column=0, sticky="w", pady=2)
        self.anthropic_status = ttk.Label(status_grid, text="Checking...")
        self.anthropic_status.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        # News status
        ttk.Label(status_grid, text="News Service:").grid(row=1, column=0, sticky="w", pady=2)
        self.news_status = ttk.Label(status_grid, text="Checking...")
        self.news_status.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        # Price status (always available)
        ttk.Label(status_grid, text="Price Data:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(
            status_grid,
            text="Available (no key required)",
            foreground="#16a34a",
        ).grid(row=2, column=1, sticky="w", padx=10, pady=2)

        self._update_status_display()

        # =====================================================================
        # Buttons
        # =====================================================================
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
        ).pack(side="right")

        ttk.Button(
            btn_frame,
            text="Save & Apply",
            command=self._save_keys,
        ).pack(side="right", padx=10)

        ttk.Button(
            btn_frame,
            text="Test Keys",
            command=self._test_keys,
        ).pack(side="right", padx=10)

    def _toggle_show(self, entry: ttk.Entry, var: tk.BooleanVar):
        """Toggle showing/hiding the API key."""
        if var.get():
            entry.configure(show="")
        else:
            entry.configure(show="*")

    def _load_current_keys(self):
        """Load current API keys from settings."""
        settings = self.main_window.data_service.load_settings()

        anthropic_key = settings.get("anthropic_api_key", "")
        news_key = settings.get("news_api_key", "")

        self.anthropic_key_var.set(anthropic_key)
        self.news_key_var.set(news_key)

    def _update_status_display(self):
        """Update the status indicators."""
        # Check Anthropic
        if self.main_window.ai_service.is_available():
            self.anthropic_status.configure(
                text="Connected",
                foreground="#16a34a",
            )
        else:
            self.anthropic_status.configure(
                text="Not configured (using demo mode)",
                foreground="#d97706",
            )

        # Check News
        if self.main_window.news_service.is_available():
            self.news_status.configure(
                text="Connected",
                foreground="#16a34a",
            )
        else:
            self.news_status.configure(
                text="Not configured (using demo mode)",
                foreground="#d97706",
            )

    def _open_anthropic_signup(self):
        """Open Anthropic Console in browser."""
        webbrowser.open("https://console.anthropic.com/")

        # Show instructions
        messagebox.showinfo(
            "Get Anthropic API Key",
            "A browser window will open to the Anthropic Console.\n\n"
            "To get your API key:\n"
            "1. Sign up or log in to your account\n"
            "2. Go to 'API Keys' in the left sidebar\n"
            "3. Click 'Create Key'\n"
            "4. Copy the key and paste it here\n\n"
            "Note: You'll need to add billing info, but there's a free tier!",
        )

    def _open_newsapi_signup(self):
        """Open NewsAPI signup in browser."""
        webbrowser.open("https://newsapi.org/register")

        messagebox.showinfo(
            "Get NewsAPI Key",
            "A browser window will open to NewsAPI.\n\n"
            "To get your API key:\n"
            "1. Sign up for a free account\n"
            "2. Your API key will be shown on the dashboard\n"
            "3. Copy the key and paste it here\n\n"
            "Free tier includes 1000 requests per day!",
        )

    def _test_keys(self):
        """Test the entered API keys."""
        anthropic_key = self.anthropic_key_var.get().strip()
        news_key = self.news_key_var.get().strip()

        results = []

        # Test Anthropic key
        if anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=anthropic_key)
                # Make a minimal API call to test
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}],
                )
                results.append("Anthropic API Key: Valid!")
            except Exception as e:
                error_msg = str(e)
                if "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                    results.append("Anthropic API Key: Invalid key")
                else:
                    results.append(f"Anthropic API Key: Error - {error_msg[:50]}")
        else:
            results.append("Anthropic API Key: Not entered")

        # Test News key
        if news_key:
            try:
                import requests
                response = requests.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={"apiKey": news_key, "country": "us", "pageSize": 1},
                    timeout=10,
                )
                if response.status_code == 200:
                    results.append("NewsAPI Key: Valid!")
                elif response.status_code == 401:
                    results.append("NewsAPI Key: Invalid key")
                else:
                    results.append(f"NewsAPI Key: Error (status {response.status_code})")
            except Exception as e:
                results.append(f"NewsAPI Key: Error - {str(e)[:50]}")
        else:
            results.append("NewsAPI Key: Not entered")

        messagebox.showinfo("API Key Test Results", "\n".join(results))

    def _save_keys(self):
        """Save the API keys and reinitialize services."""
        anthropic_key = self.anthropic_key_var.get().strip()
        news_key = self.news_key_var.get().strip()

        # Load existing settings
        settings = self.main_window.data_service.load_settings()

        # Update with new keys
        settings["anthropic_api_key"] = anthropic_key
        settings["news_api_key"] = news_key

        # Save settings
        if self.main_window.data_service.save_settings(settings):
            # Reinitialize services with new keys
            self.main_window.reinitialize_services()

            messagebox.showinfo(
                "Settings Saved",
                "API keys have been saved and services reinitialized.\n\n"
                "The AI Assistant and News features will now use your keys.",
            )
            self.destroy()
        else:
            messagebox.showerror(
                "Save Failed",
                "Failed to save settings. Please try again.",
            )


class SettingsDialog(tk.Toplevel):
    """
    Main settings dialog with multiple sections.
    """

    def __init__(self, parent, main_window: "MainWindow"):
        """Initialize settings dialog."""
        super().__init__(parent)

        self.main_window = main_window

        self.title("Settings")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        # Center
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Settings",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 20))

        # API Keys section
        api_frame = ttk.LabelFrame(frame, text="API Configuration", padding=10)
        api_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            api_frame,
            text="Configure API keys for AI Assistant and News features.",
            foreground="#64748b",
        ).pack(anchor="w", pady=(0, 10))

        ttk.Button(
            api_frame,
            text="Configure API Keys...",
            command=self._open_api_settings,
        ).pack(anchor="w")

        # Current status
        status_frame = ttk.Frame(api_frame)
        status_frame.pack(fill="x", pady=(10, 0))

        ai_status = "Connected" if self.main_window.ai_service.is_available() else "Demo Mode"
        ai_color = "#16a34a" if self.main_window.ai_service.is_available() else "#d97706"
        ttk.Label(status_frame, text=f"AI Assistant: ", foreground="#64748b").pack(side="left")
        ttk.Label(status_frame, text=ai_status, foreground=ai_color).pack(side="left")

        news_status = "Connected" if self.main_window.news_service.is_available() else "Demo Mode"
        news_color = "#16a34a" if self.main_window.news_service.is_available() else "#d97706"
        ttk.Label(status_frame, text="   |   News: ", foreground="#64748b").pack(side="left")
        ttk.Label(status_frame, text=news_status, foreground=news_color).pack(side="left")

        # Data Management section
        data_frame = ttk.LabelFrame(frame, text="Data Management", padding=10)
        data_frame.pack(fill="x", pady=(0, 15))

        btn_row = ttk.Frame(data_frame)
        btn_row.pack(fill="x")

        ttk.Button(
            btn_row,
            text="Export Portfolio (CSV)",
            command=self._export_csv,
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            btn_row,
            text="Export Transactions",
            command=self._export_transactions,
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            btn_row,
            text="View Backups",
            command=self._view_backups,
        ).pack(side="left")

        # About section
        about_frame = ttk.LabelFrame(frame, text="About", padding=10)
        about_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            about_frame,
            text="Invest AI Assistant v1.0.0\n\n"
            "A portfolio tracking application with AI-powered investment education.\n\n"
            "DISCLAIMER: This is for educational purposes only, not financial advice.",
            wraplength=420,
            justify="left",
        ).pack(anchor="w")

        # Close button
        ttk.Button(
            frame,
            text="Close",
            command=self.destroy,
        ).pack(side="right", pady=(10, 0))

    def _open_api_settings(self):
        """Open API key settings dialog."""
        dialog = APIKeySettingsDialog(self, self.main_window)
        self.wait_window(dialog)
        # Refresh this dialog's status display
        self.destroy()
        SettingsDialog(self.master, self.main_window)

    def _export_csv(self):
        """Export portfolio to CSV."""
        from tkinter import filedialog
        from pathlib import Path

        filepath = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfilename="portfolio_export.csv",
        )
        if filepath:
            if self.main_window.data_service.export_portfolio_csv(
                self.main_window.portfolio, Path(filepath)
            ):
                messagebox.showinfo("Export Complete", f"Portfolio exported to:\n{filepath}")
            else:
                messagebox.showerror("Export Failed", "Failed to export portfolio")

    def _export_transactions(self):
        """Export transactions to CSV."""
        from tkinter import filedialog
        from pathlib import Path

        filepath = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfilename="transactions_export.csv",
        )
        if filepath:
            if self.main_window.data_service.export_transactions_csv(
                self.main_window.portfolio, Path(filepath)
            ):
                messagebox.showinfo("Export Complete", f"Transactions exported to:\n{filepath}")
            else:
                messagebox.showerror("Export Failed", "Failed to export transactions")

    def _view_backups(self):
        """Show backup files."""
        backups = self.main_window.data_service.get_backup_list()
        if not backups:
            messagebox.showinfo("Backups", "No backup files found")
            return

        backup_list = "\n".join(
            f"- {b['filename']} ({b['modified'][:10]})"
            for b in backups[:10]
        )
        messagebox.showinfo(
            "Available Backups",
            f"Found {len(backups)} backup(s):\n\n{backup_list}"
        )
