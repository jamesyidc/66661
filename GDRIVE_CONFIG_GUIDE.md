# Google Drive API 配置完整指南

## 📋 概述

本指南将帮助你配置 Google Drive API，使系统能够自动读取你 Google Drive 中的数据文件。

**配置后效果：**
- ✅ 系统自动读取每天文件夹中最新的 TXT 文件
- ✅ 每 10 分钟自动更新一次数据
- ✅ 无需手动上传或更新数据
- ✅ 支持多种文件名格式（`2025-12-02_2238.txt` 或 `信号.txt`）

---

## 🚀 快速开始（5 步完成）

### 步骤 1：创建 Google Cloud 项目

1. 访问 Google Cloud Console：https://console.cloud.google.com/
2. 点击顶部的项目选择器
3. 点击 "NEW PROJECT"（新建项目）
4. 输入项目名称：`crypto-monitor`（或任意名称）
5. 点击 "CREATE"

### 步骤 2：启用 Google Drive API

1. 在项目仪表板，点击左侧菜单 "APIs & Services" > "Library"
2. 搜索 "Google Drive API"
3. 点击 "Google Drive API"
4. 点击 "ENABLE"（启用）
5. 等待几秒钟，直到显示 "API enabled"

### 步骤 3：创建服务账号

1. 点击左侧菜单 "APIs & Services" > "Credentials"
2. 点击顶部 "+ CREATE CREDENTIALS"
3. 选择 "Service account"（服务账号）
4. 填写信息：
   - Service account name: `crypto-monitor-reader`
   - Service account ID: 自动生成
   - Description: `用于读取加密货币监控数据`
5. 点击 "CREATE AND CONTINUE"
6. 在 "Grant this service account access to project" 页面：
   - 无需选择角色，直接点击 "CONTINUE"
7. 在 "Grant users access to this service account" 页面：
   - 无需填写，直接点击 "DONE"

### 步骤 4：下载 JSON 密钥文件

1. 在 Credentials 页面，找到刚创建的服务账号
2. 点击服务账号邮箱（类似 `crypto-monitor-reader@xxx.iam.gserviceaccount.com`）
3. 切换到 "KEYS" 标签
4. 点击 "ADD KEY" > "Create new key"
5. 选择 "JSON" 格式
6. 点击 "CREATE"
7. JSON 文件会自动下载到你的电脑
8. **将下载的文件重命名为 `gdrive_credentials.json`**

### 步骤 5：配置文件夹共享权限

1. 打开刚下载的 `gdrive_credentials.json` 文件（用文本编辑器打开）
2. 找到 `"client_email"` 字段，复制邮箱地址（类似 `xxx@xxx.iam.gserviceaccount.com`）
3. 打开你的 Google Drive 共享文件夹：
   ```
   https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
   ```
4. 点击文件夹右上角的 "共享" 图标（人像图标）
5. 在 "添加用户和组" 输入框中，粘贴服务账号邮箱
6. 权限设置为 "查看者" (Viewer)
7. **取消勾选** "通知用户"（服务账号不需要通知）
8. 点击 "共享" 或 "完成"

---

## 📂 上传凭据文件到服务器

你有两种方式上传 `gdrive_credentials.json` 文件：

### 方法 1：使用文件上传界面（推荐）

如果你的环境支持文件上传，直接上传 `gdrive_credentials.json` 到 `/home/user/webapp/` 目录。

### 方法 2：复制粘贴内容

1. 打开 `gdrive_credentials.json` 文件
2. 复制全部内容
3. 告诉我，我会帮你创建文件

---

## ✅ 验证配置

上传完凭据文件后，运行配置向导验证：

```bash
cd /home/user/webapp
python3 setup_gdrive.py
```

配置向导会：
- ✅ 检查凭据文件是否存在
- ✅ 验证文件格式是否正确
- ✅ 测试 Google Drive 连接
- ✅ 查找今天的文件夹
- ✅ 读取最新的 TXT 文件

---

## 🔧 故障排查

### 问题 1：找不到凭据文件
```
❌ 未找到凭据文件: /home/user/webapp/gdrive_credentials.json
```

**解决方案：**
- 确保文件名是 `gdrive_credentials.json`（全小写）
- 确保文件在 `/home/user/webapp/` 目录下
- 检查文件权限：`ls -la gdrive_credentials.json`

### 问题 2：权限被拒绝
```
❌ 未找到今天的文件夹: 2025-12-02
```

**解决方案：**
- 确保服务账号邮箱已添加到 Google Drive 文件夹共享列表
- 权限至少是 "查看者" (Viewer)
- 等待几分钟让权限生效

### 问题 3：未找到 TXT 文件
```
❌ 未找到 TXT 文件
```

**解决方案：**
- 确保今天的文件夹中有 `.txt` 文件
- 检查文件扩展名是否正确（`.txt` 而不是 `.TXT`）
- 确认文件没有被删除或移动

### 问题 4：API 未启用
```
❌ Google Drive API has not been used in project xxx before or it is disabled
```

**解决方案：**
- 返回 Google Cloud Console
- 确保已启用 Google Drive API
- 等待几分钟让 API 生效

---

## 📖 文件格式说明

系统支持以下文件格式：

### 信号数据文件
- 文件名：`2025-12-02_2238.txt` 或 `信号.txt`
- 格式：`做空信号|变化|做多信号|变化|时间`
- 示例：`146|0|0|0|2025-12-02 22:38:00`

### 恐慌清洗数据文件
- 文件名：`恐慌清洗.txt`
- 格式：`指标|评级-区间-人数-金额-持仓量-时间`
- 示例：`10.68-绿|5-多头主升区间-99305-2.26-92.18-2025-12-02 22:38:00`

---

## 🎯 常见问题

**Q: 需要付费吗？**
A: Google Drive API 有免费额度，日常使用完全够用（每天 1,000 次请求）。

**Q: 安全吗？**
A: 服务账号只有读取权限，无法修改或删除你的文件。

**Q: 多久更新一次？**
A: 系统每 10 分钟自动读取一次最新数据。

**Q: 支持哪些文件名？**
A: 系统会自动查找文件夹中最新修改的 `.txt` 文件，支持任意文件名。

**Q: 如果今天没有数据怎么办？**
A: 系统会回退到演示数据，不会崩溃。

---

## 📞 需要帮助？

如果配置过程中遇到问题：
1. 运行配置向导查看详细错误信息：`python3 setup_gdrive.py`
2. 检查服务器日志：`tail -50 server.log`
3. 确认文件夹 ID：`1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV`

---

## ✨ 配置完成后

重启服务器以应用配置：

```bash
cd /home/user/webapp
pkill -f crypto_server_demo
python3 crypto_server_demo.py
```

访问页面查看实时数据：
- 主页：https://5001-ivx1gqv2svtq7f2kvor6q-b32ec7bb.sandbox.novita.ai/
- 信号监控：.../signal
- 恐慌指数：.../panic

享受自动化的数据更新！🎉
