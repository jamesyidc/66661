# 📂 Google Drive TXT监控 - 文件夹ID显示

## 🎯 更新内容

根据用户需求，现在监控页面显示：
1. **1️⃣ 单数日期父文件夹ID** - 用于1, 3, 5, 7, 9, 11, 13...号
2. **2️⃣ 双数日期父文件夹ID** - 用于2, 4, 6, 8, 10, 12, 14...号
3. **📁 子账号文件夹ID** - 今天实际使用的文件夹（今日文件夹）

---

## 🌐 访问地址

### Google Drive TXT监控页面
```
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/gdrive-detector
```

---

## 🎨 页面效果

### 显示的三个卡片

```
┌──────────────────────────────────┐  ┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ 1️⃣ 单数日期父文件夹              │  │ 2️⃣ 双数日期父文件夹              │  │ 📁 子账号文件夹ID                 │
├──────────────────────────────────┤  ├──────────────────────────────────┤  ├──────────────────────────────────┤
│ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM │  │ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM │  │ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM │
│                                  │  │                                  │  │                                  │
│ ✅ 今天使用 (1, 3, 5, 7, 9...)   │  │ 📂 备用 (2, 4, 6, 8, 10...)      │  │ 今日使用的文件夹                  │
└──────────────────────────────────┘  └──────────────────────────────────┘  └──────────────────────────────────┘
        蓝色 #3b82f6                          紫色 #8b5cf6                         金色 #fbbf24
```

