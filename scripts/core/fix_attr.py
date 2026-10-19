# -*- coding: utf-8 -*-
"""修正属性: 是否防水→不防水（下拉）, 连续照明时间→1（文本框）。
定位法: 找标签叶子文本('是否防水'/'连续照明时间')，沿祖先链找到含可见input的行。
用法: python fix_attr.py"""
import sys, json, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import CDP, find_page_ws

def click_center(c, x, y):
    c.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
    c.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})

def locate_input(c, label):
    r = c.eval(r'''(()=>{
      const l=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&(e.textContent||'').trim()===''' + json.dumps(label) + r''');
      if(!l)return 'no-label';
      let p=l;
      for(let i=0;i<8&&p;i++){
        if(p.querySelector){
          const inp=p.querySelector('input');
          if(inp&&inp.offsetParent){
            inp.scrollIntoView({block:'center'});
            const r=inp.getBoundingClientRect();
            return JSON.stringify({v:inp.value,ph:inp.placeholder||'',x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)});
          }
        }
        p=p.parentElement;
      }
      return 'no-input';
    })()''', timeout=30)
    return r

def set_dropdown(c, label, want):
    info = locate_input(c, label)
    if 'no-' in str(info):
        return 'notfound:' + str(info)
    d = json.loads(info)
    if d.get('v') == want:
        return 'already:' + want
    click_center(c, d['x'], d['y']); time.sleep(1.0)
    r = c.eval(r'''(()=>{
      const l=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&e.offsetParent&&(e.textContent||'').trim()===''' + json.dumps(want) + r''');
      if(!l)return 'no-option';
      const r=l.getBoundingClientRect();
      return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)});
    })()''', timeout=20)
    if 'no-option' in str(r):
        return 'no-option:' + want
    o = json.loads(r)
    click_center(c, o['x'], o['y']); time.sleep(0.8)
    time.sleep(0.4)
    info2 = locate_input(c, label)
    try:
        return 'after:' + json.loads(info2).get('v', '?')
    except Exception:
        return 'after:?'

def set_text(c, label, want):
    info = locate_input(c, label)
    if 'no-' in str(info):
        return 'notfound:' + str(info)
    d = json.loads(info)
    if d.get('v') == want:
        return 'already:' + want
    click_center(c, d['x'], d['y']); time.sleep(0.4)
    c.eval("if(document.activeElement&&document.activeElement.select)document.activeElement.select()"); time.sleep(0.2)
    c.send("Input.insertText", {"text": want}); time.sleep(0.3)
    c.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9})
    c.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9})
    time.sleep(0.8)
    info2 = locate_input(c, label)
    try:
        return 'after:' + json.loads(info2).get('v', '?')
    except Exception:
        return 'after:?'

ws, _, _ = find_page_ws(prefer="goods_add")
if not ws:
    print("NO_EDIT_PAGE"); sys.exit(1)
c = CDP(ws)
time.sleep(1)
print("防水改后:", set_dropdown(c, "是否防水", "不防水"), flush=True)
print("照明时间:", set_text(c, "连续照明时间", "1"), flush=True)
c.close()
