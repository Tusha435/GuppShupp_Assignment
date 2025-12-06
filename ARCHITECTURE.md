# System Architecture 🏗️

Complete architecture documentation for the Personality AI Chatbot.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React Frontend - Port 3000)                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    Chat      │  │   Memory     │  │  Comparison  │         │
│  │  Interface   │  │    Panel     │  │     View     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      FLASK BACKEND                              │
│                        (Port 5000)                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    API ENDPOINTS                        │  │
│  │  POST /api/chat                                         │  │
│  │  GET  /api/memory/{user_id}                            │  │
│  │  POST /api/compare-personalities                       │  │
│  │  DELETE /api/clear-history/{user_id}                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                             │                                   │
│  ┌──────────────┬───────────┴────────┬──────────────┐         │
│  │              │                    │              │         │
│  ▼              ▼                    ▼              ▼         │
│  ┌────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Chat  │  │ Memory   │  │ Personality  │  │   Chat     │  │
│  │Handler │  │Extractor │  │   Engine     │  │  History   │  │
│  └────────┘  └──────────┘  └──────────────┘  │ (In-Memory)│  │
│       │            │              │           └────────────┘  │
└───────┼────────────┼──────────────┼─────────────────────────────┘
        │            │              │
        │            │              │
        ▼            ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LANGCHAIN LAYER                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   OpenAI     │  │  Anthropic   │  │  LLM Chains  │         │
│  │ Integration  │  │ Integration  │  │  & Prompts   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────┬────────────────┬────────────────────────────────────┘
          │                │
          │                │
          ▼                ▼
┌──────────────────────────────────────┐
│       EXTERNAL AI SERVICES           │
│                                      │
│  ┌──────────────────────────────┐   │
│  │   OpenAI GPT-4 API          │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │   Anthropic Claude API       │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

## Component Breakdown

### Frontend (React)

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.js       # Main chat UI
│   │   │   ├── Message display
│   │   │   ├── Input form
│   │   │   ├── Personality selector
│   │   │   └── Provider selector
│   │   │
│   │   ├── MemoryPanel.js         # Memory display
│   │   │   ├── Preferences list
│   │   │   ├── Emotional patterns
│   │   │   ├── Facts display
│   │   │   └── Auto-refresh
│   │   │
│   │   └── ComparisonView.js      # Personality comparison
│   │       ├── Input form
│   │       ├── 4x Personality cards
│   │       └── Side-by-side display
│   │
│   ├── services/
│   │   └── api.js                 # API client
│   │       ├── sendMessage()
│   │       ├── getMemory()
│   │       ├── comparePersonalities()
│   │       └── clearHistory()
│   │
│   └── App.js                     # Main app
│       ├── View routing
│       └── User ID management
```

### Backend (Flask + LangChain)

```
backend/
├── app.py                         # Flask server
│   ├── Route handlers
│   ├── CORS configuration
│   └── In-memory chat storage
│
├── memory_extractor.py            # Memory extraction
│   ├── MemoryExtractor class
│   ├── extract_preferences()
│   ├── extract_emotional_patterns()
│   ├── extract_facts()
│   └── LangChain LLM chains
│
├── personality_engine.py          # Personality system
│   ├── PersonalityEngine class
│   ├── 4x Personality configs
│   │   ├── Calm Mentor
│   │   ├── Witty Friend
│   │   ├── Therapist
│   │   └── Professional
│   ├── System prompt generation
│   └── Temperature settings
│
└── chat_handler.py                # AI integration
    ├── ChatHandler class
    ├── OpenAI integration
    ├── Anthropic integration
    └── Response generation
```

## Data Flow

### 1. Chat Message Flow

```
User Types Message
       │
       ▼
ChatInterface Component
       │
       ├─ Adds to local state
       ├─ Shows user message bubble
       └─ Calls API
           │
           ▼
    POST /api/chat
           │
           ├─ Extracts: message, personality, provider
           ├─ Retrieves chat history
           └─ Calls MemoryExtractor
               │
               ▼
       Memory Extraction
               │
               ├─ Analyzes recent messages
               ├─ Extracts preferences
               ├─ Detects emotions
               └─ Identifies facts
                   │
                   ▼
          ChatHandler
                   │
                   ├─ Gets personality config
                   ├─ Builds system prompt
                   ├─ Adds memory context
                   └─ Calls AI (OpenAI/Anthropic)
                       │
                       ▼
                  AI Response
                       │
                       ├─ Stores in history
                       └─ Returns to frontend
                           │
                           ▼
                   Display in UI
