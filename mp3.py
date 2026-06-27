import os
from pathlib import Path
from yt_dlp import YoutubeDL

# 1. Gather inputs from the user
user_path_input = input(
    "Enter desired file path destination (or press Enter for default Downloads): "
).strip()
input_vid = input("Enter link to the video: ").strip()

print(
    f"\nYou entered Path: {user_path_input if user_path_input else 'Default Downloads'}"
)
print(f"You entered URL: {input_vid}")

# 2. Correctly format the confirmation prompt (input only takes 1 string argument)
user_confirm = input(f"\nIs this correct? (y/n): ")
user_confirm = user_confirm.casefold()  # Added () to actually execute the method

# 3. Process the path based on user confirmation
if user_confirm == "y" or user_confirm == "yes":
    # If the user pressed enter/left it blank, default to their system Downloads folder
    if not user_path_input:
        final_output_dir = Path.home() / "Downloads"
    else:
        final_output_dir = Path(user_path_input)

    # Convert the Path object to a string for OS operations
    final_output_str = str(final_output_dir)
else:
    print("Operation cancelled by user.")
    exit()  # Stop the script if they didn't confirm 'y'


def convert_mp3(url, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Configure yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best",  # Fetch the best quality audio stream
        "outtmpl": os.path.join(
            output_directory, "%(title)s.%(ext)s"
        ),  # Save using video title
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",  # Tell yt-dlp to extract audio using FFmpeg
                "preferredcodec": "mp3",  # Convert to MP3
                "preferredquality": "192",  # 192kbps audio quality
            }
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nConversion and download successful!")
    except Exception as e:
        print(f"\nError occurred: {e}")


# 4. Pass both required arguments to the function
convert_mp3(input_vid, final_output_str)
