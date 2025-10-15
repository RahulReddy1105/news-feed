from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import requests
import openai
import nltk
from textblob import TextBlob
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import json
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# Initialize AI models
model = SentenceTransformer('all-MiniLM-L6-v2')
openai.api_key = os.getenv('OPENAI_API_KEY', '')

# News API configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'b8c7xxxxxxxxxxxxxxxxxxxxx')
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

# Advanced storage with user sessions and caching
articles = []
user_profiles = {}
article_embeddings = None
topic_clusters = {}
article_metadata = {}

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Advanced AI Functions
def generate_article_summary(content, max_length=1200):
    """Generate AI-powered article summary"""
    try:
        # Target character limit: prefer 1200 (over 1000) unless overridden
        limit_chars = max_length if max_length else 1200
        # Safety cap
        if limit_chars > 2000:
            limit_chars = 2000

        # Use OpenAI if available to produce a simple-language summary
        if openai.api_key:
            prompt = (
                "You are a helpful assistant that summarizes news articles in very simple, plain English. "
                f"Create a concise, easy-to-read summary using short sentences, avoid jargon, and keep the summary under {limit_chars} characters. "
                "Do not include the source name or extra commentary. Be factual and neutral.\n\nArticle:\n" + content
            )
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.2,
            )
            summary = resp.choices[0].message.content.strip()
            if len(summary) > limit_chars:
                summary = summary[:limit_chars].rsplit(' ', 1)[0] + '...'
            return summary

        # Fallback: basic extractive summarization using sentence tokens up to limit_chars
        clean = re.sub(r"\s+", " ", content).strip()
        sentences = nltk.sent_tokenize(clean)
        if not sentences:
            return ""
        out = ""
        for s in sentences:
            if len(out) + len(s) + 1 > limit_chars:
                break
            out = (out + " " + s).strip()
        if not out:
            out = sentences[0][:limit_chars]
        return out if len(out) <= limit_chars else out[:limit_chars].rsplit(' ', 1)[0] + '...'
    except Exception:
        # Last-resort fallback
        try:
            sentences = nltk.sent_tokenize(content)
            if not sentences:
                return ""
            fallback = sentences[0][:limit_chars]
            return fallback + ('...' if len(fallback) >= limit_chars else '')
        except Exception:
            return ""

def rewrite_headline(headline):
    """Rewrite misleading or unclear headlines using AI"""
    try:
        # Remove trailing source fragments like " - ABC News - Breaking News..."
        cleaned = re.split(r"\s-\s[A-Za-z0-9].*$", headline)[0]
        cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", cleaned).strip()

        # If OpenAI is available, ask for a short simple headline (10 words max)
        if openai.api_key:
            prompt = (
                "You are a headline editor. Rewrite the following headline to be short (10 words max), clear, neutral, and use simple words. "
                "Do not include the news source or tags. Keep it under 80 characters.\n\nHeadline:\n" + cleaned
            )
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=40,
                temperature=0.2,
            )
            result = resp.choices[0].message.content.strip()
            result = re.sub(r"\s-\s.*$", "", result).strip()
            if len(result) > 120:
                result = result[:120].rsplit(' ', 1)[0] + '...'
            return result

        # Heuristic fallback: take up to 10 words and 80 chars
        short = re.sub(r"\s+", " ", cleaned)
        words = short.split()
        if len(words) > 10:
            short = " ".join(words[:10]) + "..."
        if len(short) > 80:
            short = short[:80].rsplit(' ', 1)[0] + '...'
        return short
    except Exception as e:
        return headline

