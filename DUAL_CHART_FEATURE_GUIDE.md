# 恐慌清洗指数双曲线图表功能说明

**更新时间**: 2025-12-06  
**功能**: 恐慌清洗指数趋势图 + 全网持仓量双曲线展示

---

## 📊 功能概述

在恐慌清洗指数页面的趋势图中，同时展示**恐慌清洗指数**和**全网持仓量**两条曲线，帮助用户全面分析市场状态。

### 双曲线设计

```
┌─────────────────────────────────────────────────┐
│  恐慌清洗指数趋势 (3分钟更新)                        │
│  ━━━ 恐慌清洗指数  ━━━ 全网持仓量                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  12%┤     ╱╲                          ┊     │95亿$
│  10%┤    ╱  ╲                         ┊     │93亿$
│   8%┤   ╱    ╲___                     ┊     │91亿$
│   6%┤  ╱         ╲                    ┊╱╲   │89亿$
│   4%┤_╱           ╲                  ╱╯  ╲  │87亿$
│   2%┤              ╲_______________╱      ╲_│85亿$
│     └────────────────────────────────────────┤
│      21:00  21:30  22:00  22:30  23:00       │
│      左侧Y轴: 恐慌指数(%)  右侧Y轴: 持仓量(亿$)  │
└─────────────────────────────────────────────────┘
```

---

## 🎨 图表特性

### 1. 双Y轴设计

| Y轴位置 | 指标名称 | 颜色 | 单位 | 说明 |
|---------|----------|------|------|------|
| **左侧** | 恐慌清洗指数 | 🔵 蓝色 | % | 市场恐慌程度 |
| **右侧** | 全网持仓量 | 🟢 绿色 | 亿美元 | 加密货币总持仓 |

### 2. 曲线样式

**恐慌清洗指数 (蓝色)**
- 类型: 平滑曲线
- 填充: 蓝色渐变 (rgba(59, 125, 255, 0.3) → 0.05)
- 线宽: 2px
- 符号: 圆点 (6px)

**全网持仓量 (绿色)**
- 类型: 平滑曲线
- 填充: 无
- 线宽: 2px
- 符号: 圆点 (6px)
- 颜色: #10b981

### 3. 交互功能

#### Tooltip (悬浮提示)
鼠标悬停在图表上时，自动显示:
```
22:00
● 恐慌清洗指数: 11.64%
● 全网持仓量: $93.01亿
```

#### Legend (图例切换)
- 点击"恐慌清洗指数"图例 → 隐藏/显示恐慌曲线
- 点击"全网持仓量"图例 → 隐藏/显示持仓曲线
- 支持单独观察任一指标

---

## 🔄 数据更新

### 自动采集
```
⏰ 采集频率: 每3分钟
📡 数据来源: btc123.fans API
💾 存储位置: crypto_data.db (panic_wash_index表)
```

### 数据字段
```sql
SELECT 
    record_time,        -- 记录时间
    panic_index,        -- 恐慌指数 (%)
    total_position,     -- 全网持仓 (亿美元)
    hour_1_amount,      -- 1小时爆仓 (亿美元)
    hour_24_amount,     -- 24小时爆仓 (亿美元)
    hour_24_people      -- 24小时爆仓人数 (万人)
FROM panic_wash_index
ORDER BY record_time DESC
LIMIT 50;
```

### 图表数据流

```
┌─────────────┐
│ 数据采集器   │ liquidation_amount_collector.py
│ 每3分钟      │ panic_wash_collector.py
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 数据库存储   │ crypto_data.db
│ panic_wash_  │ (panic_index, total_position)
│ index 表     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Flask API   │ /api/panic/history?limit=50
│ 查询接口     │ 返回最近50条记录
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 前端渲染     │ ECharts 双曲线图表
│ JavaScript   │ loadHistoryData()
└─────────────┘
```

---

## 💻 技术实现

### 前端代码 (panic_new.html)

#### 1. ECharts 配置
```javascript
const option = {
    legend: {
        data: ['恐慌清洗指数', '全网持仓量']
    },
    yAxis: [
        {
            type: 'value',
            name: '恐慌指数 (%)',
            position: 'left',
            axisLabel: {
                color: '#3b7dff',
                formatter: '{value}%'
            }
        },
        {
            type: 'value',
            name: '全网持仓 (亿$)',
            position: 'right',
            axisLabel: {
                color: '#10b981',
                formatter: '${value}亿'
            }
        }
    ],
    series: [
        {
            name: '恐慌清洗指数',
            yAxisIndex: 0,
            type: 'line',
            data: panicValues  // [11.64, 11.58, ...]
        },
        {
            name: '全网持仓量',
            yAxisIndex: 1,
            type: 'line',
            data: positionValues  // [93.01, 92.85, ...]
        }
    ]
};
```

#### 2. 数据加载
```javascript
async function loadHistoryData() {
    const conn = await fetch('/api/panic/history?limit=50');
    const result = await conn.json();
    
    const data = result.data.reverse(); // 时间正序
    
    // 提取数据
    const times = data.map(item => 
        item.record_time.split(' ')[1].substring(0, 5)
    );
    const panicValues = data.map(item => 
        item.panic_index.toFixed(2)
    );
    const positionValues = data.map(item => 
        item.total_position.toFixed(2)
    );
    
    // 更新图表
    chart.setOption({
        xAxis: { data: times },
        series: [
            { name: '恐慌清洗指数', data: panicValues },
            { name: '全网持仓量', data: positionValues }
        ]
    });
}
```

