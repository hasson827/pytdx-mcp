# pytdx-mcp

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**pytdx-mcp** 是一个基于 [pytdx](https://github.com/rainx/pytdx) 的 MCP（Model Context Protocol）服务器，用于获取实时A股行情数据。

## 特性

- 🔄 **实时行情** - 获取A股实时价格、成交量等数据
- 📊 **批量查询** - 一次获取多只股票行情，提高效率
- 📈 **K线数据** - 支持日线、分钟线等多种K线类型
- 🚀 **自动重连** - 智能选择可用服务器，自动故障转移
- 💰 **完全免费** - 无需API密钥，无需注册
- 🔌 **MCP集成** - 无缝对接支持MCP的大模型应用

## 安装

### 方法1：从GitHub安装（推荐）

```bash
pip install git+https://github.com/hasson827/pytdx-mcp.git
```

### 方法2：从源码安装

```bash
git clone https://github.com/hasson827/pytdx-mcp.git
cd pytdx-mcp
pip install -e .
```

### 验证安装

```bash
pytdx-mcp --help
```

## 配置

### OpenCode配置

编辑 `~/.config/opencode/opencode.json`，添加：

```json
{
  "mcpServers": {
    "pytdx-mcp": {
      "type": "local",
      "command": ["pytdx-mcp"],
      "enabled": true
    }
  }
}
```

### Claude Desktop配置

编辑 Claude Desktop 配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加内容：

```json
{
  "mcpServers": {
    "pytdx-mcp": {
      "command": "pytdx-mcp"
    }
  }
}
```

## 可用工具

### 1. `get_realtime_quote` - 获取单只股票实时行情

获取指定股票的实时价格、成交量等信息。

**参数：**
- `market` (int): 市场代码
  - `0` = 深圳A股（包括创业板）
  - `1` = 上海A股（包括科创板）
- `code` (str): 股票代码（如 `"300766"`, `"600126"`）

**返回数据：**
```json
{
  "code": "300766",
  "name": "每日互动",
  "price": 44.57,
  "open": 44.00,
  "high": 45.20,
  "low": 43.80,
  "last_close": 44.41,
  "vol": 248869,
  "amount": 110123456.78,
  "change_pct": 0.36
}
```

### 2. `get_batch_quotes` - 批量获取多只股票行情

一次获取多只股票的实时行情，提高效率。

**参数：**
- `stocks` (List[Dict]): 股票列表，每个元素包含：
  - `market` (int): 市场代码
  - `code` (str): 股票代码

**示例：**
```python
stocks = [
    {"market": 0, "code": "300766"},  # 每日互动
    {"market": 1, "code": "688316"},  # 青云科技
]
```

### 3. `get_kline_data` - 获取K线数据

获取股票的历史K线数据，包括日线、分钟线等。

**参数：**
- `market` (int): 市场代码
- `code` (str): 股票代码
- `kline_type` (int): K线类型
  - `9` = 日线
  - `5` = 5分钟线
  - `8` = 60分钟线
- `count` (int): 获取的K线数量（默认100）

## 使用示例

### 示例1：获取单只股票行情

```
请使用pytdx-mcp查询每日互动(300766)的最新价格
```

### 示例2：批量查询多只股票

```
使用pytdx-mcp批量查询以下股票的实时行情：
- 每日互动 (300766) - 深市
- 青云科技 (688316) - 沪市
- 杭钢股份 (600126) - 沪市
```

### 示例3：获取K线数据

```
使用pytdx-mcp获取每日互动最近100天的日K线数据
```

## 市场代码对照表

| 市场 | 代码 | 说明 |
|------|------|------|
| 深圳A股 | 0 | 包括主板、中小板、创业板 |
| 上海A股 | 1 | 包括主板、科创板 |

**常见股票代码：**
- 每日互动: 市场0，代码300766
- 青云科技: 市场1，代码688316
- 杭钢股份: 市场0，代码600126
- 航锦科技: 市场0，代码000818

## ⚙️ 技术细节

### 服务器连接

pytdx-mcp使用以下策略确保稳定连接：

1. **自动选择服务器** - 维护多个备用服务器地址
2. **故障转移** - 当前服务器不可用时自动切换
3. **长连接** - 保持连接以提高性能
4. **自动重连** - 连接失败时自动重置并重试

### 备用服务器列表

```
218.75.126.9:7709      # 杭州
115.238.56.198:7709    # 上海
115.238.90.165:7709    # 上海
218.108.50.178:7709    # 杭州
140.207.198.6:7709     # 上海
```

## 注意事项

1. **交易时间** - A股交易时间为 9:30-11:30, 13:00-15:00
2. **查询频率** - 建议每次查询间隔≥3秒，避免被封IP
3. **数据延迟** - 免费数据可能有1-3秒延迟
4. **仅供学习** - 请勿用于商业用途或实盘交易

## 相关项目

- [pytdx](https://github.com/rainx/pytdx) - 通达信数据接口
- [fastmcp](https://github.com/anthropics/fastmcp) - 快速MCP开发框架
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

- [pytdx](https://github.com/rainx/pytdx) 提供通达信数据接口
- [fastmcp](https://github.com/anthropics/fastmcp) 提供MCP开发框架

---

**免责声明：** 本项目仅供学习和研究使用，不构成任何投资建议。使用本工具获取的数据请遵守相关法律法规。
