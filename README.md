# yt\_dl\_music (Youtube Download Music)

## Deprecated

use youtube-dl

`pip install youtube-dl`

`youtube-dl -x https://www.youtube.com/my-playlist`

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

#### Demo video

https://www.youtube.com/watch?v=O7cTA19rAbo&feature=youtu.be

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

#### Command Line

    usage: yt_dl_music.py [-h] [-t] [-k] [-v] [-i index index] [-d]
                          <youtube_vid> [<directory>]

    Download video[s] from Youtube [playlist] with video thumbnail & Youtube
    metadata. Then it converts each to audio files.

    positional arguments:
      <youtube_vid>         Vid or playlist from Youtube
      <directory>           Dir to put downloaded files in

    optional arguments:
      -h, --help            show this help message and exit
      -t, --touch           Call `touch` command on each file downloaded (Unix
                            only)
      -k, --keep-history    Keep track of videos of playlists downloaded in text
                            file
      -v, --download-video-audio
                            Download video and audio of each Youtube video
      -i index index, --indices index index
                            Start (0 is first) & end (-1 is last) indices to
                            indicate range of vids of a playlist to download
      -d, --debug           Print various variables as data is processed


#### Submodule

call main(...) function with url of playlist/vid you wish to download

example:

    if __name__ == "__main__":
        url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd23ThY-ZYARtUeKsQA3oUDV-'
        main(url)


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
