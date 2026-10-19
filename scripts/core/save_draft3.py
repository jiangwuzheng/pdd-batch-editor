# -*- coding: utf-8 -*-
"""点保存草稿并快速轮询'保存成功'提示。"""
import sys, json, time, base64, os
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
ws,_,_=find_page_ws(); c=CDP(ws)

def evalj(expr):
    r=c.eval(expr)
    if isinstance(r,str):
        try: return json.loads(r)
        except Exception: return r
    return r

# 点保存草稿
pos=evalj(r"""(()=>{
  const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
  const s=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&vis(e)&&(e.textContent||'').trim()==='保存草稿'&&e.getBoundingClientRect().y>1250);
  if(!s)return null;
  const r=s.getBoundingClientRect();
  return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};
})()""")
print("按钮:",pos)
if not pos: c.close(); sys.exit(1)
c.real_click(pos["x"],pos["y"])
# 快速轮询提示与弹窗
found=None
for i in range(20):
    time.sleep(0.4)
    r=evalj(r"""(()=>{
      const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
      const tips=[...document.querySelectorAll('*')].filter(e=>vis(e)&&e.children.length===0&&(e.textContent||'').trim().match(/保存成功|发布成功|失败|错误/)).map(e=>e.textContent.trim()).slice(0,4);
      const btns=[...document.querySelectorAll('*')].filter(e=>vis(e)&&e.children.length===0&&['确定','确认'].includes((e.textContent||'').trim())&&e.getBoundingClientRect().y>300&&e.getBoundingClientRect().y<1000).map(e=>{const r=e.getBoundingClientRect();return {t:e.textContent.trim(),x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)}});
      return {tips,btns:btns.slice(0,3)};
    })()""")
    if r.get("btns"):
        b=r["btns"][0]
        print(f"  第{i}轮: 弹窗按钮 {b}")
        c.real_click(b["x"],b["y"])
        found=r.get("tips"); time.sleep(0.6)
        # 弹窗后继续轮询提示
        for j in range(8):
            time.sleep(0.4)
            r2=evalj(r"""(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const t=[...document.querySelectorAll('*')].filter(e=>vis(e)&&e.children.length===0&&(e.textContent||'').trim().match(/保存成功|发布成功|失败/)).map(e=>e.textContent.trim());return t.slice(0,4);})()""")
            if r2: print(f"    弹窗后提示: {r2}")
        break
    if r.get("tips"):
        found=r["tips"]; print(f"  第{i}轮: 提示 {found}"); break
print("最终提示:",found)
cap=c.send("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
open(os.path.join(sys.path[0],"draft_saved_check.png"),"wb").write(base64.b64decode(cap["data"]))
c.close()
