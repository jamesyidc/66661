# 使用说明 - Google Drive 当日文件夹最新txt文件查找器

## 🎯 功能说明

这个工具可以**自动**完成以下任务：

1. ✅ 自动判断当前的北京时间日期（例如：2025-12-02）
2. ✅ 在Google Drive主文件夹中查找对应日期的子文件夹
3. ✅ 列出该文件夹中的所有txt文件
4. ✅ 按修改时间排序，找出**最后更新的txt文件**
5. ✅ 显示文件的详细信息（名称、修改时间、大小、下载链接）

**您不需要每天手动修改任何代码或配置！** 脚本会自动根据当天日期查找对应的文件夹。

## 📋 一次性设置步骤

### 前置要求

- Python 3.7 或更高版本
- Google账号（拥有目标Google Drive文件夹的访问权限）

### 步骤1: 安装依赖

```bash
# 方式1: 使用快速开始脚本（推荐）
./quick_start.sh

# 方式2: 手动安装
pip3 install -r requirements.txt
```

### 步骤2: 设置Google Drive API访问权限

#### 2.1 创建Google Cloud项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击顶部的项目选择器
3. 点击"新建项目"
4. 输入项目名称（例如：`google-drive-finder`）
5. 点击"创建"

#### 2.2 启用Google Drive API

1. 在项目中，点击左侧菜单："APIs & Services" > "Library"
2. 搜索："Google Drive API"
3. 点击进入，然后点击"启用"

#### 2.3 创建Service Account

1. 点击左侧菜单："APIs & Services" > "Credentials"
2. 点击顶部的"Create Credentials" > "Service Account"
3. 填写信息：
   - **Service account name**: `google-drive-finder`（或任意名称）
   - **Service account description**: `用于自动查找Google Drive文件`
4. 点击"Create and Continue"
5. 跳过"Grant this service account access to project"（可选），点击"Continue"
6. 跳过"Grant users access to this service account"（可选），点击"Done"

#### 2.4 下载Service Account密钥

1. 在"Credentials"页面，找到刚创建的Service Account
2. 点击Service Account的邮箱地址（类似：`xxxxx@xxxxx.iam.gserviceaccount.com`）
3. 切换到"Keys"标签
4. 点击"Add Key" > "Create new key"
5. 选择"JSON"格式
6. 点击"Create"
7. JSON文件会自动下载到您的电脑

#### 2.5 配置凭证文件

1. 找到刚下载的JSON文件（通常在"下载"文件夹）
2. **重命名为：`credentials.json`**
3. **将文件移动到项目目录**（`/home/user/webapp/credentials.json`）

#### 2.6 共享Google Drive文件夹

这是**最关键**的一步！

1. 打开`credentials.json`文件
2. 找到`client_email`字段，复制邮箱地址（类似：`xxxxx@xxxxx.iam.gserviceaccount.com`）
3. 打开您的Google Drive文件夹：https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
4. 右键点击文件夹，选择"共享"（或点击文件夹名称旁的共享图标）
5. 在"添加用户和群组"框中，粘贴Service Account的邮箱地址
6. 权限设置为：**查看者**
7. **取消勾选"通知用户"**（Service Account不需要接收邮件）
8. 点击"共享"或"发送"

### 步骤3: 验证设置

运行设置向导来验证配置：

```bash
python3 setup_guide.py
```

如果看到以下输出，说明设置成功：

```
✅ 找到 credentials.json 文件
✅ 凭证文件格式正确
📧 Service Account邮箱: xxxxx@xxxxx.iam.gserviceaccount.com
🆔 项目ID: your-project-id
```

## 🚀 日常使用

设置完成后，每天只需运行一个命令：

```bash
python3 google_drive_finder.py
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

✅ 找到 3 个txt文件

================================================================================
文件列表 (按修改时间降序):
================================================================================

[1] 数据报告_2025-12-02_18-30.txt
    文件ID: xxxxxxxxxxxxx
    修改时间: 2025-12-02 18:30:45 (北京时间)
    创建时间: 2025-12-02 18:30:45 (北京时间)
    文件大小: 15.23 KB

[2] 日志_2025-12-02_15-20.txt
    文件ID: xxxxxxxxxxxxx
    修改时间: 2025-12-02 15:20:30 (北京时间)
    创建时间: 2025-12-02 15:20:30 (北京时间)
    文件大小: 8.45 KB

[3] 统计_2025-12-02_09-10.txt
    文件ID: xxxxxxxxxxxxx
    修改时间: 2025-12-02 09:10:15 (北京时间)
    创建时间: 2025-12-02 09:10:15 (北京时间)
    文件大小: 5.67 KB

================================================================================
🎯 最后更新的txt文件:
================================================================================
文件名: 数据报告_2025-12-02_18-30.txt
文件ID: xxxxxxxxxxxxx
修改时间: 2025-12-02 18:30:45 (北京时间)
文件链接: https://drive.google.com/file/d/{文件ID}/view
================================================================================
```

