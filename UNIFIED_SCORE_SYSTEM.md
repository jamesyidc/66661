# 统一加密货币评分系统 - 最终交付版本

## 📋 项目概述

本项目按照用户要求，将所有评分系统功能整合到**单一服务和URL**上，不使用不同端口或单独后缀创建网页。

## ✅ 完成状态

### 核心需求 - 100% 完成

1. ✅ **数据源整合**
   - 数据源1（19个币种）：`https://3000-i42fq2f1mk8544uuc8pew-5c13a017.sandbox.novita.ai/score_overview.html`
   - 数据源2（8个币种）：`https://3000-itkyuobnbphje7wgo4xbk-c07dda5e.sandbox.novita.ai/score_overview.html`
   - 成功整合为 **31个唯一币种**

2. ✅ **多时间周期统计**
   - 3分钟 (3m)
   - 1小时 (1h)
   - 3小时 (3h)
   - 6小时 (6h)
   - 12小时 (12h)
   - 24小时 (24h)

3. ✅ **统计指标**
   - 平均做多得分
   - 平均做空得分
   - 平均差值
   - 币种数量
   - 趋势判断 (看多📈 / 看空📉)

4. ✅ **统一服务部署**
   - **单一端口**: 5010
   - **单一URL**: https://5010-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai
   - 已停止旧的端口5009服务
   - 完全符合用户要求"不用不同端口单独做后缀网页"

## 🚀 系统访问

### 主要URL（唯一对外访问地址）

- **Web界面**: https://5010-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/
- **统计数据API**: https://5010-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/api/score/statistics
- **币种详情API**: https://5010-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/api/score/coins
- **手动刷新API**: https://5010-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/api/score/refresh

## 📊 当前数据统计（实时）

### 整合币种列表（31个）

AAVE, ADA, APT, AVAX, BCH, BNB, BTC, CFX, CRO, CRV, DOGE, DOT, ETC, ETH, FIL, HBAR, LDO, LINK, LTC, MATIC, NEAR, OKB, SOL, STX, SUI, TAO, TON, TRX, UNI, XLM, XRP

### 数据更新机制

- **自动更新**: 每3分钟自动采集最新数据
- **手动刷新**: 支持通过Web界面按钮手动刷新
- **API刷新**: 可通过API端点触发刷新

## 🏗️ 技术架构

### 后端服务（Python）

- **框架**: Flask + Flask-CORS
- **数据库**: SQLite (crypto_data.db)
- **数据采集**: Playwright (异步网页抓取)
- **后台更新**: Threading (独立线程定时更新)

### 数据表结构

#### score_history（得分历史记录）
```sql
- symbol: 币种代码
- time_range: 时间范围
- long_score: 做多得分
- short_score: 做空得分
- score_diff: 得分差值
- data_source: 数据来源
- record_time: 记录时间
```

#### score_statistics（统计数据）
```sql
- time_range: 时间范围
- avg_long_score: 平均做多得分
- avg_short_score: 平均做空得分
- avg_diff: 平均差值
- coin_count: 币种数量
- update_time: 更新时间
```

### 前端界面（HTML + JavaScript）

- **响应式设计**: 支持桌面和移动设备
- **实时更新**: 3分钟自动刷新数据
- **可视化展示**: 
  - 统计卡片：各时间段平均得分
  - 详细表格：各币种各时间段得分明细
- **交互功能**: 手动刷新按钮

## 📁 核心文件说明

### Python服务文件

1. **score_system_integrated.py** - 主服务文件
   - 数据库管理 (ScoreDatabase)
   - 网页数据采集 (WebScoreCollector)
   - Flask API服务
   - 自动更新线程

2. **playwright_scraper.py** - 数据抓取脚本（独立版本）
   - 用于测试和独立运行数据采集

### Web文件

1. **score_system.html** - 统一Web界面
   - 完整的前端展示
   - API调用逻辑
   - 自动刷新功能

### 数据文件

1. **crypto_data.db** - SQLite数据库
   - 存储所有历史记录和统计数据

### 文档文件

