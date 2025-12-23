# 📂 父文件夹ID管理指南

## 🎯 功能概述

系统现在支持**两个独立的父文件夹ID**，根据日期的单双数自动选择：
- **单数日期父文件夹**：用于每月的 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31 号
- **双数日期父文件夹**：用于每月的 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30 号

这样的设计可以：
- ✅ 分散存储压力
- ✅ 更灵活的数据管理
- ✅ 支持A/B测试或灾备方案
- ✅ 自动切换，无需手动干预

---

## 🌐 监控页面展示

### 访问地址
```
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/gdrive-monitor-status
```

### 页面布局

在数据源警告框和超时保险框之间，新增了**两个父文件夹ID显示框**：

```
┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│ 1️⃣  单数日期父文件夹                │  │ 2️⃣  双数日期父文件夹                │
│                                     │  │                                     │
│ 1, 3, 5, 7, 9, 11, 13, 15...       │  │ 2, 4, 6, 8, 10, 12, 14, 16...       │
├─────────────────────────────────────┤  ├─────────────────────────────────────┤
│ Folder ID:                          │  │ Folder ID:                          │
│ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM   │  │ 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM   │
│                                     │  │                                     │
│ [✅ 今天使用]                        │  │ [📂 备用]                            │
└─────────────────────────────────────┘  └─────────────────────────────────────┘
     蓝色渐变 + 蓝色边框                          紫色渐变 + 紫色边框
```

### 视觉效果