```

### 2. Memory Extraction Flow

```
User Has Conversation (30 messages)
       │
       ▼
Memory Panel Requests Update
       │
       ▼
GET /api/memory/{user_id}
       │
       ├─ Retrieves chat history
       └─ Calls MemoryExtractor
           │
           ├─────────────────┬─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
   Preference Chain    Emotion Chain     Facts Chain
           │                 │                 │
           │                 │                 │
      [LLM Call]        [LLM Call]        [LLM Call]
      GPT-4 Mini        GPT-4 Mini        GPT-4 Mini
           │                 │                 │
           ▼                 ▼                 ▼
    JSON Response       JSON Response     JSON Response
           │                 │                 │
           └─────────────────┴─────────────────┘
                             │
                             ▼
                    Combine & Return
                             │
                             ▼
                    Display in Memory Panel
```

### 3. Personality Comparison Flow

```
User Enters Message
       │
       ▼
POST /api/compare-personalities
       │
       ├─ Extract message
       ├─ Get memory insights
       └─ Loop through 4 personalities
           │
           ├─ Calm Mentor
           │   ├─ System prompt + temp 0.7
           │   └─ AI response
           │
           ├─ Witty Friend
           │   ├─ System prompt + temp 0.9
           │   └─ AI response
           │
           ├─ Therapist
           │   ├─ System prompt + temp 0.6
           │   └─ AI response
           │
           └─ Professional
               ├─ System prompt + temp 0.5
               └─ AI response
                   │
                   ▼
           Return 4 responses
                   │
                   ▼
       Display in 4 cards side-by-side
```

## Memory Extraction Process

### Input: Chat Messages

```python
messages = [
    {"role": "user", "content": "I love Python"},
    {"role": "assistant", "content": "That's great!"},
    {"role": "user", "content": "I work as a developer"},
    {"role": "assistant", "content": "Interesting!"},
    # ... more messages
]
```

### Processing: LangChain Chains

```python
# Preference Extraction Chain
preference_prompt = """
Analyze messages and extract preferences:
- Hobbies, interests
- Likes and dislikes
- Preferred topics
Return JSON: {"preferences": [...]}
"""

# Emotion Extraction Chain
emotion_prompt = """
Analyze messages and extract emotional patterns:
- Recurring emotions
- Triggers
- Communication style
Return JSON: {"emotional_patterns": [...], "dominant_emotion": "...", ...}
"""

# Facts Extraction Chain
facts_prompt = """
Analyze messages and extract important facts:
- Personal info
- Goals
- Challenges
Return JSON: {"facts": [...]}
"""
```

### Output: Memory Insights

```python
{
    "preferences": [
        "Enjoys coding in Python",
        "Interested in machine learning"
    ],
    "emotional_patterns": {
        "emotional_patterns": ["Enthusiastic about learning"],
        "dominant_emotion": "excited",
        "communication_style": "curious and engaged"
    },
    "facts": [
        "Works as a developer",
        "Learning machine learning"
    ]
}
```

## Personality Engine

### Configuration Structure

```python
{
    'calm_mentor': {
        'name': 'Calm Mentor',
        'description': 'Wise, patient, and encouraging guide',
        'system_prompt': """You are a calm, wise mentor...""",
        'temperature': 0.7,
        'tone_markers': ['thoughtful', 'patient', 'wise', 'encouraging']
    },
    # ... other personalities
}
```

### Prompt Construction

```
SYSTEM PROMPT
    │
    ├─ Base personality instructions
    │  ("You are a calm mentor...")
    │
    ├─ Communication style rules
    │  ("Use phrases like 'I notice...'")
    │
    └─ Memory context (if available)
       │
       ├─ "User preferences: Python, ML"
       ├─ "Current emotion: excited"
       └─ "Important facts: Works as developer"

CHAT HISTORY
    │
    ├─ Previous messages for context
    └─ Limited to last 10 exchanges

CURRENT MESSAGE
    │
    └─ User's latest input

    ↓

AI RESPONSE
```

## State Management

### In-Memory Storage (Current)

```python
chat_histories = {
    'user_123': [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi there!'},
        # ... more messages
    ],
    'user_456': [...]
}
```

**Limitations:**
- Lost on server restart
- Not suitable for production
- No concurrent user isolation

### Future: Database Storage

```
PostgreSQL Schema:

