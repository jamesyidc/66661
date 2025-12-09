# Panic Wash Reader V5 使用文档

## 功能特性

使用 **Playwright 自动化浏览器**技术，直接从 Google Drive 读取最新的 `.txt` 文件数据。

### 核心优势

1. ✅ **绕过 API 限制** - 不需要 Google Drive API 认证
2. ✅ **实时获取最新数据** - 每次调用都从 Google Drive 获取最新文件
3. ✅ **突破50条限制** - 通过浏览器自动化，可以获取所有文件
4. ✅ **自动解析数据** - 自动解析急涨、急跌、比值、差值等关键指标
5. ✅ **支持GBK编码** - 正确处理中文内容

## 安装依赖

```bash
# 安装 Python 依赖
pip install playwright pytz

# 安装浏览器
playwright install chromium

# 安装系统依赖（Linux）
sudo apt-get install libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libxdamage1 libgbm1 libasound2
```

## 使用方法

### 方法 1: 异步方式（推荐）

```python
import asyncio
from panic_wash_reader_v5 import PanicWashReaderV5

async def main():
    reader = PanicWashReaderV5()
    
    # 获取最新数据
    data = await reader.get_data()
    
    if data:
        print(f"文件名: {data['filename']}")
        print(f"急涨: {data['rise_total']}")
        print(f"急跌: {data['fall_total']}")
        print(f"比值: {data['rise_fall_ratio']}")
        print(f"差值: {data['diff_result']}")
        print(f"币种数量: {len(data['coins'])}")

# 运行
asyncio.run(main())
```

### 方法 2: 同步方式

```python
from panic_wash_reader_v5 import get_latest_panic_wash_data

# 获取最新数据（同步方式）
data = get_latest_panic_wash_data()

if data:
    print(f"急涨: {data['rise_total']}")
    print(f"急跌: {data['fall_total']}")
```

### 方法 3: 在 Flask/API 中使用

```python
from flask import Flask, jsonify
from panic_wash_reader_v5 import PanicWashReaderV5
import asyncio

app = Flask(__name__)
reader = PanicWashReaderV5()

@app.route('/api/latest-data')
async def get_latest_data():
    # 异步获取最新数据
    data = await reader.get_data()
    
    if data:
        return jsonify({
            'success': True,
            'data': data
        })
    else:
        return jsonify({
            'success': False,
            'message': '获取数据失败'
        }), 500
```

## 返回数据格式

```python
{
    'filename': '2025-12-06_0819.txt',      # 文件名
    'rise_total': 0,                        # 急涨总和
    'fall_total': 22,                       # 急跌总和
    'five_states': '震荡无序',               # 市场状态
    'rise_fall_ratio': 999.0,               # 急涨急跌比值
    'diff_result': -22.0,                   # 差值结果
    'green_count': 3,                       # 绿色数量
    'count_times': 8,                       # 计次
    'coins': [                              # 币种详细数据
        {
            'seq_num': 1,
            'coin_name': 'BTC',
            'rise_speed': -0.09,
            'rise_signal': 0,
            'fall_signal': 0,
            'current_price': 88777.21549,
            'change_24h': -3.27
        },
        # ... 更多币种
    ]
}
```

## 配置说明

可以通过修改脚本中的常量来配置：

```python
# Google Drive 文件夹ID
GOOGLE_DRIVE_FOLDER_ID = "1JNZKKnZLeoBkxSumjS63SOInCriPfAKX"

# 时区设置
BEIJING_TZ = pytz.timezone('Asia/Shanghai')
```

## 性能说明

- **首次调用**: 约 20-30 秒（启动浏览器 + 访问 Google Drive + 解析数据）
- **后续调用**: 约 15-25 秒
- **建议**: 在后台定时任务中使用，缓存结果供 API 使用

## 错误处理

脚本内置了多种错误处理机制：

1. 页面加载超时（30秒）
2. 文件未找到处理
3. 解析失败兜底
4. 浏览器异常自动关闭

## 测试命令

```bash
# 直接测试
python3 panic_wash_reader_v5.py

# 预期输出
# ============================================================
# Panic Wash Reader V5 - Playwright 版本
# ============================================================
# 
# 正在获取最新数据...
# 正在访问 Google Drive 文件夹...
# 找到最新文件: 2025-12-06_0819.txt (08:19)
# ✓ 数据更新成功: 2025-12-06_0819.txt
# 
# ✓ 数据获取成功!
# 文件名: 2025-12-06_0819.txt
# 急涨: 0
# 急跌: 22
# 状态: 震荡无序
# 比值: 999.0
# 差值: -22.0
```

## 常见问题

### Q1: 为什么第一次运行很慢？

A: Playwright 需要启动真实的 Chromium 浏览器，首次启动需要初始化。建议使用缓存机制。

### Q2: 如何加快速度？

A: 
1. 使用 `headless=True` 模式（默认已启用）
2. 实现数据缓存机制
3. 使用后台定时任务预加载数据

### Q3: 会不会被 Google 限制？

A: Playwright 模拟真实浏览器访问，与用户手动访问无异，不会被限制。但建议：
- 不要频繁调用（建议间隔 1-5 分钟）
- 使用缓存机制减少请求

## 与其他版本对比

| 版本 | 方式 | 优点 | 缺点 |
|------|------|------|------|
| V1-V4 | requests + HTML解析 | 快速 | 受50条限制，无法获取最新文件 |
| **V5** | Playwright浏览器 | 突破限制，获取最新数据 | 较慢（20-30秒） |

## 最佳实践

```python
# 建议：使用后台定时任务 + 缓存
import asyncio
from panic_wash_reader_v5 import PanicWashReaderV5
from datetime import datetime, timedelta

class CachedDataReader:
    def __init__(self, cache_minutes=5):
        self.reader = PanicWashReaderV5()
        self.cached_data = None
        self.last_update = None
        self.cache_minutes = cache_minutes
    
    async def get_data(self, force_refresh=False):
        """获取数据（带缓存）"""
        now = datetime.now()
        
        # 检查缓存是否有效
        if not force_refresh and self.cached_data and self.last_update:
            if now - self.last_update < timedelta(minutes=self.cache_minutes):
                return self.cached_data
        
        # 缓存过期或强制刷新，重新获取
        data = await self.reader.get_data()
        if data:
            self.cached_data = data
            self.last_update = now
        
        return self.cached_data

# 使用
cached_reader = CachedDataReader(cache_minutes=5)

# 第一次调用：从 Google Drive 获取（慢）
data1 = await cached_reader.get_data()

# 5分钟内的调用：使用缓存（快）
data2 = await cached_reader.get_data()

# 强制刷新
data3 = await cached_reader.get_data(force_refresh=True)
```

## 技术原理

1. **启动 Playwright Chromium 浏览器**（headless 模式）
2. **访问 Google Drive 文件夹**页面
3. **等待页面加载**完成（networkidle）
4. **解析 HTML**，提取所有 .txt 文件列表
5. **定位最新文件**（按时间戳排序）
6. **自动化点击**文件（或直接下载）
7. **获取文件内容**并解析
8. **关闭浏览器**，返回数据

## 维护建议

- 定期检查 Google Drive 文件夹 ID 是否变化
- 监控脚本执行时间，优化性能
- 记录获取失败的日志
- 设置告警机制（如连续失败3次）

---

**作者**: AI Assistant  
**版本**: V5.0  
**更新日期**: 2025-12-06  
**GitHub**: https://github.com/jamesyidc/6666.git
