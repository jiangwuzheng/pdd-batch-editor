# -*- coding: utf-8 -*-
"""读装修商详预览iframe内全部详情大图(按y顺序)，与参照5张URL/dHash比对。"""
import sys, json, time, os, hashlib, urllib.request, ssl
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
from PIL import Image
REFD=r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\sku_images\ref_detail"
OUT=r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch\_decor";os.makedirs(OUT,exist_ok=True)
def dl(u):
    u=u.split("?")[0];h=hashlib.md5(u.encode()).hexdigest()[:14];p=os.path.join(OUT,h+".jpg")
    if not os.path.exists(p):
        ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
        try: open(p,"wb").write(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=20,context=ctx).read())
        except Exception as e: return None
    return p
def dh(img,size=16):
    img=img.convert("L").resize((size+1,size));px=list(img.getdata());b=[]
    for r in range(size):
        for cc in range(size): b.append(px[r*(size+1)+cc]>px[r*(size+1)+cc+1])
    return b
def dist(a,b): return sum(x!=y for x,y in zip(a,b))
ws,_,_=find_page_ws(); c=CDP(ws)
# 遍历所有文档(主+iframe)，收集宽>=300的详情大图，按y排序
r=c.eval(r"""(()=>{
  const docs=[document];
  [...document.querySelectorAll('iframe')].forEach(f=>{try{if(f.contentDocument)docs.push(f.contentDocument);}catch(e){}});
  const all=[];
  docs.forEach((doc,di)=>{
    [...doc.querySelectorAll('img,[style*=background-image]')].forEach(e=>{
      const u=e.src||((e.style.backgroundImage||'').match(/url\(["']?(.*?)["']?\)/)||[''])[1]||'';
      if(!/pddpic|pinduoduo/.test(u))return;
      const rc=e.getBoundingClientRect();
      if(rc.width>=280&&rc.height>=120){all.push({u:u.split('?')[0],y:Math.round(rc.y+(di*0)),h:Math.round(rc.height)});}
    });
  });
  // 按y去重排序（同URL只留第一个）
  const seen={},sorted=[];
  all.sort((a,b)=>a.y-b.y).forEach(x=>{const k=x.u.slice(-30);if(!seen[k]){seen[k]=1;sorted.push(x);}});
  return JSON.stringify(sorted);
})()""")
lst=json.loads(r)
print("装修商详大图数:",len(lst))
# 参照5张
refs={1:("FAQ",dh(Image.open(os.path.join(REFD,"detail_01.jpeg")))),2:("售后",dh(Image.open(os.path.join(REFD,"detail_02.jpeg")))),3:("色卡",dh(Image.open(os.path.join(REFD,"detail_03.jpeg")))),23:("产品信息",dh(Image.open(os.path.join(REFD,"detail_23.jpeg")))),24:("版本区别",dh(Image.open(os.path.join(REFD,"detail_24.jpeg"))))}
for i,x in enumerate(lst,1):
    tag=""
    p=dl(x["u"])
    if p:
        h=dh(Image.open(p))
        for ri,(nm,rh) in refs.items():
            if dist(h,rh)<=12: tag=f"  <<< 参照{ri} {nm}"
    print(f"  {i:2d} h{x['h']:5d} {x['u'][-34:]}{tag}")
json.dump(lst,open(r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch\_decor_list.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
c.close()
