# 📱 Telegram消息系统 - 快速命令手册

**更新日期**: 2025-12-20  
**适用范围**: Telegram消息通知系统日常管理

---

## 🚀 服务管理命令

### 查看服务状态
```bash
# 查看所有PM2服务
pm2 status

# 只看Telegram服务
pm2 status telegram-notifier

# 查看详细信息
pm2 show telegram-notifier
```

### 启动/停止/重启服务
```bash
# 启动服务
pm2 start telegram-notifier

# 停止服务
pm2 stop telegram-notifier

# 重启服务
pm2 restart telegram-notifier

# 重载服务（0秒停机）
pm2 reload telegram-notifier

# 删除服务
pm2 delete telegram-notifier
```

### 从配置文件启动
```bash
# 启动Telegram服务
pm2 start /home/user/webapp/ecosystem.config.js --only telegram-notifier

# 启动所有服务
pm2 start /home/user/webapp/ecosystem.config.js

# 保存PM2配置
pm2 save
```

---

## 📋 日志查看命令

### 实时日志
```bash
# 查看实时日志（按Ctrl+C退出）
pm2 logs telegram-notifier

# 只看最近20行
pm2 logs telegram-notifier --lines 20

# 查看最近50行（不实时）
pm2 logs telegram-notifier --lines 50 --nostream
```

### 错误日志
```bash
# 只看错误日志
pm2 logs telegram-notifier --err

# 查看最近30行错误
pm2 logs telegram-notifier --err --lines 30 --nostream
```

### 日志文件位置
```bash
# 标准输出日志
cat ~/.pm2/logs/telegram-notifier-out.log

# 错误日志
cat ~/.pm2/logs/telegram-notifier-error.log

# 实时查看日志文件
tail -f ~/.pm2/logs/telegram-notifier-out.log
```

---

## ⚙️ 配置管理命令

### 查看配置
```bash
# 查看完整配置
cat /home/user/webapp/telegram_config.json

# 格式化查看（需要jq）
cat /home/user/webapp/telegram_config.json | jq .

# 只看推送条件
cat /home/user/webapp/telegram_config.json | jq '.push_conditions'
```

### 修改配置
```bash
# 编辑配置文件
nano /home/user/webapp/telegram_config.json

# 修改后重启服务
pm2 restart telegram-notifier

# 验证配置生效
pm2 logs telegram-notifier --lines 10 --nostream
```

### 常用配置调整

#### 调整冷却时间（默认300秒=5分钟）
```bash
# 编辑配置
nano /home/user/webapp/telegram_config.json

# 找到这行并修改：
"cooldown_seconds": 300  # 改为你想要的秒数

# 例如改为10分钟：
"cooldown_seconds": 600

# 保存后重启
pm2 restart telegram-notifier
```

#### 调整最小触发币种数（默认1个）
```bash
# 编辑配置
nano /home/user/webapp/telegram_config.json

# 找到这行并修改：
"min_coins": 1  # 改为你想要的数量

# 例如改为3个币种才推送：
"min_coins": 3

# 保存后重启
pm2 restart telegram-notifier
```

#### 禁用某类信号推送
```bash
# 编辑配置
nano /home/user/webapp/telegram_config.json

# 禁用抄底信号：
"buy": {
  "enabled": false,  # 改为false
  "name": "抄底信号",
  "emoji": "🟢"
}

# 禁用逃顶信号：
"sell": {
  "enabled": false,  # 改为false
  "name": "逃顶信号",
  "emoji": "🔴"
}

# 保存后重启
pm2 restart telegram-notifier
```

---

## 🧪 测试命令

### 测试Bot连接
```bash
# 测试Bot是否有效
curl -s "https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/getMe" | jq

# 获取最新更新（检查Chat ID）
curl -s "https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/getUpdates" | jq
```

### 发送测试消息
```bash
# 发送简单测试消息
curl -s "https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/sendMessage" \
  -d "chat_id=-1003227444260" \
  -d "text=测试消息 - $(date '+%Y-%m-%d %H:%M:%S')" | jq

# 发送HTML格式消息
curl -s "https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/sendMessage" \
  -d "chat_id=-1003227444260" \
  -d "text=<b>测试消息</b>%0A时间: $(date '+%Y-%m-%d %H:%M:%S')" \
  -d "parse_mode=HTML" | jq
```

