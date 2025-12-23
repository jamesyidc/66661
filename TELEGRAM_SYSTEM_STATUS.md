# Telegram信号推送系统 - 完整版运行状态

## ✅ 系统状态

### 核心服务
- **Flask应用**: ✅ 运行中 (PID: 98035)
- **Telegram推送服务**: ✅ 运行中 (PID: 98926)
- **数据采集器**: ✅ 运行中

### 系统访问
- **监控仪表盘**: https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/telegram-dashboard
- **强制刷新**: Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac)

## 📊 三大块系统配置（完整版）

### 一、支撑压力线系统（抄底/逃顶）
- **数据源**: /support-resistance
- **API**: `/api/telegram/signals/support-resistance`
- **触发条件**: 2小时内的新信号
- **信号类型**:
  - 🟢 抄底信号 (buy)
  - 🔴 逃顶信号 (sell)

### 二、计次预警系统
- **数据源**: /query
- **API**: `/api/telegram/signals/count-alerts`
- **触发条件**:
  - 每小时整点记录基准计次值
  - 当前计次 >= 基准值+2 时触发预警
- **监控指标**: 急涨、急跌、计次、状态、差值等

### 三、交易信号系统（完整版）
- **API**: `/api/telegram/signals/trading`

#### 3.1 买点信号（来源：trading-signals）
- 🟢 **买点1**: 连续下跌 + 反弹确认
- 🟢 **买点2**: 震荡筑底 + 突破
- 🟢 **买点3**: 回调支撑 + 反弹

#### 3.2 买点4 + 卖点1（来源：kline-indicators）
- 🟢 **买点4**: 5分钟周期 + 7日最低点 + 后续2根K线不创新低 + **RSI < 20**
- 🔴 **卖点1**: 价格冲高 + **RSI >= 60**

#### 3.3 高低点信号（来源：kline-indicators）
- 📈 **7日最高点**: 7天内价格最高点
- 📉 **7日最低点**: 7天内价格最低点
- 📈 **48h最高点**: 48小时内价格最高点
- 📉 **48h最低点**: 48小时内价格最低点

## 🔔 Telegram推送规则

### 推送时间窗口
- **所有信号**: 2小时内的新信号自动推送
- **检查频率**: 每60秒检查一次
- **自动去重**: 相同信号不会重复推送

### 推送格式示例

#### 买点4推送
```
🟢 【买点4】

币种: BTC
价格: $42,350.00
时间: 2025-12-15 18:30:00
RSI: 18.5
7日低点: $41,800.00

[查看详情]
```

#### 7日最高点推送
```
📈 【7日最高点】

币种: ETH
价格: $2,250.00
时间: 2025-12-15 18:30:00

[查看详情]
```

#### 计次预警推送
```
⚠️ 【计次预警】

当前计次: 9次
基准值: 7次 (09:00)
超出: +2次

运算时间: 2025-12-15 09:30:00
急涨: 18 | 急跌: 5
状态: 震荡无序

[查看详情]
```

## 📈 信号统计

### 当前状态（最新）
- **支撑压力线**: 0个信号
- **计次预警**: 0个预警
- **交易信号**: 0个信号（买点4需RSI<20）

### 数据库信号
- **买点4**: 128个（RSI为NULL，不推送）
- **其他信号**: 待市场触发

## 🔄 系统运行机制

### 监控流程
```
每60秒循环:
1. 检查支撑压力线系统 → 抄底/逃顶信号
2. 检查计次预警系统 → 整点记录 + 阈值判断
3. 检查交易信号系统 → 
   - 买点1-3（trading-signals API）
   - 买点4、卖点1、7日/48h高低点（kline-indicators API）
4. 去重 + 推送新信号到Telegram
```

### 数据库表结构
```sql
-- 支撑压力线信号
support_resistance_signals (
    symbol, signal_type, price, signal_time
)

-- 计次预警
count_alerts (
    record_time, count_value, threshold, full_data
)

-- 计次基准（每小时整点）
count_baselines (
    hour_time, count_value
)

-- 交易信号（统一）
trading_signals (
    signal_type,  -- buy_point_1/2/3/4, sell_point_1, 
                  -- day7_high/low, h48_high/low
    symbol, price, signal_time, rsi, additional_info
)
```

## 🛠️ 系统控制

### 命令行控制
```bash
# 查看日志
tail -f telegram_signal_system.log

# 停止系统
./stop_telegram_signal_system.sh

# 启动系统
./start_telegram_signal_system.sh
```

### API控制
- **启动**: `POST /api/telegram/start`
- **停止**: `POST /api/telegram/stop`
- **状态**: `GET /api/telegram/system/status`

### 仪表盘控制
访问 `/telegram-dashboard` 页面，点击右上角状态按钮：
- **⚪ 未运行**: 点击启动
- **🟢 运行中**: 点击停止

## 📱 Telegram配置

- **Bot Token**: `8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0`
- **Chat ID**: `-1003227444260`
- **系统启动消息**: ✅ 已发送（包含完整监控模块列表）

## 🎯 信号触发条件汇总

| 信号类型 | 数据源 | 触发条件 | 推送时间 |
|---------|--------|---------|---------|
| 抄底/逃顶 | support-resistance | 出现新信号 | 2小时内 |
| 计次预警 | query | 整点后达到阈值 | 实时 |
| 买点1-3 | trading-signals | 出现新信号 | 2小时内 |
| 买点4 | kline-indicators | RSI < 20 + 7日低点 | 2小时内 |
| 卖点1 | kline-indicators | RSI >= 60 + 冲高 | 2小时内 |
| 7日最高/低点 | kline-indicators | 达到极值点 | 2小时内 |
| 48h最高/低点 | kline-indicators | 达到极值点 | 2小时内 |

## 📝 更新日志

### v2.0 - 2025-12-15 10:45
- ✅ 添加 7日最高/低点信号监控和推送
- ✅ 添加 48h最高/低点信号监控和推送
- ✅ 仪表盘标题更新为"买点1-4 + 卖点1 + 7日/48h高低点"
- ✅ 添加蓝色中性样式用于高低点信号
- ✅ 使用 📈/📉 图标区分高点和低点

### v1.0 - 2025-12-15 10:24
- ✅ 三大块系统整合完成
- ✅ 支撑压力线、计次预警、交易信号监控
- ✅ 买点1-4 + 卖点1 自动推送
- ✅ 每60秒自动检查，去重推送

---
**系统版本**: v2.0  
**更新时间**: 2025-12-15 10:50:00  
**状态**: ✅ 完整运行中
