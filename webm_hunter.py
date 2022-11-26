#!/usr/bin/env python

import argparse
import requests
import sys

parser = argparse.ArgumentParser(
    description="Generate M3U playlist full of strange videos"
)
parser.add_argument(
    "--board",
    "-b",
    action="store",
    type=str,
    help="Codename of the board; e.g a, b, rf, wh...",
    required=True,
)
parser.add_argument(
    "--filter",
    "-f",
    action="store",
    type=str,
    help="String for searching in thread titles.",
    required=False,
)
parser.add_argument(
    "--output",
    "-o",
    action="store",
    type=str,
    help="Path to save webm.m3u playlist",
    required=False,
)
parser.add_argument(
    "--verbose", "-v",
    action="store_true",
    help="Increase output verbosity",
    required=False,
)
args = parser.parse_args()


def progress_bar_info(thread_name: str) -> str:
    return (thread_name[:35] + "...") if len(thread_name) > 35 else thread_name


def draw_progress_bar(index: int, max_index: int, thread_name: str, files_found: str):
    status = round(index / max_index * 50)
    sys.stdout.write("\r")
    sys.stdout.write(
        "["
        + status * "*"
        + (50 - status) * " "
        + "]"
        + " "
        + files_found
        + " "
        + str(progress_bar_info(thread_name))
    )
    sys.stdout.write("\r")


def get_threads_list(board_id: str) -> list:
    board_json = requests.get("https://2ch.hk/" + board_id + "/threads.json")
    return [k["num"] for k in board_json.json()["threads"]]


def get_filtered_threads_list(board_id: str, filter: str) -> list:
    board_json = requests.get("https://2ch.hk/" + board_id + "/threads.json")
    return [k["num"] for k in board_json.json()["threads"] if filter in k["subject"]]


def get_thread_json(board_id: str, thread_id: str) -> dict:
    return requests.get(
        "https://2ch.hk/" + board_id + "/res/" + str(thread_id) + ".json"
    ).json()


def get_posts_list(thread_json: dict) -> list:
    return [k for k in thread_json["threads"][0]["posts"]]


def get_files_list(posts_list: list) -> list:
    return [k["files"] for k in posts_list if k["files"]]


def get_flatten_list(value: list) -> list:
    return [k for innerList in value for k in innerList]


def get_webm_links(board_id: str, thread_list: list):
    for index, thread in enumerate(thread_list):
        thread_json = get_thread_json(board_id, str(thread))
        flat_file_list = get_flatten_list(get_files_list(get_posts_list(thread_json)))
        if args.verbose:
            draw_progress_bar(
                index,
                len(thread_list),
                thread_json["title"],
                str(len(flat_file_list)),
            )
        yield [
            k["path"]
            for k in flat_file_list
            if ".webm" in k["path"] or ".mp4" in k["path"]
        ]


def gen_webm_list(board_id: str, thread_list: list) -> list:
    result = []
    for item in get_webm_links(board_id, thread_list):
        result += item
    return list(map("http://2ch.hk".__add__, result))


def write_m3u_playlist(webm_set: list, output: str):
    file = open(output, "w")
    file.write("#EXTM3U\n")
    for item in webm_set:
        file.write("#EXTINF:0,WEBM\n")
        file.write(item + "\n")
    file.close()


if args.filter:
    thread_list = get_filtered_threads_list(args.board, args.filter)
else:
    thread_list = get_threads_list(args.board)

if args.output:
    output = args.output
else:
    output = "./webm.m3u"

if args.verbose:
    print("Got", len(thread_list), "threads!")

webm_list = gen_webm_list(args.board, thread_list)
write_m3u_playlist(webm_list, output)
print("\nAll done!", len(webm_list), "<:::> videos found!")
