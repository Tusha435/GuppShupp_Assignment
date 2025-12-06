from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from personality_engine import PersonalityEngine
import os


class ChatHandler:
    """
    Handles chat interactions with both OpenAI and Anthropic models.
    Integrates personality engine and memory insights.
    """

    def __init__(self, openai_api_key: str = None, anthropic_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.personality_engine = PersonalityEngine()

        # Initialize LLM instances
        self.openai_llm = None
        self.anthropic_llm = None

        if self.openai_api_key:
            try:
                self.openai_llm = ChatOpenAI(
                    model="gpt-4o",
                    api_key=self.openai_api_key,
                    temperature=0.7
                )
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")

        if self.anthropic_api_key:
            try:
                self.anthropic_llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    api_key=self.anthropic_api_key,
                    temperature=0.7
                )
            except Exception as e:
                print(f"Failed to initialize Anthropic: {e}")

    def _format_chat_history(self, chat_history: List[Dict[str, str]], limit: int = 10) -> List:
        """Convert chat history to LangChain message format."""
        messages = []

        # Get recent messages
        recent_history = chat_history[-(limit * 2):] if len(chat_history) > limit * 2 else chat_history

        for msg in recent_history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'user':
                messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                messages.append(AIMessage(content=content))

        return messages

    def generate_response(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        personality: str = 'calm_mentor',
        memory_insights: Dict[str, Any] = None,
        provider: str = 'openai'
    ) -> str:
        """
        Generate a response using specified AI provider and personality.

        Args:
            message: Current user message
            chat_history: Full chat history
            personality: Personality type to use
            memory_insights: User memory data
            provider: 'openai' or 'anthropic'

        Returns:
            Generated response string
        """
        # Select LLM based on provider
        if provider == 'anthropic' and self.anthropic_llm:
            llm = self.anthropic_llm
        elif provider == 'openai' and self.openai_llm:
            llm = self.openai_llm
        else:
            # Fallback to available provider
            llm = self.openai_llm or self.anthropic_llm

        if not llm:
            raise ValueError("No AI provider available. Please configure API keys.")

        # Get personality configuration
        system_prompt = self.personality_engine.get_system_prompt(personality, memory_insights)
        temperature = self.personality_engine.get_temperature(personality)

        # Update LLM temperature
        llm.temperature = temperature

        # Build message sequence
        messages = [SystemMessage(content=system_prompt)]

        # Add recent chat history for context
        if chat_history and len(chat_history) > 1:
            history_messages = self._format_chat_history(chat_history[:-1])  # Exclude current message
            messages.extend(history_messages)

        # Add current message
        messages.append(HumanMessage(content=message))

        # Generate response
        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def generate_response_stream(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        personality: str = 'calm_mentor',
        memory_insights: Dict[str, Any] = None,
        provider: str = 'openai'
    ):
        """
        Generate a streaming response using specified AI provider and personality.

        Args:
            message: Current user message
            chat_history: Full chat history
            personality: Personality type to use
            memory_insights: User memory data
            provider: 'openai' or 'anthropic'

        Yields:
            Response chunks as they are generated
        """
        # Select LLM based on provider
        if provider == 'anthropic' and self.anthropic_llm:
            llm = self.anthropic_llm
        elif provider == 'openai' and self.openai_llm:
            llm = self.openai_llm
        else:
            # Fallback to available provider
            llm = self.openai_llm or self.anthropic_llm

        if not llm:
            raise ValueError("No AI provider available. Please configure API keys.")

        # Get personality configuration
        system_prompt = self.personality_engine.get_system_prompt(personality, memory_insights)
        temperature = self.personality_engine.get_temperature(personality)

        # Update LLM temperature
        llm.temperature = temperature

        # Build message sequence
        messages = [SystemMessage(content=system_prompt)]

        # Add recent chat history for context
        if chat_history and len(chat_history) > 1:
            history_messages = self._format_chat_history(chat_history[:-1])  # Exclude current message
            messages.extend(history_messages)

        # Add current message
        messages.append(HumanMessage(content=message))

        # Stream response
        try:
            for chunk in llm.stream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
        except Exception as e:
            print(f"Error generating streaming response: {e}")
            yield f"I apologize, but I encountered an error: {str(e)}"

    def generate_comparison(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        memory_insights: Dict[str, Any] = None,
        provider: str = 'openai'
    ) -> Dict[str, str]:
        """
        Generate responses in all personality styles for comparison.

        Returns:
            Dictionary mapping personality type to response
        """
        personalities = self.personality_engine.list_personalities()
        responses = {}

        for personality_key in personalities.keys():
            try:
                response = self.generate_response(
                    message=message,
                    chat_history=chat_history,
                    personality=personality_key,
                    memory_insights=memory_insights,
                    provider=provider
                )
                responses[personality_key] = response
            except Exception as e:
                responses[personality_key] = f"Error: {str(e)}"

        return responses
