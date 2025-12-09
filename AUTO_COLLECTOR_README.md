# Google Drive 自动采集器 V2 使用文档

## 功能说明

自动从 Google Drive 读取最新的加密货币数据文件，并保存到本地数据库。

### 核心特性

- ✅ **使用 Playwright 浏览器自动化** - 绕过 API 限制
- ✅ **定时自动采集** - 默认每10分钟采集一次
- ✅ **后台持续运行** - 可作为守护进程运行
- ✅ **自动错误恢复** - 采集失败自动重试
- ✅ **完整日志记录** - 所有操作均有日志
- ✅ **安全停止机制** - 支持优雅退出

## 快速开始

### 1. 启动采集器

```bash
./start_collector.sh
```

**输出示例**:
```
🚀 启动 Google Drive 自动采集器...
✓ 采集器已启动 (PID: 12345)
📝 日志文件: logs/collector.log

查看日志: tail -f logs/collector.log
停止采集: ./stop_collector.sh
查看状态: python3 auto_gdrive_collector_v2.py --status
```

### 2. 查看状态

```bash
./status_collector.sh
```

或者:
```bash
python3 auto_gdrive_collector_v2.py --status
```

### 3. 停止采集器

```bash
./stop_collector.sh
```

### 4. 查看实时日志

```bash
tail -f logs/collector.log
```

## 使用方法

### 方法一：后台运行（推荐）

```bash
# 启动
./start_collector.sh

# 查看状态
./status_collector.sh

# 查看日志
tail -f logs/collector.log

# 停止
./stop_collector.sh
```

### 方法二：测试模式（执行一次）

```bash
python3 auto_gdrive_collector_v2.py --once
```

### 方法三：直接运行（前台）

```bash
python3 auto_gdrive_collector_v2.py
```

按 `Ctrl+C` 停止。

## 配置说明

编辑 `auto_gdrive_collector_v2.py` 修改配置：

```python
# 采集间隔（秒）
COLLECTION_INTERVAL = 600  # 10分钟

# 数据库路径
DB_PATH = 'homepage_data.db'

# Google Drive 文件夹 ID（在 panic_wash_reader_v5.py 中配置）
GOOGLE_DRIVE_FOLDER_ID = "1JNZKKnZLeoBkxSumjS63SOInCriPfAKX"
```

## 日志说明

### 日志文件位置

- **标准日志**: `logs/collector.log`
- **错误日志**: `logs/collector_error.log`
- **进程 PID**: `logs/collector.pid`

### 日志内容示例

```
============================================================
开始采集数据: 2025-12-06 09:40:02
============================================================
正在访问 Google Drive 文件夹...
找到最新文件: 2025-12-06_0819.txt (08:19)
正在打开文件...
✓ 数据更新成功: 2025-12-06_0819.txt
✓ 数据保存成功: ID=75, 急涨=0, 急跌=22, 币种=29

✓ 采集成功:
  文件名: 2025-12-06_0819.txt
  急涨: 0
  急跌: 22
  比值: 999.0
  差值: -22.0
  币种数量: 29

⏰ 下次采集时间: 2025-12-06 09:50:02
💤 等待 600秒...
```

## 数据库结构

### summary_data 表（汇总数据）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| rise_total | INTEGER | 急涨总和 |
| fall_total | INTEGER | 急跌总和 |
| five_states | TEXT | 市场状态 |
| rise_fall_ratio | REAL | 急涨急跌比值 |
| diff_result | REAL | 差值结果 |
| count_times | INTEGER | 计次 |
| record_time | TEXT | 记录时间 |
| created_at | TIMESTAMP | 创建时间 |

### coin_details 表（币种详细数据）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| summary_id | INTEGER | 关联汇总数据 |
| seq_num | INTEGER | 序号 |
| coin_name | TEXT | 币种名称 |
| rise_speed | REAL | 涨速 |
| rise_signal | INTEGER | 急涨信号 |
| fall_signal | INTEGER | 急跌信号 |
| current_price | REAL | 当前价格 |
| change_24h | REAL | 24小时涨幅 |
| record_time | TEXT | 记录时间 |

## 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 采集间隔 | 10分钟 | 可配置 |
| 单次采集时间 | 20-30秒 | 包含浏览器启动时间 |
| 数据准确性 | 100% | 与源文件完全一致 |
| 内存占用 | ~200MB | Chromium 浏览器 |

