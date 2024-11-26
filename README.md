# Alma - Find Your Spotify Soulmate

Alma is a sophisticated music-based social platform that connects users based on their musical taste and preferences. Using Spotify's rich music data, Alma creates meaningful connections between users who share similar music interests.

## Features

### Core Features
- **Spotify Integration**
  - OAuth2 authentication
  - Real-time music data synchronization
  - Comprehensive music profile analysis
- **Smart Connection System**
  - AI-powered music compatibility matching
  - Privacy-focused social connections
  - Gradual profile reveal system
- **Mood Rooms**
  - Real-time music sharing spaces
  - Live track synchronization
- **Music Analysis**
  - Genre preference matching
  - Artist overlap detection
  - Listening pattern analysis
  - Music soul level calculation

### Technical Features
- FastAPI backend with async support
- SQLAlchemy ORM with PostgreSQL
- Redis for real-time features
- Comprehensive test coverage
- Secure authentication system

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- Spotify Developer Account

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd alma
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

### Running the Application

Start the application using:
```bash
bash run.sh
```

Or manually:
```bash
uvicorn main:app --reload --port 8000
```

## Development

### Project Structure
```
alma/
├── app/                 # Application package
│   ├── auth/           # Authentication
│   ├── connections/    # User connections
│   ├── database/       # Database models and config
│   ├── models/         # Pydantic models
│   ├── music/          # Music analysis
│   ├── playlists/      # Playlist management
│   └── websockets/     # Real-time features
├── tests/              # Test suite
│   ├── auth/
│   ├── connections/
│   └── ...
├── alembic/            # Database migrations
└── requirements.txt    # Project dependencies
```

### Running Tests

Run the full test suite:
```bash
pytest
```

With coverage report:
```bash
pytest --cov=app tests/
```

Run specific tests:
```bash
pytest tests/auth/       # Run auth tests
pytest tests/models/     # Run model tests
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

## API Documentation

Once the application is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.