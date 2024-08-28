import click, re
import os
import time
from chromectrl.utils.process import find_or_start_chromium
from chromectrl.utils.controller import Controller
from chromectrl.utils.logger import Logger

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


def close_url(url, chrome_controller):
    url_prefix = extract_url_parts(url)
    url_tab_id = chrome_controller.get_tab_id(url=url_prefix)

    if url_tab_id:
        chrome_controller.close_tab(url_tab_id)
    
    return url_tab_id


@click.group()
@click.pass_context
def chromectrl_cli(ctx):
    ctx.obj = {
        'controller': Controller()
    }

@chromectrl_cli.command(help="Open a tab with the specified URL")
@click.option('-j', '--jsonify', is_flag=True, show_default=True, default=False, help="Display the result as JSON")
@click.pass_context
@click.argument('url')
def open_tab(ctx, jsonify, url):
    controller = ctx.obj['controller']

    controller.open_tab(url)

@chromectrl_cli.command(help="Get a list of the current tabs")
@click.option('-j', '--jsonify', is_flag=True, show_default=True, default=False, help="Display the result as JSON")
@click.pass_context
def get_tabs(ctx, jsonify):
    controller = ctx.obj['controller']

    cur_tabs = controller.get_all_tabs()

    if not jsonify:
        for tab in cur_tabs:
            click.echo(tab['url'])
    else:
        click.echo(cur_tabs)

@chromectrl_cli.command(help="Close a tab with the specified URL")
@click.option('-j', '--jsonify', is_flag=True, show_default=True, default=False, help="Display the result as JSON")
@click.pass_context
@click.argument('url')
def close_tab(ctx, jsonify, url):
    controller = ctx.obj['controller']

    cur_tabs = controller.get_all_tabs()

    for tab in cur_tabs:
        if tab['url'] == url:
            controller.close_tab(tab['targetId'])

            if jsonify:
                click.echo(tab)
            else:
                click.echo(tab['url'])
            break

@chromectrl_cli.command(help="Set the current tabs")
@click.option('-j', '--jsonify', is_flag=True, show_default=True, default=False, help="Display the result as JSON")
@click.option('-p', '--preserve', is_flag=True, show_default=True, default=False, help="Preserve existing tabs")
@click.argument('urls', nargs=-1)
@click.pass_context
def set_tabs(ctx, jsonify, preserve, urls):
    controller = ctx.obj['controller']
    initial_tabs = controller.get_all_tabs()
    changed_tabs = []

    for i in range(0,len(urls)):
        url = urls[i]

        # Try to reuse tabs
        if len(initial_tabs) > i:
            prev_tab = initial_tabs[i]

            if prev_tab['url'] == url:
                continue
            else:
                controller.set_tab_url(prev_tab['targetId'], url)
                changed_tabs.append(prev_tab) # Keep track of tabs we've changed
        else:
            controller.open_tab(url)
        
        # Approximation. Guess we could
        # poll until the tab is opened properly
        time.sleep(5)
    
    if not preserve:
        if len(urls) > len(initial_tabs):
            for i in range(len(urls), len(initial_tabs)):
                old_tab = initial_tabs[i]
                controller.close_tab(old_tab['targetId'])
    else:
        # Reopen the URLs of any tabs we changed
        for old_tab in changed_tabs:
            controller.open_tab(old_tab['url'])
    
    # Print new tab list
    cur_tabs = controller.get_all_tabs()

    if not jsonify:
        for tab in cur_tabs:
            click.echo(tab['url'])
    else:
        click.echo(cur_tabs)

@chromectrl_cli.command(help="Focus a tab with the specified URL")
@click.option('-j', '--jsonify', is_flag=True, show_default=True, default=False, help="Display the result as JSON")
@click.argument('url')
@click.pass_context
def focus_tab(ctx, jsonify, url):
    controller = ctx.obj['controller']

    cur_tabs = controller.get_all_tabs()

    for tab in cur_tabs:
        if tab['url'] == url:
            controller.focus_tab(tab['targetId'])

            if jsonify:
                click.echo(tab)
            else:
                click.echo(tab['url'])
            break

@chromectrl_cli.command(help="Send keystroke(s) to the page")
@click.pass_context
@click.argument("keys")
def send_keystroke(ctx, keys):
    controller = ctx.obj['controller']

    controller.send_keystroke(keys)

@chromectrl_cli.command(help="Exit full screen")
@click.pass_context
def exit_fullscreen(ctx):
    controller = ctx.obj['controller']

    rv = controller.evaluate_expression('if (document.exitFullscreen) document.exitFullscreen();')

if __name__ == '__main__':
    chromectrl_cli()