---
name: pdd-backend-sku-sync
description: "拼多多商家后台（mms.pinduoduo.com）商品批量编辑 RPA：把一个『目标商品』的全部 SKU（规格名称、拼单价/单买价、库存、上下架状态、SKU 规格预览图）完全对齐到一个『参照商品』；参照商品全程只读。支持含下架款在内的全部规格逐行对齐、批量上下架、SKU 预览图从参照商品原图自动提取并逐行上传、详情页图片替换/排序。适用：多 SKU 手电筒/灯具等商品复制同款、批量改价改库存、批量换 SKU 图、详情页某张图替换或前置。不依赖拼多多开放平台 API（个人小商家申请不到），用浏览器自动化（豆包 computer_use_tool plane=bu，或 Codex/OpenClaw/Hermes 的 CDP）直接操作后台网页。触发词：拼多多 SKU 对齐、批量编辑、规格预览图、SKU 图替换、商品同款复制、改价改库存、批量上下架、详情页换图。"
platform: 拼多多商家后台网页版
version: 1.3.0
updated: 2026-10-19
---

# 拼多多后台 SKU 批量对齐 Skill（RPA，不依赖开放平台 API）

## 什么时候用
- 老板给一个目标商品 id 和一个参照商品 id，要求"SKU 全部和参照一样，参照不许改"。
- 批量改价格三档、库存、上下架（含把部分 SKU 下架并关掉"已上架"开关）。
- 批量给每个 SKU 配规格预览图（图在参照商品里已有，或在图片空间）。
- 详情页某张图要替换、或某几张图要排到最前面。

## 输入（开工前必须明确）
- 目标商品 `goods_id`（要改的）→ 编辑页 `https://mms.pinduoduo.com/goods/goods_add/index?id=<sid>&goods_id=<目标id>&type=edit`
- 参照商品 `goods_id`（只读模板，禁止保存/修改）→ 同类 URL。
- SKU 清单：每个规格的 `功率 + 颜色名`、价格（拼单/单买）、库存、上架还是下架。
- 参照商品登录态有效（在已登录的 Chrome 里）。

## 铁律
- **参照商品标签页只读**：只截图、读 DOM、提图 URL，绝不点保存/提交/改任何字段。
- 收尾只点"保存草稿"；"提交/发布"是对外动作，必须老板明确点头再做。
- 虚拟滚动：SKU 表格只渲染约 15 个可见行，任何"全量"操作都要滚动遍历，不能假设 DOM 里有全部行。
- 保存/导航/切 tab 后元素句柄(ref)全部失效，重新定位。

## 价格三档基准（2026-10-13 实测，旧的 8瓦=109/119 已作废）
- 10 瓦：拼单价 139 / 单买价 149
- 8 瓦：拼单价 **128** / 单买价 **129**（注意不是 109/119）
- 定制：拼单价 169 / 单买价 179
- 库存口径：上架款保留目标现有库存；**下架款库存必须清空**（参照下架款库存为空）。

## 步骤零：操作前先扫描页面（找按钮坐标，避免瞎点）
- 用 web-recon 技能扫描当前编辑页，拿到所有按钮/输入框的精确坐标：
  ```bash
  python f:\AI共享知识库项目_执行版\skills\web-recon\scan_page.py --match goods_add --out <输出目录>
  ```
- 产物：`_侦察地图.html`（可视化）、`_recon.json`（结构化数据）、`_recon.png`（截图）。
- **只扫当前视口**，需先滚到目标区域再扫。找定制规格删除按钮时，扫完按y排序取最大2个就是定制规格的。

## 步骤一：新增款式（参照有、目标没有的 SKU）——真实商品已跑通
- 规格定义区（款式标签）最末尾总有一个空 input（`placeholder="请输入规格名称"`）。
- 正解（React 受控组件，必须真实事件，不能直接设 value）：
  1. 对空 input 先 `focus()` + 真实鼠标点击（`Input.dispatchMouseEvent` pressed/released）；
  2. `Input.insertText` 输入款式名（**无空格**，如 `10瓦白黄金冰无极调光CD1`）；
  3. 发 `Tab`（`Input.dispatchKeyEvent`）确认 → 页面自动生成新 SKU 行 + 新的空 input；
  4. 新行默认：价格空、库存空、已上架、无图，伴随"拼单价必须大于0"红字（填价后消失）。