### 后端API (app_new.py)

#### /api/panic/history 接口
```python
@app.route('/api/panic/history')
def panic_history():
    limit = request.args.get('limit', 50, type=int)
    
    cursor.execute("""
        SELECT 
            record_time,
            panic_index,
            hour_24_people / 10000 as hour_24_people,
            total_position / 100000000 as total_position
        FROM panic_wash_index
        ORDER BY record_time DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    
    return jsonify({
        'success': True,
        'data': [{
            'record_time': row[0],
            'panic_index': row[1],
            'hour_24_people': row[2],
            'total_position': row[3]
        } for row in rows]
    })
```

---

## 📈 用户使用指南

### 1. 访问页面
打开恐慌清洗指数页面:
```
https://5000-xxx.sandbox.novita.ai/panic
```

### 2. 查看双曲线图表
找到页面中部的"恐慌清洗指数趋势"图表区域

### 3. 交互操作

#### 悬停查看数据
- 鼠标悬停在图表任意位置
- 自动显示该时刻的两个指标值

#### 切换曲线显示
- 点击图例"恐慌清洗指数" → 隐藏/显示蓝色曲线
- 点击图例"全网持仓量" → 隐藏/显示绿色曲线

#### 缩放查看
- 鼠标滚轮: 放大/缩小图表
- 拖拽: 移动查看不同时间段

### 4. 数据分析

#### 关联分析
- 恐慌指数 ↑ + 持仓量 ↓ → 市场恐慌，资金撤离
- 恐慌指数 ↓ + 持仓量 ↑ → 市场信心恢复，资金进入
- 恐慌指数 ↑ + 持仓量 ↑ → 高风险高杠杆，警惕爆仓

#### 趋势判断
- 蓝线陡升 → 恐慌加剧，避险为主
- 绿线上升 → 资金流入，可能反弹
- 双线齐降 → 市场冷静，观望情绪

---

## 🎯 功能优势

### 1. 数据全面性
- ✅ 同时展示情绪指标（恐慌）和资金指标（持仓）
- ✅ 避免单一指标的局限性
- ✅ 更准确判断市场状态

### 2. 可视化直观
- ✅ 双Y轴设计，单位清晰
- ✅ 颜色区分，一目了然
- ✅ 平滑曲线，趋势明显

### 3. 实时更新
- ✅ 每3分钟自动采集
- ✅ 数据来源可靠（btc123.fans）
- ✅ 历史记录完整（最近50条）

### 4. 交互友好
- ✅ 悬停即显详情
- ✅ 图例切换灵活
- ✅ 响应速度快

---

## 🔧 维护指南

### 检查采集器状态
```bash
# 查看爆仓金额采集器
./liquidation_amount_control.sh status

# 查看日志
tail -f liquidation_amount_collector.log
```

### 手动触发采集
```bash
# 测试采集一次
./liquidation_amount_control.sh test
```

### 数据验证
```bash
# 查询最新数据
sqlite3 crypto_data.db "
SELECT 
    record_time,
    panic_index,
    total_position
FROM panic_wash_index
ORDER BY record_time DESC
LIMIT 5;
"
```

### 测试API
```bash
# 测试历史数据接口
curl 'http://localhost:5000/api/panic/history?limit=5' | python3 -m json.tool
```

---

## 🐛 故障排查

### 问题1: 图表不显示第二条曲线

**原因**: API未返回 total_position 字段

**解决**:
```bash
# 检查API返回
curl 'http://localhost:5000/api/panic/history?limit=1'

# 应该包含 "total_position" 字段
```

### 问题2: 数据不更新

**原因**: 采集器未运行

**解决**:
```bash
# 重启采集器
./liquidation_amount_control.sh restart
```

### 问题3: 曲线显示异常

**原因**: 数据库数据异常

**解决**:
```bash
# 检查数据库最新记录
python3 << EOF
import sqlite3
db = sqlite3.connect('crypto_data.db')
cursor = db.cursor()
cursor.execute("SELECT * FROM panic_wash_index ORDER BY record_time DESC LIMIT 1")
print(cursor.fetchone())
EOF
```

---

## 📚 相关文档

- `LIQUIDATION_FIX_FINAL_REPORT.md` - 1小时爆仓金额修复报告
- `LIQUIDATION_COLLECTOR_GUIDE.md` - 爆仓金额采集器使用指南
- `SIGNAL_VALIDATION_GUIDE.md` - 信号数据验证机制说明

---

## ✅ 功能清单

- [x] 双Y轴配置 (恐慌指数 + 全网持仓)
- [x] 双曲线展示 (蓝色 + 绿色)
- [x] Tooltip 自动格式化单位
- [x] Legend 图例切换功能
- [x] 数据自动采集 (每3分钟)
- [x] API 接口支持
- [x] 响应式设计
- [x] 文档完整

---

**创建时间**: 2025-12-06 22:05  
**Git 提交**: `6a3d993`  
**分支**: `genspark_ai_developer`

🎊 **功能状态: 100% 完成** 🎊
