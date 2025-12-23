# 信号系统配置说明

## 📊 4大信号系统定义

### 1️⃣ 支撑压力线系统
**功能**: 抄底信号和逃顶信号  
**数据源**: `GET /api/support-resistance/latest-signal`  
**信号类型**:
- 🔵 **抄底信号** (Bottom Fishing Signal)
  - 情况1: 价格突破并站稳支撑线
  - 情况2: 价格接近支撑线(5%范围内)
- 🔴 **逃顶信号** (Top Escape Signal)
  - 情况3: 价格突破压力线但未站稳
  - 情况4: 价格接近压力线(5%范围内)

**监控币种**: 8个主流币种 (BTC, ETH, SOL, XRP, BNB, UNI, DOGE, LTC)

---

### 2️⃣ 历史数据查询系统
**功能**: 计次预警  
**数据源**: `crypto_data.db` 数据库  
**信号类型**:
- ⚠️ **计次预警** (Count Warning)
  - 基于历史数据统计的异常计次警报
  - 用于识别市场异常波动

**状态**: 待实现

---

### 3️⃣ 交易信号系统
**功能**: 买点1/2/3信号  
**数据源**: `GET /api/signals/stats`  
**信号类型**:
- 🟢 **买点信号** (Buy Point 1/2/3)
  - 做多信号数 > 30时触发
  - 显示做多/做空比例
  - 信号强度分级(强/中)

**覆盖范围**: 全市场综合信号

---

### 4️⃣ K线指标系统 (买点4)
**功能**: 买点4信号  
**数据源**: `GET /api/kline-indicators/signals`  
**信号类型**:
- 🎯 **买点4** (Buy Point 4)
  - 定义: 7天低点 + 后续2根K线未跌破低点
  - 确认时间: 第2根K线完成时
  - 价格条件: 当前价格在7天低点的5%范围内
  - 时间限制: 仅显示24小时内的信号

**监控币种**: 27个币种 (覆盖所有主流和热门币种)  
**更新频率**: 每5分钟更新一次K线数据

---

## 🤖 Telegram推送配置

### Bot信息
- **Bot Name**: @jamesyi9999_bot
- **Bot ID**: 8437045462
- **Bot Token**: `8437045462:AAFePnwdC21cqeWhZISMQHGGJmroVqE2H0`
- **Chat ID**: `-1003227444260`

### 监控设置
- **检查间隔**: 60秒
- **消息格式**: HTML
- **去重机制**: 基于信号键值(symbol+type+time)
- **发送延迟**: 1秒(避免频繁请求)

---

## 📈 K线信号面板

### 访问地址
```
https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/kline-indicators
```

### 显示内容
1. **买点4** - 7天低点+2根不破 (潜在买入机会)
2. **卖点1** - 7天高点+5根不破 (潜在卖出机会)
3. **7天高点** - 短期阻力位
4. **7天低点** - 短期支撑位
5. **48小时高点** - 超短期阻力
6. **48小时低点** - 超短期支撑

### 更新频率
- 自动刷新: 每30秒
- 数据过滤: 仅显示24小时内信号
- 实时统计: 各类信号数量

---

## 📊 Telegram监控面板

### 访问地址
```
https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/telegram-dashboard
```

### 功能特性
1. **系统状态**
   - 运行状态 (Running/Stopped)
   - 进程ID (PID)
   - 运行时长

2. **统计数据**
   - 总发送数
   - 最近1小时发送数
   - 今日发送数
   - 最后发送时间

3. **信号类型统计**
   - 支撑压力信号数
   - 计次预警数
   - 交易信号数
   - 买点4信号数

4. **历史记录查询**
   - 分页显示
   - 类型过滤
   - 实时刷新(30秒)

---

## 🗄️ 数据库结构

### tg_signals.db
```sql
CREATE TABLE signal_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_type TEXT NOT NULL,     -- 信号类型
    symbol TEXT NOT NULL,           -- 币种符号
    signal_name TEXT NOT NULL,      -- 信号名称
    signal_data TEXT NOT NULL,      -- 信号数据(JSON)
    sent_time TEXT NOT NULL,        -- 发送时间(北京时间)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 系统管理

### 控制脚本
```bash
# 查看状态
bash tg_signal_control.sh status

# 重启服务
bash tg_signal_control.sh restart

# 停止服务
bash tg_signal_control.sh stop

# 启动服务
bash tg_signal_control.sh start

# 查看日志
bash tg_signal_control.sh logs
```

### 日志文件
- **TG监控日志**: `tg_signal_monitor.log`
- **Flask日志**: `flask_app.log`

---

## ✅ 当前运行状态

### 已完成功能
- ✅ 支撑压力线系统(抄底/逃顶信号)
- ✅ 交易信号系统(买点1/2/3)
- ✅ K线指标系统(买点4)
- ✅ Telegram自动推送
- ✅ K线信号面板
- ✅ Telegram监控面板
- ✅ 数据库持久化
- ✅ 去重机制
- ✅ 24小时信号过滤

### 待实现功能
- ⏳ 历史数据查询系统(计次预警)

### 系统指标
- **运行状态**: 🟢 正常
- **消息成功率**: 100%
- **监控币种**: 27个
- **信号准确性**: 已验证
- **推送延迟**: <2秒

---

## 📝 更新日志

### 2025-12-14
- ✅ 修正买点4信号源：从支撑压力API改为K线指标API
- ✅ 添加24小时信号过滤机制
- ✅ 完善K线信号面板显示
- ✅ 清理错误V1/V2信号数据
- ✅ 创建Telegram监控面板
- ✅ 实现4大信号系统监控

---

## 🔗 相关链接

- **GitHub PR**: https://github.com/jamesyidc/66661/pull/1
- **K线指标页面**: /kline-indicators
- **TG监控面板**: /telegram-dashboard
- **支撑压力API**: /api/support-resistance/latest-signal
- **K线信号API**: /api/kline-indicators/signals
- **交易信号API**: /api/signals/stats

