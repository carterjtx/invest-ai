"""
AI service for Invest AI Assistant.

Integrates with Claude API for conversational investment assistance.
Provides educational information and portfolio insights.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

logger = logging.getLogger(__name__)


# System prompt for the AI assistant
SYSTEM_PROMPT = """You are an AI investment assistant designed to help beginners understand investing concepts and manage their portfolios. You are educational, helpful, and always remind users that you are not providing financial advice.

Your key responsibilities:
1. Explain investing concepts in simple, beginner-friendly terms
2. Help users understand their portfolio composition and diversification
3. Provide educational insights about stocks, ETFs, cryptocurrencies, and other assets
4. Answer questions about investing terminology and strategies
5. Analyze portfolio allocation and suggest areas for consideration (not recommendations)

Important guidelines:
- ALWAYS include a disclaimer that this is educational content, not financial advice
- NEVER recommend specific stocks or investments to buy or sell
- Focus on education and helping users understand concepts
- When discussing portfolio analysis, present information objectively
- Encourage users to consult with qualified financial advisors for personalized advice
- Be clear about the risks associated with different types of investments
- Use simple language and explain jargon when necessary

If asked about specific investment actions, redirect to general education about the topic and remind users to do their own research and consult professionals."""


@dataclass
class Message:
    """A chat message."""

    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API."""
        return {"role": self.role, "content": self.content}


@dataclass
class ChatSession:
    """A conversation session with context."""

    messages: List[Message] = field(default_factory=list)
    portfolio_context: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_user_message(self, content: str) -> Message:
        """Add a user message to the session."""
        message = Message(role="user", content=content)
        self.messages.append(message)
        return message

    def add_assistant_message(self, content: str) -> Message:
        """Add an assistant message to the session."""
        message = Message(role="assistant", content=content)
        self.messages.append(message)
        return message

    def get_api_messages(self) -> List[Dict[str, str]]:
        """Get messages formatted for API call."""
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()


