import os
import json
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

analyzer = SentimentIntensityAnalyzer()
KEYSTROKE_FILE = "keystrokes.txt"

THRESHOLD = -0.1  # Updated threshold here as per your requirement
ALERT_LIMIT = 5    # Updated alert limit

ALERT_STATUS_FILE = "alert_status.json"

# Load and score last line

def get_latest_mood():
    if not os.path.exists(KEYSTROKE_FILE):
        return 0.0
    with open(KEYSTROKE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return 0.0
        last_line = lines[-1].strip()
        score = analyzer.polarity_scores(last_line)['compound']
        return score

# Analyze all keystrokes as history

def get_day_analysis():
    if not os.path.exists(KEYSTROKE_FILE):
        return []
    result = []
    with open(KEYSTROKE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            score = analyzer.polarity_scores(line)['compound']
            timestamp = datetime.now().isoformat()
            result.append((timestamp, score))
    return result


def get_alert_status():
    if os.path.exists(ALERT_STATUS_FILE):
        with open(ALERT_STATUS_FILE, "r") as f:
            return json.load(f)
    return {"last_alert_line": 0}

def set_alert_status(line_num):
    status = {"last_alert_line": line_num}
    with open(ALERT_STATUS_FILE, "w") as f:
        json.dump(status, f)

def count_below_threshold(return_lines=False):
    if not os.path.exists(KEYSTROKE_FILE):
        return (0, 0, []) if return_lines else (0, 0)
    count = 0
    lines = []
    neg_lines = []
    with open(KEYSTROKE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    status = get_alert_status()
    start = status.get("last_alert_line", 0)
    for i, line in enumerate(lines[start:], start):
        line = line.strip()
        print("LINE VAR: ", line)
        if not line:
            continue
        score = analyzer.polarity_scores(line)['compound']
        print(score, flush=True)
        if score < THRESHOLD:
            count += 1
            neg_lines.append(line)
    if return_lines:
        return count, len(lines), neg_lines
    else:
        return count, len(lines)

def reset_alert_status():
    status = {"last_alert_line": 0}
    with open(ALERT_STATUS_FILE, "w") as f:
        json.dump(status, f)