#### 单数日期框（今天是13号）
- **背景**：蓝色渐变 (rgba(59,130,246) → rgba(37,99,235))
- **边框**：3px 蓝色实线 (#3b82f6)
- **图标**：1️⃣
- **状态徽章**：✅ 今天使用 (绿色)

#### 双数日期框
- **背景**：紫色渐变 (rgba(139,92,246) → rgba(124,58,237))
- **边框**：3px 紫色实线 (#8b5cf6)
- **图标**：2️⃣
- **状态徽章**：📂 备用 (蓝灰色)

---

## 🛠️ 配置工具

### 工具脚本：`update_root_folders.py`

这是一个命令行工具，用于更新父文件夹ID配置。

#### 1. 查看当前配置

```bash
cd /home/user/webapp
python3 update_root_folders.py
```

**输出示例：**
```
======================================================================
📂 当前父文件夹ID配置
======================================================================

📅 今天日期: 2025-12-13 (13号)
📌 今天使用: 单数日期父文件夹

1️⃣  单数日期父文件夹 (1, 3, 5, 7, 9, 11, 13...)
   ID: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
   状态: ✅ 今天使用

2️⃣  双数日期父文件夹 (2, 4, 6, 8, 10, 12, 14...)
   ID: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
   状态: 📂 备用

⏰ 最后更新: 2025-12-11 23:11:13
======================================================================
```

#### 2. 更新单数日期父文件夹

```bash
python3 update_root_folders.py --odd <新的folder_id>
```

**示例：**
```bash
python3 update_root_folders.py --odd 1ABC123XYZ456def789
```

#### 3. 更新双数日期父文件夹

```bash
python3 update_root_folders.py --even <新的folder_id>
```

**示例：**
```bash
python3 update_root_folders.py --even 1XYZ789ABC123def456
```

#### 4. 同时更新两个

```bash
python3 update_root_folders.py --odd <id1> --even <id2>
```

**示例：**
```bash
python3 update_root_folders.py \
  --odd 1ABC123XYZ456def789 \
  --even 1XYZ789ABC123def456
```

---

## 📋 配置文件结构

### 文件位置
```
/home/user/webapp/daily_folder_config.json
```

### JSON 格式

```json
{
  "root_folder_odd": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
  "root_folder_even": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
  "folder_id": "13js7p3V4FUtbkfZxWq9et_xYz7EQ9Q9O",
  "data_date": "2025-12-12",
  "current_date": "2025-12-12",
  "last_update": "2025-12-13 00:35:00",
  "root_folder_description": {
    "odd": "单数日期父文件夹 (1, 3, 5, 7, 9, 11...)",
    "even": "双数日期父文件夹 (2, 4, 6, 8, 10, 12...)"
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `root_folder_odd` | String | 单数日期的父文件夹ID |
| `root_folder_even` | String | 双数日期的父文件夹ID |
| `folder_id` | String | 当前使用的文件夹ID |
| `data_date` | String | 数据日期 |
| `current_date` | String | 当前日期 |
| `last_update` | String | 最后更新时间 |
| `root_folder_description` | Object | 描述信息 |

---

## 🔧 API 端点

### `/api/gdrive-monitor/status`

现在返回的JSON包含父文件夹ID：

```json
{
  "success": true,
  "root_folder_odd": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
  "root_folder_even": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
  "today_date": "2025-12-13",
  "current_folder_id": "13js7p3V4FUtbkfZxWq9et_xYz7EQ9Q9O",
  "folder_date": "2025-12-12",
  "data_source_status": "stale",
  ...
}
```

### 使用示例

```bash
# 获取父文件夹ID
curl -s "http://localhost:5000/api/gdrive-monitor/status" | \
  python3 -c "import sys, json; d=json.load(sys.stdin); \
  print('单数:', d['root_folder_odd']); \
  print('双数:', d['root_folder_even'])"
```

---

## 🎨 前端逻辑

### 自动检测今天使用哪个文件夹

JavaScript会自动判断今天是单数还是双数日期：

```javascript
const today = new Date();
const dayOfMonth = today.getDate();
const isOddDay = dayOfMonth % 2 === 1;

if (isOddDay) {
    // 今天是单数日期 (1, 3, 5, 7...)
    statusOddEl.innerHTML = '✅ 今天使用';
    statusEvenEl.innerHTML = '📂 备用';
} else {
    // 今天是双数日期 (2, 4, 6, 8...)
    statusOddEl.innerHTML = '📂 备用';
    statusEvenEl.innerHTML = '✅ 今天使用';
}
```

### 自动刷新

页面每2秒自动刷新一次，实时更新状态。

---

## 📝 使用场景

### 场景1：正常切换
- **今天是13号（单数）**
  - 系统自动使用 `root_folder_odd`
  - 页面显示：单数框标记为"✅ 今天使用"
  
- **明天是14号（双数）**
  - 系统自动切换到 `root_folder_even`
  - 页面显示：双数框标记为"✅ 今天使用"

### 场景2：更新父文件夹ID

假设你需要更换单数日期的父文件夹：

```bash
# 1. 查看当前配置
python3 update_root_folders.py

# 2. 更新单数日期父文件夹
python3 update_root_folders.py --odd 1NewFolderID123456

# 3. 重启监控服务（可选，如果需要立即生效）
pm2 restart gdrive-monitor

# 4. 检查监控页面
# 访问 https://5000-xxx.sandbox.novita.ai/gdrive-monitor-status
# 确认单数框显示新的Folder ID
```

### 场景3：灾备切换

如果发现某个父文件夹出现问题：

```bash
# 临时将问题文件夹的ID指向备用文件夹
python3 update_root_folders.py --odd <备用文件夹ID>

# 监控页面会立即显示新的配置
```

---

## 🚀 部署说明

### 已部署组件

1. ✅ 监控页面UI（两个父文件夹框）
2. ✅ API端点（返回 `root_folder_odd` 和 `root_folder_even`）
3. ✅ 配置文件结构（支持两个root folder ID）
4. ✅ 管理工具（`update_root_folders.py`）

### 服务状态

```bash
# 查看Flask应用状态
pm2 list | grep flask-app

# 查看监控服务状态
pm2 list | grep gdrive-monitor
```

---

## 🎯 快速开始

### 第一次使用

1. **查看当前配置**
   ```bash
   cd /home/user/webapp
   python3 update_root_folders.py
   ```

2. **设置父文件夹ID**（如果还没设置）
   ```bash
   python3 update_root_folders.py \
     --odd <单数日期父文件夹ID> \
     --even <双数日期父文件夹ID>
   ```

3. **访问监控页面**
   ```
   https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/gdrive-monitor-status
   ```

4. **验证显示**
   - 确认两个框都显示正确的Folder ID
   - 确认今天对应的框标记为"✅ 今天使用"
   - 确认备用框标记为"📂 备用"

---

## 📚 相关文档

- [GDRIVE_DATA_SOURCE_DIAGNOSIS.md](GDRIVE_DATA_SOURCE_DIAGNOSIS.md) - 数据源诊断
- [GDRIVE_11MIN_TIMEOUT_RECOVERY.md](GDRIVE_11MIN_TIMEOUT_RECOVERY.md) - 超时恢复机制
- [GDRIVE_MONITOR_VISUALIZATION.md](GDRIVE_MONITOR_VISUALIZATION.md) - 监控可视化

---

## 🔍 故障排查

### 问题1：页面不显示父文件夹ID

**检查：**
```bash
# 1. 确认配置文件存在且格式正确
cat /home/user/webapp/daily_folder_config.json

# 2. 测试API
curl -s "http://localhost:5000/api/gdrive-monitor/status" | grep root_folder

# 3. 检查Flask应用日志
pm2 logs flask-app --lines 50
```

### 问题2：状态徽章显示错误

**原因**：可能是浏览器缓存

**解决**：
1. 强制刷新页面 (Ctrl + Shift + R 或 Cmd + Shift + R)
2. 清除浏览器缓存
3. 检查今天日期是否正确

### 问题3：更新后不生效

**检查**：
```bash
# 1. 确认配置已保存
cat /home/user/webapp/daily_folder_config.json | grep root_folder

# 2. 重启Flask应用
pm2 restart flask-app

# 3. 等待几秒后访问页面
```

---

## 💡 最佳实践

### 1. 定期备份配置
```bash
# 备份配置文件
cp /home/user/webapp/daily_folder_config.json \
   /home/user/webapp/daily_folder_config.backup.json
```

### 2. 更新前先查看
```bash
# 总是先查看当前配置
python3 update_root_folders.py

# 再进行更新
python3 update_root_folders.py --odd <new_id>
```

### 3. 验证更新结果
```bash
# 更新后立即验证
python3 update_root_folders.py

# 并访问监控页面确认
```

---

**📍 更新时间**: 2025-12-13 00:40 (北京时间)  
**🔧 功能状态**: ✅ 已部署并测试  
**🌐 监控页面**: [查看实时状态](https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/gdrive-monitor-status)
