## v3.9.7 - 统一所有时间显示为北京时间（UTC+8）

### ✅ 已修复问题
**问题**: 逃顶信号时间显示为 12:06/12:48 而非正确的 20:06/20:48
**原因**: `toLocaleString()` 在不同浏览器环境输出不稳定
**解决**: 使用可靠的手动时区转换方法

### 🔧 核心修改
```javascript
// ❌ 旧代码 - 不稳定
const timeStr = utcTime.toLocaleString('zh-CN', { 
    timeZone: 'Asia/Shanghai',
    hour: '2-digit', 
    minute: '2-digit'
}).split(' ')[1];

// ✅ 新代码 - 可靠
const beijingTime = new Date(utcTime.getTime() + 8 * 60 * 60 * 1000);
const hours = beijingTime.getUTCHours().toString().padStart(2, '0');
const minutes = beijingTime.getUTCMinutes().toString().padStart(2, '0');
const timeStr = `${hours}:${minutes}`;
```

### ✅ 验证结果
| UTC时间 | 北京时间 | 状态 |
|---------|----------|------|
| 2025-12-12 12:06:00 | 20:06 | ✅ |
| 2025-12-12 12:48:00 | 20:48 | ✅ |

### 📍 测试页面
- **LINK 第2页**: https://5000-iypypqmz2wvn9dmtq7ewn-583b4d74.sandbox.novita.ai/symbol/LINK/v6?page=1
  - 显示2个橙色逃顶信号：20:06 和 20:48 ✅
  - 对应2个绿色卖点2信号 ✅

### 🎨 图表标记说明（全部北京时间）
- 🟣 **紫色圆点**: 支撑压力最新时间（来自 support_resistance_levels.record_time）
- 🟠 **橙色标记**: 逃顶信号时间（UTC转北京，情况3+4>=8）
- 🟢 **绿色标记**: 卖点2（逃顶信号后5根K线内的不创新高点）
- 🔴 **红色标记**: 买点4（7天低点+2根不创新低+抄底条件）
- 🔵 **蓝色标记**: 卖点1（48小时高点+RSI>=50）

### 📊 数据源时区说明
| 数据表 | 字段 | 时区 | 前端处理 |
|--------|------|------|----------|
| support_resistance_levels | record_time | 北京时间 | 直接显示 |
| support_resistance_snapshots | snapshot_time | UTC | +8小时转北京 |
| okex K线数据 | timestamp | UTC毫秒 | X轴设为Asia/Shanghai |

### 🔄 提交记录
- `fix(v3.9.7): 修正逃顶信号时间显示-使用可靠的手动计算方法`
- 替换 toLocaleString() 为手动时区转换
- UTC时间戳 +8小时 后用 getUTCHours/getUTCMinutes 提取
- 确保浏览器环境下时间显示为20:06/20:48而非12:06/12:48
