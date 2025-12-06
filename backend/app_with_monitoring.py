"""
Flask API with Built-in User Monitoring
Alternative to app.py with comprehensive logging
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from memory_extractor import MemoryExtractor
from personality_engine import PersonalityEngine
from chat_handler import ChatHandler
from monitoring import monitor, log_message, log_response, log_memory, get_stats
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize components
memory_extractor = MemoryExtractor()
personality_engine = PersonalityEngine()
chat_handler = ChatHandler(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
)

# In-memory storage for demo (use a database in production)
chat_histories = {}


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()

    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        message = data.get('message', '')
        personality = data.get('personality', 'calm_mentor')
        ai_provider = data.get('ai_provider', 'openai')

        # ============ LOG USER MESSAGE ============
        log_message(user_id, message, personality=personality, provider=ai_provider)

        # Initialize user history if not exists
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        # Add user message to history
        chat_histories[user_id].append({
            'role': 'user',
            'content': message
        })

        # Extract memory insights from chat history
        memory_start = time.time()
        memory_insights = memory_extractor.extract_memories(chat_histories[user_id])
        memory_time = (time.time() - memory_start) * 1000  # ms

        # ============ LOG MEMORY EXTRACTION ============
        if memory_insights:
            log_memory(user_id, memory_insights, memory_time)

        # Generate response based on personality and provider
        response_start = time.time()
        response = chat_handler.generate_response(
            message=message,
            chat_history=chat_histories[user_id],
            personality=personality,
            memory_insights=memory_insights,
            provider=ai_provider
        )
        response_time = (time.time() - response_start) * 1000  # ms

        # Add assistant response to history
        chat_histories[user_id].append({
            'role': 'assistant',
            'content': response
        })

        # ============ LOG AI RESPONSE ============
        log_response(
            user_id=user_id,
            response=response,
            personality=personality,
            provider=ai_provider,
            response_time_ms=response_time,
            total_messages=len(chat_histories[user_id])
        )

        total_time = (time.time() - start_time) * 1000  # ms

        return jsonify({
            'response': response,
            'memory_insights': memory_insights,
            'personality': personality,
            'provider': ai_provider,
            'timing': {
                'memory_extraction_ms': memory_time,
                'response_generation_ms': response_time,
                'total_ms': total_time
            }
        }), 200

    except Exception as e:
        monitor.log_error(
            user_id=data.get('user_id', 'unknown'),
            error=str(e),
            context={'endpoint': '/api/chat', 'data': data}
        )
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/<user_id>', methods=['GET'])
def get_memory(user_id):
    try:
        if user_id not in chat_histories:
            return jsonify({'memories': {}}), 200

        memories = memory_extractor.extract_memories(chat_histories[user_id])
        return jsonify({'memories': memories}), 200

    except Exception as e:
        monitor.log_error(user_id, str(e), {'endpoint': '/api/memory'})
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-personalities', methods=['POST'])
def compare_personalities():
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        ai_provider = data.get('ai_provider', 'openai')

        # Log comparison request
        log_message(user_id, message, event='comparison', provider=ai_provider)

        chat_history = chat_histories.get(user_id, [])
        memory_insights = memory_extractor.extract_memories(chat_history) if chat_history else {}

        # Get available personalities
        personalities = ['calm_mentor', 'witty_friend', 'therapist', 'professional']

        responses = {}
        for personality in personalities:
            start_time = time.time()
            response = chat_handler.generate_response(
                message=message,
                chat_history=chat_history,
                personality=personality,
                memory_insights=memory_insights,
                provider=ai_provider
            )
            response_time = (time.time() - start_time) * 1000

            responses[personality] = response

            # Log each personality response
            log_response(
                user_id=user_id,
                response=response,
                personality=personality,
                provider=ai_provider,
                response_time_ms=response_time,
                event='comparison'
            )

        return jsonify({
            'original_message': message,
            'responses': responses,
            'memory_insights': memory_insights
        }), 200

    except Exception as e:
        monitor.log_error(user_id, str(e), {'endpoint': '/api/compare-personalities'})
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear-history/<user_id>', methods=['DELETE'])
def clear_history(user_id):
    if user_id in chat_histories:
        del chat_histories[user_id]

    # Log clearing
    monitor.logger.info(f"Cleared history for user: {user_id}")

    return jsonify({'message': 'History cleared'}), 200


# ==================== MONITORING ENDPOINTS ====================

@app.route('/api/monitor/stats', methods=['GET'])
def get_monitoring_stats():
    """Get monitoring statistics for all users."""
    user_id = request.args.get('user_id')

    try:
        stats = get_stats(user_id)
        return jsonify({'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/activity', methods=['GET'])
def get_recent_activity():
    """Get recent activity across all users."""
    limit = int(request.args.get('limit', 20))

    try:
        activity = monitor.get_recent_activity(limit)
        return jsonify({'activity': activity}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/search', methods=['GET'])
def search_conversations():
    """Search through conversations."""
    query = request.args.get('query', '')
    user_id = request.args.get('user_id')

    try:
        results = monitor.search_conversations(query, user_id)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/export/<user_id>', methods=['GET'])
def export_conversation(user_id):
    """Export a user's conversation."""
    try:
        file_path = monitor.export_user_conversation(user_id)
        return jsonify({'message': 'Exported successfully', 'file': file_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("\n" + "="*60)
    print("🎯 User Monitoring Enabled!")
    print("="*60)
    print(f"📊 Logs saved to: {monitor.log_dir}")
    print(f"📝 JSON Log: {monitor.json_log}")
    print(f"📈 CSV Log: {monitor.csv_log}")
    print(f"🖥️  Console logging: ENABLED")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
