#!/usr/bin/env python3
"""
Google Drive 数据采集自动触发守护进程
功能：
1. 每天 00:10 自动触发数据采集
2. 如果 00:10 后超过20分钟还没有新数据，自动触发采集
3. 每5分钟检查一次
"""
import time
import schedule
import subprocess
import sqlite3
from datetime import datetime, timedelta
import pytz
import sys
import os

BEIJING_TZ = pytz.timezone('Asia/Shanghai')
DB_PATH = '/home/user/webapp/crypto_data.db'
SCRIPT_PATH = '/home/user/webapp/gdrive_final_detector.py'
LOG_FILE = '/home/user/webapp/logs/gdrive-auto-trigger-daemon.log'

def log(message):
    """写入日志"""
    timestamp = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except:
        pass

def get_latest_data_time():
    """获取最新数据时间"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT snapshot_time 
            FROM crypto_snapshots 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            snapshot_time = result[0]
            try:
                dt = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S')
                return BEIJING_TZ.localize(dt)
            except:
                dt = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S.%f')
                return BEIJING_TZ.localize(dt)
        return None
    except Exception as e:
        log(f"❌ 获取最新数据时间失败: {e}")
        return None

def trigger_collection(reason):
    """触发数据采集"""
    try:
        log(f"🚀 触发数据采集 - 原因: {reason}")
        
        # 运行采集脚本
        process = subprocess.Popen(
            ['python3', SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(SCRIPT_PATH)
        )
        
        log(f"✅ 采集脚本已启动 (PID: {process.pid})")
        return True
        
    except Exception as e:
        log(f"❌ 触发采集失败: {e}")
        return False

def update_config_for_new_date():
    """更新配置文件到新日期的文件夹"""
    try:
        import json
        import requests
        from bs4 import BeautifulSoup
        import re
        
        log("📂 开始更新配置文件到新日期...")
        
        config_file = '/home/user/webapp/daily_folder_config.json'
        
        # 读取现有配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 获取"首页数据"文件夹ID（根文件夹）
        homepage_folder_id = config.get('root_folder_odd', config.get('root_folder_even'))
        
        if not homepage_folder_id:
            log("❌ 配置文件中未找到根文件夹ID")
            return False
        
        log(f"✅ 根文件夹ID（首页数据）: {homepage_folder_id}")
        
        # 今天的日期
        today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
        log(f"📅 目标日期: {today}")
        
        # 访问"首页数据"文件夹，查找今天的日期文件夹
        url = f"https://drive.google.com/embeddedfolderview?id={homepage_folder_id}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_links = soup.find_all('a', href=True)
        today_folder_id = None
        
        for link in all_links:
            href = link.get('href', '')
            foldername = link.get_text(strip=True)
            
            if foldername == today:
                if '/folders/' in href:
                    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', href)
                    if match:
                        today_folder_id = match.group(1)
                        log(f"✅ 找到今天的日期文件夹: {today}")
                        log(f"📂 文件夹ID: {today_folder_id}")
                        break
        
        if not today_folder_id:
            log(f"❌ 未找到今天的日期文件夹: {today}")
            log(f"⚠️  请确保'首页数据'文件夹下存在名为 '{today}' 的子文件夹")
            return False
        
        # 更新配置文件
        config['folder_id'] = today_folder_id
        config['current_date'] = today
        config['folder_name'] = today
        config['auto_update_time'] = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        config['update_reason'] = '每日00:10自动更新到新日期文件夹'
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        log(f"✅ 配置文件已更新")
        log(f"   📅 日期: {today}")
        log(f"   📂 文件夹ID: {today_folder_id}")
        return True
        
    except Exception as e:
        log(f"❌ 更新配置文件失败: {e}")
        import traceback
        log(f"错误详情: {traceback.format_exc()}")
        return False

def daily_trigger_at_00_10():
    """每天 00:10 定时触发"""
    log("=" * 80)
    log("⏰ 定时任务触发: 每日 00:10 自动采集")
    log("=" * 80)
    
    # 先更新配置文件到新日期的文件夹
    log("🔄 步骤1: 更新配置文件到新日期文件夹")
    if update_config_for_new_date():
        log("✅ 配置文件更新成功")
    else:
        log("⚠️ 配置文件更新失败，但仍继续触发采集")
    
    log("")
    log("🔄 步骤2: 触发数据采集")
    trigger_collection("每日 00:10 定时任务")

def check_and_trigger_if_delayed():
    """检查数据延迟，如果超过阈值则触发"""
    now = datetime.now(BEIJING_TZ)
    
    # 只在 00:10 之后检查
    if now.hour == 0 and now.minute < 10:
        return
    
    # 如果在 00:10 到 00:40 之间，检查是否需要触发
    if now.hour == 0 and 10 <= now.minute <= 40:
        latest_data_time = get_latest_data_time()
        
        if latest_data_time:
            # 计算延迟（分钟）
            delay_minutes = (now - latest_data_time).total_seconds() / 60
            
            log(f"📊 数据状态检查: 最新数据时间 {latest_data_time.strftime('%Y-%m-%d %H:%M:%S')}, 延迟 {delay_minutes:.1f} 分钟")
            
            # 如果延迟超过20分钟，触发采集
            if delay_minutes > 20:
                log(f"⚠️ 数据延迟超过20分钟 ({delay_minutes:.1f}分钟)，触发自动采集")
                trigger_collection(f"数据延迟超过20分钟 ({delay_minutes:.1f}分钟)")
        else:
            log("⚠️ 未找到最新数据，触发采集")
            trigger_collection("未找到最新数据")

def periodic_check():
    """定期检查（每5分钟）"""
    now = datetime.now(BEIJING_TZ)
    log(f"🔍 定期检查 - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查数据延迟
    check_and_trigger_if_delayed()

def main():
    """主函数"""
    log("=" * 80)
    log("🚀 Google Drive 自动触发守护进程启动")
    log(f"📁 脚本路径: {SCRIPT_PATH}")
    log(f"💾 数据库路径: {DB_PATH}")
    log(f"📝 日志文件: {LOG_FILE}")
    log("")
    log("⏰ 触发规则:")
    log("   • 每天 00:10 自动触发数据采集")
    log("   • 如果 00:10 后数据延迟超过20分钟，自动触发")
    log("   • 每5分钟检查一次")
    log("=" * 80)
    
    # 设置定时任务
    schedule.every().day.at("00:10").do(daily_trigger_at_00_10)
    schedule.every(5).minutes.do(periodic_check)
    
    log("✅ 定时任务已设置，开始监控...")
    
    # 首次启动时立即检查一次
    log("🔍 启动时执行首次检查...")
    periodic_check()
    
    # 主循环
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)  # 每30秒检查一次是否有待执行的任务
        except KeyboardInterrupt:
            log("\n👋 收到停止信号，正在退出...")
            sys.exit(0)
        except Exception as e:
            log(f"❌ 发生错误: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
