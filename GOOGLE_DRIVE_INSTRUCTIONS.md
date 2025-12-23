# 📋 Google Drive 数据导入指南

## ✅ 今天的文件夹已确认

**当前北京时间**: 2025-12-09 12:47  
**Google Drive文件夹**: https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV  
**今天的日期文件夹**: **2025-12-09** ✓

## 📥 方法1：手动导入（最简单）

### 步骤：

1. **从Google Drive下载最新TXT文件**
   - 打开：https://drive.google.com/drive/folders/1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV
   - 进入 `2025-12-09` 文件夹
   - 下载最新的TXT文件（例如：`2025-12-09_1240.txt`）

2. **上传到AI Drive**
   - 将文件上传到 `/mnt/aidrive/`

3. **运行导入命令**
   ```bash
   python3 manual_txt_import.py /mnt/aidrive/2025-12-09_1240.txt
   ```

### 示例：
```bash
cd /home/user/webapp
python3 manual_txt_import.py /mnt/aidrive/2025-12-09_1240.txt
```

输出：
```
✅ 导入成功！
   快照时间: 2025-12-09 12:40:00
   急涨/急跌: 5/3
   状态: 上涨趋势
   币种数量: 29
```

## 🔄 方法2：自动采集（持续运行）

如果文件已经在AI Drive或本地目录：

```bash
# 单次采集
python3 google_drive_snapshot_collector.py --once

# 持续运行（10分钟间隔）
python3 google_drive_snapshot_collector.py

# 后台运行
nohup python3 google_drive_snapshot_collector.py > gdrive_collector.log 2>&1 &
```

采集器会自动：
- 从 `/mnt/aidrive/` 或当前目录查找最新TXT文件
- 解析文件内容
- 存入 `crypto_data.db`
- 每10分钟重复一次

## 📊 验证数据

导入后，检查数据：

```bash
# 查看API返回
curl http://localhost:5000/api/latest | python3 -m json.tool

# 访问查询页面
https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/query
```

## 🎯 TXT文件格式

系统期望的格式：
```
透明标签_急涨总和=急涨：5
透明标签_急跌总和=急跌：3
透明标签_五种状态=状态：上涨趋势
透明标签_计次=12
[超级列表框_首页开始]
1|BTC|0.15|1|0|2025-12-09 12:40:00|...|...
2|ETH|0.08|0|0|2025-12-09 12:40:00|...|...
...
[超级列表框_首页结束]
```

## 🔧 故障排除

### 问题：文件解析失败
- 检查文件格式是否正确
- 确保文件编码为 UTF-8
- 确认文件包含 `[超级列表框_首页开始]` 标记

### 问题：数据库错误
- 确保 `crypto_data.db` 有写权限
- 运行：`python3 google_drive_snapshot_collector.py --once` 重新初始化

### 问题：API返回空数据
- 确认数据已成功导入
- 重启Flask应用：`pkill -f app_new.py && nohup python3 app_new.py > flask_new.log 2>&1 &`

## 📞 需要帮助？

如果遇到问题，提供以下信息：
1. TXT文件的前几行内容
2. 错误消息
3. 数据库中的最新记录：`python3 -c "import sqlite3; conn=sqlite3.connect('crypto_data.db'); print(conn.execute('SELECT snapshot_time FROM crypto_snapshots ORDER BY snapshot_time DESC LIMIT 1').fetchone())"`

---

**创建时间**: 2025-12-09 12:47 UTC  
**状态**: 等待用户提供今天的TXT文件
