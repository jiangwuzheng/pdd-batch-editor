# -*- coding: utf-8 -*-
"""批量新增款式：在规格定义区空input逐个输入+Tab确认。用法: python add_batch.py "名1" "名2" ..."""
import sys, json, time
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
NAMES=sys.argv[1:]
ws,_,_=find_page_ws(); c=CDP(ws)
c.eval(r"""(()=>{const l=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&(e.textContent||'').trim()==='商品规格');if(l)l.scrollIntoView({block:'start'});})()""")
time.sleep(0.8)
for NAME in NAMES:
    f=c.eval(r"""(()=>{
      const ins=[...document.querySelectorAll('input.IPT_input_5-188-0')].filter(i=>i.placeholder==='请输入规格名称'&&!i.value.trim());
      if(!ins.length)return 'none';
      const t=ins[ins.length-1];t.scrollIntoView({block:'center'});
      const r=t.getBoundingClientRect();return JSON.stringify({left:r.left,top:r.top,width:r.width,height:r.height});
    })()""")
    if not f or f=="none":
        print(f"[{NAME}] 无空input，跳过");continue
    r=json.loads(f)
    c.eval(r"""(()=>{const ins=[...document.querySelectorAll('input.IPT_input_5-188-0')].filter(i=>i.placeholder==='请输入规格名称'&&!i.value.trim());ins[ins.length-1].focus();})()""")
    time.sleep(0.15)
    c.real_click(r["left"]+r["width"]/2, r["top"]+r["height"]/2); time.sleep(0.3)
    c.send("Input.insertText",{"text":NAME}); time.sleep(0.4)
    c.send("Input.dispatchKeyEvent",{"type":"keyDown","key":"Tab","code":"Tab","windowsVirtualKeyCode":9})
    c.send("Input.dispatchKeyEvent",{"type":"keyUp","key":"Tab","code":"Tab","windowsVirtualKeyCode":9})
    time.sleep(1.4)
    # 确认
    ok=c.eval(r"""(()=>{const spec=[...document.querySelectorAll('input.IPT_input_5-188-0')].filter(i=>i.placeholder==='请输入规格名称'&&i.value.trim()).map(i=>i.value.replace(/\s+/g,''));return spec.some(v=>v.includes(KEY_T));})()""".replace("KEY_T",json.dumps(NAME.replace("无极调光CD1","").replace(" ","")[:6])))
    print(f"[{NAME}] {'OK' if ok else '失败'}")
print("新增完成")
c.close()
