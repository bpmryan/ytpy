# ytpy

## Features:
* Convert media into mp3 or wav
    * Applicable media:
        * Youtube videos and playlists

* Terminal program to activates with following commands below (depending on user's OS)

## Sources:
* [Powers of Python 5:20](https://www.youtube.com/watch?v=vEQ8CXFWLZU&t=320s)
* [Convert Videos to MP3 with FFmpeg in Python](https://www.youtube.com/watch?v=ucXTQ0V8qMA)
* [ffmpeg download](https://www.gyan.dev/ffmpeg/builds/)


## Installation Notes/Guide:
1. Clone/download zip this repo 
2. *General*:  
`pip install --upgrade pip`  
`pip install yt-dlp`

4. *cookies.txt*
    * Install cookies.txt extension in browser
    * Go to YouTube and go to toolbar, click on extension, and download file into this project
      
5. *OS Specific*
   * *Linux*: install .venv `python -m venv .venv`
       * *before running* `source .venv/bin/activate`
       * *install* ffmpeg 
            * *example* `sudo pacman -S ffmpeg`
       * *run* `python mp3.py`
   
   * *Windows*:
       * *install* `winget install ffmpeg`  
       * *run* `python mp3.py`
   
   * *Mac*:
       * Has not been tested


