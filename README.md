# MindTrackAI

MindTrackAI is a desktop application that helps track and visualize your mood in real-time based on your daily typing activity. It offers sentiment analysis, live mood graphs, and automatic guardian alerts for mental health support—all in a friendly and modern interface.

## 🚀 Features

- **Real-time Sentiment Monitoring:** Uses a background keylogger to passively record what you type and analyze the sentiment of each new line.
- **Mood Visualization:** Live graph displays your mood trends throughout the day.
- **Guardian Alerts:** Notifies a trusted contact if negative sentiment persists, to promote mental health safety.
- **Google OAuth Authentication:** Secure login and easy access using your Google account.
- **Modern GUI:** Stylish, dark-themed interface with convenient top-bar and sidebar navigation.
- **Personalized Experience:** App adapts based on your user info and settings.

## 🛠️ Installation & Setup

1. **Clone This Repository**
   ```bash
   git clone https://github.com/yourusername/MindTrackAI.git
   cd MindTrackAI
   ```

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```
   *(You’ll need Python 3.7+)*  
   Typical dependencies: `pynput`, `nltk`, `google-auth-oauthlib`, `google-api-python-client`, `tkinter`, `matplotlib`.

3. **Google OAuth Setup**
   - Generate OAuth credentials at [Google Cloud Console](https://console.cloud.google.com/).
   - Place your downloaded `client_secret.json` in the project root.
   - Required OAuth scopes:  
     `openid`, `userinfo.profile`, `userinfo.email`

4. **Setup Gmail App Password (for alerts)**
   - For alert e-mails, you’ll need to enable [App Passwords](https://myaccount.google.com/apppasswords) for your Gmail.
   - Set your app email and password in `mailer.py`.

## 🚦 Usage

1. **Start the Application**
   ```
   python main.py
   ```

2. **Login with Google**
   - Follow the popup browser window to authenticate.
   - Your name and email will appear in the GUI.

3. **Let MindTrackAI Run!**
   - The keylogger will monitor lines you type across the OS (e.g., editors/chats).
   - Sentiment is analyzed in real time.
   - View your current mood and mood trends in the GUI.
   - If your mood drops too often below a threshold, your guardian will be notified by email.

## ⚠️ Security & Privacy

- **Keylogging Notice:** MindTrackAI records all lines you type (into `keystrokes.txt`) for mood detection. Use responsibly and don't let the app run while you're entering sensitive information
- **Credentials:** NEVER commit or share your `client_secret.json`, Gmail app password, or any sensitive info.
- **Guardian Alerts:** Alerts are sent via a backend Gmail account for simplicity; "From" appears as the current app user.

## 👨💻 Authors

Created by Sannihith Madasu, KR Keshav, Srikanth PMS and Rakesh Kumar as Team xEN Coders for Vyoma Hackathon, 2025.

## 📣 Acknowledgments

Inspired by mental health challenges and modern AI capabilities.
