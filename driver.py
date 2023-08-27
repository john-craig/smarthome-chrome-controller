from utils.process import find_or_start_chromium
from utils.controller import Controller

chromium_pid = find_or_start_chromium()
chrome_controller = Controller(chromium_pid)

yt_music_prefix = "https://music.youtube.com"
yt_music_playlist_url = "https://music.youtube.com/watch?v=4Hg1Kudd_x4&list=PLGELcwbcacxdHoxytHajHYMVbFrcg9HfR"

yt_music_tab_id = chrome_controller.get_tab_id(url=yt_music_prefix)

if not yt_music_tab_id:
    yt_music_tab_id = chrome_controller.open_tab(yt_music_playlist_url)
else:  
    chrome_controller.set_tab_url(yt_music_tab_id, yt_music_playlist_url)

print(yt_music_tab_id)