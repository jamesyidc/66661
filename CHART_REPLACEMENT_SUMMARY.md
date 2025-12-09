# 📊 /live 页面曲线图替换总结

## 🎯 需求描述

将 `/live` 页面中的曲线图替换为 `/history` 页面中的曲线样式，数据源从数据库历史数据读取，而非实时累加。

---

## ✅ 实现方案

### 1️⃣ **数据源切换**

**修改前**：
```javascript
function updateChart(data) {
    // 从实时数据提取值
    const rushUp = parseInt(stats.rushUp) || 0;
    const rushDown = parseInt(stats.rushDown) || 0;
    
    // 累加新数据点到 historyData
    historyData.push({
        time: updateTime.split(' ')[1].substring(0, 5),
        rushUp: rushUp,
        rushDown: rushDown,
        diff: diff,
        count: countValue
    });
    
    // 保持最多50个数据点
    if (historyData.length > MAX_HISTORY_POINTS) {
        historyData.shift();
    }
}
```

**修改后**：
```javascript
async function updateChart(data) {
    // ✅ 每次刷新时重新加载完整历史数据
    await loadHistoryData();
}
```

**优势**：
- ✅ 数据来源统一为数据库（`/api/history/query`）
- ✅ 每次刷新显示完整准确的历史数据
- ✅ 不依赖前端累加，避免数据不一致

---

### 2️⃣ **图表样式优化**

#### 图表标题
```javascript
title: {
    display: true,
    text: '急涨/急跌历史趋势图（今日数据）',  // ✅ 明确标注为历史数据
    color: '#4a9eff',
    font: {
        size: 18,      // ✅ 从16增加到18
        weight: 'bold' // ✅ 加粗显示
    }
}
```

#### 图例样式
```javascript
legend: {
    labels: {
        color: '#eee',
        font: { size: 14 },  // ✅ 增加字体大小
        padding: 15          // ✅ 增加间距
    }
}
```

#### Tooltip（悬停提示）
```javascript
tooltip: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',  // ✅ 黑色半透明背景
    titleColor: '#4a9eff',                   // ✅ 蓝色标题
    bodyColor: '#eee',                       // ✅ 白色文字
    borderColor: '#4a9eff',                  // ✅ 蓝色边框
    borderWidth: 1,
    padding: 12,
    displayColors: true,
    callbacks: {
        label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            label += context.parsed.y;
            return label;
        }
    }
}
```

#### X轴样式
```javascript
x: {
    ticks: {
        color: '#888',
        font: { size: 12 },      // ✅ 设置字体大小
        maxRotation: 45,
        minRotation: 45
    },
    grid: {
        color: 'rgba(255, 255, 255, 0.1)',
        drawBorder: false        // ✅ 不绘制边框
    }
}
```

#### Y轴样式
```javascript
y: {
    type: 'linear',
    display: true,
    position: 'left',
    beginAtZero: true,           // ✅ 从0开始
    ticks: {
        color: '#888',
        font: { size: 12 },      // ✅ 字体大小
        stepSize: 1              // ✅ 步长为1
    },
    grid: {
        color: 'rgba(255, 255, 255, 0.1)',
        drawBorder: false        // ✅ 不绘制边框
    },
    title: {
        display: true,
        text: '急涨/急跌/差值',
        color: '#aaa',           // ✅ 灰色标题
        font: { size: 13 }       // ✅ 字体大小
    }
}
```

---

### 3️⃣ **数据加载流程**

```
页面加载
   ↓
initChart()              // 初始化空图表
   ↓
loadHistoryData()        // 从 /api/history/query 加载今日完整历史数据
   ↓
updateChartWithHighlight() // 更新图表并应用高亮样式
   ↓
loadData()               // 加载最新实时数据（更新统计栏）
   ↓
startAutoRefresh()       // 开始自动刷新（每次调用 loadHistoryData()）
```

---

## 📊 图表数据结构

### 4条曲线配置

