# 🔥 低波动K线连续序列标注功能

## 功能说明

在5分钟K线图上**自动检测并标注**符合以下条件的连续K线：

### 检测条件
- ✅ **涨跌幅** ≤ 0.25%  （计算方式：|(收盘价 - 开盘价) / 开盘价| × 100%）
- ✅ **震荡幅度** ≤ 0.50%  （计算方式：|(最高价 - 最低价) / 开盘价| × 100%）
- ✅ **连续数量** ≥ 2根

## 视觉效果

### 1. **橙色半透明区域**
- 覆盖整个连续低波动K线序列
- 颜色：`rgba(255, 165, 0, 0.15)` (橙色，15%透明度)
- 从起始K线到结束K线的完整区域

### 2. **顶部标签**
- 显示内容：`🔥 N根` (N为连续K线数量)
- 颜色：橙色 `#ffa500`
- 背景：半透明黑色
- 字体：12px，加粗

### 3. **控制台日志**
```javascript
[低波动K线检测] 符合条件的连续序列: [
  { start: 5, end: 7, count: 3 },
  { start: 12, end: 14, count: 3 },
  ...
]
```

## 实际检测结果（FIL，2025-12-11 14:08）

**检测到 18 个连续低波动K线序列！**

这表示在当前144根5分钟K线中，有18个不同的时间段出现了连续的低波动行情。

## 使用场景

### 🎯 交易策略参考
1. **盘整识别**：低波动连续序列通常表示价格在窄幅区间震荡
2. **突破前兆**：长时间低波动后可能出现大幅突破
3. **风险评估**：低波动期间适合观望，等待明确方向

### 📊 技术分析
- **2-3根连续**：短期盘整
- **4-6根连续**：中期盘整
- **7根以上**：长期盘整，突破概率增加

## 技术实现

### 算法逻辑
```javascript
for (let i = 0; i < ohlc.length; i++) {
    const [open, close, low, high] = ohlc[i];
    const changePct = Math.abs((close - open) / open * 100);
    const volatilityPct = Math.abs((high - low) / open * 100);
    
    if (changePct <= 0.25 && volatilityPct <= 0.50) {
        // 符合条件，计数+1
        consecutiveCount++;
    } else {
        // 不符合，记录之前的序列（如果≥2根）
        if (consecutiveCount >= 2) {
            lowVolatilityMarkers.push({...});
        }
        consecutiveCount = 0;
    }
}
```

### ECharts渲染
```javascript
markArea: {
    data: lowVolatilityMarkers.map(marker => [
        {
            name: `连续${marker.count}根低波动K线`,
            xAxis: marker.start,
            itemStyle: { color: 'rgba(255, 165, 0, 0.15)' },
            label: { 
                formatter: `🔥 ${marker.count}根`,
                color: '#ffa500'
            }
        },
        { xAxis: marker.end }
    ])
}
```

## 如何查看

1. **访问任意K线页面**：`/symbol/FIL` 或 `/symbol/FIL/v6`
2. **自动标注**：橙色区域会自动显示在图表上
3. **查看详情**：
   - 鼠标hover到标注区域可以看到说明
   - 打开F12控制台查看检测日志

## 参数调整（开发者）

如需调整检测阈值，修改 `symbol_detail_v6.html` 中的条件：

```javascript
// 当前阈值
if (changePct <= 0.25 && volatilityPct <= 0.50) { ... }

// 例如更严格的条件
if (changePct <= 0.15 && volatilityPct <= 0.30) { ... }

// 例如更宽松的条件
if (changePct <= 0.50 && volatilityPct <= 1.00) { ... }
```

---

**Git Commit:** `e3da3e9` - feat: 添加低波动K线连续序列标注功能  
**PR链接:** https://github.com/jamesyidc/66661/pull/1  
**部署时间:** 2025-12-11 14:08:28 UTC