- 先单款验证 `add_one_sku.py "名"`，再批量 `add_batch.py "名1" "名2" ...`（每款间等 1.2~1.5s）。
- 批量新增完所有款后，再统一改价、下架、配图，避免边增边改定位错乱。

## 步骤二：改名（Tab 法）
- 定位规格定义区要改的款式 input（旧名如"定制 容量升级（不支持退款）"）→ focus()+真实点击 → 全选（selectAll）→ `Input.insertText` 新名 → `Tab`。
- 实例：颜色定制→"定制 颜色组合（不支持退款）"；容量升级→"定制 电池容量升级（不支持退款）"。

## 步骤二点五：定制规格的正确添加（带橙色"定制"标签，关键！）
- **大坑**：定制规格不能当普通款式加（用空input+Tab加出来的没有橙色"定制"标签，系统不认）。必须用"添加定制规格"按钮。
- **正确流程**：
  1. 如果已有错误的普通"定制"规格（无橙色标签），先删除：找到规格定义区最后2行的"删除"按钮（y坐标最大的2个），逐个点击→确认。
  2. 点击"**添加定制规格**"按钮（规格定义区底部，"添加规格"旁边）。
  3. 输入规格名（如"颜色组合（不支持退款）"）→ 按 **Enter** 确认（**不是Tab**！Tab会失效）。
  4. 重复2-3添加第二个（如"电池容量升级（不支持退款）"）。
  5. 添加成功后，规格名前会出现**橙色"定制"标签**，这才是系统认可的定制规格。
- **设置价格/库存**：在SKU表格里找到这2行定制规格，设拼单价169/单买价179、库存1000。
- **上传定制规格图片**：用 `DOM.setFileInputFiles` 给定制规格行的 `input[type=file]` 注入本地图片（`定制_颜色组合.jpeg`、`定制_电池容量升级.jpeg`）。
- 最后保存草稿。

## 步骤三：改价 / 库存 / 上下架（逐行 DOM，比官方批量设置稳）
- SKU 行 `tr` 内 `input.IPT_input_5-188-0` 顺序：[0]增减按钮(定制款有时是数字)、[1]库存、[2]拼单价、[3]单买价、[4]规格编码。
- 改价：input 真实点击聚焦→全选→`Input.insertText` 数字→Tab；按功率前缀三档统一改（10瓦139/149、8瓦128/129、定制169/179）。
- 下架（关开关）：状态开关 `div[data-testid="beast-core-switch"]`（上架含 class `SIH_active`）；逐行 `scrollIntoView({block:'center'})` + 真实点击，确认变"已下架"（灰）。批量脚本 `batch_hide.py`。
- 清空下架款库存：`clear_hidden_stock.py`（参照下架款库存为空；旧残留如 1002 必须清）。
- **关键陷阱：下架款价格仍计入商品价格区间**。若下架款留旧价（如 109），保存后区间仍显示 109~169；必须把已下架款也改成对应档位价（128/129），区间才正确（128~169 / 129~179）。
- 虚拟滚动：SKU 表只渲染约 15 行，从 `.goods-sku-img` 向上找 `scrollHeight>clientHeight+20 && clientHeight>200` 的容器，`scrollTop += 200~240`，每步等 450~650ms，约 80~90 步。
- 官方批量工具栏（全部款式多选→批量设置）可作备选，但 option 要**点 option 本体**（点里面 span 会变全选）。

## 步骤四：SKU 规格预览图（关键，SKU 组件没有"图片空间"入口）
- SKU 预览图单元格 `.goods-sku-img` 内是 `MmsUiUploadPicVideoButton`，**只有"本地上传"**：一个隐藏
  `input.MmsUiUploadPicVideoButton___origin___3-T[type=file][accept="image/jpeg,image/png"]`。
  点它只弹系统文件对话框（无头看不到），**没有图片空间 tab**。（轮播图/白底图/详情图的 `MaterialModalButton_v2_materialContainer` 才有"图片空间"。）
