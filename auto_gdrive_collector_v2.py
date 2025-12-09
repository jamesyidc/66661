#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动 Google Drive 数据采集器 V2
使用 Playwright 定期从 Google Drive 获取最新数据并保存到数据库
"""

import asyncio
import sqlite3
import time
from datetime import datetime, timedelta
import pytz
import signal
import sys
from panic_wash_reader_v5 import PanicWashReaderV5

# 配置
DB_PATH = 'homepage_data.db'
BEIJING_TZ = pytz.timezone('Asia/Shanghai')
COLLECTION_INTERVAL = 600  # 10分钟 = 600秒

# 全局变量
running = True


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    global running
    print('\n\n收到停止信号，正在安全退出...')
    running = False


def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建汇总数据表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summary_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rise_total INTEGER,
            fall_total INTEGER,
            five_states TEXT,
            rise_fall_ratio REAL,
            green_count INTEGER,
            green_percent REAL,
            count_times INTEGER,
            all_green_score REAL,
            price_lowest_score REAL,
            price_new_high INTEGER,
            fall_count INTEGER,
            diff_result REAL,
            record_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建币种详细数据表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coin_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER,
            seq_num INTEGER,
            coin_name TEXT,
            rise_speed REAL,
            rise_signal INTEGER,
            fall_signal INTEGER,
            update_time TEXT,
            history_high REAL,
            high_time TEXT,
            drop_from_high REAL,
            change_24h REAL,
            plus_4_percent INTEGER,
            minus_3_percent INTEGER,
            ranking INTEGER,
            current_price REAL,
            high_ratio REAL,
            low_ratio REAL,
            anomaly TEXT,
            record_time TEXT,
            FOREIGN KEY (summary_id) REFERENCES summary_data(id)
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_summary_time 
        ON summary_data(record_time)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_coin_time 
        ON coin_details(record_time)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_coin_summary 
        ON coin_details(summary_id)
    """)
    
    conn.commit()
    conn.close()
    print("✓ 数据库初始化完成")


def save_to_database(data):
    """
    保存数据到数据库
    Args:
        data: 从 panic_wash_reader_v5 获取的数据
    Returns:
        bool: 是否保存成功
    """
    if not data:
        print("✗ 数据为空，跳过保存")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取当前北京时间
        beijing_now = datetime.now(BEIJING_TZ)
        record_time = beijing_now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 插入汇总数据
        cursor.execute("""
            INSERT INTO summary_data (
                rise_total, fall_total, five_states, rise_fall_ratio,
                green_count, green_percent, count_times, all_green_score,
                price_lowest_score, price_new_high, fall_count, diff_result,
                record_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('rise_total', 0),
            data.get('fall_total', 0),
            data.get('five_states', ''),
            data.get('rise_fall_ratio', 0.0),
            data.get('green_count', 0),
            0.0,  # green_percent
            data.get('count_times', 0),
            0.0,  # all_green_score
            0.0,  # price_lowest_score
            0,    # price_new_high
            0,    # fall_count
            data.get('diff_result', 0.0),
            record_time
        ))
        
        summary_id = cursor.lastrowid
        
        # 插入币种详细数据
        coins_saved = 0
        for coin in data.get('coins', []):
            cursor.execute("""
                INSERT INTO coin_details (
                    summary_id, seq_num, coin_name, rise_speed, rise_signal,
                    fall_signal, current_price, change_24h, record_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                summary_id,
                coin.get('seq_num', 0),
                coin.get('coin_name', ''),
                coin.get('rise_speed', 0.0),
                coin.get('rise_signal', 0),
                coin.get('fall_signal', 0),
                coin.get('current_price', 0.0),
                coin.get('change_24h', 0.0),
                record_time
            ))
            coins_saved += 1
        
        conn.commit()
        conn.close()
        
        print(f"✓ 数据保存成功: ID={summary_id}, 急涨={data.get('rise_total')}, 急跌={data.get('fall_total')}, 币种={coins_saved}")
        return True
        
    except Exception as e:
        print(f"✗ 保存数据失败: {e}")
        return False


