from argparse import ArgumentParser
import os

def parse_arguments(args):
    parser = ArgumentParser(description='Download video[s] from Youtube \
        [playlist] with video thumbnail & Youtube metadata. Then it converts \
        each to audio files.')

    # positional args
    parser.add_argument('vid', metavar='<youtube_vid>', help='Vid or playlist \
                        from Youtube')
    parser.add_argument('dir', metavar='<directory>', nargs='?',
                        default=os.path.join(os.getcwd(), 'yt_dl_music'),
                        help='Dir to put downloaded files in')

    # optional args
    parser.add_argument('-t', '--touch', default=True, required=False,
                        help='Call `touch` command on each file downloaded \
                        (Unix only)', action='store_true')
    parser.add_argument('-k', '--keep-history', default=True, required=False,
                        action='store_true', help='Keep track of videos of \
                        playlists downloaded in text file')
    parser.add_argument('-x', '--extract-audio', default=True, required=False,
                        help='Only download audio',
                        action='store_true')
    parser.add_argument('-i', '--indices', default=[0, -1], required=False, type=int,
                        nargs=2, metavar='index',
                        help='Start (0 is first) & end (-1 is last) indices \
                        to indicate range of vids of a playlist to download')
    parser.add_argument('-d', '--debug', default=False, required=False,
                        help='Print various variables as data is processed',
                        action='store_true')

    parsed_arguments = parser.parse_args(args)

    return parsed_arguments
