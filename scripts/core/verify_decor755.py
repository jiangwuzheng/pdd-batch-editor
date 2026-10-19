# -*- coding: utf-8 -*-
import sys, json, os, urllib.request
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, CDP_HTTP
def pages(): return json.loads(urllib.request.urlopen(CDP_HTTP+"/json",timeout=8).read())
t=[x for x in pages() if x.get("type")=="page" and "755487448180" in x.get("url","") and "goods_add/index" in x.get("url","")]
wsurl=t[0]["webSocketDebuggerUrl"]; c=CDP(wsurl)
BASE=sys.path[0]
TARGETS=json.load(open(os.path.join(BASE,"_detail_targets.json"),encoding="utf-8"))
r=c.eval("(()=>{const p=document.querySelector('.Preview_preview__1wgYD');if(!p)return [];const imgs=[...p.querySelectorAll('img.image')].filter(e=>e.offsetParent&&e.getBoundingClientRect().width>250).map(im=>({y:Math.round(im.getBoundingClientRect().top),src:(im.src||'').split('?')[0]})).sort((a,b)=>a.y-b.y);return imgs;})()")
canvas=json.loads(r) if isinstance(r,str) else r
print("画布图数:",len(canvas))
ok=0; bad=[]
for i,t in enumerate(TARGETS):
    exp=t["frag"].split(".")[0]
    act=canvas[i]["src"].split("/")[-1].split(".")[0] if i<len(canvas) else "MISSING"
    if exp==act: ok+=1
    else: bad.append((i+1,t["name"],exp,act))
print("顺序匹配 %d/25"%ok)
for b in bad: print("  不一致:",b)
c.close()