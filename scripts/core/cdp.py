# -*- coding: utf-8 -*-
"""极简 Chrome DevTools Protocol 客户端：连接系统Edge(9223)的PDD标签页。
支持 eval(JS) / navigate / 上传文件。系统Edge需带 --remote-debugging-port=9223 启动。
"""
import json, time, urllib.request, itertools, os
import websocket  # websocket-client

CDP_HTTP = "http://127.0.0.1:9223"

def _http_json(url):
    with urllib.request.urlopen(url, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))

def find_page_ws(url_contains="mms.pinduoduo.com", prefer="goods_add"):
    """返回(页面wsUrl, pageId, url)。优先选编辑页，其次任意mms页。"""
    targets = _http_json(CDP_HTTP + "/json")
    pages = [t for t in targets if t.get("type") == "page" and url_contains in t.get("url", "")]
    if not pages:
        return None, None, None
    edit = [t for t in pages if prefer in t.get("url", "")]
    t = edit[0] if edit else pages[0]
    return t["webSocketDebuggerUrl"], t["id"], t["url"]

def new_tab(url):
    """通过 /json/new 开新标签（旧版Chrome支持PUT/GET）。返回pageId。"""
    try:
        with urllib.request.urlopen(CDP_HTTP + "/json/new?" + urllib.parse.quote(url, safe=":/?=&"), timeout=8) as r:
            return json.loads(r.read().decode())["id"]
    except Exception:
        # Chrome 155 需 PUT
        req = urllib.request.Request(CDP_HTTP + "/json/new?" + urllib.parse.quote(url, safe=":/?=&"), method="PUT")
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read().decode())["id"]

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, max_receive_message_size=64*1024*1024,
                                              timeout=60, suppress_origin=True)
        self._ids = itertools.count(1)
        self._file_node = None  # 文档根节点，用于 DOM.setFileInputFiles

    def send(self, method, params=None, timeout=60):
        mid = next(self._ids)
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        end = time.time() + timeout
        while time.time() < end:
            self.ws.settimeout(max(0.5, end - time.time()))
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method} error: {msg['error']}")
                return msg.get("result", {})
        raise TimeoutError(method)

    def eval(self, expression, await_promise=True, return_by_value=True, timeout=60):
        r = self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": return_by_value,
            "awaitPromise": await_promise,
        }, timeout=timeout)
        if "exceptionDetails" in r:
            exc = r["exceptionDetails"].get("exception", {})
            raise RuntimeError("JS异常: " + str(exc.get("description", r["exceptionDetails"])))
        return r.get("result", {}).get("value")

    def real_click(self, x, y):
        """在页面视口坐标(CSS像素)派发真实鼠标事件，用于React开关等DOM.click失效的元素。"""
        for t, kw in [
            ("mouseMoved", {}),
            ("mousePressed", {"button": "left", "buttons": 1, "clickCount": 1}),
            ("mouseReleased", {"button": "left", "buttons": 0, "clickCount": 1}),
        ]:
            p = {"type": t, "x": float(x), "y": float(y)}
            p.update(kw)
            self.send("Input.dispatchMouseEvent", p)

    def click_rect(self, rect):
        """对getBoundingClientRect返回的{left,top,width,height}中心真实点击。"""
        self.real_click(rect["left"] + rect["width"] / 2, rect["top"] + rect["height"] / 2)

    def navigate(self, url, wait=2.5):
        self.send("Page.enable")
        self.send("Page.navigate", {"url": url})
        time.sleep(wait)

    def upload(self, selector, abspath):
        """给选择器对应的 file input 赋文件。selector 为 CSS。"""
        doc = self.send("DOM.getDocument", {"depth": 0})
        root = doc["root"]["nodeId"]
        q = self.send("DOM.querySelector", {"nodeId": root, "selector": selector})
        node = q["nodeId"]
        if not node:
            raise RuntimeError("找不到 file input: " + selector)
        self.send("DOM.setFileInputFiles", {"files": [os.path.abspath(abspath)], "nodeId": node})

    def close(self):
        try: self.ws.close()
        except: pass

    # ========== 新增功能 ==========

    def drag(self, x1, y1, x2, y2, steps=20):
        """拖拽：从(x1,y1)拖到(x2,y2)，用于装修商详组件拖拽。"""
        # mouse press at start
        self.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": float(x1), "y": float(y1)})
        self.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": float(x1), "y": float(y1), "button": "left", "buttons": 1, "clickCount": 1})
        # move in steps
        for i in range(1, steps + 1):
            x = x1 + (x2 - x1) * i / steps
            y = y1 + (y2 - y1) * i / steps
            self.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": float(x), "y": float(y), "button": "left", "buttons": 1})
            time.sleep(0.02)
        # mouse release at end
        self.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": float(x2), "y": float(y2), "button": "left", "buttons": 0, "clickCount": 1})

    def scroll(self, x, y, delta_y, delta_x=0):
        """滚动页面。delta_y正数向下，负数向上。"""
        self.send("Input.dispatchMouseEvent", {
            "type": "mouseWheel",
            "x": float(x), "y": float(y),
            "deltaX": float(delta_x), "deltaY": float(delta_y),
        })

    def type_text(self, text):
        """键盘输入文字。"""
        for ch in text:
            self.send("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "text": ch,
                "key": ch,
                "windowsVirtualKeyCode": ord(ch),
            })
            self.send("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "key": ch,
                "windowsVirtualKeyCode": ord(ch),
            })

    def wait_for(self, js_condition, timeout=30, interval=0.5):
        """等待JS条件为true。js_condition是一段返回boolean的JS表达式。"""
        end = time.time() + timeout
        while time.time() < end:
            try:
                r = self.eval(js_condition, await_promise=False)
                if r:
                    return True
            except:
                pass
            time.sleep(interval)
        raise TimeoutError(f"wait_for timeout: {js_condition[:80]}")

    def inject_stealth(self):
        """注入反检测JS，隐藏自动化痕迹。"""
        js = """
        (function(){
          try {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
          } catch(e) {}
          window.chrome = {runtime: {}};
          try {
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
          } catch(e) {}
          try {
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
          } catch(e) {}
          try {
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
              parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
            );
          } catch(e) {}
        })();
        """
        self.eval(js, await_promise=False)
        self.send("Page.addScriptToEvaluateOnNewDocument", {"source": js})

if __name__ == "__main__":
    ws, pid, url = find_page_ws()
    print("page:", pid, url)
    c = CDP(ws)
    print("title:", c.eval("document.title"))
    print("url:", c.eval("location.href"))
    c.close()