Table: users
├── id (PK)
├── username
└── created_at

Table: conversations
├── id (PK)
├── user_id (FK)
├── started_at
└── last_message_at

Table: messages
├── id (PK)
├── conversation_id (FK)
├── role (user/assistant)
├── content
├── personality
├── provider
└── timestamp

Table: memories
├── id (PK)
├── user_id (FK)
├── memory_type (preference/emotion/fact)
├── content
└── extracted_at
```

## API Endpoints Detail

### POST /api/chat

**Request:**
```json
{
  "user_id": "string",
  "message": "string",
  "personality": "calm_mentor" | "witty_friend" | "therapist" | "professional",
  "ai_provider": "openai" | "anthropic"
}
```

**Response:**
```json
{
  "response": "AI generated response",
  "memory_insights": {
    "preferences": [...],
    "emotional_patterns": {...},
    "facts": [...]
  },
  "personality": "calm_mentor",
  "provider": "openai"
}
```

**Processing Steps:**
1. Validate input
2. Retrieve chat history
3. Extract memory insights
4. Generate personality-based response
5. Store in history
6. Return response

### GET /api/memory/{user_id}

**Response:**
```json
{
  "memories": {
    "preferences": [...],
    "emotional_patterns": {...},
    "facts": [...]
  }
}
```

**Processing Steps:**
1. Retrieve chat history
2. Run memory extraction
3. Return insights

### POST /api/compare-personalities

**Request:**
```json
{
  "user_id": "string",
  "message": "string",
  "ai_provider": "openai" | "anthropic"
}
```

**Response:**
```json
{
  "original_message": "string",
  "responses": {
    "calm_mentor": "response",
    "witty_friend": "response",
    "therapist": "response",
    "professional": "response"
  },
  "memory_insights": {...}
}
```

**Processing Steps:**
1. Validate input
2. Retrieve memory insights
3. Generate 4 responses in parallel
4. Return all responses

## Deployment Architecture (Railway)

```
GitHub Repository
       │
       ▼
Railway Platform
       │
       ├─ Detects nixpacks.toml
       ├─ Provisions container
       │
       ├─ Build Phase
       │   ├─ Install Python 3.10
       │   ├─ Install Node.js 18
       │   ├─ pip install requirements
       │   ├─ npm install
       │   └─ npm run build (React)
       │
       └─ Deploy Phase
           ├─ Start Gunicorn
           ├─ Bind to $PORT
           └─ Serve traffic
               │
               ▼
       HTTPS Domain
       your-app.railway.app
```

## Security Architecture

### Environment Variables Flow

```
.env file (local)
    │
    └─ NEVER committed to git
        │
        ▼
Railway Dashboard
    │
    ├─ Stored securely
    └─ Injected at runtime
        │
        ▼
Backend Process
    │
    └─ os.getenv('OPENAI_API_KEY')
```

### CORS Protection

```
Frontend (localhost:3000)
       │
       ▼
Request to Backend
       │
       ▼
CORS Middleware checks origin
       │
       ├─ Allowed? → Process
       └─ Denied? → 403 Error
```

## Performance Considerations

### Response Times

```
Chat Request
├─ API Call: ~100ms
├─ Memory Extraction: ~2-3s (if triggered)
├─ AI Response: ~2-5s
└─ Total: ~2-8s
```

### Optimization Strategies

1. **Caching**: Cache memory insights
2. **Async**: Run memory extraction in background
3. **Batching**: Extract memories once per N messages
4. **Database**: Use proper storage instead of in-memory

## Scalability

### Current Limits

- In-memory storage: ~100 users
- Concurrent requests: ~10-20
- Memory extraction: Sequential

### Scaling Path

```
Phase 1 (Current)
├─ In-memory storage
└─ Single instance

Phase 2 (Database)
├─ PostgreSQL
├─ Redis caching
└─ Single instance

Phase 3 (Horizontal)
├─ Multiple instances
├─ Load balancer
├─ Shared database
└─ Redis sessions

Phase 4 (Distributed)
├─ Microservices
├─ Message queue
├─ CDN for frontend
└─ Auto-scaling
```

---

This architecture provides a solid foundation for a production-ready personality-driven chatbot with memory capabilities.
