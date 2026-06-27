from pytubefix import Youtube, Playlist
from sys import argv

type_down = input("Enter 1 for video or 2 for playlist: ")
print("You chose: ", type_down)

link = input("Copy and paste the link here: ")
confirm = input(f"{link} \n Is this the correct link? (y/n): ")