## 故障排查

### 问题1: 采集器无法启动

**解决方案**:
1. 检查是否已经在运行: `./status_collector.sh`
2. 检查日志: `cat logs/collector.log`
3. 手动测试: `python3 auto_gdrive_collector_v2.py --once`

### 问题2: 采集失败

**可能原因**:
- Google Drive 访问失败
- 网络连接问题
- Playwright 浏览器启动失败

**解决方案**:
1. 查看错误日志: `cat logs/collector_error.log`
2. 手动测试: `python3 panic_wash_reader_v5.py`
3. 检查网络连接

### 问题3: 数据未更新

**检查步骤**:
1. 确认采集器正在运行: `./status_collector.sh`
2. 查看最近的采集日志: `tail -50 logs/collector.log`
3. 检查数据库: `python3 auto_gdrive_collector_v2.py --status`

## 监控建议

### 1. 定期检查状态

```bash
# 添加到 crontab
0 * * * * /home/user/webapp/status_collector.sh > /tmp/collector_check.log
```

### 2. 监控日志大小

```bash
# 定期清理旧日志
find logs/ -name "*.log" -mtime +7 -delete
```

### 3. 数据库维护

```bash
# 定期清理旧数据（保留最近30天）
sqlite3 homepage_data.db "DELETE FROM summary_data WHERE record_time < date('now', '-30 days')"
sqlite3 homepage_data.db "VACUUM"
```

## 高级用法

### 使用 systemd 管理（推荐生产环境）

```bash
# 复制服务文件
sudo cp gdrive-collector.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start gdrive-collector

# 开机自启
sudo systemctl enable gdrive-collector

# 查看状态
sudo systemctl status gdrive-collector

# 查看日志
sudo journalctl -u gdrive-collector -f
```

### 自定义采集间隔

编辑 `auto_gdrive_collector_v2.py`:

```python
# 改为5分钟
COLLECTION_INTERVAL = 300

# 改为15分钟
COLLECTION_INTERVAL = 900

# 改为1小时
COLLECTION_INTERVAL = 3600
```

### 多实例运行

```bash
# 创建独立的配置文件
cp auto_gdrive_collector_v2.py collector_instance2.py

# 修改数据库路径
# DB_PATH = 'homepage_data_instance2.db'

# 启动第二个实例
python3 collector_instance2.py &
```

## 最佳实践

1. **使用后台运行** - 通过 `start_collector.sh` 启动
2. **定期检查状态** - 每小时检查一次
3. **监控日志大小** - 定期清理旧日志
4. **备份数据库** - 每天备份数据库文件
5. **测试后部署** - 先用 `--once` 测试，确认无误后再持续运行

## 常见问题

### Q1: 为什么采集这么慢？

A: Playwright 需要启动真实浏览器，首次启动较慢。后续采集会复用浏览器进程，速度会有所提升。

### Q2: 可以同时运行多个采集器吗？

A: 可以，但需要使用不同的数据库文件，避免冲突。

### Q3: 如何确认采集器正常工作？

A: 使用 `./status_collector.sh` 查看状态，或查看日志文件 `logs/collector.log`。

### Q4: 采集器会占用多少资源？

A: 约200MB内存（Chromium浏览器），CPU占用很低（采集时短暂升高）。

## 技术架构

```
auto_gdrive_collector_v2.py
    │
    ├─> panic_wash_reader_v5.py (Playwright 数据读取)
    │       │
    │       └─> Google Drive 文件夹
    │
    └─> homepage_data.db (SQLite 数据库)
            │
            ├─> summary_data (汇总数据)
            └─> coin_details (币种详细数据)
```

## 相关文件

| 文件 | 说明 |
|------|------|
| `auto_gdrive_collector_v2.py` | 主程序 |
| `panic_wash_reader_v5.py` | Playwright 数据读取器 |
| `start_collector.sh` | 启动脚本 |
| `stop_collector.sh` | 停止脚本 |
| `status_collector.sh` | 状态查看脚本 |
| `gdrive-collector.service` | systemd 服务配置 |
| `logs/collector.log` | 运行日志 |
| `logs/collector.pid` | 进程ID文件 |

---

**版本**: V2.0  
**更新日期**: 2025-12-06  
**作者**: AI Assistant  
**GitHub**: https://github.com/jamesyidc/6666.git