- 正解：**从参照商品逐行提原图 → 下载本地 → 喂给目标行隐藏 file input**。

### 4.1 从参照商品提图（图是 background-image，不是 img.src）
```js
function parse(tr){
  const name=tr.querySelector('td').textContent.replace(/\s+/g,'');
  if(name.includes('定制颜色组合'))return ['定制','颜色组合'];
  if(name.includes('定制电池容量'))return ['定制','电池容量升级'];
  let w='',c='';
  if(name.startsWith('10瓦'))w='10W'; else if(name.startsWith('8瓦'))w='8W';
  const m=name.match(/瓦([一-龥]+?)无极调光/); if(m)c=m[1];
  return [w,c];
}
// cell=tr.querySelector('.goods-sku-img'); bg=cell.querySelector('[style*=background]');
// url=(bg.style.backgroundImage.match(/url\(["']?(.*?)["']?\)/)||[])[1]  // img.src 是 AI 角标，真图看 background
```
域名 img.pddpic.com/mms-goods-image/<日期>/<uuid>.jpeg，可直接下载，无需 cookie。

### 4.2 下载到本地（按 `功率_颜色.jpeg` 命名，参照 26 张存 sku_images/）
规格：宽高均 >480px、≤3M、仅 JPG/PNG（参照图一般 800×800 已合规）。

### 4.3 目标商品逐行上传（CDP 用 DOM.setFileInputFiles）
- 按 `[功率,颜色]` **全等**匹配（不能 includes，否则白黄橙冰/白黄橙金互串）。
- 对行 file input 设临时 id `tr.querySelector('input[type=file][accept*=jpeg]').id='sku_upload_target'`，再 `DOM.setFileInputFiles`（selector 用 CSS id）注入本地文件。
- 逐行滚动定位→注入，每张间隔约 1s；脚本 `sync_img.py <gid> check|apply`。
- 新上传图临时域名常是 pfs.* 或 pddpic，dHash 一般仍能判同图（距离≤12），本轮 11 张 apply 后"需换图 0 张"。

### 4.4 dHash 校验防错位
收集目标每行背景图 URL 下载，与本地参照图 16×16 dHash 比对，汉明距离 ≤12 同图；全部通过才算完。

## 步骤五：详情页图片替换（装修商详，2026-10-13 完整跑通）
- 编辑页详情区点"**装修商详**"按钮进可视化编辑器（不是普通详情列表）。编辑器分三块：
  左侧组件库（图文类/商品类/高级组件）；**中间主文档编辑画布 `.Preview_preview__1wgYD`（overflow=auto 的可滚动容器，里面图组件 `img.image` 宽 375，这才是可编辑的）**；右侧属性面板（选中组件后出现）。
- **大坑**：编辑器里还有一个跨域手机预览 **OOPIF iframe**（`mobile.yangkeduo.com/comm_goods_decoration_preview.html?goods_id=...`，独立 ws target，contentDocument 跨域不可访问、内部只读无按钮）。鼠标在它上面滚轮只是视觉预览。**真正要点/改的是主文档 `.Preview_preview__1wgYD` 画布**（坐标在 iframe 右侧，实测画布图 l≈1018、宽 375）。
- 换某张图的完整路径：
  1. 在主画布点击目标图片组件（先按 y 滚动 `.Preview_preview` 让它进视口，真实点击图片中心）→ 组件出现蓝框 + 右侧属性面板显示"图片N / 图片要求 / 图片1 缩略图 / **更换图片**"。
  2. 点右侧"**更换图片**"（约 x=2266,y=314，以 DOM 定位为准）→ 弹"图片空间"选择器（搜索框+左侧文件夹+图片网格+分页；每页 10 张，共数千张）。
  3. 在图片空间定位目标图：按文件名标签（卡片下方文字，如 `w1ZTPLl.jpeg`，注意字体易混）或用搜索框；**选中前先取完整 URL 下载做 dHash 核对**（距离 ≤12），避免选到旧版（如 6 色旧色卡 vs 10 色新色卡）。
  4. 点卡片（整个卡片 119×119 是勾选区，勾选框在右上角）→ 出现蓝勾 + 底部"已选 1 张"。
  5. 点蓝色"**确认**"（弹窗右下角；实测文字 span 约 l=1577,点中心命中）→ 弹窗关闭，右侧缩略图与画布换成新图。
  6. 点装修编辑器**底部蓝色"保存"**（`button.BTN_primary`，实测 l=1114,t=1298，可能略低于初始视口，先 `scrollIntoView` 再点）→ 保存后编辑器自动关闭回编辑页。
  7. **关闭装修编辑器的 × 在编辑器标题栏右上角（实测 l≈2398,t=12）**；不要点最右侧 l≈3302 那个（是浏览器层，关不掉装修）。
