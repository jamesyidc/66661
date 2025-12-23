#!/usr/bin/env python3
"""
Google Drive TXT文件智能检测器 - 最终版本
按照用户提出的4步策略:
1. 确认当天北京时间日期，确定文件夹
2. 进入文件夹查看有多少个TXT文件
3. 保存这些TXT文件的名称
4. 找到最新的TXT文件，使用固定ID抓取数据
"""
import requests
import re
import time
import sqlite3
from datetime import datetime
import pytz
import sys

# 导入计次得分计算函数
from calculate_count_score import calculate_count_score

# 配置
TODAY_FOLDER_ID = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"  # 默认文件夹ID（如果配置文件不存在则使用此值）
ROOT_FOLDER_ID = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"  # 默认根文件夹ID (所有日期文件夹的父文件夹)
ROOT_FOLDER_ODD = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"  # 单数日期父文件夹（默认值）
ROOT_FOLDER_EVEN = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"  # 双数日期父文件夹（默认值）
FIXED_FILE_ID = "1eyYiU6lU8n7SwWUvFtm_kUIvaZI0SO4U"  # 固定的数据文件ID
CHECK_INTERVAL = 30  # 检测间隔（秒）
TIMEOUT_THRESHOLD = 11 * 60  # 超时阈值（秒）= 11分钟
LOG_FILE = "/home/user/webapp/gdrive_final_detector.log"
DB_PATH = "/home/user/webapp/crypto_data.db"
CONFIG_FILE = "/home/user/webapp/daily_folder_config.json"  # 每日文件夹ID配置文件
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def get_root_folder_for_today():
    """🆕 根据今天是单数还是双数，获取对应的父文件夹ID"""
    today = datetime.now(BEIJING_TZ)
    day_of_month = today.day
    is_odd_day = day_of_month % 2 == 1
    
    # 从配置文件读取单数/双数父文件夹ID
    root_folder_odd = ROOT_FOLDER_ODD
    root_folder_even = ROOT_FOLDER_EVEN
    
    try:
        import json
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if 'root_folder_odd' in config:
                root_folder_odd = config['root_folder_odd']
            if 'root_folder_even' in config:
                root_folder_even = config['root_folder_even']
    except:
        pass
    
    # 根据日期选择父文件夹
    if is_odd_day:
        log(f"📅 今天是{day_of_month}号（单数日期）")
        log(f"📂 使用单数日期父文件夹: {root_folder_odd}")
        return root_folder_odd
    else:
        log(f"📅 今天是{day_of_month}号（双数日期）")
        log(f"📂 使用双数日期父文件夹: {root_folder_even}")
        return root_folder_even

def get_today_folder_id():
    """从配置文件读取今天的文件夹ID"""
    try:
        import json
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
            config_date = config.get('current_date', 'unknown')
            
            # 检查配置日期是否是今天
            if config_date == today:
                folder_id = config.get('folder_id', TODAY_FOLDER_ID)
                log(f"✅ 配置文件日期匹配: {config_date}")
                log(f"📂 从配置文件读取文件夹ID: {folder_id}")
                return folder_id
            else:
                log(f"")
                log(f"⚠️ " + "=" * 60)
                log(f"⚠️  警告：配置文件日期不匹配！")
                log(f"⚠️  配置文件日期: {config_date}")
                log(f"⚠️  当前系统日期: {today}")
                log(f"⚠️  使用默认文件夹ID: {TODAY_FOLDER_ID}")
                log(f"⚠️  请更新 config.json 文件中的 current_date 和 folder_id")
                log(f"⚠️ " + "=" * 60)
                log(f"")
                return TODAY_FOLDER_ID
    except Exception as e:
        log(f"❌ 无法读取配置文件: {e}")
        log(f"📂 使用默认文件夹ID: {TODAY_FOLDER_ID}")
        return TODAY_FOLDER_ID

