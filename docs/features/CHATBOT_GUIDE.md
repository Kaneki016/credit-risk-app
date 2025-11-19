# Chatbot Guide

## Overview

The Credit Risk Assistant is an AI-powered chatbot that helps you interact with your database and understand your system. It's always available in the bottom-right corner of the screen.

---

## 🤖 Features

### What the Chatbot Can Do:

1. **📊 Database Statistics**
   - Total predictions
   - Risk distribution
   - Application counts
   - Feedback statistics

2. **🔍 Recent Predictions**
   - Last 5 predictions
   - Risk levels
   - Timestamps
   - Probability scores

3. **📈 Model Performance**
   - Training data status
   - Retraining readiness
   - Feedback ratio
   - Sample requirements

4. **❓ Help & Guidance**
   - How to import data
   - How to retrain model
   - How to use features
   - System tutorials

---

## 🚀 How to Use

### Opening the Chatbot

1. Look for the **💬** button in the bottom-right corner
2. Click it to open the chat window
3. Start asking questions!

### Quick Actions

When you first open the chatbot, you'll see quick action buttons:
- **📊 Database Stats** - View database statistics
- **🔍 Recent Predictions** - See latest predictions
- **📈 Model Performance** - Check model status
- **❓ Help** - Get usage instructions

Click any button for instant answers!

---

## 💬 Example Questions

### Database Queries

```
"show database statistics"
"how many predictions do I have?"
"what's in my database?"
"show me the stats"
```

**Response:**
- Total predictions
- High/Low risk counts
- Applications status
- Feedback counts

---

### Recent Activity

```
"show recent predictions"
"what are the latest predictions?"
"show me the last predictions"
"recent activity"
```

**Response:**
- Last 5 predictions
- Risk levels
- Probabilities
- Timestamps

---

### Model Information

```
"show model performance"
"is my model ready to retrain?"
"model metrics"
"training status"
```

**Response:**
- Training data count
- Feedback ratio
- Retraining readiness
- Requirements status

---

### Help & Tutorials

```
"help"
"how do I use this?"
"how to import data?"
"how to retrain model?"
"guide"
```

**Response:**
- Step-by-step instructions
- Feature explanations
- Best practices
- Quick tips

---

## 🎨 Chatbot Interface

### Components:

**Header:**
- 🤖 Avatar
- Title: "Credit Risk Assistant"
- Subtitle: "Ask me anything about your data"
- Close button (✕)

**Messages Area:**
- Your messages (right side, purple)
- Bot responses (left side, white)
- Timestamps
- Data displays (when applicable)

**Quick Actions:**
- Appear on first open
- One-click queries
- Common questions

**Input Area:**
- Text input field
- Send button (➤)
- Press Enter to send
- Shift+Enter for new line

---

## 📊 Response Types

### Text Responses
Simple text answers with formatting:
```
📊 Database Statistics
• Total: 32,631
• High Risk: 20 (40%)
• Low Risk: 30 (60%)
```

### Data Responses
Structured data with key-value pairs:
```
predictions: 32631
high_risk: 20
low_risk: 30
with_feedback: 32581
```

### Help Responses
Step-by-step instructions:
```
1. Click "Admin" button
2. Go to "Import Data" tab
3. Upload CSV file
4. Click "Import"
```

---

## 🎯 Use Cases

### 1. Quick Status Check
**Scenario:** You want to know how much data you have

**Ask:** "show database statistics"

**Get:**
- Total predictions
- Risk distribution
- Application counts
- Feedback status

---

### 2. Monitor Recent Activity
**Scenario:** Check if predictions are being made

**Ask:** "show recent predictions"

**Get:**
- Last 5 predictions
- Risk levels
- Timestamps
- Quick overview

---

### 3. Check Retraining Readiness
**Scenario:** Want to know if you can retrain

**Ask:** "show model performance"

**Get:**
- Current data count
- Feedback ratio
- Ready status
- Requirements

---

### 4. Learn How to Use Features
**Scenario:** New user needs guidance

**Ask:** "how do I import data?"

**Get:**
- Step-by-step guide
- Requirements
- Best practices
- Next steps

---

## 💡 Tips & Tricks

### Natural Language
The chatbot understands natural language:
- ✅ "show me the database stats"
- ✅ "what's in my database?"
- ✅ "how many predictions?"
- ✅ "stats please"

All work the same way!

