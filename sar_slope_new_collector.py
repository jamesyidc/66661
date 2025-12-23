#!/usr/bin/env python3
"""
SAR斜率系统 V2.0 - 重新构建
功能：
1. 判断SAR多空方向
2. 从多空转换点开始计算（SAR空01, SAR空02, ...）
3. 计算连续SAR差值和百分比变化率
4. 计算滚动平均值（当天、3天、7天、15天）
5. 异常检测：偏离平均值>30%触发预警
6. 标记极值点（最低点/最高点）
"""

import sqlite3
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import traceback
import pytz

# 27个监控币种
MONITORED_SYMBOLS = [
    'BTC-USDT-SWAP', 'ETH-USDT-SWAP', 'XRP-USDT-SWAP', 'BNB-USDT-SWAP',
    'SOL-USDT-SWAP', 'LTC-USDT-SWAP', 'DOGE-USDT-SWAP', 'SUI-USDT-SWAP',
    'TRX-USDT-SWAP', 'TON-USDT-SWAP', 'ETC-USDT-SWAP', 'BCH-USDT-SWAP',
    'HBAR-USDT-SWAP', 'XLM-USDT-SWAP', 'FIL-USDT-SWAP', 'LINK-USDT-SWAP',
    'CRO-USDT-SWAP', 'DOT-USDT-SWAP', 'AAVE-USDT-SWAP', 'UNI-USDT-SWAP',
    'NEAR-USDT-SWAP', 'APT-USDT-SWAP', 'CFX-USDT-SWAP', 'CRV-USDT-SWAP',
    'STX-USDT-SWAP', 'LDO-USDT-SWAP', 'TAO-USDT-SWAP'
]

BEIJING_TZ = pytz.timezone('Asia/Shanghai')
DB_PATH = '/home/user/webapp/crypto_data.db'
TIMEFRAME = '5m'
ANOMALY_THRESHOLD = 30.0  # 异常阈值：偏离平均值30%