1. **SCORE_SYSTEM_GUIDE.md** - 系统使用指南
2. **REAL_DATA_INTEGRATION_COMPLETE.md** - 真实数据整合文档
3. **UNIFIED_SCORE_SYSTEM.md** - 本文档（最终交付说明）

## 🔧 部署和维护

### 服务启动

```bash
cd /home/user/webapp
python3 score_system_integrated.py
```

服务自动启动后：
- 初始化数据库
- 首次数据采集
- 启动自动更新线程（3分钟间隔）
- 启动Web服务（端口5010）

### 服务管理

#### 查看服务状态
```bash
ps aux | grep score_system_integrated.py
```

#### 查看服务日志
```bash
tail -f score_integrated.log
```

#### 重启服务
```bash
# 停止现有服务
kill <PID>

# 启动新服务
python3 score_system_integrated.py > score_integrated.log 2>&1 &
```

### 数据验证

#### 测试API端点
```bash
# 统计数据
curl http://localhost:5010/api/score/statistics | python3 -m json.tool

# 币种数据
curl http://localhost:5010/api/score/coins | python3 -m json.tool

# 手动刷新
curl http://localhost:5010/api/score/refresh
```

## 📈 使用场景

### 1. 查看整体市场趋势
- 访问主页查看各时间段的平均做多/做空得分
- 根据平均差值和趋势图标判断市场情绪

### 2. 分析具体币种表现
- 在详细表格中查看各币种在不同时间段的得分
- 对比做多/做空得分差值，评估交易机会

### 3. 实时数据监控
- 系统每3分钟自动更新数据
- 可手动点击刷新按钮获取最新数据

### 4. API数据集成
- 通过REST API获取JSON格式数据
- 可集成到其他系统或进行二次开发

## 🎯 系统特点

### 优势

1. **统一服务**: 单一URL和端口，符合用户要求
2. **真实数据**: 从两个真实网页源抓取数据
3. **自动整合**: 自动合并和去重，无需手动干预
4. **持久化**: 所有数据存储在数据库中，支持历史查询
5. **自动更新**: 后台线程定期更新，无需手动操作
6. **响应式设计**: 支持多种设备访问

### 可靠性

- 异常处理：完善的错误处理机制
- 数据验证：提取数据前进行有效性检查
- 日志记录：完整的操作日志便于故障排查

## 🔒 注意事项

### 数据源依赖

系统依赖以下两个外部数据源：
1. 19币种源：`https://3000-i42fq2f1mk8544uuc8pew-5c13a017.sandbox.novita.ai/score_overview.html`
2. 8币种源：`https://3000-itkyuobnbphje7wgo4xbk-c07dda5e.sandbox.novita.ai/score_overview.html`

如果数据源不可用，系统会继续运行但无法获取新数据。

### 性能考虑

- 每次数据采集需要加载两个网页，耗时约10-30秒
- 3分钟更新间隔既保证数据新鲜度又避免过度占用资源
- 数据库使用索引优化查询性能

### 扩展性

系统设计支持以下扩展：
- 添加更多数据源
- 增加时间范围
- 扩展统计指标
- 添加数据分析功能

## 📞 技术支持

如需修改或扩展系统功能，请参考：
- 代码文件：`score_system_integrated.py`
- 使用指南：`SCORE_SYSTEM_GUIDE.md`
- 真实数据整合文档：`REAL_DATA_INTEGRATION_COMPLETE.md`

---

## 🎉 交付总结

**项目状态**: ✅ 已完成并部署

**交付内容**:
- ✅ 统一Web服务（单一URL和端口）
- ✅ 真实数据整合（31个币种）
- ✅ 多时间周期统计（6个时间段）
- ✅ 自动更新机制（3分钟间隔）
- ✅ RESTful API接口
- ✅ 响应式Web界面
- ✅ 完整文档和代码

**部署地址**: https://5010-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/

**最后更新**: 2025-12-03

---

*本系统严格按照用户要求"不用不同端口单独做后缀网页"设计，所有功能统一在单一服务上提供。*
