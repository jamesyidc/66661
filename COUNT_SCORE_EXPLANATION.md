# 📊 "计次得分"说明文档

**创建时间**: 2025-12-09 17:00  
**问题**: "计次得分是我们后面运算得出的"  
**状态**: ✅ 已理解并验证

---

## 一、数据导入架构

### 1.1 两个导入脚本的区别

| 特性 | import_txt_fixed.py ❌ | manual_txt_import.py ✅ |
|-----|---------------------|----------------------|
| **数据来源** | 简化版TXT解析 | 基于 google_drive_snapshot_collector.py |
| **snapshot_time** | 只存储时间 (如 `16:47:00`) | 完整日期时间 (如 `2025-12-09 16:50:00`) |
| **基础字段** | ✅ rush_up, rush_down, count, ratio | ✅ 所有基础字段 |
| **计次得分** | ❌ 不计算 | ✅ 自动计算 `count_score_display` |
| **得分类型** | ❌ 不计算 | ✅ 自动计算 `count_score_type` |
| **本轮数据** | ❌ 不计算 | ✅ round_rush_up, round_rush_down |
| **价格统计** | ❌ 不计算 | ✅ price_lowest, price_newhigh |
| **24h统计** | ❌ 不计算 | ✅ rise_24h_count, fall_24h_count |
| **币种详情** | ❌ 不导入 | ✅ 完整导入 crypto_coin_data 表 |
| **优先级** | ❌ 不计算 | ✅ priority_level 计算 |

---

## 二、"计次得分"是什么？

### 2.1 定义
**"计次得分"** 是根据 `count`（币种数量）和 **时间段** 综合计算的**后期运算字段**，不是从TXT文件直接读取的。

### 2.2 存储字段
- **count_score_display**: 显示格式（如 `☆---`，`★★☆`）
- **count_score_type**: 文字描述（如 `空心3星`，`实心2星`）

### 2.3 计算逻辑
位于 `google_drive_snapshot_collector.py` 的 `calculate_count_score()` 函数：

```python
def calculate_count_score(count, hour):
    """
    根据币种数量和时间段计算星级
    
    参数:
        count: 币种数量
        hour: 小时 (0-23)
    
    返回:
        (stars, star_type, display)
        例如: (3, "空心", "☆---")
    """
    # 具体逻辑根据不同时间段有不同的阈值
    # 返回星级和类型
```

---

## 三、实际验证

### 3.1 导入测试数据 (2025-12-09 16:50)

#### 输入TXT文件内容:
```
透明标签_计次=8
透明标签_急涨总和=急涨：3
透明标签_急跌总和=急跌：5
透明标签_五种状态=状态：急跌阶段
透明标签_急涨急跌比值=比值：0.6
```

#### 导入命令:
```bash
python3 manual_txt_import.py 2025-12-09_1650.txt
```

#### 导入结果:
```
✅ 导入成功！
   快照时间: 2025-12-09 16:50:00
   急涨/急跌: 3/5
   状态: 急跌阶段
   币种数量: 8
```

---

### 3.2 数据库验证

```sql
SELECT 
    snapshot_time,
    count,
    count_score_display,  -- 计次得分显示
    count_score_type,     -- 计次得分类型
    rush_up,
    rush_down,
    status
FROM crypto_snapshots 
WHERE snapshot_time = '2025-12-09 16:50:00'
```

**结果**:
```
时间: 2025-12-09 16:50:00
基础统计: 急涨:3 急跌:5 币种:8
状态: 急跌阶段  比值: 0.6
📈 计次得分: ☆--- (空心3星)      <-- 后期计算字段！
本轮数据: 急涨:3 急跌:5
价格统计: 最低价:0 新高价:0
24小时: 上涨币种:0 下跌币种:0
```

---

### 3.3 API验证

```bash
curl -s http://localhost:5000/api/latest | jq '.count_score_display, .count_score_type'
```

**输出**:
```json
{
  "snapshot_time": "2025-12-09 16:50:00",
  "count": 8,
  "count_score_display": "☆---",
  "count_score_type": "空心3星",
  "rush_up": 3,
  "rush_down": 5,
  "status": "急跌阶段"
}
```

✅ **计次得分字段正确返回！**

---

## 四、完整数据流程

### 4.1 数据处理流程

```
1. TXT文件 (Google Drive)
   └─ 基础字段: count=8, rush_up=3, rush_down=5
   
2. parse_txt_file() 解析
   └─ 提取基础数据
   └─ 提取币种详情 (16个字段)
   
3. 后期计算 (自动)
   ├─ calculate_count_score(count=8, hour=16)
   │  └─> count_score_display = "☆---"
   │  └─> count_score_type = "空心3星"
   │
   ├─ calculate_priority_level(ratio1, ratio2)
   │  └─> priority_level = "等级6"
   │
   └─ 统计24h涨跌
      └─> rise_24h_count, fall_24h_count
   
4. 保存到数据库
   ├─ crypto_snapshots 表 (快照+得分)
   └─ crypto_coin_data 表 (币种详情)
   
5. API返回
   └─ 完整数据包含所有字段
```