def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # SAR斜率主数据表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sar_slope_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            datetime_utc TEXT NOT NULL,
            datetime_beijing TEXT NOT NULL,
            
            -- SAR基础数据
            sar_value REAL NOT NULL,
            sar_direction TEXT NOT NULL,  -- 'long' 或 'short'
            
            -- 位置序号（从转换点开始计数）
            sequence_number INTEGER NOT NULL,  -- 第几根K线（空01, 空02, ...）
            
            -- 差值计算
            sar_diff REAL,  -- 与前一根SAR的差值
            sar_diff_percent REAL,  -- 差值百分比
            
            -- 滚动平均值
            avg_1day REAL,  -- 当天平均值
            avg_3day REAL,  -- 3天平均值
            avg_7day REAL,  -- 7天平均值
            avg_15day REAL,  -- 15天平均值
            
            -- 异常检测
            is_anomaly INTEGER DEFAULT 0,  -- 是否异常（0:正常, 1:异常）
            anomaly_type TEXT,  -- 异常类型：'spike'(激增) 或 'drop'(骤降)
            deviation_percent REAL,  -- 偏离平均值的百分比
            
            -- 极值标记
            is_extreme INTEGER DEFAULT 0,  -- 是否极值点（0:否, 1:是）
            extreme_type TEXT,  -- 极值类型：'high'(最高点) 或 'low'(最低点)
            
            -- 价格数据
            price_open REAL,
            price_close REAL,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        )
    """)
    
    # SAR转换点记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sar_direction_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            change_timestamp INTEGER NOT NULL,
            change_datetime_beijing TEXT NOT NULL,
            
            from_direction TEXT NOT NULL,  -- 从哪个方向转换
            to_direction TEXT NOT NULL,    -- 转换到哪个方向
            
            sar_value_at_change REAL NOT NULL,
            price_at_change REAL,
            
            previous_duration INTEGER,  -- 上一个方向持续了多少根K线
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, change_timestamp)
        )
    """)
    
    # SAR当前状态表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sar_current_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL UNIQUE,
            
            current_direction TEXT NOT NULL,  -- 当前方向
            direction_start_timestamp INTEGER NOT NULL,  -- 当前方向开始时间
            direction_start_datetime TEXT NOT NULL,
            current_sequence INTEGER DEFAULT 1,  -- 当前序号
            
            last_sar_value REAL NOT NULL,
            last_timestamp INTEGER NOT NULL,
            last_update_beijing TEXT NOT NULL,
            
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sar_v2_symbol_timestamp 
        ON sar_slope_v2(symbol, timestamp DESC)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sar_v2_direction 
        ON sar_slope_v2(symbol, sar_direction, timestamp DESC)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sar_v2_anomaly 
        ON sar_slope_v2(symbol, is_anomaly, timestamp DESC)
    """)
    
    conn.commit()
    conn.close()
    
    beijing_time = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    print(f"✅ Database initialized at {beijing_time}")

def get_latest_sar_from_markers(symbol: str) -> Optional[Dict]:
    """从kline_technical_markers表获取最新SAR数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, sar, sar_position
        FROM kline_technical_markers
        WHERE symbol = ? AND timeframe = ? AND sar IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 1
    """, (symbol, TIMEFRAME))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'timestamp': row[0],
        'sar': row[1],
        'sar_position': row[2]  # 'above' 或 'below'
    }

def get_price_data(symbol: str, timestamp: int) -> Optional[Tuple[float, float]]:
    """获取开盘价和收盘价"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT open, close FROM okex_kline_ohlc
        WHERE symbol = ? AND timeframe = ? AND timestamp = ?
        LIMIT 1
    """, (symbol, TIMEFRAME, timestamp))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return (row[0], row[1])  # (开盘价, 收盘价)

def get_current_state(symbol: str) -> Optional[Dict]:
    """获取币种当前状态"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT current_direction, direction_start_timestamp, 
               current_sequence, last_sar_value, last_timestamp
        FROM sar_current_state
        WHERE symbol = ?
    """, (symbol,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'current_direction': row[0],
        'direction_start_timestamp': row[1],
        'current_sequence': row[2],
        'last_sar_value': row[3],
        'last_timestamp': row[4]
    }

def update_current_state(symbol: str, direction: str, timestamp: int, 
                         sar_value: float, sequence: int, datetime_beijing: str):
    """更新当前状态"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO sar_current_state 
        (symbol, current_direction, direction_start_timestamp, 
         direction_start_datetime, current_sequence, last_sar_value, 
         last_timestamp, last_update_beijing)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(symbol) DO UPDATE SET
            current_direction = excluded.current_direction,
            direction_start_timestamp = CASE 
                WHEN current_direction != excluded.current_direction 
                THEN excluded.direction_start_timestamp 
                ELSE direction_start_timestamp 
            END,
            direction_start_datetime = CASE 
                WHEN current_direction != excluded.current_direction 
                THEN excluded.direction_start_datetime 
                ELSE direction_start_datetime 
            END,
            current_sequence = excluded.current_sequence,
            last_sar_value = excluded.last_sar_value,
            last_timestamp = excluded.last_timestamp,
            last_update_beijing = excluded.last_update_beijing,
            updated_at = CURRENT_TIMESTAMP
    """, (symbol, direction, timestamp, datetime_beijing, sequence, 
          sar_value, timestamp, datetime_beijing))
    
    conn.commit()
    conn.close()

def record_direction_change(symbol: str, timestamp: int, datetime_beijing: str,
                            from_dir: str, to_dir: str, sar_value: float,
                            price: float, previous_duration: int):
    """记录方向转换"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO sar_direction_changes
        (symbol, change_timestamp, change_datetime_beijing, from_direction, 
         to_direction, sar_value_at_change, price_at_change, previous_duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (symbol, timestamp, datetime_beijing, from_dir, to_dir, 
          sar_value, price, previous_duration))
    
    conn.commit()
    conn.close()

def calculate_diff_and_percent(current_sar: float, previous_sar: float) -> Tuple[float, float]:
    """计算SAR差值和百分比"""
    diff = abs(current_sar - previous_sar)
    percent = (diff / previous_sar * 100) if previous_sar != 0 else 0.0
    return diff, percent