def log(message):
    """写入日志"""
    timestamp = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except:
        pass

def step1_get_today_date():
    """步骤1: 确认当天北京时间日期"""
    today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
    log(f"📅 步骤1: 确认今天日期 = {today}")
    return today

def step2_count_txt_files(folder_id, today):
    """步骤2: 进入文件夹，查看总共有多少个TXT文件，并提取真实File ID"""
    log(f"📂 步骤2: 进入文件夹 {folder_id}")
    
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
    
    try:
        from bs4 import BeautifulSoup
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有包含日期的文件
        file_info = {}  # {date_time: file_id}
        
        # 查找所有文件链接（修正：直接从<a>标签的文本内容提取文件名）
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            # 方法1：从链接的text提取文件名
            filename = link.get_text(strip=True)
            
            # 检查是否是.txt文件
            if filename.endswith('.txt'):
                # 提取file ID
                if '/file/d/' in href:
                    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', href)
                    if match:
                        file_id = match.group(1)
                        # 检查是否符合日期格式 YYYY-MM-DD_HHMM.txt
                        time_match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{4})\.txt', filename)
                        if time_match:
                            file_date = time_match.group(1)
                            time_str = time_match.group(2)
                            # 保存所有日期的文件，不仅仅是今天的（因为可能需要使用昨天的数据）
                            key = f"{file_date}_{time_str}"
                            file_info[key] = {
                                'file_id': file_id,
                                'filename': filename,
                                'date': file_date,
                                'time': time_str
                            }
        
        # 筛选出今天的文件
        today_files = {k: v for k, v in file_info.items() if v['date'] == today}
        
        # 如果今天没有文件，尝试使用最近日期的文件
        if not today_files and file_info:
            log(f"   ⚠️ 今天({today})没有文件，尝试查找最近的文件...")
            # 找到最新日期的文件
            latest_date = max(v['date'] for v in file_info.values())
            today_files = {k: v for k, v in file_info.items() if v['date'] == latest_date}
            log(f"   ✅ 使用最新日期的文件: {latest_date} ({len(today_files)}个文件)")
        
        count = len(today_files)
        log(f"   ✅ 找到 {count} 个TXT文件（含真实ID）")
        
        if today_files:
            # 显示最新的几个文件
            sorted_files = sorted(today_files.items(), key=lambda x: x[1]['time'], reverse=True)
            log(f"   最新3个文件: {', '.join([v['filename'] for k, v in sorted_files[:3]])}")
        
        # 转换回旧格式以兼容后续代码 {time: file_id}
        result = {v['time']: v['file_id'] for k, v in today_files.items()}
        return result
        
    except Exception as e:
        log(f"   ❌ 查询失败: {e}")
        import traceback
        log(f"   错误详情: {traceback.format_exc()}")
        return {}

def step3_save_filenames(file_info, today):
    """步骤3: 保存这些TXT文件的名称和ID"""
    if not file_info:
        log(f"📝 步骤3: 没有文件可保存")
        return {}
    
    filenames = [f"{today}_{time}.txt" for time in file_info.keys()]
    log(f"📝 步骤3: 保存 {len(filenames)} 个文件名和ID")
    log(f"   最新5个: {', '.join(sorted(filenames, reverse=True)[:5])}")
    log(f"   最早5个: {', '.join(sorted(filenames)[:5])}")
    
    return file_info

