# 股票监测系统 - 项目审查报告

## 一、发现的主要问题

### 1. 代码重复问题 (严重)

| 问题 | 位置 | 影响 |
|------|------|------|
| `get_current_user()` 重复定义 | `dependencies.py` 和 `api/auth.py` | 维护困难，容易不同步 |
| `calculate_ma()` 重复定义 | `api/stocks.py` 和 `api/charts.py` | 代码冗余 |
| 认证逻辑在 `auth.py` 的 `get_me()` 中又重复实现 | `api/auth.py:85-110` | 完全没必要 |

### 2. API设计不一致 (严重)

| 问题 | 详情 |
|------|------|
| 路由重复 | `/api/stocks/{id}/kline` 和 `/api/charts/kline/{id}` 功能相同 |
| 路由重复 | `/api/stocks/{id}/indicators` 和 `/api/charts/indicators/{id}` 功能相同 |
| 参数命名不统一 | `stocks` 用 `type`，`charts` 用 `period` |
| 响应格式不统一 | `stocks/kline` 返回 `{klines, period, total}`，`charts/kline` 返回 `{stock, klines, period, total}` |

### 3. 前端API调用混乱 (中等)

- `api/index.ts` 中同时定义了 `stocks.getKline()` 和 `charts.getKline()`
- `MarketOverview.vue` 和 `EnhancedStockDetail.vue` 直接使用 `fetch()` 而不是 `api` 模块
- 前端类型定义与后端响应不完全匹配

### 4. 安全问题 (严重)

- CORS 配置允许所有源：`allow_origins=["*"]`
- JWT SECRET_KEY 硬编码在配置中
- 缺少速率限制

### 5. 数据流向不清晰 (中等)

- `data_fetcher.py` 作为统一数据源，但其他服务有时直接调用 AkShare
- 缓存策略不统一

---

## 二、修复计划

### P0 - 立即修复

1. **删除重复的认证代码**
   - 删除 `api/auth.py` 中的 `get_current_user()` 函数
   - 使用 `dependencies.py` 中的版本
   - 简化 `get_me()` 接口

2. **统一API路由**
   - 删除 `/api/charts/` 路由，统一使用 `/api/stocks/`
   - 或者让 `charts` 路由调用 `stocks` 的实现

3. **提取重复的工具函数**
   - 创建 `app/utils/indicators.py` 存放技术指标计算函数

4. **修复CORS配置**
   - 限制允许的源为前端地址

### P1 - 短期改进

1. **统一API响应格式**
2. **统一前端API调用方式**
3. **修复前后端数据格式匹配**

### P2 - 中期优化

1. **添加单元测试**
2. **优化缓存策略**
3. **添加API文档**

---

## 三、当前修复进度

- [x] 删除重复的 `get_current_user()` - 已统一到 `dependencies.py`
- [x] 删除重复的 `calculate_ma()` - 已提取到 `app/utils/indicators.py`
- [x] 统一API路由 - `charts.py` 保留但添加废弃提示
- [x] 修复CORS配置 - 使用配置文件控制允许的源
- [x] 统一前端API调用 - 添加 `api.enhanced` 模块，修复直接使用 `fetch` 的问题
- [x] 添加技术指标工具函数 - `app/utils/indicators.py` (MA, EMA, RSI, MACD, 布林带)
- [x] 改进配置管理 - 添加缓存TTL配置、CORS配置、安全警告
- [x] 市场数据缓存优化 - 新增 `app/services/market_cache.py`
  - 定时刷新全市场数据（开盘前、盘中每5分钟、收盘后）
  - 避免每次请求都调用 AkShare API
  - 防止频繁请求被封禁
  - 添加缓存状态查询和手动刷新接口

## 四、新增文件

| 文件 | 说明 |
|------|------|
| `app/utils/__init__.py` | 工具函数模块初始化 |
| `app/utils/indicators.py` | 技术指标计算函数（MA、EMA、RSI、MACD、布林带） |
| `app/services/market_cache.py` | 市场数据缓存服务 |

## 五、修改的文件

| 文件 | 修改内容 |
|------|---------|
| `app/api/auth.py` | 删除重复的 `get_current_user()`，简化 `get_me()` |
| `app/api/stocks.py` | 使用统一的技术指标工具函数 |
| `app/api/charts.py` | 使用统一的技术指标工具函数，添加废弃提示 |
| `app/api/enhanced_stocks.py` | 使用市场缓存，添加缓存状态接口 |
| `app/config.py` | 添加 CORS 配置、缓存 TTL 配置 |
| `app/main.py` | 使用配置文件的 CORS 设置 |
| `app/core/scheduler.py` | 添加市场数据缓存刷新任务 |
| `app/services/data_fetcher.py` | 优先使用市场缓存获取实时数据 |
| `stock-monitor-pc/src/api/index.ts` | 添加 `enhanced` API 模块 |
| `stock-monitor-pc/src/views/MarketOverview.vue` | 使用统一的 API 模块 |
| `stock-monitor-pc/src/views/EnhancedStockDetail.vue` | 使用统一的 API 模块 |
