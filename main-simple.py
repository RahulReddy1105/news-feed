from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import requests
import hashlib
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv('file.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# News API configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '2193264622854f27b28c55487c2694d4')
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

# Debug: Print the API key (first 10 characters for security)
print(f"Using API Key: {NEWS_API_KEY[:10]}...")
print(f"News URL: {NEWS_URL[:50]}...")

# Storage for articles and user preferences
articles = []
user_profiles = {}
article_metadata = {}

# Persistent storage file
USER_DATA_FILE = 'user_data.json'

def load_user_data():
    """Load user data from JSON file"""
    global user_profiles
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                user_profiles = json.load(f)
            print(f"Loaded user data for {len(user_profiles)} users")
        else:
            user_profiles = {}
            print("No existing user data found, starting fresh")
    except Exception as e:
        print(f"Error loading user data: {e}")
        user_profiles = {}

def save_user_data():
    """Save user data to JSON file"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(user_profiles, f, indent=2)
        print(f"Saved user data for {len(user_profiles)} users")
    except Exception as e:
        print(f"Error saving user data: {e}")

# Load existing user data on startup
load_user_data()

# Simple sentiment analysis without heavy dependencies
def analyze_sentiment_simple(text):
    """Simple sentiment analysis based on keyword matching"""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'success', 'win', 'victory']
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'failure', 'lose', 'defeat', 'crisis', 'problem']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

def extract_topics_simple(text):
    """Simple topic extraction based on common keywords"""
    topics = []
    topic_keywords = {
        'technology': ['tech', 'ai', 'artificial intelligence', 'computer', 'software', 'digital'],
        'business': ['business', 'economy', 'market', 'finance', 'company', 'corporate'],
        'politics': ['politics', 'government', 'election', 'president', 'congress', 'policy'],
        'sports': ['sports', 'football', 'basketball', 'baseball', 'soccer', 'game'],
        'health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'treatment'],
        'entertainment': ['movie', 'music', 'celebrity', 'entertainment', 'film', 'show']
    }
    
    text_lower = text.lower()
    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.append(topic)
    
    return topics[:3]  # Return top 3 topics

def generate_summary_simple(content, max_length=1200):
    """Simple extractive summarization limited to ~1200 characters and simplified language."""
    # Basic cleaning
    clean = re.sub(r"\s+", " ", content).strip()
    sentences = clean.split('. ')
    if not sentences:
        return ""
    out = ""
    for s in sentences:
        if len(out) + len(s) + 2 > max_length:
            break
        out = (out + ". " + s).strip('.')
    if not out:
        out = sentences[0][:max_length]
    # Ensure short words and simple phrasing by truncating longer clauses
    if len(out) > max_length:
        out = out[:max_length].rsplit(' ', 1)[0] + '...'
    return out

def fetch_news():
    global articles, article_metadata
    try:
        response = requests.get(NEWS_URL)
        response.raise_for_status()
        data = response.json()
        
        raw_articles = [
            {
                "title": a["title"],
                "description": a["description"] or "",
                "url": a["url"],
                "image": a["urlToImage"] or "",
                "source": a.get("source", {}).get("name", "Unknown"),
                "publishedAt": a.get("publishedAt", ""),
                "content": (a["title"] or "") + " " + (a["description"] or ""),
                "id": hashlib.md5((a["title"] or "").encode()).hexdigest()[:8]
            }
            for a in data.get("articles", [])
            if a["title"] and a["description"]
        ]
        
        # Process articles with simple AI features
        articles = []
        for article in raw_articles:
            # Generate summary
            summary = generate_summary_simple(article["content"])
            
            # Analyze sentiment
            sentiment = analyze_sentiment_simple(article["content"])
            
            # Extract topics
            topics = extract_topics_simple(article["content"])
            
            # Store metadata
            article_metadata[article["id"]] = {
                "summary": summary,
                "sentiment": sentiment,
                "topics": topics,
                "read_time": len(article["content"].split()) // 200 + 1,
                "engagement_score": 0.5
            }
            
            # Enhanced article object
            # Preserve original title, and produce a short simplified title for display
            cleaned_title = article.get("title") or ""
            # Remove common labels
            cleaned_title = cleaned_title.replace("BREAKING:", "").replace("EXCLUSIVE:", "").strip()
            words = cleaned_title.split()
            short_title = cleaned_title if len(words) <= 10 else " ".join(words[:10]) + "..."
            if len(short_title) > 80:
                short_title = short_title[:80].rsplit(' ', 1)[0] + '...'

            enhanced_article = {
                **article,
                "original_title": article.get("title"),
                "title": short_title,
                "summary": summary,
                "sentiment": sentiment,
                "topics": topics,
                "read_time": article_metadata[article["id"]]["read_time"],
                "engagement_score": article_metadata[article["id"]]["engagement_score"]
            }
            
            articles.append(enhanced_article)
        
        return articles
    except Exception as e:
        articles = []
        return str(e)

# Simple recommendation system
def get_user_profile(user_id):
    """Get or create user profile"""
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            "liked_articles": [],
            "disliked_articles": [],
            "read_articles": [],
            "topic_preferences": {},
            "sentiment_preferences": {"positive": 0, "negative": 0, "neutral": 0},
            "reading_time_preferences": [],
            "engagement_history": []
        }
    return user_profiles[user_id]

def update_user_profile(user_id, action, article_id):
    """Update user profile based on interactions"""
    profile = get_user_profile(user_id)
    
    if action == "like":
        if article_id not in profile["liked_articles"]:
            profile["liked_articles"].append(article_id)
            # Update topic preferences
            if article_id in article_metadata:
                topics = article_metadata[article_id]["topics"]
                sentiment = article_metadata[article_id]["sentiment"]
                for topic in topics:
                    profile["topic_preferences"][topic] = profile["topic_preferences"].get(topic, 0) + 1
                profile["sentiment_preferences"][sentiment] += 1
            save_user_data()  # Save after each like
                
    elif action == "dislike":
        if article_id not in profile["disliked_articles"]:
            profile["disliked_articles"].append(article_id)
            save_user_data()  # Save after each dislike
            
    elif action == "read":
        if article_id not in profile["read_articles"]:
            profile["read_articles"].append(article_id)
            if article_id in article_metadata:
                read_time = article_metadata[article_id]["read_time"]
                profile["reading_time_preferences"].append(read_time)
            save_user_data()  # Save after each read

def generate_simple_recommendations(user_id, limit=10):
    """Generate simple recommendations based on topic preferences"""
    profile = get_user_profile(user_id)
    
    if not profile["liked_articles"]:
        # New user: return diverse articles
        return articles[:limit]
    
    # Simple topic-based recommendation
    user_topics = set()
    for article_id in profile["liked_articles"]:
        if article_id in article_metadata:
            user_topics.update(article_metadata[article_id]["topics"])
    
    recommendations = []
    for article in articles:
        article_topics = set(article["topics"])
        if user_topics.intersection(article_topics):
            recommendations.append(article)
    
    # Add some random articles for diversity
    remaining = limit - len(recommendations)
    if remaining > 0:
        for article in articles:
            if article not in recommendations and remaining > 0:
                recommendations.append(article)
                remaining -= 1
    
    return recommendations[:limit]

# Routes
@app.route('/')
def index():
    error = None
    if not articles:
        result = fetch_news()
        if isinstance(result, str):
            error = f"Error fetching news: {result}"
    
    # Get user session or create new one
    if 'user_id' not in session:
        session['user_id'] = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        session.permanent = True  # Make session permanent
    
    # Ensure user profile exists in persistent storage
    get_user_profile(session['user_id'])
    
    return render_template('index.html', 
                         articles=articles, 
                         error=error,
                         topic_clusters={},
                         user_id=session['user_id'])

@app.route('/api/like', methods=['POST'])
def like_article():
    data = request.get_json()
    article_id = data.get("article_id")
    user_id = session.get('user_id')
    
    if not user_id or not article_id:
        return jsonify({"error": "Missing user_id or article_id"}), 400
    
    update_user_profile(user_id, "like", article_id)
    
    # Update article engagement score
    article = next((a for a in articles if a["id"] == article_id), None)
    if article:
        article["engagement_score"] += 0.1
    
    return jsonify({"message": "Article liked!", "engagement_score": article["engagement_score"] if article else 0})

@app.route('/api/dislike', methods=['POST'])
def dislike_article():
    data = request.get_json()
    article_id = data.get("article_id")
    user_id = session.get('user_id')
    
    if not user_id or not article_id:
        return jsonify({"error": "Missing user_id or article_id"}), 400
    
    update_user_profile(user_id, "dislike", article_id)
    
    # Update article engagement score
    article = next((a for a in articles if a["id"] == article_id), None)
    if article:
        article["engagement_score"] -= 0.05
    
    return jsonify({"message": "Article disliked!"})

@app.route('/api/read', methods=['POST'])
def mark_as_read():
    data = request.get_json()
    article_id = data.get("article_id")
    user_id = session.get('user_id')
    
    if not user_id or not article_id:
        return jsonify({"error": "Missing user_id or article_id"}), 400
    
    update_user_profile(user_id, "read", article_id)
    return jsonify({"message": "Article marked as read!"})

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = session.get('user_id')
    limit = request.args.get('limit', 10, type=int)
    
    if not user_id:
        return jsonify({"error": "No user session"}), 400
    
    recommendations = generate_simple_recommendations(user_id, limit)
    return jsonify(recommendations)

@app.route('/api/summarize', methods=['POST'])
def summarize_article():
    data = request.get_json()
    article_id = data.get("article_id")
    
    if not article_id:
        return jsonify({"error": "Missing article_id"}), 400
    
    article = next((a for a in articles if a["id"] == article_id), None)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    
    summary = generate_summary_simple(article["content"])
    return jsonify({"summary": summary})

@app.route('/api/rewrite-headline', methods=['POST'])
def rewrite_headline_endpoint():
    data = request.get_json()
    article_id = data.get("article_id")
    
    if not article_id:
        return jsonify({"error": "Missing article_id"}), 400
    
    article = next((a for a in articles if a["id"] == article_id), None)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    
    # Simple headline improvement
    original = article["title"]
    # Basic improvements
    rewritten = original.replace("BREAKING:", "").replace("EXCLUSIVE:", "").strip()
    if rewritten != original:
        rewritten = rewritten[:100] + "..." if len(rewritten) > 100 else rewritten
    else:
        rewritten = original
    
    return jsonify({"original": original, "rewritten": rewritten})

@app.route('/api/user-profile', methods=['GET'])
def get_user_profile_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No user session"}), 400
    
    profile = get_user_profile(user_id)
    return jsonify(profile)

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """Refresh articles and user data"""
    global articles
    result = fetch_news()
    if isinstance(result, str):
        return jsonify({"error": result}), 500
    
    return jsonify({
        "message": "Data refreshed successfully",
        "article_count": len(articles)
    })

if __name__ == "__main__":
    app.run(debug=True)

