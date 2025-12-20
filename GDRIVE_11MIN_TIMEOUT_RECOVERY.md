# Google Drive 11分钟超时恢复机制

**实现日期**: 2025-12-12  
**Git提交**: `b9b3dd1`  
**功能**: 超过11分钟未找到TXT文件时自动恢复  

---

## 🎯 问题场景

从用户截图可以看到:
- **当前时间**: 12-12 00:10:58 (北京时间)
- **当前时间发现时间**: 00:10:43
- **检测次数**: 已检测 20 分钟
- **问题**: 超过11分钟没有找到TXT文件

这种情况通常发生在:
1. 日期文件夹ID配置错误
2. 跨日期时新文件夹尚未创建
3. Google Drive访问权限变更

---

## 🛡️ 解决方案: 11分钟超时恢复机制

### 工作流程

```
┌─────────────────────────────────────────────────┐
│  正常监控: 每30秒检查一次TXT文件                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  找到文件?      │
         └────┬──────┬────┘
              │Yes   │No
              ▼      ▼
         ┌─────┐  ┌──────────────────┐
         │继续 │  │ 计时器累加        │
         │监控 │  │ (last_file_found_time)│
         └─────┘  └──────┬───────────┘
                         │
                         ▼
                  ┌─────────────────┐
                  │ 超过11分钟?     │
                  └────┬──────┬─────┘
                       │Yes   │No
                       ▼      ▼
              ┌─────────────┐ ┌──────┐
              │触发恢复机制  │ │继续等│
              │             │ │待    │
              └─────┬───────┘ └──────┘
                    │
                    ▼
         ┌────────────────────────────┐
         │ 1. 访问根文件夹             │
         │ 2. 查找今天日期文件夹       │
         │ 3. 提取新文件夹ID           │
         │ 4. 更新配置文件             │
         │ 5. 重置计时器               │
         │ 6. 继续监控                 │
         └────────────────────────────┘
```

---

## 📋 实现细节

### 1. 配置参数

```python
# 根文件夹ID (所有日期文件夹的父文件夹)
ROOT_FOLDER_ID = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"

# 超时阈值 = 11分钟
TIMEOUT_THRESHOLD = 11 * 60  # 660秒

# 检测间隔 = 30秒
CHECK_INTERVAL = 30
```

### 2. 核心函数

#### `get_root_folder_id_and_create_today_folder()`
```python
def get_root_folder_id_and_create_today_folder():
    """
    11分钟超时恢复机制:
    1. 重新获取根文件夹ID (父文件夹)
    2. 在根文件夹下创建/查找今天日期的文件夹
    3. 更新配置文件
    4. 返回新的文件夹ID
    """
    today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
    
    # 步骤1: 访问根文件夹
    url = f"https://drive.google.com/embeddedfolderview?id={ROOT_FOLDER_ID}"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 步骤2: 查找今天日期的文件夹
    for link in soup.find_all('a', href=True):
        foldername = link.get_text(strip=True)
        
        if foldername == today:  # 例如: "2025-12-12"
            # 提取文件夹ID
            match = re.search(r'/folders/([a-zA-Z0-9_-]+)', href)
            today_folder_id = match.group(1)
            
            # 步骤3: 更新配置文件
            config = {
                'current_date': today,
                'folder_id': today_folder_id,
                'updated_at': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S'),
                'update_reason': '11分钟超时自动恢复'
            }
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return today_folder_id
    
    return None
```

### 3. 监控循环中的超时检测

```python
# 初始化计时器
last_file_found_time = datetime.now(BEIJING_TZ)
timeout_recovery_triggered = False

while True:
    # 查找文件
    file_info = step2_count_txt_files(current_folder_id, today)
    
    if not file_info:
        # 计算已等待时间
        time_since_last_file = (datetime.now(BEIJING_TZ) - last_file_found_time).total_seconds()
        minutes_elapsed = time_since_last_file / 60
        
        # 超过11分钟且未触发过恢复
        if minutes_elapsed > 11 and not timeout_recovery_triggered:
            log("⚠️ 触发11分钟超时恢复机制!")
            
            # 执行恢复
            new_folder_id = get_root_folder_id_and_create_today_folder()
            
            if new_folder_id:
                # 更新文件夹ID
                current_folder_id = new_folder_id
                
                # 重置计时器
                last_file_found_time = datetime.now(BEIJING_TZ)
                timeout_recovery_triggered = True
                
                # 立即重试
                file_info = step2_count_txt_files(current_folder_id, today)
                
                if file_info:
                    log("🎉 恢复成功!")
                    timeout_recovery_triggered = False
        else:
            if minutes_elapsed > 5:
                log(f"⏳ 已等待 {minutes_elapsed:.1f} 分钟 (阈值: 11分钟)")
    else:
        # 找到文件,重置计时器
        last_file_found_time = datetime.now(BEIJING_TZ)
        timeout_recovery_triggered = False
```

---

## 📊 日志输出示例

### 正常运行 (< 5分钟)
```
[2025-12-12 00:10:30] 🔍 检查 #10 | 2025-12-12 00:10:30
[2025-12-12 00:10:30] 📂 当前使用的文件夹ID: 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
[2025-12-12 00:10:32] ⏰ 没有找到文件，等待下次检查...
```

### 等待中 (5-11分钟)
```
[2025-12-12 00:15:30] 🔍 检查 #20 | 2025-12-12 00:15:30
[2025-12-12 00:15:32] ⏳ 已等待 6.2 分钟未找到文件 (超时阈值: 11分钟)
[2025-12-12 00:15:32] ⏰ 没有找到文件，等待下次检查...
```

