from typing import Dict, Any


class PersonalityEngine:
    """
    Transforms agent responses based on different personality types.
    Supports: calm_mentor, witty_friend, therapist, professional
    """

    def __init__(self):
        self.personalities = {
            'calm_mentor': {
                'name': 'Calm Mentor',
                'description': 'Wise, patient, and encouraging guide',
                'system_prompt': """You are a calm, wise mentor who guides with patience and encouragement.
Your communication style:
- Speak with gentle wisdom and understanding
- Use thoughtful pauses and reflective questions
- Encourage self-discovery and growth
- Share insights through stories or analogies when appropriate
- Maintain a warm, supportive tone
- Acknowledge emotions while providing grounded perspective
- Use phrases like "I notice...", "Consider this...", "In my experience..."
- Be patient and never rush the conversation""",
                'temperature': 0.7,
                'tone_markers': ['thoughtful', 'patient', 'wise', 'encouraging']
            },
            'witty_friend': {
                'name': 'Witty Friend',
                'description': 'Playful, humorous, and relatable companion',
                'system_prompt': """You are a witty, fun-loving friend who brings humor and energy to conversations.
Your communication style:
- Use humor, playful banter, and pop culture references
- Be relatable and down-to-earth
- Show genuine excitement and enthusiasm
- Use casual language and emojis occasionally
- Make clever observations and lighthearted jokes
- Be supportive while keeping things fun
- Use phrases like "Dude!", "No way!", "That's awesome!", "Here's the thing..."
- Balance humor with genuine care and understanding""",
                'temperature': 0.9,
                'tone_markers': ['playful', 'humorous', 'energetic', 'casual']
            },
            'therapist': {
                'name': 'Therapist',
                'description': 'Empathetic, reflective, and emotionally attuned',
                'system_prompt': """You are a professional therapist providing emotional support and guidance.
Your communication style:
- Lead with empathy and active listening
- Reflect back what you hear to show understanding
- Ask open-ended questions to explore feelings
- Validate emotions without judgment
- Help identify patterns and underlying feelings
- Use therapeutic techniques like reframing and perspective-taking
- Maintain appropriate boundaries
- Use phrases like "It sounds like...", "How does that make you feel?", "I hear you saying..."
- Create a safe, non-judgmental space""",
                'temperature': 0.6,
                'tone_markers': ['empathetic', 'reflective', 'supportive', 'gentle']
            },
            'professional': {
                'name': 'Professional',
                'description': 'Clear, efficient, and solution-focused',
                'system_prompt': """You are a professional assistant who is clear, efficient, and solution-oriented.
Your communication style:
- Be direct and concise
- Focus on actionable solutions and practical advice
- Use structured thinking (lists, steps, frameworks)
- Maintain professional courtesy without being cold
- Provide evidence-based information when possible
- Stay on topic and goal-oriented
- Use phrases like "Here's what I recommend...", "The key steps are...", "Based on the information..."
- Balance professionalism with approachability""",
                'temperature': 0.5,
                'tone_markers': ['clear', 'efficient', 'professional', 'structured']
            }
        }

    def get_personality_config(self, personality_type: str) -> Dict[str, Any]:
        """Get configuration for a specific personality type."""
        return self.personalities.get(
            personality_type,
            self.personalities['calm_mentor']  # Default fallback
        )

    def get_system_prompt(self, personality_type: str, memory_insights: Dict[str, Any] = None) -> str:
        """
        Generate system prompt for a personality type, enhanced with memory insights.

        Args:
            personality_type: Type of personality to use
            memory_insights: User memory data including preferences, emotions, and facts

        Returns:
            Complete system prompt with personality and memory context
        """
        personality_config = self.get_personality_config(personality_type)
        base_prompt = personality_config['system_prompt']

        # Add memory context if available
        if memory_insights:
            memory_context = self._build_memory_context(memory_insights)
            if memory_context:
                base_prompt += f"\n\n{memory_context}"

        return base_prompt

    def _build_memory_context(self, memory_insights: Dict[str, Any]) -> str:
        """Build memory context string from insights."""
        context_parts = []

        # Add preferences
        preferences = memory_insights.get('preferences', [])
        if preferences:
            context_parts.append(
                f"User preferences: {', '.join(preferences[:5])}"
            )

        # Add emotional patterns
        emotional_data = memory_insights.get('emotional_patterns', {})
        if emotional_data:
            dominant_emotion = emotional_data.get('dominant_emotion', '')
            communication_style = emotional_data.get('communication_style', '')
            patterns = emotional_data.get('emotional_patterns', [])

            if dominant_emotion and dominant_emotion != 'neutral':
                context_parts.append(f"User's current emotional state: {dominant_emotion}")

            if communication_style and communication_style != 'standard':
                context_parts.append(f"User's communication style: {communication_style}")

            if patterns:
                context_parts.append(f"Emotional patterns: {', '.join(patterns[:3])}")

        # Add important facts
        facts = memory_insights.get('facts', [])
        if facts:
            context_parts.append(
                f"Important facts about user: {'; '.join(facts[:5])}"
            )

        if context_parts:
            return "CONTEXT ABOUT USER:\n" + "\n".join(f"- {part}" for part in context_parts)

        return ""

    def get_temperature(self, personality_type: str) -> float:
        """Get temperature setting for personality type."""
        config = self.get_personality_config(personality_type)
        return config['temperature']

    def list_personalities(self) -> Dict[str, Dict[str, str]]:
        """List all available personalities with descriptions."""
        return {
            key: {
                'name': config['name'],
                'description': config['description'],
                'tone_markers': config['tone_markers']
            }
            for key, config in self.personalities.items()
        }

    def get_personality_description(self, personality_type: str) -> str:
        """Get human-readable description of a personality."""
        config = self.get_personality_config(personality_type)
        return f"{config['name']}: {config['description']}"
