# 🥊 Personal Class Signup Automation 🥋

A private Quality-of-Life project to automate signing up for martial arts classes that always fill up too quickly on Sunday releases! 💪

## 🎯 Why I Built This

Got tired of sitting ready every Sunday to sign up for next week's kickboxing classes, only to see them fill up in seconds. Instead of fast fingers, I decided to use some code! 🚀

## 🤖 How It Works

1. **Authentication** 🔐
   - Logs into the gym's website using session management
   - Maintains cookies and headers for authentic-looking requests

2. **Class Data Extraction** 📋
   - Fetches the class signup page
   - Cleans the HTML (removes scripts, styles, comments) to reduce token usage
   - Uses OpenAI to intelligently parse the cleaned HTML for class details
   - This approach is more resilient to HTML structure changes compared to fixed BeautifulSoup selectors!

3. **Smart Parsing** 🧠
   - Instead of hardcoding HTML paths or class IDs, the script uses OpenAI to understand and extract:
     - Class names
     - Schedule IDs
     - Start dates
     - Required action parameters
   - This makes the script more maintainable and resistant to website updates 

## 🔧 Setup
1. Create `.env`:
```env
WEBSITE_USERNAME=email
WEBSITE_PASSWORD=password
WEBSITE_URL=gym_url
```

2. Configure `config.yaml`:
```yaml
openai:
  model: "o3-mini-2025-01-31"

classes:
  - "Mandag fundamentals 17-18"
  - "MMA tirsdag 18-19"
  # Add your desired classes here
```

3. Run:
```bash
poetry run python classes_signup.py
```


## 💭 Technical Learning Points

This project was a fun exercise to:
- Work with `requests` library for session management
- Handle HTML parsing efficiently
- Integrate OpenAI API for intelligent data extraction
- Practice building resilient web automation tools

## ⚠️ Personal Note

This is a private QoL project, not intended for distribution. It's specifically tailored to my gym's website structure and my personal needs. 

---
Built because I love coding almost as much as I love not missing kickboxing classes! 🥊
