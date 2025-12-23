#!/usr/bin/env python3
"""
支撑压力线快照采集器
每1分钟保存一次4种情况的统计数据和符合条件的币种列表
"""

import os
import sys
import time
import sqlite3
import json
import pytz
from datetime import datetime
from typing import Dict, List

# 数据库配置
DB_PATH = os.path.join(os.path.dirname(__file__), 'crypto_data.db')

# 日志文件
LOG_FILE = os.path.join(os.path.dirname(__file__), 'support_resistance_snapshot.log')

def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except Exception as e:
        print(f"写入日志失败: {e}")

def create_snapshot_table():
    """创建快照表（如果不存在）"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建快照表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_resistance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_time TEXT NOT NULL,
                snapshot_date TEXT NOT NULL,
                scenario_1_count INTEGER DEFAULT 0,
                scenario_2_count INTEGER DEFAULT 0,
                scenario_3_count INTEGER DEFAULT 0,
                scenario_4_count INTEGER DEFAULT 0,
                scenario_1_coins TEXT,
                scenario_2_coins TEXT,
                scenario_3_coins TEXT,
                scenario_4_coins TEXT,
                total_coins INTEGER DEFAULT 27,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_snapshot_time 
            ON support_resistance_snapshots(snapshot_time)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_snapshot_date 
            ON support_resistance_snapshots(snapshot_date)
        ''')
        
        conn.commit()
        conn.close()
        log("✅ 快照表检查/创建完成")
        return True
        
    except Exception as e:
        log(f"❌ 创建快照表失败: {e}")
        return False

def get_latest_data() -> List[Dict]:
    """获取最新的支撑压力线数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取每个币种的最新记录
        cursor.execute('''
            SELECT 
                symbol, current_price,
                support_line_1, support_line_2,
                resistance_line_1, resistance_line_2,
                position_s2_r1, position_s1_r2,
                position_s1_r2_upper, position_s1_r1,
                alert_scenario_1, alert_scenario_2,
                alert_scenario_3, alert_scenario_4,
                record_time
            FROM support_resistance_levels
            WHERE id IN (
                SELECT MAX(id)
                FROM support_resistance_levels
                GROUP BY symbol
            )
            ORDER BY symbol
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'symbol': row[0],
                'current_price': row[1],
                'support_line_1': row[2],
                'support_line_2': row[3],
                'resistance_line_1': row[4],
                'resistance_line_2': row[5],
                'position_s2_r1': row[6],
                'position_s1_r2': row[7],
                'position_s1_r2_upper': row[8],
                'position_s1_r1': row[9],
                'alert_scenario_1': bool(row[10]),
                'alert_scenario_2': bool(row[11]),
                'alert_scenario_3': bool(row[12]),
                'alert_scenario_4': bool(row[13]),
                'record_time': row[14]
            })
        
        return results
        
    except Exception as e:
        log(f"❌ 获取最新数据失败: {e}")
        return []

def analyze_scenarios(data_list: List[Dict]) -> Dict:
    """分析4种情况的统计数据"""
    scenario_1_coins = []
    scenario_2_coins = []
    scenario_3_coins = []
    scenario_4_coins = []
    
    for data in data_list:
        symbol = data['symbol']
        
        # 情况1: 支撑2→压力1 (<=5%)
        if data['alert_scenario_1']:
            scenario_1_coins.append({
                'symbol': symbol,
                'current_price': data['current_price'],
                'position': data['position_s2_r1'],
                'support_2': data['support_line_2'],
                'resistance_1': data['resistance_line_1']
            })
        
        # 情况2: 支撑1→压力2 (<=5%)
        if data['alert_scenario_2']:
            scenario_2_coins.append({
                'symbol': symbol,
                'current_price': data['current_price'],
                'position': data['position_s1_r2'],
                'support_1': data['support_line_1'],
                'resistance_2': data['resistance_line_2']
            })
        
        # 情况3: 支撑1→压力2 (>=95%)
        if data['alert_scenario_3']:
            scenario_3_coins.append({
                'symbol': symbol,
                'current_price': data['current_price'],
                'position': data['position_s1_r2_upper'],
                'support_1': data['support_line_1'],
                'resistance_2': data['resistance_line_2']
            })
        
        # 情况4: 支撑1→压力1 (>=95%)
        if data['alert_scenario_4']:
            scenario_4_coins.append({
                'symbol': symbol,
                'current_price': data['current_price'],
                'position': data['position_s1_r1'],
                'support_1': data['support_line_1'],
                'resistance_1': data['resistance_line_1']
            })
    
    return {
        'scenario_1': {
            'count': len(scenario_1_coins),
            'coins': scenario_1_coins
        },
        'scenario_2': {
            'count': len(scenario_2_coins),
            'coins': scenario_2_coins
        },
        'scenario_3': {
            'count': len(scenario_3_coins),
            'coins': scenario_3_coins
        },
        'scenario_4': {
            'count': len(scenario_4_coins),
            'coins': scenario_4_coins
        },
        'total_coins': len(data_list)
    }

def save_snapshot(analysis: Dict) -> bool:
    """保存快照到数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 使用北京时间存储（UTC+8）
        now_beijing = datetime.now(pytz.timezone('Asia/Shanghai'))
        snapshot_time = now_beijing.strftime('%Y-%m-%d %H:%M:%S')
        snapshot_date = now_beijing.strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO support_resistance_snapshots (
                snapshot_time, snapshot_date,
                scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                total_coins
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_time, snapshot_date,
            analysis['scenario_1']['count'],
            analysis['scenario_2']['count'],
            analysis['scenario_3']['count'],
            analysis['scenario_4']['count'],
            json.dumps(analysis['scenario_1']['coins'], ensure_ascii=False),
            json.dumps(analysis['scenario_2']['coins'], ensure_ascii=False),
            json.dumps(analysis['scenario_3']['coins'], ensure_ascii=False),
            json.dumps(analysis['scenario_4']['coins'], ensure_ascii=False),
            analysis['total_coins']
        ))
        
        conn.commit()
        conn.close()
        
        log(f"✅ 快照保存成功: {snapshot_time} | "
            f"情况1:{analysis['scenario_1']['count']} "
            f"情况2:{analysis['scenario_2']['count']} "
            f"情况3:{analysis['scenario_3']['count']} "
            f"情况4:{analysis['scenario_4']['count']}")
        
        return True
        
    except Exception as e:
        log(f"❌ 保存快照失败: {e}")
        return False

def collect_snapshot():
    """采集一次快照"""
    log("=" * 60)
    log("📸 开始采集支撑压力线快照")
    
    # 1. 获取最新数据
    data_list = get_latest_data()
    
    if not data_list:
        log("⚠️ 没有获取到数据")
        return False
    
    log(f"📊 获取到 {len(data_list)} 个币种的最新数据")
    
    # 2. 分析4种情况
    analysis = analyze_scenarios(data_list)
    
    log(f"📈 情况1（接近支撑2）: {analysis['scenario_1']['count']} 个币种")
    log(f"📈 情况2（接近支撑1）: {analysis['scenario_2']['count']} 个币种")
    log(f"📉 情况3（接近压力2）: {analysis['scenario_3']['count']} 个币种")
    log(f"📉 情况4（接近压力1）: {analysis['scenario_4']['count']} 个币种")
    
    # 3. 保存快照
    success = save_snapshot(analysis)
    
    log("=" * 60)
    return success

def main():
    """主函数"""
    log("🎯 支撑压力线快照采集器启动")
    log(f"⏰ 采集间隔: 60秒 (1分钟)")
    log(f"📁 数据库路径: {DB_PATH}")
    
    # 创建表
    if not create_snapshot_table():
        log("❌ 无法创建数据库表，退出")
        return
    
    while True:
        try:
            collect_snapshot()
            log("⏳ 等待60秒后进行下一次采集...")
            time.sleep(60)  # 1分钟
            
        except KeyboardInterrupt:
            log("⚠️ 收到停止信号，正在退出...")
            break
        except Exception as e:
            log(f"❌ 采集出错: {e}")
            log("⏳ 等待60秒后重试...")
            time.sleep(60)

if __name__ == '__main__':
    main()
