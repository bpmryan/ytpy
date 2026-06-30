import os
from pathlib import Path
import urllib.request
import json
from yt_dlp import YoutubeDL

# 1. Gather inputs from the user
user_path_input = input(
    "Enter desired file path destination (or press Enter for default Downloads): "
).strip()
input_url = input("Enter YouTube or Spotify link: ").strip()

# New Format Selection
file_format = input("Enter desired format (mp3 / wav): ").strip().lower()
if file_format not in ["mp3", "wav"]:
    print("Invalid format selected. Defaulting to mp3.")
    file_format = "mp3"

print(f"\nYou entered Path: {user_path_input if user_path_input else 'Default Downloads'}")
print(f"You entered URL: {input_url}")
print(f"Target Format: {file_format.upper()}\n")

# 2. Check if it's a playlist (YouTube or Spotify)
is_playlist = "n"
if "list=" in input_url or "playlist" in input_url:
    is_playlist = (
        input("This link appears to contain a playlist. Download full playlist? (y/n): ")
        .strip()
        .casefold()
    )

# 3. Confirmation prompt
user_confirm = input("Is this correct? (y/n): ").strip().casefold()

if user_confirm not in ["y", "yes"]:
    print("Operation cancelled by user.")
    exit()

# Set up output directory paths
if not user_path_input:
    final_output_dir = Path.home() / "Downloads"
else:
    final_output_dir = Path(user_path_input)
final_output_str = str(final_output_dir)


def get_spotify_tracks(url, download_playlist):
    """
    Uses public embed endpoints to fetch Spotify metadata 
    without needing a heavy API developer account setup.
    """
    tracks = []
    try:
        # Convert standard URL to embed URL to scrape metadata easily
        if "playlist/" in url:
            embed_url = url.replace("spotify.com/", "spotify.com/embed/")
        elif "track/" in url:
            embed_url = url.replace("spotify.com/", "spotify.com/embed/")
            download_playlist = False
        else:
            return tracks, "Unknown"

        req = urllib.request.Request(embed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        # Extract the JSON payload containing track data embedded in the page
        start_idx = html.find('<script id="__NEXT_DATA__" type="application/json">')
        if start_idx == -1:
            return tracks, "Spotify_Playlist"
        
        start_data = html.find('>', start_idx) + 1
        end_data = html.find('</script>', start_data)
        json_data = json.loads(html[start_data:end_data])
        
        props = json_data['props']['pageProps']['state']
        
        if "track" in url:
            track_name = props['data']['name']
            artist_name = props['data']['artists'][0]['name']
            tracks.append(f"{track_name} - {artist_name}")
            return tracks, "Single_Tracks"
        else:
            playlist_name = props['data']['name']
            items = props['data']['tracks']['items']
            for item in items:
                # Handle different nested structures in embed schemas
                track = item.get('track', item)
                tracks.append(f"{track['name']} - {track['artists'][0]['name']}")
                if not download_playlist:
                    break
            return tracks, playlist_name

    except Exception as e:
        print(f"Error reading Spotify metadata: {e}")
        return tracks, "Spotify_Downloads"


def download_media(url_or_search, output_directory, download_playlist, file_format, playlist_title=None):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Dynamic output folder templates based on context
    if playlist_title:
        out_template = os.path.join(output_directory, playlist_title, "%(title)s.%(ext)s")
    elif download_playlist:
        out_template = os.path.join(output_directory, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")
    else:
        out_template = os.path.join(output_directory, "%(title)s.%(ext)s")

    # Configure Postprocessor for MP3 vs WAV
    if file_format == "wav":
        postprocessor = {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }
    else:
        postprocessor = {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }

    cookies_path = Path(__file__).parent / "cookies.txt"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": not download_playlist,
        "postprocessors": [postprocessor],
        "ignoreerrors": True,
    }

    if cookies_path.exists():
        ydl_opts["cookies"] = str(cookies_path)

    # Cross-platform Windows FFmpeg fallback pathing
    if os.path.exists(r"C:\ffmpeg\bin"):
        ydl_opts["ffmpeg_location"] = r"C:\ffmpeg\bin"

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # If it's a plain text search string (from Spotify metadata)
            if not url_or_search.startswith("http"):
                ydl.download([f"ytsearch1:{url_or_search}"])
            else:
                ydl.download([url_or_search])
    except Exception as e:
        print(f"Error occurred during download: {e}")


# 4. Main Execution Engine
playlist_flag = True if is_playlist in ["y", "yes"] else False

print("\nStarting download/conversion process. Please wait...")

if "spotify.com" in input_url:
    print("Spotify link detected. Parsing song titles...")
    search_queries, collection_title = get_spotify_tracks(input_url, playlist_flag)
    
    if not search_queries:
        print("Could not retrieve songs from Spotify link.")
        exit()
        
    print(f"Found {len(search_queries)} track(s). Matching items on YouTube...")
    for index, song_query in enumerate(search_queries, 1):
        print(f"\n[{index}/{len(search_queries)}] Processing: {song_query}")
        # Pass the folder name explicitly to prevent spotify lookups separating files randomly
        download_media(song_query, final_output_str, playlist_flag, file_format, playlist_title=collection_title)
else:
    # Standard Native YouTube processing
    download_media(input_url, final_output_str, playlist_flag, file_format)

print("\nConversion and download process finished!")