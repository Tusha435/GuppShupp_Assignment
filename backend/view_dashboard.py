#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard
Run this script to view live user activity
"""

import time
import os
from monitoring import monitor
from datetime import datetime


def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print dashboard header."""
    print("\n" + "="*80)
    print(" "*25 + "📊 USER MONITORING DASHBOARD")
    print("="*80)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


def print_user_stats():
    """Print statistics for all users."""
    stats = monitor.get_all_users_stats()

    if not stats:
        print("📭 No user activity yet. Start chatting to see data!")
        return

    print(f"👥 Total Users: {len(stats)}\n")

    for user_stat in stats:
        print("─" * 80)
        print(f"\n📊 User: {user_stat['user_id']}")
        print(f"   💬 Messages Sent: {user_stat['total_messages']}")
        print(f"   🤖 AI Responses: {user_stat['total_responses']}")
        print(f"   📏 Avg Message Length: {user_stat['avg_message_length']:.0f} characters")
        print(f"   ⏱️  Avg Response Time: {user_stat['avg_response_time']:.0f}ms")
        print(f"   🎭 Personalities Used: {', '.join(user_stat['personalities_used']) or 'None'}")
        print(f"   🤖 AI Providers: {', '.join(user_stat['providers_used']) or 'None'}")
        print(f"   🕐 Last Activity: {user_stat['last_activity'] or 'Never'}")

    print("\n" + "─" * 80 + "\n")


def print_recent_activity(limit=5):
    """Print recent activity."""
    activity = monitor.get_recent_activity(limit)

    if not activity:
        print("📭 No recent activity")
        return

    print(f"🔄 Recent Activity (Last {limit} events):\n")

    for i, entry in enumerate(activity, 1):
        timestamp = entry.get('timestamp', 'Unknown')
        event_type = entry.get('event_type', 'unknown')
        user_id = entry.get('user_id', 'unknown')

        if event_type == 'user_message':
            message = entry.get('message', '')[:50]
            print(f"{i}. [{timestamp}] 👤 {user_id}: {message}...")

        elif event_type == 'ai_response':
            personality = entry.get('personality', 'unknown')
            provider = entry.get('provider', 'unknown')
            response_time = entry.get('response_time_ms', 0)
            print(f"{i}. [{timestamp}] 🤖 {personality}/{provider} → {user_id} ({response_time:.0f}ms)")

        elif event_type == 'memory_extraction':
            prefs = entry.get('preferences_count', 0)
            facts = entry.get('facts_count', 0)
            emotions = entry.get('emotional_patterns_count', 0)
            print(f"{i}. [{timestamp}] 🧠 Memory extracted for {user_id}: {prefs} prefs, {facts} facts, {emotions} emotions")

        elif event_type == 'error':
            error = entry.get('error', 'Unknown error')
            print(f"{i}. [{timestamp}] ❌ Error for {user_id}: {error[:50]}...")

    print()


def print_menu():
    """Print menu options."""
    print("\n" + "─" * 80)
    print("Options:")
    print("  [R] Refresh  [Q] Quit  [E] Export conversation  [S] Search  [A] Auto-refresh")
    print("─" * 80)


def export_user_conversation():
    """Export a user's conversation."""
    user_id = input("\nEnter user ID to export: ").strip()
    if user_id:
        try:
            file_path = monitor.export_user_conversation(user_id)
            print(f"✅ Exported to: {file_path}")
        except Exception as e:
            print(f"❌ Error: {e}")
    input("\nPress Enter to continue...")


def search_conversations():
    """Search through conversations."""
    query = input("\nEnter search term: ").strip()
    if query:
        results = monitor.search_conversations(query)
        print(f"\n🔍 Found {len(results)} results:\n")

        for i, entry in enumerate(results[:10], 1):  # Limit to 10
            timestamp = entry.get('timestamp', 'Unknown')
            user_id = entry.get('user_id', 'unknown')
            text = entry.get('message', entry.get('response', ''))[:100]
            print(f"{i}. [{timestamp}] {user_id}: {text}...")

        if len(results) > 10:
            print(f"\n... and {len(results) - 10} more results")

    input("\nPress Enter to continue...")


def auto_refresh_mode():
    """Auto-refresh dashboard every few seconds."""
    print("\n🔄 Auto-refresh mode (Press Ctrl+C to stop)\n")

    try:
        while True:
            clear_screen()
            print_header()
            print_user_stats()
            print_recent_activity(10)
            print("\n⏱️  Refreshing in 5 seconds... (Ctrl+C to stop)")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n⏸️  Auto-refresh stopped")
        input("Press Enter to return to menu...")


def main():
    """Main dashboard loop."""
    while True:
        clear_screen()
        print_header()
        print_user_stats()
        print_recent_activity(5)
        print_menu()

        choice = input("\nYour choice: ").strip().upper()

        if choice == 'Q':
            print("\n👋 Goodbye!\n")
            break
        elif choice == 'R':
            continue  # Refresh
        elif choice == 'E':
            export_user_conversation()
        elif choice == 'S':
            search_conversations()
        elif choice == 'A':
            auto_refresh_mode()
        else:
            print("❌ Invalid choice")
            time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed\n")
