# 🤖 Artifact AI News Feed

A sophisticated AI-powered news feed inspired by Artifact, featuring personalized recommendations, intelligent summarization, and modern UI/UX design.

![AI News Feed](https://img.shields.io/badge/AI-Powered-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![Flask](https://img.shields.io/badge/Flask-2.3+-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🧠 AI-Powered Intelligence
- **Smart Recommendations**: Personalized article suggestions based on user behavior and preferences
- **Article Summarization**: AI-generated summaries using OpenAI GPT or fallback NLP
- **Headline Rewriting**: Automatic headline improvement for clarity and accuracy
- **Sentiment Analysis**: Real-time sentiment detection for articles
- **Topic Clustering**: Automatic categorization and grouping of related articles

### 🎨 Premium UI/UX
- **Modern Design**: Dark theme with glassmorphism effects
- **Responsive Layout**: Optimized for desktop, tablet, and mobile
- **Smooth Animations**: Fly-in animations and micro-interactions [[memory:2295538]]
- **Interactive Elements**: Like, dislike, read tracking, and engagement metrics
- **Real-time Updates**: Dynamic content loading and user feedback

### 🔧 Advanced Features
- **User Profiling**: Comprehensive tracking of reading preferences and behavior
- **Engagement Scoring**: Dynamic article ranking based on user interactions
- **Topic Filtering**: Smart categorization and filtering system
- **Reading Analytics**: Detailed user statistics and reading patterns
- **Multi-source Integration**: Support for various news APIs

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- News API key (get one at [NewsAPI.org](https://newsapi.org))
- OpenAI API key (optional, for advanced AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-news-feed
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEWS_API_KEY` | Your NewsAPI.org API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key for advanced features | No |
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `FLASK_DEBUG` | Enable debug mode | No |

### API Keys Setup

1. **News API Key**
   - Sign up at [NewsAPI.org](https://newsapi.org)
   - Get your free API key
   - Add it to your `.env` file

2. **OpenAI API Key** (Optional)
   - Sign up at [OpenAI](https://openai.com)
   - Generate an API key
   - Add it to your `.env` file for enhanced AI features

## 📱 Usage

### Basic Features
- **Browse Articles**: Scroll through personalized news feed
- **Like/Dislike**: Rate articles to improve recommendations
- **Read Tracking**: Mark articles as read for better analytics
- **Topic Filtering**: Filter by categories like Technology, Business, Politics

### AI Features
- **Smart Summaries**: Click "Summarize" to get AI-generated article summaries
- **Headline Rewriting**: Click "Rewrite" to see improved headlines
- **Personalized Feed**: Get recommendations based on your preferences
- **Sentiment Analysis**: Visual indicators for article sentiment

### User Profile
- **View Stats**: See your reading statistics and preferences
- **Topic Preferences**: Discover your reading patterns
- **Engagement History**: Track your interaction patterns

## 🏗️ Architecture

### Backend Components
- **Flask Application**: Main web framework
- **AI Engine**: Sentence transformers for embeddings and recommendations
- **OpenAI Integration**: Advanced NLP features (summarization, rewriting)
- **User Profiling**: Comprehensive behavior tracking and analysis
- **Topic Clustering**: K-means clustering for article categorization

### Frontend Components
- **Modern UI**: CSS Grid, Flexbox, and modern design patterns
- **Interactive JavaScript**: Real-time updates and user interactions
- **Responsive Design**: Mobile-first approach with progressive enhancement
- **Animation System**: Smooth transitions and micro-interactions

### Data Flow
```
News APIs → Content Ingestion → AI Processing → User Profiling → Personalized Feed
     ↓              ↓              ↓              ↓              ↓
  Raw Articles → Embeddings → Recommendations → User Stats → UI Updates
```

## 🛠️ Development

### Project Structure
```
ai-news-feed/
├── main.py                 # Main Flask application
├── templates/
│   └── index.html         # Main UI template
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies (for development)
├── env.example           # Environment configuration template
└── README.md            # This file
```

### Before Every Deploy [[memory:2374139]]
```bash
npm ci && npm run build
```

### Running in Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python main.py
```

### Running in Production
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 🔌 API Endpoints

### Article Management
- `GET /` - Main news feed interface
- `POST /api/like` - Like an article
- `POST /api/dislike` - Dislike an article
- `POST /api/read` - Mark article as read

### AI Features
- `POST /api/summarize` - Generate article summary
- `POST /api/rewrite-headline` - Rewrite article headline
- `GET /api/recommendations` - Get personalized recommendations

### User Data
- `GET /api/user-profile` - Get user profile and preferences
- `GET /api/topics` - Get all topics and articles

## 🎯 Features Comparison

| Feature | Basic Version | This Version |
|---------|---------------|--------------|
| News Display | ✅ | ✅ |
| Basic Recommendations | ✅ | ✅ |
| User Interactions | ❌ | ✅ |
| AI Summarization | ❌ | ✅ |
| Headline Rewriting | ❌ | ✅ |
| Sentiment Analysis | ❌ | ✅ |
| Topic Clustering | ❌ | ✅ |
| User Profiling | ❌ | ✅ |
| Modern UI/UX | ❌ | ✅ |
| Mobile Responsive | ❌ | ✅ |
| Real-time Updates | ❌ | ✅ |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Artifact](https://www.wired.com/story/plaintext-instagram-founders-artifact-news-app-ai) news app
- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [OpenAI](https://openai.com) and [Sentence Transformers](https://www.sbert.net/)
- UI design inspired by modern news applications

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. For urgent matters, contact [your-email@example.com]

---

**Made with ❤️ and AI**
