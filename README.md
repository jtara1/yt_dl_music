# yt\_dl\_music (Youtube Download Music)

## Description
Built implementing [youtube-dl](https://github.com/rg3/youtube-dl) as a library in Python to download vids and convert them to an audio file including vid thumbnail and metadata from Youtube.
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


Deletes all 0 bytes files in folder with saved vids.

## Requirements

- Python 2.7 (Python 3 untested)

## Dependencies
- youtube-dl
- colorama

## Install

    git clone https://github.com/jtara1/yt_dl_music

    cd yt_dl_music

    sudo pip install -r requirements.txt


## Usage
call main(...) function with url of playlist/vid you wish to download

example:

    if __name__ == "__main__":
        url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd20gA7y6XHFOUZy0xUOpVR8_'
        main(url)
        main(url, dir_downloads='/home/user/Downloads', debug=True)

#### Demo video

https://www.youtube.com/watch?v=O7cTA19rAbo&feature=youtu.be

## main(...) docstring
    """Use youtube_dl module to download vids from playlist & convert each to
    an audio file with thumbnail & other metadata from youtube_dl

    :param url_download: URL of youtube playlist (or video)
    :param dir_downloads: directory to download playlists or vids to
    :param indices_to_download: indices (start index & end index) of playlist
        to download
    :param keep_history: log data showing playlist title, indices downloaded, &
        playlist size to a file located in the folder where vids are downloaded
    :param touch_files: (Unix only) run sys command `touch` on each file
        downloaded to update creation date metadata to download date
    :param debug: print or write to file extra info as data is processed

    :rtype: None
    """
