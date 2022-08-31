#!/usr/bin/env python

import argparse
import requests
import sys

parser = argparse.ArgumentParser(description='Generate M3U playlist full of strange videos')
parser.add_argument('--board', action="store", type=str, help="Codename of the board; e.g a, b, rf, wh...", required=True)
parser.add_argument('--filter',   action="store", type=str, help="String for searching in thread titles.")
parser.add_argument('--verbose', action="store_true", help="Increase output verbosity")
args = parser.parse_args()


def progress_bar_info(thread_name: str) -> str:
    return (thread_name[:35] + '...') if len(thread_name) > 35 else thread_name


def progress_bar(index: int, max_index: int, thread_name: str, files_found: str):
    sys.stdout.write('\r')
    status = round(index / max_index * 50)
    sys.stdout.write('[' + status * '*' + (50 - status) *' ' + ']' + ' ' + files_found + ' ' + str(progress_bar_info(thread_name)))
    sys.stdout.write('\r')


def get_threads_list(board: str) -> list:
    board_json = requests.get('https://2ch.hk/' + board + '/threads.json')
    return [element['num'] for element in board_json.json()['threads']]

def get_webm_links(board: str, thread_list: list):
    for index in range(len(thread_list)):
        thread_json = requests.get('https://2ch.hk/' + board + '/res/' + str(thread_list[index]) + '.json')
        if args.filter in thread_json.json()['title'].lower():
            posts_list = [element for element in thread_json.json()['threads'][0]['posts']]
            files_list = [element['files'] for element in posts_list if element['files']]
            flat_list = [element for innerList in files_list for element in innerList]
            if args.verbose:
                progress_bar(index, len(thread_list), thread_json.json()['title'], str(len(flat_list)))
            yield [element['path'] for element in flat_list if '.webm' in element['path'] or '.mp4' in element['path']]

def gen_webm_list(board: str, thread_list: list) -> list:
    result = []
    for item in get_webm_links(board, thread_list):
        result += item
    return list(map("http://2ch.hk".__add__, result))

def write_m3u_playlist(webm_set: list):
    file = open("webm.m3u", "w")
    file.write("#EXTM3U\n")
    for item in webm_set:
        file.write("#EXTINF:0,WEBM\n")
        file.write(item + "\n")
    file.close()

thread_list = get_threads_list(args.board)
if args.verbose:
    print("Got", len(thread_list), "threads!" )
webm_list = gen_webm_list(args.board, thread_list)
write_m3u_playlist(webm_list)
print('\n')
print('All done!', len(webm_list), '<:::> videos found!')
