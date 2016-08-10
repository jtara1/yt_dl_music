# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 12:31:16 2016

@author: jtara1 (github)
OS: Linux Ubuntu 16.04, should work on all OS's, needs testing
Python 2.7

"""

from __future__ import unicode_literals
import youtube_dl
import os
import colorama # supports cross platform, used to add color to text printed to console
colorama.init()
#from termcolor import colored # dont think this supports cross-platform


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
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
        
        
def historyLog(wdir, mode = 'read', msg = ''):
    with open(wdir + 'log.txt', 'a') as f:
        if mode == 'read':
            txt = f.readline()
            if txt == '':
                index = 1
            else:
                index = int(txt)
#            print ('index: ' + index)
            return index 
        elif mode == 'write':
            f.seek(0)
            f.write(msg)
            return int(msg)
            

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
            with open(wdir + file_log, 'r') as f:
                data = f.read()    
                return eval(data)
        except IOError:
                return {}
    elif mode == 'write':
        with open(wdir + file_log, 'w') as f:
            f.write(str(output))
            return True
    else:
        print (colorama.Fore.RED + 'Error in historyLog2 func: invalid mode' + colorama.Style.RESET_ALL)
        return False
            

def main(url_download, indices_to_download = [0, -1], keep_history = True, debug = False):
    '''
    DESCRIPTION:
        Utilizes youtube_dl to download vids from playlists and convert each to an .mp3 with vid thumbnail and metadata attached
        Downloads 'vids to ./downloads/'
        Downloads vids of playlist to './downloads/[playlist_title]/'
        Tested & working with Youtube playlists and individual Youtube videoes
        Note: If info on last videoes download for playlist from url_download exists in './downloads/[playlist_title]/._dl_history.txt' then
            this takes priority over indices_to_download parameter
    PARAMETERS:
        url_download:         string  - url to download, any video url should work with youtube-dl (only tested youtube vids here)
        indices_to_download:  list    - [start_index, stop_index], 1 is the 1st index in YT playlist, -1 or None means the the last index of the playlist
        keep_history:         boolean - if True and if playlist is downloaded, then the program writes the index of last video downloads
        debug:                boolean - if True prints messages and saves an extra file in root dir of this file
    TODO-TESTS:
        0. Test and attempt to create a cron job to run this daily and download undownloaded vids to convert to .mp3
        1a. Do more testing with youtube videoes and playlists
        1b. Test and add functionality for other sites (specifically saving history logs)
        1c. Test indices_to_download parameter, check YoutubeDL.py for more info
    TODO:
        1. Add functionality to prioritize using indices_to_download or '_dl_history.txt' as playlist indices to download
        2. Import ydl_opts as a parameter from a file
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
    dir_downloads_root = os.getcwd() + '/downloads/'
    dir_downloads_playlist = dir_downloads_root + playlist_title + '/' # by default, playlist_title = ''
    
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
    ydl_opts = {
        'outtmpl': dir_downloads_playlist + '%(title)s.%(ext)s', # location & template for title of output file
        'usetitle': True,
        'writethumbnail': True, # needed if using postprocessing EmbedThumbnail
        'playliststart': last_dl_index + 1, # we don't want to re-download the last vid we downloaded so increment this by 1
        'playlistend': end_dl_index,
        'format': 'bestaudio/best',
        'ignoreerrors': True, # allows continuation after errors such as Download Failed from deleted or removed videoes
        'postprocessors': [
            {
            'key': 'FFmpegExtractAudio',            
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            },
            {
            'key': 'EmbedThumbnail',            
            },
            {
            'key': 'FFmpegMetadata',
            }
        ],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    # update params to ydl_opts set above, and extract info about video(es) and download them
    ydl.__init__(params = ydl_opts)
    extract_info = ydl.extract_info(url_download, download=True)

    if debug:    
        with open(os.getcwd() + '/extracted_info.txt', 'w') as f:
            f.write(str(extract_info))
    
    # update history log
    if is_playlist and keep_history:
        indices = history_downloads[playlist_title][u'downloaded_indices']
        history_downloads[playlist_title]['playlist_size'] = len(extract_info[u'entries'])
        for vid in extract_info[u'entries']:
            if vid and vid[u'playlist_index'] not in indices:
                indices.append(vid[u'playlist_index'])
        if debug:
            print('INDICES:\n' + str(indices))
        historyLog2(dir_downloads_playlist, file_log, 'write', history_downloads)            

        
if __name__ == '__main__':
    # enter your url into main function below and check main docstring for more info on parameters and functionality
    # jtara1's test playlist, for testing purposes, these vids are short (< 1min) and the 2nd of the 3 vids has been deleted
    url = 'https://www.youtube.com/playlist?list=PLQRGmPzigd20gA7y6XHFOUZy0xUOpVR8_'
    main(url)
