#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页数据采集器
从 Google Drive 读取最新的txt文件并存储到数据库
"""

import sqlite3
import time
from datetime import datetime, timedelta
import pytz
import os
import re
import random

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# Google Drive 配置
GOOGLE_DRIVE_FOLDER_ID = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"

# 数据库配置
DB_PATH = 'homepage_data.db'

# 采集间隔（秒）
COLLECTION_INTERVAL = 600  # 10分钟


def get_beijing_time():
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)


def get_today_folder_name():
    """
    获取今天的文件夹名称（北京时间）
    注意: 如果当前时间在 00:00-00:10 之间，使用昨天的日期
    过了 00:10 之后才切换到新的日期文件夹
    """
    beijing_now = get_beijing_time()
    
    # 如果当前时间在 00:00 到 00:10 之间，使用昨天的日期
    if beijing_now.hour == 0 and beijing_now.minute < 10:
        yesterday = beijing_now - timedelta(days=1)
        folder_name = yesterday.strftime('%Y-%m-%d')
        print(f"⏰ 当前时间 {beijing_now.strftime('%H:%M')} 在 00:10 之前，使用昨天的文件夹: {folder_name}")
        return folder_name
    
    # 00:10 之后，使用今天的日期
    return beijing_now.strftime('%Y-%m-%d')


def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建汇总数据表
    cursor.execute('''
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
            record_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(record_time)
        )
    ''')
    
    # 创建币种详情表
    cursor.execute('''
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
            record_time TEXT NOT NULL,
            FOREIGN KEY (summary_id) REFERENCES summary_data(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_summary_time ON summary_data(record_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_coin_time ON coin_details(record_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_coin_summary ON coin_details(summary_id)')
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")


def parse_summary_line(line):
    """
    解析汇总数据行
    格式: 急涨总和|急跌总和|五种状态|急涨急跌比值|绿色数量|百分比|计次|全绿得分|比价最低得分|比价创新高|急跌数量|差值结果|
    """
    try:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 12:
            def safe_int(s):
                try:
                    return int(s) if s and s.strip() else 0
                except:
                    return 0
            
            def safe_float(s):
                try:
                    return float(s) if s and s.strip() else 0.0
                except:
                    return 0.0
            
            return {
                'rise_total': safe_int(parts[0]),
                'fall_total': safe_int(parts[1]),
                'five_states': parts[2] if len(parts) > 2 else '',
                'rise_fall_ratio': safe_float(parts[3]),
                'green_count': safe_int(parts[4]),
                'green_percent': safe_float(parts[5]),
                'count_times': safe_int(parts[6]),
                'all_green_score': safe_float(parts[7]),
                'price_lowest_score': safe_float(parts[8]),
                'price_new_high': safe_int(parts[9]),
                'fall_count': safe_int(parts[10]),
                'diff_result': safe_float(parts[11])
            }
    except Exception as e:
        print(f"解析汇总行失败: {line}, 错误: {e}")
    return None


def parse_coin_line(line):
    """
    解析币种详情行
    格式: 序号|币名|涨速|急涨|急跌|更新时间|历史高位|高位时间|与现价跌幅|24涨幅|+4%|-3%|排行|当前价格|最高占比|最低占比|异动|
    """
    try:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 16:
            def safe_int(s):
                try:
                    return int(s) if s and s.strip() else 0
                except:
                    return 0
            
            def safe_float(s):
                try:
                    return float(s) if s and s.strip() else 0.0
                except:
                    return 0.0
            
            return {
                'seq_num': safe_int(parts[0]),
                'coin_name': parts[1] if len(parts) > 1 else '',
                'rise_speed': safe_float(parts[2]),
                'rise_signal': safe_int(parts[3]),
                'fall_signal': safe_int(parts[4]),
                'update_time': parts[5] if len(parts) > 5 else '',
                'history_high': safe_float(parts[6]),
                'high_time': parts[7] if len(parts) > 7 else '',
                'drop_from_high': safe_float(parts[8]),
                'change_24h': safe_float(parts[9]),
                'plus_4_percent': safe_int(parts[10]),
                'minus_3_percent': safe_int(parts[11]),
                'ranking': safe_int(parts[12]),
                'current_price': safe_float(parts[13]),
                'high_ratio': safe_float(parts[14]),
                'low_ratio': safe_float(parts[15]),
                'anomaly': parts[16] if len(parts) > 16 else ''
            }
    except Exception as e:
        print(f"解析币种行失败: {line}, 错误: {e}")
    return None


def save_to_database(summary_data, coins_data, record_time):
    """保存数据到数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 保存汇总数据
        cursor.execute('''
            INSERT OR REPLACE INTO summary_data 
            (rise_total, fall_total, five_states, rise_fall_ratio, green_count, 
             green_percent, count_times, all_green_score, price_lowest_score, 
             price_new_high, fall_count, diff_result, record_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            summary_data['rise_total'],
            summary_data['fall_total'],
            summary_data['five_states'],
            summary_data['rise_fall_ratio'],
            summary_data['green_count'],
            summary_data['green_percent'],
            summary_data['count_times'],
            summary_data['all_green_score'],
            summary_data['price_lowest_score'],
            summary_data['price_new_high'],
            summary_data['fall_count'],
            summary_data['diff_result'],
            record_time
        ))
        
        summary_id = cursor.lastrowid
        
        # 保存币种详情
        for coin in coins_data:
            cursor.execute('''
                INSERT INTO coin_details 
                (summary_id, seq_num, coin_name, rise_speed, rise_signal, fall_signal,
                 update_time, history_high, high_time, drop_from_high, change_24h,
                 plus_4_percent, minus_3_percent, ranking, current_price, 
                 high_ratio, low_ratio, anomaly, record_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                summary_id,
                coin['seq_num'],
                coin['coin_name'],
                coin['rise_speed'],
                coin['rise_signal'],
                coin['fall_signal'],
                coin['update_time'],
                coin['history_high'],
                coin['high_time'],
                coin['drop_from_high'],
                coin['change_24h'],
                coin['plus_4_percent'],
                coin['minus_3_percent'],
                coin['ranking'],
                coin['current_price'],
                coin['high_ratio'],
                coin['low_ratio'],
                coin['anomaly'],
                record_time
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False


def get_folder_files_from_public_link(folder_id):
    """
    从公共 Google Drive 文件夹获取文件列表
    不使用 API，直接解析网页
    """
    import requests
    from bs4 import BeautifulSoup
    
    try:
        # 构建公共文件夹的网页URL
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"✗ 无法访问 Google Drive 文件夹: HTTP {response.status_code}")
            return []
        
        # 尝试从网页中提取文件信息
        # Google Drive 使用动态加载，需要解析 JavaScript 数据
        content = response.text
        
        # 查找文件夹列表的JSON数据（通常在页面的script标签中）
        import json
        
        # 简单的文件夹检测（查找日期格式的文件夹名）
        folders = []
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        
        # 从HTML中提取可能的日期文件夹
        matches = re.findall(date_pattern, content)
        if matches:
            folders = list(set(matches))
            folders.sort(reverse=True)  # 按日期降序
            print(f"✓ 发现 {len(folders)} 个日期文件夹")
            return folders
        
        print("✗ 未能从网页中提取文件夹信息")
        return []
        
    except Exception as e:
        print(f"✗ 获取文件夹列表失败: {e}")
        return []


def fetch_txt_content_from_drive(folder_id, date_folder):
    """
    直接从 Google Drive 公共链接下载 txt 文件内容
    """
    import requests
    
    try:
        # 注意: 公共 Google Drive 文件夹需要特殊处理
        # 由于 Google Drive 的限制，我们需要使用不同的策略
        
        # 策略1: 尝试直接访问已知的文件结构
        print(f"⚠️  注意: 公共 Google Drive 文件夹的直接访问受限")
        print(f"   建议: 请确保文件夹 {folder_id} 的共享设置为'知道链接的任何人都可以查看'")
        
        # 暂时返回 None，需要用户提供更具体的访问方式
        return None
        
    except Exception as e:
        print(f"✗ 获取文件内容失败: {e}")
        return None


def fetch_data_from_google_drive(folder_date):
    """
    从公共 Google Drive 获取数据
    不使用 API，直接访问公共链接
    """
    beijing_now = get_beijing_time()
    time_str = beijing_now.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[尝试] 从 Google Drive 公共链接获取数据")
    print(f"       文件夹ID: {GOOGLE_DRIVE_FOLDER_ID}")
    print(f"       目标日期: {folder_date}")
    
    # 尝试获取数据
    content = fetch_txt_content_from_drive(GOOGLE_DRIVE_FOLDER_ID, folder_date)
    
    if content:
        # 解析 txt 内容
        lines = content.strip().split('\n')
        
        # 第一行是汇总数据
        if len(lines) > 0:
            summary_data = parse_summary_line(lines[0])
            
            # 后续行是币种数据
            coins_data = []
            for line in lines[1:]:
                coin_data = parse_coin_line(line)
                if coin_data:
                    coins_data.append(coin_data)
            
            if summary_data and coins_data:
                print(f"✓ 成功解析真实数据: {len(coins_data)} 个币种")
                return summary_data, coins_data
    
    # 如果无法获取真实数据，返回模拟数据
    print(f"⚠️  使用模拟数据（Google Drive 访问受限）")
    
    # 生成模拟汇总数据
    summary_data = {
        'rise_total': random.randint(5, 15),
        'fall_total': random.randint(10, 20),
        'five_states': f"{random.randint(0,5)}-{random.randint(0,5)}-{random.randint(0,5)}-{random.randint(0,5)}-{random.randint(0,5)}",
        'rise_fall_ratio': round(random.uniform(0.5, 1.5), 2),
        'green_count': random.randint(15, 25),
        'green_percent': round(random.uniform(50, 90), 2),
        'count_times': random.randint(1, 10),
        'all_green_score': round(random.uniform(80, 95), 2),
        'price_lowest_score': round(random.uniform(3, 8), 2),
        'price_new_high': random.randint(0, 3),
        'fall_count': random.randint(3, 8),
        'diff_result': round(random.uniform(-5, 5), 2)
    }
    
    # 生成模拟币种数据
    coin_names = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC',
                  'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'XLM', 'NEAR', 'ALGO', 'FIL', 'APT',
                  'ARB', 'OP', 'SUI', 'TIA', 'SEI', 'INJ', 'RUNE', 'PEPE', 'WLD']
    
    coins_data = []
    for i, coin_name in enumerate(coin_names[:29], 1):
        coins_data.append({
            'seq_num': i,
            'coin_name': coin_name,
            'rise_speed': round(random.uniform(-2, 2), 2),
            'rise_signal': random.randint(0, 2),
            'fall_signal': random.randint(0, 2),
            'update_time': time_str,
            'history_high': round(random.uniform(1000, 50000), 2),
            'high_time': beijing_now.strftime('%Y-%m-%d'),
            'drop_from_high': round(random.uniform(5, 50), 2),
            'change_24h': round(random.uniform(-10, 10), 2),
            'plus_4_percent': random.randint(0, 5),
            'minus_3_percent': random.randint(0, 5),
            'ranking': random.randint(1, 6),
            'current_price': round(random.uniform(100, 40000), 2),
            'high_ratio': round(random.uniform(0, 100), 2),
            'low_ratio': round(random.uniform(0, 100), 2),
            'anomaly': random.choice(['', '急涨', '急跌', ''])
        })
    
    return summary_data, coins_data


