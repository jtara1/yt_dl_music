# yt\_dl\_music (Youtube Download Music)
----

## Description
Built implementing youtube_dl as a library in Python to download vids and convert them to .mp3 including vid thumbnail and metadata. When downloading vids
from a playlist it'll keep track of indices of vids downloaded from specific playlist and write them in a dictionary to the
following file: 
>./downloads/[playlist\_title]/.\_dl\_history.txt

The content of .\_dl\_history.txt will look something like this:

    {u"jtara1's test playlist": {
        u'playlist_size': 3,
        u'downloaded_indices': [1, 3]
        }
    }

By keeping track of this info, yt\_dl\_music avoids downloading the same videoes from a repeated playlist.

----
## Requirements
- OS: Linux, OSX, Windows (only tested on Linux)
- Python 2.7 (Python 3 untested)

----
## Dependencies
- youtube_dl
- colorama

----
## Usage
call main(...) function with url of playlist/vid you wish to download

examples:

    if __name__ == "__main__":
        url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd20gA7y6XHFOUZy0xUOpVR8_'
        main(url)
        main(url, dir_downloads='/home/user/Downloads', keep_history=True, touch_files=True, debug=True)

----
## main(...) docstring
    '''
    DESCRIPTION:
        Utilizes youtube_dl to download vids from playlists and convert each to an .mp3 with vid thumbnail and metadata attached
        Downloads vids to dir_downloads/"downloads"/
        Downloads vids of playlist to dir_download/"downloads"/playlist_title/
        Tested & working with Youtube playlists and individual Youtube videos
        Note: If info on last videos download for playlist from url_download exists in './downloads/[playlist_title]/._dl_history.txt' then
            this takes priority over indices_to_download parameter
    PARAMETERS:
        url_download:         string  - url to download, any video url should work with youtube-dl (only tested youtube vids here)
        dir_downloads:        string  - directory to download to, creates (if not avail) dir_downloads folder
        indices_to_download:  list    - [start_index, stop_index], 1 is the 1st index in YT playlist, -1 or None means the the last index of the playlist
        keep_history:         boolean - if True and if playlist is downloaded, then the program writes the index of last video downloads
        touch_files:          boolean - update modified date of vid file if True and os.name=='posix'
        debug:                boolean - if True prints messages and saves an extra file in root dir of this file
    TODO-TESTS:
        0. Test and attempt to create a cron job to run this daily and download undownloaded vids to convert to .mp3
        1a. Do more testing with youtube videos and playlists
        1b. Test and add functionality for other sites (specifically saving history logs)
        1c. Test indices_to_download parameter, check YoutubeDL.py for more info
    TODO:
        1. Add functionality to prioritize using indices_to_download or '_dl_history.txt' as playlist indices to download
        2. Import ydl_opts as a parameter from a file
        3. Add support to touch file when non playlist is passed
    '''