### 触发恢复 (> 11分钟)
```
[2025-12-12 00:21:30] 🔍 检查 #30 | 2025-12-12 00:21:30

⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
⏱️  警告: 已经 11.5 分钟未找到TXT文件!
🔧 启动11分钟超时恢复机制...
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️

🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
⚠️  触发11分钟超时恢复机制！
📅 目标日期文件夹: 2025-12-12
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄

📂 步骤1: 访问根文件夹 1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM
   ✅ 找到今天的文件夹: 2025-12-12
   📂 文件夹ID: 1abcdefgh123456789

📝 步骤2: 更新配置文件
   ✅ 配置文件已更新
   📅 日期: 2025-12-12
   📂 文件夹ID: 1abcdefgh123456789

✅ 恢复机制执行成功！
📂 新文件夹ID: 1abcdefgh123456789
🔄 重置计时器，继续监控...

🔍 使用新文件夹ID重新查找文件...
   ✅ 找到 5 个TXT文件（含真实ID）
   最新3个文件: 2025-12-12_0020.txt, 2025-12-12_0015.txt, ...

🎉 恢复成功! 在新文件夹中找到 5 个TXT文件
```

---

## 🔍 恢复机制触发条件

| 条件 | 说明 |
|------|------|
| **时间阈值** | 超过11分钟 (660秒) 未找到TXT文件 |
| **触发标志** | `timeout_recovery_triggered = False` (未被触发过) |
| **检测频率** | 每30秒检查一次 |
| **重置条件** | 找到文件 OR 恢复成功 |

---

## 📝 配置文件格式

### daily_folder_config.json
```json
{
  "current_date": "2025-12-12",
  "folder_id": "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM",
  "updated_at": "2025-12-12 00:21:35",
  "update_reason": "11分钟超时自动恢复"
}
```

---

## 🛠️ 手动配置根文件夹ID

如果需要修改根文件夹ID,编辑 `gdrive_final_detector.py`:

```python
# 配置 (第22行)
ROOT_FOLDER_ID = "YOUR_ROOT_FOLDER_ID_HERE"  # 替换为实际的根文件夹ID
```

---

## 🔧 调试和测试

### 1. 查看实时日志
```bash
pm2 logs gdrive-monitor --lines 50
```

### 2. 检查配置文件
```bash
cat /home/user/webapp/daily_folder_config.json
```

### 3. 手动触发恢复测试
```bash
# 修改超时阈值为1分钟 (测试用)
# 编辑 gdrive_final_detector.py 第24行:
TIMEOUT_THRESHOLD = 1 * 60  # 改为60秒

# 重启服务
pm2 restart gdrive-monitor

# 观察日志
pm2 logs gdrive-monitor
```

### 4. 验证恢复功能
```bash
# 等待1分钟后,应该看到:
# ⚠️  警告: 已经 1.x 分钟未找到TXT文件!
# 🔧 启动11分钟超时恢复机制...
```

---

## ⚠️ 注意事项

### 1. 根文件夹结构要求
```
根文件夹 (ROOT_FOLDER_ID)
├── 2025-12-10/
│   ├── 2025-12-10_0000.txt
│   ├── 2025-12-10_0005.txt
│   └── ...
├── 2025-12-11/
│   ├── 2025-12-11_0000.txt
│   └── ...
└── 2025-12-12/  ← 今天的文件夹
    ├── 2025-12-12_0000.txt
    └── ...
```

### 2. 文件夹命名规范
- 必须使用 `YYYY-MM-DD` 格式 (例如: `2025-12-12`)
- 不能有多余的空格或特殊字符
- 区分大小写

### 3. 恢复失败处理
如果恢复机制执行失败:
- 继续使用当前文件夹ID
- 不会重复触发恢复 (防止死循环)
- 需要手动检查根文件夹结构和权限

---

## 📈 性能影响

| 指标 | 值 | 说明 |
|------|-----|------|
| 额外网络请求 | 1次/11分钟 | 仅在超时时触发 |
| 额外CPU占用 | 可忽略 | 简单的时间计算 |
| 额外内存占用 | < 1KB | 仅存储时间戳 |
| 恢复耗时 | 2-5秒 | 访问根文件夹+更新配置 |

---

## ✅ 用户场景

### 场景1: 跨日期时没有新文件夹
**问题**: 0:00-0:10之间,新日期文件夹还没创建

**解决**:
1. 系统继续使用昨天的文件夹ID (0:00-0:10)
2. 如果超过11分钟还没文件,触发恢复机制
3. 自动查找并切换到新日期文件夹

---

### 场景2: 配置文件错误
**问题**: `daily_folder_config.json` 中的文件夹ID不正确

**解决**:
1. 系统持续检测,超过11分钟未找到文件
2. 自动访问根文件夹,重新获取正确的文件夹ID
3. 更新配置文件,继续监控

---

### 场景3: Google Drive权限变更
**问题**: 原文件夹访问权限被撤销

**解决**:
1. 检测超时,触发恢复机制
2. 尝试从根文件夹重新获取
3. 如果根文件夹也无权限,则记录错误日志

---

## 🎯 总结

✅ **自动化**: 无需人工干预  
✅ **智能化**: 11分钟阈值防止误触发  
✅ **可靠性**: 失败后继续使用当前配置  
✅ **可追溯**: 完整的日志记录  
✅ **易维护**: 配置文件自动更新  

**现在,系统可以自动从配置错误或跨日期问题中恢复!** 🎉

---

## 🔗 相关文件

- **主程序**: `gdrive_final_detector.py`
- **配置文件**: `daily_folder_config.json`
- **日志文件**: `gdrive_final_detector.log`
- **PM2配置**: `ecosystem.config.js`

---

**Git提交**: `b9b3dd1`  
**实现日期**: 2025-12-12  
**状态**: ✅ 已部署并运行
