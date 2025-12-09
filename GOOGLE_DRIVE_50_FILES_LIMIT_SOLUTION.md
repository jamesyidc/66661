# Google Drive 50文件限制问题 - 解决方案

## 问题现状

✅ **确认问题**：
- Google Drive 文件夹中有超过50个文件（实际有至少60个文件，到10:00）
- 网页接口（包括Playwright）只显示前50个文件（按名称排序：0006-0819）
- 无法通过网页接口访问后面的文件（0829-1000）

## 已尝试的方法（全部失败）

1. ❌ **Playwright 滚动加载** - 无效，仍然只显示50个
2. ❌ **gdown 库** - 硬编码50文件限制
3. ❌ **URL参数控制排序** - 无效
4. ❌ **搜索功能** - 搜索框无法使用
5. ❌ **点击排序按钮** - 无法定位到排序控件

## ✅ 有效解决方案

### 方案1：使用 Google Drive API（推荐）

需要配置 OAuth 2.0 认证：

1. **创建 Google Cloud 项目**：
   - 访问 https://console.cloud.google.com/
   - 创建新项目或选择现有项目

2. **启用 Google Drive API**：
   - 在项目中启用 Google Drive API

3. **创建 OAuth 2.0 凭证**：
   - 创建 OAuth 2.0 客户端 ID
   - 下载 `credentials.json` 文件
   - 将文件放到 `/home/user/webapp/` 目录

4. **运行认证流程**：
   ```bash
   python3 use_real_gdrive_api.py
   ```

### 方案2：手动定期清理旧文件（临时方案）

定期删除旧文件，保持文件夹内文件数量在50以下：

```bash
# 删除今天早上6点之前的文件
# 例如只保留最近4小时的文件
```

### 方案3：按小时创建子文件夹

修改上传程序，按小时创建子文件夹：
```
2025-12-06/
  ├─ 00-06/  (00:00-06:00的文件)
  ├─ 06-12/  (06:00-12:00的文件)
  └─ 12-18/  (12:00-18:00的文件)
```

## 当前状态

|项目|值|
|---|---|
|Google Drive最新文件|2025-12-06_1000.txt (10:00)|
|程序能访问到的最新文件|2025-12-06_0819.txt (08:19)|
|无法访问的文件|0829, 0839, 0849, 0859, 0909, 0919, 0929, 0939, 0949, 1000|
|原因|网页接口50文件显示限制|

## 立即行动

### 临时方案：直接读取最新10:00文件

由于您能在Google Drive网页看到最新文件，最简单的方法是：

1. **手动下载** `2025-12-06_1000.txt` 文件
2. 上传到服务器的 `/home/user/webapp/` 目录
3. 系统会自动读取并更新

或者：

1. **提供文件的直接下载链接或文件ID**
2. 我可以直接通过文件ID获取内容

## 代码修改建议

如果配置了Google Drive API认证，可以修改 `panic_wash_reader_v5.py` 使用API而不是网页爬虫：

```python
# 使用 Google Drive API
from googleapiclient.discovery import build

service = build('drive', 'v3', credentials=creds)
results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    pageSize=100,
    orderBy='modifiedTime desc',  # 按修改时间倒序
    fields="files(id, name, modifiedTime)"
).execute()

files = results.get('files', [])
# 获取最新文件
latest_file = files[0]
```

## 总结

**问题根本原因**：Google Drive 网页接口对匿名/未认证访问有50个文件的显示限制。

**最佳解决方案**：配置 Google Drive API OAuth认证，使用API访问所有文件。

**临时解决方案**：
1. 手动上传最新文件
2. 或提供文件ID/直接链接
3. 定期清理旧文件

---
文档创建时间: 2025-12-06 10:07
