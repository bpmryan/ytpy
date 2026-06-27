import os
from pathlib import Path
from yt_dlp import YoutubeDL

# 1. Gather inputs from the user
user_path_input = input(
    "Enter desired file path destination (or press Enter for default Downloads): "
).strip()
input_vid = input("Enter link to the video or playlist: ").strip()

print(
    f"\nYou entered Path: {user_path_input if user_path_input else 'Default Downloads'}"
)
print(f"You entered URL: {input_vid}")

# 2. Ask if they want to treat it as a playlist (if applicable)
is_playlist = "n"
if "list=" in input_vid:
    is_playlist = (
        input(
            "This link appears to contain a playlist. Download full playlist? (y/n): "
        )
        .strip()
        .casefold()
    )

# 3. Confirmation prompt
user_confirm = input(f"Is this correct? (y/n): ").strip().casefold()

# 4. Process the path based on user confirmation
if user_confirm in ["y", "yes"]:
    if not user_path_input:
        final_output_dir = Path.home() / "Downloads"
    else:
        final_output_dir = Path(user_path_input)
    final_output_str = str(final_output_dir)
else:
    print("Operation cancelled by user.")
    exit()


def convert_mp3(url, output_directory, download_playlist):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Base output template:
    # If downloading a playlist, organize them into a subfolder with track numbers: Output_Dir/Playlist_Title/01 - Video_Title.mp3
    # If a single video: Output_Dir/Video_Title.mp3
    if download_playlist:
        out_template = os.path.join(
            output_directory,
            "%(playlist_title)s",
            "%(playlist_index)s - %(title)s.%(ext)s",
        )
    else:
        out_template = os.path.join(output_directory, "%(title)s.%(ext)s")

    cookies_path = Path(__file__).parent / "cookies.txt"

    # Configure yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": not download_playlist,  # True means extract ONLY the video; False means download the whole playlist
        # Target your main browser, but format it to read safely while open
        "cookies": str(cookies_path),

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        # Ignore errors if a single video in a massive playlist is deleted/private, so the script keeps downloading the rest
        "ignoreerrors": True,
    }

    try:
        print("\nStarting download/conversion process. Please wait...")
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nConversion and download successful!")
    except Exception as e:
        print(f"\nError occurred: {e}")


# 5. Run the function
playlist_flag = True if is_playlist in ["y", "yes"] else False
convert_mp3(input_vid, final_output_str, playlist_flag)
