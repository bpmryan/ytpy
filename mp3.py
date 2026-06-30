import os
from pathlib import Path
import urllib.request
import json
from yt_dlp import YoutubeDL

def get_spotify_tracks(url, download_playlist):
    """
    Uses public embed endpoints to fetch Spotify metadata
    without needing a heavy API developer account setup.
    """
    tracks = []
    try:
        # FIX: Force Python to follow redirect shortlinks (like spotify.link) 
        # to reveal the full standard path containing 'track/' or 'playlist/'
        req_expand = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_expand) as response:
            final_url = response.geturl()  # This grabs the true expanded link
        
        # Now use the true, expanded URL for processing
        embed_url = final_url
        if "embed" not in final_url:
            if "playlist/" in final_url:
                embed_url = final_url.replace("playlist/", "embed/playlist/")
            elif "track/" in final_url:
                embed_url = final_url.replace("track/", "embed/track/")
                download_playlist = False

        # Clean off tracking queries like ?si=xxxx which can cause API parsing glitches
        if "?" in embed_url:
            embed_url = embed_url.split("?")[0]

        req = urllib.request.Request(embed_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode("utf-8")

        # Extract the JSON payload containing track data embedded in the page
        start_idx = html.find('<script id="__NEXT_DATA__" type="application/json">')
        if start_idx == -1:
            return tracks, "Spotify_Playlist"

        start_data = html.find(">", start_idx) + 1
        end_data = html.find("</script>", start_data)
        json_data = json.loads(html[start_data:end_data])

        props = json_data["props"]["pageProps"]["state"]
        data_node = props.get("data", props.get("entity", {}))

        # Check against the expanded final_url string
        if "track/" in final_url:
            track_name = data_node.get("name", "Unknown Track")
            artist_name = data_node.get("artists", [{}])[0].get("name", "Unknown Artist")
            tracks.append(f"{track_name} - {artist_name}")
            return tracks, "Single_Tracks"
        else:
            playlist_name = data_node.get("name", "Spotify_Playlist")
            tracks_struct = data_node.get("tracks", {})
            items = tracks_struct.get("items", []) if isinstance(tracks_struct, dict) else []

            for item in items:
                track = item.get("track", item)
                if not track or "name" not in track:
                    continue
                artists = track.get("artists", [{}])
                artist_name = artists[0].get("name", "Unknown Artist") if artists else "Unknown Artist"
                tracks.append(f"{track['name']} - {artist_name}")
                if not download_playlist:
                    break
            return tracks, playlist_name

    except Exception as e:
        print(f"Error reading Spotify metadata: {e}")
        return tracks, "Spotify_Downloads"


def convert(url_or_search, output_directory, download_playlist, file_format, playlist_title=None):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    if playlist_title:
        out_template = os.path.join(output_directory, playlist_title, "%(title)s.%(ext)s")
    elif download_playlist:
        out_template = os.path.join(output_directory, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")
    else:
        out_template = os.path.join(output_directory, "%(title)s.%(ext)s")

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

    if os.path.exists(r"C:\ffmpeg\bin"):
        ydl_opts["ffmpeg_location"] = r"C:\ffmpeg\bin"

    try:
        with YoutubeDL(ydl_opts) as ydl:
            if not url_or_search.startswith("http"):
                ydl.download([f"ytsearch1:{url_or_search}"])
            else:
                ydl.download([url_or_search])
    except Exception as e:
        print(f"Error occurred during download: {e}")


# 1 & 4. Wrapped Interactive Selection Engine Loop 
while True:
    user_path_input = input("Enter desired file path destination (or press Enter for default Downloads): ").strip()
    input_url = input("Enter Youtube or Spotify link: ").strip()

    file_format = input("Enter desired format (mp3 / wav): ").strip().lower()
    if file_format not in ["mp3", "wav"]:
        print("Invalid format selected. Defaulting to mp3.")
        file_format = "mp3"

    print(f"\nYou entered Path: {user_path_input if user_path_input else 'Default Downloads'}")
    print(f"You entered URL: {input_url}")
    print(f"Target Format: {file_format.upper()}\n")

    is_playlist = "n"
    if "list=" in input_url or "playlist" in input_url:
        is_playlist = input("This link appears to contain a playlist. Download full playlist? (y/n): ").strip().casefold()

    user_confirm = input("Is this correct? (y/n): ").strip().casefold()

    if user_confirm in ["y", "yes"]:
        if not user_path_input:
            final_output_dir = Path.home() / "Downloads"
        else:
            final_output_dir = Path(user_path_input)
        final_output_str = str(final_output_dir)
        break # Exit the loop and move to downloading execution
    else:
        print("\n[Notice] Resetting input selections. Let's try again.\n")
        # Loop continues back to start instead of dropping script execution via exit()

# Execution process
playlist_flag = True if is_playlist in ["y", "yes"] else False
print("\nStarting download/conversion process. Please wait...")

# FIXED: Checks for both classic URLs and shortened tracking links
if "spotify.com" in input_url or "spotify.link" in input_url:
    print("Spotify link detected. Parsing song titles...")
    search_queries, collection_title = get_spotify_tracks(input_url, playlist_flag)
    
    if not search_queries:
        print("Could not retrieve songs from Spotify link.")
        exit()

    print(f"Found {len(search_queries)} track(s). Matching items on YouTube...")
    for index, song_query in enumerate(search_queries, 1):
        print(f"\n[{index}/{len(search_queries)}] Processing: {song_query}")
        convert(
            song_query,
            final_output_str,
            playlist_flag,
            file_format,
            playlist_title=collection_title,
        )
else:
    convert(input_url, final_output_str, playlist_flag, file_format)

print("\nConversion and download process finished!")