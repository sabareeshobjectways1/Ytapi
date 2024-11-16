import requests
import smtplib
from email.mime.text import MIMEText
import time
from datetime import datetime
import json

def fetch_latest_youtube_video():
    api_url = "https://youtube.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": "UC-JFyL0zDFOsPMpuWu39rPA",
        "type": "video",
        "maxResults": 1,
        "order": "date",
        "publishedAfter": "2024-11-16T00:00:00Z",
        "key": "AIzaSyDwHs4dou-4hLfcEfCbekg3VUoOO18VGks"
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            video = data['items'][0]
            return {
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'videoId': video['id']['videoId'],
                'publishedAt': video['snippet']['publishedAt']
            }
        return None
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return None

def send_to_blogger(video_data, gmail_user, gmail_password):
    if not video_data:
        return
    
    recipient = "sabareeshs363.ytapi@blogger.com"
    subject = video_data['title']
    
    # Create HTML content with video embed
    body = f"""
    <h2>{video_data['title']}</h2>
    <iframe width="560" height="315" 
    src="https://www.youtube.com/embed/{video_data['videoId']}" 
    frameborder="0" allowfullscreen></iframe>
    <p>{video_data['description']}</p>
    """
    
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = recipient
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        print(f"Posted video: {video_data['title']}")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    # Replace with your Gmail credentials
    gmail_user = "your_email@gmail.com"
    gmail_password = "your_app_password"  # Use App Password, not regular password
    
    last_video_id = None
    
    while True:
        try:
            video_data = fetch_latest_youtube_video()
            
            if video_data and video_data['videoId'] != last_video_id:
                send_to_blogger(video_data, gmail_user, gmail_password)
                last_video_id = video_data['videoId']
            
            # Wait for 3 minutes
            time.sleep(180)
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(180)  # Still wait before retrying

if __name__ == "__main__":
    main()
