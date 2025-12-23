# 🔧 单数/双数父文件夹ID配置修复指南

## ❌ 当前问题

用户反映：**今天13号应该是单数，但是和双数的ID一样，这是错误的。没有重新取ID，而是从数据里取了老的ID。**

### 问题分析
检查配置文件 `daily_folder_config.json`：
```json
{
    "root_folder_odd": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
    "root_folder_even": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"
}
```

**问题核心**：
- ✅ 单数日期（1,3,5,7,9,11,13...）父文件夹ID：`1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM`
- ✅ 双数日期（2,4,6,8,10,12,14...）父文件夹ID：`1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM`
- ❌ **两个ID完全相同！应该是不同的文件夹ID！**

---

## ✅ 解决方案

### 步骤1: 确认Google Drive中实际的文件夹结构

您需要提供两个**不同的**父文件夹ID：

```
📁 单数日期文件夹 (1, 3, 5, 7, 9, 11, 13...)
   └─ ID: ????????????????

📁 双数日期文件夹 (2, 4, 6, 8, 10, 12, 14...)
   └─ ID: ????????????????
```

**如何获取文件夹ID？**
1. 在Google Drive中打开对应文件夹
2. 查看浏览器地址栏URL
3. 提取 `/folders/` 后面的ID部分

例如：
```
https://drive.google.com/drive/folders/1ABCxyz123_-example
                                         ↑
                                   这就是文件夹ID
```

---

### 步骤2: 使用工具更新配置

运行以下命令更新配置：

```bash
# 更新单数日期父文件夹ID
python3 /home/user/webapp/update_root_folders.py --odd "你的单数文件夹ID"

# 更新双数日期父文件夹ID
python3 /home/user/webapp/update_root_folders.py --even "你的双数文件夹ID"

# 一次性设置两个
python3 /home/user/webapp/update_root_folders.py \
    --odd "单数文件夹ID" \
    --even "双数文件夹ID"
```

---

### 步骤3: 验证配置

```bash
# 查看当前配置
python3 /home/user/webapp/update_root_folders.py --view

# 测试今天应该使用哪个文件夹
python3 /home/user/webapp/test_odd_even_selection.py
```

---

### 步骤4: 重启监控进程

```bash
cd /home/user/webapp && pm2 restart gdrive-monitor
cd /home/user/webapp && pm2 restart flask-app
```

---

## 🔍 系统逻辑说明

### 自动选择机制

系统会根据当天日期自动选择父文件夹：

```python
今天日期 = 13号
13 % 2 == 1  → 单数日期
系统使用 → root_folder_odd
```

```python
今天日期 = 14号
14 % 2 == 0  → 双数日期
系统使用 → root_folder_even
```

### 监控日志输出

正常情况下，日志会显示：

**单数日期（如13号）：**
```
[2025-12-13 01:00:00] 📅 今天是13号（单数日期）
[2025-12-13 01:00:00] 📂 使用单数日期父文件夹: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
```

**双数日期（如14号）：**
```
[2025-12-14 01:00:00] 📅 今天是14号（双数日期）
[2025-12-14 01:00:00] 📂 使用双数日期父文件夹: 另一个不同的ID
```

---

## 📝 配置文件格式

`daily_folder_config.json` 正确格式：

```json
{
    "root_folder_odd": "单数日期父文件夹ID",
    "root_folder_even": "双数日期父文件夹ID",
    "folder_id": "当前子账号今日文件夹ID",
    "data_date": "2025-12-13",
    "current_date": "2025-12-13",
    "last_update": "2025-12-13 01:00:00",
    "root_folder_description": {
        "odd": "单数日期父文件夹 (1, 3, 5, 7, 9, 11...)",
        "even": "双数日期父文件夹 (2, 4, 6, 8, 10, 12...)"
    }
}
```

---

## ⚠️ 重要提醒

1. **单数和双数文件夹ID必须不同**  
   如果相同，系统将无法正确切换文件夹

2. **文件夹ID格式**  
   正确格式：`1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM`（字母、数字、下划线、连字符）

3. **11分钟超时恢复机制**  
   当超过11分钟未找到新文件时，系统会自动触发恢复：
   - 根据今天日期选择对应的父文件夹（单数/双数）
   - 在父文件夹中搜索今天日期的子文件夹
   - 更新配置文件为新的子文件夹ID

4. **跨日期自动切换**  
   每天00:00后，系统会自动：
   - 判断新日期是单数还是双数
   - 选择对应的父文件夹
   - 搜索并更新今天的子文件夹ID

---

## 🧪 测试验证

运行测试脚本验证配置：

```bash
cd /home/user/webapp

# 测试今天应该使用哪个文件夹
python3 test_odd_even_selection.py

# 预期输出（13号为例）：
# ✅ 今天: 2025-12-13 (单数日期)
# 📂 应使用单数父文件夹: xxxxxx
# ⚠️  当前配置的双数父文件夹: yyyyyy
# ❌ 检测到问题: 单数和双数文件夹ID相同！
```

---

## 📞 下一步行动

**请提供以下信息：**

1. **单数日期父文件夹的Google Drive ID**（用于1,3,5,7,9,11,13...号）
2. **双数日期父文件夹的Google Drive ID**（用于2,4,6,8,10,12,14...号）

提供后，我将立即：
1. 更新配置文件
2. 重启监控服务
3. 验证系统正确识别并使用对应文件夹
4. 提交代码并创建PR

---

## 📊 当前系统状态

- 监控服务: ✅ 运行中
- Flask应用: ✅ 运行中
- 配置文件: ⚠️  单数/双数ID相同（需要修复）
- 检测逻辑: ✅ 已实现（待配置正确ID后生效）

完成时间: 2025-12-13 01:00 (北京时间)
