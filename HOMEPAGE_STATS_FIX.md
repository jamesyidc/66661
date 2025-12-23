# 首页统计数据修复报告

## 问题描述
首页的统计卡片显示的数据没有实时更新，停留在旧数据：
- **交易信号监控**: 1125条记录，最后更新 16:23
- **恐慌清洗指数**: 963条记录，最后更新 16:22

## 根本原因
1. **数据表停止更新**：
   - `trading_signals` 表最后更新时间：2025-12-11 16:23:25
   - `panic_wash_index` 表最后更新时间：2025-12-11 16:22:59

2. **采集脚本未运行**：
   - PM2中只运行了3个服务：flask-app, gdrive-monitor, websocket-collector
   - 缺少 `signal_collector.py` 和 `panic_wash_collector.py` 两个数据采集脚本

## 解决方案
启动缺失的数据采集服务：

### 1. 启动交易信号采集器
```bash
pm2 start signal_collector.py --name signal-collector --interpreter python3
```
- 功能：每3分钟采集一次交易信号数据（做多/做空数量）
- 数据源：filtered-signals API
- 存储表：`trading_signals`

### 2. 启动恐慌清洗指数采集器
```bash
pm2 start panic_wash_collector.py --name panic-collector --interpreter python3
```
- 功能：每3分钟采集一次爆仓数据并计算恐慌清洗指数
- 数据源：btc123.fans爆仓API
- 存储表：`panic_wash_index`
- 计算公式：恐慌清洗指数 = 24小时爆仓人数(万人) / 全网持仓量(亿美元)

### 3. 保存PM2配置
```bash
pm2 save
```

## 修复结果

### 数据更新验证
**修复前**:
```json
{
  "signal_module": {
    "total_records": 1125,
    "last_update": "16:23"
  },
  "panic_module": {
    "total_records": 963,
    "last_update": "16:22"
  }
}
```

**修复后**:
```json
{
  "signal_module": {
    "total_records": 1127,
    "last_update": "18:55"
  },
  "panic_module": {
    "total_records": 964,
    "last_update": "18:55"
  }
}
```

✅ **统计数据已实时更新**

### PM2服务列表
当前运行的5个服务：

| ID | 服务名 | 功能 | 状态 |
|----|--------|------|------|
| 0 | flask-app | Web服务器 | ✅ Online |
| 1 | websocket-collector | K线数据采集 | ✅ Online |
| 2 | gdrive-monitor | Drive监控 | ✅ Online |
| 3 | signal-collector | 交易信号采集 | ✅ Online (新增) |
| 4 | panic-collector | 恐慌指数采集 | ✅ Online (新增) |

## 验证方法

### 1. 检查PM2服务状态
```bash
pm2 list
```

### 2. 查看采集器日志
```bash
# 交易信号采集器日志
pm2 logs signal-collector --lines 20

# 恐慌指数采集器日志
pm2 logs panic-collector --lines 20
```

### 3. 测试API
```bash
curl http://localhost:5000/api/modules/stats | python3 -m json.tool
```

### 4. 访问首页
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai

## 技术细节

### signal_collector.py
- **采集间隔**: 180秒（3分钟）
- **API端点**: `https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai`
- **数据字段**:
  - record_time: 记录时间
  - record_date: 记录日期
  - total_signals: 总信号数
  - long_signals: 做多信号数
  - short_signals: 做空信号数
- **日志文件**: `/home/user/webapp/signal_collector.log`

### panic_wash_collector.py
- **采集间隔**: 180秒（3分钟）
- **API端点**: `https://api.btc123.fans/bicoin.php`
- **数据字段**:
  - record_time: 记录时间
  - liquidation_1h: 1小时爆仓金额(万)
  - liquidation_24h: 24小时爆仓金额(亿)
  - liquidation_people_24h: 24小时爆仓人数(万人)
  - total_positions: 全网持仓量(亿)
  - panic_index: 恐慌清洗指数
- **日志文件**: `/home/user/webapp/panic_wash_collector.log`

## 注意事项

1. **服务自动启动**: PM2配置已保存，服务器重启后会自动恢复
2. **采集频率**: 两个采集器都是每3分钟运行一次
3. **日志监控**: 建议定期检查日志确保采集正常
4. **错误处理**: 两个采集器都有重试机制（最多4次尝试）

## 相关文件
- `signal_collector.py` - 交易信号采集器
- `panic_wash_collector.py` - 恐慌清洗指数采集器
- `app_new.py` - Flask API服务（包含/api/modules/stats接口）
- `templates/index.html` - 首页模板（统计卡片展示）

## 时间线
- **问题发现**: 2025-12-11 10:50
- **问题诊断**: 数据表停止更新在 16:22-16:23
- **解决方案实施**: 启动signal-collector和panic-collector
- **验证完成**: 2025-12-11 18:55 数据更新成功

---
**修复日期**: 2025-12-11  
**修复人员**: AI Assistant  
**影响范围**: 首页统计卡片数据展示  
**修复状态**: ✅ 已完成
