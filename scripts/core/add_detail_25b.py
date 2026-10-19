# -*- coding: utf-8 -*-
"""详情页重建v2: 逐张添加25图, 输入值校验+失败重试。"""
import sys, json, time, base64, os
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
ws,_,_=find_page_ws(); c=CDP(ws)

BASE=sys.path[0]
TARGETS=json.load(open(os.path.join(BASE,"_detail_targets.json"),encoding="utf-8"))

def evalj(expr):
    r=c.eval(expr)
    if isinstance(r,str):
        try:
            return json.loads(r)
        except Exception:
            return r
    return r

def shot(name):
    try:
        cap=c.send("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
        open(os.path.join(BASE,name),"wb").write(base64.b64decode(cap["data"]))
    except Exception as e:
        print("shot fail",e)

def n_images():
    return evalj(r"""(()=>{const p=document.querySelector('.Preview_preview__1wgYD');if(!p)return -1;return [...p.querySelectorAll('img.image')].filter(e=>e.offsetParent&&e.getBoundingClientRect().width>250).length;})()""")

def modal_open():
    return evalj(r"""(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);return modals.length>0;})()""")

def click_plugin():
    pos=evalj(r"""(()=>{
      const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
      const nm=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&(e.textContent||'').trim()==='图片'&&e.getBoundingClientRect().x<500&&e.getBoundingClientRect().y<300);
      if(!nm)return null;
      const r=nm.getBoundingClientRect();
      return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};
    })()""")
    if not pos: return False
    c.real_click(pos["x"],pos["y"])
    for _ in range(15):
        time.sleep(0.6)
        if modal_open(): return True
    return False

def search(name):
    """输入搜索词并点查询, 返回是否成功。带输入值校验。"""
    for attempt in range(3):
        box=evalj(r"""(()=>{
          const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
          const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);
          const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];
          if(!m)return null;
          const sb=[...m.querySelectorAll('input')].find(e=>vis(e)&&(e.placeholder||'').includes('名称'));
          if(!sb)return null;
          const r=sb.getBoundingClientRect();
          return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};
        })()""")
        if not box: return False
        c.real_click(box["x"],box["y"]); time.sleep(0.5)
        # Ctrl+A 全选
        for t in ("rawKeyDown","keyUp"):
            c.send("Input.dispatchKeyEvent",{"type":t,"key":"a","code":"KeyA","modifiers":2,"windowsVirtualKeyCode":65,"nativeVirtualKeyCode":65})
        time.sleep(0.3)
        c.send("Input.insertText",{"text":name}); time.sleep(0.4)
        val=evalj(r"""(()=>{const e=document.activeElement;return e&&e.value!==undefined?String(e.value):null;})()""")
        if str(val)==name:
            break
        print(f"    输入值={val!r} 重试{attempt+1}",flush=True)
    else:
        return False
    q=evalj(r"""(()=>{
      const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
      const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);
      const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];
      if(!m)return null;
      const b=[...m.querySelectorAll('*')].find(e=>e.children.length===0&&(e.textContent||'').trim()==='查询'&&vis(e));
      if(!b)return null;
      const r=b.getBoundingClientRect();
      return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};
    })()""")
    if not q: return False
    c.real_click(q["x"],q["y"]); time.sleep(2.2)
    return True

def pick_card(frag):
    card=evalj(r"""((frag)=>{
      const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
      const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);
      const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];
      if(!m)return null;
      const mr=m.getBoundingClientRect();
      const im=[...m.querySelectorAll('img')].find(im=>vis(im)&&im.getBoundingClientRect().x>mr.x+150&&(im.src||'').includes(frag));
      if(!im)return null;
      const r=im.getBoundingClientRect();
      return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};
    })""" + f"({json.dumps(frag)})")
    if not card: return None
    c.real_click(card["x"],card["y"]); time.sleep(1.0)
    return True

def visible_frags():
    return evalj(r"""(()=>{
      const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
      const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700&&e.getBoundingClientRect().height>400);
      const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];
      if(!m)return [];
      const mr=m.getBoundingClientRect();
      return [...m.querySelectorAll('img')].filter(im=>vis(im)&&im.getBoundingClientRect().x>mr.x+150&&im.getBoundingClientRect().width>30)
        .map(im=>(im.src||'').split('?')[0].split('/').pop()).slice(0,20);
    })()""")

def confirm():
    btn=evalj(r"""(()=>{
      const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
      const s=[...document.querySelectorAll('span')].find(e=>vis(e)&&(e.textContent||'').trim()==='确认'&&e.getBoundingClientRect().y>880&&e.getBoundingClientRect().y<1020);
      if(!s)return null;
      const r=s.getBoundingClientRect();
      return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};
    })()""")
    if not btn: return False
    c.real_click(btn["x"],btn["y"])
    for _ in range(12):
        time.sleep(0.5)
        if not modal_open(): return True
    return True

start=time.time(); total=len(TARGETS); done=0; fail=[]
for idx,t in enumerate(TARGETS,1):
    name=t["name"]; frag=t["frag"]
    # 跳过已添加的: 按当前画布数判断 — 需要知道之前加到哪
    if idx-1<=done and done>0 and False:
        pass
    print(f"[{idx}/{total}] {name} frag={frag}",flush=True)
    if not click_plugin():
        print("  !! 打开选择器失败"); fail.append((name,"plugin")); break
    time.sleep(0.5)
    if not search(name):
        print("  !! 搜索失败"); fail.append((name,"search")); continue
    card=pick_card(frag)
    if card is None:
        print("  !! 未找到目标卡, 可见:",visible_frags()[:10])
        # 重试一次搜索
        c.eval(r"""(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>700);const m=modals.sort((a,b)=>b.getBoundingClientRect().width-a.getBoundingClientRect().width)[0];const x=m.querySelector('[class*=headerClose],[class*=HeaderClose]');if(x)x.click();})()""")
        time.sleep(1)
        if not click_plugin(): fail.append((name,"reopen")); continue
        if not search(name): fail.append((name,"search2")); continue
        card=pick_card(frag)
        if card is None:
            print("  !! 重试仍失败"); fail.append((name,"card")); continue
    if not confirm():
        print("  !! 确认失败"); fail.append((name,"confirm")); continue
    done+=1
    if done%3==0 or done==total:
        print(f"  进度: 画布图数={n_images()} 用时={int(time.time()-start)}s",flush=True)

print(f"\n完成 {done}/{total}, 失败 {fail}")
print("最终画布图数:",n_images())
shot("detail_after_add2.png")
c.close()
