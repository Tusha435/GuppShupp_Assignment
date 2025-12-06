# Personality AI Chatbot with Memory 🧠

A sophisticated chatbot system that extracts user memories (preferences, emotional patterns, facts) and responds with different AI personalities using LangChain, OpenAI, and Anthropic APIs.

## Features ✨

### 🧠 Memory Extraction Module
- **User Preferences**: Automatically identifies topics, hobbies, interests, likes/dislikes
- **Emotional Patterns**: Detects emotional states, triggers, and communication styles
- **Important Facts**: Remembers personal information, goals, challenges, and life events

### 🎭 Personality Engine
Choose from 4 distinct AI personalities:
1. **Calm Mentor** 🧘 - Wise, patient, encouraging guide
2. **Witty Friend** 😄 - Playful, humorous, relatable companion
3. **Therapist** 💭 - Empathetic, reflective, emotionally attuned
4. **Professional** 💼 - Clear, efficient, solution-focused

### 🤖 Dual AI Support
- **OpenAI GPT-4**: Advanced language understanding
- **Anthropic Claude**: Thoughtful and nuanced responses

### 🎨 Beautiful React Frontend
- Modern, gradient-based UI design
- Real-time chat interface
- Memory insights panel
- Side-by-side personality comparison view
- Responsive design for all devices

## Project Structure

```
GuppShupp/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── memory_extractor.py       # LangChain memory extraction
│   ├── personality_engine.py     # Personality system prompts
│   ├── chat_handler.py           # OpenAI/Anthropic integration
│   ├── requirements.txt          # Python dependencies
│   └── .env.example             # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.js  # Main chat UI
│   │   │   ├── MemoryPanel.js    # Memory display
│   │   │   └── ComparisonView.js # Personality comparison
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.js               # Main app component
│   │   └── index.js             # Entry point
│   ├── package.json
│   └── .env.example
├── railway.json                  # Railway deployment config
├── nixpacks.toml                # Build configuration
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys)) - **REQUIRED**
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/)) - OPTIONAL

> **⚠️ Important:** LangChain does NOT need a separate API key! It uses your OpenAI/Anthropic keys. See [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) for details.

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from template:
```bash
cp .env.example .env
```

5. Add your API keys to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
FLASK_ENV=development
PORT=5000
```

6. Run the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Update `.env` if needed:
```env
REACT_APP_API_URL=http://localhost:5000
```

5. Start the development server:
```bash
npm start
```

The frontend will open at `http://localhost:3000`

## Railway Deployment 🚂

### Deploy to Railway in 3 Steps:

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy on Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the configuration from `nixpacks.toml`

3. **Set Environment Variables**:
   In Railway dashboard, add these variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `FLASK_ENV`: `production`
   - `PORT`: Railway will set this automatically

4. **Update Frontend API URL**:
   After deployment, update `REACT_APP_API_URL` in Railway to your backend URL:
   ```
   REACT_APP_API_URL=https://your-app.railway.app
   ```

Railway will automatically:
- Install Python and Node.js dependencies
- Build the React frontend
- Start the Flask backend with Gunicorn
- Provide HTTPS and a custom domain

## API Endpoints

### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "user_id": "string",
  "message": "string",
  "personality": "calm_mentor" | "witty_friend" | "therapist" | "professional",
  "ai_provider": "openai" | "anthropic"
}
```

### Get Memory
```http
GET /api/memory/{user_id}
```

### Compare Personalities
```http
POST /api/compare-personalities
Content-Type: application/json

{
  "user_id": "string",
  "message": "string",
  "ai_provider": "openai" | "anthropic"
}
```

### Clear History
```http
DELETE /api/clear-history/{user_id}
```

## Usage Examples

### Example 1: Chat with Memory
After 30 messages, the system learns:
- **Preferences**: "Enjoys coding in Python", "Interested in AI/ML"
- **Emotions**: "Feels excited about new projects", "Gets stressed about deadlines"
- **Facts**: "Works as a software engineer", "Learning React"

### Example 2: Personality Comparison

**Input**: "I'm feeling stressed about a project deadline"

**Calm Mentor**: "I notice you're feeling pressure around this deadline. Consider this: what's one small step you could take right now to move forward? In my experience, breaking down overwhelming tasks into manageable pieces often reveals the path forward..."

**Witty Friend**: "Dude! Deadline stress is the worst, right? But hey, you've crushed deadlines before! Here's the thing - stress means you care, which is awesome. Let's tackle this together. What's the biggest blocker right now?"

**Therapist**: "It sounds like you're experiencing significant stress related to your project deadline. How does that pressure feel in your body right now? Sometimes acknowledging our stress is the first step toward managing it..."

**Professional**: "Here's what I recommend for managing deadline pressure: 1. Prioritize critical tasks, 2. Create a realistic timeline, 3. Identify blockers early, 4. Communicate with stakeholders. What specific aspect of the deadline concerns you most?"

## Technology Stack

- **Backend**: Flask, LangChain, OpenAI API, Anthropic API
- **Frontend**: React, Axios, React Icons, React Markdown
- **Deployment**: Railway, Gunicorn
- **Styling**: Custom CSS with gradients and animations

## Key Features Explained

### Memory Extraction
Uses LangChain with GPT-4 to analyze chat history and extract:
1. Recurring themes and preferences
2. Emotional states and triggers
3. Important personal facts

The system limits analysis to the most recent 30 messages for efficiency.

### Personality System
Each personality has:
- Custom system prompts defining tone and style
- Different temperature settings (0.5-0.9)
- Unique response patterns
- Integration with user memories

### Before/After Personality Examples

**Without Personality Engine** (Generic):
"I understand you're stressed. Try to break down your tasks."

**With Personality Engine**:
- **Calm Mentor**: Reflective, uses metaphors, asks guiding questions
- **Witty Friend**: Uses casual language, humor, enthusiasm
- **Therapist**: Validates emotions, explores feelings deeply
- **Professional**: Structured, actionable, evidence-based

## Environment Variables

### Backend (.env)
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
FLASK_ENV=development
PORT=5000
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000
```

## Development Tips

1. **Testing Different Personalities**: Use the "Compare Personalities" view
2. **Memory Insights**: Watch the Memory Panel update as you chat
3. **API Provider Switching**: Toggle between OpenAI and Anthropic in real-time
4. **Clear History**: Use the trash icon to reset conversation and memories

## Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check API keys in `.env`
- Verify Python version (3.10+)

### Frontend can't connect
- Check `REACT_APP_API_URL` in frontend `.env`
- Ensure backend is running on correct port
- Check CORS settings in Flask

### Railway deployment issues
- Verify all environment variables are set
- Check build logs for errors
- Ensure `nixpacks.toml` is in root directory

## Future Enhancements

- [ ] Persistent database for chat history (PostgreSQL/MongoDB)
- [ ] User authentication and multi-user support
- [ ] Voice input/output
- [ ] Export chat history
- [ ] Custom personality creation
- [ ] Advanced memory search
- [ ] Sentiment analysis graphs
- [ ] Mobile app

## Contributing

Feel free to submit issues or pull requests!

## License

MIT License - feel free to use this project for learning or commercial purposes.

## Credits

Built with:
- [LangChain](https://langchain.com)
- [OpenAI API](https://openai.com)
- [Anthropic Claude](https://anthropic.com)
- [Flask](https://flask.palletsprojects.com)
- [React](https://react.dev)

---

Made with ❤️ for exploring AI personalities and memory systems
