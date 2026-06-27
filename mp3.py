import os 
import subprocess 

input_vid = "media/"

def convert_mp3(input,  output):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input,
        "-vn",
        "-acodec", "libmp3lame",
        "-ab", "192k",
        "-ar", "44100",
        "-y",
        output
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Conversion successful: {input} -> {output}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")


convert_mp3({input_vid}, "output_audio.mp3")