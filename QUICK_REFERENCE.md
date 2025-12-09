# 快速参考卡 🚀

## 核心命令

### 每天使用（只需这一条命令！）
```bash
python3 google_drive_finder.py
```

### 首次设置
```bash
# 1. 安装依赖
pip3 install -r requirements.txt

# 2. 运行设置向导
python3 setup_guide.py

# 3. 按向导提示创建 credentials.json

# 4. 运行主程序
python3 google_drive_finder.py
```

---

## 文件说明

| 文件 | 用途 | 必需? |
|------|------|-------|
| `google_drive_finder.py` | 主程序 | ✅ 是 |
| `credentials.json` | API凭证 | ✅ 是（需自己创建） |
| `requirements.txt` | Python依赖 | ✅ 是 |
| `setup_guide.py` | 设置向导 | 📝 建议使用 |
| `README.md` | 英文文档 | 📖 参考 |
| `USAGE_CN.md` | 中文详细说明 | 📖 参考 |
| `PROJECT_SUMMARY.md` | 项目总结 | 📖 参考 |
| `quick_start.sh` | 快速开始 | 🚀 可选 |

---

## 关键信息

### Google Drive 主文件夹ID
```
1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
```

### 文件夹命名格式
```
YYYY-MM-DD
例如：2025-12-02
```

### 时区设置
```
北京时间 (Asia/Shanghai, UTC+8)
```

---

## 常见问题速查

### ❌ 未找到凭证文件
```bash
# 检查文件是否存在
ls -la credentials.json

# 如果不存在，运行设置向导
python3 setup_guide.py
```

### ❌ 未找到今天的文件夹
**原因**:
1. 文件夹尚未创建
2. Service Account无权限（未共享）
3. 文件夹名称格式错误

**解决**: 检查Google Drive中是否有今天日期的文件夹

### ❌ API错误
**检查**:
1. Google Drive API是否启用
2. credentials.json是否正确
3. 网络连接是否正常
4. 文件夹是否已共享给Service Account

---

## 输出解读

### 成功输出
```
🎯 最后更新的txt文件:
文件名: 数据报告_18-30.txt
修改时间: 2025-12-02 18:30:45 (北京时间)
```
👆 这就是您要的答案！

### 文件列表
```
[1] 数据报告_18-30.txt    <- 最新的
[2] 日志_15-20.txt
[3] 统计_09-10.txt         <- 最旧的
```
👆 按修改时间降序排列

---

## 一键命令

### 完整流程（首次）
```bash
cd /home/user/webapp && \
pip3 install -r requirements.txt && \
python3 setup_guide.py
```

### 日常使用
```bash
cd /home/user/webapp && python3 google_drive_finder.py
```

### 添加到定时任务（每天9点）
```bash
# 编辑crontab
crontab -e

# 添加以下行
0 9 * * * cd /home/user/webapp && python3 google_drive_finder.py >> /tmp/drive_finder.log 2>&1
```

---

## 修改配置

### 更改主文件夹
编辑 `google_drive_finder.py` 第14行：
```python
MAIN_FOLDER_ID = "你的新文件夹ID"
```

### 更改时区
编辑 `google_drive_finder.py` 第21行：
```python
beijing_tz = pytz.timezone('Asia/Shanghai')  # 改为其他时区
```

### 更改日期格式
编辑 `google_drive_finder.py` 第23行：
```python
return beijing_time.strftime('%Y-%m-%d')  # 改为其他格式
```

---

## 技术支持

1. **查看详细文档**: `USAGE_CN.md`
2. **运行设置向导**: `python3 setup_guide.py`
3. **检查项目总结**: `PROJECT_SUMMARY.md`

---

## 版本信息

- **版本**: 1.0.0
- **Python**: 3.7+
- **创建日期**: 2025-12-02
- **状态**: ✅ 生产可用

---

## 快速测试

```bash
# 测试Python环境
python3 --version

# 测试依赖安装
python3 -c "import google.auth; import pytz; print('✅ 依赖已安装')"

# 测试今天日期
python3 -c "from datetime import datetime; import pytz; print('今天:', datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d'))"
```

---

**记住**: 完成设置后，每天只需一条命令：`python3 google_drive_finder.py` ✨
