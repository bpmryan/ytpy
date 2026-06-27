import os 
import subprocess 

input_vid = input("Enter link to the video: ")
print("You entered: ", input_vid)

def convert_mp3(input, output):
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

# function call to convert the video to mp3 format and save it in the Downloads folder
convert_mp3({input_vid}, "Downloads/test.mp3")