# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 12:31:16 2016

author: jtara1 (github)
OS: Linux, should work on all OS's, needs testing
Python 2.7

"""

from __future__ import unicode_literals
from subprocess import call
import youtube_dl
import os
import sys
import logging
import json
import colorama # supports cross platform, used to add color to text printed to console
colorama.init()
#from termcolor import colored # dont think this supports cross-platform


class YoutubeDownloadMusicException(Exception):
    """Raised when youtube-dl module throws an exception"""
    def __init__(self, msg = False):
        self.msg = msg


class WrongDataException(Exception):
    """Raised when data is not what we expected"""
    def __init__(self, data, message):
        self.data = data
        self.message = message

class MyLogger(object):
    # the following functions will print same messages printed in cli of youtube-cli
    def debug(self, msg):
        print (colorama.Fore.BLUE + msg + colorama.Style.RESET_ALL)

    def warning(self, msg):
        print (colorama.Fore.YELLOW + msg + colorama.Style.RESET_ALL)

    def error(self, msg):
        print (colorama.Fore.RED + msg + colorama.Style.RESET_ALL)


def my_hook(d):
    '''
    DESCRIPTION:
        This function gets called by youtube_dl; check their docs for more info (YoutubeDL.py)
        Upon completion of download of a video, print string
    '''
#    print (d) # debug - can be used to extract percentage or bytes of file downloaded or time spent downloading or check if download finished
#    with open('my_hook.txt', 'w') as f:
#        f.write(d)
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def history_log(wdir=os.getcwd(), log_file='log_file.txt', mode='read', write_data=None):
    """Read python dictionary from or write python dictionary to a file

    :param wdir: directory for text file to be saved to
    :param log_file: name of text file (include .txt extension)
    :param mode: 'read', 'write', or 'append' are valid
    :param write_data: data that'll get written in the log_file
    :type write_data: dictionary (or list or set)

    :return: returns data read from or written to file (depending on mode)
    :rtype: dictionary

    .. note:: Big thanks to https://github.com/rachmadaniHaryono for helping cleanup & fix security of this function.
    """
    mode_dict = {
        'read': 'r',
        'write': 'w',
        'append': 'a'
    }
    if mode in mode_dict:
        with open(os.path.join(wdir, log_file), mode_dict[mode]) as f:
            if mode == 'read':
                return json.loads(f.read())
            else:
                f.write(json.dumps(write_data))
                return write_data
    else:
        logging.error('history_log func: invalid mode (param #3)')
        return {}



def main(url_download, dir_downloads=os.getcwd(), indices_to_download=[0, -1],
        keep_history=True, touch_files=True, debug=False):
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

    py_version = sys.version_info[0]

    playlist_title = ''
    file_log = '._dl_history.txt' # files that start with '.' seem to be hidden on linux-distros
    last_dl_index = indices_to_download[0]
    end_dl_index = indices_to_download[1]

    # create logger
    logging.basicConfig(filename='log.txt')
    _log = logging.getLogger('yt_dl_music')

    # youtube_dl, uncertain of playlist title & at what index to start downloading so no options passed in parameter
    ydl = youtube_dl.YoutubeDL()
    extract_info = ydl.extract_info(url_download, download=False, process=False) # process=False just gives playlist info without each individual video info included

    if debug:
        with open('extracted_info.txt', 'w') as f:
            f.write(str(extract_info))

    # determines if link is_playlist, and gets playlist_title
    if extract_info[u'extractor'] == u'youtube:playlist':
        playlist_title = extract_info[u'title']
        is_playlist = True
    else:
        is_playlist = False

    if debug:
        print('PLAYLIST_TITLE: ' + playlist_title) # debug

    # local variables for directories
#    dir_downloads_root = os.path.join(dir_downloads, 'yt_dl_music')
    dir_downloads_root = dir_downloads
    dir_downloads_playlist = os.path.join(dir_downloads_root, playlist_title) # by default, playlist_title = ''

    if debug:
        print('DIR_DOWNLOADS: ' + dir_downloads)
        print('DIR_DOWNLOADS_ROOT: ' + dir_downloads_root)
        print('DIR_DOWNLOADS_PLAYLIST: ' + dir_downloads_playlist)

    # make directories if not already made
    if not os.path.isdir(dir_downloads_root):
        os.mkdir(dir_downloads_root)
    if not os.path.isdir(dir_downloads_playlist):
        os.mkdir(dir_downloads_playlist)

    FailedToOpenError = FileNotFoundError if py_version == 3 else IOError

    # read the data from history log, if file does not exist, returns {}
    if is_playlist:
        try:
            update_history = False
            # try to open the file
            history_downloads = history_log(dir_downloads_playlist, file_log, 'read')

            # check to see if the data loaded is a dictionary
            if not isinstance(history_downloads, dict):
                raise WrongDataException(history_downloads, 'Expected Python dictionary')

            # try to get last download index
            dl_indices = history_downloads[playlist_title]['downloaded_indices']
            last_dl_index = int(dl_indices[-1])

        except FailedToOpenError: # py3 & py2 errors for opening of dne file
            history_downloads = {
                playlist_title: {
                    'downloaded_indices': [],
                    'playlist_size': 0,
                }
            }
            update_history = True

        except WrongDataException as e:
            _log.error(e.message+'\n%s', e.data)
            update_history = True

        except KeyError as e:
            if playlist_title in e.message:
                _log.warn('%s loaded, but %s not found' % (file_log, playlist_title))
                history_downloads[playlist_title] = {'downloaded_indices': []}
            elif 'downloaded_indices' in e.message:
                _log.warn('%s loaded, but downloaded_indices not found' % file_log)
                history_downloads[playlist_title]['downloaded_indices'] = []
            update_history = True

        except IndexError:
            _log.warn('%s loaded, but no most recent download index available, \
                starting from beginning of playlist' % file_log)
            update_history = True

        except:
            _log.critical('Unknown error in history checking')

        if update_history:
            last_dl_index = 0 # note: this value gets incremented by 1 later
            history_downloads = history_log(dir_downloads_playlist, file_log,
                                            'write', history_downloads)

    if debug:
        print('last_dl_index: %i' % last_dl_index)
        print('end_dl_index: %i' % end_dl_index)
        print ('HISTORY_DOWNLOADS:\n' + str(history_downloads) + '\n' + str(type(history_downloads)))

    # check YoutubeDL.py in the youtube_dl library for more info
    preferredcodec = 'mp3'
    ydl_opts = {
        'outtmpl': os.path.join(dir_downloads_playlist, '%(title)s.%(ext)s'), # location & template for title of output file
        'usetitle': True,
        'writethumbnail': True,             # needed if using postprocessing EmbedThumbnail
        'playliststart': last_dl_index + 1,
        'playlistend': end_dl_index,        # stop downloading at this index
        'format': 'bestaudio/best',
        'ignoreerrors': True,               # allows continuation after errors such as Download Failed from deleted or removed videos
        'postprocessors': [
            {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferredcodec,
            'preferredquality': '192',
            },
            {
            'key': 'EmbedThumbnail', # embed thumbnail in file
            },
            {
            'key': 'FFmpegMetadata', # embed metadata in file (uploader & upload date, I think)
            }
        ],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    # update params to ydl_opts set above, and extract info about video(es) and download them
#    ydl = youtube_dl.YoutubeDL(ydl_opts)
    try:
        ydl.__init__(params = ydl_opts)
        extract_info = ydl.extract_info(url_download, download=True)
    except Exception as e:
        print(e.msg)

    if debug:
        with open(os.getcwd() + '/extracted_info2.txt', 'w') as f:
            f.write(str(extract_info))

    # update history log or call commmand touch on dl files
    if is_playlist and extract_info and (
        keep_history or (touch_files and (os.name == 'posix' or os.name == 'mac'))):

        indices = history_downloads[playlist_title][u'downloaded_indices']
        history_downloads[playlist_title]['playlist_size'] = len(extract_info[u'entries'])
        for vid in extract_info[u'entries']:
            if vid and vid[u'playlist_index'] not in indices:
                if keep_history:
                    indices.append(vid[u'playlist_index'])
                if touch_files:
                    call(['touch', os.path.join(dir_downloads_playlist, vid[u'title'] + '.' + preferredcodec)]) # call command 'touch [VID_FILE_PATH]'
        if keep_history:
            history_downloads[playlist_title]['downloaded_indices'] = indices
            history_log(dir_downloads_playlist, file_log, 'write', history_downloads)
        if debug:
            print('INDICES:\n' + str(indices))


if __name__ == '__main__':
    # enter your url into main function below and check main docstring for more info on parameters and functionality
    # jtara1's test playlist, for testing purposes, these 2 vids are short (< 1min)
    url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd20gA7y6XHFOUZy0xUOpVR8_'
    dir_dl_jtara1 = '/home/j/Downloads/yt_dl_music'
    main(url, debug=True)
