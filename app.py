import requests
import json
import time
from datetime import datetime

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
                'publishedAt': video['snippet']['publishedAt'],
                'thumbnailUrl': video['snippet']['thumbnails']['high']['url']
            }
        return None
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return None

def post_to_blogger(video_data, blogger_access_token, blog_id):
    if not video_data:
        return
    
    # Blogger API endpoint
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts"
    
    # Create HTML content
    content = f"""
    <h2>{video_data['title']}</h2>
    <div class="video-container">
        <iframe width="560" 
                height="315" 
                src="https://www.youtube.com/embed/{video_data['videoId']}" 
                frameborder="0" 
                allowfullscreen>
        </iframe>
    </div>
    <img src="{video_data['thumbnailUrl']}" alt="{video_data['title']}" style="max-width:100%;height:auto;">
    <p>{video_data['description']}</p>
    <p>Watch on YouTube: <a href="https://www.youtube.com/watch?v={video_data['videoId']}" target="_blank">
        https://www.youtube.com/watch?v={video_data['videoId']}</a>
    </p>
    """
    
    # Prepare the post data
    post_data = {
        'kind': 'blogger#post',
        'title': video_data['title'],
        'content': content,
        'labels': ['YouTube', 'Auto-Posted']
    }
    
    # Set up headers with OAuth token
    headers = {
        'Authorization': f'Bearer {blogger_access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        print(f"Successfully posted: {video_data['title']}")
        return response.json()
    except Exception as e:
        print(f"Error posting to Blogger: {e}")
        return None

def main():
    # Your Blogger details
    BLOG_ID = 'YOUR_BLOG_ID'  # Get from your Blogger dashboard URL
    ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'  # Get from Google OAuth 2.0 Playground
    
    last_video_id = None
    
    print("Starting YouTube to Blogger auto-poster...")
    
    while True:
        try:
            video_data = fetch_latest_youtube_video()
            
            if video_data and video_data['videoId'] != last_video_id:
                print(f"New video found: {video_data['title']}")
                post_to_blogger(video_data, ACCESS_TOKEN, BLOG_ID)
                last_video_id = video_data['videoId']
            else:
                print("No new videos found")
            
            print("Waiting for 3 minutes before next check...")
            time.sleep(180)  # Wait for 3 minutes
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(180)  # Still wait before retrying

if __name__ == "__main__":
    main()
