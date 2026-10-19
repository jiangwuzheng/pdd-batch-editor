# -*- coding: utf-8 -*-
"""SKU图同步：dHash核对 -> 单遍滚动上传（不每张从头滚）-> 多遍兜底。
用法: python sync_img.py <gid> check|apply
"""
import sys, json, time, os, urllib.request, hashlib
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
from PIL import Image

IMGDIR=r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\sku_images"
TMPDIR=r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch\_tgtimg"; os.makedirs(TMPDIR,exist_ok=True)
THRESH=12
def dhash(img,size=16):
    img=img.convert("L").resize((size+1,size)); px=list(img.getdata()); bits=[]
    for r in range(size):
        for c in range(size):
            bits.append(px[r*(size+1)+c]>px[r*(size+1)+c+1])
    return bits
def dist(a,b): return sum(x!=y for x,y in zip(a,b))
def local_key(name):
    n=name.replace(" ","")
    if n.startswith("定制颜色组合"): return "定制_颜色组合"
    if n.startswith("定制电池容量升级"): return "定制_电池容量升级"
    w="10W" if n.startswith("10瓦") else ("8W" if n.startswith("8瓦") else "")
    import re
    m=re.search(r"瓦([一-龥]+?)无极调光",n)
    col=m.group(1) if m else ""
    return f"{w}_{col}" if w else None
def dl(url):
    u=url.split("?")[0]; h=hashlib.md5(u.encode()).hexdigest()[:12]; p=os.path.join(TMPDIR,h+".jpeg")
    if not os.path.exists(p):
        req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
        open(p,"wb").write(urllib.request.urlopen(req,timeout=25).read()); time.sleep(0.1)
    return p

COLLECT=r"""new Promise((resolve)=>{
  const cells=document.querySelectorAll('.goods-sku-img');
  let sc=cells[0]; while(sc){if(sc.scrollHeight>sc.clientHeight+20&&sc.clientHeight>200)break;sc=sc.parentElement;}
  const map={}; let pos=0,guard=0;
  const collect=()=>{document.querySelectorAll('tr').forEach(tr=>{
    const cell=tr.querySelector('.goods-sku-img'); if(!cell)return;
    const name=tr.querySelector('td').textContent.replace(/\s+/g,''); if(!name)return;
    const bg=cell.querySelector('[style*=background]'); let url='';
    if(bg){const m=(bg.style.backgroundImage||'').match(/url\(["']?(.*?)["']?\)/);url=m?m[1]:'';}
    if(url&&!map[name])map[name]=url;
  });};
  const step=()=>{collect();if(sc){sc.scrollTop=pos;sc.dispatchEvent(new Event('scroll',{bubbles:true}));pos+=70;}guard++;
    if(sc&&pos<sc.scrollHeight+100&&guard<90){setTimeout(step,500);}else{sc.scrollTop=0;sc.dispatchEvent(new Event('scroll',{bubbles:true}));resolve(JSON.stringify(map));}};
  setTimeout(step,300);
})"""

gid=sys.argv[1]; mode=sys.argv[2] if len(sys.argv)>2 else "check"
ws,_,_=find_page_ws(); c=CDP(ws)
ref=json.load(open(r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch\ref_standard.json",encoding="utf-8"))
cur=json.loads(c.eval(COLLECT,timeout=90))
_alias={"定制颜色组合（不支持退款）":"定制颜色组合（不支持退款）定制",
        "定制电池容量升级（不支持退款）":"定制电池容量升级（不支持退款）定制"}
for k,v in list(cur.items()):
    if k in _alias and _alias[k] not in cur: cur[_alias[k]]=v
print("读到行数:",len(cur))
need=[]
for name in ref["order"]:
    key=local_key(name); lp=os.path.join(IMGDIR,key+".jpeg")
    if not os.path.exists(lp): print("  缺本地图:",key); continue
    url=cur.get(name,"")
    if not url: need.append((name,key,lp,"无图")); continue
    try:
        d=dist(dhash(Image.open(lp)), dhash(Image.open(dl(url))))
        if d>THRESH: need.append((name,key,lp,f"距离{d}"))
    except Exception as e:
        need.append((name,key,lp,f"比对失败{str(e)[:30]}"))
print("\n=== 需换图 %d 张 ==="%len(need))
for name,key,lp,why in need: print(f"  {key:14s} {why}")
if mode!="apply" or not need:
    c.close(); sys.exit(0)

# ===== 单遍滚动上传 =====
TARGET={name:lp for name,key,lp,why in need}
KEYMAP={name:key for name,key,lp,why in need}
c.eval("window.__done=[];window.__target="+json.dumps(list(TARGET.keys()),ensure_ascii=False)+";")
STEP=r"""(()=>{
  const cells=document.querySelectorAll('.goods-sku-img');
  let sc=cells[0];while(sc){if(sc.scrollHeight>sc.clientHeight+20&&sc.clientHeight>200)break;sc=sc.parentElement;}
  if(window.__p==null){window.__p=0;sc.scrollTop=0;}
  sc.scrollTop=window.__p;sc.dispatchEvent(new Event('scroll',{bubbles:true}));
  const done=new Set(window.__done);const T=new Set(window.__target);
  let hit=null;
  document.querySelectorAll('tr').forEach(tr=>{const cell=tr.querySelector('.goods-sku-img');if(!cell||hit)return;
    const name=tr.querySelector('td').textContent.replace(/\s+/g,'');
    if(T.has(name)&&!done.has(name)){
      const inp=tr.querySelector('input[type=file]');
      if(inp){inp.id='sku_upload_now';inp.scrollIntoView({block:'center'});hit=name;}
    }});
  const cur=window.__p;window.__p+=70;
  return JSON.stringify({hit:hit,cur:cur,max:sc.scrollHeight});
})()"""
print("\n=== 单遍滚动上传 ===")
for round_i in range(3):
    c.eval("window.__p=0;")
    while True:
        st=json.loads(c.eval(STEP))
        time.sleep(0.35)
        if st["hit"]:
            nm=st["hit"]; lp=TARGET[nm]
            try:
                c.upload("#sku_upload_now", lp)
                c.eval("window.__done.push(%s);"%json.dumps(nm))
                done_n=json.loads(c.eval("JSON.stringify(window.__done)"))
                print(f"  [轮{round_i+1}] 上传 {KEYMAP[nm]}  累计{len(done_n)}/{len(TARGET)}")
                time.sleep(2.2)
            except Exception as e:
                print(f"  {KEYMAP[nm]} 异常:{str(e)[:40]}");time.sleep(1.2)
        if st["cur"]>st["max"]+120: break
    done=json.loads(c.eval("JSON.stringify(window.__done)"))
    remain=[n for n in TARGET if n not in done]
    print(f"  轮{round_i+1}结束，剩余{len(remain)}")
    if not remain: break
    time.sleep(1)
done=json.loads(c.eval("JSON.stringify(window.__done)"))
failn=[KEYMAP[n] for n in TARGET if n not in done]
print("\n成功 %d/%d，失败:%s"%(len(done),len(TARGET),failn if failn else "无"))
c.close()