### 手动运行服务（调试用）
```bash
# 进入项目目录
cd /home/user/webapp

# 手动运行（查看实时输出）
python3 telegram_notifier.py

# 按Ctrl+C停止
```

---

## 🔍 数据库检查命令

### 检查数据更新状态
```bash
cd /home/user/webapp && python3 << 'EOF'
import sqlite3
from datetime import datetime

conn = sqlite3.connect('/home/user/webapp/crypto_data.db')
cursor = conn.cursor()

# 检查最近5分钟的数据
cursor.execute("SELECT COUNT(*), MAX(record_time) FROM support_resistance_levels WHERE record_time >= datetime('now', '-5 minutes')")
result = cursor.fetchone()
print(f"最近5分钟数据: {result[0]}条")
print(f"最新时间: {result[1]}")

conn.close()
EOF
```

### 检查当前触发信号
```bash
cd /home/user/webapp && python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('/home/user/webapp/crypto_data.db')
cursor = conn.cursor()

# 统计信号
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN alert_scenario_1=1 OR alert_scenario_2=1 THEN 1 ELSE 0 END) as buy,
        SUM(CASE WHEN alert_scenario_3=1 OR alert_scenario_4=1 THEN 1 ELSE 0 END) as sell
    FROM support_resistance_levels
    WHERE record_time = (SELECT MAX(record_time) FROM support_resistance_levels)
""")
result = cursor.fetchone()
print(f"总币种: {result[0]}")
print(f"抄底信号: {result[1]}个")
print(f"逃顶信号: {result[2]}个")

conn.close()
EOF
```

### 查看触发信号详情
```bash
cd /home/user/webapp && python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('/home/user/webapp/crypto_data.db')
cursor = conn.cursor()

# 抄底信号详情
print("🟢 抄底信号:")
cursor.execute("""
    SELECT symbol, current_price, 
           CASE WHEN alert_scenario_1=1 THEN '接近支撑1' ELSE '接近支撑2' END,
           distance_to_support_1, distance_to_support_2
    FROM support_resistance_levels
    WHERE record_time = (SELECT MAX(record_time) FROM support_resistance_levels)
      AND (alert_scenario_1=1 OR alert_scenario_2=1)
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: ${row[1]:.2f} - {row[2]}")

# 逃顶信号详情
print("\n🔴 逃顶信号:")
cursor.execute("""
    SELECT symbol, current_price,
           CASE WHEN alert_scenario_3=1 THEN '接近压力1' ELSE '接近压力2' END,
           distance_to_resistance_1, distance_to_resistance_2
    FROM support_resistance_levels
    WHERE record_time = (SELECT MAX(record_time) FROM support_resistance_levels)
      AND (alert_scenario_3=1 OR alert_scenario_4=1)
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: ${row[1]:.2f} - {row[2]}")

conn.close()
EOF
```

---

## 🐛 故障排查命令

### 检查服务是否运行
```bash
# 查看PM2进程列表
pm2 list | grep telegram

# 查看进程详情
pm2 show telegram-notifier

# 查看系统进程
ps aux | grep telegram_notifier
```

### 检查网络连接
```bash
# 测试Telegram API连通性
curl -s -o /dev/null -w "%{http_code}" "https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/getMe"
# 返回200表示正常

# 测试网络延迟
ping -c 4 api.telegram.org
```

### 检查文件是否存在
```bash
# 检查核心文件
ls -lh /home/user/webapp/telegram_*.py
ls -lh /home/user/webapp/telegram_config.json
ls -lh /home/user/webapp/crypto_data.db

# 检查日志文件
ls -lh ~/.pm2/logs/telegram-notifier*
```

### 检查配置文件格式
```bash
# 验证JSON格式
python3 -c "import json; json.load(open('/home/user/webapp/telegram_config.json')); print('✅ JSON格式正确')"

# 查看Python语法错误
python3 -m py_compile /home/user/webapp/telegram_notifier.py && echo "✅ Python语法正确"
```

---

## 📊 性能监控命令

