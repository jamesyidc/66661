# 币种K线图详情页功能文档

## 📊 功能概述

为每个币种创建独立的K线图详情页面，展示15天的历史K线数据和所有技术指标。

## 🎯 核心功能

### 1. **独立币种页面**
- **URL格式**: `/symbol/{SYMBOL}` 
- **示例**: `/symbol/BTC-USDT-SWAP`
- 每个币种都有独立的详情页面

### 2. **双时间周期切换**
- **5分钟周期**: 显示最近15天的5分钟K线（约4320根）
- **1小时周期**: 显示最近15天的1小时K线（约360根）
- 一键切换，实时加载数据

### 3. **完整技术指标展示**

#### 主K线图
- 蜡烛图（OHLC）
- 成交量柱状图
- 数据缩放和拖动功能
- 十字准线定位

#### RSI指标图
- RSI(14)曲线
- 超买线（70）
- 超卖线（30）
- 渐变填充效果

#### SAR & 布林带图
- Parabolic SAR点位（多头绿色、空头红色）
- 布林带上轨（红色）
- 布林带中轨（灰色虚线）
- 布林带下轨（绿色）

### 4. **实时统计卡片**
- 当前价格
- RSI指标值（超买/超卖颜色标识）
- SAR位置（多头/空头标签）
- SAR值
- 布林带上轨/下轨

## 🔌 API接口

### 1. K线数据API
**接口**: `/api/symbol/{SYMBOL}/kline`

**参数**:
- `timeframe`: 时间周期（5m 或 1h）

**返回示例**:
```json
{
  "success": true,
  "symbol": "BTC-USDT-SWAP",
  "timeframe": "5m",
  "count": 4320,
  "data": [
    {
      "timestamp": 1765401900000,
      "data": [92486.0, 92334.7, 92300.2, 92528.5],
      "volume": 14920.06
    }
  ]
}
```

### 2. 技术指标API
**接口**: `/api/symbol/{SYMBOL}/indicators`

**参数**:
- `timeframe`: 时间周期（5m 或 1h）

**返回示例**:
```json
{
  "success": true,
  "symbol": "BTC-USDT-SWAP",
  "timeframe": "5m",
  "count": 4320,
  "data": [
    {
      "time": "2025-12-11 08:30:00",
      "price": 90000.50,
      "rsi": 45.23,
      "sar": 89500.00,
      "sar_position": "bullish",
      "sar_label": "多头15",
      "bb_upper": 91000.00,
      "bb_middle": 90000.00,
      "bb_lower": 89000.00
    }
  ]
}
```

## 🎨 页面设计特点

### 视觉风格
- **深色主题**: 专业的交易界面风格
- **主色调**: #00d4aa（青绿色）
- **背景色**: #0e1117（深灰黑）
- **卡片背景**: #1a1d29（深蓝灰）

### 交互体验
- **响应式设计**: 支持桌面和移动端
- **平滑切换**: 时间周期切换无刷新
- **加载动画**: 数据加载时显示旋转动画
- **数据缩放**: 支持鼠标滚轮和拖动缩放
- **悬停提示**: ECharts图表悬停显示详细数据

### 图表特性
- **自适应缩放**: 图表随窗口大小自动调整
- **默认显示区间**: 显示最近50%的数据（可调整）
- **多图表联动**: K线图和成交量共享X轴
- **颜色一致性**: 多头绿色、空头红色

## 📱 使用方式

### 1. 从K线指标页面跳转
在 `/kline-indicators` 页面，点击任意币种名称即可跳转到详情页。

币种名称现在是**蓝色可点击链接**，鼠标悬停显示"查看XXX详细K线图"提示。

### 2. 直接访问URL
直接访问 `https://xxx.com/symbol/BTC-USDT-SWAP` 即可查看BTC详情。

### 3. 支持的币种（27个）
BTC, ETH, XRP, BNB, SOL, LTC, DOGE, SUI, TRX, TON, ETC, BCH, HBAR, XLM, FIL, LINK, CRO, DOT, AAVE, UNI, NEAR, APT, CFX, CRV, STX, LDO, TAO

## 🛠️ 技术实现

### 前端技术栈
- **ECharts 5.4.3**: 专业图表库
- **原生JavaScript**: 无框架依赖
- **Fetch API**: 异步数据加载
- **CSS3**: 现代样式和动画

### 后端技术栈
- **Flask**: Web框架
- **SQLite**: 数据存储
- **Jinja2**: 模板引擎

### 数据来源
- **K线数据**: `okex_kline_5m` 和 `okex_kline_1h` 表
- **技术指标**: `okex_technical_indicators` 表
- **实时更新**: WebSocket采集器持续更新

## 📂 相关文件

- `app_new.py`: Flask路由和API接口
  - `/symbol/<symbol>` - 详情页面路由
  - `/api/symbol/<symbol>/kline` - K线数据API
  - `/api/symbol/<symbol>/indicators` - 指标数据API

- `templates/symbol_detail.html`: 详情页面模板
  - 页面布局和样式
  - ECharts图表配置
  - 交互逻辑

- `templates/kline_indicators.html`: K线指标列表页
  - 添加了币种名称链接
  - 点击跳转到详情页

## 🎯 未来优化方向

1. **数据对比**: 支持多币种K线对比
2. **自定义周期**: 支持更多时间周期（15m, 4h, 1d等）
3. **技术形态识别**: 自动识别头肩顶、双底等形态
4. **预警功能**: 价格突破、指标交叉等预警
5. **数据导出**: 支持CSV/Excel导出
6. **更多指标**: MACD, KDJ, 成交量指标等

## ✅ 功能验证

### 测试步骤
1. 访问 `/kline-indicators` 页面
2. 点击任意币种名称（如BTC）
3. 进入币种详情页，自动加载5分钟K线
4. 点击"1小时"标签，切换到1小时K线
5. 使用鼠标滚轮缩放K线图
6. 悬停查看详细数据点

### 预期结果
- ✅ 页面加载顺畅
- ✅ K线图正确显示
- ✅ RSI和SAR指标准确
- ✅ 时间周期切换流畅
- ✅ 统计卡片实时更新

---

**创建时间**: 2025-12-11  
**功能状态**: ✅ 已完成并测试通过  
**在线访问**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/BTC-USDT-SWAP
