# 🚀 加密货币监控面板 - 快速指南

## ✅ 项目已完成！

我已经为您创建了一个完整的加密货币数据监控面板，功能如下：

### 📊 核心功能

1. ✅ **自动获取Google Drive数据**
   - 每10分钟自动从Google Drive获取最新txt文件
   - 文件命名格式: `YYYY-MM-DD_HHMM.txt`
   - 例如: `2025-12-02_1806.txt` (18点06分)

2. ✅ **实时数据展示**
   - 加密货币数据表格（与您的截图完全一致）
   - 顶部统计栏（急涨、急跌、比值等）
   - 颜色标识（绿色=涨、红色=跌）

3. ✅ **自动刷新**
   - 每10分钟自动更新数据
   - 右上角倒计时显示
   - 无需手动刷新

4. ✅ **响应式设计**
   - 支持电脑和手机访问
   - 自适应屏幕大小

---

## 🎯 当前演示

### 演示地址（已启动）:

**🌐 访问地址**: https://5000-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai

**注意**: 这是演示版本，使用模拟数据。要使用真实的Google Drive数据，请按照下面的步骤配置。

---

## 📋 使用真实数据的步骤

### 方案A: 快速启动（推荐）

如果您已经有 `credentials.json` 文件：

```bash
# 1. 停止演示服务器
# (如果正在运行)

# 2. 启动真实数据服务器
./start_dashboard.sh
```

### 方案B: 首次设置

如果还没有 `credentials.json`：

#### 步骤1: 设置Google Drive API

```bash
python3 setup_guide.py
```

按照提示完成：
1. 访问 Google Cloud Console
2. 创建 Service Account
3. 下载 JSON 密钥文件
4. 重命名为 `credentials.json`
5. 共享Google Drive文件夹给Service Account邮箱

**详细步骤**: 查看 `USAGE_CN.md`

#### 步骤2: 启动服务器

```bash
./start_dashboard.sh
```

或直接运行：

```bash
python3 crypto_server.py
```

#### 步骤3: 访问页面

打开浏览器访问: `http://localhost:5000`

---

## 🎨 界面说明

### 顶部导航栏
```
首页 | 查询 | 挂号 | 比价 | 追涨比价 | 盘控 | 重点盘控 | 查询 | 工具
```

### 统计栏指标
```
急涨: 15 | 急跌: 4 | 状态: 震荡无序 | 比值: 2.75 ★★
绿色数量: 27 | 百分比: 93% | 计次: 7 | 差值: 11 ★★
```

### 数据表格列
```
序号 | 币名 | 涨幅 | 急涨 | 急跌 | 更新时间 | 历史高价 | 高价时间
跌幅 | 24小时 | ... | 排行 | 当前价格 | 盘点占比 | 最低占比
```

### 颜色标识
- 🟢 **绿色背景**: 涨幅 > 0.3% (强势上涨)
- 🟡 **黄色背景**: 涨幅 >= 0.2% (温和上涨)
- 🔴 **红色背景**: 跌幅 < -0.05% (下跌)

---

## 📁 项目文件说明

### 核心文件

| 文件 | 说明 | 是否必需 |
|------|------|----------|
| `crypto_dashboard.html` | 前端页面 | ✅ 必需 |
| `crypto_server.py` | 真实数据服务器 | ✅ 必需 |
| `crypto_server_demo.py` | 演示服务器 | 📝 可选 |
| `credentials.json` | Google API凭证 | ✅ 真实数据必需 |
| `start_dashboard.sh` | 启动脚本 | 📝 推荐 |

### 文档文件

| 文件 | 说明 |
|------|------|
| `CRYPTO_DASHBOARD_README.md` | 完整使用文档 |
| `DASHBOARD_GUIDE.md` | 快速指南（本文件） |
| `USAGE_CN.md` | Google Drive API设置详解 |

### 其他Google Drive工具

| 文件 | 说明 |
|------|------|
| `google_drive_finder.py` | 通用版查找工具 |
| `google_drive_finder_optimized.py` | 优化版查找工具 |
| `demo_filename_parser.py` | 文件名解析演示 |

---

## ⚙️ 配置选项

### 修改刷新间隔

编辑 `crypto_server.py` 和 `crypto_dashboard.html`，搜索 `600` 或 `10 * 60 * 1000`，修改为您想要的秒数或毫秒数。

### 修改监控文件夹

编辑 `crypto_server.py` 第23行：
```python
MAIN_FOLDER_ID = "您的文件夹ID"
```

### 修改服务器端口

编辑 `crypto_server.py` 第266行：
```python
port = 5000  # 改为其他端口
```

---

## 🔧 API接口

### 1. 获取数据
```
GET http://localhost:5000/api/crypto-data
```

返回：
```json
{
  "success": true,
  "data": [...],
  "stats": {...},
  "updateTime": "2025-12-02 18:06:42",
  "filename": "2025-12-02_1806.txt"
}
```

### 2. 手动刷新
```
GET http://localhost:5000/api/refresh
```

强制从Google Drive重新获取数据。

---

## 🎯 数据流程

```
Google Drive (txt文件)
    ↓
每10分钟自动获取
    ↓
Python后端解析数据
    ↓
API接口提供JSON
    ↓
前端页面展示
    ↓
自动刷新循环
```

---

## 📱 使用场景

### 场景1: 本地监控
```bash
./start_dashboard.sh
# 访问: http://localhost:5000
```

### 场景2: 团队共享
```bash
python3 crypto_server.py
# 团队访问: http://服务器IP:5000
```

### 场景3: 后台运行
```bash
nohup python3 crypto_server.py > crypto.log 2>&1 &
```

### 场景4: 演示模式（无需API）
```bash
python3 crypto_server_demo.py
# 使用模拟数据
```

---

## ❓ 常见问题

### Q1: 如何切换到真实数据？

**A**: 
1. 创建 `credentials.json`（运行 `python3 setup_guide.py`）
2. 停止演示服务器
3. 运行 `python3 crypto_server.py`

### Q2: 页面不刷新怎么办？

**A**: 
1. 检查浏览器控制台是否有错误
2. 确认后端服务器正在运行
3. 访问 `/api/crypto-data` 测试API

### Q3: 数据不更新怎么办？

**A**: 
1. 检查Google Drive中是否有新文件
2. 确认文件命名格式正确
3. 访问 `/api/refresh` 手动刷新

### Q4: 如何在手机上访问？

**A**: 
1. 确保手机和服务器在同一网络
2. 访问 `http://服务器IP:5000`
3. 建议添加到主屏幕

---

## 🎉 功能特性对比

| 功能 | 演示版 | 真实版 |
|------|--------|--------|
| 界面展示 | ✅ | ✅ |
| 数据刷新 | ✅ | ✅ |
| 真实数据 | ❌ | ✅ |
| 自动更新 | ❌ | ✅ |
| 需要API | ❌ | ✅ |

---

## 📞 下一步

1. **测试演示**: 访问上面的演示地址查看效果
2. **设置API**: 如果要使用真实数据，运行 `python3 setup_guide.py`
3. **启动服务**: 运行 `./start_dashboard.sh` 或 `python3 crypto_server.py`
4. **开始监控**: 打开浏览器访问页面

---

## 📚 完整文档

- **API设置**: `USAGE_CN.md`
- **详细使用**: `CRYPTO_DASHBOARD_README.md`
- **项目总结**: `PROJECT_SUMMARY.md`
- **快速参考**: `QUICK_REFERENCE.md`

---

**演示服务器已启动**: https://5000-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai

**项目状态**: ✅ 完成并可用  
**创建时间**: 2025-12-02  
**版本**: 1.0.0