## 🔧 高级用法

### 修改主文件夹ID

如果您需要查找不同的Google Drive文件夹：

1. 打开 `google_drive_finder.py`
2. 找到第14行：`MAIN_FOLDER_ID = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"`
3. 替换为您的文件夹ID（从Google Drive URL中获取）

### 集成到自动化脚本

您可以将这个工具集成到cron任务或其他自动化流程中：

```bash
# 示例：每天早上9点自动运行
0 9 * * * cd /home/user/webapp && python3 google_drive_finder.py >> /var/log/drive_finder.log 2>&1
```

### 作为Python模块使用

```python
from google_drive_finder import get_beijing_date, find_latest_txt_file

# 获取今天的日期
today = get_beijing_date()
print(f"今天是: {today}")

# 查找最新文件
# ... (需要先创建service对象)
```

## ❓ 常见问题

### Q1: 提示"未找到凭证文件"？

**A**: 请检查：
- `credentials.json` 是否在项目根目录（`/home/user/webapp/`）
- 文件名是否完全正确（区分大小写）
- 文件是否是有效的JSON格式

### Q2: 提示"未找到今天的文件夹"？

**A**: 请检查：
- 文件夹名称格式必须是 `YYYY-MM-DD`（例如：`2025-12-02`）
- 文件夹确实存在于主文件夹中
- Service Account是否有访问权限（已共享文件夹）
- 日期是否正确（脚本使用北京时间）

### Q3: 提示"API错误"或权限错误？

**A**: 请检查：
1. Google Drive API是否已在Google Cloud Console中启用
2. Service Account的JSON凭证是否正确
3. 是否已将文件夹共享给Service Account的邮箱
4. 共享权限至少为"查看者"

### Q4: 文件夹中没有txt文件？

**A**: 脚本会提示"文件夹中没有找到txt文件"。请确认：
- 文件扩展名是否为 `.txt`（小写）
- 文件是否在今天的文件夹中（不是子文件夹）
- Service Account是否有查看文件的权限

### Q5: 时区不对？

**A**: 脚本默认使用北京时间（Asia/Shanghai，UTC+8）。如果需要修改时区：
1. 打开 `google_drive_finder.py`
2. 找到 `get_beijing_date()` 函数
3. 修改时区设置：`beijing_tz = pytz.timezone('Asia/Shanghai')`

### Q6: 如何获取文件内容？

**A**: 脚本目前只查找和显示文件信息。如果需要下载文件内容，可以：
1. 使用输出的文件链接在浏览器中打开
2. 修改脚本添加下载功能（使用Drive API的 `files().get_media()` 方法）

## 🔒 安全提示

1. **不要将 `credentials.json` 上传到公共代码仓库**
2. 已添加到 `.gitignore` 文件中
3. 定期轮换Service Account密钥
4. 仅授予必要的最小权限（查看者权限即可）
5. 定期检查哪些Service Account有访问权限

## 📞 技术支持

如果遇到问题：

1. 首先运行 `python3 setup_guide.py` 检查配置
2. 查看本文档的"常见问题"部分
3. 检查Google Cloud Console的API使用情况
4. 查看错误日志获取详细信息

## 📝 文件清单

- ✅ `google_drive_finder.py` - 主程序
- ✅ `setup_guide.py` - 设置向导
- ✅ `quick_start.sh` - 快速开始脚本
- ✅ `requirements.txt` - Python依赖
- ✅ `README.md` - 英文说明文档
- ✅ `USAGE_CN.md` - 中文使用说明（本文档）
- ✅ `.gitignore` - Git忽略配置

## 🎉 总结

完成一次性设置后，您只需：

```bash
python3 google_drive_finder.py
```

脚本会自动：
- ✅ 识别今天的日期（北京时间）
- ✅ 找到对应的文件夹
- ✅ 列出所有txt文件
- ✅ 显示最后更新的文件

**不需要每天修改任何东西！** 🎯