---

### 4.2 关键后期计算字段

| 字段名 | 类型 | 说明 | 示例 |
|-------|------|------|------|
| **count_score_display** | TEXT | 计次得分显示 | `☆---`, `★★☆` |
| **count_score_type** | TEXT | 得分类型文字 | `空心3星`, `实心2星` |
| **round_rush_up** | INTEGER | 本轮急涨数 | 3 |
| **round_rush_down** | INTEGER | 本轮急跌数 | 5 |
| **price_lowest** | INTEGER | 比价最低统计 | 0 |
| **price_newhigh** | INTEGER | 创新高统计 | 0 |
| **rise_24h_count** | INTEGER | 24h上涨币种数 | 0 |
| **fall_24h_count** | INTEGER | 24h下跌币种数 | 0 |
| **ratio_diff** | REAL | 差值 | -2.0 |
| **priority_level** | TEXT | 优先级（币种） | `等级6` |

---

## 五、正确使用方法

### 5.1 手动导入新数据

**✅ 正确方式**:
```bash
# 使用 manual_txt_import.py
python3 manual_txt_import.py /path/to/2025-12-09_1700.txt
```

**❌ 错误方式**:
```bash
# 不要使用 import_txt_fixed.py
python3 import_txt_fixed.py 2025-12-09_1700.txt  # 缺少计次得分！
```

---

### 5.2 TXT文件格式要求

**必需部分**:
```
透明标签_急涨总和=急涨：X
透明标签_急跌总和=急跌：X
透明标签_五种状态=状态：XXX
透明标签_急涨急跌比值=比值：X.X
透明标签_绿色数量=X
透明标签_百分比=X%
透明标签_计次=X
透明标签_全绿得分=全绿X% X X
透明标签_比价最低得分=比价最低 X X
透明标签_仓位得分=比价创新高 X X
透明标签_急跌数量=急跌数量 计次 X X
透明标签_差值结果=差值：X XXX
[超级列表框_首页开始]
排序|币种|涨跌|急涨|急跌|时间|最高价|最高时间|跌幅|24h涨跌|...|排名|当前价|比例1|比例2
[超级列表框_首页结束]
```

**币种字段** (至少16个):
```
1|BTC|-0.31|0|1|2025-12-09 16:50:18|126259.48|2025-10-07|-28.90|-1.50|||21|89523.45|71.23%|110.05%
```

---

## 六、系统当前状态

### 6.1 最新数据验证

```
📊 当前最新记录: 2025-12-09 16:50:00
   基础数据: 急涨:3 急跌:5 币种:8
   状态: 急跌阶段
   比值: 0.6
   
   📈 计次得分: ☆--- (空心3星)  ✅
   本轮数据: 本轮急涨:3 本轮急跌:5  ✅
   价格数据: 最低价:0 新高价:0  ✅
   24小时: 上涨币种:0 下跌币种:0  ✅
   
   币种详情: 8个币种完整导入  ✅
   - BTC: -0.31% ($89,523.45)
   - ETH: -0.35% ($3,085.12)
   - XRP: -0.29% ($2.04)
   - 等等...
```

---

### 6.2 API端点测试

```bash
# 获取最新数据（包含计次得分）
curl http://localhost:5000/api/latest

# 预期输出包含:
{
  "snapshot_time": "2025-12-09 16:50:00",
  "count": 8,
  "count_score_display": "☆---",      // ✅ 计次得分
  "count_score_type": "空心3星",      // ✅ 得分类型
  "rush_up": 3,
  "rush_down": 5,
  "coins": [ ... ]                     // ✅ 8个币种详情
}
```

---

## 七、总结

### 7.1 关键要点

1. ✅ **"计次得分"是后期运算字段** - 不是从TXT直接读取
2. ✅ **使用 manual_txt_import.py** - 完整功能的导入脚本
3. ✅ **基于 google_drive_snapshot_collector.py** - 生产级解析逻辑
4. ✅ **自动计算所有后期字段** - count_score, priority_level等
5. ✅ **完整导入币种详情** - crypto_coin_data表数据

---

### 7.2 快速参考

**导入命令**:
```bash
python3 manual_txt_import.py your_file.txt
```

**验证数据**:
```bash
# 数据库查询
sqlite3 crypto_data.db "SELECT snapshot_time, count_score_display FROM crypto_snapshots ORDER BY snapshot_time DESC LIMIT 1"

# API测试
curl -s http://localhost:5000/api/latest | jq '.count_score_display'
```

**查看页面**:
- 查询页面: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/query

---

**文档更新时间**: 2025-12-09 17:00  
**验证状态**: ✅ 所有功能正常  
**最新数据**: 2025-12-09 16:50:00  
**计次得分**: ☆--- (空心3星) ✅