def step4_get_latest_data(file_info, fixed_file_id):
    """步骤4: 找到最新的TXT文件，使用其真实ID抓取数据"""
    if not file_info:
        log(f"🔍 步骤4: 没有可用文件")
        return None
    
    # 找到最新的时间
    latest_time = sorted(file_info.keys(), reverse=True)[0]
    latest_file_id = file_info[latest_time]
    today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
    latest_filename = f"{today}_{latest_time}.txt"
    
    log(f"🔍 步骤4: 最新文件名 = {latest_filename}")
    log(f"   ✅ 使用真实File ID: {latest_file_id} (不再使用固定ID)")
    
    # 使用真实ID下载内容
    url = f"https://drive.google.com/uc?export=download&id={latest_file_id}"
    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # 提取文件内容的时间戳
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})', content)
            if timestamp_match:
                file_timestamp = f"{timestamp_match.group(1)} {timestamp_match.group(2)}"
                log(f"   文件内容时间戳: {file_timestamp}")
                
                return {
                    'latest_filename': latest_filename,
                    'content': content,
                    'file_timestamp': file_timestamp
                }
            else:
                log(f"   ❌ 无法提取时间戳")
                return None
        else:
            log(f"   ❌ 下载失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        log(f"   ❌ 下载失败: {e}")
        return None

def parse_content(content):
    """解析TXT文件内容"""
    try:
        # 提取时间戳
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})', content)
        if not timestamp_match:
            return None
        
        date_str, time_str = timestamp_match.groups()
        timestamp = f"{date_str} {time_str}"
        
        # 解析为datetime对象（只保留到分钟）
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        snapshot_time = dt.strftime('%Y-%m-%d %H:%M:00')
        snapshot_date = dt.strftime('%Y-%m-%d')
        
        # 提取急涨急跌数据（兼容新旧格式）
        rush_up_match = re.search(r'透明标签_急涨总和=急涨[:：](\d+)', content)
        if not rush_up_match:
            rush_up_match = re.search(r'本轮急涨.*?(\d+)/', content)
        
        rush_down_match = re.search(r'透明标签_急跌总和=急跌[:：](\d+)', content)
        if not rush_down_match:
            rush_down_match = re.search(r'本轮急跌.*?(\d+)/', content)
        
        rush_up = int(rush_up_match.group(1)) if rush_up_match else 0
        rush_down = int(rush_down_match.group(1)) if rush_down_match else 0
        
        # 提取计次和状态（兼容新旧格式）
        count_match = re.search(r'透明标签_计次=(\d+)', content)
        if not count_match:
            count_match = re.search(r'计次[:：](\d+)', content)
        
        status_match = re.search(r'透明标签_五种状态=状态[:：]([^\r\n]+)', content)
        if not status_match:
            status_match = re.search(r'[★☆]+\s*\|\s*([^\n]+)', content)
        
        count = int(count_match.group(1)) if count_match else 0
        status = status_match.group(1).strip() if status_match else ""
        
        # 提取计次得分显示（先从文件中提取，如果没有则自动计算）
        score_match = re.search(r'((?:[★☆])+(?:---)?)', content)
        count_score_display_from_file = score_match.group(1) if score_match else ""
        
        # 自动计算计次得分（确保数据完整性）
        count_score_display, count_score_type = calculate_count_score(snapshot_time, count)
        
        # 如果文件中有得分，记录日志但使用计算结果
        if count_score_display_from_file and count_score_display_from_file != count_score_display:
            log(f"   ⚠️ 文件中的计次得分 '{count_score_display_from_file}' 与计算结果 '{count_score_display}' 不一致，使用计算结果")
        
        # 计算diff = rush_up - rush_down
        diff = rush_up - rush_down
        
        return {
            'snapshot_time': snapshot_time,
            'snapshot_date': snapshot_date,
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'count': count,
            'status': status,
            'count_score_display': count_score_display,
            'count_score_type': count_score_type,
            'file_timestamp': timestamp
        }
        
    except Exception as e:
        log(f"❌ 解析内容失败: {e}")
        return None