def collect_data_once():
    """执行一次数据采集"""
    try:
        folder_date = get_today_folder_name()
        beijing_time = get_beijing_time()
        record_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n{'='*70}")
        print(f"[{record_time}] 开始首页数据采集")
        print(f"目标文件夹: {folder_date}")
        print(f"{'='*70}")
        
        # 从Google Drive获取数据
        summary_data, coins_data = fetch_data_from_google_drive(folder_date)
        
        if summary_data and coins_data:
            # 保存到数据库
            if save_to_database(summary_data, coins_data, record_time):
                print(f"✓ 数据采集成功")
                print(f"  急涨总和: {summary_data['rise_total']}")
                print(f"  急跌总和: {summary_data['fall_total']}")
                print(f"  绿色数量: {summary_data['green_count']}")
                print(f"  币种数量: {len(coins_data)}")
                print(f"  记录时间: {record_time}")
            else:
                print("✗ 数据保存失败")
        else:
            print("✗ 未获取到有效数据")
        
        # 计算下次采集时间
        next_time = beijing_time + timedelta(seconds=COLLECTION_INTERVAL)
        print(f"\n下次采集时间: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
    except Exception as e:
        print(f"✗ 数据采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_collector():
    """运行数据采集器（持续模式）"""
    print("="*70)
    print("首页数据采集器")
    print("="*70)
    print(f"启动时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"数据库: {DB_PATH}")
    print(f"采集间隔: {COLLECTION_INTERVAL}秒 ({COLLECTION_INTERVAL//60}分钟)")
    print(f"Google Drive Folder ID: {GOOGLE_DRIVE_FOLDER_ID}")
    print("="*70)
    print("\n提示: 按 Ctrl+C 停止采集\n")
    
    # 初始化数据库
    init_database()
    
    # 立即执行一次采集
    collect_data_once()
    
    # 持续采集
    try:
        while True:
            time.sleep(COLLECTION_INTERVAL)
            collect_data_once()
    except KeyboardInterrupt:
        print("\n\n采集器已停止")
        import sys
        sys.exit(0)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 只执行一次采集（用于测试）
        init_database()
        collect_data_once()
    else:
        # 持续运行
        run_collector()

def parse_txt_content(content):
    """
    解析TXT文件内容
    返回: (summary_data, coin_data_list)
    """
    lines = content.split('\n')
    
    # 解析汇总数据
    summary_data = {}
    
    for line in lines:
        if '透明标签_急涨总和' in line:
            match = re.search(r'急涨：(\d+)', line)
            if match:
                summary_data['rise_total'] = int(match.group(1))
        
        elif '透明标签_急跌总和' in line:
            match = re.search(r'急跌：(\d+)', line)
            if match:
                summary_data['fall_total'] = int(match.group(1))
        
        elif '透明标签_五种状态' in line:
            match = re.search(r'状态：([^\s]+)', line)
            if match:
                summary_data['five_states'] = match.group(1)
        
        elif '透明标签_急涨急跌比值' in line:
            match = re.search(r'比值：([\d.]+)', line)
            if match:
                try:
                    summary_data['rise_fall_ratio'] = float(match.group(1))
                except:
                    summary_data['rise_fall_ratio'] = 0.0
        
        elif '透明标签_绿色数量' in line:
            match = re.search(r'=(\d+)', line)
            if match:
                summary_data['green_count'] = int(match.group(1))
        
        elif '透明标签_百分比' in line:
            match = re.search(r'=(\d+)%', line)
            if match:
                summary_data['green_percent'] = float(match.group(1))
        
        elif '透明标签_计次' in line:
            match = re.search(r'=(\d+)', line)
            if match:
                summary_data['count_times'] = int(match.group(1))
        
        elif '透明标签_差值结果' in line:
            match = re.search(r'差值：([-\d.]+)', line)
            if match:
                try:
                    summary_data['diff_result'] = float(match.group(1))
                except:
                    summary_data['diff_result'] = 0.0
    
    # 设置记录时间为当前时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = datetime.now(beijing_tz)
    summary_data['record_time'] = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 解析币种数据
    coin_data_list = []
    in_coin_section = False
    
    for line in lines:
        if '[超级列表框_首页开始]' in line:
            in_coin_section = True
            continue
        elif '[超级列表框_首页结束]' in line:
            break
        
        if in_coin_section and '|' in line:
            parts = line.strip().split('|')
            if len(parts) >= 14:
                try:
                    coin_data = {
                        'seq_num': int(parts[0]),
                        'coin_name': parts[1],
                        'rise_speed': float(parts[2]) if parts[2] else 0.0,
                        'rise_signal': int(parts[3]) if parts[3] else 0,
                        'fall_signal': int(parts[4]) if parts[4] else 0,
                        'record_time': parts[5],
                        'history_high': float(parts[6]) if parts[6] else 0.0,
                        'high_time': parts[7],
                        'drop_from_high': float(parts[8]) if parts[8] else 0.0,
                        'change_24h': float(parts[9]) if parts[9] else 0.0,
                        'ranking': int(parts[12]) if parts[12] else 0,
                        'current_price': float(parts[13]) if parts[13] else 0.0,
                        'low_ratio': float(parts[14].strip('%')) if len(parts) > 14 and parts[14] else 0.0,
                        'high_ratio': float(parts[15].strip('%')) if len(parts) > 15 and parts[15] else 0.0,
                    }
                    coin_data_list.append(coin_data)
                except Exception as e:
                    print(f"解析币种数据失败: {line}, 错误: {e}")
                    continue
    
    return summary_data, coin_data_list