| 曲线 | 颜色 | 类型 | Y轴 | 描述 |
|-----|------|------|-----|------|
| **急涨** | 红色 (#ff4444) | 实线+填充 | y | 急涨币种数量 |
| **急跌** | 绿色 (#00ff88) | 实线+填充 | y | 急跌币种数量 |
| **差值** | 橙色 (#ffaa00) | 虚线 | y | 急涨-急跌 |
| **计次** | 蓝色 (#00ccff) | 实线+填充 | y1 | 计次统计 |

### 数据点高亮规则

| 条件 | 效果 | 优先级 |
|------|------|--------|
| 差值 > 50 或 < -50 | 黄色星标 + 最大点 (20px) | 最高 |
| 差值 > 20 或 < -20 | 白色高亮 + 大点 (16px) | 高 |
| 急涨 >= 10 或 急跌 >= 10 | 第一次出现高亮 (14px) | 中 |

---

## 🎯 实现效果

### ✅ **修改前** (实时累加)
- 数据源：前端累加实时API返回的数据
- 数据点：从页面打开开始累加，最多50个点
- 问题：刷新页面后数据丢失，数据可能不准确

### ✅ **修改后** (历史数据)
- 数据源：数据库历史数据（`/api/history/query`）
- 数据点：显示今日完整历史数据，最多50个点
- 优势：
  - ✅ 数据准确完整，来自数据库
  - ✅ 刷新页面后数据不丢失
  - ✅ 与 `/history` 页面数据一致
  - ✅ 每次自动刷新都是完整数据，不是累加

---

## 🔄 数据更新机制

### 自动刷新流程

```javascript
startAutoRefresh() {
    setInterval(() => {
        loadData();  // 加载最新实时数据 → 触发 updateChart()
                     //                  → 调用 loadHistoryData()
                     //                  → 重新加载完整历史数据
    }, 180000);      // 每3分钟刷新一次
}
```

### API请求

```http
GET /api/history/query?start_time=2025-12-03%2000:00:00&end_time=2025-12-03%2023:59:59&limit=200

Response:
{
    "success": true,
    "data": [
        {
            "record_time": "2025-12-03 18:51:00",
            "rush_up": 15,
            "rush_down": 9,
            "count_times": 6,
            "difference": 6
        },
        ...
    ]
}
```

---

## 📱 用户体验

### ✅ **页面打开**
1. 显示完整今日历史数据（最近50个数据点）
2. 图表立即可见，不需要等待数据累加
3. 高亮标记自动应用（极端差值、大差值、急涨急跌>10）

### ✅ **自动刷新**（每3分钟）
1. 重新从数据库加载完整历史数据
2. 图表完整刷新，不是增量更新
3. 始终显示最准确的数据

### ✅ **手动刷新**
1. 点击"立即刷新"按钮
2. 重新加载历史数据
3. 图表完整更新

---

## 📁 文件变更

### 修改文件
- `crypto_home_v2.html` - 主要修改

### 关键函数变更

| 函数 | 修改前 | 修改后 |
|------|--------|--------|
| `updateChart()` | 累加新数据点 | 重新加载历史数据 |
| `initChart()` | 基础配置 | 增强样式配置 |
| `loadHistoryData()` | 已存在 | 保持不变 |

---

## 🚀 部署状态

- ✅ 代码已修改并测试
- ✅ 提交到GitHub: commit 304b149
- ✅ 服务正在运行（PID: 53015）
- ✅ 访问地址: https://5003-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/live

---

## 🔍 验证方法

### 1. **打开 /live 页面**
- 观察曲线图标题是否为"急涨/急跌历史趋势图（今日数据）"
- 检查是否显示今日完整历史数据

### 2. **检查数据源**
- 打开浏览器开发者工具 (F12)
- 查看Network标签
- 确认请求 `/api/history/query` 端点

### 3. **测试刷新**
- 等待3分钟自动刷新
- 或点击"立即刷新"按钮
- 观察图表是否完整重新加载数据

### 4. **对比 /history 页面**
- 打开 `/history` 页面
- 选择今日日期
- 对比两个页面的曲线图数据是否一致

---

## 📊 性能优化

### 数据限制
- 最多显示 **50个数据点**（`MAX_HISTORY_POINTS`）
- API请求限制 **200条记录**（`limit=200`）
- 前端筛选最近50个点

### 加载策略
- 页面加载时：加载1次历史数据
- 自动刷新：每3分钟重新加载
- 手动刷新：立即重新加载

---

## 📝 总结

### ✅ **核心改进**
1. **数据源统一**：从数据库读取，不再前端累加
2. **样式一致**：与 `/history` 页面样式一致
3. **数据准确**：每次显示完整准确的历史数据
4. **用户体验**：页面打开即显示完整数据

### ✅ **保留功能**
- ⭐ 星级提醒系统
- 📊 实时统计数据栏
- 🔄 自动刷新机制
- 🎨 数据点高亮标记

---

**完成时间**: 2025-12-03 19:03:00 (Beijing Time)  
**GitHub提交**: commit 304b149 - "📊 替换/live页面曲线为历史数据曲线"  
**服务状态**: ✅ 正常运行  
**访问地址**: https://5003-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/live
