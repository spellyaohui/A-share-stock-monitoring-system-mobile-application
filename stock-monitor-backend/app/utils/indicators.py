"""
技术指标计算工具函数
统一的技术指标计算逻辑，避免代码重复
"""
from typing import List, Optional


def calculate_ma(klines: List[dict], period: int) -> List[Optional[float]]:
    """
    计算移动平均线 (Moving Average)
    
    Args:
        klines: K线数据列表，每个元素需包含 'close' 字段
        period: 计算周期
        
    Returns:
        移动平均线数值列表，前 period-1 个值为 None
    """
    if not klines or len(klines) < period:
        return []
    
    ma_values = []
    for i in range(len(klines)):
        if i < period - 1:
            ma_values.append(None)
        else:
            sum_close = sum(kline["close"] for kline in klines[i-period+1:i+1])
            ma_values.append(round(sum_close / period, 2))
    
    return ma_values


def calculate_ema(klines: List[dict], period: int) -> List[Optional[float]]:
    """
    计算指数移动平均线 (Exponential Moving Average)
    
    Args:
        klines: K线数据列表
        period: 计算周期
        
    Returns:
        EMA数值列表
    """
    if not klines or len(klines) < period:
        return []
    
    multiplier = 2 / (period + 1)
    ema_values = []
    
    # 第一个EMA值使用SMA
    first_sma = sum(kline["close"] for kline in klines[:period]) / period
    ema_values.extend([None] * (period - 1))
    ema_values.append(round(first_sma, 2))
    
    # 后续使用EMA公式
    for i in range(period, len(klines)):
        ema = (klines[i]["close"] - ema_values[-1]) * multiplier + ema_values[-1]
        ema_values.append(round(ema, 2))
    
    return ema_values


def calculate_rsi(klines: List[dict], period: int = 14) -> List[Optional[float]]:
    """
    计算相对强弱指标 (Relative Strength Index)
    
    Args:
        klines: K线数据列表
        period: 计算周期，默认14
        
    Returns:
        RSI数值列表
    """
    if not klines or len(klines) < period + 1:
        return []
    
    rsi_values = [None] * period
    
    # 计算价格变化
    changes = []
    for i in range(1, len(klines)):
        changes.append(klines[i]["close"] - klines[i-1]["close"])
    
    # 计算初始平均涨跌
    gains = [max(0, c) for c in changes[:period]]
    losses = [abs(min(0, c)) for c in changes[:period]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        rsi_values.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_values.append(round(100 - (100 / (1 + rs)), 2))
    
    # 计算后续RSI
    for i in range(period, len(changes)):
        gain = max(0, changes[i])
        loss = abs(min(0, changes[i]))
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        if avg_loss == 0:
            rsi_values.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(round(100 - (100 / (1 + rs)), 2))
    
    return rsi_values


def calculate_macd(klines: List[dict], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    计算MACD指标
    
    Args:
        klines: K线数据列表
        fast: 快线周期，默认12
        slow: 慢线周期，默认26
        signal: 信号线周期，默认9
        
    Returns:
        包含 dif, dea, macd 的字典
    """
    if not klines or len(klines) < slow:
        return {"dif": [], "dea": [], "macd": []}
    
    # 计算快慢EMA
    ema_fast = calculate_ema(klines, fast)
    ema_slow = calculate_ema(klines, slow)
    
    # 计算DIF
    dif = []
    for i in range(len(klines)):
        if ema_fast[i] is None or ema_slow[i] is None:
            dif.append(None)
        else:
            dif.append(round(ema_fast[i] - ema_slow[i], 2))
    
    # 计算DEA (DIF的EMA)
    dif_for_dea = [{"close": d} for d in dif if d is not None]
    dea_raw = calculate_ema(dif_for_dea, signal) if len(dif_for_dea) >= signal else []
    
    # 对齐DEA
    dea = [None] * (len(dif) - len(dea_raw)) + dea_raw
    
    # 计算MACD柱
    macd = []
    for i in range(len(dif)):
        if dif[i] is None or dea[i] is None:
            macd.append(None)
        else:
            macd.append(round((dif[i] - dea[i]) * 2, 2))
    
    return {"dif": dif, "dea": dea, "macd": macd}


def calculate_bollinger_bands(klines: List[dict], period: int = 20, std_dev: float = 2.0) -> dict:
    """
    计算布林带 (Bollinger Bands)
    
    Args:
        klines: K线数据列表
        period: 计算周期，默认20
        std_dev: 标准差倍数，默认2
        
    Returns:
        包含 upper, middle, lower 的字典
    """
    if not klines or len(klines) < period:
        return {"upper": [], "middle": [], "lower": []}
    
    import math
    
    upper = []
    middle = []
    lower = []
    
    for i in range(len(klines)):
        if i < period - 1:
            upper.append(None)
            middle.append(None)
            lower.append(None)
        else:
            closes = [kline["close"] for kline in klines[i-period+1:i+1]]
            ma = sum(closes) / period
            
            # 计算标准差
            variance = sum((c - ma) ** 2 for c in closes) / period
            std = math.sqrt(variance)
            
            middle.append(round(ma, 2))
            upper.append(round(ma + std_dev * std, 2))
            lower.append(round(ma - std_dev * std, 2))
    
    return {"upper": upper, "middle": middle, "lower": lower}
