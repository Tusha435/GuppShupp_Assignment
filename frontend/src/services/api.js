import axios from "axios";

/**
 * API base URL
 *
 * - In production (Railway build): use same origin => ""
 * - In local dev: use REACT_APP_API_URL or fall back to http://localhost:5000
 *
 * For local dev, create frontend/.env with:
 *   REACT_APP_API_URL=http://localhost:5000
 */
const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? ""
    : process.env.REACT_APP_API_URL || "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach token to each request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ================== AUTH API ==================

export const authAPI = {
  register: async (email, password, username) => {
    try {
      const response = await api.post("/api/auth/register", {
        email,
        password,
        username,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  login: async (email, password) => {
    try {
      const response = await api.post("/api/auth/login", {
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await api.get("/api/auth/me");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

// ================== CHAT API ==================

export const chatAPI = {
  sendMessage: async (message, personality, aiProvider) => {
    try {
      const response = await api.post("/api/chat", {
        message,
        personality,
        ai_provider: aiProvider,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Streaming version using Fetch + SSE-style chunks
  sendMessageStream: async (
    message,
    personality,
    aiProvider,
    onChunk,
    onComplete,
    onError
  ) => {
    try {
      const token = localStorage.getItem("token");

      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        body: JSON.stringify({
          message,
          personality,
          ai_provider: aiProvider,
          stream: true,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw errorData || { message: "Failed to start stream" };
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let metadata = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // keep incomplete line

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;

          try {
            const data = JSON.parse(line.slice(6));

            if (data.type === "start") {
              metadata = {
                memory_insights: data.memory_insights,
                personality: data.personality,
                provider: data.provider,
              };
            } else if (data.type === "chunk") {
              onChunk?.(data.content);
            } else if (data.type === "done") {
              onComplete?.({
                ...metadata,
                timing: data.timing,
              });
            } else if (data.type === "error") {
              onError?.(data.message);
            }
          } catch (e) {
            console.error("Error parsing SSE data:", e);
          }
        }
      }
    } catch (error) {
      console.error("Stream error:", error);
      onError?.(error.error || error.message || "An error occurred");
    }
  },

  getMemory: async () => {
    try {
      const response = await api.get("/api/memory");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getHistory: async () => {
    try {
      const response = await api.get("/api/history");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  clearHistory: async () => {
    try {
      const response = await api.delete("/api/history");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  comparePersonalities: async (message, aiProvider) => {
    try {
      const response = await api.post("/api/compare-personalities", {
        message,
        ai_provider: aiProvider,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  healthCheck: async () => {
    try {
      const response = await api.get("/health");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

// ================== ADMIN API ==================

export const adminAPI = {
  getAllUsers: async () => {
    try {
      const response = await api.get("/api/admin/users");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getAllLogs: async (limit = 50) => {
    try {
      const response = await api.get(`/api/admin/logs/all?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getUserLogs: async (userId) => {
    try {
      const response = await api.get(`/api/admin/logs/user/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  searchLogs: async (query, userId = null) => {
    try {
      const params = new URLSearchParams({ query });
      if (userId) params.append("user_id", userId);

      const response = await api.get(`/api/admin/logs/search?${params}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  exportUserLogs: async (userId) => {
    try {
      const response = await api.get(`/api/admin/logs/export/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getStats: async () => {
    try {
      const response = await api.get("/api/admin/stats");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  updateUser: async (email, updates) => {
    try {
      const response = await api.put(`/api/admin/users/${email}`, updates);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  deleteUser: async (email) => {
    try {
      const response = await api.delete(`/api/admin/users/${email}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default api;
