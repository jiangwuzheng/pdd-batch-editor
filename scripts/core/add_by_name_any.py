# -*- coding: utf-8 -*-
"""718 按名字挨个点（参数化自 add_by_name_755.py）: 开选择器->树导航进ai批量上传->翻页->按名字点卡->确认。幂等。"""
import sys, json, time, base64, os, urllib.request
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, CDP_HTTP
BASE=sys.path[0]
GID=sys.argv[1] if len(sys.argv)>1 else "718003403072"
def pages(): return json.loads(urllib.request.urlopen(CDP_HTTP+"/json",timeout=8).read())
t=[x for x in pages() if x.get("type")=="page" and GID in x.get("url","") and "goods_add/index" in x.get("url","")]
if not t:
    print("!! 没有",GID,"编辑页tab"); sys.exit(1)
wsurl=t[0]["webSocketDebuggerUrl"]; c=CDP(wsurl)
def evalj(expr):
    r=c.eval(expr)
    if isinstance(r,str):
        try: return json.loads(r)
        except Exception: return r
    return r
def shot(name):
    try:
        cap=c.send("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
        open(os.path.join(BASE,name),"wb").write(base64.b64decode(cap["data"]))
    except Exception as e: print("shot fail",e)
def modal_open():
    return evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);return modals.length>0;})()")
def get_modal():
    return evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);if(!modals.length)return null;const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];return m;})()")
def canvas_frags():
    return evalj("(()=>{const p=document.querySelector('.Preview_preview__1wgYD');if(!p)return [];return [...p.querySelectorAll('img.image')].filter(e=>e.offsetParent&&e.getBoundingClientRect().width>250).map(im=>(im.src||'').split('?')[0].split('/').pop().split('.')[0].slice(0,12));})()")
def click_plugin():
    p=evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const nm=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&(e.textContent||'').trim()==='图片'&&e.getBoundingClientRect().x<500&&e.getBoundingClientRect().y<300&&e.getBoundingClientRect().width>30);if(!nm)return null;const r=nm.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})()")
    if not p: return False
    c.real_click(p["x"],p["y"])
    for _ in range(15):
        time.sleep(0.6)
        if modal_open(): return True
    return False
def find_node(name_part):
    return evalj("((np)=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);if(!modals.length)return null;const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];const nodes=[...m.querySelectorAll('[class*=Tree_treeNode]')].filter(vis);const target=nodes.find(e=>{const t=e.querySelector('[class*=Tree_labelWrapper]');return t&&(t.textContent||'').trim().includes(np);});if(!target)return null;target.scrollIntoView({block:'center'});const t=target.querySelector('[class*=Tree_labelWrapper]');const ic=target.querySelector('[class*=Tree_iconWrapper]');const tr=t.getBoundingClientRect();const r=target.getBoundingClientRect();const ir=ic?ic.getBoundingClientRect():null;return {name:(t.textContent||'').trim(),arrow:ir?{x:Math.round(ir.x+ir.width/2),y:Math.round(ir.y+ir.height/2)}:null,text:{x:Math.round(tr.x+tr.width/2),y:Math.round(tr.y+tr.height/2)}};})"+f"({json.dumps(name_part)})")
def mclick(pt):
    c.send("Input.dispatchMouseEvent",{"type":"mousePressed","x":pt["x"],"y":pt["y"],"button":"left","clickCount":1})
    c.send("Input.dispatchMouseEvent",{"type":"mouseReleased","x":pt["x"],"y":pt["y"],"button":"left","clickCount":1})
    time.sleep(1.8)
def nav_to_ai():
    found=False
    for _w in range(12):
        if find_node('手电筒造影灯罩组合'):
            found=True; break
        time.sleep(0.8)
    print("  树加载:",found,flush=True)
    n2=find_node("详情页2")
    if not n2 or not n2["arrow"]:
        n=find_node("手电筒造影灯罩组合")
        if not n or not n["arrow"]:
            print("  !! 无手电筒造影节点",flush=True); return False
        mclick(n["arrow"])
        n2=None
        for _r in range(6):
            n2=find_node("详情页2")
            if n2 and n2["arrow"]: break
            time.sleep(0.8)
    if not n2 or not n2["arrow"]:
        print("  !! 展开后无详情页2节点",flush=True); return False
    n3=find_node("ai批量上传")
    if not n3 or not n3["text"]:
        mclick(n2["arrow"])
        n3=None
        for _r in range(6):
            n3=find_node("ai批量上传")
            if n3 and n3["text"]: break
            time.sleep(0.8)
    if not n3 or not n3["text"]:
        print("  !! 无ai批量上传节点",flush=True); return False
    mclick(n3["text"])
    time.sleep(1.0)
    return True
