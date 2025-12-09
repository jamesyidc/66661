#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页数据采集器 V2 - 使用 gdown 从 Google Drive 下载数据
"""

import sqlite3
import time
import re
from datetime import datetime, timedelta
import pytz
import gdown
import requests
import os

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# Google Drive 配置
MAIN_FOLDER_ID = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"

# 数据库配置
DB_PATH = 'homepage_data.db'

# 采集间隔（秒）
COLLECTION_INTERVAL = 600  # 10分钟


def get_beijing_time():
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)


def get_today_folder_name():
    """获取今天的文件夹名称（00:10之前使用昨天）"""
    beijing_now = get_beijing_time()
    if beijing_now.hour == 0 and beijing_now.minute < 10:
        yesterday = beijing_now - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    return beijing_now.strftime('%Y-%m-%d')


def get_date_folder_id(main_folder_id, target_date):
    """获取指定日期文件夹的ID"""
    try:
        url = f"https://drive.google.com/drive/folders/{main_folder_id}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        html = response.text
        
        # 查找日期附近的文件夹ID
        idx = html.find(target_date)
        if idx > 0:
            context = html[max(0, idx-1000):min(len(html), idx+1000)]
            ids = re.findall(r'"([a-zA-Z0-9_-]{33})"', context)
            if ids:
                return ids[0]  # 返回第一个找到的ID
    except:
        pass
    return None


def download_latest_file_from_folder(folder_id):
    """从文件夹下载最新的txt文件"""
    try:
        # 使用gdown获取文件夹内容（仅前50个文件）
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        
        # 获取文件列表
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(folder_url, headers=headers, timeout=30)
        html = response.text
        
        # 提取文件名和ID的映射
        # 查找所有txt文件
        txt_pattern = r'Processing file ([a-zA-Z0-9_-]+) ([\d_]+\.txt)'
        
        # 使用不同的策略：直接查找文件ID模式
        # Google Drive HTML中的文件ID通常在特定结构中
        file_pattern = r'"([a-zA-Z0-9_-]{33})","([^"]+\.txt)"'
        matches = re.findall(file_pattern, html)
        
        if matches:
            # 按文件名排序，获取最新的
            matches.sort(key=lambda x: x[1], reverse=True)
            latest_file_id, latest_filename = matches[0]
            
            print(f"最新文件: {latest_filename} (ID: {latest_file_id})")
            
            # 下载文件
            download_url = f"https://drive.google.com/uc?id={latest_file_id}"
            output_path = "/tmp/google_drive_latest.txt"
            
            gdown.download(download_url, output_path, quiet=True)
            
            # 读取文件（GBK编码）
            with open(output_path, 'rb') as f:
                raw_data = f.read()
            
            content = raw_data.decode('gbk')
            return content, latest_filename
            
    except Exception as e:
        print(f"下载文件失败: {e}")
    
    return None, None


def parse_data(content):
    """解析txt内容"""
    lines = content.strip().split('\n')
    
    summary_data = {}
    coins_data = []
    in_coin_section = False
    
    for line in lines:
        line = line.strip()
        
        if '透明标签_' in line:
            if '急涨总和' in line:
                match = re.search(r'急涨：(\d+)', line)
                if match:
                    summary_data['rise_total'] = int(match.group(1))
            elif '急跌总和' in line:
                match = re.search(r'急跌：(\d+)', line)
                if match:
                    summary_data['fall_total'] = int(match.group(1))
            elif '五种状态' in line:
                match = re.search(r'状态：(.+)', line)
                if match:
                    summary_data['five_states'] = match.group(1)
            elif '急涨急跌比值' in line:
                match = re.search(r'比值：([\d.]+)', line)
                if match:
                    summary_data['rise_fall_ratio'] = float(match.group(1))
            elif '绿色数量' in line:
                match = re.search(r'=(\d+)', line)
                if match:
                    summary_data['green_count'] = int(match.group(1))
            elif '百分比' in line:
                match = re.search(r'=(\d+)%', line)
                if match:
                    summary_data['green_percent'] = float(match.group(1))
            elif '计次' in line and '得分' not in line:
                match = re.search(r'=(\d+)', line)
                if match:
                    summary_data['count_times'] = int(match.group(1))
            elif '差值结果' in line:
                match = re.search(r'差值：([-\d.]+)', line)
                if match:
                    summary_data['diff_result'] = float(match.group(1))
                    
        elif line.startswith('[超级列表框_首页开始]'):
            in_coin_section = True
        elif line.startswith('[超级列表框_首页结束]'):
            break
        elif in_coin_section and '|' in line:
            parts = line.split('|')
            if len(parts) >= 15:
                try:
                    coin = {
                        'seq_num': int(parts[0]),
                        'coin_name': parts[1],
                        'rise_speed': float(parts[2]),
                        'rise_signal': int(parts[3]),
                        'fall_signal': int(parts[4]),
                        'update_time': parts[5],
                        'history_high': float(parts[6]),
                        'high_time': parts[7],
                        'drop_from_high': float(parts[8]),
                        'change_24h': float(parts[9]),
                        'plus_4_percent': int(parts[10]) if parts[10] else 0,
                        'minus_3_percent': int(parts[11]) if parts[11] else 0,
                        'ranking': int(parts[12]) if parts[12] else 0,
                        'current_price': float(parts[13]),
                        'high_ratio': float(parts[14].replace('%', '')),
                        'low_ratio': float(parts[15].replace('%', '')) if len(parts) > 15 else 0,
                        'anomaly': parts[16] if len(parts) > 16 else ''
                    }
                    coins_data.append(coin)
                except:
                    pass
    
    # 填充缺失字段
    summary_data.setdefault('all_green_score', 0.0)
    summary_data.setdefault('price_lowest_score', 0.0)
    summary_data.setdefault('price_new_high', 0)
    summary_data.setdefault('fall_count', summary_data.get('fall_total', 0))
    
    return summary_data, coins_data


def save_to_database(summary_data, coins_data, record_time):
    """保存到数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
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
        
        for coin in coins_data:
            cursor.execute('''
                INSERT INTO coin_details 
                (summary_id, seq_num, coin_name, rise_speed, rise_signal, fall_signal,
                 update_time, history_high, high_time, drop_from_high, change_24h,
                 plus_4_percent, minus_3_percent, ranking, current_price, 
                 high_ratio, low_ratio, anomaly, record_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                summary_id, coin['seq_num'], coin['coin_name'], coin['rise_speed'],
                coin['rise_signal'], coin['fall_signal'], coin['update_time'],
                coin['history_high'], coin['high_time'], coin['drop_from_high'],
                coin['change_24h'], coin['plus_4_percent'], coin['minus_3_percent'],
                coin['ranking'], coin['current_price'], coin['high_ratio'],
                coin['low_ratio'], coin['anomaly'], record_time
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False


def collect_once():
    """执行一次采集"""
    try:
        beijing_now = get_beijing_time()
        record_time = beijing_now.strftime('%Y-%m-%d %H:%M:%S')
        target_date = get_today_folder_name()
        
        print(f"\n{'='*70}")
        print(f"[{record_time}] 开始数据采集")
        print(f"目标日期: {target_date}")
        print('='*70)
        
        # 获取日期文件夹ID
        folder_id = get_date_folder_id(MAIN_FOLDER_ID, target_date)
        
        if not folder_id:
            print("未找到日期文件夹，使用默认ID")
            # 使用已知的文件夹ID
            folder_id = "1y0Dm0W8S1enfjobDKAyXiOA2U33pUbsD"
        
        print(f"文件夹ID: {folder_id}")
        
        # 下载最新文件
        content, filename = download_latest_file_from_folder(folder_id)
        
        if content:
            # 解析数据
            summary, coins = parse_data(content)
            
            if summary and coins:
                # 保存
                if save_to_database(summary, coins, record_time):
                    print(f"✓ 数据采集成功!")
                    print(f"  急涨: {summary['rise_total']}, 急跌: {summary['fall_total']}")
                    print(f"  币种数量: {len(coins)}")
                else:
                    print("✗ 数据保存失败")
            else:
                print("✗ 数据解析失败")
        else:
            print("✗ 文件下载失败")
        
        next_time = beijing_now + timedelta(seconds=COLLECTION_INTERVAL)
        print(f"下次采集: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"采集失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("="*70)
    print("首页数据采集器 V2")
    print("="*70)
    print(f"启动时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"采集间隔: {COLLECTION_INTERVAL//60} 分钟")
    print("="*70)
    
    # 立即采集一次
    collect_once()
    
    # 持续采集
    try:
        while True:
            time.sleep(COLLECTION_INTERVAL)
            collect_once()
    except KeyboardInterrupt:
        print("\n\n采集器已停止")
