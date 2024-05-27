# Chrome Controller
This project is meant to automate the process of opening and closing tabs on a running instance of Chrome.

In general, it should operate on a list of URLs, which it will open on a running Chromium instance in the sequence they are given.

It should have an options for how these new tabs are opened in relation to existing tabs:
    - right (default): the tabs are opened to the right of
    existing tabs
    - left: the tabs are opened to the left of existing tabs
    - clean: existing tabs are closed after new tabs are opened

Alternatively, it should be able to set the focus of a given URL in a tab which is already opened.

Test commands:

**POST focus**
```
curl -X POST -H 'Content-Type: application/json' -d '{"tabId": "73463BCBE4D7438457B6451EE3AC082D"}' http://127.0.0.1:5000/focus
```

**GET tabs**
```
curl -X GET http://127.0.0.1:5000/tabs
```

**POST tabs**
```
curl -X POST -H 'Content-Type: application/json' -d '{"action":"open-right", "urls": ["https://archlinux.org"]}' http://127.0.0.1:5000/tabs

curl -X POST -H 'Content-Type: application/json' -d '{"action":"close-others", "urls": ["https://archlinux.org"]}' http://127.0.0.1:5000/tabs

# 'open-left' is currently non-functional
curl -X POST -H 'Content-Type: application/json' -d '{"action":"open-left", "urls": ["https://archlinux.org"]}' http://127.0.0.1:5000/tabs
```

The PATCH thing is currently not working.
```
curl -X PATCH -H 'Content-Type: application/json' -d '{"action":"close-others", "tabs": [{ "tabPos": 0, "url": "https://chiliahedron.wtf/" }]}' http://127.0.0.1:5000/tabs
```