#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
30日爆仓历史数据采集器
每小时采集一次，覆盖原有数据
"""

import requests
import sqlite3
import time
import sys
from datetime import datetime
import pytz

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    # 创建30日爆仓历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS liquidation_30days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            long_amount REAL DEFAULT 0,
            short_amount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

def fetch_30days_liquidation():
    """获取30天爆仓数据"""
    try:
        url = "https://api.btc123.fans/bicoin.php?from=30daybaocang"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://history.btc123.fans/'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        json_data = response.json()
        
        # API返回格式: {code: 0, data: {...}, dialog: null}
        if json_data.get('code') != 0:
            print(f"❌ API返回错误码: {json_data.get('code')}")
            return []
        
        data = json_data.get('data', {})
        
        # 解析数据
        result = []
        
        for date_str, coins_data in data.items():
            # 跳过非日期数据
            if not isinstance(date_str, str) or not (date_str.startswith('2024') or date_str.startswith('2025')):
                continue
            
            long_total = 0
            short_total = 0
            
            # 遍历所有币种
            for coin, info in coins_data.items():
                if isinstance(info, dict):
                    # 多单爆仓金额
                    long_amount = float(info.get('totalBlast', 0))
                    # 空单爆仓金额
                    short_amount = float(info.get('totalBlastS', 0))
                    
                    long_total += long_amount
                    short_total += short_amount
            
            total = long_total + short_total
            
            result.append({
                'date': date_str,
                'long_amount': long_total,
                'short_amount': short_total,
                'total_amount': total
            })
        
        # 按日期排序（最新的在前面）
        result.sort(key=lambda x: x['date'], reverse=True)
        
        return result
    
    except Exception as e:
        print(f"❌ 获取30天爆仓数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_liquidation_data(data_list):
    """保存或更新爆仓数据（覆盖模式）"""
    if not data_list:
        print("⚠️ 没有数据需要保存")
        return
    
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        beijing_time = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        
        for item in data_list:
            # 使用 INSERT OR REPLACE 实现覆盖
            cursor.execute('''
                INSERT OR REPLACE INTO liquidation_30days 
                (date, long_amount, short_amount, total_amount, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                item['date'],
                item['long_amount'],
                item['short_amount'],
                item['total_amount'],
                beijing_time
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 成功保存/更新 {len(data_list)} 条30日爆仓数据")
        print(f"   时间: {beijing_time}")
        
    except Exception as e:
        print(f"❌ 保存数据失败: {e}")

def collect_once():
    """执行一次采集"""
    print("\n" + "="*50)
    print(f"开始采集30日爆仓数据...")
    print("="*50)
    
    data = fetch_30days_liquidation()
    
    if data:
        print(f"✅ 获取到 {len(data)} 天的数据")
        save_liquidation_data(data)
    else:
        print("❌ 未获取到数据")

def run_daemon():
    """守护进程模式 - 每小时采集一次"""
    print("\n" + "="*50)
    print("30日爆仓数据采集器启动")
    print("采集间隔: 1小时")
    print("="*50 + "\n")
    
    # 立即执行一次
    collect_once()
    
    # 每小时执行一次
    interval = 3600  # 1小时 = 3600秒
    
    while True:
        try:
            print(f"\n等待下次采集... (间隔: {interval}秒 / 1小时)")
            time.sleep(interval)
            collect_once()
            
        except KeyboardInterrupt:
            print("\n\n收到中断信号，停止采集器...")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 采集过程出错: {e}")
            print("等待60秒后重试...")
            time.sleep(60)

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 只执行一次
        collect_once()
    else:
        # 守护进程模式
        run_daemon()
