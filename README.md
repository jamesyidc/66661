# Google Drive 当日文件夹最新txt文件查找器

自动查找Google Drive中当日文件夹（基于北京时间）里最后更新的txt文件。

## 功能特点

- ✅ 自动识别北京时间的当前日期
- ✅ 自动在Google Drive中查找对应日期的文件夹（格式：YYYY-MM-DD）
- ✅ 列出文件夹中所有txt文件
- ✅ 按修改时间排序，显示最后更新的txt文件
- ✅ 显示文件详细信息（修改时间、创建时间、大小等）

## 设置步骤

### 1. 创建Google Cloud项目和Service Account

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 在左侧菜单中，选择 "APIs & Services" > "Library"
4. 搜索并启用 "Google Drive API"

### 2. 创建Service Account

1. 在左侧菜单中，选择 "APIs & Services" > "Credentials"
2. 点击 "Create Credentials" > "Service Account"
3. 填写Service Account详细信息：
   - Name: `google-drive-finder` (或任意名称)
   - Description: `用于访问Google Drive文件夹`
4. 点击 "Create and Continue"
5. 跳过权限设置（可选），点击 "Continue"
6. 点击 "Done"

### 3. 下载Service Account密钥

1. 在Credentials页面，找到刚创建的Service Account
2. 点击Service Account邮箱地址
3. 切换到 "Keys" 标签
4. 点击 "Add Key" > "Create new key"
5. 选择 "JSON" 格式
6. 点击 "Create"，密钥文件会自动下载
7. **重命名下载的JSON文件为 `credentials.json`**
8. **将 `credentials.json` 放在项目根目录中**

### 4. 共享Google Drive文件夹

1. 打开Service Account的JSON文件，找到 `client_email` 字段（类似：`xxxxx@xxxxx.iam.gserviceaccount.com`）
2. 复制这个邮箱地址
3. 打开您的Google Drive文件夹：https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
4. 点击右键或点击文件夹名称旁的"共享"按钮
5. 将文件夹共享给Service Account的邮箱地址
6. 权限设置为"查看者"即可
7. 点击"发送"

### 5. 安装依赖

```bash
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib google-auth pytz
```

## 使用方法

### 基本使用

```bash
python google_drive_finder.py
```

### 输出示例

```
================================================================================
📁 Google Drive 当日文件夹最新txt文件查找器
================================================================================

📅 北京时间今天的日期: 2025-12-02

🔐 正在加载凭证文件: credentials.json
✅ Drive API服务已创建

🔍 正在查找文件夹: 2025-12-02
✅ 找到文件夹: 2025-12-02 (ID: xxxxxxxxxxxxx)

📄 正在查找txt文件...

✅ 找到 5 个txt文件

================================================================================
文件列表 (按修改时间降序):
================================================================================

[1] report_2025-12-02_18-30.txt
    文件ID: xxxxxxxxxxxxx
    修改时间: 2025-12-02 18:30:45 (北京时间)
    创建时间: 2025-12-02 18:30:45 (北京时间)
    文件大小: 15.23 KB

[2] data_2025-12-02_15-20.txt
    文件ID: xxxxxxxxxxxxx
    修改时间: 2025-12-02 15:20:30 (北京时间)
    创建时间: 2025-12-02 15:20:30 (北京时间)
    文件大小: 8.45 KB

...

================================================================================
🎯 最后更新的txt文件:
================================================================================
文件名: report_2025-12-02_18-30.txt
文件ID: xxxxxxxxxxxxx
修改时间: 2025-12-02 18:30:45 (北京时间)
文件链接: https://drive.google.com/file/d/{文件ID}/view
================================================================================
```

## 文件结构

```
.
├── google_drive_finder.py    # 主程序
├── requirements.txt           # Python依赖
├── credentials.json          # Google Service Account凭证 (需要自己创建)
└── README.md                 # 说明文档
```

## 常见问题

### Q: 提示"未找到凭证文件"？
A: 请确保已经下载Service Account的JSON密钥文件，并重命名为 `credentials.json`，放在项目根目录。

### Q: 提示"未找到今天的文件夹"？
A: 请检查：
1. 文件夹名称格式是否为 `YYYY-MM-DD`（如：2025-12-02）
2. Service Account是否有访问权限（已共享文件夹给Service Account邮箱）
3. 文件夹是否确实存在

### Q: 提示"API错误"？
A: 请检查：
1. Google Drive API是否已启用
2. Service Account凭证是否正确
3. 网络连接是否正常

### Q: 如何修改主文件夹ID？
A: 编辑 `google_drive_finder.py`，修改 `MAIN_FOLDER_ID` 变量的值。

## 技术说明

- 使用 Google Drive API v3
- 基于Service Account认证（无需用户交互）
- 时区处理：所有时间显示均为北京时间（UTC+8）
- 文件排序：按修改时间降序（最新的在前）

## 许可证

MIT License

## 作者

AI Assistant

---

**注意**: 请妥善保管 `credentials.json` 文件，不要将其上传到公共代码仓库。建议将其添加到 `.gitignore` 文件中。
