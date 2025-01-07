# 🎵 Alma - Your Musical Soulmate Finder

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Spotify](https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)](https://developer.spotify.com/documentation/web-api/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Testing](https://img.shields.io/badge/pytest-testing-green?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/en/stable/)

> 🎶 *"Music is the universal language of mankind"* - Henry Wadsworth Longfellow

## 🌟 What is Alma?

Alma is not just another social platform – it's your gateway to meaningful connections through the universal language of music. By analyzing your Spotify listening patterns, Alma finds your musical soulmates and creates connections that resonate with your soul. 

### 🎯 Why Alma?

- 🎨 **Authentic Connections** - Connect based on genuine musical taste, not curated profiles
- 🔒 **Privacy First** - Your data is yours. Share only what you want, when you want
- 🤖 **Smart Matching** - AI-powered algorithms that understand music like you do
- ⚡ **Real-time Experience** - Live music sharing and synchronized listening experiences

## ✨ Features

### 🎸 Core Features

<details>
<summary><b>🔑 Spotify Integration</b></summary>

- 🔐 Secure OAuth2 authentication
- 🔄 Real-time music data sync
- 📊 Deep musical taste analysis
</details>

<details>
<summary><b>🤝 Smart Connection System</b></summary>

- 🧠 AI-powered compatibility matching
- 🛡️ Privacy-focused social features
- 🎭 Progressive profile reveal
</details>

<details>
<summary><b>🎧 Mood Rooms</b></summary>

- 🎵 Real-time music sharing spaces
- 🔄 Live track synchronization
- 👥 Shared listening experiences
</details>

<details>
<summary><b>📊 Music Analysis</b></summary>

- 🎯 Genre preference matching
- 🎸 Artist overlap detection
- 📈 Listening pattern analysis
- 💫 Music soul level calculation
</details>

## 🚀 Quick Start

### 📋 Prerequisites

Before you begin, ensure you have:
- 🐍 Python 3.9+
- 🐘 PostgreSQL
- 📦 Redis
- 🎵 Spotify Developer Account

### 💻 Installation

1️⃣ **Clone & Navigate**
```bash
git clone [repository-url]
cd alma
```

2️⃣ **Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # 🪟 Windows: venv\Scripts\activate
```

3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

4️⃣ **Configure Environment**
```bash
cp .env.example .env
# ✏️ Edit .env with your settings
```

5️⃣ **Initialize Database**
```bash
alembic upgrade head
```

### 🏃‍♂️ Running Alma

**Quick Start:**
```bash
bash run.sh
```

**Manual Start:**
```bash
uvicorn main:app --reload --port 8000
```

## 🛠️ Development

### 📁 Project Structure
```
alma/
├── 📱 app/                # Application core
│   ├── 🔑 auth/          # Authentication
│   ├── 🤝 connections/   # User connections
│   ├── 💾 database/      # Database layer
│   ├── 📊 models/        # Data models
│   ├── 🎵 music/         # Music analysis
│   ├── 📝 playlists/     # Playlist management
│   └── 🔌 websockets/    # Real-time features
├── 🧪 tests/             # Test suite
├── 📦 alembic/           # Database migrations
└── 📄 requirements.txt   # Dependencies
```

### 🧪 Testing

**Run All Tests:**
```bash
pytest                 # 🧪 All tests
pytest --cov=app      # 📊 With coverage
```

**Specific Test Categories:**
```bash
pytest tests/auth/    # 🔑 Auth tests
pytest tests/models/  # 📊 Model tests
pytest -m unit        # 🎯 Unit tests
```

### 📚 API Documentation

Once running, explore the API at:
- 🔍 Swagger UI: `http://localhost:8000/docs`
- 📖 ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

We love your input! Check out our [Contributing Guidelines](CONTRIBUTING.md) for ways to contribute.

1. 🍴 Fork the repo
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit changes (`git commit -m 'Add AmazingFeature'`)
4. 📤 Push to branch (`git push origin feature/AmazingFeature`)
5. 🎁 Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- 🎵 Spotify Web API
- 🚀 FastAPI Framework
- 💾 SQLAlchemy ORM
- 🔄 Redis

---

<p align="center">
Made with ❤️ by the Alma Team
</p>

<p align="center">
<a href="https://github.com/yourusername/alma/stargazers">⭐ Star us on GitHub</a>