class AIService:
    """
    Service for AI-powered investment assistance using Claude.

    Provides conversational interface for investment questions
    and portfolio analysis.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the AI service.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self.session = ChatSession()

        if ANTHROPIC_AVAILABLE and api_key and api_key != "your_anthropic_key_here":
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

    def is_available(self) -> bool:
        """Check if the AI service is available and configured."""
        return (
            ANTHROPIC_AVAILABLE
            and self.client is not None
            and self.api_key
            and self.api_key != "your_anthropic_key_here"
        )

    def set_portfolio_context(self, portfolio_summary: str) -> None:
        """
        Set the current portfolio context for more relevant responses.

        Args:
            portfolio_summary: Summary of current portfolio holdings
        """
        self.session.portfolio_context = portfolio_summary

    def clear_context(self) -> None:
        """Clear the conversation context."""
        self.session.clear()
        self.session.portfolio_context = None

    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response from the AI assistant.

        Args:
            user_message: The user's message/question

        Returns:
            The assistant's response
        """
        if not self.is_available():
            return self._get_fallback_response(user_message)

        # Add user message to session
        self.session.add_user_message(user_message)

        try:
            # Build system prompt with portfolio context if available
            system = SYSTEM_PROMPT
            if self.session.portfolio_context:
                system += f"\n\nCurrent portfolio context:\n{self.session.portfolio_context}"

            # Make API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=self.session.get_api_messages(),
            )

            # Extract response text
            assistant_message = response.content[0].text

            # Add assistant message to session
            self.session.add_assistant_message(assistant_message)

            return assistant_message

        except anthropic.APIError as e:
            logger.error(f"API error: {e}")
            self.session.messages.pop()  # Remove failed user message
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."

        except Exception as e:
            logger.error(f"Chat error: {e}")
            self.session.messages.pop()  # Remove failed user message
            return "I apologize, but something went wrong. Please try again."

    def get_portfolio_analysis(self, portfolio_data: Dict[str, Any]) -> str:
        """
        Get AI analysis of a portfolio.

        Args:
            portfolio_data: Dictionary containing portfolio information

        Returns:
            Analysis text from the AI
        """
        # Format portfolio data as a message
        holdings_summary = self._format_portfolio_for_analysis(portfolio_data)

        prompt = f"""Please analyze this investment portfolio and provide educational insights:

{holdings_summary}

Please provide:
1. A brief overview of the portfolio composition
2. Observations about diversification (sectors, asset types)
3. Educational points about the types of investments held
4. General areas the investor might want to learn more about

Remember: This is for educational purposes only, not financial advice."""

        return self.chat(prompt)

    def explain_term(self, term: str) -> str:
        """
        Get a beginner-friendly explanation of an investing term.

        Args:
            term: The investing term to explain

        Returns:
            Educational explanation
        """
        prompt = f"""Please explain the investing term "{term}" in simple, beginner-friendly language.

Include:
- A clear definition
- A simple example or analogy
- Why it matters to investors
- Any related terms they should know

Keep the explanation accessible for someone new to investing."""

        return self.chat(prompt)

    def get_diversification_advice(self, allocation_data: Dict[str, float]) -> str:
        """
        Get educational advice about portfolio diversification.

        Args:
            allocation_data: Dictionary mapping sectors/types to percentages

        Returns:
            Educational advice about diversification
        """
        allocation_str = "\n".join(
            f"- {sector}: {pct:.1f}%" for sector, pct in allocation_data.items()
        )

        prompt = f"""Here is a portfolio's current allocation:

{allocation_str}

Please provide educational information about:
1. What this allocation looks like (concentrated vs diversified)
2. General principles of diversification
3. How different sectors typically behave
4. Questions the investor might want to consider

This is educational information only, not a recommendation to change anything."""

        return self.chat(prompt)

    def _format_portfolio_for_analysis(self, portfolio_data: Dict[str, Any]) -> str:
        """Format portfolio data as a readable summary."""
        lines = []

        # Holdings
        holdings = portfolio_data.get("holdings", {})
        if holdings:
            lines.append("Holdings:")
            for symbol, holding in holdings.items():
                value = holding.get("market_value", holding.get("cost_basis", 0))
                lines.append(
                    f"  - {symbol} ({holding.get('name', 'Unknown')}): "
                    f"${value:,.2f} ({holding.get('sector', 'Other')})"
                )

        # Summary stats
        total_value = portfolio_data.get("total_value", 0)
        total_cost = portfolio_data.get("total_cost", 0)
        if total_value:
            gain = total_value - total_cost
            gain_pct = (gain / total_cost * 100) if total_cost else 0
            lines.append(f"\nTotal Value: ${total_value:,.2f}")
            lines.append(f"Total Cost: ${total_cost:,.2f}")
            lines.append(f"Gain/Loss: ${gain:,.2f} ({gain_pct:+.1f}%)")

        # Sector allocation
        sectors = portfolio_data.get("sector_allocation", {})
        if sectors:
            lines.append("\nSector Allocation:")
            for sector, pct in sectors.items():
                lines.append(f"  - {sector}: {pct:.1f}%")

        return "\n".join(lines)

    def _get_fallback_response(self, user_message: str) -> str:
        """
        Provide a fallback response when AI is not available.

        Args:
            user_message: The user's message

        Returns:
            A helpful fallback response
        """
        lower_msg = user_message.lower()

        # Basic keyword matching for common questions
        if any(word in lower_msg for word in ["diversif", "spread", "allocation"]):
            return """Diversification is a key investing concept that means spreading your
investments across different assets, sectors, and sometimes geographies. The idea is to
reduce risk - if one investment performs poorly, others might perform well and balance
things out.

A well-diversified portfolio typically includes:
- Different asset classes (stocks, bonds, etc.)
- Multiple sectors (technology, healthcare, etc.)
- Various company sizes (large-cap, small-cap)

Note: AI assistant is not configured. For personalized analysis, please set up your
Anthropic API key in the configuration.

DISCLAIMER: This is general educational information, not financial advice."""

        elif any(word in lower_msg for word in ["dividend", "yield", "income"]):
            return """Dividends are payments made by companies to their shareholders,
usually from profits. They provide a way to earn regular income from your investments.

Key dividend concepts:
- Dividend Yield: Annual dividend divided by stock price (e.g., 3% yield)
- Ex-Dividend Date: You must own the stock before this date to receive the dividend
- Dividend Growth: Some companies increase dividends yearly

Not all companies pay dividends - growth companies often reinvest profits instead.

Note: AI assistant is not configured. For personalized analysis, please set up your
Anthropic API key.

DISCLAIMER: This is educational information, not financial advice."""

        elif any(word in lower_msg for word in ["risk", "volatile", "safe"]):
            return """Risk in investing generally refers to the possibility of losing money.
Different investments carry different levels of risk:

- Stocks: Higher risk, higher potential return
- Bonds: Generally lower risk, lower potential return
- Crypto: Very high risk and volatility
- Cash: Lowest risk, but may lose value to inflation

Risk tolerance varies by person - factors include age, financial goals, and how you'd
feel about short-term losses.

Note: AI assistant is not configured. For personalized analysis, please set up your
Anthropic API key.

DISCLAIMER: This is educational information, not financial advice."""

        else:
            return """I'm the AI investment assistant! I can help you understand:

- Portfolio concepts (diversification, allocation, etc.)
- Investment terms and definitions
- Different types of assets (stocks, ETFs, crypto)
- Basic risk assessment concepts

Note: The full AI assistant is not currently configured. To enable intelligent
responses, please set up your Anthropic API key in the configuration.

What would you like to learn about?

DISCLAIMER: All information provided is for educational purposes only and should not
be considered financial advice. Please consult a qualified financial advisor for
personalized investment guidance."""

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
            }
            for msg in self.session.messages
        ]


class MockAIService(AIService):
    """
    Mock AI service for testing and demo purposes.

    Provides pre-defined responses without making API calls.
    """

    def __init__(self):
        """Initialize mock service (no API key needed)."""
        super().__init__(api_key="mock")
        self.client = None  # Ensure we use fallback

    def is_available(self) -> bool:
        """Mock service uses fallback responses."""
        return False  # Force fallback responses

    def chat(self, user_message: str) -> str:
        """Use fallback responses."""
        # Add to session for history tracking
        self.session.add_user_message(user_message)
        response = self._get_fallback_response(user_message)
        self.session.add_assistant_message(response)
        return response
