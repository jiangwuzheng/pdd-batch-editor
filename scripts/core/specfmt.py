# -*- coding: utf-8 -*-
"""ref_standard 内部名(去空格) -> 前台显示名(带空格)。
"10瓦白黄橙冰无极调光CD1" -> "10瓦 白黄橙冰 无极调光CD1"
"定制颜色组合（不支持退款）定制" -> "定制 颜色组合（不支持退款）"
"""
import re

def spaced(key):
    m = re.match(r'^(10瓦|8瓦)(.+?)无极调光CD1$', key)
    if m:
        return "%s %s 无极调光CD1" % (m.group(1), m.group(2))
    if "颜色组合" in key:
        return "定制 颜色组合（不支持退款）"
    if "电池容量升级" in key:
        return "定制 电池容量升级（不支持退款）"
    return key
