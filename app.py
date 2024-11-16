import requests
import json
import time
from datetime import datetime

YOUTUBE_API_KEY = "AIzaSyDwHs4dou-4hLfcEfCbekg3VUoOO18VGks"
BLOG_ID = "1050468214587466272"
ACCESS_TOKEN = "ya29.a0AeDClZCy1WLDEENeBtm6_QMC7NASa94ikF__KE6dp84z0fh1hT3NZi1NOMasMBP1ALZIlOqbR4XasKdLg4B9NKvafZWlU16V-OD3IcI6-kgr2rECqfXutPLJBYsQXcUVnte67OYU1Vzp1WMunNYIeIzPGpfNOJ6ieyEsPR25aCgYKARUSARISFQHGX2MiZ-LVW8ReZFPorcX-cZl-qQ0175"
CHANNEL_ID = "UC-JFyL0zDFOsPMpuWu39rPA"

def fetch_latest_youtube_video():
    api_url = "https://youtube.googleapis.com/youtube/v3/search"
    current_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    params = {
        "part": "snippet",
        "channelId": CHANNEL_ID,
        "type": "video",
        "maxResults": 1,
        "order": "date",
        "publishedAfter": "2024-11-16T00:00:00Z",
        "key": YOUTUBE_API_KEY
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
        print("No videos found in response:", data)
        return None
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        if 'response' in locals():
            print("Response content:", response.text)
        return None

def post_to_blogger(video_data):
    if not video_data:
        return
    
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts"
    
    content = f"""
    <h2>{video_data['title']}</h2>
    <div class="video-container">
        <iframe width="560" 
                height="315" 
                src="https://www.youtube.com/embed/{video_data['videoId']}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
        </iframe>
    </div>
    <img src="{video_data['thumbnailUrl']}" alt="{video_data['title']}" style="max-width:100%;height:auto;">
    <p>{video_data['description']}</p>
    <p>Watch on YouTube: <a href="https://www.youtube.com/watch?v={video_data['videoId']}" target="_blank">
        https://www.youtube.com/watch?v={video_data['videoId']}</a>
    </p>
    """
    
    post_data = {
        'kind': 'blogger#post',
        'title': video_data['title'],
        'content': content,
        'labels': ['YouTube', 'Auto-Posted']
    }
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        print(f"Successfully posted: {video_data['title']}")
        return response.json()
    except Exception as e:
        print(f"Error posting to Blogger: {e}")
        print("Response content:", response.text if 'response' in locals() else "No response")
        return None

def check_token_validity():
    test_url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}"
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    
    try:
        response = requests.get(test_url, headers=headers)
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting YouTube to Blogger auto-poster...")
    
    # First check if token is valid
    if not check_token_validity():
        print("ERROR: Access token is invalid or expired. Please get a new access token.")
        return
    
    last_video_id = None
    error_count = 0
    
    while True:
        try:
            print("\nChecking for new videos...")
            video_data = fetch_latest_youtube_video()
            
            if video_data and video_data['videoId'] != last_video_id:
                print(f"New video found: {video_data['title']}")
                if post_to_blogger(video_data):
                    last_video_id = video_data['videoId']
                    error_count = 0
            else:
                print("No new videos found")
            
            # If too many errors occur, stop the script
            if error_count >= 5:
                print("Too many errors occurred. Stopping script.")
                break
                
            print("Waiting for 3 minutes before next check...")
            time.sleep(180)  # Wait for 3 minutes
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            error_count += 1
            time.sleep(180)  # Still wait before retrying

if __name__ == "__main__":
    main()