### 查看资源占用
```bash
# 查看内存和CPU使用
pm2 status telegram-notifier

# 实时监控（每2秒刷新）
pm2 monit

# 查看详细资源使用
pm2 show telegram-notifier
```

### 查看服务运行时间
```bash
# 查看uptime
pm2 status telegram-notifier | grep uptime

# 查看重启次数
pm2 status telegram-notifier | grep restart
```

---

## 🔄 维护命令

### 清理日志
```bash
# 清空所有PM2日志
pm2 flush

# 清空Telegram服务日志
pm2 flush telegram-notifier

# 手动删除旧日志（7天前）
find ~/.pm2/logs/ -name "telegram-notifier*.log" -mtime +7 -delete
```

### 备份配置
```bash
# 备份配置文件
cp /home/user/webapp/telegram_config.json /home/user/webapp/telegram_config.json.backup.$(date +%Y%m%d)

# 查看备份
ls -lh /home/user/webapp/telegram_config.json.backup.*
```

### 恢复配置
```bash
# 恢复指定日期的备份
cp /home/user/webapp/telegram_config.json.backup.20251220 /home/user/webapp/telegram_config.json

# 重启服务
pm2 restart telegram-notifier
```

---

## 📌 常用组合命令

### 完整重启流程
```bash
# 1. 停止服务
pm2 stop telegram-notifier

# 2. 清空日志
pm2 flush telegram-notifier

# 3. 启动服务
pm2 start telegram-notifier

# 4. 查看实时日志
pm2 logs telegram-notifier --lines 20
```

### 配置修改后的完整流程
```bash
# 1. 备份当前配置
cp /home/user/webapp/telegram_config.json /home/user/webapp/telegram_config.json.backup

# 2. 编辑配置
nano /home/user/webapp/telegram_config.json

# 3. 验证JSON格式
python3 -c "import json; json.load(open('/home/user/webapp/telegram_config.json'))"

# 4. 重启服务
pm2 restart telegram-notifier

# 5. 验证生效
pm2 logs telegram-notifier --lines 10 --nostream
```

### 故障排查完整流程
```bash
# 1. 检查服务状态
pm2 status telegram-notifier

# 2. 查看错误日志
pm2 logs telegram-notifier --err --lines 50 --nostream

# 3. 检查配置文件
cat /home/user/webapp/telegram_config.json | jq .

# 4. 测试Bot连接
curl -s "https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/getMe" | jq

# 5. 检查数据库
python3 -c "import sqlite3; conn = sqlite3.connect('/home/user/webapp/crypto_data.db'); cursor = conn.cursor(); cursor.execute('SELECT MAX(record_time) FROM support_resistance_levels'); print(cursor.fetchone())"

# 6. 重启服务
pm2 restart telegram-notifier

# 7. 监控运行
pm2 logs telegram-notifier
```

---

## 🎯 快速参考表

| 操作 | 命令 |
|------|------|
| 启动服务 | `pm2 start telegram-notifier` |
| 停止服务 | `pm2 stop telegram-notifier` |
| 重启服务 | `pm2 restart telegram-notifier` |
| 查看状态 | `pm2 status telegram-notifier` |
| 实时日志 | `pm2 logs telegram-notifier` |
| 最近日志 | `pm2 logs telegram-notifier --lines 20 --nostream` |
| 错误日志 | `pm2 logs telegram-notifier --err --nostream` |
| 查看配置 | `cat /home/user/webapp/telegram_config.json` |
| 编辑配置 | `nano /home/user/webapp/telegram_config.json` |
| 测试消息 | `curl -d "chat_id=-1003227444260" -d "text=测试" https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/sendMessage` |

---

## 📞 联系信息

**Bot信息**:
- 名称: jamesyi9999_bot
- ID: 8437045462
- Username: @jamesyi9999_bot

**目标频道**:
- Chat ID: -1003227444260
- 名称: Mr.J

**相关链接**:
- 支撑/阻力位页面: https://5000-ilsitop6yown44mau7vd7-c07dda5e.sandbox.novita.ai/support-resistance
- API URL: https://api.telegram.org/bot8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0/

---

**提示**: 将本文档保存为书签，方便快速查阅！
