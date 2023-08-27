import PyChromeDevTools


class Controller:
    def __init__(self, chrome_pid):
        self.chrome_pid = chrome_pid
        self.chrome = PyChromeDevTools.ChromeInterface()


    def get_tab_id(self, url=""):
        ret_val, messages = self.chrome.Target.getTargets()
        tab_info = ret_val['result']['targetInfos']

        for tab in tab_info:
            if tab['url'].startswith(url):
                return tab['targetId']
        
        return None

    def set_tab_url(self, tab_id, url):
        self.chrome.Target.activateTarget(targetId=tab_id)
        self.chrome.Page.navigate(url=url)

    def open_tab(self, url):
        ret_val, messages = self.chrome.Target.createTarget(url=url)

        return ret_val['result']['targetId']

