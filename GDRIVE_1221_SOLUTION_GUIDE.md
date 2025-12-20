# 🚨 12-21 数据缺失问题 - 完整解决方案

## 问题现状

**时间**: 2025-12-21 02:50 (Beijing Time)  
**问题**: 系统未采集到 2025-12-21 的数据  
**影响**: 首页数据监控停止更新，最后数据时间 2025-12-20 23:54:00

---

## 根本原因 (3个关键问题)

### 1️⃣ Google Drive 凭证文件缺失 🔴 CRITICAL

**缺失文件**:
```bash
❌ credentials.json   # Google Drive API 凭证
❌ token.pickle       # 认证令牌
✅ credentials.json.example  # 只有示例文件
```

**影响**:
- 无法访问 Google Drive API
- 无法自动探索文件夹结构
- 无法自动获取新日期文件夹ID
- 自动更新功能完全失效

### 2️⃣ 配置文件日期过期

**当前配置** (`daily_folder_config.json`):
```json
{
    "current_date": "2025-12-20",  // ❌ 应该是 2025-12-21
    "folder_id": "1e5QUggAocpt77SG0ER-g-gaADUyEWWPe",
    "parent_folder_id": "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"
}
```

### 3️⃣ 00:10 定时任务错过执行

**原因**: 服务重启时间 02:34:26，已过当天的 00:10 触发时间  
**下次触发**: 明天 2025-12-22 00:10 (Beijing Time)  
**时区修复**: ✅ 已完成 (UTC 16:10 = Beijing 00:10)

---

## 解决方案 (3个方案)

### 🎯 方案A: 快速手动修复 (推荐)

**需要**: 用户提供正确的 folder ID

#### 步骤1: 获取 folder ID

访问您的 Google Drive:
1. 打开: https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH
2. 进入【首页数据】文件夹
3. 复制 URL 中的 folder ID
   - URL 格式: `https://drive.google.com/drive/folders/{FOLDER_ID}`
   - 例如: `1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV`
4. 进入【2025-12-21】或【可行】文件夹
5. 复制该文件夹的 ID

#### 步骤2: 运行更新脚本

```bash
cd /home/user/webapp

# 方式1: 更新 parent 和 daily folder (推荐)
./manual_update_folder_config.sh <首页数据_folder_id> <2025-12-21_folder_id>

# 方式2: 只更新 daily folder
./manual_update_folder_config.sh <2025-12-21_folder_id>
```

**示例**:
```bash
# 假设您提供的ID是:
# 首页数据: 1ABC123xyz
# 2025-12-21: 1DEF456abc

./manual_update_folder_config.sh 1ABC123xyz 1DEF456abc
```

#### 步骤3: 验证

```bash
# 查看新配置
cat daily_folder_config.json

# 手动触发采集
python3 gdrive_final_detector.py

# 查看日志
pm2 logs gdrive-monitor --lines 30 --nostream
```

**时间**: 5分钟内完成  
**效果**: 立即恢复数据采集

---

### 🔧 方案B: 恢复凭证文件 (长期解决)

**需要**: 从备份恢复或重新创建凭证

#### 选项1: 从备份恢复

```bash
cd /home/user/webapp

# 从备份中找到这两个文件
credentials.json
token.pickle

# 复制到项目根目录
# 重启服务
pm2 restart all
```

#### 选项2: 重新创建

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目
3. 启用 Google Drive API
4. 创建 OAuth 2.0 凭证
5. 下载 `credentials.json`
6. 运行认证流程生成 `token.pickle`

**时间**: 10-15分钟  
**好处**: 完全恢复自动化功能

---

### ⏳ 方案C: 等待明天自动触发 (不推荐)

**触发时间**: 2025-12-22 00:10 (Beijing Time)  
**代价**: 丢失今天的数据  
**风险**: ⚠️ 如果 parent_folder_id 不正确，明天仍会失败

---

## 文件夹结构说明

### 正确的层级关系

```
📁 爷爷文件夹 (1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH)
   https://drive.google.com/drive/folders/1U5VjRis2FYnBJvtR_8mmPrmFcJCMPGrH
   
   └─ 📁 首页数据 (Homepage Data)
      ↑ 这个文件夹的 ID 应该是 parent_folder_id
      
      └─ 📁 2025-12-21 或 可行
         ↑ 这个文件夹的 ID 应该是 folder_id
         
         ├─ 📄 2025-12-21_0010.txt
         ├─ 📄 2025-12-21_0020.txt
         ├─ 📄 2025-12-21_0030.txt
         └─ ...
```

### 当前使用的 ID (可能不正确)

```
parent_folder_id: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
folder_id: 1e5QUggAocpt77SG0ER-g-gaADUyEWWPe
默认fallback: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
```

**问题**: 这些ID可能不是您的【首页数据】文件夹

---

## 快速诊断命令

### 查看当前配置
```bash
cat /home/user/webapp/daily_folder_config.json | python3 -m json.tool
```

### 查看最新数据时间
```bash
sqlite3 /home/user/webapp/crypto_data.db \
  "SELECT datetime(snapshot_time) as time, urgent_rise, urgent_fall 
   FROM homepage_snapshots 
   ORDER BY snapshot_time DESC LIMIT 10;"
```

### 查看服务状态
```bash
pm2 status | grep gdrive
pm2 logs gdrive-monitor --lines 20 --nostream
pm2 logs gdrive-auto-trigger --lines 20 --nostream
```

### 手动触发采集
```bash
cd /home/user/webapp && python3 gdrive_final_detector.py 2>&1 | head -50
```

---

## 下一步行动

### 📌 立即需要做的 (选择其一)

1. **方案A - 最快**: 
   - 提供【首页数据】folder ID
   - 提供【2025-12-21】folder ID
   - 我会立即更新配置

2. **方案B - 完整**: 
   - 提供 `credentials.json` 文件
   - 我会恢复完整的自动化功能

3. **确认现有配置**: 
   - 确认 `parent_folder_id: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV` 
   - 是否就是【首页数据】文件夹的ID

---

## 相关文档

| 文档 | 内容 |
|-----|-----|
| `GDRIVE_1221_MISSING_DATA_ROOT_CAUSE.md` | 详细根因分析 |
| `GDRIVE_0010_TASK_FIX_REPORT.md` | 时区修复记录 |
| `manual_update_folder_config.sh` | 手动更新脚本 |
| `explore_gdrive_folders.py` | 文件夹探索工具 (需要凭证) |

---

## 联系信息

- GitHub PR: https://github.com/jamesyidc/66661/pull/1
- 在线访问: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai

---

**生成时间**: 2025-12-21 02:50:00 (Beijing Time)  
**状态**: 🟡 等待用户提供 folder ID 或凭证文件