### 今天是13号（单数）的显示效果
- **单数父文件夹卡片**：
  - 显示 Folder ID
  - 状态：✅ 今天使用 (1, 3, 5, 7, 9, 11...)
  - 颜色：蓝色 (#3b82f6)
  - 状态文字：绿色 (#10b981)

- **双数父文件夹卡片**：
  - 显示 Folder ID
  - 状态：📂 备用 (2, 4, 6, 8, 10, 12...)
  - 颜色：紫色 (#8b5cf6)
  - 状态文字：灰色 (rgba(255,255,255,0.4))

- **子账号文件夹卡片**：
  - 显示今天实际使用的文件夹ID
  - 说明：今日使用的文件夹
  - 颜色：金色 (#fbbf24)

---

## 🔧 技术实现

### 前端 HTML 结构

```html
<!-- 单数日期父文件夹 -->
<div class="stat-card">
    <div class="stat-label">1️⃣ 单数日期父文件夹</div>
    <div class="stat-value" id="root-folder-odd" 
         style="font-size: 0.9rem; word-break: break-all; color: #3b82f6;">-</div>
    <div class="stat-description" id="odd-status" 
         style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 5px;">
         1, 3, 5, 7, 9, 11, 13...
    </div>
</div>

<!-- 双数日期父文件夹 -->
<div class="stat-card">
    <div class="stat-label">2️⃣ 双数日期父文件夹</div>
    <div class="stat-value" id="root-folder-even" 
         style="font-size: 0.9rem; word-break: break-all; color: #8b5cf6;">-</div>
    <div class="stat-description" id="even-status" 
         style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 5px;">
         2, 4, 6, 8, 10, 12, 14...
    </div>
</div>

<!-- 子账号文件夹 -->
<div class="stat-card">
    <div class="stat-label">📁 子账号文件夹ID</div>
    <div class="stat-value" id="folder-id" 
         style="font-size: 1.0rem; word-break: break-all; color: #fbbf24;">-</div>
    <div class="stat-description" 
         style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 5px;">
         今日使用的文件夹
    </div>
</div>
```

### JavaScript 逻辑

```javascript
// 读取单数/双数父文件夹ID
const rootFolderOdd = data.root_folder_odd || '1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM';
const rootFolderEven = data.root_folder_even || '1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM';

document.getElementById('root-folder-odd').textContent = rootFolderOdd;
document.getElementById('root-folder-even').textContent = rootFolderEven;

// 判断今天是单数还是双数
const dayOfMonth = new Date().getDate();
const isOddDay = dayOfMonth % 2 === 1;

// 更新状态显示
if (isOddDay) {
    oddStatusEl.textContent = '✅ 今天使用 (1, 3, 5, 7, 9, 11...)';
    oddStatusEl.style.color = '#10b981';  // 绿色
    evenStatusEl.textContent = '📂 备用 (2, 4, 6, 8, 10, 12...)';
    evenStatusEl.style.color = 'rgba(255,255,255,0.4)';  // 灰色
} else {
    // 双数日期的处理逻辑...
}

// 子账号文件夹ID
document.getElementById('folder-id').textContent = data.folder_id || '未找到';
```

### API 端点

#### `/api/gdrive-detector/status`

**返回数据**：
```json
{
  "success": true,
  "data": {
    "detector_running": true,
    "file_timestamp": "2025-12-13 00:38:04",
    "delay_minutes": 47,
    "check_count": 23,
    "last_check_time": "2025-12-13 00:38:04",
    "current_time": "2025-12-13 01:25:00",
    "folder_id": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "root_folder_odd": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "root_folder_even": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "today_date": "2025年12月13日"
  }
}
```

**数据来源**：
```python
# 从配置文件读取
config_file = '/home/user/webapp/daily_folder_config.json'
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)
    root_folder_odd = config.get('root_folder_odd', '默认值')
    root_folder_even = config.get('root_folder_even', '默认值')
```

---

## 📝 配置文件

### daily_folder_config.json

```json
{
  "root_folder_odd": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
  "root_folder_even": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
  "folder_id": "13js7p3V4FUtbkfZxWq9et_xYz7EQ9Q9O",
  "data_date": "2025-12-12",
  "current_date": "2025-12-12",
  "last_update": "2025-12-13 00:40:00",
  "root_folder_description": {
    "odd": "单数日期父文件夹 (1, 3, 5, 7, 9, 11...)",
    "even": "双数日期父文件夹 (2, 4, 6, 8, 10, 12...)"
  }
}
```

### 更新配置工具

使用 `update_root_folders.py` 更新父文件夹ID：

```bash
# 查看当前配置
python3 update_root_folders.py

# 更新单数日期父文件夹
python3 update_root_folders.py --odd <新的folder_id>

# 更新双数日期父文件夹
python3 update_root_folders.py --even <新的folder_id>

# 同时更新两个
python3 update_root_folders.py --odd <id1> --even <id2>
```

---

## 🎯 功能说明

### 1. 单数日期父文件夹 (1️⃣)
- **用途**：每月单数日期（1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31号）的根文件夹
- **显示颜色**：蓝色 (#3b82f6)
- **状态标识**：
  - 单数日期当天：✅ 今天使用（绿色）
  - 双数日期当天：📂 备用（灰色）

### 2. 双数日期父文件夹 (2️⃣)
- **用途**：每月双数日期（2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30号）的根文件夹
- **显示颜色**：紫色 (#8b5cf6)
- **状态标识**：
  - 双数日期当天：✅ 今天使用（绿色）
  - 单数日期当天：📂 备用（灰色）

### 3. 子账号文件夹ID (📁)
- **用途**：今天实际使用的文件夹ID（日期文件夹）
- **显示颜色**：金色 (#fbbf24)
- **说明**：这是在父文件夹下面，按日期创建的子文件夹
- **示例**：如果父文件夹是 `1jFGGlGP...`，那么今天的子文件夹可能是 `13js7p3V...`

---

## 📊 显示逻辑

### 自动日期检测

```javascript
// 获取今天的日期号数
const today = new Date();
const dayOfMonth = today.getDate();  // 例如：13

// 判断是单数还是双数
const isOddDay = dayOfMonth % 2 === 1;  // 13 % 2 = 1 (单数)
```

### 状态显示规则

| 今天日期 | 单数文件夹状态 | 双数文件夹状态 |
|---------|--------------|--------------|
| 1, 3, 5, 7, 9, 11, 13... | ✅ 今天使用 | 📂 备用 |
| 2, 4, 6, 8, 10, 12, 14... | 📂 备用 | ✅ 今天使用 |

---

## 🔍 测试验证

### 1. 访问页面
```
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/gdrive-detector
```

### 2. 检查显示
- ✅ 应该看到三个卡片：单数父文件夹、双数父文件夹、子账号文件夹
- ✅ 今天是13号（单数），单数卡片应显示"✅ 今天使用"
- ✅ 双数卡片应显示"📂 备用"
- ✅ 子账号文件夹显示今天的文件夹ID

### 3. API 测试
```bash
curl -s "http://localhost:5000/api/gdrive-detector/status" | python3 -c "
import sys, json
d = json.load(sys.stdin)['data']
print('单数父文件夹:', d.get('root_folder_odd'))
print('双数父文件夹:', d.get('root_folder_even'))
print('子账号文件夹:', d.get('folder_id'))
"
```

**预期输出**：
```
单数父文件夹: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
双数父文件夹: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
子账号文件夹: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
```

---

## 📚 相关文档

- **[ROOT_FOLDERS_GUIDE.md](ROOT_FOLDERS_GUIDE.md)** - 父文件夹管理完整指南
- **[FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)** - 功能总结
- **[update_root_folders.py](update_root_folders.py)** - 配置更新工具

---

## 🎨 UI 效果对比

### 之前的显示
```
┌──────────────────────────────────┐
│ 📁 今日文件夹                     │
│ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ 📦 父文件夹ID                     │
│ 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV │
└──────────────────────────────────┘
```

### 现在的显示
```
┌──────────────────────────────────┐  ┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ 1️⃣ 单数日期父文件夹 (蓝色)       │  │ 2️⃣ 双数日期父文件夹 (紫色)       │  │ 📁 子账号文件夹ID (金色)          │
│ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM │  │ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM │  │ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM │
│ ✅ 今天使用 (1, 3, 5, 7...)      │  │ 📂 备用 (2, 4, 6, 8...)          │  │ 今日使用的文件夹                  │
└──────────────────────────────────┘  └──────────────────────────────────┘  └──────────────────────────────────┘
```

---

## ✅ 完成清单

- [x] ✅ 显示单数日期父文件夹ID
- [x] ✅ 显示双数日期父文件夹ID
- [x] ✅ 显示子账号文件夹ID（今日文件夹）
- [x] ✅ 自动检测今天是单数还是双数
- [x] ✅ 高亮显示当前使用的父文件夹
- [x] ✅ 颜色区分（蓝色、紫色、金色）
- [x] ✅ API返回三个folder ID
- [x] ✅ 从配置文件读取
- [x] ✅ 状态标识（✅ 今天使用 / 📂 备用）
- [x] ✅ 响应式布局
- [x] ✅ 实时刷新

---

**📍 更新时间**: 2025-12-13 01:00 (北京时间)  
**🎯 状态**: ✅ **已完成并部署**  
**🌐 访问**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/gdrive-detector  
**📖 文档**: ✅ **完整**
