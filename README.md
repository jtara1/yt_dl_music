# yt\_dl\_music (Youtube Download Music)

## Description
Built implementing youtube-dl as a library in Python to download vids and convert them to .mp3 including vid thumbnail and metadata.
The youtube-dl library will avoid downloading a file if a file with the same name already exists in the save location.

When downloading vids from a playlist it'll keep track of indices of vids downloaded from specific playlist and write them in a dictionary to the
following file: 
>./[playlist\_title]/.\_dl\_history.txt

The content of .\_dl\_history.txt will look something like this:

    {u"jtara1's test playlist": {
        u'playlist_size': 3,
        u'downloaded_indices': [1, 3]
        }
    }

By keeping track of this info, yt\_dl\_music saves time by skipping extracting info from each vid in a playlist every time.

## Requirements
- OS: Linux, OSX, Windows (only tested on Linux)
- Python 2.7 (Python 3 untested)

## Dependencies
- youtube-dl
- colorama

## Usage
call main(...) function with url of playlist/vid you wish to download

examples:

    if __name__ == "__main__":
        url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd20gA7y6XHFOUZy0xUOpVR8_'
        main(url)
        main(url, dir_downloads='/home/user/Downloads', keep_history=True, touch_files=True, debug=True)

## main(...) docstring
    '''
    DESCRIPTION:
        Utilizes youtube_dl to download vids from playlists and convert each to an .mp3 with vid thumbnail and metadata attached
        Downloads vids to dir_downloads
        Downloads vids of playlist to dir_download/playlist_title/
        Tested & working with Youtube playlists and individual Youtube videos
        Note: If info on last videos download for playlist from url_download exists in './downloads/[playlist_title]/._dl_history.txt' then
            this takes priority over indices_to_download parameter
    PARAMETERS:
        url_download:         string  - url to download, any video url should work with youtube-dl (only tested youtube vids here)
        dir_downloads:        string  - directory to download to, creates (if not avail) dir_downloads folder
        indices_to_download:  list    - [start_index, stop_index], 1 is the 1st vid in YT playlist, -1 or None means the the last index of the playlist
        keep_history:         boolean - if playlist is downloaded, then the program writes the indices video(s) downloaded to '._dl_history.txt'
        touch_files:          boolean - update modified date of vid file if True and os.name=='posix'
        debug:                boolean - prints messages and saves an extra file in same folder of this file
    TODO-TESTS:
        1. Test and add functionality for other sites (specifically saving history logs)
        2. Test indices_to_download parameter, check YoutubeDL.py for more info
    TODO:
        1. Import ydl_opts as a parameter from a file
        2. Add cli
        3. Allow single video to have "touch" command called on it.
    '''
