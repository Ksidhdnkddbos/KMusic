from youtubesearchpython import VideosSearch, PlaylistsSearch
from urllib.parse import urlparse, parse_qs
import yt_dlp
import config
import os
import asyncio
import json
import glob
import random
from typing import Tuple, Optional

def cookie_txt_file() -> str:
    """الحصول على ملف كوكيز عشوائي من مجلد cookies"""
    folder_path = os.path.join(os.getcwd(), "cookies")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the cookies folder")
    
    return random.choice(txt_files)

async def searchYt(query: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """
    بحث عن فيديو في يوتيوب وإرجاع (العنوان, المدة بالثواني, الرابط)
    """
    try:
        if not query or not query.strip():
            print("Empty search query")
            return None, None, None

        videosSearch = VideosSearch(query.strip(), limit=1)
        result = videosSearch.result()
        
        if not result or not result.get("result") or len(result["result"]) == 0:
            print(f"No results found for query: {query}")
            return None, None, None
            
        video = result["result"][0]
        title = video.get("title", "No Title")
        duration = video.get("duration", "0:00")
        link = video.get("link")
        
        if not link:
            print(f"No link found for video: {title}")
            return None, None, None
        
        # تحويل المدة إلى ثواني
        try:
            duration_parts = list(map(int, duration.split(':')))
            if len(duration_parts) == 3:  # HH:MM:SS
                duration_seconds = duration_parts[0]*3600 + duration_parts[1]*60 + duration_parts[2]
            elif len(duration_parts) == 2:  # MM:SS
                duration_seconds = duration_parts[0]*60 + duration_parts[1]
            else:  # SS
                duration_seconds = duration_parts[0]
        except Exception as e:
            print(f"Error parsing duration {duration}: {e}")
            duration_seconds = 0
            
        return title, duration_seconds, link
        
    except Exception as e:
        print(f"Error in searchYt for query '{query}': {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

async def download_audio(link: str, file_name: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """تنزيل الصوت من يوتيوب"""
    output_path = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(output_path, f'{file_name}.%(ext)s'),
        'cookiefile': config.COOK_PATH if hasattr(config, 'COOK_PATH') else None,
        'ffmpeg_location': '/usr/bin/ffmpeg', 
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            if not info:
                raise Exception("Failed to get video info")
                
            duration = info.get('duration', 0)
            title = info.get('title', file_name)
            
            if asyncio.current_task().cancelled():
                print("Download cancelled")
                return None, None, None
            
            ydl.download([link])
        
        output_file = os.path.join(output_path, f'{file_name}.mp3')
        if not os.path.exists(output_file):
            raise Exception(f"Failed to download file: {output_file}")
        
        return output_file, title, duration
        
    except Exception as e:
        print(f"Error in download_audio: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

def searchPlaylist(query: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """البحث عن قوائم تشغيل يوتيوب"""
    try:
        query = str(query).strip()
        if not query:
            return None, None, None
            
        playlistResult = PlaylistsSearch(query, limit=1)
        Result = playlistResult.result()
        
        if not Result or not Result.get("result") or len(Result["result"]) == 0:
            return None, None, None
            
        playlist = Result["result"][0]
        title = playlist.get("title")
        videoCount = playlist.get("videoCount", 0)
        link = playlist.get("link")
        
        return title, videoCount, link
        
    except Exception as e:
        print(f"Error in searchPlaylist: {e}")
        return None, None, None

def extract_playlist_id(url: str) -> Optional[str]:
    """استخراج معرف قائمة التشغيل من الرابط"""
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('list', [None])[0]
    except:
        return None

def extract_video_id(url: str) -> Optional[str]:
    """استخراج معرف الفيديو من الرابط"""
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
            
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    except:
        return None