- 复核：重新打开装修，跑 `read_decorate.py` 读主画布宽≥280 的图，按 y 排序与参照 5 张（FAQ/售后/色卡/产品信息/版本区别）dHash 比对，目标位置应出现 `<<< 参照N`。
- 老板口径：**缺的补、旧的换、已经有的不动、其他图一律不改**；改哪几张必须老板点名。
- 参照 5 张关键图（去 `?` 取原图，pddpic 免 cookie）：
  1 FAQ `2025-09-10/049a1607-87bb-4911-9bfd-87deae2b873b.jpeg.a.jpeg`；
  2 售后 `2025-06-28/94100e67-d173-4d58-af7f-d3b6d6ed7fdf.jpeg`；
  3 色卡(10色) `garner-api-new/1270679b5921748a7c92c7e59d5ad17d.jpeg`；
  23 产品信息尺寸表 `2025-08-26/3a6e4eeb-f330-4d2a-b8aa-acd082065f79.jpeg`；
  24 版本区别表 `garner-api-new/b0570f9e24764ad3113da104a1eaec81.jpeg`。

### 5.1 用图片空间 file/list API 秒定位素材（关键，比翻页快）
- 不要在选择器里一页页翻（数千张、每页 10 张）。在编辑页（同域、已登录）**页面内直接 fetch 列表接口**，带登录 cookie，无需 anti-content：
  ```js
  // POST https://mms.pinduoduo.com/garner/mms/file/list
  // headers {'Content-Type':'application/json'}，credentials:include
  // body {"page_number":N,"page_size":500}
  // 返回 result.total、result.list[]（id/name/extension/url/create_time/extra_info.width/height）
  const r=await fetch('https://mms.pinduoduo.com/garner/mms/file/list',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({page_number:1,page_size:500})});
  ```
  分页拉全量（total 数千时每页 500 共 6 页），按 URL 片段（如 `94100e67`）匹配，直接拿到素材 id 和真实文件名。脚本 `space_find_refs.py`（产出 `_ref_material_ids.json`）。
- **5 张参照图在图片空间的素材 id 和真实文件名（搜名字必须用这个，别搜"售后"）**：
  | 图 | 素材 id | 图片空间里的 name |
  |---|---|---|
  | 1 FAQ | 80154512001 | `常见问题解答  手电筒10瓦` |
  | 2 售后(新手电筒) | 61715617529 | **`使用说明CD1`**（不是"售后"！搜"售后"0 结果） |
  | 3 色卡(10色) | 82465277195 | `jKJRr7P` |
  | 23 产品信息 | 65039610480 | `cd1--详情页_15` |
  | 24 版本区别 | 80154675595 | `71zGXpe` |
  拿到 name 后在图片空间选择器搜索框搜中文名 → 卡片勾选（`space_click_confirm.py` 只勾选不确认，再单独点确认，避免重复点取消勾选）。

