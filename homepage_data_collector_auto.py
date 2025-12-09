#!/usr/bin/env python3
"""
首页数据自动采集器 - Google Drive版本
每10分钟自动从Google Drive下载并解析最新的txt文件
"""

import requests
import re
import sqlite3
from datetime import datetime, timedelta
import pytz
import time
import sys

# 配置
PARENT_FOLDER_ID = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"
DB_PATH = 'homepage_data.db'
COLLECTION_INTERVAL = 600  # 10分钟

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_beijing_time():
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz)

def find_today_folder():
    """查找今天的文件夹ID"""
    beijing_now = get_beijing_time()
    today_str = beijing_now.strftime('%Y-%m-%d')
    
    parent_url = f"https://drive.google.com/drive/folders/{PARENT_FOLDER_ID}"
    
    try:
        response = requests.get(parent_url, headers=headers, timeout=20)
        html = response.text
        
        # 查找今天日期对应的文件夹ID
        folder_entries = re.findall(r'"([\w-]{28,33})"[^}]{0,500}"' + re.escape(today_str) + '"', html)
        
        if folder_entries:
            for folder_id in set(folder_entries):
                # 验证文件夹
                test_url = f"https://drive.google.com/drive/folders/{folder_id}"
                test_response = requests.get(test_url, headers=headers, timeout=15)
                
                if today_str in test_response.text and '.txt' in test_response.text:
                    print(f"✓ 找到今天的文件夹: {folder_id}")
                    return folder_id
        
        print(f"✗ 未找到今天 ({today_str}) 的文件夹")
        return None
        
    except Exception as e:
        print(f"✗ 查找文件夹失败: {e}")
        return None

def download_latest_file(folder_id):
    """下载最新的txt文件"""
    beijing_now = get_beijing_time()
    today_str = beijing_now.strftime('%Y-%m-%d')
    
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    
    try:
        response = requests.get(folder_url, headers=headers, timeout=20)
        html = response.text
        
        # 查找所有今天的txt文件
        txt_pattern = rf'{re.escape(today_str)}_\d{{4}}\.txt'
        txt_files = re.findall(txt_pattern, html)
        
        if not txt_files:
            print(f"✗ 文件夹中没有找到txt文件")
            return None
        
        txt_files = sorted(set(txt_files), reverse=True)
        latest_file = txt_files[0]
        
        print(f"最新文件: {latest_file}")
        
        # 查找所有可能的文件ID并尝试下载
        all_ids = re.findall(r'"([\w-]{28,33})"', html)
        
        for file_id in list(set(all_ids)):
            try:
                download_url = f"https://drive.google.com/uc?id={file_id}"
                file_response = requests.get(download_url, timeout=10, allow_redirects=True)
                
                if file_response.status_code == 200 and len(file_response.content) > 100:
                    # 尝试解码
                    try:
                        content = file_response.content.decode('gbk')
                        if '透明标签' in content and '急涨' in content:
                            print(f"✓ 成功下载文件 (ID: {file_id})")
                            return content
                    except:
                        pass
            except:
                pass
        
        print("✗ 无法下载文件内容")
        return None
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return None

def parse_content(content):
    """解析文件内容"""
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
                        'update_time': parts[5],
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
                except:
                    pass
    
    return summary_data, coin_data_list

def save_to_database(summary_data, coin_data_list):
    """保存到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    beijing_time = get_beijing_time()
    record_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 插入汇总数据
    cursor.execute("""
        INSERT INTO summary_data (
            rise_total, fall_total, five_states, rise_fall_ratio,
            green_count, green_percent, count_times, diff_result, record_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary_data.get('rise_total', 0),
        summary_data.get('fall_total', 0),
        summary_data.get('five_states', ''),
        summary_data.get('rise_fall_ratio', 0.0),
        summary_data.get('green_count', 0),
        summary_data.get('green_percent', 0.0),
        summary_data.get('count_times', 0),
        summary_data.get('diff_result', 0.0),
        record_time
    ))
    
    summary_id = cursor.lastrowid
    
    # 插入币种数据
    for coin in coin_data_list:
        cursor.execute("""
            INSERT INTO coin_details (
                summary_id, seq_num, coin_name, rise_speed, rise_signal,
                fall_signal, update_time, history_high, high_time,
                drop_from_high, change_24h, ranking, current_price,
                low_ratio, high_ratio, record_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
            coin['ranking'],
            coin['current_price'],
            coin['low_ratio'],
            coin['high_ratio'],
            record_time
        ))
    
    conn.commit()
    conn.close()
    
    return summary_id

def collect_once():
    """执行一次数据采集"""
    beijing_now = get_beijing_time()
    print(f"\n{'='*60}")
    print(f"[{beijing_now.strftime('%Y-%m-%d %H:%M:%S')}] 开始数据采集")
    print(f"{'='*60}")
    
    # 1. 查找今天的文件夹
    folder_id = find_today_folder()
    if not folder_id:
        print("✗ 采集失败：无法找到今天的文件夹")
        return False
    
    # 2. 下载最新文件
    content = download_latest_file(folder_id)
    if not content:
        print("✗ 采集失败：无法下载文件")
        return False
    
    # 3. 解析数据
    summary_data, coin_data_list = parse_content(content)
    
    if not summary_data:
        print("✗ 采集失败：数据解析错误")
        return False
    
    # 4. 保存到数据库
    summary_id = save_to_database(summary_data, coin_data_list)
    
    print(f"\n✓ 采集成功！")
    print(f"  汇总ID: {summary_id}")
    print(f"  急涨: {summary_data.get('rise_total', 0)}")
    print(f"  急跌: {summary_data.get('fall_total', 0)}")
    print(f"  比值: {summary_data.get('rise_fall_ratio', 0)}")
    print(f"  差值: {summary_data.get('diff_result', 0)}")
    print(f"  币种数: {len(coin_data_list)}")
    
    return True

def run_collector():
    """持续运行采集器"""
    print("首页数据自动采集器已启动")
    print(f"采集间隔: {COLLECTION_INTERVAL} 秒 ({COLLECTION_INTERVAL//60} 分钟)")
    print("="*60)
    
    while True:
        try:
            collect_once()
        except Exception as e:
            print(f"✗ 采集异常: {e}")
            import traceback
            traceback.print_exc()
        
        beijing_now = get_beijing_time()
        next_time = beijing_now + timedelta(seconds=COLLECTION_INTERVAL)
        print(f"\n下次采集时间: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        time.sleep(COLLECTION_INTERVAL)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 单次执行模式
        collect_once()
    else:
        # 持续运行模式
        run_collector()

