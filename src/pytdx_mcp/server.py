"""
pytdx-mcp: MCP服务器，用于获取实时A股行情数据
"""

from typing import Any, Dict, List

from fastmcp import FastMCP
from pytdx.hq import TdxHq_API

# 创建MCP服务器实例
mcp = FastMCP("pytdx-realtime")

# 全局API实例
_api = None
_connected_server = None

# 备用服务器列表（按优先级排序）
SERVERS = [
    ("218.75.126.9", 7709),  # 杭州
    ("115.238.56.198", 7709),  # 上海
    ("115.238.90.165", 7709),  # 上海
    ("218.108.50.178", 7709),  # 杭州
    ("140.207.198.6", 7709),  # 上海
]


def get_api() -> TdxHq_API:
    """获取或创建TdxHq_API实例，自动选择可用服务器"""
    global _api, _connected_server

    if _api is None:
        _api = TdxHq_API()

    # 如果已连接到某个服务器，直接返回
    if _connected_server:
        return _api

    # 尝试连接备用服务器
    for host, port in SERVERS:
        if _api.connect(host, port):
            _connected_server = (host, port)
            print(f"✅ 已连接到服务器: {host}:{port}")
            return _api

    # 所有服务器都不可用
    raise ConnectionError("❌ 无法连接到任何行情服务器，请检查网络连接")


def reset_connection():
    """重置连接（在出错时调用）"""
    global _api, _connected_server
    if _api:
        try:
            _api.disconnect()
        except Exception:
            pass
    _api = None
    _connected_server = None


@mcp.tool()
def get_realtime_quote(market: int, code: str) -> Dict[str, Any]:
    """
    获取单只股票的实时行情

    Args:
        market: 市场代码 (0=深市, 1=沪市)
        code: 股票代码 (如 '300766', '600126')

    Returns:
        包含实时行情数据的字典，包括：
        - code: 股票代码
        - name: 股票名称
        - price: 当前价格
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - last_close: 昨收价
        - vol: 成交量（手）
        - amount: 成交额（元）
        - change_pct: 涨跌幅（%）
    """
    try:
        api = get_api()
        # 注意：不要断开连接，保持长连接
        data = api.get_security_quotes([(market, code)])

        if data and len(data) > 0:
            stock = data[0]
            change_pct = (
                ((stock["price"] - stock["last_close"]) / stock["last_close"] * 100)
                if stock["last_close"] > 0
                else 0
            )

            return {
                "code": stock["code"],
                "name": stock.get("name", ""),
                "price": float(stock["price"]),
                "open": float(stock["open"]),
                "high": float(stock["high"]),
                "low": float(stock["low"]),
                "last_close": float(stock["last_close"]),
                "vol": int(stock["vol"]),
                "amount": float(stock["amount"]),
                "change_pct": round(change_pct, 2),
            }

        return {"error": f"无法获取股票 {code} 的行情数据"}

    except Exception as e:
        # 连接失败时重置连接
        reset_connection()
        return {"error": f"获取行情失败: {str(e)}"}


@mcp.tool()
def get_batch_quotes(stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    批量获取多只股票的实时行情

    Args:
        stocks: 股票列表，每个元素包含:
            - market: 市场代码 (0=深市, 1=沪市)
            - code: 股票代码

    Returns:
        股票行情列表，每个元素包含实时行情数据

    Example:
        stocks = [
            {"market": 0, "code": "300766"},
            {"market": 1, "code": "688316"}
        ]
    """
    results = []

    try:
        api = get_api()
        # 构建查询参数
        params = [(s["market"], s["code"]) for s in stocks]

        data = api.get_security_quotes(params)

        if data:
            for stock in data:
                change_pct = (
                    ((stock["price"] - stock["last_close"]) / stock["last_close"] * 100)
                    if stock["last_close"] > 0
                    else 0
                )

                results.append(
                    {
                        "code": stock["code"],
                        "name": stock.get("name", ""),
                        "price": float(stock["price"]),
                        "open": float(stock["open"]),
                        "high": float(stock["high"]),
                        "low": float(stock["low"]),
                        "last_close": float(stock["last_close"]),
                        "vol": int(stock["vol"]),
                        "amount": float(stock["amount"]),
                        "change_pct": round(change_pct, 2),
                    }
                )

        return results

    except Exception as e:
        # 连接失败时重置连接
        reset_connection()
        return [{"error": f"批量获取行情失败: {str(e)}"}]


@mcp.tool()
def get_kline_data(market: int, code: str, kline_type: int = 9, count: int = 100) -> Dict[str, Any]:
    """
    获取股票K线数据

    Args:
        market: 市场代码 (0=深市, 1=沪市)
        code: 股票代码
        kline_type: K线类型 (9=日线, 5=5分钟线, 8=60分钟线)
        count: 获取的K线数量

    Returns:
        K线数据，包括：
        - datetime: 时间
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - vol: 成交量
        - amount: 成交额
    """
    try:
        api = get_api()

        data = api.get_security_bars(kline_type, market, code, 0, count)

        if data:
            klines = []
            for bar in data:
                klines.append(
                    {
                        "datetime": bar["datetime"],
                        "open": float(bar["open"]),
                        "high": float(bar["high"]),
                        "low": float(bar["low"]),
                        "close": float(bar["close"]),
                        "vol": int(bar["vol"]),
                        "amount": float(bar["amount"]),
                    }
                )

            return {
                "code": code,
                "market": market,
                "count": len(klines),
                "klines": klines,
            }

        return {"error": f"无法获取股票 {code} 的K线数据"}

    except Exception as e:
        # 连接失败时重置连接
        reset_connection()
        return {"error": f"获取K线失败: {str(e)}"}


def main():
    """启动MCP服务器"""
    mcp.run()


if __name__ == "__main__":
    main()