async def collect_once():
    """执行一次数据采集"""
    beijing_now = datetime.now(BEIJING_TZ)
    print(f"\n{'='*60}")
    print(f"开始采集数据: {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # 使用 Playwright 获取最新数据
        reader = PanicWashReaderV5()
        data = await reader.get_data()
        
        if data:
            # 保存到数据库
            success = save_to_database(data)
            
            if success:
                print(f"\n✓ 采集成功:")
                print(f"  文件名: {data.get('filename')}")
                print(f"  急涨: {data.get('rise_total')}")
                print(f"  急跌: {data.get('fall_total')}")
                print(f"  比值: {data.get('rise_fall_ratio')}")
                print(f"  差值: {data.get('diff_result')}")
                print(f"  币种数量: {len(data.get('coins', []))}")
            else:
                print("\n✗ 数据保存失败")
        else:
            print("\n✗ 数据获取失败")
            
    except Exception as e:
        print(f"\n✗ 采集出错: {e}")


async def run_collector():
    """运行自动采集器（持续运行）"""
    print("\n" + "="*60)
    print("🚀 自动 Google Drive 数据采集器 V2 启动")
    print("="*60)
    print(f"采集间隔: {COLLECTION_INTERVAL}秒 ({COLLECTION_INTERVAL//60}分钟)")
    print(f"数据库路径: {DB_PATH}")
    print(f"使用技术: Playwright 浏览器自动化")
    print("按 Ctrl+C 停止采集器")
    print("="*60)
    
    # 初始化数据库
    init_database()
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 立即执行一次采集
    await collect_once()
    
    # 持续采集
    while running:
        beijing_now = datetime.now(BEIJING_TZ)
        next_collection_time = beijing_now + timedelta(seconds=COLLECTION_INTERVAL)
        
        print(f"\n⏰ 下次采集时间: {next_collection_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💤 等待 {COLLECTION_INTERVAL}秒...")
        
        # 分段等待，以便能够响应停止信号
        for i in range(COLLECTION_INTERVAL):
            if not running:
                break
            await asyncio.sleep(1)
        
        if running:
            await collect_once()
    
    print("\n采集器已安全停止")


async def run_once_mode():
    """只执行一次采集（测试模式）"""
    print("\n" + "="*60)
    print("🧪 测试模式: 执行一次数据采集")
    print("="*60)
    
    init_database()
    await collect_once()
    
    print("\n✓ 测试完成")


def get_collection_status():
    """获取采集状态信息"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取最新记录
        cursor.execute("""
            SELECT id, rise_total, fall_total, rise_fall_ratio, diff_result, record_time
            FROM summary_data
            ORDER BY id DESC
            LIMIT 1
        """)
        latest = cursor.fetchone()
        
        # 获取总记录数
        cursor.execute("SELECT COUNT(*) FROM summary_data")
        total_count = cursor.fetchone()[0]
        
        # 获取今天的记录数
        beijing_now = datetime.now(BEIJING_TZ)
        today_str = beijing_now.strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) FROM summary_data
            WHERE record_time LIKE ?
        """, (f"{today_str}%",))
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'latest': latest,
            'total_count': total_count,
            'today_count': today_count
        }
    except Exception as e:
        print(f"获取状态失败: {e}")
        return None


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            # 测试模式：只执行一次
            asyncio.run(run_once_mode())
        elif sys.argv[1] == '--status':
            # 显示采集状态
            status = get_collection_status()
            if status:
                print("\n" + "="*60)
                print("📊 采集状态")
                print("="*60)
                print(f"总记录数: {status['total_count']}")
                print(f"今日记录数: {status['today_count']}")
                
                if status['latest']:
                    latest = status['latest']
                    print(f"\n最新记录:")
                    print(f"  ID: {latest[0]}")
                    print(f"  急涨: {latest[1]}")
                    print(f"  急跌: {latest[2]}")
                    print(f"  比值: {latest[3]}")
                    print(f"  差值: {latest[4]}")
                    print(f"  时间: {latest[5]}")
                else:
                    print("\n暂无记录")
                print("="*60)
        else:
            print("用法:")
            print("  python3 auto_gdrive_collector_v2.py           # 持续运行")
            print("  python3 auto_gdrive_collector_v2.py --once    # 执行一次（测试）")
            print("  python3 auto_gdrive_collector_v2.py --status  # 查看状态")
    else:
        # 默认：持续运行
        asyncio.run(run_collector())
