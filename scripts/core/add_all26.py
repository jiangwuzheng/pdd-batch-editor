# -*- coding: utf-8 -*-
import sys, json, time, urllib.request
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, CDP_HTTP

names = [
 "10瓦 白黄橙冰 无极调光CD1","10瓦 白黄橙金 无极调光CD1","10瓦 白黄橙蓝 无极调光CD1",
 "10瓦 白黄橙红 无极调光CD1","10瓦 白黄橙粉 无极调光CD1","10瓦 白黄橙绿 无极调光CD1",
 "10瓦 黄橙粉冰 无极调光CD1","10瓦 黄橙红冰 无极调光CD1","10瓦 白蓝橙红 无极调光CD1",
 "10瓦 白蓝绿红 无极调光CD1","10瓦 白黄金冰 无极调光CD1","10瓦 黄金粉冰 无极调光CD1",
 "10瓦 白蓝金冰 无极调光CD1","10瓦 白金粉红 无极调光CD1","10瓦 白金红冰 无极调光CD1",
 "10瓦 白金粉冰 无极调光CD1","10瓦 黄橙金绿 无极调光CD1","10瓦 黄橙粉金 无极调光CD1",
 "10瓦 黄金红绿 无极调光CD1","10瓦 黄金红冰 无极调光CD1","10瓦 蓝金粉红 无极调光CD1",
 "8瓦 白黄橙冰 无极调光CD1","8瓦 白黄橙金 无极调光CD1","8瓦 黄橙粉冰 无极调光CD1",
 "定制 颜色组合（不支持退款）","定制 电池容量升级（不支持退款）",
]

tabs=json.loads(urllib.request.urlopen(CDP_HTTP+"/json",timeout=8).read())
ed=[t for t in tabs if "goods_id=893967772726" in t.get("url","") and "goods_add" in t.get("url","")][0]
c=CDP(ed["webSocketDebuggerUrl"])

for i,name in enumerate(names):
    # 定位空输入框
    pos=json.loads(c.eval(r"""(()=>{
      const ins=[...document.querySelectorAll('input.IPT_input_5-188-0')].filter(i=>(i.placeholder||'').includes('规格名称')&&!i.value);
      if(!ins.length) return JSON.stringify({err:'no empty input'});
      const t=ins[ins.length-1]; t.scrollIntoView({block:'center'});
      const rc=t.getBoundingClientRect();
      return JSON.stringify({x:rc.x+rc.width/2,y:rc.y+rc.height/2});
    })()"""))
    if "err" in pos:
        print(i,name,"->",pos); break
    x,y=pos["x"],pos["y"]
    c.send("Input.dispatchMouseEvent",{"type":"mousePressed","x":x,"y":y,"button":"left","clickCount":1})
    c.send("Input.dispatchMouseEvent",{"type":"mouseReleased","x":x,"y":y,"button":"left","clickCount":1})
    time.sleep(0.3)
    c.send("Input.insertText",{"text":name})
    time.sleep(0.2)
    c.send("Input.dispatchKeyEvent",{"type":"keyDown","key":"Tab","code":"Tab","windowsVirtualKeyCode":9})
    c.send("Input.dispatchKeyEvent",{"type":"keyUp","key":"Tab","code":"Tab","windowsVirtualKeyCode":9})
    time.sleep(0.9)
    # 校验当前已加数量
    cnt=c.eval(r"""(()=>{return [...document.querySelectorAll('input.IPT_input_5-188-0')].filter(i=>/无极调光CD1|不支持退款/.test(i.value||'')).length;})()""")
    print(i,name,"ok, total=",cnt)

# 最终列出所有规格名
fin=json.loads(c.eval(r"""(()=>JSON.stringify([...document.querySelectorAll('input.IPT_input_5-188-0')].filter(i=>/无极调光CD1|不支持退款/.test(i.value||'')).map(i=>i.value)))()"""))
print("FINAL",len(fin))
for n in fin: print(" ",n)
c.close()
