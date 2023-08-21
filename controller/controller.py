import PyChromeDevTools

chrome = PyChromeDevTools.ChromeInterface()

def get_tab_id(chrome, url=""):
    ret_val, messages = chrome.Target.getTargets()
    tab_info = ret_val['result']['targetInfos']

    for tab in tab_info:
        if tab['url'].startswith(url):
            return tab['targetId']
    
    return None

def set_tab_url(chrome, tab_id, url):
    chrome.Target.activateTarget(targetId=tab_id)
    chrome.Page.navigate(url=url)

def open_tab(chrome, url):
    ret_val, messages = chrome.Target.createTarget(url=url)

    return ret_val['result']['targetId']

yt_music_prefix = "https://music.youtube.com"
yt_music_playlist_url = "https://music.youtube.com/watch?v=4Hg1Kudd_x4&list=PLGELcwbcacxdHoxytHajHYMVbFrcg9HfR"

yt_music_tab_id = get_tab_id(chrome, url=yt_music_prefix)

if not yt_music_tab_id:
    yt_music_tab_id = open_tab(chrome, yt_music_playlist_url)
else:  
    set_tab_url(chrome, yt_music_tab_id, yt_music_playlist_url)

print(yt_music_tab_id)