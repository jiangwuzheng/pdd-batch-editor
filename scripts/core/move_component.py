# -*- coding: utf-8 -*-
"""装修主画布移动组件顺序。用法: python move_component.py <图URL片段> <up/down> <次数> [tag]"""
import sys, json, time, base64, os
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
URL=sys.argv[1]; DIR=sys.argv[2]; N=int(sys.argv[3]); tag=sys.argv[4] if len(sys.argv)>4 else "move"
ws,_,_=find_page_ws(); c=CDP(ws)
def select_comp():
    return c.eval(r"""(()=>{
      const pv=document.querySelector('.Preview_preview__1wgYD');
      const imgs=[...pv.querySelectorAll('img')].filter(i=>i.naturalWidth>200);
      let img=imgs.find(i=>(i.src||'').includes(URL));
      if(!img)return 'noimg';
      let box=img;
      for(let k=0;k<10;k++){if((box.className||'').toString().includes('inner-box'))break;if(!box.parentElement)break;box=box.parentElement;}
      box.scrollIntoView({block:'center'});
      return JSON.stringify({x:box.getBoundingClientRect().x,y:box.getBoundingClientRect().y,w:box.getBoundingClientRect().width,h:box.getBoundingClientRect().height});
    })()""".replace("URL",json.dumps(URL)))
for i in range(N):
    r=select_comp()
    if r=="noimg": print("找不到图",URL);break
    rc=json.loads(r)
    cx=rc["x"]+rc["w"]/2; cy=rc["y"]+min(rc["h"],300)/2
    c.real_click(cx,cy)  # 点击选中
    time.sleep(0.8)
    # 重新读active组件
    ar=c.eval(r"""(()=>{const a=document.querySelector('.Preview_preview__1wgYD .inner-box.--active,[class*=--active]');if(!a)return '';const rc=a.getBoundingClientRect();return JSON.stringify({x:rc.x,y:rc.y,w:rc.width,h:rc.height});})()""")
    if not ar:
        print("未选中");break
    a=json.loads(ar)
    btn_x=a["x"]+a["w"]+16+8  # svg x=1409 vs right 1393 -> +16, svg中心+8
    # up=top+13+8 ; down=top+52+8
    btn_y=a["y"]+(21 if DIR=="up" else 60)
    c.real_click(btn_x,btn_y)
    print(f"第{i+1}次 {DIR} 组件top={a['y']:.0f} 点({btn_x:.0f},{btn_y:.0f})")
    time.sleep(1.0)
time.sleep(0.8)
# 最终前5顺序
order=c.eval(r"""(()=>{
  const pv=document.querySelector('.Preview_preview__1wgYD');
  const imgs=[...pv.querySelectorAll('img')].filter(i=>i.naturalWidth>200);
  const arr=imgs.map(i=>{const r=i.getBoundingClientRect();return {y:Math.round(r.y+r.height/2),src:(i.src||'').slice(0,75)};}).sort((a,b)=>a.y-b.y);
  return JSON.stringify(arr.slice(0,5),null,1);
})()""")
print("前5顺序:\n",order)
cap=c.send("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
p=os.path.join(sys.path[0],tag+".png");open(p,"wb").write(base64.b64decode(cap["data"]))
print("截图:",p)
c.close()
