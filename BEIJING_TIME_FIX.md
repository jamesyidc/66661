# 北京时间显示修复说明

## 📋 问题描述

用户反馈支撑阻力分析页面（Support Resistance）的时间显示不正确：
- **显示时间**: 图表X轴显示的是UTC时间（如00:00、01:00等）
- **期望时间**: 应该显示北京时间（UTC+8，如08:00、09:00等）
- **12小时分页**: 每页应该显示12小时的北京时间数据

## 🔍 根本原因

1. **数据库存储**: `crypto_data.db` 中的 `support_resistance_snapshots` 表存储的是UTC时间
   ```
   snapshot_time: 2025-12-12 00:00:00  (UTC)
   ```

2. **API返回**: `/api/support-resistance/snapshots` 直接返回数据库中的UTC时间，没有进行时区转换

3. **前端显示**: 前端直接显示API返回的时间字符串，导致显示UTC时间而非北京时间

## ✅ 解决方案

### 1. API时区转换（app_new.py 第5916-5933行）

在API返回数据前，将UTC时间转换为北京时间：

```python
# 时区转换器
beijing_tz = pytz.timezone('Asia/Shanghai')
utc_tz = pytz.UTC

for row in rows:
    # 将数据库中的UTC时间转换为北京时间
    utc_time = datetime.strptime(row['snapshot_time'], '%Y-%m-%d %H:%M:%S')
    utc_time = utc_tz.localize(utc_time)
    beijing_time = utc_time.astimezone(beijing_tz)
    
    data.append({
        'snapshot_time': beijing_time.strftime('%Y-%m-%d %H:%M:%S'),  # 北京时间
        'snapshot_time_utc': row['snapshot_time'],  # UTC时间（供参考）
        # ... 其他字段
    })
```

### 2. 12小时分页查询（app_new.py 第5867-5890行）

API已支持按北京时间小时范围查询：

```python
# 前端请求: ?date=2025-12-12&start_hour=0&end_hour=12
# 表示: 2025-12-12 00:00 - 12:00 (北京时间)

# API自动转换为UTC时间查询数据库:
beijing_start = beijing_tz.localize(datetime.strptime(f"{date} {start_hour:02d}:00:00", "%Y-%m-%d %H:%M:%S"))
beijing_end = beijing_tz.localize(datetime.strptime(f"{date} {end_hour:02d}:00:00", "%Y-%m-%d %H:%M:%S"))

# 转换为UTC
utc_start = beijing_start.astimezone(utc_tz)  # 2025-12-11 16:00:00 UTC
utc_end = beijing_end.astimezone(utc_tz)      # 2025-12-12 04:00:00 UTC
```

### 3. 前端显示（support_resistance.html 第1073-1079行）

前端直接提取API返回的北京时间显示：

```javascript
// API返回的snapshot_time已经是北京时间
const times = data.map(d => {
    const parts = d.snapshot_time.split(' ');
    const date = parts[0].substring(5); // MM-DD
    const time = parts[1].substring(0, 5); // HH:MM
    return `${date}|${time}`;  // 格式: 12-12|08:00 (北京时间)
});
```

## 🧪 测试验证

### 测试1: API时间转换

```bash
curl "http://localhost:5000/api/support-resistance/snapshots?date=2025-12-12&start_hour=0&end_hour=12"
```

**结果**:
- 返回80条快照数据
- `snapshot_time`: `2025-12-12 08:00:00` (北京时间) ✅
- `snapshot_time_utc`: `2025-12-12 00:00:00` (UTC时间)

### 测试2: 12小时分页

**第1页** (00:00-12:00 北京时间):
- 查询参数: `start_hour=0&end_hour=12`
- 对应UTC: 2025-12-11 16:00 - 2025-12-12 04:00
- 返回数据时间范围: 08:00 - 12:00 (北京时间) ✅

**第2页** (12:00-24:00 北京时间):
- 查询参数: `start_hour=12&end_hour=24`
- 对应UTC: 2025-12-12 04:00 - 2025-12-12 16:00
- 返回数据时间范围: 12:00 - 24:00 (北京时间) ✅

## 📊 时间对照表

| 北京时间 (CST UTC+8) | UTC时间 | 数据库存储 | API返回 | 前端显示 |
|---------------------|---------|-----------|---------|---------|
| 2025-12-12 08:00    | 2025-12-12 00:00 | 00:00 | **08:00** | **08:00** ✅ |
| 2025-12-12 12:00    | 2025-12-12 04:00 | 04:00 | **12:00** | **12:00** ✅ |
| 2025-12-12 20:00    | 2025-12-12 12:00 | 12:00 | **20:00** | **20:00** ✅ |
| 2025-12-13 00:00    | 2025-12-12 16:00 | 16:00 | **00:00** | **00:00** ✅ |

## 🎯 修复效果

### ✅ 修复前问题
- X轴显示: `00:00, 01:00, 02:00...` (UTC时间)
- 用户困惑: "为什么是0点的数据？现在是北京时间8点啊！"

### ✅ 修复后效果
- X轴显示: `08:00, 09:00, 10:00...` (北京时间)
- 符合预期: 显示北京时间，与用户当地时间一致
- 12小时分页: 00:00-12:00 和 12:00-24:00 (北京时间)

## 📝 注意事项

1. **数据库时间**: 保持UTC时间存储（标准做法）
2. **API转换**: 在API层进行时区转换
3. **前端显示**: 直接使用转换后的北京时间
4. **双时间字段**: API返回包含 `snapshot_time` (北京时间) 和 `snapshot_time_utc` (UTC时间)

## 🔗 相关文件

- **API**: `app_new.py` (第5836-5948行)
- **前端**: `templates/support_resistance.html` (第1059-1099行)
- **数据库**: `crypto_data.db` → `support_resistance_snapshots` 表

## 📌 部署状态

- ✅ 代码已提交: commit `b631c0d`
- ✅ 服务已重启: `pm2 restart flask-app`
- ✅ 功能已验证: API时间转换正常
- ✅ 已推送GitHub: `genspark_ai_developer` 分支

---

**修复时间**: 2025-12-13 01:30 (北京时间)  
**问题来源**: 用户截图反馈  
**修复人员**: GenSpark AI Assistant
