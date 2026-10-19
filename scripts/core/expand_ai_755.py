# -*- coding: utf-8 -*-
import sys, json, time, base64, os, urllib.request
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, CDP_HTTP
BASE=sys.path[0]
def pages(): return json.loads(urllib.request.urlopen(CDP_HTTP+"/json",timeout=8).read())
t=[x for x in pages() if x.get("type")=="page" and "755487448180" in x.get("url","") and "goods_add/index" in x.get("url","")]
wsurl=t[0]["webSocketDebuggerUrl"]; c=CDP(wsurl)
def evalj(expr):
    r=c.eval(expr)
    if isinstance(r,str):
        try: return json.loads(r)
        except Exception: return r
    return r
def modal_open():
    return evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);return modals.length>0;})()")
def click_plugin():
    p=evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const nm=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&(e.textContent||'').trim()==='图片'&&e.getBoundingClientRect().x<500&&e.getBoundingClientRect().y<300&&e.getBoundingClientRect().width>30);if(!nm)return null;const r=nm.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})()")
    if not p: return False
    c.real_click(p["x"],p["y"])
    for _ in range(15):
        time.sleep(0.6)
        if modal_open(): return True
    return False
def tree_names():
    return evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);if(!modals.length)return [];const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];const nodes=[...m.querySelectorAll('[class*=Tree_treeNode]')].filter(vis);const out=[];for(const e of nodes){const t=e.querySelector('[class*=Tree_labelWrapper]');const ic=e.querySelector('[class*=Tree_iconWrapper]');const r=e.getBoundingClientRect();const ir=ic?ic.getBoundingClientRect():null;const tr=t?t.getBoundingClientRect():null;out.push({name:(t?t.textContent:'').trim(),y:Math.round(r.y),arrow:ir?{x:Math.round(ir.x+ir.width/2),y:Math.round(ir.y+ir.height/2)}:null,text:tr?{x:Math.round(tr.x+tr.width/2),y:Math.round(tr.y+tr.height/2)}:null});}return out;})()")
def scroll_tree():
    return evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];if(!m)return 'no-modal';const nodes=[...m.querySelectorAll('[class*=Tree_treeNode]')].filter(vis);let cur=nodes[0];for(let i=0;i<6&&cur;i++){const cs=getComputedStyle(cur);if(cs.overflowY==='auto'||cs.overflowY==='scroll'||cur.scrollHeight>cur.clientHeight+10){cur.scrollTop=cur.scrollHeight;return 'scrolled:'+cur.scrollTop+'/'+cur.scrollHeight;}cur=cur.parentElement;}return 'no-scroll';})()")
def mclick(pt):
    c.send("Input.dispatchMouseEvent",{"type":"mousePressed","x":pt["x"],"y":pt["y"],"button":"left","clickCount":1})
    c.send("Input.dispatchMouseEvent",{"type":"mouseReleased","x":pt["x"],"y":pt["y"],"button":"left","clickCount":1})
    time.sleep(2.2)
if not modal_open():
    print("重开选择器:",click_plugin())
time.sleep(0.5)
print("滚动树:",scroll_tree())
time.sleep(1.0)
tn=tree_names()
print("滚动后树末8:",json.dumps(tn[-8:],ensure_ascii=False))
node=[x for x in tn if "手电筒造影" in x["name"]]
if node:
    n=node[0]
    print("手电筒造影:",json.dumps(n,ensure_ascii=False))
    if n["arrow"]:
        mclick(n["arrow"])
    tn2=tree_names()
    print("展开后新增:",[x["name"] for x in tn2 if "详情" in x["name"] or "ai" in x["name"] or "SKU" in x["name"] or "sku" in x["name"]])
    d2=[x for x in tn2 if "详情页" in x["name"]]
    if d2:
        print("详情页:",json.dumps(d2,ensure_ascii=False))
        if d2[0]["arrow"]:
            mclick(d2[0]["arrow"])
        ai=[x for x in tree_names() if "ai批量" in x["name"]]
        print("ai:",json.dumps(ai,ensure_ascii=False))
        if ai and ai[0]["text"]:
            mclick(ai[0]["text"])
            cards=evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);if(!modals.length)return [];const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];const mr=m.getBoundingClientRect();return [...m.querySelectorAll('*')].filter(e=>e.children.length===0&&vis(e)&&/\\.(jpe?g|png|gif)$/i.test((e.textContent||'').trim())&&e.getBoundingClientRect().x>mr.x+150).slice(0,15).map(e=>{const r=e.getBoundingClientRect();return {t:e.textContent.trim(),x:Math.round(r.x),y:Math.round(r.y)};});})()")
            print("ai文件夹卡片:",json.dumps(cards,ensure_ascii=False))
            cap=c.send("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
            open(os.path.join(BASE,"picker_755_ai.png"),"wb").write(base64.b64decode(cap["data"]))
else:
    print("未找到节点; 树末10:",json.dumps([x["name"] for x in tn[-10:]],ensure_ascii=False))
c.close()