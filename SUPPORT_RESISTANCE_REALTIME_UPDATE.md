# 支撑/压力线实时更新机制说明

## 当前更新机制

### 📊 数据采集

**support_resistance_collector.py** 采集器负责:
- **采集频率**: 每5分钟采集一次
- **数据内容**:
  - 获取当前价格(实时)
  - 计算7天支撑/压力线
  - 计算48小时支撑/压力线
  - 计算距离百分比
  - 计算位置百分比
- **存储位置**: `support_resistance_levels` 表

### 🌐 前端更新

**templates/support_resistance.html** 页面:
- **刷新频率**: 每30秒自动刷新
- **数据来源**: `/api/support-resistance/latest` API
- **更新内容**:
  - 当前价格
  - 支撑/压力线
  - 距离百分比
  - 位置百分比
  - 警报状态

### 🔄 更新流程

```
第0秒  - 采集器采集数据 → 存入数据库
第30秒 - 前端刷新 → 读取最新数据(来自第0秒采集)
第60秒 - 前端刷新 → 读取最新数据(来自第0秒采集)
第90秒 - 前端刷新 → 读取最新数据(来自第0秒采集)
...
第300秒 - 采集器再次采集 → 更新数据库
第330秒 - 前端刷新 → 读取最新数据(来自第300秒采集)
```

## 数据验证

### API 返回示例 (2025-12-14 21:50)

```json
{
  "symbol": "BTCUSDT",
  "current_price": 89848.30,
  "support_line_1": 88503.30,    // 7天最低
  "support_line_2": 88503.30,    // 48h最低
  "resistance_line_1": 90450.00, // 7天最高
  "resistance_line_2": 90450.00, // 48h最高
  "distance_to_support_1": 1.52, // 距离7天支撑的百分比
  "distance_to_support_2": 1.52, // 距离48h支撑的百分比
  "distance_to_resistance_1": 0.67, // 距离7天压力的百分比
  "distance_to_resistance_2": 0.67  // 距离48h压力的百分比
}
```

### 距离计算公式

**距离支撑线百分比**:
```
distance_to_support = ((current_price - support_line) / support_line) * 100
```

**距离压力线百分比**:
```
distance_to_resistance = ((resistance_line - current_price) / current_price) * 100
```

### 实际数据验证

所有27个币种的距离数据都正常:

```
✅ BTCUSDT: S1=+1.52%, S2=+1.52%, R1=+0.67%, R2=+0.67%
✅ ETHUSDT: S1=+1.83%, S2=+1.83%, R1=+0.83%, R2=+0.83%
✅ XRPUSDT: S1=+0.83%, S2=+0.83%, R1=+1.74%, R2=+1.74%
✅ BNBUSDT: S1=+0.70%, S2=+0.70%, R1=+1.60%, R2=+1.60%
✅ SOLUSDT: S1=+1.25%, S2=+1.25%, R1=+1.56%, R2=+1.56%
... (共27个币种)

统计: 有效数据 27/27, 距离都为0: 0/27
```

## 常见问题排查

### 问题1: 页面显示距离都是 +0.00%

**可能原因**:
1. 浏览器缓存了旧的 JavaScript 代码
2. API 调用失败
3. 数据格式解析错误

**解决方法**:
1. **强制刷新浏览器**: 
   - Windows: `Ctrl + F5` 或 `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`
2. **清除浏览器缓存**:
   - Chrome: 设置 → 隐私和安全 → 清除浏览数据
   - Firefox: 设置 → 隐私与安全 → 清除数据
3. **检查浏览器控制台**: 
   - 按 `F12` 打开开发者工具
   - 查看 Console 标签是否有错误
   - 查看 Network 标签,检查 API 请求是否成功

### 问题2: 数据不更新

**检查步骤**:

1. **检查采集器是否运行**:
   ```bash
   ps aux | grep support_resistance_collector
   ```

2. **检查最新采集时间**:
   ```bash
   tail -10 support_resistance_collector.log
   ```

3. **检查数据库最新数据**:
   ```bash
   sqlite3 crypto_data.db "SELECT symbol, record_time FROM support_resistance_levels ORDER BY record_time DESC LIMIT 5"
   ```

4. **检查 Flask 服务**:
   ```bash
   curl http://localhost:5000/api/support-resistance/latest
   ```

### 问题3: 页面显示错误

**检查步骤**:

1. **打开浏览器开发者工具** (F12)
2. **查看 Console 错误信息**
3. **查看 Network 请求**:
   - 找到 `/api/support-resistance/latest` 请求
   - 查看 Response 数据
   - 检查 Status Code (应该是 200)

## 手动测试

### 测试 API
```bash
curl -s http://localhost:5000/api/support-resistance/latest | python3 -m json.tool | head -50
```

### 测试采集器
```bash
# 查看采集器日志
tail -f /home/user/webapp/support_resistance_collector.log

# 手动运行一次采集
cd /home/user/webapp
python3 support_resistance_collector.py
```

### 测试数据库
```bash
cd /home/user/webapp
sqlite3 crypto_data.db << 'EOF'
SELECT symbol, current_price, 
       support_line_1, distance_to_support_1,
       support_line_2, distance_to_support_2,
       record_time
FROM support_resistance_levels
WHERE symbol = 'BTCUSDT'
ORDER BY record_time DESC
LIMIT 1;
EOF
```

## 页面访问

- **URL**: https://5000-iz6uddj6rs3xe48ilsyqq-cbeee0f9.sandbox.novita.ai/support-resistance
- **更新频率**: 每30秒自动刷新
- **数据源**: 每5分钟采集一次的最新数据

## 代码位置

- **采集器**: `support_resistance_collector.py` (第102-198行)
- **API**: `app_new.py` (第5787-5972行)
- **前端**: `templates/support_resistance.html` (第1071-1097行, 第2268-2280行)
- **距离计算**: `support_resistance_collector.py` (第136-139行)

## 总结

✅ **采集器**: 每5分钟采集一次,计算实时价格和距离百分比  
✅ **API**: 返回最新数据,包含正确的距离百分比  
✅ **前端**: 每30秒自动刷新,显示最新数据  
✅ **数据验证**: 所有27个币种距离数据正常  

如果页面显示异常,请强制刷新浏览器(Ctrl+F5)清除缓存。
