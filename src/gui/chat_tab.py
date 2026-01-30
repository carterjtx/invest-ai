"""
AI Chat tab for Invest AI Assistant.

Provides a conversational interface for asking investment questions
and getting portfolio analysis from the AI assistant.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, TYPE_CHECKING
import logging
import threading
from datetime import datetime

from .widgets import create_tooltip, ScrollableFrame
from ..utils.constants import INVESTING_TERMS

if TYPE_CHECKING:
    from .main_window import MainWindow

logger = logging.getLogger(__name__)


class ChatTab(ttk.Frame):
    """
    AI Chat interface tab.

    Allows users to ask questions about investing concepts
    and get analysis of their portfolio.
    """

    def __init__(self, parent, main_window: "MainWindow"):
        """
        Initialize chat tab.

        Args:
            parent: Parent notebook widget
            main_window: Reference to main window
        """
        super().__init__(parent, padding=10)

        self.main_window = main_window
        self.is_processing = False

        self._create_widgets()
        self._add_welcome_message()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container with two columns
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Left side - Chat interface
        chat_container = ttk.Frame(container)
        chat_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Header
        header = ttk.Frame(chat_container)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header,
            text="AI Investment Assistant",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        # AI status indicator
        ai_available = self.main_window.ai_service.is_available()
        status_text = "Connected" if ai_available else "Demo Mode"
        status_color = "#16a34a" if ai_available else "#d97706"

        ttk.Label(
            header,
            text=f"  ({status_text})",
            foreground=status_color,
            font=("Segoe UI", 9),
        ).pack(side="left")

        # Clear button
        ttk.Button(
            header,
            text="Clear Chat",
            command=self._clear_chat,
        ).pack(side="right")

        # Chat display area (scrollable)
        self.chat_scroll = ScrollableFrame(chat_container)
        self.chat_scroll.pack(fill="both", expand=True)

        self.chat_container = self.chat_scroll.inner_frame

        # Input area
        input_frame = ttk.Frame(chat_container)
        input_frame.pack(fill="x", pady=(10, 0))

        # Text input
        self.input_text = tk.Text(
            input_frame,
            height=3,
            wrap="word",
            font=("Segoe UI", 10),
        )
        self.input_text.pack(side="left", fill="both", expand=True)

        # Bind Enter key (Shift+Enter for newline)
        self.input_text.bind("<Return>", self._on_enter)
        self.input_text.bind("<Shift-Return>", lambda e: None)

        # Send button
        self.send_btn = ttk.Button(
            input_frame,
            text="Send",
            command=self._send_message,
            width=10,
        )
        self.send_btn.pack(side="right", padx=(10, 0), fill="y")

        # Right side - Quick actions and tips
        sidebar = ttk.Frame(container, width=250)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        # Quick actions
        self._create_quick_actions(sidebar)

        # Tips section
        self._create_tips_section(sidebar)

    def _create_quick_actions(self, parent):
        """Create quick action buttons."""
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding=10)
        actions_frame.pack(fill="x", pady=(0, 10))

        actions = [
            ("Analyze My Portfolio", self._analyze_portfolio),
            ("Explain Diversification", lambda: self._quick_question("What is diversification and why is it important?")),
            ("What Are ETFs?", lambda: self._quick_question("What are ETFs and how do they work?")),
            ("Risk vs Return", lambda: self._quick_question("Explain the relationship between risk and return in investing")),
            ("Dividend Investing", lambda: self._quick_question("What is dividend investing and how do dividend yields work?")),
        ]

        for text, command in actions:
            btn = ttk.Button(
                actions_frame,
                text=text,
                command=command,
            )
            btn.pack(fill="x", pady=2)

    def _create_tips_section(self, parent):
        """Create tips section."""
        tips_frame = ttk.LabelFrame(parent, text="Tips", padding=10)
        tips_frame.pack(fill="x")

        tips = [
            "Ask about any investing term",
            "Request portfolio analysis",
            "Learn about different assets",
            "Understand risk concepts",
        ]

        for tip in tips:
            ttk.Label(
                tips_frame,
                text=f"• {tip}",
                foreground="#64748b",
                wraplength=200,
            ).pack(anchor="w", pady=2)

        # Disclaimer
        ttk.Separator(tips_frame).pack(fill="x", pady=10)

        ttk.Label(
            tips_frame,
            text="Remember: This is for educational purposes only, not financial advice.",
            foreground="#d97706",
            wraplength=200,
            font=("Segoe UI", 8),
        ).pack(anchor="w")

    def _add_welcome_message(self):
        """Add welcome message to chat."""
        ai_available = self.main_window.ai_service.is_available()

        if ai_available:
            welcome = (
                "Hello! I'm your AI investment assistant. I can help you understand "
                "investing concepts, analyze your portfolio, and answer questions about "
                "stocks, ETFs, cryptocurrencies, and more.\n\n"
                "What would you like to learn about today?\n\n"
                "Remember: I provide educational information only, not financial advice."
            )
        else:
            welcome = (
                "Hello! I'm your AI investment assistant running in demo mode.\n\n"
                "To enable full AI capabilities, configure your Anthropic API key in config.py.\n\n"
                "In demo mode, I can still help with basic investing questions. Try asking about "
                "diversification, dividends, or risk!\n\n"
                "Remember: I provide educational information only, not financial advice."
            )

        self._add_message("assistant", welcome)

    def _add_message(self, role: str, content: str):
        """
        Add a message to the chat display.

        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        # Message container
        msg_frame = ttk.Frame(self.chat_container)
        msg_frame.pack(fill="x", pady=5)

        # Styling based on role
        if role == "user":
            bg_color = "#e0e7ff"
            anchor = "e"
            label_text = "You"
        else:
            bg_color = "#f1f5f9"
            anchor = "w"
            label_text = "AI Assistant"

        # Inner frame for the message bubble
        bubble = ttk.Frame(msg_frame)
        bubble.pack(anchor=anchor, fill="x", padx=(50 if role == "user" else 0, 50 if role == "assistant" else 0))

        # Header with role label
        header = ttk.Frame(bubble)
        header.pack(fill="x")

        ttk.Label(
            header,
            text=label_text,
            font=("Segoe UI", 9, "bold"),
            foreground="#64748b",
        ).pack(anchor=anchor)

        # Message content
        # Use a Text widget for better text wrapping
        msg_text = tk.Text(
            bubble,
            wrap="word",
            height=1,
            font=("Segoe UI", 10),
            bg=bg_color,
            relief="flat",
            padx=10,
            pady=8,
            cursor="arrow",
        )
        msg_text.pack(fill="x")

        # Insert content and auto-resize
        msg_text.insert("1.0", content)
        msg_text.configure(state="disabled")

        # Calculate height based on content
        num_lines = int(msg_text.index("end-1c").split(".")[0])
        # Account for wrapping - estimate based on content length
        avg_chars_per_line = 60  # Approximate
        estimated_lines = max(num_lines, len(content) // avg_chars_per_line + 1)
        msg_text.configure(height=min(estimated_lines, 20))  # Max 20 lines visible

        # Scroll to bottom
        self.chat_container.update_idletasks()
        self.chat_scroll.canvas.yview_moveto(1.0)

    def _add_loading_message(self):
        """Add a loading indicator."""
        self.loading_frame = ttk.Frame(self.chat_container)
        self.loading_frame.pack(fill="x", pady=5)

        inner = ttk.Frame(self.loading_frame)
        inner.pack(anchor="w")

        ttk.Label(
            inner,
            text="AI Assistant",
            font=("Segoe UI", 9, "bold"),
            foreground="#64748b",
        ).pack(anchor="w")

        self.loading_label = ttk.Label(
            inner,
            text="Thinking...",
            font=("Segoe UI", 10),
            foreground="#64748b",
        )
        self.loading_label.pack(anchor="w", pady=5)

        # Scroll to bottom
        self.chat_container.update_idletasks()
        self.chat_scroll.canvas.yview_moveto(1.0)

    def _remove_loading_message(self):
        """Remove the loading indicator."""
        if hasattr(self, "loading_frame"):
            self.loading_frame.destroy()

    def _on_enter(self, event):
        """Handle Enter key press."""
        if not event.state & 0x1:  # Shift not pressed
            self._send_message()
            return "break"  # Prevent newline

    def _send_message(self):
        """Send the user's message."""
        if self.is_processing:
            return

        # Get message text
        message = self.input_text.get("1.0", "end-1c").strip()
        if not message:
            return

        # Clear input
        self.input_text.delete("1.0", "end")

        # Add user message to chat
        self._add_message("user", message)

        # Process message
        self._process_message(message)

    def _process_message(self, message: str):
        """
        Process the user's message and get AI response.

        Args:
            message: User's message
        """
        self.is_processing = True
        self.send_btn.configure(state="disabled")

        # Show loading
        self._add_loading_message()

        # Update portfolio context
        portfolio_summary = self.main_window.get_portfolio_summary()
        self.main_window.ai_service.set_portfolio_context(portfolio_summary)

        def get_response():
            try:
                response = self.main_window.ai_service.chat(message)
                self.after(0, lambda: self._handle_response(response))

            except Exception as e:
                logger.error(f"AI response failed: {e}")
                self.after(0, lambda: self._handle_response(
                    f"I apologize, but I encountered an error: {str(e)}. Please try again."
                ))

        thread = threading.Thread(target=get_response, daemon=True)
        thread.start()

    def _handle_response(self, response: str):
        """Handle AI response."""
        self._remove_loading_message()
        self._add_message("assistant", response)

        self.is_processing = False
        self.send_btn.configure(state="normal")

    def _clear_chat(self):
        """Clear the chat history."""
        # Clear display
        for widget in self.chat_container.winfo_children():
            widget.destroy()

        # Clear AI context
        self.main_window.ai_service.clear_context()

        # Add welcome message back
        self._add_welcome_message()

    def _analyze_portfolio(self):
        """Request portfolio analysis."""
        if not self.main_window.portfolio.holdings:
            self._add_message("user", "Analyze my portfolio")
            self._add_message(
                "assistant",
                "I don't see any holdings in your portfolio yet. "
                "Add some investments in the Portfolio tab, and I'll be happy to provide analysis!"
            )
            return

        self._quick_question(
            "Please analyze my current portfolio and provide educational insights "
            "about my diversification, sector allocation, and any areas I might want "
            "to learn more about."
        )

    def _quick_question(self, question: str):
        """Send a quick pre-defined question."""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", question)
        self._send_message()


class TermDefinitionPopup(tk.Toplevel):
    """
    Popup window for displaying investing term definitions.
    """

    def __init__(self, parent, term: str, definition: str):
        """
        Initialize definition popup.

        Args:
            parent: Parent window
            term: The term being defined
            definition: The definition text
        """
        super().__init__(parent)

        self.title(f"What is {term}?")
        self.geometry("400x200")
        self.transient(parent)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=term,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        ttk.Separator(frame).pack(fill="x", pady=10)

        ttk.Label(
            frame,
            text=definition,
            wraplength=350,
            justify="left",
        ).pack(anchor="w", fill="both", expand=True)

        ttk.Button(
            frame,
            text="Close",
            command=self.destroy,
        ).pack(pady=(10, 0))
