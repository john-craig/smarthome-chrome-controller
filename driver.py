import argparse, re
import os
from utils.process import find_or_start_chromium
from utils.controller import Controller
from utils.logger import Logger
import yaml
import time

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



if __name__ == "__main__":
    # Set up the logger
    home_directory = os.path.expanduser("~")
    log_file_path = os.path.join(home_directory, ".config", "controller.log")
    logger = Logger(log_file_path)

    # Set up the arguement parser
    parser = argparse.ArgumentParser()

    parser.add_argument('--profiles', action='store')

    args = parser.parse_args()
    profiles_path = args.profiles

    if not profiles_path:
        profiles_path = DEFAULT_PROFILES_PATH

    # New configuration input
    with open(profiles_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()

    profiles_conf = yaml.safe_load(yaml_content)

    # Get a running chrome instance
    chromium_pid = find_or_start_chromium()
    chrome_controller = Controller(chromium_pid)

    # Iterate through the 'tabs' list of the first profile and open tabs
    if 'profiles' in profiles_conf:
        profiles = profiles_conf['profiles']
        if profiles:
            first_profile = profiles[0]
            conform_tabs(first_profile, chrome_controller)
            

# https://music.youtube.com/watch?v=4Hg1Kudd_x4&list=PLGELcwbcacxdHoxytHajHYMVbFrcg9HfR