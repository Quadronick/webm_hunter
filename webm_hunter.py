#!/usr/bin/env python

import argparse
import json
import requests

parser = argparse.ArgumentParser(description='Generate M3U playlist full of strange videos')
parser.add_argument('--board', action="store", dest="board", type=str, help="Codename of the board; String;", required=True)
args = parser.parse_args()


def get_threads_list(board):
    board_json = requests.get('https://2ch.hk/' + board + '/threads.json')
    return [element['num'] for element in board_json.json()['threads'] if element['num']]

def get_webm_links(board, thread_list):
    for index in range(len(thread_list)):
        thread_json = requests.get('https://2ch.hk/' + board + '/res/' + thread_list[index] + '.json')
        posts_list = [element for element in thread_json.json()['threads'][0]['posts']]
        files_list = [element['files'] for element in posts_list if element['files']]
        yield [element[0]['path'] for element in files_list if 'webm' in element[0]['path'] or 'mp4' in element[0]['path']]

def gen_webm_list(board, thread_list):
    result = []
    for item in get_webm_links(board, thread_list):
        result += item
    return list(map("http://2ch.hk".__add__, result))

def write_m3u_playlist(webm_set):
    file = open("webm.m3u", "w")
    file.write("#EXTM3U\n")
    for item in webm_set:
        file.write("#EXTINF:0,WEBM\n")
        file.write(item + "\n")
    file.close()

get_threads_list(args.board)
thread_list = get_threads_list(args.board)
webm_list = gen_webm_list(args.board, thread_list)
write_m3u_playlist(webm_list)

print('All done!', len(webm_list), '<:::> videos found!')