def analyze_sentiment(text):
    """Analyze sentiment of article content"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def extract_key_topics(content):
    """Extract key topics from article content"""
    blob = TextBlob(content)
    # Extract noun phrases as potential topics
    topics = [phrase for phrase in blob.noun_phrases if len(phrase.split()) <= 3]
    return topics[:5]  # Return top 5 topics

def cluster_articles_by_topic():
    """Cluster articles by topic using embeddings"""
    global topic_clusters, article_embeddings
    
    if not articles or len(articles) < 3:
        return
    
    try:
        # Generate embeddings for all articles
        article_texts = [a["content"] for a in articles]
        article_embeddings = model.encode(article_texts)
        
        # Perform K-means clustering
        n_clusters = min(5, len(articles) // 2)  # Adaptive number of clusters
        if n_clusters < 2:
            n_clusters = 2
            
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(article_embeddings)
        
        # Group articles by cluster
        topic_clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in topic_clusters:
                topic_clusters[label] = []
            topic_clusters[label].append(i)
            
    except Exception as e:
        print(f"Clustering error: {e}")

# Enhanced news fetching with AI processing
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
        
        # Process articles with AI features
        articles = []
        for article in raw_articles:
            # Generate summary
            summary = generate_article_summary(article["content"])
            
            # Analyze sentiment
            sentiment = analyze_sentiment(article["content"])
            
            # Extract topics
            topics = extract_key_topics(article["content"])
            
            # Store metadata
            article_metadata[article["id"]] = {
                "summary": summary,
                "sentiment": sentiment,
                "topics": topics,
                "read_time": len(article["content"].split()) // 200 + 1,  # Estimate read time
                "engagement_score": 0.5  # Default engagement score
            }
            
            # Enhanced article object
            # Preserve original title, and generate a short rewritten headline for display
            short_title = rewrite_headline(article["title"]) if article.get("title") else article.get("title")
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
        
        # Cluster articles by topic
        cluster_articles_by_topic()
        
        return articles
    except Exception as e:
        articles = []
        return str(e)

# Advanced recommendation engine
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
                
    elif action == "dislike":
        if article_id not in profile["disliked_articles"]:
            profile["disliked_articles"].append(article_id)
            
    elif action == "read":
        if article_id not in profile["read_articles"]:
            profile["read_articles"].append(article_id)
            if article_id in article_metadata:
                read_time = article_metadata[article_id]["read_time"]
                profile["reading_time_preferences"].append(read_time)

def generate_smart_recommendations(user_id, limit=10):
    """Generate intelligent recommendations using multiple signals"""
    profile = get_user_profile(user_id)
    
    if not profile["liked_articles"] and not profile["read_articles"]:
        # New user: return diverse, trending articles
        return get_diverse_recommendations(limit)
    
    try:
        # Content-based filtering using embeddings
        if profile["liked_articles"]:
            liked_content = []
            for article_id in profile["liked_articles"]:
                article = next((a for a in articles if a["id"] == article_id), None)
                if article:
                    liked_content.append(article["content"])
            
            if liked_content:
                liked_embeddings = model.encode(liked_content)
                user_embedding = liked_embeddings.mean(axis=0).reshape(1, -1)
                
                # Compute similarities
                article_texts = [a["content"] for a in articles]
                article_embeddings = model.encode(article_texts)
                similarities = cosine_similarity(user_embedding, article_embeddings)[0]
                
                # Apply topic and sentiment preferences
                scored_articles = []
                for i, article in enumerate(articles):
                    score = similarities[i]
                    
                    # Boost score based on topic preferences
                    for topic in article["topics"]:
                        score += profile["topic_preferences"].get(topic, 0) * 0.1
                    
                    # Boost score based on sentiment preferences
                    sentiment = article["sentiment"]
                    sentiment_boost = profile["sentiment_preferences"].get(sentiment, 0) * 0.05
                    score += sentiment_boost
                    
                    # Penalize disliked articles
                    if article["id"] in profile["disliked_articles"]:
                        score -= 0.5
                    
                    # Penalize already seen articles
                    if article["id"] in profile["read_articles"]:
                        score -= 0.3
                    
                    scored_articles.append((score, article))
                
                # Sort by score and return top recommendations
                scored_articles.sort(key=lambda x: x[0], reverse=True)
                return [article for score, article in scored_articles[:limit]]
        
    except Exception as e:
        print(f"Recommendation error: {e}")
    
    return get_diverse_recommendations(limit)

def get_diverse_recommendations(limit):
    """Get diverse recommendations across different topics"""
    if not topic_clusters:
        return articles[:limit]
    
    recommendations = []
    articles_per_cluster = limit // len(topic_clusters)
    
    for cluster_id, article_indices in topic_clusters.items():
        cluster_articles = [articles[i] for i in article_indices]
        # Sort by engagement score and take top articles
        cluster_articles.sort(key=lambda x: x["engagement_score"], reverse=True)
        recommendations.extend(cluster_articles[:articles_per_cluster])
    
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
    
    return render_template('index.html', 
                         articles=articles, 
                         error=error,
                         topic_clusters=topic_clusters,
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
    
    recommendations = generate_smart_recommendations(user_id, limit)
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
    
    summary = generate_article_summary(article["content"])
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
    
    rewritten = rewrite_headline(article["title"])
    return jsonify({"original": article["title"], "rewritten": rewritten})

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get all topics and their articles"""
    topics_dict = {}
    for article in articles:
        for topic in article["topics"]:
            if topic not in topics_dict:
                topics_dict[topic] = []
            topics_dict[topic].append(article)
    
    return jsonify(topics_dict)

@app.route('/api/user-profile', methods=['GET'])
def get_user_profile_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No user session"}), 400
    
    profile = get_user_profile(user_id)
    return jsonify(profile)

if __name__ == "__main__":
    app.run(debug=True)
