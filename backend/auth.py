"""
Authentication and Authorization System
Secure user and admin login with role-based permissions
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import os
from typing import Dict, Any, Optional
import json
from pathlib import Path


class AuthManager:
    """
    Manages user authentication and authorization.
    Supports user and admin roles with different permissions.
    """

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.token_expiry_hours = 24

        # Initialize user storage
        self.users_file = Path('data/users.json')
        self.users_file.parent.mkdir(exist_ok=True)

        # Load or create users
        self.users = self._load_users()

        # Create default admin if not exists
        self._create_default_admin()

    def _load_users(self) -> Dict[str, Dict]:
        """Load users from JSON file."""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_users(self):
        """Save users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def _create_default_admin(self):
        """Create default admin account if none exists."""
        admin_exists = any(u['role'] == 'admin' for u in self.users.values())

        if not admin_exists:
            # Use environment variables for production deployment
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@chatbot.com')
            admin_password = os.getenv('ADMIN_PASSWORD', 'Admin@123')
            admin_username = os.getenv('ADMIN_USERNAME', 'Admin')

            self.register_user(
                email=admin_email,
                password=admin_password,
                username=admin_username,
                role='admin'
            )

            # Only show credentials in development mode
            is_production = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('FLASK_ENV') == 'production'
            if not is_production:
                print("[AUTH] Default admin created:")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                print("   WARNING: CHANGE THIS PASSWORD IN PRODUCTION!")
            else:
                print("[AUTH] Admin account initialized from environment variables")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_token(self, user_id: str, email: str, role: str) -> str:
        """
        Generate JWT token for user.

        Args:
            user_id: Unique user identifier
            email: User email
            role: User role (user/admin)

        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }

        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def register_user(
        self,
        email: str,
        password: str,
        username: str,
        role: str = 'user'
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            email: User email (unique)
            password: Plain text password
            username: Display name
            role: 'user' or 'admin'

        Returns:
            User data (without password)

        Raises:
            ValueError: If email already exists
        """
        # Check if email exists
        if email in self.users:
            raise ValueError('Email already registered')

        # Validate password strength
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters')

        # Create user
        user_id = f"user_{len(self.users) + 1}_{datetime.now().timestamp()}"

        user_data = {
            'user_id': user_id,
            'email': email,
            'username': username,
            'password_hash': self.hash_password(password),
            'role': role,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True
        }

        self.users[email] = user_data
        self._save_users()

        # Return user data without password
        return {k: v for k, v in user_data.items() if k != 'password_hash'}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate token.

        Args:
            email: User email
            password: Plain text password

        Returns:
            Dictionary with token and user data

        Raises:
            ValueError: If credentials are invalid
        """
        # Check if user exists
        if email not in self.users:
            raise ValueError('Invalid credentials')

        user = self.users[email]

        # Check if account is active
        if not user.get('is_active', True):
            raise ValueError('Account is disabled')

        # Verify password
        if not self.verify_password(password, user['password_hash']):
            raise ValueError('Invalid credentials')

        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users()

        # Generate token
        token = self.generate_token(user['user_id'], email, user['role'])

        return {
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'email': user['email'],
                'username': user['username'],
                'role': user['role']
            }
        }

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data by email (without password)."""
        user = self.users.get(email)
        if user:
            return {k: v for k, v in user.items() if k != 'password_hash'}
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by user_id (without password)."""
        for user in self.users.values():
            if user['user_id'] == user_id:
                return {k: v for k, v in user.items() if k != 'password_hash'}
        return None

    def get_all_users(self) -> list:
        """Get all users (admin only, without passwords)."""
        return [
            {k: v for k, v in user.items() if k != 'password_hash'}
            for user in self.users.values()
        ]

    def update_user(self, email: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user data.

        Args:
            email: User email
            updates: Dictionary of fields to update

        Returns:
            Updated user data
        """
        if email not in self.users:
            raise ValueError('User not found')

        user = self.users[email]

        # Allow updating specific fields
        allowed_fields = ['username', 'is_active']
        for field in allowed_fields:
            if field in updates:
                user[field] = updates[field]

        # Handle password change separately
        if 'new_password' in updates:
            user['password_hash'] = self.hash_password(updates['new_password'])

        self._save_users()

        return {k: v for k, v in user.items() if k != 'password_hash'}

    def delete_user(self, email: str):
        """Delete a user account."""
        if email in self.users:
            del self.users[email]
            self._save_users()


# Global auth manager instance
auth_manager = AuthManager()


# ==================== DECORATORS ====================

def token_required(f):
    """
    Decorator to require valid JWT token.
    Extracts user info and passes to route.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Format: "Bearer <token>"
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        # Verify token
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        # Pass user info to route
        return f(current_user=payload, *args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator to require admin role.
    Must be used with @token_required.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = kwargs.get('current_user')

        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401

        if current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)

    return decorated


def user_or_admin_required(f):
    """
    Decorator to require user or admin role.
    Allows users to access their own data, admins to access all.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = kwargs.get('current_user')

        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401

        # Extract requested user_id from route
        requested_user_id = kwargs.get('user_id') or request.view_args.get('user_id')

        # Admin can access anything
        if current_user.get('role') == 'admin':
            return f(*args, **kwargs)

        # Regular user can only access their own data
        if requested_user_id and requested_user_id != current_user.get('user_id'):
            return jsonify({'error': 'Access denied'}), 403

        return f(*args, **kwargs)

    return decorated


# ==================== PERMISSION CHECKER ====================

class Permissions:
    """Define permissions for different roles."""

    USER_PERMISSIONS = {
        'chat': True,
        'view_own_history': True,
        'view_own_memory': True,
        'delete_own_history': True,
        'compare_personalities': True,
        'view_logs': False,  # ❌ Users CANNOT see logs
        'view_other_users': False,
        'admin_panel': False
    }

    ADMIN_PERMISSIONS = {
        'chat': True,
        'view_own_history': True,
        'view_own_memory': True,
        'delete_own_history': True,
        'compare_personalities': True,
        'view_logs': True,  # ✅ Admins CAN see all logs
        'view_other_users': True,
        'view_all_logs': True,  # ✅ Can see everyone's logs
        'admin_panel': True,
        'manage_users': True,
        'export_all_data': True
    }

    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if a role has a specific permission."""
        if role == 'admin':
            return Permissions.ADMIN_PERMISSIONS.get(permission, False)
        else:
            return Permissions.USER_PERMISSIONS.get(permission, False)

    @staticmethod
    def get_all_permissions(role: str) -> Dict[str, bool]:
        """Get all permissions for a role."""
        if role == 'admin':
            return Permissions.ADMIN_PERMISSIONS
        else:
            return Permissions.USER_PERMISSIONS


def check_permission(permission: str):
    """
    Decorator to check specific permission.

    Args:
        permission: Permission name to check
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')

            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401

            role = current_user.get('role', 'user')

            if not Permissions.has_permission(role, permission):
                return jsonify({
                    'error': f'Permission denied: {permission}',
                    'message': 'You do not have permission to access this resource'
                }), 403

            return f(*args, **kwargs)

        return decorated
    return decorator