def parse_coin_data(content):
    """解析币种详细数据"""
    try:
        coins = []
        lines = content.split('\n')
        
        # 查找币种数据区域（在[超级列表框_首页开始]之后）
        in_coin_section = False
        for line in lines:
            if '[超级列表框_首页开始]' in line:
                in_coin_section = True
                continue
            
            if '[超级列表框_首页结束]' in line:
                break
            
            if in_coin_section and '|' in line:
                # 格式: 1|BTC|-0.14|0|0|2025-12-09 22:20:00|126259.48|2025-10-07|-28.43|-1.24|||15|89901.39296|71.71%|110.5%
                parts = line.strip().split('|')
                if len(parts) >= 15:
                    try:
                        index = int(parts[0])
                        
                        # 解析最高占比和最低占比 (ratio1=最高占比, ratio2=最低占比)
                        ratio1_str = parts[14] if len(parts) > 14 else '0%'
                        ratio2_str = parts[15] if len(parts) > 15 else '0%'
                        
                        # 移除百分号并转换为浮点数
                        try:
                            max_ratio = float(ratio1_str.rstrip('%')) if ratio1_str else 0
                            min_ratio = float(ratio2_str.rstrip('%')) if ratio2_str else 0
                        except:
                            max_ratio = 0
                            min_ratio = 0
                        
                        # 根据最高占比和最低占比计算优先级等级
                        # 等级1: 最高占比>90 且 最低占比>120
                        # 等级2: 最高占比>80 且 最低占比>120
                        # 等级3: 最高占比>90 且 最低占比>110
                        # 等级4: 最高占比>70 且 最低占比>120
                        # 等级5: 最高占比>80 且 最低占比>110
                        # 等级6: 其他情况 (最高占比<80 或 最低占比<110)
                        if max_ratio > 90 and min_ratio > 120:
                            priority_level = '等级1'
                        elif max_ratio > 80 and min_ratio > 120:
                            priority_level = '等级2'
                        elif max_ratio > 90 and min_ratio > 110:
                            priority_level = '等级3'
                        elif max_ratio > 70 and min_ratio > 120:
                            priority_level = '等级4'
                        elif max_ratio > 80 and min_ratio > 110:
                            priority_level = '等级5'
                        else:
                            priority_level = '等级6'
                        
                        coin = {
                            'index_order': index,
                            'symbol': parts[1],
                            'change': float(parts[2]) if parts[2] else 0,
                            'rush_up': int(parts[3]) if parts[3] else 0,
                            'rush_down': int(parts[4]) if parts[4] else 0,
                            'update_time': parts[5],
                            'high_price': float(parts[6]) if parts[6] else 0,
                            'high_time': parts[7],
                            'decline': float(parts[8]) if parts[8] else 0,
                            'change_24h': float(parts[9]) if parts[9] else 0,
                            'rank': int(parts[12]) if parts[12] else 0,
                            'current_price': float(parts[13]) if parts[13] else 0,
                            'ratio1': ratio1_str,  # 最高占比
                            'ratio2': ratio2_str,  # 最低占比
                            'priority_level': priority_level
                        }
                        coins.append(coin)
                    except (ValueError, IndexError) as e:
                        continue
        
        return coins
        
    except Exception as e:
        log(f"❌ 解析币种数据失败: {e}")
        return []

