#!/usr/bin/env python3
"""
自动更新每日文件夹配置
- 检测日期变化
- 自动搜索新日期的文件夹ID
- 更新 daily_folder_config.json
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 配置
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "daily_folder_config.json"
LOG_FILE = BASE_DIR / "logs/auto_update_folder.log"

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_current_date_beijing():
    """获取北京时间当前日期"""
    now = datetime.now(BEIJING_TZ)
    return now.strftime('%Y-%m-%d')

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        return None

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logging.info(f"✅ 配置已保存: {CONFIG_FILE}")
        return True
    except Exception as e:
        logging.error(f"保存配置文件失败: {e}")
        return False

def explore_drive_folder(folder_id, target_folder_name=None):
    """
    探索Google Drive文件夹
    返回文件夹列表 [{name, id}, ...]
    """
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        html = response.text
        
        # 解析文件夹列表
        folders = []
        import re
        
        # 匹配文件夹项
        # 格式: <div class="flip-entry" id="entry-...">
        pattern = r'<div class="flip-entry"[^>]*id="entry-([^"]+)"[^>]*>.*?<div[^>]*title="([^"]+)"'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for folder_id_match, folder_name in matches:
            # 只保留文件夹（通过检查是否有 dir- 前缀）
            if folder_id_match.startswith('dir-'):
                actual_id = folder_id_match.replace('dir-', '')
                folders.append({
                    'name': folder_name,
                    'id': actual_id
                })
        
        # 如果指定了目标文件夹名，查找匹配的
        if target_folder_name:
            for folder in folders:
                if folder['name'] == target_folder_name:
                    return folder
            return None
        
        return folders
        
    except Exception as e:
        logging.error(f"探索文件夹失败: {e}")
        return None if target_folder_name else []

def find_today_folder(parent_folder_id, today_date):
    """
    在父文件夹中查找今天日期的文件夹
    返回: {name, id} 或 None
    """
    logging.info(f"🔍 在父文件夹 {parent_folder_id} 中查找 '{today_date}' 文件夹...")
    
    folder = explore_drive_folder(parent_folder_id, today_date)
    
    if folder:
        logging.info(f"✅ 找到目标文件夹: {folder['name']} (ID: {folder['id']})")
        return folder
    else:
        logging.warning(f"⚠️ 未找到 '{today_date}' 文件夹")
        return None

def auto_update_config():
    """自动更新配置文件"""
    logging.info("="*70)
    logging.info("🔄 开始自动更新文件夹配置")
    logging.info("="*70)
    
    # 1. 获取当前日期（北京时间）
    today_date = get_current_date_beijing()
    logging.info(f"📅 当前日期（北京时间）: {today_date}")
    
    # 2. 加载配置
    config = load_config()
    if not config:
        logging.error("❌ 无法加载配置文件")
        return False
    
    current_date_in_config = config.get('current_date', '')
    logging.info(f"📝 配置文件中的日期: {current_date_in_config}")
    
    # 3. 检查是否需要更新
    if current_date_in_config == today_date:
        logging.info(f"✅ 配置日期已是最新 ({today_date})，无需更新")
        return True
    
    logging.warning(f"⚠️ 配置日期 ({current_date_in_config}) 与当前日期 ({today_date}) 不匹配")
    logging.info(f"🔄 开始查找新日期文件夹...")
    
    # 4. 查找新日期的文件夹
    parent_folder_id = config.get('parent_folder_id', '')
    if not parent_folder_id:
        logging.error("❌ 配置文件中缺少 parent_folder_id")
        return False
    
    today_folder = find_today_folder(parent_folder_id, today_date)
    
    if not today_folder:
        logging.error(f"❌ 未能找到 {today_date} 文件夹，无法自动更新")
        return False
    
    # 5. 更新配置
    old_config = config.copy()
    config['current_date'] = today_date
    config['folder_id'] = today_folder['id']
    config['updated_at'] = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    config['auto_updated'] = True
    config['file_count'] = 0  # 重置文件计数
    
    # 6. 保存配置
    if save_config(config):
        logging.info("="*70)
        logging.info("✅ 文件夹配置自动更新成功")
        logging.info("="*70)
        logging.info(f"📅 日期: {old_config.get('current_date')} → {config['current_date']}")
        logging.info(f"📁 文件夹ID: {old_config.get('folder_id')} → {config['folder_id']}")
        logging.info(f"🕐 更新时间: {config['updated_at']}")
        logging.info("="*70)
        return True
    else:
        logging.error("❌ 保存配置失败")
        return False

if __name__ == "__main__":
    try:
        success = auto_update_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.critical(f"❌ 自动更新失败: {e}", exc_info=True)
        sys.exit(2)
