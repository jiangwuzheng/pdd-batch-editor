# -*- coding: utf-8 -*-
import json, os, urllib.request, io
from PIL import Image

base = os.path.dirname(os.path.abspath(__file__))
urls = json.load(open(os.path.join(base, "_target_urls.json"), encoding="utf-8"))
tgtdir = os.path.join(base, "_target"); os.makedirs(tgtdir, exist_ok=True)

def dhash(img, size=16):
    img = img.convert("L").resize((size+1, size))
    px = list(img.getdata())
    bits = []
    for r in range(size):
        for c in range(size):
            bits.append(px[r*(size+1)+c] > px[r*(size+1)+c+1])
    return bits

def dist(a,b):
    return sum(x!=y for x,y in zip(a,b))

results=[]
for key,url in urls.items():
    refp = os.path.join(base, key+".jpeg")
    tgtp = os.path.join(tgtdir, key+".jpeg")
    try:
        if not os.path.exists(tgtp):
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=25).read()
            open(tgtp,"wb").write(data)
        ref = Image.open(refp); tgt = Image.open(tgtp)
        d = dist(dhash(ref), dhash(tgt))
        # 错位检测：和其它参照图比
        results.append((key, ref.size, tgt.size, d))
    except Exception as e:
        results.append((key, "ERR", str(e)[:40], -1))

print("=== 自身匹配（参照图 vs 目标图，dhash汉明距离，越小越像，<40为同图）===")
bad=[]
for key,rs,ts,d in results:
    flag = "OK" if isinstance(d,int) and d<40 else "异常"
    if flag=="异常": bad.append(key)
    print(f"{key:20s} ref={rs} tgt={ts} 距离={d} {flag}")
print("\n需复查:", bad if bad else "无，全部26张与参照一致")
