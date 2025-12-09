# 加密货币数据监控面板

实时监控Google Drive中的加密货币数据，每10分钟自动更新。

## 🎯 功能特性

- ✅ 自动从Google Drive获取当日最新txt文件
- ✅ 解析并展示加密货币数据表格
- ✅ 每10分钟自动刷新数据
- ✅ 实时倒计时显示
- ✅ 颜色标识（绿色=上涨，红色=下跌）
- ✅ 顶部统计栏显示关键指标
- ✅ 响应式设计，支持手机和电脑

## 📋 数据来源

- **Google Drive文件夹**: `1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV`
- **文件命名格式**: `YYYY-MM-DD_HHMM.txt` (例如: `2025-12-02_1806.txt`)
- **更新频率**: 每10分钟自动获取最新数据

## 🚀 快速开始

### 前置要求

1. **Python 3.7+**
2. **Google Drive API凭证** (credentials.json)

### 步骤1: 安装依赖

```bash
pip3 install -r requirements.txt
```

### 步骤2: 配置Google Drive API

如果还没有 `credentials.json`，请运行：

```bash
python3 setup_guide.py
```

按照提示完成以下操作：
1. 创建Google Cloud项目
2. 启用Google Drive API
3. 创建Service Account
4. 下载JSON密钥并重命名为 `credentials.json`
5. 将Google Drive文件夹共享给Service Account邮箱

详细步骤请查看 `USAGE_CN.md`

### 步骤3: 启动服务器

#### 方式1: 使用启动脚本（推荐）

```bash
./start_dashboard.sh
```

#### 方式2: 直接启动

```bash
python3 crypto_server.py
```

### 步骤4: 访问页面

服务器启动后，打开浏览器访问：

```
http://localhost:5000
```

或从其他设备访问（需要知道服务器IP）：

```
http://YOUR_SERVER_IP:5000
```

## 📊 页面功能说明

### 顶部统计栏

显示关键市场指标：
- **急涨**: 急涨币种数量
- **急跌**: 急跌币种数量
- **状态**: 市场状态（震荡无序/趋势明显等）
- **比值**: 急涨/急跌比值
- **绿色数量**: 上涨币种数量
- **百分比**: 上涨币种占比
- **计次**: 统计计次
- **差值**: 差值指标

### 数据表格

显示每个加密货币的详细信息：
- **币名**: 币种符号（BTC, ETH等）
- **涨幅**: 当前涨跌幅（带颜色标识）
- **急涨/急跌**: 是否急涨急跌
- **更新时间**: 数据更新时间
- **历史高价**: 历史最高价格
- **高价时间**: 达到最高价的时间
- **跌幅**: 相对历史高价的跌幅
- **24小时**: 24小时涨跌幅
- **当前价格**: 实时价格
- **盘点占比/最低占比**: 其他指标

### 颜色标识

- 🟢 **绿色**: 涨幅 > 0.3%
- 🟡 **黄色**: 涨幅 >= 0.2%
- 🔴 **红色**: 跌幅 < -0.05%

### 自动刷新

- 页面右上角显示倒计时
- 每10分钟自动刷新数据
- 无需手动刷新页面

## 🔧 API接口

### 获取数据

```
GET /api/crypto-data
```

返回JSON格式：
```json
{
  "success": true,
  "data": [...],
  "stats": {...},
  "updateTime": "2025-12-02 18:06:42",
  "filename": "2025-12-02_1806.txt"
}
```

### 手动刷新

```
GET /api/refresh
```

强制从Google Drive获取最新数据。

## 📁 项目文件

```
.
├── crypto_dashboard.html      # 前端页面
├── crypto_server.py          # 后端服务器
├── start_dashboard.sh        # 启动脚本
├── credentials.json          # Google API凭证（需自己创建）
├── requirements.txt          # Python依赖
└── CRYPTO_DASHBOARD_README.md # 本文档
```

## ⚙️ 配置选项

### 修改刷新间隔

编辑 `crypto_server.py`，修改第29行：

```python
# 默认10分钟（600秒）
if (datetime.now() - cached_data['lastFetch']).total_seconds() > 600:
```

