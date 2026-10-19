# -*- coding: utf-8 -*-
"""提交完整流程: 关'保存成功'弹窗 -> 点提交 -> 处理确认弹窗 -> 验证结果。"""
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

def find_text(t, ymin=0, ymax=2000, exact=True):
    return evalj(f"""(()=>{{
      const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
      const all=[...document.querySelectorAll('*')].filter(e=>vis(e)&&e.children.length===0);
      const s=all.find(e=>{{
        const tx=(e.textContent||'').trim();
        return tx==={json.dumps(t) if exact else '"x"'}||(!{json.dumps(exact)}&&tx.includes({json.dumps(t)}));
      }});
      if(!s)return null;
      const r=s.getBoundingClientRect();
      return {{x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),t:(s.textContent||'').trim()}};
    }})()""")

def poll(sec, matcher):
    end=time.time()+sec
    while time.time()<end:
        time.sleep(0.4)
        r=evalj(f"""(()=>{{
          const vis=e=>e.offsetParent&&e.getBoundingClientRect().width>0;
          const dialogs=[...document.querySelectorAll('[class*=modal i],[class*=MDL_],[class*=dialog i],[class*=Modal i]')].filter(e=>vis(e)&&e.getBoundingClientRect().width>250&&e.getBoundingClientRect().height>100);
          const dtxt=dialogs.map(d=>(d.textContent||'').trim().replace(/\\s+/g,' ').slice(0,120)).slice(0,2);
          const toasts=[...document.querySelectorAll('*')].filter(e=>vis(e)&&e.children.length===0&&(e.textContent||'').trim().match({json.dumps(matcher)})).map(e=>e.textContent.trim()).slice(0,5);
          return {{dialogs:dtxt,toasts:toasts}};
        }})()""")
        if r.get("dialogs") or r.get("toasts"):
            return r
    return None

url0=evalj("location.href")
# 1. 关闭'保存成功'弹窗
d=find_text("确定",300,1000)
if d:
    print("关保存成功弹窗:",d); c.real_click(d["x"],d["y"]); time.sleep(1.5)
# 2. 点提交
btn=find_text("提交",1250,1400)
print("提交按钮:",btn)
if not btn: c.close(); sys.exit(1)
c.real_click(btn["x"],btn["y"])
# 3. 轮询响应
for stage in range(4):
    r=poll(8, r"提交成功|提交失败|审核|确认提交|确定要|请填写|请选择|保存成功|必填")
    print(f"阶段{stage}:",json.dumps(r,ensure_ascii=False))
    if not r: break
    dtxt=" ".join(r.get("dialogs",[])+r.get("toasts",[]))
    # 有弹窗/提示就找确定/确认点掉(用户要求: 遇到弹窗自己点确定不要停)
    d=find_text("确定",300,1000) or find_text("确认",300,1000)
    if d:
        print("  点:",d); c.real_click(d["x"],d["y"]); time.sleep(1.5)
        continue
    # 没有可点按钮则等结果
    time.sleep(2)
url_now=evalj("location.href")
print("URL:",url0[:60],"->",url_now[:120])
print("页面含'提交成功':",evalj("document.body.innerText.includes('提交成功')"))
cap=c.send("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
open(os.path.join(sys.path[0],"after_submit_final.png"),"wb").write(base64.b64decode(cap["data"]))
print("截图完成")
c.close()