### 5.2 装修"本地上传"批量组件走不通（已验证，勿再试）
- 详情图"更换图片"弹的选择器里有"本地上传"tab，是独立批量上传 modal（`MDL_outerWrapper`，单张≤3MB、jpg/jpeg/png），file input 是页面第 i=5 个 `accept=".jpg,.jpeg,.png" multiple`。
- `DOM.setFileInputFiles` 注入后 files=1 但 UI 无反应；手动 input/change、页面内 fetch URL→new File→DataTransfer 赋 input.files、合成 DragEvent(dragstart/drop) 全部无效。
- 原因：浏览器安全模型——合成 DragEvent 的 dataTransfer.files 在 drop 时为空，只有真实拖拽或原生文件框能携带文件；该批量组件只认这两种，不监听 input change。
- **SKU 图的单次上传组件（MmsUiUploadPicVideoButton）能被 setFileInputFiles 触发，但装修批量上传组件不行。详情图一律走"图片空间选择器"（5.1），不要走本地上传。**
- 关掉卡住的本地上传 modal：`.MDL_headerClose`（svg 关闭×，约 x=1723,y=362）。

### 5.3 详情图排序（把某几张移到最前）——组件右侧 ↑/↓ 控件
- 选中组件后，组件框 class 为 `inner-box --active`，其**右侧竖排 3 个 svg 操作按钮**（class `ICN_outerWrapper ... oper`，宽 16，x=组件右边缘+16≈1409）：
  - **上移 ↑**：中心 `x=组件right+24`，`y=组件top+21`
  - **下移 ↓**：`y=组件top+60`
  - **删除 🗑**：`y=组件top+92`（勿点）
- 脚本 `move_component.py <图URL片段> <up/down> <次数>`：自动滚动居中→点击组件选中→重读 active 框→点对应 ↑/↓。
- 案例（目标前4原为 海报/售后/FAQ/色卡，要前3=FAQ/售后/色卡）：FAQ ↑2 次到第1 → 售后 ↑1 次到第2 → 色卡 ↑1 次到第3；海报（带热区组件）顺延到第4，内容/热区不动。
- 带热区的"热区图片"营销组件可以被跨组件类型上移/下移（↑↓ 能越过它），但不要删除。

## 完成判据
- 左侧"商品优化建议 → 错误 (0)"，规格与库存无红字。
- 点"保存草稿"出现"保存成功！提交商品信息且发布成功后方可生效"。
- dHash 校验全部行同图；下架款库存 0、开关灰；上架款库存/价格/开关正确。
- 提交发布需老板确认。

## 工具无关实现提示
- 豆包：`computer_use_tool(plane="bu", import seed_browser_use as bu)`；JS 用 `bu.js("(()=>{ ... return X; })()")`（IIFE 才有返回值，普通箭头函数返回空 `{}`）。
- Codex/OpenClaw/Hermes：用各自 CDP 连登录态 Chrome；文件注入用 `DOM.setFileInputFiles`；其余选择器、parse、滚动、dHash 完全通用。
- 坐标点击易误触，优先用 DOM/选择器；表格滚动用 JS 设容器 scrollTop，不要拖滚动条（拖偏会全选页面文本）。

## CDP 环境与故障恢复（Windows，扩展屏2，已固化）
- 系统 Chrome（老板明确拒绝豆包 bu 浏览器）：`C:\Program Files\Google\Chrome\Application\chrome.exe`，
  独立配置 `C:\temp\pdd-cdp`，`--remote-debugging-port=9222 --window-position=1920,0 --window-size=2560,1440 --profile-directory=Default --no-first-run --no-default-browser-check`。页面 innerHeight≈1290~1346。
- HTTP 端点：开新 tab 用 `PUT http://127.0.0.1:9222/json/new?<urlencode>`（Chrome 155 必须 PUT，GET 报 405）；关 tab 用 `/json/close/<id>`；列 tab 用 `/json`。
- **渲染进程卡死**（从编辑页 Page.navigate 到 goods_list 后常见）：用 `/json/new` 开干净 about:blank tab → `/json/close/<卡死tab>` → 在新 tab 上重新 goto 导航，不要在卡死 tab 上重试。
- **关闭最后一个 tab 会导致整个 CDP Chrome 退出**（9222 WinError 10061）：始终保留至少一个 tab；若 Chrome 整退，用上面 `C:\temp\pdd-cdp` 启动参数重启，登录态保留、免扫码。
- 标签页控制在 3~4 个，用完即关。
- 取编辑 URL：商品列表"多个查询"输 goods_id→查询→hook `window.open=function(u){window.__openUrls.push(u);return null}`→点"编辑"→从 `window.__openUrls` 取 goods_add 完整 URL（会话 id 商品维度、重开不变）。

