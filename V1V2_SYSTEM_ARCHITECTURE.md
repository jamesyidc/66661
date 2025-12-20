# V1V2 监控系统架构说明

## ✅ 数据存储方式：**完全基于数据库**

### 📊 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     V1V2 监控系统架构                              │
└─────────────────────────────────────────────────────────────────┘

1. 数据采集层 (v1v2_collector.py)
   ├─ 每 30 秒运行一次
   ├─ 从 OKEx API 获取 27 个币种的 5 分钟 K 线成交额
   ├─ 计算 V1/V2 级别
   └─ 写入 SQLite 数据库 (v1v2_data.db)
          ↓
          ↓ (INSERT)
          ↓
2. 数据存储层 (v1v2_data.db)
   ├─ 每个币种一个独立表 (volume_btc, volume_eth, ...)
   ├─ 字段: timestamp, collect_time, volume, v1_threshold, v2_threshold, level
   ├─ 索引: idx_volume_{coin}_timestamp (加速查询)
   └─ 实时数据: ✅ 数据新鲜度 < 30 秒
          ↓
          ↓ (SELECT)
          ↓
3. API 服务层 (app_new.py)
   ├─ /api/v1v2/latest - 获取所有币种最新数据
   ├─ /api/v1v2/statistics - 获取历史统计数据
   └─ 直接从数据库读取 (无缓存)
          ↓
          ↓ (fetch())
          ↓
4. 前端展示层 (v1v2_monitor.html)
   ├─ 每 30 秒自动刷新
   ├─ 从 API 获取数据 (fetch)
   ├─ 仅做视觉渲染计算 (进度条百分比)
   └─ 无本地缓存或计算逻辑
```

---

## 🔍 数据流详解

### 1. **数据采集** (每 30 秒)

```python
# v1v2_collector.py
def fetch_volume_from_okex(symbol):
    # 从 OKEx 获取最新 5 分钟 K 线
    url = 'https://www.okx.com/api/v5/market/candles'
    # 获取 volCcyQuote (USDT 成交额)
    return volume_usdt, timestamp

def save_to_database(symbol, volume, timestamp, v1, v2, level):
    # 保存到对应币种的表
    INSERT INTO volume_btc (timestamp, collect_time, volume, v1_threshold, v2_threshold, level)
```

**数据示例**：
```
时间: 2025-12-15 16:50:00
成交额: $3,830,804.64
级别: V1
V1阈值: $200,000
V2阈值: $100,000
```

---

### 2. **数据存储** (SQLite 数据库)

**数据库结构**：
```sql
-- 每个币种一个表
CREATE TABLE volume_btc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,           -- OKEx 时间戳
    collect_time TEXT NOT NULL,           -- 采集时间 (格式化)
    volume REAL NOT NULL,                 -- USDT 成交额
    v1_threshold REAL NOT NULL,           -- V1 阈值
    v2_threshold REAL NOT NULL,           -- V2 阈值
    level TEXT NOT NULL,                  -- V1 / V2 / NONE
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_volume_btc_timestamp ON volume_btc(timestamp DESC);
```

**当前数据量**：
- BTC: 4151 条记录
- ETH: 4150 条记录
- XRP: 4149 条记录
- SOL: 4152 条记录
- DOGE: 4153 条记录
- ... (共 27 个币种)

---

### 3. **API 读取** (从数据库)

```python
# app_new.py
@app.route('/api/v1v2/latest')
def api_v1v2_latest():
    conn = sqlite3.connect('v1v2_data.db')
    
    for symbol in coins_config.keys():
        # 从数据库读取最新一条记录
        SELECT volume, collect_time, level, timestamp
        FROM volume_{symbol.lower()}
        ORDER BY id DESC
        LIMIT 1
    
    return {
        'success': True,
        'data': result,
        'count': 27,
        'update_time': '2025-12-15 16:50:00'
    }
```

**API 响应示例**：
```json
{
  "success": true,
  "count": 27,
  "update_time": "2025-12-15 16:50:00",
  "data": [
    {
      "symbol": "ETH",
      "volume": 12694218.91,
      "collect_time": "2025-12-15 16:50:00",
      "level": "V1",
      "v1": 1300000,
      "v2": 500000
    },
    ...
  ]
}
```

---

### 4. **前端展示** (仅做渲染)

```javascript
// v1v2_monitor.html
async function loadData() {
    // 从 API 获取数据
    const response = await fetch('/api/v1v2/latest');
    const data = await response.json();
    
    // 渲染到页面
    renderData(data.data);
}

function calculateProgress(volume, v1, v2) {
    // 仅计算进度条百分比 (不是数据计算)
    if (volume >= v1) return 100;
    if (volume >= v2) return 50 + (volume - v2) / (v1 - v2) * 50;
    return (volume / v2) * 50;
}
```

**前端职责**：
- ✅ 从 API 获取数据 (fetch)
- ✅ 渲染卡片和统计表
- ✅ 计算进度条百分比 (视觉效果)
- ❌ **不做数据计算或缓存**
- ❌ **不从 OKEx 直接获取数据**

---

## 📌 关键特性

### ✅ **完全数据库驱动**
- 所有交易数据存储在 SQLite 数据库
- API 直接从数据库读取
- 前端零数据计算逻辑

### ⚡ **实时性保证**
- 采集器每 30 秒更新
- 数据新鲜度 < 30 秒
- 前端每 30 秒自动刷新

### 🔒 **数据一致性**
- 单一数据源 (数据库)
- 无浏览器缓存干扰
- 所有客户端看到相同数据

### 📊 **历史数据**
- 数据库保存所有历史记录
- 可查询任意时间段统计
- 支持 1h/3h/6h/12h/24h 统计

---

## 🚀 验证结果

```bash
✅ 数据库中有实时数据 (最新: 2025-12-15 16:50:00)
✅ 数据非常新鲜 (< 30 秒前)
✅ 27 个币种全部正常采集
✅ 每个币种 4000+ 条历史记录
✅ API 工作正常
✅ 前端正常展示
```

---

## 🎯 结论

**V1V2 监控系统是 100% 基于数据库的实时监控系统**

| 组件 | 数据来源 | 计算位置 | 存储位置 |
|------|---------|---------|---------|
| 采集器 | OKEx API | 采集器 | 数据库 |
| API | 数据库 | 无 | 数据库 |
| 前端 | API | 仅进度条 | 无 (不缓存) |

**无任何本地浏览器缓存或计算逻辑！**

---

## 📖 相关文件

- `v1v2_collector.py` - 数据采集器
- `v1v2_data.db` - SQLite 数据库
- `app_new.py` - Flask API (行 4373-4500)
- `templates/v1v2_monitor.html` - 前端页面
- `v1v2_collector.log` - 采集器日志

---

**更新时间**: 2025-12-15 16:52:00
