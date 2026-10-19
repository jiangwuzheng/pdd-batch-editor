# -*- coding: utf-8 -*-
"""保存装修(点编辑器底部'保存'), 确认编辑器关闭。"""
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

# 找底部'保存'(y>1250) - 装修编辑器的保存
btn=evalj(r"""(()=>{
  const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
  const s=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&vis(e)&&(e.textContent||'').trim()==='保存'&&e.getBoundingClientRect().y>1250);
  if(!s)return null;
  const r=s.getBoundingClientRect();
  return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};
})()""")
print("装修保存按钮:",btn)
if not btn: c.close(); sys.exit(1)
c.real_click(btn["x"],btn["y"]); time.sleep(3)
# 检查编辑器是否关闭(预览容器消失)
st=evalj(r"""(()=>{const p=document.querySelector('.Preview_preview__1wgYD');const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const modals=[...document.querySelectorAll('[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>300&&e.getBoundingClientRect().height>100);return {preview:!!p,modals:modals.map(m=>(m.textContent||'').trim().slice(0,40)).slice(0,3)};})()""")
print("保存后状态:",json.dumps(st,ensure_ascii=False))
tips=evalj(r"""(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const all=[...document.querySelectorAll('*')].filter(e=>vis(e)&&e.children.length===0&&(e.textContent||'').trim().includes('保存成功'));return all.map(e=>e.textContent.trim()).slice(0,3);})()""")
print("保存提示:",tips)
cap=c.send("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
open(os.path.join(sys.path[0],"after_save_decor.png"),"wb").write(base64.b64decode(cap["data"]))
c.close()
