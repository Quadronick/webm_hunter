# WebM Hunter
WebM Hunter is a simple python3 app, that creates an M3U playlist filled with dubious video content.
Just another demonstration of possible usage of 'json', 'requests' and 'argparse' modules at once.

# How to use this?
./webm_hunter.py 
   --board, -b `<BOARD_CODE>`, where `<BOARD_CODE>` is a String. Full list of boards could be found at https://2ch.hk.
   --filter, -f `<FILTER_STRING>`, process only threads, whose titles are matched with `<FILTER_STRING>`
   --output, -o `<FILE_PATH>`, path to save M3U playlist. Is set to `~/webm.m3u` by deafult.
   --verbose, -v will enable fancy verbose output
   
# Usage example
`./webm_hunter.py -b b -f pony -o '~/Downloads/I_love_pony.m3u' --verbose`