编辑 `crypto_dashboard.html`，修改JavaScript中的配置：

```javascript
const REFRESH_INTERVAL = 10 * 60 * 1000; // 10分钟，单位毫秒
```

### 修改监控的文件夹

编辑 `crypto_server.py`，修改第23行：

```python
MAIN_FOLDER_ID = "你的文件夹ID"
```

### 修改端口

编辑 `crypto_server.py`，修改第266行：

```python
port = 5000  # 改为其他端口
```

## 🔍 故障排查

### 问题1: 提示"未找到credentials.json"

**解决方案**:
1. 运行 `python3 setup_guide.py`
2. 按照提示创建Google Service Account
3. 下载JSON密钥文件并重命名为 `credentials.json`
4. 将文件放在项目根目录

### 问题2: 提示"未找到今天的文件夹"

**解决方案**:
1. 检查Google Drive中是否有今天日期的文件夹（格式：YYYY-MM-DD）
2. 确认Service Account有访问权限（已共享文件夹）
3. 检查系统时区是否为北京时间

### 问题3: 数据显示不正常

**解决方案**:
1. 检查txt文件格式是否正确
2. 访问 `/api/crypto-data` 查看原始数据
3. 查看服务器控制台输出的错误信息

### 问题4: 页面无法访问

**解决方案**:
1. 确认服务器已启动
2. 检查端口5000是否被占用
3. 尝试使用 `http://127.0.0.1:5000` 而不是 `localhost`
4. 检查防火墙设置

### 问题5: 自动刷新不工作

**解决方案**:
1. 检查浏览器控制台是否有JavaScript错误
2. 确认后端API可以正常访问
3. 检查网络连接

## 🎯 使用场景

### 场景1: 个人监控

在本地运行，实时监控加密货币市场变化。

```bash
./start_dashboard.sh
# 访问 http://localhost:5000
```

### 场景2: 团队共享

在服务器上运行，团队成员通过网络访问。

```bash
# 在服务器上启动
python3 crypto_server.py

# 团队成员访问
http://服务器IP:5000
```

### 场景3: 后台运行

使用screen或nohup在后台持续运行。

```bash
# 使用screen
screen -S crypto
python3 crypto_server.py
# 按 Ctrl+A+D 脱离screen

# 使用nohup
nohup python3 crypto_server.py > crypto.log 2>&1 &
```

### 场景4: 系统服务

配置为系统服务，开机自动启动。

创建systemd服务文件 `/etc/systemd/system/crypto-dashboard.service`:

```ini
[Unit]
Description=Crypto Dashboard Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/webapp
ExecStart=/usr/bin/python3 /home/user/webapp/crypto_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable crypto-dashboard
sudo systemctl start crypto-dashboard
```

## 📱 移动端访问

页面支持响应式设计，可以在手机上访问：

1. 确保手机和服务器在同一网络
2. 获取服务器IP地址
3. 在手机浏览器中访问 `http://服务器IP:5000`
4. 建议将页面添加到主屏幕，方便快速访问

## 🔒 安全建议

1. **不要将credentials.json提交到Git**
2. **使用防火墙限制访问**
3. **考虑添加身份验证**
4. **使用HTTPS（生产环境）**
5. **定期更新依赖包**

## 📈 未来改进

- [ ] 添加用户登录功能
- [ ] 支持多个数据源
- [ ] 添加数据图表展示
- [ ] 支持数据导出（CSV/Excel）
- [ ] 添加价格预警功能
- [ ] 支持WebSocket实时推送
- [ ] 添加历史数据查询
- [ ] 移动端App

## 📞 技术支持

如果遇到问题：
1. 查看本文档的"故障排查"部分
2. 查看服务器控制台输出
3. 检查浏览器开发者工具的Console
4. 查看 `USAGE_CN.md` 了解Google Drive API设置

## 📄 相关文档

- `USAGE_CN.md` - Google Drive API详细设置指南
- `PROJECT_SUMMARY.md` - 项目总体说明
- `QUICK_REFERENCE.md` - 快速参考
- `UPDATE_LOG.md` - 更新日志

---

**最后更新**: 2025-12-02  
**版本**: 1.0.0  
**状态**: ✅ 生产可用
