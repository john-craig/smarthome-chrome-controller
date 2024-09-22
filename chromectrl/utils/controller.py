import PyChromeDevTools
from websocket._exceptions import WebSocketConnectionClosedException

class Controller:
    def __init__(self, port=9222, logger=None):
        self.port = port
        self.chrome = PyChromeDevTools.ChromeInterface(port=port)
        self.logger = logger


    def get_tab_id(self, url=""):
        ret_val, messages = self.chrome.Target.getTargets()
        tab_info = ret_val['result']['targetInfos']

        for tab in tab_info:
            if tab['url'].startswith(url):
                return tab['targetId']
        
        return None

    def set_tab_url(self, tab_id, url, verbose=False):
        if verbose:
            print(f"Setting URL of tab with ID {tab_id} to {url}")

        try:
            self.chrome.Target.activateTarget(targetId=tab_id)

            self.chrome.Page.navigate(url=url)
        except WebSocketConnectionClosedException as e:
            self.chrome = PyChromeDevTools.ChromeInterface(port=self.port)
            return self.set_tab_url(tab_id, url, verbose)
        
    def open_tab(self, url, verbose=False):
        if verbose:
            print(f"Opening new tab with URL: {url}")

        try:
            ret_val, messages = self.chrome.Target.createTarget(url=url)
        except WebSocketConnectionClosedException as e:
            self.chrome = PyChromeDevTools.ChromeInterface(port=self.port)
            return self.open_tab(url, verbose)

        if verbose:
            print(f"  Result: {ret_val}")

        return ret_val['result']['targetId']

    def close_tab(self, tab_id, verbose=False):
        if verbose:
            print(f"Closing tab with ID: {tab_id}")

        try:
            ret_val, messages = self.chrome.Target.closeTarget(targetId=tab_id)
        except WebSocketConnectionClosedException as e:
            self.chrome = PyChromeDevTools.ChromeInterface(port=self.port)
            return self.close_tab(tab_id, verbose)

        if verbose:
            print(f"  Result: {ret_val}")

        if ret_val:
            return ret_val['result']

    def focus_tab(self, tab_id, verbose=False):
        self.chrome.Target.activateTarget(targetId=tab_id)

    ####

    def get_all_tabs(self):
        try:
            ret_val, messages = self.chrome.Target.getTargets()
        except WebSocketConnectionClosedException as e:
            self.chrome = PyChromeDevTools.ChromeInterface(port=self.port)
            return self.get_all_tabs()
        
        # This gets returned based on the order the tabs were opened (e.g., right to left)
        # but it is far more intuitive to want it in the order the tabs appear in the browser
        # (e.g., right to left)
        tab_info = list(reversed(ret_val['result']['targetInfos']))

        return tab_info
    
    def send_keystroke(self, keystroke):
        try:
            ret_val, messages = self.chrome.Input.dispatchKeyEvent(type='rawKeyDown', text=keystroke)
        except WebSocketConnectionClosedException as e:
            self.chrome = PyChromeDevTools.ChromeInterface(port=self.port)
            return self.send_keystroke(keystroke)
        
        return ret_val

    def evaluate_expression(self, expression):
        try:
            ret_val, messages = self.chrome.Runtime.evaluate(expression=expression)
        except WebSocketConnectionClosedException as e:
            self.chrome = PyChromeDevTools.ChromeInterface(port=self.port)
            return self.evaluate_expression(expression)
        
        return ret_val