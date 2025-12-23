# Telegram 通知配置说明 - 只推送双重信号

## 📋 需求说明

**用户要求**:
- LDO 单独触发抄底信号（支撑1 或 支撑2）**不要发通知**
- 必须 **支撑线1 AND 支撑线2 同时满足** 才发通知
- 压力线同理：**压力线1 AND 压力线2 同时满足** 才发通知

---

## ✅ 配置修改

### 1. telegram_config.json 配置

```json
{
  "signal_types": {
    "buy": {
      "enabled": false,        // ❌ 禁用单独抄底信号
      "name": "抄底信号",
      "emoji": "🟢",
      "color": "green"
    },
    "sell": {
      "enabled": false,        // ❌ 禁用单独逃顶信号
      "name": "逃顶信号",
      "emoji": "🔴",
      "color": "red"
    },
    "double_buy": {
      "enabled": true,         // ✅ 启用双重抄底信号
      "name": "双重抄底信号",
      "emoji": "🟢🟢",
      "color": "green"
    },
    "double_sell": {
      "enabled": true,         // ✅ 启用双重逃顶信号
      "name": "双重逃顶信号",
      "emoji": "🔴🔴",
      "color": "red"
    }
  }
}
```

### 2. telegram_notifier.py 代码修改

**修改前** (检查单独信号配置):
```python
if double_buy_data and self.config['signal_types']['buy']['enabled']:
```

**修改后** (检查双重信号配置):
```python
if double_buy_data and self.config['signal_types'].get('double_buy', {}).get('enabled', False):
```

**优势**:
- ✅ 向后兼容：配置不存在时默认 False
- ✅ 独立控制：双重信号与单独信号分离
- ✅ 灵活配置：可单独启用/禁用不同类型

---

## 📊 信号类型对比

### 单独信号 (已禁用)
| 信号类型 | 触发条件 | 配置 | 推送 |
|---------|---------|------|------|
| 🟢 抄底信号 | `alert_scenario_1 = 1` **OR** `alert_scenario_2 = 1` | `buy.enabled = false` | ❌ 不推送 |
| 🔴 逃顶信号 | `alert_scenario_3 = 1` **OR** `alert_scenario_4 = 1` | `sell.enabled = false` | ❌ 不推送 |

**示例**：LDO 只触发支撑1 → 不推送 ✅

### 双重信号 (已启用)
| 信号类型 | 触发条件 | 配置 | 推送 |
|---------|---------|------|------|
| 🟢🟢 双重抄底 | `alert_scenario_1 = 1` **AND** `alert_scenario_2 = 1` | `double_buy.enabled = true` | ✅ 推送 |
| 🔴🔴 双重逃顶 | `alert_scenario_3 = 1` **AND** `alert_scenario_4 = 1` | `double_sell.enabled = true` | ✅ 推送 |

**示例**：UNI 同时触发压力1+压力2 → 推送 (Message ID: 2836) ✅

---

## 🧪 验证结果

### 测试时间
2025-12-20 22:42:23 重启服务后

### 当前信号统计
```
单独抄底信号: 1个 (已禁用推送) ✅
🟢🟢 双重抄底: 0个 (启用推送)
单独逃顶信号: 1个 (已禁用推送) ✅
🔴🔴 双重逃顶: 1个 (启用推送) ✅
```

### 推送记录
```
[22:42:48] 🔴🔴 检测到双重逃顶信号（压力1+2）: 1个币种
[22:42:49] ✅ 消息发送成功 (Message ID: 2836)

币种: UNIUSDT
价格: 接近压力线1和压力线2
```

### 验证结论
✅ **单独信号不推送** - LDO 等单独触发的信号不会发送通知  
✅ **双重信号正常推送** - UNI 双重逃顶信号成功发送  
✅ **配置生效** - 修改后立即生效

---

## 📁 配置文件位置

```
/home/user/webapp/telegram_config.json  (不提交到 Git)
/home/user/webapp/telegram_notifier.py  (已提交)
```

**注意**: `telegram_config.json` 被 `.gitignore` 忽略，不会提交到远程仓库

---

## 🔄 如何恢复单独信号推送

如果将来需要恢复单独信号推送，修改 `telegram_config.json`:

```json
{
  "signal_types": {
    "buy": {
      "enabled": true,   // 改为 true
      ...
    },
    "sell": {
      "enabled": true,   // 改为 true
      ...
    }
  }
}
```

然后重启服务：
```bash
pm2 restart telegram-notifier
```

---

## 📊 信号强度对比

### 信号强度等级
1. **单独信号** (已禁用)
   - 🟢 支撑1 或 支撑2
   - 🔴 压力1 或 压力2
   - 强度: ⭐⭐⭐ (中等)

2. **双重信号** (启用) 
   - 🟢🟢 支撑1 AND 支撑2
   - 🔴🔴 压力1 AND 压力2
   - 强度: ⭐⭐⭐⭐⭐ (极强)

### 为什么只推送双重信号？
1. **更高准确性**: 两条线同时触发，信号更可靠
2. **减少噪音**: 避免频繁的单独信号通知
3. **关键时机**: 双重信号代表更强的买卖点
4. **质量优先**: 只推送最重要的交易信号

---

## 🚀 服务状态

```
服务名称: telegram-notifier
版本: v2.2
状态: Online ✅
检查间隔: 30秒
冷却时间: 300秒 (5分钟)
```

---

## 📝 更新日志

### v2.2 (2025-12-20 22:42)
- ✅ 禁用单独信号推送 (buy, sell)
- ✅ 启用双重信号推送 (double_buy, double_sell)
- ✅ 代码向后兼容修改
- ✅ 配置文件更新

### v2.1 (2025-12-20 22:33)
- ✅ 修复 UNI 信号遗漏问题
- ✅ 查询逻辑优化
- ✅ 5分钟时间窗口容错

---

**配置完成时间**: 2025-12-20 22:42  
**状态**: ✅ 已生效  
**验证**: ✅ 已通过
