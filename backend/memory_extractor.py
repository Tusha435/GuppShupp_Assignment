from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
import json
import re


class MemoryExtractor:
    """
    Extracts and manages user memories from chat history.
    Identifies preferences, emotional patterns, and important facts.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

        # Prompt for extracting preferences
        self.preference_prompt = PromptTemplate(
            input_variables=["messages"],
            template="""Analyze the following chat messages and extract user preferences.
Look for:
- Favorite topics, hobbies, interests
- Communication style preferences
- Likes and dislikes
- Preferred activities or subjects
- Any explicit or implicit preferences mentioned

Chat messages:
{messages}

Return ONLY a JSON object with this structure:
{{
  "preferences": ["preference1", "preference2", ...]
}}

Response:"""
        )

        # Prompt for extracting emotional patterns
        self.emotion_prompt = PromptTemplate(
            input_variables=["messages"],
            template="""Analyze the following chat messages and identify emotional patterns.
Look for:
- Recurring emotional states (happy, anxious, frustrated, excited)
- Triggers for specific emotions
- Emotional communication style
- Stress indicators or coping mechanisms

Chat messages:
{messages}

Return ONLY a JSON object with this structure:
{{
  "emotional_patterns": ["pattern1", "pattern2", ...],
  "dominant_emotion": "emotion",
  "communication_style": "style description"
}}

Response:"""
        )

        # Prompt for extracting facts
        self.facts_prompt = PromptTemplate(
            input_variables=["messages"],
            template="""Analyze the following chat messages and extract important facts about the user.
Look for:
- Personal information (job, location, age, family)
- Goals and aspirations
- Challenges or problems they're facing
- Important life events
- Relationships and social context

Chat messages:
{messages}

Return ONLY a JSON object with this structure:
{{
  "facts": ["fact1", "fact2", ...]
}}

Response:"""
        )

        # Use modern RunnableSequence (pipe operator)
        self.preference_chain = self.preference_prompt | self.llm | StrOutputParser()
        self.emotion_chain = self.emotion_prompt | self.llm | StrOutputParser()
        self.facts_chain = self.facts_prompt | self.llm | StrOutputParser()

    def _format_messages(self, messages: List[Dict[str, str]], limit: int = 30) -> str:
        """Format messages for analysis, limiting to most recent messages."""
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        formatted = []
        for msg in recent_messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted.append(f"{role.upper()}: {content}")
        return "\n".join(formatted)

    def _safe_json_parse(self, response: str, default_key: str) -> Dict[str, Any]:
        """Safely parse JSON from LLM response."""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {default_key: []}
        except json.JSONDecodeError:
            # If parsing fails, try to extract content manually
            return {default_key: []}

    def extract_preferences(self, messages: List[Dict[str, str]]) -> List[str]:
        """Extract user preferences from chat messages."""
        if not messages:
            return []

        try:
            formatted_messages = self._format_messages(messages)
            response = self.preference_chain.invoke({"messages": formatted_messages})
            data = self._safe_json_parse(response, 'preferences')
            return data.get('preferences', [])
        except Exception as e:
            print(f"Error extracting preferences: {e}")
            return []

    def extract_emotional_patterns(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract emotional patterns from chat messages."""
        if not messages:
            return {
                'emotional_patterns': [],
                'dominant_emotion': 'neutral',
                'communication_style': 'standard'
            }

        try:
            formatted_messages = self._format_messages(messages)
            response = self.emotion_chain.invoke({"messages": formatted_messages})
            data = self._safe_json_parse(response, 'emotional_patterns')
            return {
                'emotional_patterns': data.get('emotional_patterns', []),
                'dominant_emotion': data.get('dominant_emotion', 'neutral'),
                'communication_style': data.get('communication_style', 'standard')
            }
        except Exception as e:
            print(f"Error extracting emotional patterns: {e}")
            return {
                'emotional_patterns': [],
                'dominant_emotion': 'neutral',
                'communication_style': 'standard'
            }

    def extract_facts(self, messages: List[Dict[str, str]]) -> List[str]:
        """Extract important facts from chat messages."""
        if not messages:
            return []

        try:
            formatted_messages = self._format_messages(messages)
            response = self.facts_chain.invoke({"messages": formatted_messages})
            data = self._safe_json_parse(response, 'facts')
            return data.get('facts', [])
        except Exception as e:
            print(f"Error extracting facts: {e}")
            return []

    def extract_memories(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Extract all memory components from chat messages.

        Returns:
            Dictionary containing preferences, emotional patterns, and facts
        """
        if not messages or len(messages) < 2:
            return {
                'preferences': [],
                'emotional_patterns': {
                    'emotional_patterns': [],
                    'dominant_emotion': 'neutral',
                    'communication_style': 'standard'
                },
                'facts': []
            }

        # Only extract from user messages for efficiency
        user_messages = [msg for msg in messages if msg.get('role') == 'user']

        # Extract all components
        preferences = self.extract_preferences(user_messages)
        emotional_patterns = self.extract_emotional_patterns(user_messages)
        facts = self.extract_facts(user_messages)

        return {
            'preferences': preferences,
            'emotional_patterns': emotional_patterns,
            'facts': facts
        }