## 能力边界 / 不要做
- 本 skill 只做网页后台 RPA，不调用拼多多开放平台 API（个人/个体户小商家申请不到商品编辑 API：需企业资质、PRD、演示视频、域名、ICP 备案、软著、招商小二花名；淘宝/天猫 TOP、抖音抖店、小红书千帆同样卡企业资质/软著）。浏览器自动化是唯一现实路径。
- 不改参照商品；不读密码/cookie；不擅自提交发布（逐商品只存草稿，提交前老板统一确认）。
- 不擅自删除任何 SKU（不可逆）；旧体系商品对齐时参照没有的旧款一律**下架保留**（关开关、清库存），是否删除由老板拍板。
- AI 生图/素材不是本 skill 范畴（那是 IMIVA `ai-ecommerce-expert-*` 等生图技能）。

## 实测案例
- 2026-10-13 目标 711514793460 对齐参照 699950114171，26 个 SKU（10瓦21+8瓦3+定制2，含11下架款）全部对齐，26 张预览图 dHash 距离 0~2，保存草稿成功。
- 2026-10-13 目标 893967772726：28 款→改名"定制颜色组合"、8瓦3款改 128/129、8瓦白蓝绿红下架（下架款价也改 128/129，否则区间仍 109~169），区间 128~169/129~179，详情 35 张已含参照 5 张关键图零改动，存草稿。
- 2026-10-13 目标 760113150076（A类，真实跑通新增+换详情图）：16 款→27 款。新增 11 个 10 瓦下架款（空 input+insertText+Tab）+改名"定制电池容量升级"；17 行改价（8瓦128/129、定制169/179、10瓦139/149）；12 款下架（11新增+8瓦白蓝绿红）；清空下架款库存；11 张 SKU 图 setFileInputFiles 上传（需换图 0 张）；verify 26/26、价格区间 128~169/129~179。详情页经装修商详把旧 6 色色卡（第4张）换成图片空间新 10 色卡 w1ZTPLl.jpeg（dHash=3，URL `2026-10-13/2a3fd6a5-b853-4acd-b36a-81d6db7dad0a.jpeg`），FAQ/售后/产品信息/版本区别 dHash 均在位，存草稿"保存成功"。
- 2026-10-13 目标 761729958760（C类，旧24款全下架+新建26款=50款，完整跑通 file/list API 换图+排序）：先给24旧款改价→**新建26款时发现"全下架场景必须先建参照上架款、最后才下架保底款"（系统提示"请至少上架1个规格"）**→新建24灯款+2定制→三档改价→上架款填参照库存→下架11参照下架款+5瓦保底款共12款→清24旧款残留库存→sync_img 26张"需换图0张"→verify 26/26、旧24款全下架/库存空。详情页：图2旧"锂电池售后"经 file/list API 定位素材 id=61715617529（name=`使用说明CD1`）图片空间勾选替换为新版"手电筒售后"；move_component ↑↓ 把前3排成 FAQ/售后/色卡（热区海报顺延第4）；read_decorate 复核 图1/2/3=参照1/2/3、图24/25=参照23/24，5张全在位；存草稿价格区间 128~169/129~179、"保存成功"。
- 工作目录 `pdd_batch/`：cdp.py / read_page.py / add_batch.py / align_b_rename.py / set_prices_b.py / batch_hide.py / clear_hidden_stock.py / sync_img.py / verify_b.py / open_decor.py / read_decorate.py / select_space.py / confirm_space.py / save_draft.py；参照基准 ref_standard.json；26 张 SKU 图在 sku_images/，5 张详情图在 sku_images/ref_detail/。
