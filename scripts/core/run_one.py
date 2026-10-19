# -*- coding: utf-8 -*-
"""一键处理单个商品【全删重建模式】：
导航→删所有款式标签(直到剩1个)→改第1款为参照第1款→添加剩余25款→改价→库存→下架→清库存→传图→存草稿。
用法: python run_one.py <gid>
"""
import sys, subprocess, time, os, json
BASE=os.path.dirname(os.path.abspath(__file__))
gid=sys.argv[1]
PY=sys.executable
REF=json.load(open(os.path.join(BASE,"ref_standard.json"),encoding="utf-8"))
ALL26=REF["order"]

def run(step, args, timeout=400):
    print(f"\n========== [{gid}] {step} ==========", flush=True)
    t0=time.time()
    try:
        r=subprocess.run([PY]+args,cwd=BASE,capture_output=True,text=True,timeout=timeout,encoding="utf-8",errors="replace")
    except subprocess.TimeoutExpired:
        print(f"  !! 超时 {step}"); return False
    out=(r.stdout or "")+(r.stderr or "")
    for line in out.splitlines():
        s=line.strip()
        if not s: continue
        if any(k in s for k in ["改价","新增完成","填库存","下架","清空","成功","失败","no delete","保存","缺失","当前已有","删除","删完"]):
            print("  ", s[:120], flush=True)
    print(f"  -- {step} 用时{time.time()-t0:.0f}s rc={r.returncode}", flush=True)
    return r.returncode==0

# 1. 导航
run("导航", ["goto_goods.py", gid], 60)
time.sleep(3)

from cdp import CDP, find_page_ws

# 2. 滚到款式标签+删除所有款式标签（直到剩1个）
print(f"\n========== [{gid}] 删所有款式标签 ==========", flush=True)
ws,_,_=find_page_ws()
c=CDP(ws)
time.sleep(2)
c.eval('''(()=>{
  const all=document.querySelectorAll('*');
  for(const el of all){
    if(el.children.length===0 && el.textContent.trim()==='删除规格类型' && el.offsetParent){
      el.scrollIntoView({block:'start'});return 'ok';
    }
  }
})()''')
time.sleep(2)

# 循环删除：每次点第2个"删除"span（第1个是删除规格类型），直到只剩1个款式标签
deleted=0
for i in range(40):
    r=c.eval(r'''(()=>{
      const spans=[...document.querySelectorAll('span')].filter(s=>s.textContent.trim()==='删除'&&s.offsetParent);
      // spans[0]=删除规格类型，spans[1..N]=各款式删除按钮
      // 还能删就继续删（留1个）
      if(spans.length<=2)return 'stop:只剩1个款式';
      spans[1].click();
      return 'del one, total spans='+spans.length;
    })()''')
    if 'stop' in r:
        print(f"  删完所有多余款式，共删{deleted}个", flush=True)
        break
    deleted+=1
    if deleted%5==0: print(f"  已删{deleted}个...", flush=True)
    time.sleep(0.8)
c.close()

# 3. 把剩下的1个款式改成参照第1款
print(f"\n========== [{gid}] 改第1款为参照第1款 ==========", flush=True)
ws,_,_=find_page_ws()
c=CDP(ws)
time.sleep(1)
first_name=ALL26[0]
c.eval(r'''(()=>{
  // 找当前第一个款式标签的输入框，清空并填入参照第1款
  const inputs=[...document.querySelectorAll('input')].filter(i=>i.placeholder==='请输入规格名称'&&i.offsetParent);
  // 第一个有值的input就是当前款式名
  const filled=inputs.find(i=>i.value.trim());
  if(filled){
    const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
    setter.call(filled, FIRST_NAME);
    filled.dispatchEvent(new Event('input',{bubbles:true}));
    filled.dispatchEvent(new Event('change',{bubbles:true}));
    filled.blur();
    return 'renamed to '+filled.value;
  }
  return 'no filled input';
})()'''.replace("FIRST_NAME",json.dumps(first_name)))
time.sleep(2)
c.close()

# 4. 添加剩余25款（用add_missing2.py动态检测）
run("补剩余25款", ["add_missing2.py"], 300)

# 5. 改价
run("改价", ["set_prices_b.py"])

# 6. 库存
run("库存", ["set_stock.py"])

# 7. 下架（跑2次补漏）
run("下架", ["hide_all.py", gid], 300)
run("下架补漏", ["hide_all.py", gid], 300)

# 8. 清库存
run("清库存", ["clear_hidden_stock.py"])

# 9. 传图
run("传图", ["sync_img.py", gid, "apply"], 600)

# 10. 存草稿
print(f"\n========== [{gid}] 存草稿 ==========", flush=True)
ws,_,_=find_page_ws()
c=CDP(ws)
c.eval('''(()=>{
  const btns=document.querySelectorAll('button');
  for(const b of btns){
    if(b.offsetParent && b.textContent.trim()==='保存草稿'){b.click();return 'ok';}
  }
})()''')
time.sleep(3)
c.eval('''(()=>{
  const btns=document.querySelectorAll('button');
  for(const b of btns){
    if(b.offsetParent && b.textContent.trim()==='确定'){b.click();return 'ok';}
  }
})()''')
c.close()
print(f"  [{gid}] 全部完成", flush=True)
