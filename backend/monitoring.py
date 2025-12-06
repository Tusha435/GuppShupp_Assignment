"""
User Input Monitoring Module
Tracks and logs all user interactions without LangChain dependencies
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import csv


class UserMonitor:
    """
    Monitor and log user inputs, responses, and interactions.
    Multiple storage options: file, console, or custom handlers.
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Set up logging
        self.setup_logging()

        # Initialize storage files
        self.setup_storage()

    def setup_logging(self):
        """Configure Python logging for console output."""
        # Create file handler with UTF-8 encoding
        file_handler = logging.FileHandler(self.log_dir / 'app.log', encoding='utf-8')

        # Create console handler with UTF-8 encoding
        import sys
        console_handler = logging.StreamHandler(sys.stdout)

        # Set format for both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Configure logger
        self.logger = logging.getLogger('UserMonitor')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def setup_storage(self):
        """Initialize JSON and CSV storage files."""
        # JSON file for detailed logs
        self.json_log = self.log_dir / 'user_interactions.jsonl'

        # CSV file for analytics
        self.csv_log = self.log_dir / 'user_analytics.csv'
        if not self.csv_log.exists():
            with open(self.csv_log, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'user_id', 'message_length',
                    'personality', 'provider', 'response_time_ms'
                ])

    # ==================== LOGGING METHODS ====================

    def log_user_message(self, user_id: str, message: str, metadata: Dict = None):
        """
        Log incoming user message.

        Args:
            user_id: User identifier
            message: User's message text
            metadata: Additional context (personality, provider, etc.)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'user_message',
            'user_id': user_id,
            'message': message,
            'message_length': len(message),
            'metadata': metadata or {}
        }

        # Log to console
        self.logger.info(f"USER [{user_id}]: {message[:100]}...")

        # Save to JSON
        self._append_json(log_entry)

        return log_entry

    def log_ai_response(
        self,
        user_id: str,
        response: str,
        personality: str,
        provider: str,
        response_time_ms: float,
        metadata: Dict = None
    ):
        """
        Log AI response.

        Args:
            user_id: User identifier
            response: AI generated response
            personality: Personality type used
            provider: AI provider (openai/anthropic)
            response_time_ms: Time taken to generate response
            metadata: Additional context
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'ai_response',
            'user_id': user_id,
            'response': response,
            'response_length': len(response),
            'personality': personality,
            'provider': provider,
            'response_time_ms': response_time_ms,
            'metadata': metadata or {}
        }

        # Log to console
        self.logger.info(
            f"AI [{personality}/{provider}] → [{user_id}]: "
            f"{response[:100]}... ({response_time_ms:.0f}ms)"
        )

        # Save to JSON
        self._append_json(log_entry)

        # Save to CSV for analytics
        self._append_csv([
            log_entry['timestamp'],
            user_id,
            log_entry['response_length'],
            personality,
            provider,
            response_time_ms
        ])

        return log_entry

    def log_memory_extraction(
        self,
        user_id: str,
        memories: Dict[str, Any],
        extraction_time_ms: float
    ):
        """
        Log memory extraction events.

        Args:
            user_id: User identifier
            memories: Extracted memory insights
            extraction_time_ms: Time taken for extraction
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'memory_extraction',
            'user_id': user_id,
            'memories': memories,
            'extraction_time_ms': extraction_time_ms,
            'preferences_count': len(memories.get('preferences', [])),
            'facts_count': len(memories.get('facts', [])),
            'emotional_patterns_count': len(
                memories.get('emotional_patterns', {}).get('emotional_patterns', [])
            )
        }

        self.logger.info(
            f"MEMORY [{user_id}]: Extracted {log_entry['preferences_count']} prefs, "
            f"{log_entry['facts_count']} facts, "
            f"{log_entry['emotional_patterns_count']} emotions "
            f"({extraction_time_ms:.0f}ms)"
        )

        self._append_json(log_entry)

        return log_entry

    def log_error(self, user_id: str, error: str, context: Dict = None):
        """Log errors that occur during processing."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'error',
            'user_id': user_id,
            'error': error,
            'context': context or {}
        }

        self.logger.error(f"ERROR [{user_id}]: {error}")
        self._append_json(log_entry)

        return log_entry

    # ==================== ANALYTICS METHODS ====================

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific user.

        Returns:
            Dictionary with user statistics
        """
        stats = {
            'total_messages': 0,
            'total_responses': 0,
            'personalities_used': [],
            'providers_used': [],
            'avg_message_length': 0,
            'avg_response_time': 0,
            'last_activity': None
        }

        personalities_set = set()
        providers_set = set()
        message_lengths = []
        response_times = []

        # Read from JSONL file
        if self.json_log.exists():
            with open(self.json_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry['user_id'] != user_id:
                            continue

                        if entry['event_type'] == 'user_message':
                            stats['total_messages'] += 1
                            message_lengths.append(entry['message_length'])
                            stats['last_activity'] = entry['timestamp']

                        elif entry['event_type'] == 'ai_response':
                            stats['total_responses'] += 1
                            personalities_set.add(entry['personality'])
                            providers_set.add(entry['provider'])
                            response_times.append(entry['response_time_ms'])

                    except json.JSONDecodeError:
                        continue

        # Calculate averages
        if message_lengths:
            stats['avg_message_length'] = sum(message_lengths) / len(message_lengths)
        if response_times:
            stats['avg_response_time'] = sum(response_times) / len(response_times)

        # Convert sets to lists for JSON serialization
        stats['personalities_used'] = list(personalities_set)
        stats['providers_used'] = list(providers_set)

        return stats

    def get_all_users_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all users."""
        users = {}

        if self.json_log.exists():
            with open(self.json_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        user_id = entry['user_id']
                        if user_id not in users:
                            users[user_id] = self.get_user_stats(user_id)
                    except json.JSONDecodeError:
                        continue

        return [{'user_id': uid, **stats} for uid, stats in users.items()]

    def get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent activity across all users.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent log entries
        """
        entries = []

        if self.json_log.exists():
            with open(self.json_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Sort by timestamp (most recent first) and limit
        entries.sort(key=lambda x: x['timestamp'], reverse=True)
        return entries[:limit]

    def search_conversations(self, query: str, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Search through logged conversations.

        Args:
            query: Search term
            user_id: Optional user filter

        Returns:
            List of matching entries
        """
        results = []
        query_lower = query.lower()

        if self.json_log.exists():
            with open(self.json_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)

                        # Filter by user if specified
                        if user_id and entry['user_id'] != user_id:
                            continue

                        # Search in message or response
                        text = entry.get('message', '') + entry.get('response', '')
                        if query_lower in text.lower():
                            results.append(entry)

                    except json.JSONDecodeError:
                        continue

        return results

    # ==================== REAL-TIME MONITORING ====================

    def print_live_stats(self):
        """Print live statistics to console."""
        stats = self.get_all_users_stats()

        print("\n" + "="*60)
        print("LIVE USER MONITORING DASHBOARD")
        print("="*60)

        print(f"\nTotal Users: {len(stats)}")

        for user_stat in stats:
            print(f"\n[USER] {user_stat['user_id']}")
            print(f"   Messages: {user_stat['total_messages']}")
            print(f"   Responses: {user_stat['total_responses']}")
            print(f"   Avg Message Length: {user_stat['avg_message_length']:.0f} chars")
            print(f"   Avg Response Time: {user_stat['avg_response_time']:.0f}ms")
            print(f"   Personalities: {', '.join(user_stat['personalities_used'])}")
            print(f"   Providers: {', '.join(user_stat['providers_used'])}")
            print(f"   Last Active: {user_stat['last_activity']}")

        print("\n" + "="*60 + "\n")

    # ==================== PRIVATE HELPER METHODS ====================

    def _append_json(self, entry: Dict):
        """Append entry to JSONL file."""
        with open(self.json_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    def _append_csv(self, row: List):
        """Append row to CSV file."""
        with open(self.csv_log, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    # ==================== EXPORT METHODS ====================

    def export_user_conversation(self, user_id: str, output_file: str = None):
        """
        Export a user's full conversation to a readable format.

        Args:
            user_id: User to export
            output_file: Output filename (optional)
        """
        if not output_file:
            output_file = self.log_dir / f"conversation_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(f"Conversation Log for User: {user_id}\n")
            out.write(f"Exported: {datetime.now().isoformat()}\n")
            out.write("="*80 + "\n\n")

            if self.json_log.exists():
                with open(self.json_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            if entry['user_id'] != user_id:
                                continue

                            if entry['event_type'] == 'user_message':
                                out.write(f"\n[{entry['timestamp']}] USER:\n")
                                out.write(f"{entry['message']}\n")

                            elif entry['event_type'] == 'ai_response':
                                out.write(f"\n[{entry['timestamp']}] AI ({entry['personality']}/{entry['provider']}):\n")
                                out.write(f"{entry['response']}\n")
                                out.write(f"(Response time: {entry['response_time_ms']:.0f}ms)\n")

                        except json.JSONDecodeError:
                            continue

        self.logger.info(f"Exported conversation to {output_file}")
        return str(output_file)


# ==================== GLOBAL MONITOR INSTANCE ====================

# Create a global monitor instance
monitor = UserMonitor()


# ==================== CONVENIENCE FUNCTIONS ====================

def log_message(user_id: str, message: str, **metadata):
    """Convenience function to log user message."""
    return monitor.log_user_message(user_id, message, metadata)


def log_response(user_id: str, response: str, personality: str,
                provider: str, response_time_ms: float, **metadata):
    """Convenience function to log AI response."""
    return monitor.log_ai_response(
        user_id, response, personality, provider, response_time_ms, metadata
    )


def log_memory(user_id: str, memories: Dict, extraction_time_ms: float):
    """Convenience function to log memory extraction."""
    return monitor.log_memory_extraction(user_id, memories, extraction_time_ms)


def get_stats(user_id: str = None):
    """Get user statistics."""
    if user_id:
        return monitor.get_user_stats(user_id)
    return monitor.get_all_users_stats()


def view_dashboard():
    """Print live monitoring dashboard."""
    monitor.print_live_stats()
