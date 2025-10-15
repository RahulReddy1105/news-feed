# 🚀 Installation Guide - AI News Feed

## ✅ **SOLUTION TO YOUR INSTALLATION ERROR**

The error you encountered was due to `scikit-learn` requiring Microsoft Visual C++ 14.0 to compile from source on Windows. I've created multiple solutions for you:

## 🎯 **Option 1: Simple Version (RECOMMENDED - Already Working!)**

The simple version is already running successfully on your system! It includes all the core features without the heavy ML dependencies.

### What's Running:
- ✅ **Modern UI/UX** - Beautiful dark theme with animations
- ✅ **AI-Powered Features** - Simple sentiment analysis and topic extraction
- ✅ **User Interactions** - Like, dislike, read tracking
- ✅ **Recommendations** - Topic-based personalized recommendations
- ✅ **Article Summarization** - Simple extractive summarization
- ✅ **Responsive Design** - Works on all devices

### Access Your App:
🌐 **Open your browser to: http://localhost:5000**

## 🔧 **Option 2: Full Version with Advanced AI**

If you want the full advanced AI features, here are the solutions:

### Solution A: Install Pre-compiled Wheels
```bash
# Try installing with pre-compiled wheels
pip install scikit-learn --only-binary=all

# Then install the full requirements
pip install -r requirements-windows.txt
```

### Solution B: Install Visual Studio Build Tools
1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install "C++ build tools" workload
3. Then run: `pip install -r requirements.txt`

### Solution C: Use Conda (Alternative)
```bash
# Install Anaconda/Miniconda first, then:
conda install scikit-learn numpy pandas
pip install -r requirements.txt
```

## 🎮 **How to Use Your App**

### **Current Features (Simple Version):**
1. **Browse Articles** - Scroll through personalized news feed
2. **Like/Dislike** - Rate articles to improve recommendations
3. **Read Tracking** - Mark articles as read
4. **AI Summaries** - Click "Summarize" button on any article
5. **Headline Rewriting** - Click "Rewrite" for improved headlines
6. **Topic Filtering** - Use navigation to filter by category
7. **User Profile** - Click profile button to see your stats

### **Navigation:**
- **All Stories** - View all articles
- **For You** - Personalized recommendations
- **Trending** - Popular articles
- **Technology/Business/Politics** - Category filters

### **Article Actions:**
- ❤️ **Like** - Improves recommendations
- 👎 **Dislike** - Helps filter content
- 📖 **Summarize** - AI-generated summary
- ✏️ **Rewrite** - Improved headline
- ✅ **Mark Read** - Track reading progress

## 🛠️ **Configuration**

### **Set Up Your News API Key:**
1. Get a free API key from [NewsAPI.org](https://newsapi.org)
2. Create a `.env` file in your project directory:
```env
NEWS_API_KEY=your_actual_api_key_here
SECRET_KEY=your_secret_key_here
```

### **Optional: OpenAI API Key (for advanced features)**
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 📱 **Features Comparison**

| Feature | Simple Version | Full Version |
|---------|---------------|--------------|
| News Display | ✅ | ✅ |
| Modern UI | ✅ | ✅ |
| User Interactions | ✅ | ✅ |
| Basic AI Summarization | ✅ | ✅ |
| Simple Recommendations | ✅ | ✅ |
| Sentiment Analysis | ✅ (Simple) | ✅ (Advanced) |
| Topic Extraction | ✅ (Simple) | ✅ (Advanced) |
| OpenAI Integration | ❌ | ✅ |
| Advanced ML | ❌ | ✅ |
| Topic Clustering | ❌ | ✅ |

## 🚀 **Running the App**

### **Simple Version (Currently Running):**
```bash
python main-simple.py
```

### **Full Version (After fixing dependencies):**
```bash
python main.py
```

## 🔧 **Troubleshooting**

### **If you get import errors:**
```bash
# Make sure you're in the right directory
cd "C:\Users\Thilak\Downloads\AI-based news feed"

# Install simple requirements
pip install -r requirements-simple.txt

# Run simple version
python main-simple.py
```

### **If port 5000 is busy:**
```python
# Edit main-simple.py or main.py, change the last line to:
app.run(debug=True, port=5001)
```

### **If you want to stop the app:**
- Press `Ctrl+C` in the terminal

## 🎉 **You're All Set!**

Your AI News Feed is now running with:
- ✅ **Modern, professional UI**
- ✅ **AI-powered features**
- ✅ **Personalized recommendations**
- ✅ **User interaction tracking**
- ✅ **Responsive design**

**Access it at: http://localhost:5000**

## 📞 **Need Help?**

If you encounter any issues:
1. Make sure you have a valid News API key
2. Check that all dependencies are installed
3. Try the simple version first: `python main-simple.py`
4. Check the terminal for any error messages

**Your app is working perfectly! Enjoy your AI-powered news feed! 🎉**

