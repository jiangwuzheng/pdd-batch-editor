# -*- coding: utf-8 -*-
"""单商品全流程【全删重建+带空格名+定制橙色标签】:
导航→改属性→删所有款式标签→改第1款(带空格)→补23款(带空格)→补定制2款(添加定制规格)→改价→库存→下架→清库存→传图→存草稿。
用法: python run_full.py <gid>
"""
import sys, subprocess, time, os, json
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
gid = sys.argv[1]
PY = sys.executable
REF = json.load(open(os.path.join(BASE, "ref_standard.json"), encoding="utf-8"))
ALL26 = REF["order"]
from specfmt import spaced

def run(step, args, timeout=400):
    print(f"\n========== [{gid}] {step} ==========", flush=True)
    t0 = time.time()
    try:
        r = subprocess.run([PY] + args, cwd=BASE, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        print(f"  !! 超时 {step}", flush=True); return False
    out = (r.stdout or "") + (r.stderr or "")
    for line in out.splitlines():
        s = line.strip()
        if not s: continue
        if any(k in s for k in ["成功", "失败", "改价", "新增", "填库存", "下架", "清空", "保存",
                                "缺失", "需换图", "上传", "OK", "总款式", "错误", "已存在", "照明", "防水"]):
            print("  ", s[:120], flush=True)
    print(f"  -- {step} 用时{time.time()-t0:.0f}s rc={r.returncode}", flush=True)
    return r.returncode == 0

# 1. 导航
run("导航", ["goto_goods.py", gid], 150)
time.sleep(3)

# 2. 属性
run("改属性", ["fix_attr.py"], 120)

# 3. 删所有款式标签（直到剩1个，按剩余行数判断，避免误停）
print(f"\n========== [{gid}] 删所有款式标签 ==========", flush=True)
from cdp import CDP, find_page_ws
ws, _, _ = find_page_ws(); c = CDP(ws)
time.sleep(2)
def filled_count():
    r = c.eval(r'''(()=>{const v=[...document.querySelectorAll('input[placeholder="请输入规格名称"]')].filter(i=>i.offsetParent&&i.value.trim());return v.length;})()''', timeout=20)
    try: return int(r)
    except Exception: return 999
deleted = 0
for i in range(60):
    cnt = filled_count()
    if cnt <= 1: break
    c.eval(r'''(()=>{const s=[...document.querySelectorAll('span')].filter(x=>x.offsetParent&&x.children.length===0&&x.textContent.trim()==='删除');if(!s.length)return 'none';(s[1]||s[0]).click();return 'ok';})()''')
    deleted += 1
    if deleted % 5 == 0: print(f"  已删{deleted}个(当前{cnt})...", flush=True)
    time.sleep(0.7)
print(f"  删完，共删{deleted}个，剩{filled_count()}个", flush=True)
c.close()

# 4. 改第1款为参照第1款（带空格）
print(f"\n========== [{gid}] 改第1款为参照第1款 ==========", flush=True)
first_disp = spaced(ALL26[0])
ws, _, _ = find_page_ws(); c = CDP(ws)
time.sleep(1)
c.eval(r'''(()=>{
  const inputs=[...document.querySelectorAll('input')].filter(i=>i.placeholder==='请输入规格名称'&&i.offsetParent);
  const filled=inputs.find(i=>i.value.trim());
  if(filled){filled.scrollIntoView({block:'center'});filled.focus();return 'found';}
  return 'none';
})()''')
time.sleep(0.4)
c.eval("if(document.activeElement&&document.activeElement.select)document.activeElement.select()")
time.sleep(0.2)
c.send("Input.insertText", {"text": first_disp}); time.sleep(0.4)
c.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9})
c.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Tab", "code": "Tab", "windowsVirtualKeyCode": 9})
time.sleep(1.5)
c.close()

# 5. 补23款
run("补23款", ["add_missing3.py"], 300)
# 6. 补定制2款
run("补定制2款", ["add_customs.py"], 180)
# 7. 改价 / 状态同步(下架+恢复上架) / 库存 / 清库存 / 传图
run("改价", ["set_prices_b.py"])
run("状态同步", ["hide_all.py", gid, "refonly"], 400)
run("库存", ["set_stock.py"])
run("下架补漏", ["hide_all.py", gid, "refonly"], 300)
run("清库存", ["clear_hidden_stock.py"])
run("传图", ["sync_img.py", gid, "apply"], 600)

# 8. 存草稿
print(f"\n========== [{gid}] 存草稿 ==========", flush=True)
ws, _, _ = find_page_ws(); c = CDP(ws)
c.eval('''(()=>{const btns=document.querySelectorAll('button');for(const b of btns){if(b.offsetParent&&b.textContent.trim()==='保存草稿'){b.click();return 'ok';}}})()''')
time.sleep(3)
c.eval('''(()=>{const btns=document.querySelectorAll('button');for(const b of btns){if(b.offsetParent&&b.textContent.trim()==='确定'){b.click();return 'ok';}}})()''')
time.sleep(2)
c.close()
print(f"[{gid}] 流程结束", flush=True)
