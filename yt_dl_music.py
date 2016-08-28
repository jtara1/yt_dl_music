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
import colorama # supports cross platform, used to add color to text printed to console
colorama.init()
#from termcolor import colored # dont think this supports cross-platform


class YoutubeDownloadMusicException(Exception):
    def __init__(self, msg = False):
        self.msg = msg

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

def historyLog2(wdir, file_log, mode='read', output={}):
    '''
    DESCRIPTION:
        1. if mode == 'read' then it tries to read the file, file_log located in wdir returning a dictionary of the text
            if that fails, it returns an emtpy dictionary
        2. elif mode == 'write' it creates (or overwrites) the file, file_log, located in wdir with the data from output
        This function does not check if wdir is valid or create wdir
        This function does not create the file, file_log if mode == 'read'
    PARAMETERS:
        wdir:     string - directory to save to
        file_log: string - file to save to
        mode:     string - 'read' or 'write', see description above
        output:   any    - only relevant if mode == 'write', output is converted to string and written to file_log
    '''
    if mode == 'read':    
        try:
            with open(os.path.join(wdir, file_log), 'r') as f:
                data = f.read()    
                return eval(data)
        except IOError:
                return {}
    elif mode == 'write':
        with open(os.path.join(wdir, file_log), 'w') as f:
            f.write(str(output))
            return True
    else:
        print (colorama.Fore.RED + 'Error in historyLog2 func: invalid mode' + colorama.Style.RESET_ALL)
        return False
            

def main(url_download, dir_downloads = os.getcwd(), indices_to_download = [0, -1], keep_history = True, touch_files = True, debug = False):
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
    
    playlist_title = ''
    file_log = '._dl_history.txt' # files that start with '.' seem to be hidden on linux-distros
    last_dl_index = indices_to_download[0]
    end_dl_index = indices_to_download[1]
    
    # youtube_dl, uncertain of playlist title & at what index to start downloading so no options passed in parameter
    ydl = youtube_dl.YoutubeDL()
    extract_info = ydl.extract_info(url_download, download=False, process=False) # process=False just gives playlist info without each individual video info included
    
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

    # read the data from history log, if file does not exist, returns {}
    if is_playlist:
        history_downloads = historyLog2(dir_downloads_playlist, file_log, 'read')
        if not history_downloads == {}:
            if history_downloads[playlist_title]['downloaded_indices']:
                last_dl_index = history_downloads[playlist_title]['downloaded_indices'][-1]
        else:
            history_downloads = {
                playlist_title: {
                    'downloaded_indices': [],
                    'playlist_size': 0,
                },
            }
                
    if debug:
        print ('HISTORY_DOWNLOADS:\n' + str(history_downloads) + '\n' + str(type(history_downloads)))
        
    # check YoutubeDL.py in the youtube_dl library for more info
    preferredcodec = 'mp3'
    ydl_opts = {
        'outtmpl': os.path.join(dir_downloads_playlist, '%(title)s.%(ext)s'), # location & template for title of output file
        'usetitle': True,
        'writethumbnail': True,             # needed if using postprocessing EmbedThumbnail
        'playliststart': last_dl_index + 1, # we don't want to re-download the last vid we downloaded so increment this by 1
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
        with open(os.getcwd() + '/extracted_info.txt', 'w') as f:
            f.write(str(extract_info))
    
    # update history log or call commmand touch on dl files
    if is_playlist and (keep_history or (touch_files and (os.name == 'posix' or os.name == 'mac'))) and extract_info:
        indices = history_downloads[playlist_title][u'downloaded_indices']
        history_downloads[playlist_title]['playlist_size'] = len(extract_info[u'entries'])
        for vid in extract_info[u'entries']:
            if vid and vid[u'playlist_index'] not in indices:
                if keep_history:
                    indices.append(vid[u'playlist_index'])
                if touch_files:
                    call(['touch', os.path.join(dir_downloads_playlist, vid[u'title'] + '.' + preferredcodec)]) # call command 'touch [VID_FILE_PATH]'              
        if keep_history:
            historyLog2(dir_downloads_playlist, file_log, 'write', history_downloads)            
        if debug:
            print('INDICES:\n' + str(indices))

        
if __name__ == '__main__':
    # enter your url into main function below and check main docstring for more info on parameters and functionality
    # jtara1's test playlist, for testing purposes, these vids are short (< 1min) and the 2nd of the 3 vids has been deleted
    url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd20gA7y6XHFOUZy0xUOpVR8_'
    dir_dl_jtara1 = '/home/j/Downloads/yt_dl_music'
    main(url, debug=True)