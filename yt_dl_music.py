# @Author: jtara1
# @Date:
# @Email:  jtara@tuta.io
# @Last modified by:   jtara1
# @Last modified time: 21-Sep-2016
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from subprocess import call
import youtube_dl
import os
import sys
import logging
import json
import glob
from parse_arguments import parse_arguments
import unicodedata
import colorama # supports cross platform, used to add color to text printed to console
colorama.init()


py_version = sys.version_info[0]

logging.basicConfig(filename='log.txt')
_log = logging.getLogger('yt_dl_music')


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

    .. note:: Big thanks to https://github.com/rachmadaniHaryono for helping
        cleanup & fix security of this function.
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

def process_history_data(playlist_title, dir, file_log):
    """Get data from file_log for tracking of indices downloaded of playlist or
    update or create data in file_log

    :param playlist_title: title of playlist
    :param dir: directory file_log (& downloaded vids) will be / are located in
    :param file_log: name of file containing data

    :return: history_downloads (data), and last_dl_index (most recent download index)
    :rtype: tuple
    """

    FailedToOpenError = FileNotFoundError if py_version == 3 else IOError
    try:
        update_history = False
        # try to open the file
        history_downloads = history_log(dir, file_log, 'read')

        # check to see if the data loaded is a dictionary
        if not isinstance(history_downloads, dict):
            raise WrongDataException(history_downloads, 'Expected Python dictionary')

        # try to get last download index
        dl_indices = history_downloads[playlist_title]['downloaded_indices']
        last_dl_index = int(dl_indices[-1])

    # file_log does not exist, create a new one with initial data
    except FailedToOpenError: # py3 & py2 errors for opening of dne file
        history_downloads = {
            playlist_title: {
                'downloaded_indices': [],
                'playlist_size': 0,
            }
        }
        update_history = True

    # data loaded from file does not match expected type
    except WrongDataException as e:
        _log.error(e.message+'\n%s', e.data)
        update_history = True

    # either playlist_title or 'downloaded_indices' not found
    except KeyError as e:
        if playlist_title in e.message:
            _log.warn('%s loaded, but %s not found' % (file_log, playlist_title))
            history_downloads[playlist_title] = {'downloaded_indices': []}
        elif 'downloaded_indices' in e.message:
            _log.warn('%s loaded, but downloaded_indices not found' % file_log)
            history_downloads[playlist_title]['downloaded_indices'] = []
        update_history = True

    # last_dl_index not found
    except IndexError:
        _log.warn('%s loaded, but no most recent download index available, \
            starting from beginning of playlist' % file_log)
        update_history = True

    # unknown error occured
    except Exception as e:
        _log.critical('%s: %s' % (type(e), e))

    if update_history:
        last_dl_index = 0 # note: this value gets incremented by 1 later
        history_downloads = history_log(dir, file_log,
                                        'write', history_downloads)

    return history_downloads, last_dl_index


def delete_zero_bytes_files(path):
    """Delete all 0 bytes files given a directory"""
    if not os.path.isdir(path):
        raise ValueError('Parameter path is not a directory.')
    files = glob.glob(path + '/*')

    # create our generator to find and remove zero byte files
    generator = (os.remove(f) for f in files if (os.path.isfile(f)) and
        os.path.getsize(f)==0)

    try:
        while True:
            next(generator)
    except StopIteration:
        _log.info('Deleted zero bytes files')
    except:
        _log.error('func delete_zero_bytes_files error')


def main(url_download, dir_downloads=os.getcwd(), indices_to_download=[0, -1],
        extract_audio=True, keep_history=True, touch_files=True, debug=False):
    """Use youtube_dl module to download vids from playlist & convert each to
    an audio file with thumbnail & other metadata from youtube_dl

    :param url_download: URL of youtube playlist (or video)
    :param dir_downloads: directory to download playlists or vids to
    :param indices_to_download: indices (start index & end index) of playlist
        to download
    :param extract_audio: only downloads audio if true
    :param keep_history: log data showing playlist title, indices downloaded, &
        playlist size to a file located in the folder where vids are downloaded
    :param touch_files: (Unix only) run sys command `touch` on each file
        downloaded to update creation date metadata to download date
    :param debug: print or write to file extra info as data is processed

    :rtype: None
    """

    playlist_title = ''
    file_log = '._dl_history.txt' # files that start with '.' seem to be hidden on linux-distros
    last_dl_index = indices_to_download[0]
    end_dl_index = indices_to_download[1]

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

    # get all data from file_log or create or update it
    if is_playlist:
        history_downloads, last_dl_index = \
            process_history_data(playlist_title, dir_downloads_playlist, file_log)

    if debug:
        print('last_dl_index: %i' % last_dl_index)
        print('end_dl_index: %i' % end_dl_index)
        print ('HISTORY_DOWNLOADS:\n' + str(history_downloads) + '\n' + str(type(history_downloads)))

    # check YoutubeDL.py in the youtube_dl library for more info
    preferredcodec = 'm4a' # m4a seems to be consistantly available
    postprocessors = [
        {
            'key': 'EmbedThumbnail', # embed thumbnail in file
        },
        {
            'key': 'FFmpegMetadata', # embed metadata in file (uploader & upload date, I think)
        }
    ]
    if extract_audio: # only downloads audio
        postprocessors.append(
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': preferredcodec,
                'preferredquality': '192',
            }
        )
    ydl_opts = {
        'outtmpl': os.path.join(dir_downloads_playlist, '%(title)s.%(ext)s'), # location & template for title of output file
        'usetitle': True,
        'writethumbnail': True,             # needed if using postprocessing EmbedThumbnail
        'playliststart': last_dl_index + 1,
        'playlistend': end_dl_index,        # stop downloading at this index
        'format': 'bestaudio/best',
        'ignoreerrors': True,               # allows continuation after errors such as Download Failed from deleted or removed videos
        'postprocessors': postprocessors,
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
                     # call command 'touch [VID_FILE_PATH]'
                    call(['touch', os.path.join(dir_downloads_playlist,
                        vid[u'title'] + '.' + preferredcodec)])
        if keep_history:
            history_downloads[playlist_title]['downloaded_indices'] = indices
            history_log(dir_downloads_playlist, file_log, 'write', history_downloads)
        if debug:
            print('INDICES:\n' + str(indices))

    # remove 0 bytes files leftover by youtube_dl
    delete_zero_bytes_files(dir_downloads_playlist)


if __name__ == '__main__':
    args = parse_arguments(['--help'] if len(sys.argv) == 1 else sys.argv[1:])

    if args.download_video_audio:
        extract_audio = False
    else:
        extract_audio = True

    main(args.vid, args.dir, args.indices, extract_audio,
        args.keep_history, args.touch, args.debug)
    # enter your url into main function below and check main docstring for more info on parameters and functionality
    # jtara1's test playlist, for testing purposes, these 2 vids are short (< 3 mins)
    url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd23ThY-ZYARtUeKsQA3oUDV-'
    # main(url, debug=False)
