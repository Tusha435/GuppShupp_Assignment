from flask import Flask, request, jsonify
from flask_cors import CORS
from memory_extractor import MemoryExtractor
from personality_engine import PersonalityEngine
from chat_handler import ChatHandler
import os
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
    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        message = data.get('message', '')
        personality = data.get('personality', 'calm_mentor')
        ai_provider = data.get('ai_provider', 'openai')  # 'openai' or 'anthropic'

        # Initialize user history if not exists
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        # Add user message to history
        chat_histories[user_id].append({
            'role': 'user',
            'content': message
        })

        # Extract memory insights from chat history
        memory_insights = memory_extractor.extract_memories(chat_histories[user_id])

        # Generate response based on personality and provider
        response = chat_handler.generate_response(
            message=message,
            chat_history=chat_histories[user_id],
            personality=personality,
            memory_insights=memory_insights,
            provider=ai_provider
        )

        # Add assistant response to history
        chat_histories[user_id].append({
            'role': 'assistant',
            'content': response
        })

        return jsonify({
            'response': response,
            'memory_insights': memory_insights,
            'personality': personality,
            'provider': ai_provider
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/memory/<user_id>', methods=['GET'])
def get_memory(user_id):
    try:
        if user_id not in chat_histories:
            return jsonify({'memories': {}}), 200

        memories = memory_extractor.extract_memories(chat_histories[user_id])
        return jsonify({'memories': memories}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-personalities', methods=['POST'])
def compare_personalities():
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        ai_provider = data.get('ai_provider', 'openai')

        chat_history = chat_histories.get(user_id, [])
        memory_insights = memory_extractor.extract_memories(chat_history) if chat_history else {}

        # Get available personalities
        personalities = ['calm_mentor', 'witty_friend', 'therapist', 'professional']

        responses = {}
        for personality in personalities:
            response = chat_handler.generate_response(
                message=message,
                chat_history=chat_history,
                personality=personality,
                memory_insights=memory_insights,
                provider=ai_provider
            )
            responses[personality] = response

        return jsonify({
            'original_message': message,
            'responses': responses,
            'memory_insights': memory_insights
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear-history/<user_id>', methods=['DELETE'])
def clear_history(user_id):
    if user_id in chat_histories:
        del chat_histories[user_id]
    return jsonify({'message': 'History cleared'}), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