def goto_page(pg):
    p=evalj("((pg)=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);if(!modals.length)return null;const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];const s=[...m.querySelectorAll('*')].find(e=>e.children.length===0&&vis(e)&&(e.textContent||'').trim()===String(pg)&&e.getBoundingClientRect().y>850&&e.getBoundingClientRect().width<60);if(!s)return null;const r=s.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})"+f"({pg})")
    if not p: return False
    c.real_click(p["x"],p["y"])
    time.sleep(1.8)
    return True
def find_card_by_name(cardname):
    return evalj("((cn)=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);if(!modals.length)return null;const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];const mr=m.getBoundingClientRect();const s=[...m.querySelectorAll('*')].find(e=>e.children.length===0&&vis(e)&&(e.textContent||'').trim()===cn&&e.getBoundingClientRect().x>mr.x+150);if(!s)return null;const r=s.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})"+f"({json.dumps(cardname)})")
def confirm():
    btn=evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const s=[...document.querySelectorAll('span')].find(e=>vis(e)&&(e.textContent||'').trim()==='确认'&&e.getBoundingClientRect().y>880&&e.getBoundingClientRect().y<1020);if(!s)return null;const r=s.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})()")
    if not btn: return False
    c.real_click(btn["x"],btn["y"])
    for _ in range(12):
        time.sleep(0.5)
        if not modal_open(): return True
    return True
def page_of_card(cardname):
    for pg,cards in PICKER.items():
        for cd in cards:
            if cd["t"]==cardname:
                return pg
    return None
TARGETS=json.load(open(os.path.join(BASE,"_detail_targets.json"),encoding="utf-8"))
PICKER=json.load(open(os.path.join(BASE,"_picker_cards_755.json"),encoding="utf-8"))
PICKER={int(k):v for k,v in PICKER.items()}
def cardname_of(t):
    ext=".png" if t["frag"].endswith(".png") else ".jpeg"
    return t["name"]+ext
if modal_open():
    btn=evalj("(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const s=[...document.querySelectorAll('span')].find(e=>vis(e)&&(e.textContent||'').trim()==='取消'&&e.getBoundingClientRect().y>880&&e.getBoundingClientRect().y<1020);if(!s)return null;const r=s.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})()")
    if btn:
        c.real_click(btn["x"],btn["y"]); time.sleep(1.5)
        print("已关旧选择器")
have=set(canvas_frags())
todo=[t for t in TARGETS if t["frag"].split(".")[0][:12] not in have]
print("画布已有 %d 张, 待补 %d 张"%(len(have),len(todo)),flush=True)
for t in todo:
    cn=cardname_of(t)
    pg=page_of_card(cn)
    print("[补] %s (页%d)"%(cn,pg),flush=True)
    if not click_plugin():
        print("  !! 选择器打开失败, 停止"); break
    time.sleep(0.5)
    if not nav_to_ai():
        print("  !! 树导航失败, 停止"); break
    if pg and not goto_page(pg):
        print("  !! 翻页失败(页%d)"%pg); break
    card=find_card_by_name(cn)
    if not card:
        for _p in (p for p in (1,2,3) if p!=pg):
            goto_page(_p)
            card=find_card_by_name(cn)
            if card: break
    if not card:
        print("  !! 未找到 %s, 停止"%cn); shot("by_name_fail.png"); break
    c.real_click(card["x"],card["y"]); time.sleep(1.0)
    if not confirm():
        print("  !! 确认失败, 停止"); break
    have.add(t["frag"].split(".")[0][:12])
    print("  画布=%d/25"%(len(canvas_frags())),flush=True)
print("结束: 画布 %d/25"%(len(canvas_frags())))
shot("by_name_progress.png")
c.close()
