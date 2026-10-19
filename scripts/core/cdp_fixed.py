# -*- coding: utf-8 -*-
"""固定goods_id的CDP连接。用法: from cdp_fixed import open_goods; c=open_goods('761729958760')"""
import json, time, urllib.request, websocket

CDP_HTTP = "http://127.0.0.1:9222"

def list_tabs():
    return json.loads(urllib.request.urlopen(CDP_HTTP+"/json", timeout=8).read().decode())

def open_goods(goods_id, session_id=None):
    ts = list_tabs()
    if session_id:
        pages = [t for t in ts if t.get("type")=="page" and f"id={session_id}" in t.get("url","")]
    else:
        pages = [t for t in ts if t.get("type")=="page" and "goods_add" in t.get("url","")]
    if not pages:
        raise RuntimeError(f"找不到 tab: session={session_id}")
    t = pages[0]
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], max_receive_message_size=64*1024*1024, timeout=60, suppress_origin=True)
    import itertools
    c = _Conn(ws)
    c.send("DOM.enable")
    c.send("Page.enable")
    # verify
    url = c.eval("location.href")
    print(f"[OK] connected to {url[:100]}")
    return c

class _Conn:
    def __init__(self, ws):
        self.ws = ws
        import itertools
        self._ids = itertools.count(1)
    def send(self, method, params=None, timeout=60):
        mid = next(self._ids)
        self.ws.send(json.dumps({"id":mid,"method":method,"params":params or {}}))
        end = time.time()+timeout
        while time.time()<end:
            self.ws.settimeout(max(0.5, end-time.time()))
            msg = json.loads(self.ws.recv())
            if msg.get("id")==mid:
                if "error" in msg: raise RuntimeError(msg["error"])
                return msg.get("result",{})
        raise TimeoutError(method)
    def eval(self, expr, await_promise=True, timeout=60):
        r = self.send("Runtime.evaluate", {"expression":expr, "returnByValue":True, "awaitPromise":await_promise}, timeout=timeout)
        if "exceptionDetails" in r:
            raise RuntimeError(str(r["exceptionDetails"]))
        return r.get("result",{}).get("value")
    def real_click(self, x, y):
        for t,kw in [("mouseMoved",{}),("mousePressed",{"button":"left","buttons":1,"clickCount":1}),("mouseReleased",{"button":"left","buttons":0,"clickCount":1})]:
            p={"type":t,"x":float(x),"y":float(y)}; p.update(kw)
            self.send("Input.dispatchMouseEvent", p)
    def upload(self, selector, abspath):
        import os
        doc = self.send("DOM.getDocument", {"depth":0})
        root = doc["root"]["nodeId"]
        q = self.send("DOM.querySelector", {"nodeId":root,"selector":selector})
        node = q["nodeId"]
        if not node: raise RuntimeError("no file input")
        self.send("DOM.setFileInputFiles", {"files":[os.path.abspath(abspath)],"nodeId":node})
    def close(self):
        try: self.ws.close()
        except: pass
