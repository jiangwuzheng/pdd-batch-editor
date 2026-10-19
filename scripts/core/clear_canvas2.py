# -*- coding: utf-8 -*-
"""强制关闭所有打开的选择器弹窗, 再点清空。"""
import sys, json, time, base64, os
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
ws,_,_=find_page_ws(); c=CDP(ws)

def evalj(expr):
    r=c.eval(expr)
    return json.loads(r) if isinstance(r,str) else r

def n_images():
    return evalj(r"""(()=>{const p=document.querySelector('.Preview_preview__1wgYD');if(!p)return -1;return [...p.querySelectorAll('img.image')].filter(e=>e.offsetParent&&e.getBoundingClientRect().width>250).length;})()""")

# 1. dump 所有可见大弹窗
ms=evalj(r"""(()=>{
  const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
  return [...document.querySelectorAll('[class*=MDL_outerWrapper],[class*=modal i],[class*=Modal i],[class*=dialog i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>300&&e.getBoundingClientRect().height>150)
    .map(m=>{const r=m.getBoundingClientRect();return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),cls:(m.className||'').toString().slice(0,50)}});
})()""")
print("弹窗:",json.dumps(ms,ensure_ascii=False))
# 2. 找所有'取消'/'确认'/'关闭×' 可点元素
spans=evalj(r"""(()=>{
  const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
  const hits=[];
  [...document.querySelectorAll('span,i,svg,button')].forEach(e=>{
    if(!vis(e))return;
    const r=e.getBoundingClientRect();
    const t=(e.textContent||'').trim();
    if((t==='取消'||t==='确认')&&r.y>850&&r.y<1100){
      hits.push({t,tag:e.tagName,x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),w:Math.round(r.width)});
    }
  });
  return hits;
})()""")
print("底部按钮:",json.dumps(spans,ensure_ascii=False))
# 3. 点第一个取消(关选择器)
closed=False
for s in spans:
    if s["t"]=="取消":
        c.real_click(s["x"],s["y"]); time.sleep(2); closed=True; print("已点取消",s); break
if not closed:
    # 找 modal 的 ×
    x=evalj(r"""(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const m=[...document.querySelectorAll('[class*=MDL_headerClose],[class*=headerClose]')].find(e=>vis(e));if(!m)return null;const r=m.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})()""")
    if x:
        c.real_click(x["x"],x["y"]); time.sleep(2); print("已点关闭×",x)
print("当前图数:",n_images())
# 4. 再点清空
qk=evalj(r"""(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const s=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&vis(e)&&(e.textContent||'').trim()==='清空'&&e.getBoundingClientRect().y>1250);if(!s)return null;const r=s.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})()""")
print("清空按钮:",qk)
if qk:
    c.real_click(qk["x"],qk["y"]); time.sleep(2)
    cfm=evalj(r"""(()=>{const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;const s=[...document.querySelectorAll('*')].find(e=>vis(e)&&e.children.length===0&&(e.textContent||'').trim()==='确认'&&e.getBoundingClientRect().y>1150&&e.getBoundingClientRect().y<1350);if(!s)return null;const r=s.getBoundingClientRect();return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};})()""")
    print("清空确认框:",cfm)
    if cfm:
        c.real_click(cfm["x"],cfm["y"]); time.sleep(3)
print("清空后图数:",n_images())
c.close()
