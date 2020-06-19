#!/usr/bin/env python


import urllib3
from bs4 import BeautifulSoup


def get_threads_list(board):
    thread_list = []
    http = urllib3.PoolManager()
    main_page = http.request('GET', 'https://2ch.hk/' + board)
    main_page = main_page.data.decode('utf-8')
    soup = BeautifulSoup(main_page, 'html.parser')
    for tag in soup("a"):
        if tag.contents == ['Ответ']:
            thread_list.append("https://2ch.hk" + tag.get("href"))
    return thread_list


def get_webm_contained_threads(thread_list):
    http = urllib3.PoolManager()
    webm_thread_list = []
    for link in thread_list:
        webm_count = 0
        _page = http.request('GET', link).data.decode('utf-8')
        _soup = BeautifulSoup(_page, 'html.parser')
        for _tag in _soup.find_all('a'):
            if "webm" in str(_tag.get('href')):
                webm_count += 1
        if webm_count > 0:
            webm_thread_list.append(link)
            print("webm::", webm_count//2, link, _soup.head.title.contents)
    return webm_thread_list


def get_webm_list(webm_thread_list):
    http = urllib3.PoolManager()
    webm_list = []
    for link in webm_thread_list:
        webm_count = 0
        _page = http.request('GET', link).data.decode('utf-8')
        _soup = BeautifulSoup(_page, 'html.parser')
        for _tag in _soup.find_all('a'):
            if ("webm" or "mp4") in str(_tag.get('href')):
                webm_list.append("https://2ch.hk" + _tag.get('href'))
                webm_count += 1
    webm_set = set(webm_list)
    print("Схоронила целых", len(webm_set), "webm")
    return webm_set


def write_m3u_playlist(webm_set):
    file = open("webm.m3u", "w")
    file.write("#EXTM3U\n")
    for item in webm_set:
        file.write("#EXTINF:0,WEBM\n")
        file.write(item + "\n")
    file.close()


thread_list = get_threads_list("b")
webm_thread_list = get_webm_contained_threads(thread_list)
webm_set = get_webm_list(webm_thread_list)
write_m3u_playlist(webm_set)
