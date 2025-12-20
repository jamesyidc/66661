# 🚀 加密货币交易决策支持系统

> 一个集成多数据源、技术分析工具和实时监控的综合性加密货币交易决策系统

[![Version](https://img.shields.io/badge/version-v3.9.9-blue.svg)](https://github.com/jamesyidc/66661)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-yellow.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/jamesyidc/66661)

---

## 📋 项目简介

本系统是一个**全方位的加密货币交易决策支持平台**，整合了：
- 🎯 **K线技术分析**：多指标、买卖信号、逃顶提示
- 📊 **V1V2监控**：27币种实时成交额监控+6时间维度统计
- 🔄 **支撑压力系统**：市场情绪分析+信号生成
- 📈 **急涨急跌监控**：实时追踪市场异动

---

## ✨ 核心功能

### 1. 📊 K线图分析系统（v3.9系列）

#### 技术指标
- ✅ RSI (相对强弱指数)
- ✅ MACD (指数平滑移动平均线)
- ✅ SAR (抛物线转向指标)
- ✅ ATR (平均真实波幅)
- ✅ 布林带 (Bollinger Bands)
- ✅ WMA / EMA (加权/指数移动平均)

#### 交易信号
- 🔴 **买入4**: 7天低点 + 2根K线不创新低 + 支撑确认
- 🟢 **卖点2**: 高点 + 5根K线不创新高 + RSI过滤
- 🔵 **卖点1**: 历史高点 + 下跌趋势确认

#### 特殊标记
- 🟠 **逃顶信号**: 阻力位情况3+4>=8，橙色标记
- 🟣 **数据时效**: 支撑压力最新采集时间提示

### 2. 📈 V1V2监控系统

#### 实时监控
- **监控币种**: 27个主流币种
- **数据来源**: OKEx 5分钟成交额
- **更新频率**: 每30秒自动刷新
- **级别判定**: 
  - V1: 高成交额（>=v1阈值）
  - V2: 中等成交额（>=v2阈值）
  - None: 未达标

#### 统计分析（19列表格）
- **时间维度**: 1h, 3h, 12h, 今日, 3日, 7日
- **统计指标**: V1次数, V2次数, 合计
- **排序功能**: 全列支持升序/降序
- **应用场景**: 
  - 短期监控：捕捉突发热点（1h/3h/12h）
  - 长期追踪：识别持续活跃币种（今日/3日/7日）
  - 趋势对比：多维度数据交叉分析

### 3. 🎯 支撑压力系统

- **4种情况统计**: 
  - 情况1: 接近支撑2
  - 情况2: 接近支撑1
  - 情况3: 接近阻力1
  - 情况4: 接近阻力2
- **信号生成**:
  - 买入信号: 情况1+2 >= 16
  - 卖出信号: 情况3+4 >= 8
- **实时联动**: 与K线图实时集成

### 4. 📉 急涨急跌监控

- **数据源**: Google Drive 自动采集
- **采集频率**: 每10分钟
- **监控内容**: 
  - 急涨币种数量
  - 急跌币种数量
  - 急涨急跌比值
  - 详细币种信息

---

## 🎯 在线体验

### 主要页面
- **系统主页**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/
- **V1V2监控**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/v1v2-monitor
- **支撑阻力**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/support-resistance

### K线图示例
- **LINK**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/LINK/v6
- **BTC**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/BTC/v6
- **ETH**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/ETH/v6

---

## 📚 文档导航

### 📖 快速入门
1. **[文档索引.md](./文档索引.md)** - 所有文档快速导航
2. **[决策系统完整版本历史.md](./决策系统完整版本历史.md)** - 系统发展历程（⭐推荐）
3. **[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)** - 系统架构说明

### 📊 功能文档
- **[V1V2统计功能说明.md](./V1V2统计功能说明.md)** - V1V2监控系统完整说明
- **[V1V2_1h3h12h统计功能完成.md](./V1V2_1h3h12h统计功能完成.md)** - 小时级统计详解
- **[KLINE_HIGHLOW_MARKERS_FEATURE.md](./KLINE_HIGHLOW_MARKERS_FEATURE.md)** - K线标记功能

### 🔧 技术文档
- **[AUTO_COLLECTOR_README.md](./AUTO_COLLECTOR_README.md)** - 自动采集器说明
- **[DATABASE_USAGE.md](./DATABASE_USAGE.md)** - 数据库使用指南

---

## 🛠️ 技术栈

### 后端
- **Python 3.9+**: 核心开发语言
- **Flask**: Web框架
- **SQLite**: 数据存储
- **Playwright**: 浏览器自动化（Google Drive采集）
- **APScheduler**: 定时任务

### 前端
- **JavaScript ES6+**: 原生JS开发
- **ECharts 5.x**: 图表可视化
- **CSS3**: 自定义样式+渐变效果
- **响应式设计**: 支持桌面和移动端

### 数据源
- **OKEx API**: K线数据、成交额数据
- **Google Drive**: 急涨急跌数据
- **自研算法**: 支撑压力计算、信号生成

---

## 📊 系统统计

### 规模（截至 2025-12-13）
- **代码提交**: 100+ commits
- **版本迭代**: v1.0 → v3.9.9
- **监控币种**: 27 个
- **API端点**: 50+ 个
- **数据表**: 20+ 个
- **文档文件**: 100+ Markdown文件

### 今日数据（示例）
- **V1V2总信号**: 3,591次
  - V1信号: 2,867次
  - V2信号: 724次
- **Top 5活跃币种**:
  1. BTC: 338次
  2. ETH: 337次
  3. SOL: 328次
  4. LTC: 327次
  5. DOGE: 325次

---

## 🚀 快速部署

### 环境要求
```bash
Python 3.9+
pip
SQLite 3
Playwright (for browser automation)
```

### 安装步骤
```bash
# 1. 克隆仓库
git clone https://github.com/jamesyidc/66661.git
cd 66661

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装Playwright浏览器
playwright install chromium

# 4. 初始化数据库
python init_db.py

# 5. 启动Flask服务
python app_new.py

# 6. 启动采集器（可选）
python auto_gdrive_collector_v2.py &
python v1v2_stats_collector.py &
```

### 访问系统
```
打开浏览器访问: http://localhost:5000
```

---

## 📈 版本历史

### 最新版本: v3.9.9（2025-12-13）
- ✅ 时间显示统一为北京时间
- ✅ 明确标注时区（"北京20:06"）
- ✅ 浏览器缓存清理指南

### V1V2系统: v1.3（2025-12-13）
- ✅ 新增1h/3h/12h小时级统计
- ✅ 表格扩展到19列
- ✅ 实时查询原始数据

### 详细历史
查看 **[决策系统完整版本历史.md](./决策系统完整版本历史.md)**

---

## 🗺️ 路线图

### 短期目标（Q1 2025）
- [ ] 机器学习价格预测模型
- [ ] 实时告警系统（微信/Telegram）
- [ ] 策略回测框架

### 中期目标（Q2-Q3 2025）
- [ ] 多交易所支持（Binance, Huobi）
- [ ] 移动端应用开发
- [ ] 社区功能（策略分享）

### 长期目标（Q4 2025+）
- [ ] AI交易助手
- [ ] 企业SaaS版本
- [ ] 云服务化部署

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 开发规范
- 代码风格：遵循PEP 8
- 提交信息：使用语义化提交（Conventional Commits）
- 测试：新功能需要添加测试
- 文档：更新相关文档

---

## 📄 许可证

本项目采用 **MIT License** 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👥 团队

- **核心开发**: AI Assistant
- **产品需求**: @jamesyidc
- **GitHub**: https://github.com/jamesyidc/66661

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/jamesyidc/66661/issues
- **Pull Requests**: https://github.com/jamesyidc/66661/pulls
- **当前PR**: https://github.com/jamesyidc/66661/pull/1

---

## 🙏 致谢

感谢所有为本项目提供反馈和建议的用户！

---

## ⭐ Star History

如果这个项目对你有帮助，请给我们一个 ⭐ Star！

---

**项目状态**: ✅ 积极维护中  
**最后更新**: 2025-12-13  
**版本**: v3.9.9 + V1V2 v1.3
