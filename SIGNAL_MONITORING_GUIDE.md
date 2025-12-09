# 📊 交易信号监控系统 - 使用指南

## 🎯 功能概述

本系统自动监控加密货币交易信号，每3分钟采集一次做多/做空信号数据，并提供可视化图表展示历史趋势。

---

## 🌐 访问地址

**主页**: https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/

**信号监控页**: https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/signals

---

## 📋 核心功能

### 1️⃣ 实时统计卡片

页面顶部显示4个统计卡片：

- **最新做多信号** (绿色)
  - 当前时刻的做多信号数量
  - 占比百分比

- **最新做空信号** (红色)
  - 当前时刻的做空信号数量
  - 占比百分比

- **总信号数** (蓝色)
  - 做多+做空的总和
  - 更新时间

- **数据记录** (蓝色)
  - 历史数据点总数
  - 从开始采集至今的记录数

### 2️⃣ 趋势曲线图

**功能特性**:
- 📈 双线图表（做多/做空）
- 🎨 渐变填充效果
- 🔄 每30秒自动刷新
- 👆 鼠标悬停显示详情

**时间范围切换**:
- 1小时: 显示最近1小时数据
- 6小时: 显示最近6小时数据
- **12小时**: 默认显示12小时数据
- 24小时: 显示最近24小时数据

**分页翻页**:
- ← 上一页: 查看更早的数据
- → 下一页: 返回更新的数据
- 页码显示: "第 X / Y 页"

### 3️⃣ 历史记录表格

显示最近50条采集记录：

| 列名 | 说明 |
|------|------|
| 记录时间 | 采集的具体时间 |
| 做多信号 | 绿色显示 |
| 做空信号 | 红色显示 |
| 总信号 | 白色显示 |
| 做多占比 | 百分比（绿色）|
| 做空占比 | 百分比（红色）|

---

## 🔧 管理操作

### 采集器控制

系统提供了便捷的控制脚本：

#### 启动采集器
```bash
cd /home/user/webapp
./signal_control.sh start
```

输出示例：
```
🚀 启动信号采集器...
✅ 信号采集器已启动 (PID: 58478)
📊 采集间隔: 3分钟
📝 日志文件: /home/user/webapp/signal_collector.log
```

#### 停止采集器
```bash
./signal_control.sh stop
```

输出示例：
```
⛔ 停止信号采集器 (PID: 58478)...
✅ 信号采集器已停止
```

#### 重启采集器
```bash
./signal_control.sh restart
```

#### 查看状态
```bash
./signal_control.sh status
```

输出示例：
```
✅ 信号采集器运行中
   PID: 58478
   运行时间: 01:31
   日志文件: /home/user/webapp/signal_collector.log

📊 最近3条采集记录:
   2025-12-06 11:32:54 | 做多:0 做空:0 总计:0
   2025-12-06 11:32:51 | 做多:0 做空:0 总计:0
   2025-12-06 11:32:05 | 做多:0 做空:0 总计:0
```

#### 查看实时日志
```bash
./signal_control.sh logs
```

---

## 📊 数据说明

### 采集间隔
- **频率**: 每3分钟（180秒）
- **自动执行**: 守护进程持续运行
- **首次采集**: 启动后立即执行

### 数据来源

系统从以下API获取数据：

1. **首页统计API**
   ```
   GET https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai/api/kline/summary
   ```
   获取今日新高/新低数据

2. **过滤信号API**
   ```
   GET https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai/api/filtered-signals/stats
   ```
   获取实时的做多做空信号

### 信号分类逻辑

程序会分析每个交易信号的类型：

- **做多信号**: `signal_type` 包含 "long" 或 "做多"
- **做空信号**: `signal_type` 包含 "short" 或 "做空"

---

## 🎨 界面说明

### 深色主题
- 背景: 深蓝黑色渐变
- 卡片: 半透明深灰
- 做多: 绿色 (#10b981)
- 做空: 红色 (#ef4444)
- 强调: 科技蓝 (#00d4ff)

### 响应式设计
- ✅ 桌面端: 完整布局
- ✅ 平板: 自适应
- ✅ 手机: 单列布局

---

## 🔗 API接口文档

### 1. 获取统计数据
```
GET /api/signals/stats
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "latest_time": "2025-12-06 11:32:54",
    "latest_long": 0,
    "latest_short": 0,
    "latest_total": 0,
    "long_ratio": 0.0,
    "short_ratio": 0.0,
    "total_records": 5
  }
}
```

### 2. 获取图表数据
```
GET /api/signals/chart?page=0&range=12h
```

**参数**:
- `page`: 页码（从0开始）
- `range`: 时间范围（1h/6h/12h/24h）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "time": "11:31",
      "long_signals": 0,
      "short_signals": 0,
      "total_signals": 0
    }
  ],
  "page": 0,
  "total_pages": 1,
  "range": "12h"
}
```

### 3. 获取历史记录
```
GET /api/signals/history?limit=50
```

**参数**:
- `limit`: 返回记录数（默认50）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "record_time": "2025-12-06 11:32:54",
      "long_signals": 0,
      "short_signals": 0,
      "total_signals": 0,
      "long_ratio": 0.0,
      "short_ratio": 0.0
    }
  ]
}
```

---

## 📁 文件结构

```
/home/user/webapp/
├── signal_collector.py       # 采集器主程序
├── signal_control.sh         # 控制脚本
├── signal_collector.log      # 采集日志
├── signal_collector.pid      # 进程PID文件
├── app_new.py                # Flask Web应用
├── templates/
│   └── signals.html          # 监控页面模板
└── crypto_data.db            # SQLite数据库
    └── trading_signals表     # 信号数据表
```

---

## ⚠️ 注意事项

### 数据为0的情况

如果看到做多/做空信号都是0，可能原因：

1. **源API无数据**: filtered-signals API当前无有效信号
2. **筛选条件**: RSI阈值设置可能过滤了所有信号
3. **市场状态**: 当前市场可能没有符合条件的交易机会

**解决方法**:
- 等待市场波动，信号会逐渐出现
- 检查源站点是否正常: https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai/filtered-signals.html
- 查看日志确认采集是否正常

### 采集器异常

如果采集器停止工作：

```bash
# 1. 查看状态
./signal_control.sh status

# 2. 查看日志
tail -50 signal_collector.log

# 3. 重启采集器
./signal_control.sh restart
```

---

## 📞 技术支持

**GitHub仓库**: https://github.com/jamesyidc/6666

**PR链接**: https://github.com/jamesyidc/6666/pull/1

**提交记录**: 
- `9264956` - 主要功能实现
- `32108f0` - 完成报告

---

## 🎯 快速开始

### 第一步：访问首页
打开: https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/

### 第二步：进入监控页
点击"交易信号监控"卡片，或直接访问：
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/signals

### 第三步：查看数据
- 顶部: 实时统计
- 中部: 趋势图表（可切换时间范围）
- 底部: 历史记录表格

### 第四步：管理采集器（可选）
```bash
cd /home/user/webapp
./signal_control.sh status    # 查看状态
./signal_control.sh logs      # 查看日志
```

---

**文档版本**: 1.0  
**更新时间**: 2025-12-06 11:38  
**作者**: GenSpark AI Developer
