# 📊 系统当前状态报告

**更新时间：** 2025-12-02  
**版本：** v7.20

---

## ✅ 已完成的功能

### 1. 币种顺序修复 (v7.18)
- ✅ 币种按固定顺序显示：BTC, ETH, XRP, BNB, SOL...
- ✅ 数据库添加 `index_order` 字段记录原始顺序
- ✅ 查询时按 `index_order` 排序，保证顺序稳定

### 2. Google Drive 配置支持 (v7.19)
- ✅ 更新文件夹 ID 为你的文件夹：`1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV`
- ✅ 创建交互式配置向导：`setup_gdrive.py`
- ✅ 创建详细配置文档：`GDRIVE_CONFIG_GUIDE.md`
- ✅ 支持自动查找最新 TXT 文件

### 3. 智能文件名解析 (v7.20)
- ✅ 识别时间戳格式：`2025-12-02_2238.txt`
- ✅ 按文件名中的时间戳排序（最新优先）
- ✅ 支持北京时间
- ✅ 详细的日志输出
- ✅ 回退机制（支持 `信号.txt` 等传统文件名）

---

## 🔄 数据读取流程

```
当前流程（未配置 Google Drive API）：
┌─────────────────────┐
│  使用演示数据       │
│  (DEMO_DATA)        │
│  更新时间: 18:06:42 │
└─────────────────────┘

配置 Google Drive API 后的流程：
┌────────────────────────────────────────────────────┐
│ 1. 按北京时间获取今天日期（如：2025-12-02）       │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ 2. 在 Google Drive 中查找日期文件夹               │
│    文件夹 ID: 1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV   │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ 3. 查找文件夹中所有 .txt 文件                     │
│    - 2025-12-02_2238.txt                          │
│    - 2025-12-02_2228.txt                          │
│    - 2025-12-02_2218.txt                          │
│    - ...                                          │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ 4. 按文件名时间戳排序，选择最新的文件             │
│    → 2025-12-02_2238.txt (22:38)                  │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ 5. 下载并解析文件内容                             │
│    格式：做空|变化|做多|变化|时间                  │
│    示例：146|0|0|0|2025-12-02 22:38:00            │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ 6. 保存到数据库并展示在网页                       │
│    - 主页：最新币种数据                           │
│    - 信号页：做空=146, 做多=0                     │
│    - 恐慌页：恐慌指标数据                         │
└────────────────────────────────────────────────────┘
```

---

## ⚠️ 当前问题

### 主要问题：缺少 Google Drive API 凭据

**症状：**
- ❌ 数据更新时间停留在 `2025-12-02 18:06:42`
- ❌ 显示的是演示数据，不是 Google Drive 中的实时数据
- ❌ 无法自动读取最新的 `2025-12-02_2238.txt`

**原因：**
- 缺少 `gdrive_credentials.json` 文件
- 系统无法访问 Google Drive
- 自动回退到演示数据模式

**解决方案：**
配置 Google Drive API（详见下一节）

---

## 🚀 如何配置 Google Drive API

### 快速步骤

1. **创建 Google Cloud 项目**
   - 访问：https://console.cloud.google.com/
   - 创建新项目（如 `crypto-monitor`）

2. **启用 Google Drive API**
   - APIs & Services → Library
   - 搜索 "Google Drive API"
   - 点击 Enable

3. **创建服务账号**
   - APIs & Services → Credentials
   - Create Credentials → Service account
   - 名称：`crypto-monitor-reader`

4. **下载 JSON 密钥**
   - 点击服务账号
   - Keys → Add Key → Create new key
   - 选择 JSON 格式
   - 下载后重命名为：`gdrive_credentials.json`

5. **配置共享权限**
   - 打开 JSON 文件，找到 `client_email`
   - 复制服务账号邮箱（如 `xxx@xxx.iam.gserviceaccount.com`）
   - 打开 Google Drive 文件夹：
     ```
     https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
     ```
   - 点击 "共享"，添加服务账号邮箱
   - 权限设置为 "查看者"

