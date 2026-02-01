# FollowUP

![Cursor 2-Day AI Hackathon](https://ai-beavers.com/_next/image?url=%2Fimages%2Fhackathon-hero-20012026.png&w=1920&q=75)

> **Never miss a moment that matters.**

FollowUP is an intelligent calendar assistant that helps you achieve Work-Life Balance by automatically extracting events from text, images, and voice inputs. Every meeting, every gathering, every concert deserves your presence.

**Capture any event. Add to calendar. Stay on track.**

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Flutter (iOS / Android / Web) |
| **Backend** | Python FastAPI + SQLAlchemy |
| **AI/LLM** | LangChain + LangGraph + OpenAI GPT-4o |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Hosting** | Railway |

---

## Features

- **Multi-modal Input** — Paste text, upload images (posters, screenshots), or describe events in natural language
- **AI-Powered Extraction** — LLM automatically extracts event details (title, time, location, description)
- **Intelligent Chat Agent** — LangGraph-based agent with intent recognition for creating, querying, updating, and deleting events
- **ICS Calendar Export** — Generate standard iCalendar files compatible with all major calendar apps
- **Event Management** — Full CRUD operations for your events with follow/unfollow functionality
- **Multi-language Support** — English, German, and Chinese interface
- **Streaming Responses** — Real-time chat streaming for better user experience

---

## Architecture

```mermaid
flowchart TB
    subgraph Client["Client"]
        Flutter["Flutter App\n(iOS/Android/Web)"]
    end

    subgraph API["FastAPI Backend"]
        ChatRouter["/api/chat"]
        ParseRouter["/api/parse"]
        EventsRouter["/api/events"]
    end

    subgraph Agent["LangGraph Agent"]
        IntentClassifier["Intent Classifier"]
        
        subgraph Handlers["Handlers"]
            ChatHandler["Chat"]
            CreateHandler["Create Event"]
            QueryHandler["Query Event"]
            UpdateHandler["Update Event"]
            DeleteHandler["Delete Event"]
        end
    end

    subgraph Services["Services"]
        LLMService["LLM Service\n(OpenAI GPT-4o)"]
        Memory["Conversation Memory"]
    end

    subgraph Database["Database"]
        DB["SQLite / PostgreSQL"]
    end

    Flutter --> API
    ChatRouter --> Agent
    ParseRouter --> LLMService
    Agent --> LLMService
    Agent --> Memory
    Memory --> DB
    Handlers --> EventsRouter
    EventsRouter --> DB
```

---

## How to Run

### Prerequisites

- Python 3.11+
- Flutter 3.x
- OpenAI API Key

### Backend

```bash
# Navigate to backend directory
cd Backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the development server
python main.py
```

The API will be available at `http://localhost:8000`. View API docs at `http://localhost:8000/docs`.

### Frontend

```bash
# Navigate to frontend directory
cd Frontend/followup

# Install dependencies
flutter pub get

# Run the app
flutter run

# Build for web
flutter build web
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login, returns JWT token |
| GET | `/api/user/me` | Get current user info |
| POST | `/api/chat` | Intelligent chat agent (supports streaming) |
| DELETE | `/api/chat/{session_id}` | Clear conversation history |
| POST | `/api/parse` | Parse text/image to extract events |
| GET | `/api/events` | List user's events |
| GET | `/api/events/search` | Search events |
| POST | `/api/events` | Create new event |
| PUT | `/api/events/{id}` | Update event |
| DELETE | `/api/events/{id}` | Delete event |
| GET | `/api/events/{id}/ics` | Download ICS calendar file |
| GET | `/api/health` | Health check |

---

## Preset Users (Development)

For quick testing, use these preset accounts:

| Username | Password |
|----------|----------|
| alice | alice123 |
| bob | bob123 |
| jane | jane123 |
| xiao | xiao123 |
| moni | moni123 |

---

## Project Structure

```
follow_up/
├── Backend/
│   ├── main.py              # FastAPI entry point
│   ├── routers/             # API route handlers
│   │   ├── auth.py          # Authentication
│   │   ├── chat.py          # Intelligent chat agent
│   │   ├── events.py        # Event CRUD
│   │   └── parse.py         # Text/image parsing
│   ├── services/
│   │   ├── llm_service.py   # LangChain integration
│   │   └── agent/           # LangGraph agent
│   └── models.py            # Database models
├── Frontend/
│   └── followup/            # Flutter application
│       ├── lib/
│       │   ├── pages/       # UI screens
│       │   ├── services/    # API services
│       │   └── providers/   # State management
│       └── pubspec.yaml
└── Docs/                    # Documentation
```

---

## Documentation

- [Backend README](Backend/README.md) — Backend architecture and API details
- [Backend Development Rules](Backend/AGENTS.md) — Development guidelines
- [Product Specification](Docs/production.md) — Full product documentation

---

## License

This project was created for the Cursor 2-Day AI Hackathon (Hamburg, 2026).

---

*Built with Cursor AI*