def import_to_database(data, content):
    """导入数据到数据库（首页监控系统）"""
    try:
        log(f"   🔌 连接数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
        
        # 检查数据是否已存在
        log(f"   🔍 检查数据是否已存在...")
        cursor.execute("""
            SELECT COUNT(*) FROM crypto_snapshots 
            WHERE snapshot_time = ?
        """, (data['snapshot_time'],))
        
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            log(f"   ℹ️  数据库中已存在该时间的记录: {data['snapshot_time']}")
            conn.close()
            return False
        
        # 验证数据有效性：rush_up和rush_down不能同时为0
        if data['rush_up'] == 0 and data['rush_down'] == 0:
            log(f"   ⚠️  数据无效：rush_up和rush_down均为0，跳过本次保存")
            conn.close()
            return False
        
        # 插入新数据到crypto_snapshots
        log(f"   📝 准备插入新记录到 crypto_snapshots 表...")
        cursor.execute("""
            INSERT INTO crypto_snapshots 
            (snapshot_time, snapshot_date, rush_up, rush_down, diff, count, status, count_score_display, count_score_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+8 hours'))
        """, (
            data['snapshot_time'],
            data['snapshot_date'],
            data['rush_up'],
            data['rush_down'],
            data['diff'],
            data['count'],
            data['status'],
            data['count_score_display'],
            data['count_score_type']
        ))
        
        # 获取刚插入的snapshot_id
        snapshot_id = cursor.lastrowid
        log(f"   ✅ 快照数据插入成功 (ID: {snapshot_id})")
        
        # 解析并导入币种数据
        log(f"   🪙 开始解析币种数据...")
        coins = parse_coin_data(content)
        
        if coins:
            log(f"   📊 找到 {len(coins)} 个币种数据")
            coin_count = 0
            
            for coin in coins:
                try:
                    cursor.execute("""
                        INSERT INTO crypto_coin_data 
                        (snapshot_id, snapshot_time, symbol, index_order, change, rush_up, rush_down, 
                         update_time, high_price, high_time, decline, change_24h, rank, current_price, 
                         ratio1, ratio2, priority_level, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+8 hours'))
                    """, (
                        snapshot_id,
                        data['snapshot_time'],
                        coin['symbol'],
                        coin['index_order'],
                        coin['change'],
                        coin['rush_up'],
                        coin['rush_down'],
                        coin['update_time'],
                        coin['high_price'],
                        coin['high_time'],
                        coin['decline'],
                        coin['change_24h'],
                        coin['rank'],
                        coin['current_price'],
                        coin['ratio1'],
                        coin['ratio2'],
                        coin['priority_level']
                    ))
                    coin_count += 1
                except Exception as e:
                    log(f"   ⚠️  导入币种 {coin.get('symbol', 'Unknown')} 失败: {e}")
                    continue
            
            log(f"   ✅ 成功导入 {coin_count} 个币种数据")
        else:
            log(f"   ⚠️  未找到币种数据")
        
        log(f"   💾 提交事务...")
        conn.commit()
        
        # 验证插入
        cursor.execute("SELECT COUNT(*) FROM crypto_snapshots WHERE snapshot_time = ?", (data['snapshot_time'],))
        verify_count = cursor.fetchone()[0]
        
        conn.close()
        
        if verify_count > 0:
            log(f"   ✅ 数据库插入成功并已验证")
            log(f"   📊 记录详情: {data['snapshot_time']} | 急涨:{data['rush_up']} 急跌:{data['rush_down']} | 计次:{data['count']} {data['count_score_display']} | {data['status']}")
            return True
        else:
            log(f"   ❌ 插入验证失败")
            return False
        
    except Exception as e:
        log(f"   ❌ 数据库操作失败: {e}")
        import traceback
        log(f"   错误详情: {traceback.format_exc()}")
        return False

def get_root_folder_id_and_create_today_folder():
    """
    11分钟超时恢复机制:
    1. 重新获取根文件夹ID (父文件夹)
    2. 在根文件夹下创建/查找今天日期的文件夹
    3. 更新配置文件
    4. 返回新的文件夹ID
    """
    today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
    
    log("")
    log("🔄" * 40)
    log("⚠️  触发11分钟超时恢复机制！")
    log(f"📅 目标日期文件夹: {today}")
    log("🔄" * 40)
    log("")
    
    try:
        from bs4 import BeautifulSoup
        import json
        
        # 🆕 根据今天日期选择父文件夹
        root_folder_id = get_root_folder_for_today()
        
        # 步骤1: 访问根文件夹,查找今天日期的文件夹
        log(f"📂 步骤1: 访问根文件夹 {root_folder_id}")
        url = f"https://drive.google.com/embeddedfolderview?id={root_folder_id}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有文件夹链接
        all_links = soup.find_all('a', href=True)
        today_folder_id = None
        
        for link in all_links:
            href = link.get('href', '')
            foldername = link.get_text(strip=True)
            
            # 检查是否是今天日期的文件夹
            if foldername == today:
                # 提取文件夹ID
                if '/folders/' in href:
                    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', href)
                    if match:
                        today_folder_id = match.group(1)
                        log(f"   ✅ 找到今天的文件夹: {today}")
                        log(f"   📂 文件夹ID: {today_folder_id}")
                        break
        
        if not today_folder_id:
            log(f"   ❌ 未找到今天日期的文件夹: {today}")
            log(f"   ⚠️  请确保根文件夹下存在名为 '{today}' 的子文件夹")
            return None
        
        # 步骤2: 更新配置文件
        log(f"📝 步骤2: 更新配置文件")
        
        # 读取现有配置，保留单数/双数父文件夹ID
        existing_config = {}
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except:
            pass
        
        # 更新配置
        config = {
            'root_folder_odd': existing_config.get('root_folder_odd', ROOT_FOLDER_ODD),
            'root_folder_even': existing_config.get('root_folder_even', ROOT_FOLDER_EVEN),
            'current_date': today,
            'folder_id': today_folder_id,
            'updated_at': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S'),
            'update_reason': '11分钟超时自动恢复',
            'root_folder_description': {
                'odd': '单数日期父文件夹 (1, 3, 5, 7, 9, 11...)',
                'even': '双数日期父文件夹 (2, 4, 6, 8, 10, 12...)'
            }
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        log(f"   ✅ 配置文件已更新")
        log(f"   📅 日期: {today}")
        log(f"   📂 文件夹ID: {today_folder_id}")
        log("")
        
        return today_folder_id
        
    except Exception as e:
        log(f"❌ 恢复机制执行失败: {e}")
        import traceback
        log(f"错误详情: {traceback.format_exc()}")
        return None

def main():
    """主函数"""
    log("=" * 80)
    log("🚀 Google Drive智能检测器启动 (4步策略)")
    log(f"📁 默认文件夹ID: {TODAY_FOLDER_ID}")
    log(f"📂 配置文件: {CONFIG_FILE}")
    log(f"🔑 固定数据ID: {FIXED_FILE_ID}")
    log(f"🔄 检测间隔: {CHECK_INTERVAL}秒")
    log(f"💾 数据库: {DB_PATH}")
    log(f"")
    log(f"⏰ 跨日期重置规则:")
    log(f"   • 0:00-0:10 之间：继续使用昨天的文件夹ID（等待新文件夹生成）")
    log(f"   • 0:10 之后：自动切换到新日期，从配置文件读取新文件夹ID")
    log(f"   • 确保新日期文件夹已经生成后才开始检测")
    log(f"")
    log(f"🛡️  超时恢复机制:")
    log(f"   • 超过11分钟未找到TXT文件 → 自动重新获取父文件夹ID")
    log(f"   • 查找/创建当天日期文件夹 → 更新配置文件")
    log(f"   • 继续监控新文件夹")
    log("=" * 80)
    
    last_data_timestamp = None
    check_count = 0
    last_reset_date = datetime.now(BEIJING_TZ).date()
    date_already_reset = False  # 标记当天是否已经重置过
    last_file_found_time = datetime.now(BEIJING_TZ)  # 记录最后一次找到文件的时间
    timeout_recovery_triggered = False  # 标记是否已触发过超时恢复
    
    while True:
        try:
            check_count += 1
            current_time = datetime.now(BEIJING_TZ)
            current_date = current_time.date()
            
            # 检查是否跨日期（必须在0点10分之后才重置，确保新日期文件夹已生成）
            if current_date != last_reset_date:
                # 检查是否已经过了0点10分
                if current_time.hour == 0 and current_time.minute >= 10:
                    log("\n" + "🔄" * 40)
                    log("⏰ 检测到日期变更且已过0:10，开始重置检测器...")
                    log(f"📅 旧日期: {last_reset_date}")
                    log(f"📅 新日期: {current_date}")
                    log(f"🕐 当前时间: {current_time.strftime('%H:%M:%S')}")
                    log("🔄 重新读取配置文件中的新文件夹ID...")
                    log("🔄" * 40 + "\n")
                    last_reset_date = current_date
                    check_count = 0
                    last_data_timestamp = None
                    date_already_reset = True
                    
                    # 立即重新读取配置文件
                    log("📂 重新加载配置文件...")
                    current_folder_id = get_today_folder_id()
                    log(f"✅ 新日期文件夹ID: {current_folder_id}")
                    log("")
                elif current_time.hour == 0 and current_time.minute < 10:
                    # 0:00-0:10之间，提示等待
                    if check_count % 10 == 1:  # 每10次检查提示一次，避免刷屏
                        log(f"⏳ 检测到跨日期，但未到0:10，继续使用昨天的文件夹ID")
                        log(f"⏳ 当前时间: {current_time.strftime('%H:%M:%S')}，将在0:10后自动切换到新日期")
                elif current_time.hour > 0:
                    # 0:10之后任何时间都可以重置
                    log("\n" + "🔄" * 40)
                    log("⏰ 检测到日期变更（已过0:10），开始重置检测器...")
                    log(f"📅 旧日期: {last_reset_date}")
                    log(f"📅 新日期: {current_date}")
                    log(f"🕐 当前时间: {current_time.strftime('%H:%M:%S')}")
                    log("🔄 重新读取配置文件中的新文件夹ID...")
                    log("🔄" * 40 + "\n")
                    last_reset_date = current_date
                    check_count = 0
                    last_data_timestamp = None
                    date_already_reset = True
                    
                    # 立即重新读取配置文件
                    log("📂 重新加载配置文件...")
                    current_folder_id = get_today_folder_id()
                    log(f"✅ 新日期文件夹ID: {current_folder_id}")
                    log("")
            
            log(f"\n{'='*80}")
            log(f"🔍 检查 #{check_count} | {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            log("=" * 80)
            
            # 步骤1: 确认今天日期（每次都重新获取，确保使用最新日期）
            today = step1_get_today_date()
            
            # 读取今天的文件夹ID（每次都重新读取，确保跨日期后使用新ID）
            current_folder_id = get_today_folder_id()
            log(f"📂 当前使用的文件夹ID: {current_folder_id} (日期: {today})")
            
            # 步骤2: 统计TXT文件数量并提取File ID
            file_info = step2_count_txt_files(current_folder_id, today)
            
            if not file_info:
                # 检查是否超过11分钟未找到文件
                time_since_last_file = (datetime.now(BEIJING_TZ) - last_file_found_time).total_seconds()
                minutes_elapsed = time_since_last_file / 60
                
                if minutes_elapsed > 11 and not timeout_recovery_triggered:
                    log("")
                    log("⚠️" * 40)
                    log(f"⏱️  警告: 已经 {minutes_elapsed:.1f} 分钟未找到TXT文件!")
                    log("🔧 启动11分钟超时恢复机制...")
                    log("⚠️" * 40)
                    log("")
                    
                    # 执行恢复机制
                    new_folder_id = get_root_folder_id_and_create_today_folder()
                    
                    if new_folder_id:
                        log("✅ 恢复机制执行成功！")
                        log(f"📂 新文件夹ID: {new_folder_id}")
                        log("🔄 重置计时器，继续监控...")
                        log("")
                        
                        # 重置状态
                        current_folder_id = new_folder_id
                        last_file_found_time = datetime.now(BEIJING_TZ)
                        timeout_recovery_triggered = True
                        check_count = 0
                        
                        # 立即重试查找文件
                        log("🔍 使用新文件夹ID重新查找文件...")
                        file_info = step2_count_txt_files(current_folder_id, today)
                        
                        if file_info:
                            log(f"🎉 恢复成功! 在新文件夹中找到 {len(file_info)} 个TXT文件")
                            last_file_found_time = datetime.now(BEIJING_TZ)
                            timeout_recovery_triggered = False
                        else:
                            log("⚠️  新文件夹中暂时还没有文件，继续等待...")
                            # 重要: 即使新文件夹中没有文件，也要重置标志，允许下次超时再次触发恢复
                            timeout_recovery_triggered = False
                    else:
                        log("❌ 恢复机制执行失败，继续使用当前文件夹ID")
                        # 重要: 执行失败也要重置标志，允许下次超时再次触发恢复
                        timeout_recovery_triggered = False
                else:
                    if minutes_elapsed > 5:
                        log(f"⏳ 已等待 {minutes_elapsed:.1f} 分钟未找到文件 (超时阈值: 11分钟)")
                    log("⏰ 没有找到文件，等待下次检查...")
                
                if not file_info:
                    time.sleep(CHECK_INTERVAL)
                    continue
            else:
                # 找到文件，重置计时器
                last_file_found_time = datetime.now(BEIJING_TZ)
                timeout_recovery_triggered = False
            
            # 步骤3: 保存文件名和ID列表
            file_info = step3_save_filenames(file_info, today)
            
            # 步骤4: 获取最新数据（使用真实ID）
            result = step4_get_latest_data(file_info, FIXED_FILE_ID)
            
            if not result:
                log("⏰ 无法获取数据，等待下次检查...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # 检查是否是新数据
            if result['file_timestamp'] == last_data_timestamp:
                log(f"ℹ️  数据未更新，仍是: {result['file_timestamp']}")
                log("⏰ 等待下次检查...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # 发现新数据
            log(f"")
            log(f"{'🎉' * 40}")
            log(f"🆕 检测到新的TXT文件！")
            log(f"{'🎉' * 40}")
            log(f"📄 文件信息:")
            log(f"   最新文件名: {result['latest_filename']}")
            log(f"   数据时间戳: {result['file_timestamp']}")
            log(f"")
            
            # 解析内容
            log(f"⚙️  开始提取文件数据...")
            data = parse_content(result['content'])
            if not data:
                log("❌ 数据提取失败，等待下次检查...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            log(f"✅ 数据提取成功！")
            log(f"")
            log(f"📊 提取的数据详情:")
            log(f"   ├─ 快照时间: {data['snapshot_time']}")
            log(f"   ├─ 快照日期: {data['snapshot_date']}")
            log(f"   ├─ 急涨数量: {data['rush_up']}")
            log(f"   ├─ 急跌数量: {data['rush_down']}")
            log(f"   ├─ 计次: {data['count']}")
            log(f"   ├─ 计次评分: {data['count_score_display']}")
            log(f"   └─ 状态: {data['status']}")
            log(f"")
            
            # 导入到数据库
            log(f"💾 开始导入到首页数据监控系统...")
            import_success = import_to_database(data, result['content'])
            
            if import_success:
                last_data_timestamp = result['file_timestamp']
                log(f"")
                log(f"{'✅' * 40}")
                log(f"🎊 新数据已成功导入首页监控系统！")
                log(f"{'✅' * 40}")
                log(f"📈 系统状态:")
                log(f"   ├─ 数据库: crypto_snapshots 表")
                log(f"   ├─ 导入时间: {data['snapshot_time']}")
                log(f"   ├─ 数据类型: 快照数据")
                log(f"   └─ 可在首页查看: ✅")
                log(f"")
            else:
                log(f"ℹ️  数据已存在于系统中，无需重复导入")
            
            log("⏰ 等待下次检查...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("\n👋 收到停止信号，正在退出...")
            sys.exit(0)
        except Exception as e:
            log(f"❌ 发生错误: {e}")
            log("⏰ 等待下次检查...")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