6. **上传凭据文件**
   - 方法1：直接上传到 `/home/user/webapp/gdrive_credentials.json`
   - 方法2：复制文件内容告诉我，我帮你创建

7. **验证配置**
   ```bash
   cd /home/user/webapp
   python3 setup_gdrive.py
   ```

### 详细文档

完整的图文教程请查看：
- `/home/user/webapp/GDRIVE_CONFIG_GUIDE.md`

---

## 🧪 测试工具

### 1. 文件解析测试
```bash
cd /home/user/webapp
python3 test_file_parsing.py
```

**测试内容：**
- 模拟 9 个 TXT 文件
- 验证时间戳解析逻辑
- 验证排序算法
- 验证内容解析

**测试结果：**
```
✅ 能正确识别 2025-12-02_2238.txt 格式
✅ 能从9个文件中选择最新的（22:38）
✅ 能正确解析文件内容（做空=146, 做多=0）
```

### 2. Google Drive 配置向导
```bash
cd /home/user/webapp
python3 setup_gdrive.py
```

**功能：**
- ✅ 检查凭据文件是否存在
- ✅ 验证文件格式
- ✅ 测试 Google Drive 连接
- ✅ 查找今天的文件夹
- ✅ 读取最新 TXT 文件
- ✅ 显示文件内容预览

---

## 📁 文件结构

### 配置文件
```
/home/user/webapp/
├── gdrive_credentials.json        # ⚠️ 需要上传（当前不存在）
├── GDRIVE_CONFIG_GUIDE.md         # 配置指南
├── GDRIVE_SETUP.md                # 详细步骤
└── CURRENT_STATUS.md              # 本文档
```

### 核心代码
```
/home/user/webapp/
├── crypto_server_demo.py          # 主服务器
├── gdrive_reader.py               # Google Drive 读取器
├── monitor_data_reader.py         # 监控数据读取器
├── crypto_database.py             # 数据库操作
└── setup_gdrive.py                # 配置向导
```

### 测试工具
```
/home/user/webapp/
└── test_file_parsing.py           # 文件解析测试
```

---

## 🔗 访问链接

- **主页：** https://5001-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/
- **信号监控：** .../signal
- **恐慌指数：** .../panic

---

## 📊 数据统计

### 当前数据（演示数据）
- 做空信号：146
- 做多信号：0
- 更新时间：2025-12-02 18:06:42
- 币种数量：29
- 币种顺序：✅ 正确（BTC, ETH, XRP...）

### 配置后预期数据
- 做空信号：实时从 Google Drive 读取
- 做多信号：实时从 Google Drive 读取
- 更新时间：实时（如 22:38:00）
- 更新频率：每 10 分钟自动更新
- 数据来源：Google Drive 中最新的 TXT 文件

---

## 🎯 下一步

### 立即执行
1. ✅ 阅读配置文档：`GDRIVE_CONFIG_GUIDE.md`
2. ⏳ 创建 Google Cloud 项目
3. ⏳ 启用 Google Drive API
4. ⏳ 创建服务账号并下载 JSON
5. ⏳ 配置共享权限
6. ⏳ 上传 `gdrive_credentials.json`
7. ⏳ 运行 `setup_gdrive.py` 验证
8. ⏳ 重启服务器

### 验证成功的标志
- ✅ 配置向导显示 "配置成功"
- ✅ 能找到今天的日期文件夹
- ✅ 能读取最新的 TXT 文件
- ✅ 主页显示实时更新时间（如 22:38）
- ✅ 数据每 10 分钟自动更新

---

## 💬 需要帮助？

如果你：
- ✅ 已经有 `gdrive_credentials.json` 文件 → 直接给我文件内容
- ⏳ 还在配置过程中 → 告诉我卡在哪一步
- ❓ 遇到错误 → 发送错误信息给我

我会立即帮你解决！
