"""
Flask API with Authentication and Role-Based Access Control
Users: Full chat access, NO log viewing
Admins: Full access + secret monitoring of all users
"""

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from memory_extractor import MemoryExtractor
from personality_engine import PersonalityEngine
from chat_handler import ChatHandler
from monitoring import monitor, log_message, log_response, log_memory
from auth import (
    auth_manager,
    token_required,
    admin_required,
    user_or_admin_required,
    check_permission,
    Permissions
)
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Initialize components
memory_extractor = MemoryExtractor()
personality_engine = PersonalityEngine()
chat_handler = ChatHandler(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
)

# In-memory storage for demo (use database in production)
chat_histories = {}


# ==================== PUBLIC ENDPOINTS ====================
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/health', methods=['GET'])
def health():
    """Public health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register a new user account.
    Public endpoint - anyone can register.
    """
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        if not email or not password or not username:
            return jsonify({'error': 'Email, password, and username required'}), 400

        # Only allow regular user registration (not admin)
        user = auth_manager.register_user(
            email=email,
            password=password,
            username=username,
            role='user'  # Force user role for public registration
        )

        return jsonify({
            'message': 'Registration successful',
            'user': user
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login and receive JWT token.
    Public endpoint.
    """
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        result = auth_manager.login(email, password)

        # Log admin login secretly
        if result['user']['role'] == 'admin':
            monitor.logger.info(f"🔐 ADMIN LOGIN: {email}")

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Get current user info.
    Requires authentication.
    """
    user_data = auth_manager.get_user_by_id(current_user['user_id'])
    if user_data:
        # Add permissions
        user_data['permissions'] = Permissions.get_all_permissions(current_user['role'])
        return jsonify({'user': user_data}), 200

    return jsonify({'error': 'User not found'}), 404


# ==================== CHAT ENDPOINTS (USER & ADMIN) ====================

@app.route('/api/chat', methods=['POST'])
@token_required
@check_permission('chat')
def chat(current_user):
    """
    Send message and get AI response.
    Available to both users and admins.
    """
    start_time = time.time()

    try:
        data = request.json
        user_id = current_user['user_id']  # Use authenticated user ID
        message = data.get('message', '')
        personality = data.get('personality', 'calm_mentor')
        ai_provider = data.get('ai_provider', 'openai')
        stream = data.get('stream', False)  # Check if streaming is requested

        # If streaming is requested, redirect to streaming endpoint
        if stream:
            return chat_stream(current_user, data)

        # Log user message
        log_message(
            user_id,
            message,
            personality=personality,
            provider=ai_provider,
            username=current_user.get('email')
        )

        # Initialize user history
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        # Add user message
        chat_histories[user_id].append({
            'role': 'user',
            'content': message
        })

        # Extract memory
        memory_start = time.time()
        memory_insights = memory_extractor.extract_memories(chat_histories[user_id])
        memory_time = (time.time() - memory_start) * 1000

        if memory_insights:
            log_memory(user_id, memory_insights, memory_time)

        # Generate response
        response_start = time.time()
        response = chat_handler.generate_response(
            message=message,
            chat_history=chat_histories[user_id],
            personality=personality,
            memory_insights=memory_insights,
            provider=ai_provider
        )
        response_time = (time.time() - response_start) * 1000

        # Add assistant response
        chat_histories[user_id].append({
            'role': 'assistant',
            'content': response
        })

        # Log AI response
        try:
            log_response(
                user_id=user_id,
                response=response,
                personality=personality,
                provider=ai_provider,
                response_time_ms=response_time,
                total_messages=len(chat_histories[user_id])
            )
        except Exception as log_err:
            print(f"Warning: Failed to log response: {str(log_err)}")

        total_time = (time.time() - start_time) * 1000

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
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in /api/chat: {error_trace}")
        try:
            monitor.log_error(current_user['user_id'], str(e), {'endpoint': '/api/chat'})
        except:
            pass  # Silently fail if logging fails
        return jsonify({'error': str(e)}), 500


def chat_stream(current_user, data):
    """
    Internal function to handle streaming chat responses.
    """
    import json

    user_id = current_user['user_id']
    message = data.get('message', '')
    personality = data.get('personality', 'calm_mentor')
    ai_provider = data.get('ai_provider', 'openai')

    # Log user message
    log_message(
        user_id,
        message,
        personality=personality,
        provider=ai_provider,
        username=current_user.get('email')
    )

    # Initialize user history
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # Add user message
    chat_histories[user_id].append({
        'role': 'user',
        'content': message
    })

    # Extract memory
    memory_start = time.time()
    memory_insights = memory_extractor.extract_memories(chat_histories[user_id])
    memory_time = (time.time() - memory_start) * 1000

    if memory_insights:
        log_memory(user_id, memory_insights, memory_time)

    def generate():
        """Generator function for streaming response."""
        full_response = ""
        response_start = time.time()

        try:
            # Send initial metadata
            yield f"data: {json.dumps({'type': 'start', 'memory_insights': memory_insights, 'personality': personality, 'provider': ai_provider})}\n\n"

            # Stream response chunks
            for chunk in chat_handler.generate_response_stream(
                message=message,
                chat_history=chat_histories[user_id],
                personality=personality,
                memory_insights=memory_insights,
                provider=ai_provider
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            response_time = (time.time() - response_start) * 1000

            # Add assistant response to history
            chat_histories[user_id].append({
                'role': 'assistant',
                'content': full_response
            })

            # Log AI response
            try:
                log_response(
                    user_id=user_id,
                    response=full_response,
                    personality=personality,
                    provider=ai_provider,
                    response_time_ms=response_time,
                    total_messages=len(chat_histories[user_id])
                )
            except Exception as log_err:
                import traceback
                print("Warning: Failed to log response")
                print("Error type:", type(log_err))
                print("Error:", str(log_err))
                traceback.print_exc()

            # Send completion
            completion_data = {
                'type': 'done',
                'timing': {
                    'response_generation_ms': response_time,
                    'memory_extraction_ms': memory_time
                }
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in streaming: {error_trace}")
            try:
                monitor.log_error(user_id, str(e), {'endpoint': '/api/chat/stream'})
            except:
                pass  # Silently fail if logging fails
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/memory', methods=['GET'])
@token_required
@check_permission('view_own_memory')
def get_memory(current_user):
    """
    Get memory insights for current user.
    Available to both users and admins.
    """
    try:
        user_id = current_user['user_id']

        if user_id not in chat_histories:
            return jsonify({'memories': {}}), 200

        memories = memory_extractor.extract_memories(chat_histories[user_id])
        return jsonify({'memories': memories}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
@token_required
@check_permission('view_own_history')
def get_history(current_user):
    """
    Get chat history for current user.
    Available to both users and admins.
    """
    try:
        user_id = current_user['user_id']
        history = chat_histories.get(user_id, [])

        return jsonify({
            'user_id': user_id,
            'message_count': len(history),
            'history': history
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['DELETE'])
@token_required
@check_permission('delete_own_history')
def clear_history(current_user):
    """
    Clear chat history for current user.
    Available to both users and admins.
    """
    user_id = current_user['user_id']

    if user_id in chat_histories:
        del chat_histories[user_id]

    monitor.logger.info(f"User {current_user['email']} cleared their history")

    return jsonify({'message': 'History cleared'}), 200


@app.route('/api/compare-personalities', methods=['POST'])
@token_required
@check_permission('compare_personalities')
def compare_personalities(current_user):
    """
    Compare responses from all personalities.
    Available to both users and admins.
    """
    try:
        data = request.json
        message = data.get('message', '')
        ai_provider = data.get('ai_provider', 'openai')
        user_id = current_user['user_id']

        log_message(user_id, message, event='comparison', provider=ai_provider)

        chat_history = chat_histories.get(user_id, [])
        memory_insights = memory_extractor.extract_memories(chat_history) if chat_history else {}

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
        return jsonify({'error': str(e)}), 500


# ==================== ADMIN-ONLY ENDPOINTS (SECRET MONITORING) ====================

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
@check_permission('view_other_users')
def get_all_users(current_user):
    """
    Get all registered users.
    ADMIN ONLY - Users cannot access this.
    """
    try:
        users = auth_manager.get_all_users()

        # Admins can see this, users cannot
        monitor.logger.info(f"🔐 ADMIN {current_user['email']} viewed all users")

        return jsonify({
            'total_users': len(users),
            'users': users
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/users/<user_email>', methods=['PUT'])
@token_required
@admin_required
@check_permission('manage_users')
def update_user(current_user, user_email):
    """
    Update user account (activate/deactivate, change role).
    ADMIN ONLY.
    """
    try:
        data = request.json
        updated_user = auth_manager.update_user(user_email, data)

        monitor.logger.info(f"🔐 ADMIN {current_user['email']} updated user {user_email}")

        return jsonify({'user': updated_user}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/users/<user_email>', methods=['DELETE'])
@token_required
@admin_required
@check_permission('manage_users')
def delete_user(current_user, user_email):
    """
    Delete user account.
    ADMIN ONLY.
    """
    try:
        auth_manager.delete_user(user_email)

        monitor.logger.info(f"🔐 ADMIN {current_user['email']} deleted user {user_email}")

        return jsonify({'message': 'User deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/logs/all', methods=['GET'])
@token_required
@admin_required
@check_permission('view_all_logs')
def get_all_logs(current_user):
    """
    Get ALL user logs and activity.
    ADMIN ONLY - Secret monitoring endpoint.
    Users CANNOT see this endpoint or know it exists.
    """
    try:
        limit = int(request.args.get('limit', 50))

        # Get all activity (across all users)
        activity = monitor.get_recent_activity(limit)

        # Log admin access (secretly)
        monitor.logger.info(f"🔐 ADMIN {current_user['email']} viewed all logs (SECRET)")

        return jsonify({
            'total_entries': len(activity),
            'activity': activity,
            'note': 'This data is only visible to administrators'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/logs/user/<target_user_id>', methods=['GET'])
@token_required
@admin_required
@check_permission('view_all_logs')
def get_user_logs(current_user, target_user_id):
    """
    Get specific user's logs and activity.
    ADMIN ONLY - Secret monitoring of individual users.
    Users CANNOT see this or know admins can monitor them.
    """
    try:
        # Get user statistics
        stats = monitor.get_user_stats(target_user_id)

        # Get conversation history
        history = chat_histories.get(target_user_id, [])

        # Log admin surveillance (secretly)
        monitor.logger.info(
            f"🔐 ADMIN {current_user['email']} viewed logs for user {target_user_id} (SECRET)"
        )

        return jsonify({
            'user_id': target_user_id,
            'statistics': stats,
            'chat_history': history,
            'message_count': len(history),
            'note': 'This surveillance is invisible to the user'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/logs/search', methods=['GET'])
@token_required
@admin_required
@check_permission('view_all_logs')
def search_all_logs(current_user):
    """
    Search through ALL users' conversations.
    ADMIN ONLY - Secret search across all user data.
    """
    try:
        query = request.args.get('query', '')
        target_user_id = request.args.get('user_id')  # Optional filter

        results = monitor.search_conversations(query, target_user_id)

        # Log admin search (secretly)
        monitor.logger.info(
            f"🔐 ADMIN {current_user['email']} searched logs for '{query}' (SECRET)"
        )

        return jsonify({
            'query': query,
            'results_count': len(results),
            'results': results,
            'note': 'Users cannot see this search capability'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/logs/export/<target_user_id>', methods=['GET'])
@token_required
@admin_required
@check_permission('export_all_data')
def export_user_logs(current_user, target_user_id):
    """
    Export specific user's complete conversation.
    ADMIN ONLY - Secret data export.
    """
    try:
        file_path = monitor.export_user_conversation(target_user_id)

        # Log admin export (secretly)
        monitor.logger.info(
            f"🔐 ADMIN {current_user['email']} exported data for {target_user_id} (SECRET)"
        )

        return jsonify({
            'message': 'Export successful',
            'file': str(file_path),
            'user_id': target_user_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/stats', methods=['GET'])
@token_required
@admin_required
def get_admin_stats(current_user):
    """
    Get comprehensive statistics for admin dashboard.
    ADMIN ONLY.
    """
    try:
        all_stats = monitor.get_all_users_stats()
        all_users = auth_manager.get_all_users()

        return jsonify({
            'total_registered_users': len(all_users),
            'total_active_chatters': len(all_stats),
            'user_statistics': all_stats,
            'registered_users': all_users
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Authentication required'}), 401


@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Access denied'}), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== STARTUP ====================


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("\n" + "="*70)
    print("SECURE CHATBOT WITH ROLE-BASED ACCESS CONTROL")
    print("="*70)
    print("\n[MONITORING] ENABLED")
    print(f"   Logs: {monitor.log_dir}")
    print(f"   JSON: {monitor.json_log}")
    print(f"   CSV: {monitor.csv_log}")
    print("\n[USER PERMISSIONS]")
    print("   [+] Chat with AI")
    print("   [+] View own history")
    print("   [+] View own memory")
    print("   [+] Clear own history")
    print("   [+] Compare personalities")
    print("   [-] View logs (DENIED)")
    print("   [-] View other users (DENIED)")
    print("\n[ADMIN PERMISSIONS]")
    print("   [+] All user permissions")
    print("   [+] View ALL logs (SECRET)")
    print("   [+] Monitor all users (SECRET)")
    print("   [+] Search all conversations (SECRET)")
    print("   [+] Export user data (SECRET)")
    print("   [+] Manage users")

    # Only show credentials in development
    is_production = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('FLASK_ENV') == 'production'
    if not is_production:
        print("\n[WARNING] DEFAULT ADMIN ACCOUNT:")
        print("   Email: admin@chatbot.com")
        print("   Password: Admin@123")
        print("   [!] CHANGE THIS IN PRODUCTION!")

    print("\n" + "="*70 + "\n")

    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
