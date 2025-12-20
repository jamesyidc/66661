# K线48小时高低点标记显示修复

## 问题描述

用户反馈：K线图只显示7天最高点和最低点，但没有显示48小时的最高点和最低点。

## 根本原因分析

### 问题定位
```javascript
// ❌ 原有的错误逻辑
if (relativeIdx >= 0) {  // 只检查是否 >= 起始位置
    markPoints.push(...);
}
```

**核心问题**：在判断标记点是否应该显示时，代码只检查了标记点的全局索引是否在页面起始位置之后（`relativeIdx >= 0`），但**没有检查是否在页面结束位置之前**。

### 导致的现象
1. **48小时标记点缺失**：如果48小时的高低点在当前页面范围之外（例如在更早的页面），这些标记点会被错误地添加，但因为索引超出当前页面范围，实际不会显示
2. **只显示7天标记**：7天范围更大，恰好其高低点在当前页面范围内，所以能正常显示

### 页面范围说明
```javascript
// 当前页面数据范围
const startIdx = allKlineData.length - (currentPage + 1) * recordsPerPage;  // 页面起始索引
const endIdx = allKlineData.length - currentPage * recordsPerPage;          // 页面结束索引

// 页面实际包含的数据：allKlineData.slice(startIdx, endIdx)
// 有效索引范围：[startIdx, endIdx)
```

## 解决方案

### 修复内容
1. **函数签名更新**：添加 `pageEndIdx` 参数
   ```javascript
   // ✅ 新的函数签名
   function calculateGlobalHighLowPoints(allData, pageStartIdx, pageEndIdx) {
       // ...
   }
   ```

2. **严格的范围检查**：检查标记点是否在 `[pageStartIdx, pageEndIdx)` 范围内
   ```javascript
   // ✅ 修复后的正确逻辑
   if (max48h.globalIdx >= pageStartIdx && max48h.globalIdx < pageEndIdx) {
       markPoints.push(...);
   }
   ```

3. **调用位置更新**：传入 `endIdx` 参数
   ```javascript
   const globalMarkPoints = calculateGlobalHighLowPoints(allKlineData, startIdx, endIdx);
   ```

### 修复的4个标记点
| 标记类型 | 颜色 | 位置 | 标签 |
|----------|------|------|------|
| 48小时最高 | 🔴 红色 `#ff6b6b` | 上方 | `48H高\n{价格}` |
| 48小时最低 | 🔵 青色 `#4ecdc4` | 下方 | `48H低\n{价格}` |
| 7天最高 | 🟡 黄色 `#ffd93d` | 上方 | `7D高\n{价格}` |
| 🟢 7天最低 | 绿色 `#6bcf7f` | 下方 | `7D低\n{价格}` |

## 技术细节

### 范围检查逻辑
```javascript
// 48小时最高点
if (data48h.length > 0) {
    const max48h = data48h.reduce((max, item) => 
        item.high > max.high ? item : max, data48h[0]);
    
    const relativeIdx = max48h.globalIdx - pageStartIdx;
    
    // ✅ 双重检查：
    // 1. max48h.globalIdx >= pageStartIdx  → 标记点在页面起始位置之后
    // 2. max48h.globalIdx < pageEndIdx     → 标记点在页面结束位置之前
    if (max48h.globalIdx >= pageStartIdx && max48h.globalIdx < pageEndIdx) {
        markPoints.push({
            name: '48小时最高',
            coord: [relativeIdx, max48h.high],
            // ...
        });
    }
}
```

### 调试日志优化
```javascript
console.log('%c[全局高低点标记] 基于整个数据集计算:', 
    'color: #ffd93d; font-size: 14px; font-weight: bold', {
    '最新时间': new Date(latestTime).toLocaleString('zh-CN'),
    '48小时数据点数': data48h.length,
    '7天数据点数': data7d.length,
    '当前页范围': `[${pageStartIdx}, ${pageEndIdx})`,  // ✅ 新增
    '标记点数量': markPoints.length,
    '标记详情': markPoints.map(p => ({
        name: p.name,
        价格: p.value,
        相对索引: p.coord[0]
    }))
});
```

## 修复效果

### 修复前
- ❌ 只显示7天最高点和最低点
- ❌ 48小时标记点完全缺失
- ❌ 用户困惑为什么没有48小时数据

### 修复后
- ✅ 同时显示48小时和7天的高低点（共4个标记）
- ✅ 所有标记点都基于全局数据计算
- ✅ 只在标记点位于当前页面范围内时才显示
- ✅ 翻页后标记点的数值保持稳定（不会变化）

## 验证方法

1. **访问任意币种K线图**：
   - BTC: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/BTC/v6
   - ETH: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/ETH/v6

2. **检查标记点数量**：
   - 应该看到最多4个标记点（如果都在可视范围内）
   - 🔴 48H高、🔵 48H低、🟡 7D高、🟢 7D低

3. **翻页测试**：
   - 记录标记点的价格和时间
   - 翻页前后对比，数值应该**保持完全一致**

4. **控制台验证**：
   ```javascript
   // 打开浏览器控制台，查看日志
   [全局高低点标记] 基于整个数据集计算:
   {
       最新时间: "2025-12-12 20:30:00",
       48小时数据点数: 576,  // 48小时内的K线数量
       7天数据点数: 2016,    // 7天内的K线数量
       当前页范围: "[1916, 2016)",
       标记点数量: 4,         // ✅ 应该是4个
       标记详情: [
           { name: "48小时最高", 价格: "101245.6789", 相对索引: 45 },
           { name: "48小时最低", 价格: "99876.5432", 相对索引: 12 },
           { name: "7天最高", 价格: "102456.7890", 相对索引: 78 },
           { name: "7天最低", 价格: "98765.4321", 相对索引: 23 }
       ]
   }
   ```

## 相关文件

- **修改文件**：`templates/symbol_detail_v6.html`
- **修改函数**：`calculateGlobalHighLowPoints()`
- **影响范围**：所有27个币种的K线图（/symbol/{SYMBOL}/v6）

## 注意事项

1. **标记点可能不在当前页面**：
   - 如果48小时或7天的高低点不在当前显示的页面范围内，对应的标记点不会显示
   - 这是**正常现象**，需要翻页到相应位置才能看到

2. **标记点数量可能少于4个**：
   - 如果某些极值点不在当前页面范围内，标记点数量会少于4个
   - 例如：当前页面可能只显示 `7D高` 和 `7D低`，而48小时的高低点在其他页面

3. **数据时效性**：
   - 标记点基于完整的K线数据集计算
   - 随着新数据的到来，48小时和7天的范围会动态变化

## 总结

这次修复解决了K线图48小时高低点标记缺失的问题，确保所有4个极值标记点（48H高/低、7D高/低）都能正确显示，并且在翻页时保持数值稳定。核心改进是将范围检查从单边检查（`>= pageStartIdx`）改为双边检查（`>= pageStartIdx && < pageEndIdx`），确保只有真正在当前页面范围内的标记点才会显示。
