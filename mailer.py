import smtplib
from email.mime.text import MIMEText

def send_alert_email(to_addr, count):
    from_addr = "gameison2006@gmail.com"
    app_password = "xrqf jwis bcfn okdz"  

    message_body = (
        f"Dear Guardian,\n\n"
        f"This is an automated alert from MindTrackAI.\n\n"
        f"The user's mood sentiment score dropped below -0.5 a total of {count} times recently. "
        f"This may indicate a period of sustained low mood or distress.\n\n"
        f"Please consider reaching out to check in and offer support.\n\n"
        f"If you have questions or need more information, please let us know.\n\n"
        f"Best regards,\n"
        f"MindTrackAI"
    )

    msg = MIMEText(message_body)
    msg["Subject"] = "MindTrackAI Alert: Mood Threshold Reached"
    msg["From"] = from_addr
    msg["To"] = to_addr

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_addr, app_password)
        server.send_message(msg)
