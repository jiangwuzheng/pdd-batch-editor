# -*- coding: utf-8 -*-
"""分页拉取图片空间全部图，定位5张参照详情图的素材id/name/url。
目标URL片段:
 售后 94100e67 ; FAQ 049a1607 ; 色卡 1270679b ; 产品信息 3a6e4eeb ; 版本区别 b0570f9e
结果写 _ref_material_ids.json。
"""
import sys, json, time, os
sys.path.insert(0, r"C:\Users\admin.DESKTOP-T5A2OCK\Doubao\chats\2026-10-11\new-chat-1\pdd_batch")
from cdp import CDP, find_page_ws
TARGETS={
 "售后":"94100e67",
 "FAQ":"049a1607",
 "色卡":"1270679b",
 "产品信息":"3a6e4eeb",
 "版本区别":"b0570f9e",
}
ws,_,_=find_page_ws(); c=CDP(ws)
# 在页面里定义一个fetch函数，循环翻页
js = r"""
async function pullPage(pn,ps){
  const r=await fetch('/garner/mms/file/list',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({page_number:pn,page_size:ps}),credentials:'include'});
  return await r.json();
}
return {pullPage:pullPage.toString()};
"""
# 直接在python侧编排：每页一次eval
found={}
all_items=[]
PS=500
# 先拿total
first=c.eval(r"""fetch('/garner/mms/file/list',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({page_number:1,page_size:500}),credentials:'include'}).then(r=>r.json()).then(j=>JSON.stringify({total:j.result.total,got:j.result.list.length}))""", await_promise=True)
print("首页:",first)
total=json.loads(first)["total"]
import math
pages=math.ceil(total/PS)
print("总页数:",pages)
for pn in range(1,pages+1):
    body=c.eval(r"""fetch('/garner/mms/file/list',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({page_number:PN,page_size:PS}),credentials:'include'}).then(r=>r.json()).then(j=>JSON.stringify(j.result.list.map(x=>({id:x.id,name:x.name,ext:x.extension,url:x.url,w:x.extra_info.width,h:x.extra_info.height,ct:x.create_time}))))""".replace("PN",str(pn)).replace("PS",str(PS)), await_promise=True, timeout=40)
    items=json.loads(body)
    all_items.extend(items)
    for it in items:
        for label,key in TARGETS.items():
            if key in it["url"] and label not in found:
                found[label]=it
                print(f"找到 {label}: id={it['id']} name={it['name']} {it['w']}x{it['h']} url={it['url']}")
    if len(found)==len(TARGETS):
        print("5张全部找到，提前停止");break
    print(f"page {pn}/{pages} 累计{len(all_items)} 已找到{len(found)}")
    time.sleep(0.2)
out=os.path.join(sys.path[0],"_ref_material_ids.json")
json.dump(found,open(out,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("保存:",out)
print("未找到:",[k for k in TARGETS if k not in found])
c.close()
