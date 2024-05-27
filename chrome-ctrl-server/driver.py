import argparse, re
import os
from utils.process import find_or_start_chromium
from utils.controller import Controller
from utils.logger import Logger
import yaml
import time
from flask import Flask, jsonify, request, make_response

DEFAULT_PROFILES_PATH="./profiles.yaml"

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

def conform_tabs(profile, chrome_controller):
    inital_tabs = chrome_controller.get_all_tabs()

    if 'tabs' in first_profile:
        tabs = first_profile['tabs']
        for tab in tabs:
            if 'url' in tab:
                url = tab['url']
                chrome_controller.open_tab(url)
                time.sleep(10)

    
    for old_tab in inital_tabs:
        chrome_controller.close_tab(old_tab['targetId'])

chrome_controller = None
app = Flask(__name__)

# 
# { 'tabId': "" }
@app.route('/focus', methods=['POST'])
def set_focus():
    chrome_controller = Controller()

    focus_command = request.get_json()
    chrome_controller.focus_tab(focus_command['tabId'])

    return make_response(jsonify({'result': 'success'}), 200)


@app.route('/tabs', methods=['GET'])
def get_tabs():
    chrome_controller = Controller()
    tabs = chrome_controller.get_all_tabs()
    return jsonify(tabs)

# {
#     'urls': [
#         "https://my.first.url",
#         "https://my.second.url"
#     ],
#     'action': "open-right"
#               "close-others"
# }
@app.route('/tabs', methods=['POST'])
def add_tabs():
    verbose = False
    actions = ["open-right", "open-left", "close-others"]

    chrome_controller = Controller()
    prev_tabs = chrome_controller.get_all_tabs()

    tab_command = request.get_json()
    tab_action = tab_command['action']
    tab_urls = tab_command['urls']
    
    if tab_action not in actions:
        return make_response(jsonify({'result': 'invalid action'}), 500)
    
    if verbose:
        print(f"Tab Action: {tab_action}")
        print(f"Previous Tabs: {prev_tabs}")

    if tab_action == "open-right":
        for tab_url in tab_urls:
            res = chrome_controller.open_tab(tab_url, verbose=verbose)
    elif tab_action == "open-left":
        # Messy and forces every tab to be reloaded, but it does do what
        # it's supposed to
        new_idx = 0
        prev_idx = 0

        for i in range(0,len(prev_tabs)):
            cur_tab_id = prev_tabs[i]['targetId']

            if new_idx < len(tab_urls):
                chrome_controller.set_tab_url(cur_tab_id, tab_urls[new_idx], verbose=verbose)
                new_idx = new_idx + 1
            else:
                chrome_controller.set_tab_url(cur_tab_id, prev_tabs[prev_idx]['url'], verbose=verbose)
                prev_idx = prev_idx + 1

        while new_idx < len(tab_urls) or prev_idx < len(prev_tabs):
            if new_idx < len(tab_urls):
                chrome_controller.open_tab(tab_urls[new_idx], verbose=verbose)
                new_idx = new_idx + 1
            else:
                chrome_controller.open_tab(prev_tabs[prev_idx]['url'], verbose=verbose)
                prev_idx = prev_idx + 1
    else:
        for tab_url in tab_urls:
            chrome_controller.open_tab(tab_url, verbose=verbose)
        
        for prev_tab in prev_tabs:
            chrome_controller.close_tab(prev_tab['targetId'], verbose=verbose)
    
    return make_response(jsonify({'result': 'success'}), 200)

# This sets the URLs of the tabs at specific positions. If 'preserve' is set to true,
# it opens the tabs at the specified position, rather than overwriting the tab at that
# position.
# {
#     'tabs': [
#         { 'tabPos': 0, 'url': "https://myurl.com"  }
#     ],
#     'preserve': true/false (optional, default false)
# }
@app.route('/tabs', methods=['PATCH'])
def set_tabs():
    verbose = True
    actions = ["open-right", "open-left", "close-others"]

    chrome_controller = Controller()
    prev_tabs = chrome_controller.get_all_tabs()

    tab_command = request.get_json()
    
    if 'preserve' in tab_command:
        preserve = tab_command['preserve']
    else:
        preserve = False
    
    new_tabs = tab_command['tabs']

    if verbose:
        print(f"Tab Command: {tab_command}")
        print(f"Previous Tabs: {prev_tabs}")

    if preserve:
        for new_tab in new_tabs:
            tab_pos = new_tab['tabPos']

            if tab_pos >= len(prev_tabs):
                continue

            tab_id = prev_tabs[tab_pos]['targetId']
            chrome_controller.set_tab_url(tab_id, new_tab['url'])

            # Shift all previous tabs to the right
            for i in range(tab_pos, len(prev_tabs) - 1):
                tab_id = prev_tabs[i]['targetId']
                tab_url = prev_tabs[i+1]['url']
                chrome_controller.set_tab_url(tab_id, tab_url)
            
            # Open a new tab for the remaining one
            chrome_controller.open_tab(prev_tabs[-1]['url'])

            # Update previous tabs to reflect new state
            prev_tabs = chrome_controller.get_all_tabs()
    else:
        for new_tab in new_tabs:
            tab_pos = new_tab['tabPos']

            if tab_pos >= len(prev_tabs):
                continue
            
            tab_id = prev_tabs[tab_pos]['targetId']
            
            chrome_controller.set_tab_url(tab_id, new_tab['url'])
    
    return make_response(jsonify({'result': 'success'}), 200)

    

if __name__ == "__main__":
    app.run(debug=True)
    # Set up the logger
    # home_directory = os.path.expanduser("~")
    # log_file_path = os.path.join(home_directory, ".config", "controller.log")
    # logger = Logger(log_file_path)

    # # Set up the arguement parser
    # parser = argparse.ArgumentParser()

    # parser.add_argument('--profiles', action='store')

    # args = parser.parse_args()
    # profiles_path = args.profiles

    # if not profiles_path:
    #     profiles_path = DEFAULT_PROFILES_PATH

    # # New configuration input
    # with open(profiles_path, 'r') as yaml_file:
    #     yaml_content = yaml_file.read()

    # profiles_conf = yaml.safe_load(yaml_content)

    # # Get a running chrome instance
    # chromium_pid = find_or_start_chromium(logger=logger)
    # chrome_controller = Controller(chromium_pid, logger=logger)

    # # Iterate through the 'tabs' list of the first profile and open tabs
    # if 'profiles' in profiles_conf:
    #     profiles = profiles_conf['profiles']
    #     if profiles:
    #         first_profile = profiles[0]
    #         conform_tabs(first_profile, chrome_controller)
            

# https://music.youtube.com/watch?v=4Hg1Kudd_x4&list=PLGELcwbcacxdHoxytHajHYMVbFrcg9HfR