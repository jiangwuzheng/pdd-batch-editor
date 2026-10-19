# -*- coding: utf-8 -*-
"""清空所有已下架行的库存（ins[1]），并核对价格/状态。虚拟滚动。"""
import sys, json, time
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
ws,_,_=find_page_ws(); c=CDP(ws)
JS=r"""new Promise((resolve)=>{
  const setVal=(el,val)=>{const proto=Object.getPrototypeOf(el);const d=Object.getOwnPropertyDescriptor(proto,'value');
    el.focus();d.set.call(el,val);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));el.blur();};
  const cells=document.querySelectorAll('.goods-sku-img');
  let sc=cells[0];while(sc){if(sc.scrollHeight>sc.clientHeight+20&&sc.clientHeight>200)break;sc=sc.parentElement;}
  const log=[];
  const work=()=>{document.querySelectorAll('tr').forEach(tr=>{
    const cell=tr.querySelector('.goods-sku-img');if(!cell)return;
    const name=tr.querySelector('td').textContent.replace(/\s+/g,'');
    const sw=tr.querySelector('div[data-testid=beast-core-switch]');
    const active=sw&&sw.className.includes('SIH_active');
    const ins=tr.querySelectorAll('input.IPT_input_5-188-0');
    if(!active&&ins.length>=4){
      // 下架：找库存input（值为纯数字、在拼单价之前的那个）。ins[1]通常是库存
      if(ins[1]&&/^\d+$/.test(ins[1].value)){setVal(ins[1],'');log.push(name.slice(0,16)+' 清库存');}
      if(ins[0]&&/^\d{3,}$/.test(ins[0].value)){setVal(ins[0],'');}
    }
  });};
  let pos=0,guard=0;
  if(sc){sc.scrollTop=0;}
  const step=()=>{work();if(sc){sc.scrollTop=pos;sc.dispatchEvent(new Event('scroll',{bubbles:true}));pos+=70;}guard++;
    if(sc&&pos<sc.scrollHeight+100&&guard<90){setTimeout(step,500);}
    else{sc.scrollTop=0;sc.dispatchEvent(new Event('scroll',{bubbles:true}));setTimeout(()=>resolve(JSON.stringify({清空:log.length,log})),800);}};
  setTimeout(step,300);
})"""
print(c.eval(JS,timeout=120))
c.close()
