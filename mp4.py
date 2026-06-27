from pytube import YouTube
from sys import argv
from pathlib import Path

link = argv[1]
yt = YouTube(link)

print("Title: ", yt.title)

print("Views: ", yt.views)

print("Length: ", yt.length)

yd = yt.streams.get_highest_resolution()
print("Highest resolution stream: ", yd)

# make sure that it sends it to the downloads folder of any OS
download_path = Path.home() / "Downloads"
yd.download(download_path)