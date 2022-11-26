# WebM Hunter
WebM Hunter is a simple python3 app, that creates an M3U playlist filled with dubious video content.
Just another demonstration of possible usage of 'json', 'requests' and 'argparse' modules at once.

## Requirements
* Requests (https://github.com/psf/requests; pip install requests)

## How to use this?
./webm_hunter.py  
&emsp;--board, -b `<BOARD_CODE>` is a String; full list of boards could be found at https://2ch.hk  
&emsp;--exclude, -e `EXCLUDE_STRING` is a String; String to exclude from search in threads titles  
&emsp;--filter, -f `<FILTER_STRING>` is a String; process only threads, whose titles are matched with `<FILTER_STRING>`  
&emsp;--output, -o `<FILE_PATH>` is a String; path to save M3U playlist. Is set to `~/webm.m3u` by deafult  
&emsp;--verbose, -v will enable fancy verbose output  

## Usage example
`./webm_hunter.py -b b -f pony -o '~/Downloads/I_love_pony.m3u' --verbose`