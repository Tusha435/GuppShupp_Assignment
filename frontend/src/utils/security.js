/**
 * Security utilities for production deployment
 * Prevents credential exposure and sanitizes data
 */

/**
 * Disable console logs in production to prevent credential exposure
 */
export const disableConsoleInProduction = () => {
  if (process.env.NODE_ENV === 'production') {
    // Preserve original console methods for internal use
    const noop = () => {};

    // Disable console methods that might expose sensitive data
    console.log = noop;
    console.debug = noop;
    console.info = noop;
    console.warn = noop;

    // Keep console.error for critical issues (but sanitize in error handler)
    const originalError = console.error;
    console.error = (...args) => {
      // Filter out sensitive patterns
      const sanitized = args.map(arg => {
        if (typeof arg === 'string') {
          // Remove potential tokens, passwords, keys
          return arg
            .replace(/Bearer\s+[\w-]+\.[\w-]+\.[\w-]+/gi, 'Bearer [REDACTED]')
            .replace(/password['":\s]+[\w@!#$%^&*()]+/gi, 'password: [REDACTED]')
            .replace(/token['":\s]+[\w-]+/gi, 'token: [REDACTED]')
            .replace(/api[_-]?key['":\s]+[\w-]+/gi, 'api_key: [REDACTED]');
        }
        return arg;
      });
      originalError(...sanitized);
    };
  }
};

/**
 * Sanitize user data before storing or displaying
 * @param {Object} user - User object
 * @returns {Object} Sanitized user object
 */
export const sanitizeUserData = (user) => {
  if (!user) return null;

  const sanitized = { ...user };

  // Remove sensitive fields
  delete sanitized.password;
  delete sanitized.password_hash;
  delete sanitized.token;
  delete sanitized.api_key;

  return sanitized;
};

/**
 * Sanitize error messages to prevent information leakage
 * @param {Error|string} error - Error object or message
 * @returns {string} Safe error message
 */
export const sanitizeErrorMessage = (error) => {
  const errorStr = typeof error === 'string' ? error : error.message || 'An error occurred';

  // Generic messages for production
  if (process.env.NODE_ENV === 'production') {
    // Map specific errors to generic messages
    if (errorStr.includes('401') || errorStr.includes('Unauthorized')) {
      return 'Authentication required. Please log in again.';
    }
    if (errorStr.includes('403') || errorStr.includes('Forbidden')) {
      return 'Access denied. You do not have permission.';
    }
    if (errorStr.includes('404')) {
      return 'Resource not found.';
    }
    if (errorStr.includes('500') || errorStr.includes('Internal')) {
      return 'A server error occurred. Please try again later.';
    }

    // Remove stack traces and file paths
    return errorStr.split('\n')[0].replace(/\/[\w/]+\.(js|ts|jsx|tsx)/g, '');
  }

  // In development, show full error
  return errorStr;
};

/**
 * Check if running in production
 * @returns {boolean}
 */
export const isProduction = () => {
  return process.env.NODE_ENV === 'production';
};

/**
 * Sanitize API response to remove sensitive data
 * @param {Object} response - API response
 * @returns {Object} Sanitized response
 */
export const sanitizeResponse = (response) => {
  if (!response) return response;

  const sanitized = { ...response };

  // Remove sensitive fields from response
  delete sanitized.password;
  delete sanitized.password_hash;
  delete sanitized.jwt_secret;
  delete sanitized.api_key;
  delete sanitized.private_key;

  // Sanitize nested user objects
  if (sanitized.user) {
    sanitized.user = sanitizeUserData(sanitized.user);
  }

  return sanitized;
};

/**
 * Clear sensitive data from localStorage on logout
 */
export const clearSensitiveData = () => {
  // Clear authentication token
  localStorage.removeItem('token');

  // Clear any cached user data
  localStorage.removeItem('user');
  localStorage.removeItem('auth');

  // Clear session storage
  sessionStorage.clear();
};

/**
 * Monitor and prevent credential logging
 */
export const preventCredentialLogging = () => {
  if (typeof window !== 'undefined') {
    // Override console methods to intercept logs
    const originalMethods = {
      log: console.log,
      debug: console.debug,
      info: console.info,
      warn: console.warn,
    };

    Object.keys(originalMethods).forEach(method => {
      console[method] = (...args) => {
        // Check if any argument contains sensitive patterns
        const hasSensitiveData = args.some(arg => {
          if (typeof arg === 'string') {
            return /password|token|api[_-]?key|secret|bearer/i.test(arg);
          }
          if (typeof arg === 'object' && arg !== null) {
            return Object.keys(arg).some(key =>
              /password|token|api[_-]?key|secret/i.test(key)
            );
          }
          return false;
        });

        if (hasSensitiveData && process.env.NODE_ENV === 'production') {
          // Block the log in production
          return;
        }

        // Allow in development
        originalMethods[method](...args);
      };
    });
  }
};

export default {
  disableConsoleInProduction,
  sanitizeUserData,
  sanitizeErrorMessage,
  isProduction,
  sanitizeResponse,
  clearSensitiveData,
  preventCredentialLogging,
};
