import argparse, re
from utils.process import find_or_start_chromium
from utils.controller import Controller

def extract_url_parts(url):
    # Define a regular expression pattern to match URLs
    url_pattern = r'^(https?://)?(www\d?\.)?([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,})(/?.*)?$'

    # Use the regular expression to extract parts of the URL
    match = re.match(url_pattern, url)
    
    if match:
        protocol = match.group(1) if match.group(1) else "http://"  # Default to http:// if no protocol is provided
        subdomain = match.group(2) if match.group(2) else ""
        domain = match.group(3)
        tld = match.group(4)
        
        # Combine the parts to form the result
        result = f"{protocol}{subdomain}{domain}.{tld}"
        return result
    else:
        return "Invalid URL"

def open_url(url, chrome_controller):
    url_prefix = extract_url_parts(url)
    url_tab_id = chrome_controller.get_tab_id(url=url_prefix)

    if not url_tab_id:
        url_tab_id = chrome_controller.open_tab(url)
    else:  
        chrome_controller.set_tab_url(url_tab_id, url)
    
    return url_tab_id


def close_url(url, chrome_controller):
    url_prefix = extract_url_parts(url)
    url_tab_id = chrome_controller.get_tab_id(url=url_prefix)

    if url_tab_id:
        chrome_controller.close_tab(url_tab_id)
    
    return url_tab_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('action', choices=['open', 'close'])
    parser.add_argument('--url', action='store')

    args = parser.parse_args()
    
    url = args.url
    action = args.action

    chromium_pid = find_or_start_chromium()
    chrome_controller = Controller(chromium_pid)

    if (action == 'open'):
        res = open_url(url, chrome_controller)
    elif (action == 'close'):
        res = close_url(url, chrome_controller)
    
    print(res)

# https://music.youtube.com/watch?v=4Hg1Kudd_x4&list=PLGELcwbcacxdHoxytHajHYMVbFrcg9HfR