def calculate_rolling_averages(symbol: str, direction: str, sequence_number: int, timestamp: int) -> Dict[str, float]:
    """计算滚动平均值（1天、3天、7天、15天）
    
    重要：计算相同序号位置的差值%平均，不是时间段内所有数据的平均
    例如：序号05的1日均 = 最近1天内所有序号05位置的差值%平均
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 时间范围（天数转换为毫秒）
    periods = {
        'avg_1day': 1,    # 1天
        'avg_3day': 3,    # 3天
        'avg_7day': 7,    # 7天
        'avg_15day': 15   # 15天
    }
    
    averages = {}
    
    for period_name, days in periods.items():
        # 计算时间范围（天数 * 24小时 * 3600秒 * 1000毫秒）
        start_timestamp = timestamp - (days * 24 * 3600 * 1000)
        
        # 查询相同序号位置的差值%平均
        cursor.execute("""
            SELECT AVG(sar_diff_percent)
            FROM sar_slope_v2
            WHERE symbol = ? 
              AND sar_direction = ? 
              AND sequence_number = ?
              AND timestamp >= ? 
              AND timestamp <= ?
              AND sar_diff_percent IS NOT NULL
        """, (symbol, direction, sequence_number, start_timestamp, timestamp))
        
        row = cursor.fetchone()
        averages[period_name] = row[0] if (row and row[0] is not None) else None
    
    conn.close()
    return averages

def detect_anomaly(sar_diff_percent: float, avg_percent: Optional[float]) -> Tuple[bool, Optional[str], Optional[float]]:
    """检测异常：偏离平均值>30%"""
    if avg_percent is None or avg_percent == 0:
        return False, None, None
    
    deviation = abs((sar_diff_percent - avg_percent) / avg_percent * 100)
    
    if deviation > ANOMALY_THRESHOLD:
        anomaly_type = 'spike' if sar_diff_percent > avg_percent else 'drop'
        return True, anomaly_type, deviation
    
    return False, None, None

def find_extreme_points(symbol: str, direction: str, timestamp: int, sar_diff_percent: float) -> Tuple[bool, Optional[str]]:
    """查找极值点（最近50根K线内的最高/最低点）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询最近50根K线的数据
    lookback = 50
    start_timestamp = timestamp - (lookback * 300000)
    
    cursor.execute("""
        SELECT MAX(sar_diff_percent), MIN(sar_diff_percent)
        FROM sar_slope_v2
        WHERE symbol = ? 
          AND sar_direction = ? 
          AND timestamp >= ? 
          AND timestamp <= ?
          AND sar_diff_percent IS NOT NULL
    """, (symbol, direction, start_timestamp, timestamp))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[0] is None:
        return False, None
    
    max_val, min_val = row[0], row[1]
    
    # 判断当前值是否为极值
    if sar_diff_percent == max_val:
        return True, 'high'
    elif sar_diff_percent == min_val:
        return True, 'low'
    
    return False, None