### Keywords
Key words that trigger responses:
- **Database:** stats, statistics, how many, database
- **Predictions:** recent, latest, last, predictions
- **Model:** model, performance, accuracy, metrics
- **Help:** help, how, use, guide, tutorial
- **Import:** import, upload, csv
- **Retrain:** retrain, training, train model

### Quick Actions
Use quick action buttons for:
- Faster access
- Common queries
- No typing needed
- Instant results

### Conversation Flow
The chatbot remembers context:
1. Ask "show database statistics"
2. Then ask "how do I add more data?"
3. Get relevant import instructions

---

## 🎨 Customization

### Position
- Fixed bottom-right corner
- Always accessible
- Doesn't block content
- Responsive on mobile

### Appearance
- Purple gradient theme
- Smooth animations
- Clean, modern design
- Easy to read

### Behavior
- Opens/closes smoothly
- Auto-scrolls to latest message
- Shows typing indicator
- Timestamps on messages

---

## 📱 Mobile Support

### Responsive Design
- Full-screen on mobile
- Touch-friendly buttons
- Optimized layout
- Easy typing

### Mobile Features
- Swipe to close
- Tap to open
- Large touch targets
- Readable text

---

## 🔧 Technical Details

### API Endpoint
```
POST /chatbot/query
Body: { "query": "your question" }
```

### Response Format
```json
{
  "response": "Text response",
  "data": {
    "key": "value"
  }
}
```

### Query Processing
1. Receives user query
2. Analyzes keywords
3. Fetches relevant data
4. Formats response
5. Returns to frontend

---

## 🆘 Troubleshooting

### Chatbot Not Responding
**Problem:** No response after sending message

**Solutions:**
- Check backend is running
- Verify API endpoint: http://localhost:8000
- Check browser console for errors
- Refresh the page

### "Error" Message
**Problem:** Chatbot shows error message

**Solutions:**
- Ensure database is connected
- Check if data exists
- Verify API is accessible
- Check logs for details

### Button Not Appearing
**Problem:** Can't see chat button

**Solutions:**
- Check if page is fully loaded
- Look in bottom-right corner
- Try refreshing page
- Check browser zoom level

---

## 📚 Example Conversations

### Conversation 1: New User
```
User: "help"
Bot: Shows complete help guide

User: "how do I import data?"
Bot: Shows import instructions

User: "show database statistics"
Bot: Shows current stats (0 predictions)

User: "thanks!"
Bot: Provides encouragement
```

### Conversation 2: Checking Status
```
User: "show database statistics"
Bot: 32,631 predictions, 99% feedback

User: "show model performance"
Bot: Ready to retrain, 32,581 samples

User: "how do I retrain?"
Bot: Shows retraining steps
```

### Conversation 3: Monitoring
```
User: "show recent predictions"
Bot: Last 5 predictions with details

User: "show database statistics"
Bot: Complete database overview

User: "is everything working?"
Bot: Confirms system status
```

---

## 🎯 Best Practices

### For Users
1. **Start with quick actions** - Fastest way to get info
2. **Use natural language** - No need for exact commands
3. **Ask follow-up questions** - Build on previous answers
4. **Check regularly** - Monitor your system status

### For Admins
1. **Use for monitoring** - Quick status checks
2. **Guide new users** - Point them to chatbot
3. **Check before retraining** - Verify readiness
4. **Monitor activity** - Track recent predictions

---

## 🚀 Future Enhancements

Potential future features:
- 🔮 Prediction insights
- 📊 Data visualization
- 🔔 Proactive notifications
- 📈 Trend analysis
- 🎯 Personalized recommendations
- 🔍 Advanced search
- 📝 Export conversations
- 🌐 Multi-language support

---

## 📝 Quick Reference

| Question | Response |
|----------|----------|
| "show database statistics" | Database overview |
| "show recent predictions" | Last 5 predictions |
| "show model performance" | Training status |
| "help" | Complete guide |
| "how do I import data?" | Import instructions |
| "how do I retrain?" | Retraining steps |

---

## ✅ Summary

The chatbot provides:
- ✅ Instant database insights
- ✅ Recent activity monitoring
- ✅ Model status checking
- ✅ Interactive help system
- ✅ Natural language interface
- ✅ Always accessible
- ✅ Mobile-friendly

**Your AI assistant is ready to help!** 🤖

Just click the 💬 button and start asking questions!
