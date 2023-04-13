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
    "--exclude",
    "-e",
    action="store",
    type=str,
    help="String to exclude from search in threads titles.",
    required=False,
)
parser.add_argument(
    "--filter",
    "-f",
    action="store",
    type=str,
    help="String for searching in threads titles.",
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
    "--verbose",
    "-v",
    action="store_true",
    help="Increase output verbosity",
    required=False,
)
args = parser.parse_args()


def progress_bar_info(thread_name: str) -> str:
    """
    Truncates thread_name to a maximum of 35 characters with an ellipsis if it is longer than 35 characters.

    Args:
        thread_name (str): The name of the thread.

    Returns:
        str: The truncated thread name.
    """
    return (thread_name[:35] + "...") if len(thread_name) > 35 else thread_name


def draw_progress_bar(index: int, max_index: int, thread_name: str, files_found: str):
    """
    Draws a progress bar to the console with the given index, max_index, thread_name, and files_found.

    Args:
        index (int): The current index.
        max_index (int): The maximum index.
        thread_name (str): The name of the thread.
        files_found (str): The number of files found.

    Returns:
        None
    """
    status = round(index / max_index * 50)
    progress_bar = f"[{'*' * status}{' ' * (50 - status)}] {files_found} {progress_bar_info(thread_name)}"
    sys.stdout.write(f"\r{progress_bar}\r")


def get_threads_list(board_id: str) -> list:
    """
    Retrieves a list of thread IDs for the given board ID.

    Args:
        board_id (str): The ID of the board.

    Returns:
        list: A list of thread IDs.
    """
    board_json = requests.get("https://2ch.hk/" + board_id + "/threads.json")
    return [k["num"] for k in board_json.json()["threads"]]


def get_filtered_threads_list(board_id: str, filter: str) -> list:
    """Retrieves a list of thread IDs for the given board ID, filtered by the given substring.

    Args:
        board_id (str): The ID of the board.
        filter (str): The substring to filter the thread subjects by.

    Returns:
        list: A list of thread IDs that have subjects containing the given filter substring.
    """
    board_json = requests.get("https://2ch.hk/" + board_id + "/threads.json")
    return [k["num"] for k in board_json.json()["threads"] if filter.lower() in k["subject"].lower()]


def get_excluded_threads_list(board_id: str, exclude: str) -> list:
    """
    Retrieves a list of thread IDs for the given board ID, excluding threads with the given substring.

    Args:
        board_id (str): The ID of the board.
        exclude (str): The substring to exclude the thread subjects by.

    Returns:
        list: A list of thread IDs that have subjects not containing the given exclude substring.
    """
    board_json = requests.get("https://2ch.hk/" + board_id + "/threads.json")
    return [k["num"] for k in board_json.json()["threads"] if exclude.lower() not in k["subject"].lower()]


def get_thread_json(board_id: str, thread_id: str) -> dict:
    """
    Retrieves the JSON object of a specific thread for the given board ID and thread ID.

    Args:
        board_id (str): The ID of the board.
        thread_id (str): The ID of the thread.

    Returns:
        dict: The JSON object of the thread.
    """
    response = requests.get("https://2ch.hk/" + board_id + "/res/" + str(thread_id) + ".json")
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            pass
    return {}


def get_posts_list(thread_json: dict) -> list:
    """
    Extracts the list of posts from a thread's JSON object.

    Args:
        thread_json (dict): The JSON object of a thread.

    Returns:
        list: The list of posts in the thread.
    """
    return [k for k in thread_json["threads"][0]["posts"]]


def get_files_list(posts_list: list) -> list:
    """
    Extracts the list of files from a list of posts.

    Args:
        posts_list (list): The list of posts.

    Returns:
        list: The list of files in the posts.
    """
    return [k["files"] for k in posts_list if k["files"]]


def get_flatten_list(value: list) -> list:
    """
    Flattens a list of nested lists.

    Args:
        value (list): The list to be flattened.

    Returns:
        list: The flattened list.
    """
    return [k for innerList in value for k in innerList]


def get_webm_links(board_id: str, thread_list: list):
    """Generator that returns a list of webm/mp4 links in threads in the given board.

    Args:
        board_id (str): The ID of the 2ch board.
        thread_list (list): A list of thread IDs to search for webm/mp4 links.

    Yields:
        list: A list of webm/mp4 links in the current thread.
    """
    thread_list_len = len(thread_list)
    for index, thread in enumerate(thread_list):
        thread_json = get_thread_json(board_id, str(thread))
        flat_file_list = get_flatten_list(get_files_list(get_posts_list(thread_json)))
        if args.verbose:
            draw_progress_bar(
                index,
                thread_list_len,
                thread_json["title"],
                str(len(flat_file_list)),
            )
        yield [
            k["path"]
            for k in flat_file_list
            if ".webm" in k["path"] or ".mp4" in k["path"]
        ]


def gen_webm_list(board_id: str, thread_list: list) -> list:
    """Generates a list of URLs for all webm and mp4 files in the specified threads.

    Args:
        board_id (str): The board ID to search (e.g. 'b', 'vg', etc.).
        thread_list (list): A list of thread IDs to search.

    Returns:
        list: A list of URLs for all webm and mp4 files found.
    """
    result = []
    for item in get_webm_links(board_id, thread_list):
        result += item
    return list(map("http://2ch.hk".__add__, result))


def write_m3u_playlist(webm_set: list, output: str):
    """Writes a playlist file in M3U format with the specified URLs.

    Args:
        webm_set (list): A list of URLs to include in the playlist.
        output (str): The output file path to write the playlist to.
    """
    with open(output, "w") as file:
        file.write("#EXTM3U\n")
        lines = [f"#EXTINF:0,WEBM\n{item}\n" for item in webm_set]
        file.writelines(lines)


if args.filter:
    thread_list = get_filtered_threads_list(args.board, args.filter)
elif args.exclude:
    thread_list = get_excluded_threads_list(args.board, args.exclude)
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