def insert_sar_data(symbol: str, timestamp: int, sar_value: float, 
                    direction: str, sequence: int, price_open: float, price_close: float,
                    sar_diff: Optional[float], sar_diff_percent: Optional[float],
                    averages: Dict, is_anomaly: bool, anomaly_type: Optional[str],
                    deviation_percent: Optional[float], is_extreme: bool, extreme_type: Optional[str]):
    """插入SAR斜率数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    dt_utc = datetime.utcfromtimestamp(timestamp / 1000)
    dt_beijing = dt_utc.replace(tzinfo=pytz.UTC).astimezone(BEIJING_TZ)
    
    datetime_utc = dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    datetime_beijing = dt_beijing.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT OR REPLACE INTO sar_slope_v2
        (symbol, timestamp, datetime_utc, datetime_beijing, sar_value, sar_direction,
         sequence_number, sar_diff, sar_diff_percent, avg_1day, avg_3day, avg_7day, 
         avg_15day, is_anomaly, anomaly_type, deviation_percent, is_extreme, 
         extreme_type, price_open, price_close)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol, timestamp, datetime_utc, datetime_beijing, sar_value, direction,
        sequence, sar_diff, sar_diff_percent, averages.get('avg_1day'), 
        averages.get('avg_3day'), averages.get('avg_7day'), averages.get('avg_15day'),
        1 if is_anomaly else 0, anomaly_type, deviation_percent,
        1 if is_extreme else 0, extreme_type, price_open, price_close
    ))
    
    conn.commit()
    conn.close()

def process_symbol(symbol: str) -> bool:
    """处理单个币种的SAR数据"""
    try:
        # 1. 获取最新SAR数据
        sar_data = get_latest_sar_from_markers(symbol)
        if not sar_data:
            print(f"⚠️  {symbol.replace('-USDT-SWAP', '')}: No SAR data")
            return False
        
        timestamp = sar_data['timestamp']
        sar_value = sar_data['sar']
        
        # 2. 获取价格数据（开盘价和收盘价）
        price_data = get_price_data(symbol, timestamp)
        if not price_data:
            print(f"⚠️  {symbol.replace('-USDT-SWAP', '')}: No price data")
            return False
        
        price_open, price_close = price_data
        
        # 3. 判断SAR方向（核心逻辑）
        # SAR > 开盘价 = 空头区间（做空）
        # SAR < 开盘价 = 多头区间（做多）
        if sar_value > price_open:
            direction = 'short'  # 空头
        else:
            direction = 'long'   # 多头
        
        # 4. 获取当前状态
        current_state = get_current_state(symbol)
        
        dt_beijing = datetime.utcfromtimestamp(timestamp / 1000).replace(
            tzinfo=pytz.UTC).astimezone(BEIJING_TZ)
        datetime_beijing = dt_beijing.strftime('%Y-%m-%d %H:%M:%S')
        
        # 5. 判断是否方向转换
        if current_state is None:
            # 首次运行，初始化
            sequence = 1
            sar_diff = None
            sar_diff_percent = None
            update_current_state(symbol, direction, timestamp, sar_value, 
                               sequence, datetime_beijing)
        elif current_state['current_direction'] != direction:
            # 方向转换！记录转换点
            previous_duration = current_state['current_sequence']
            record_direction_change(symbol, timestamp, datetime_beijing,
                                  current_state['current_direction'], direction,
                                  sar_value, price_close, previous_duration)
            
            # 重置序号
            sequence = 1
            sar_diff = None
            sar_diff_percent = None
            
            update_current_state(symbol, direction, timestamp, sar_value, 
                               sequence, datetime_beijing)
            
            short_name = symbol.replace('-USDT-SWAP', '')
            print(f"🔄 {short_name}: Direction changed {current_state['current_direction']} → {direction}")
        else:
            # 方向未变，序号递增
            sequence = current_state['current_sequence'] + 1
            previous_sar = current_state['last_sar_value']
            
            # 计算差值和百分比
            sar_diff, sar_diff_percent = calculate_diff_and_percent(sar_value, previous_sar)
            
            update_current_state(symbol, direction, timestamp, sar_value, 
                               sequence, datetime_beijing)
        
        # 6. 计算滚动平均值（基于相同序号位置）
        averages = calculate_rolling_averages(symbol, direction, sequence, timestamp)
        
        # 7. 异常检测
        is_anomaly = False
        anomaly_type = None
        deviation_percent = None
        
        if sar_diff_percent is not None and averages.get('avg_3day') is not None:
            is_anomaly, anomaly_type, deviation_percent = detect_anomaly(
                sar_diff_percent, averages['avg_3day']
            )
        
        # 8. 极值点检测
        is_extreme = False
        extreme_type = None
        
        if sar_diff_percent is not None:
            is_extreme, extreme_type = find_extreme_points(
                symbol, direction, timestamp, sar_diff_percent
            )
        
        # 9. 插入数据
        insert_sar_data(
            symbol, timestamp, sar_value, direction, sequence, price_open, price_close,
            sar_diff, sar_diff_percent, averages, is_anomaly, anomaly_type,
            deviation_percent, is_extreme, extreme_type
        )
        
        # 10. 输出信息
        short_name = symbol.replace('-USDT-SWAP', '')
        dir_emoji = '📈' if direction == 'long' else '📉'
        status_parts = [f"{dir_emoji}{sequence:02d}"]
        
        if sar_diff_percent is not None:
            status_parts.append(f"{sar_diff_percent:.5f}%")
        
        if is_anomaly:
            status_parts.append(f"⚠️ {anomaly_type.upper()}")
        
        if is_extreme:
            status_parts.append(f"{'🔺' if extreme_type == 'high' else '🔻'}EXTREME")
        
        print(f"✅ {short_name}: {' '.join(status_parts)}")
        return True
        
    except Exception as e:
        print(f"❌ {symbol.replace('-USDT-SWAP', '')}: {e}")
        traceback.print_exc()
        return False

def collect_all_symbols():
    """采集所有币种"""
    print(f"\n{'='*70}")
    print(f"🔄 SAR Slope V2 Collection - {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    success = 0
    fail = 0
    
    for symbol in MONITORED_SYMBOLS:
        if process_symbol(symbol):
            success += 1
        else:
            fail += 1
    
    print(f"\n📊 Summary: ✅ {success}/{len(MONITORED_SYMBOLS)}  ❌ {fail}/{len(MONITORED_SYMBOLS)}")
    print(f"{'='*70}\n")

def cleanup_old_data():
    """清理16天前的旧数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff = int((datetime.now() - timedelta(days=16)).timestamp() * 1000)
    
    cursor.execute("DELETE FROM sar_slope_v2 WHERE timestamp < ?", (cutoff,))
    deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    if deleted > 0:
        print(f"🧹 Cleaned {deleted} old records (>16 days)")

def main():
    """主循环"""
    print("🚀 SAR Slope V2.0 Collector Starting...")
    print(f"📍 Database: {DB_PATH}")
    print(f"📊 Symbols: {len(MONITORED_SYMBOLS)}")
    print(f"⏱️  Interval: 5 minutes")
    print(f"⚠️  Anomaly Threshold: {ANOMALY_THRESHOLD}%")
    print(f"💾 Retention: 16 days")
    
    init_database()
    collect_all_symbols()
    
    cleanup_counter = 0
    
    while True:
        try:
            time.sleep(300)  # 5分钟
            collect_all_symbols()
            
            cleanup_counter += 1
            if cleanup_counter >= 288:  # 24小时
                cleanup_old_data()
                cleanup_counter = 0
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            time.sleep(60)

if __name__ == '__main__':
    main()
