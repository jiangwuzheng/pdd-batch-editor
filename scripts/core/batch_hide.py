# -*- coding: utf-8 -*-
"""批量下架：逐款 scrollIntoView 开关→真实点击→验证。用法: python batch_hide.py "名1" "名2" ..."""
import sys, json, time
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
NAMES=sys.argv[1:]
ws,_,_=find_page_ws(); c=CDP(ws)
def find_switch(name):
    return c.eval(r"""new Promise((resolve)=>{
      const NAME=NAME_T;
      let sc=null;const cells=document.querySelectorAll('.goods-sku-img');
      if(cells.length){sc=cells[0];while(sc){if(sc.scrollHeight>sc.clientHeight+20&&sc.clientHeight>200)break;sc=sc.parentElement;}}
      let pos=0,guard=0;
      if(sc){sc.scrollTop=0;}
      const step=()=>{
        let t=null;
        document.querySelectorAll('tr').forEach(tr=>{const cell=tr.querySelector('.goods-sku-img');if(!cell)return;
          if(tr.querySelector('td').textContent.replace(/\s+/g,'')===NAME)t=tr.querySelector('div[data-testid=beast-core-switch]');});
        if(t){t.scrollIntoView({block:'center'});setTimeout(()=>resolve('found'),650);return;}
        if(sc){sc.scrollTop=pos;sc.dispatchEvent(new Event('scroll',{bubbles:true}));pos+=70;}guard++;
        if(sc&&pos<sc.scrollHeight+100&&guard<90){setTimeout(step,500);}else resolve('notfound');
      };
      setTimeout(step,300);
    })""".replace("NAME_T",json.dumps(name)),timeout=80)
for name in NAMES:
    r=find_switch(name)
    if r!="found":
        print(f"[下架] {name} 找不到行");continue
    rect=c.eval(r"""(()=>{
      const NAME=NAME_T;let t=null;
      document.querySelectorAll('tr').forEach(tr=>{const cell=tr.querySelector('.goods-sku-img');if(!cell)return;
        if(tr.querySelector('td').textContent.replace(/\s+/g,'')===NAME)t=tr.querySelector('div[data-testid=beast-core-switch]');});
      if(!t)return '';const rc=t.getBoundingClientRect();
      return JSON.stringify({left:rc.left,top:rc.top,width:rc.width,height:rc.height,active:t.className.includes('SIH_active')});
    })()""".replace("NAME_T",json.dumps(name)))
    if not rect:
        print(f"[下架] {name} 无开关");continue
    rc=json.loads(rect)
    if not rc["active"]:
        print(f"[下架] {name} 已下架跳过");continue
    assert 0<rc["top"]<1290, f"top={rc['top']}"
    c.click_rect(rc); time.sleep(1.3)
    st=c.eval(r"""(()=>{const NAME=NAME_T;let o='';
      document.querySelectorAll('tr').forEach(tr=>{const cell=tr.querySelector('.goods-sku-img');if(!cell)return;
        if(tr.querySelector('td').textContent.replace(/\s+/g,'')===NAME){const sw=tr.querySelector('div[data-testid=beast-core-switch]');o=sw.className.includes('SIH_active')?'仍上架':'已下架';}});
      return o;})()""".replace("NAME_T",json.dumps(name)))
    print(f"[下架] {name} -> {st}")
c.close()
print("下架完成")
