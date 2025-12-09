# 🌐 系统访问指南 - 使用路径后缀而非端口号

## 主要网址

### **基础网址：**
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai

---

## 📍 页面路径说明

所有功能都通过路径后缀访问，统一使用 **端口 5000**，更安全且易于管理。

### 1. 首页
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/
```
- 系统介绍
- 功能概览
- 快速导航

### 2. 数据看板（主界面）
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/dashboard
```
- 完整的币种数据表格
- 急涨/急跌趋势图
- 日期时间选择器
- 优先级颜色标记

### 3. 查询页面
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/query
```
- 自动跳转到 dashboard

### 4. 关于系统
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/about
```
- 系统功能介绍
- 技术栈说明
- 相关链接

### 5. API文档
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/api/docs
```
- 完整的API接口文档
- 使用示例

---

## 🔌 API 接口

### 查询指定时间数据
```
GET /api/query?time=2025-12-06 13:42
```

### 获取最新数据
```
GET /api/latest
```

### 获取图表数据
```
GET /api/chart?date=2025-12-06
```

---

## ✨ 优势说明

### 为什么使用路径后缀而非端口号？

#### ❌ 使用端口号的问题：
- `https://5000-xxx.sandbox.ai` - 首页
- `https://8080-xxx.sandbox.ai` - 看板
- `https://8888-xxx.sandbox.ai` - 查询

**风险：**
1. 需要记住多个不同的URL
2. 端口可能被占用或冲突
3. 防火墙可能阻止某些端口
4. 不专业，难以管理

#### ✅ 使用路径后缀的优势：
- `https://5000-xxx.sandbox.ai/` - 首页
- `https://5000-xxx.sandbox.ai/dashboard` - 看板
- `https://5000-xxx.sandbox.ai/query` - 查询
- `https://5000-xxx.sandbox.ai/api/docs` - 文档

**好处：**
1. ✅ 统一的域名，易于记忆
2. ✅ 只占用一个端口，避免冲突
3. ✅ 更专业的URL结构
4. ✅ 易于添加新功能（只需新增路径）
5. ✅ 符合RESTful API设计规范

---

## 📱 快速开始

### 1. 访问首页
直接打开：
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/
```

### 2. 进入数据看板
点击首页的"进入数据看板"按钮，或直接访问：
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/dashboard
```

### 3. 查看API文档
```
https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/api/docs
```

---

## 🎯 页面功能对照

| 功能 | 路径 | 说明 |
|------|------|------|
| 首页 | `/` | 系统介绍和导航 |
| 数据看板 | `/dashboard` | 主要功能界面 |
| 查询 | `/query` | 重定向到dashboard |
| 关于 | `/about` | 系统信息 |
| API文档 | `/api/docs` | 接口说明 |
| 查询API | `/api/query` | 数据查询接口 |
| 最新数据API | `/api/latest` | 获取最新数据 |
| 图表API | `/api/chart` | 图表数据接口 |

---

## 🔗 相关链接

- **GitHub仓库：** https://github.com/jamesyidc/6666
- **Pull Request：** https://github.com/jamesyidc/6666/pull/1
- **系统首页：** https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/
- **数据看板：** https://5000-iik759kgm7i3zqlxvfrfx-cc2fbc16.sandbox.novita.ai/dashboard

---

## 💡 使用建议

1. **收藏看板页面** - `/dashboard` 是最常用的页面
2. **使用API** - 如需集成到其他系统，使用 `/api/*` 接口
3. **查看文档** - 不熟悉时，访问 `/api/docs` 查看完整说明

---

**所有功能统一在一个端口，通过路径区分，更安全、更专业！** 🚀
