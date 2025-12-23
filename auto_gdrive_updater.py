#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动Google Drive数据更新器
每10分钟自动检查并导入最新的TXT文件
"""

import os
import sys
import time
import sqlite3
import requests
import re
from datetime import datetime
import pytz
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/auto_gdrive_updater.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 配置
PARENT_FOLDER_ID = '1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV'
BEIJING_TZ = pytz.timezone('Asia/Shanghai')
CHECK_INTERVAL = 600  # 10分钟
DB_PATH = '/home/user/webapp/crypto_data.db'

def get_latest_txt_file():
    """获取Google Drive中最新的TXT文件"""
    try:
        current_time = datetime.now(BEIJING_TZ)
        folder_name = current_time.strftime('%Y-%m-%d')
        
        logger.info(f"检查文件夹: {folder_name}")
        
        # 获取父文件夹
        parent_url = f'https://drive.google.com/drive/folders/{PARENT_FOLDER_ID}'
        response = requests.get(parent_url, timeout=15)
        
        # 查找今天的文件夹ID
        pattern = r'"' + re.escape(folder_name) + r'".*?"id":"([^"]+)"'
        match = re.search(pattern, response.text)
        
        if not match:
            logger.warning(f"未找到文件夹: {folder_name}")
            return None
        
        folder_id = match.group(1)
        logger.info(f"找到文件夹ID: {folder_id}")
        
        # 获取文件夹内容
        folder_url = f'https://drive.google.com/drive/folders/{folder_id}'
        folder_response = requests.get(folder_url, timeout=15)
        
        # 查找所有TXT文件
        txt_pattern = r'"(' + re.escape(folder_name) + r'_\d{4})\.txt".*?"id":"([^"]+)"'
        txt_files = re.findall(txt_pattern, folder_response.text)
        
        if not txt_files:
            logger.warning("未找到TXT文件")
            return None
        
        # 获取最新文件
        latest_file = sorted(txt_files, reverse=True)[0]
        latest_filename, latest_id = latest_file
        
        download_url = f'https://drive.google.com/uc?id={latest_id}&export=download'
        
        logger.info(f"最新文件: {latest_filename}.txt")
        return {
            'filename': f'{latest_filename}.txt',
            'file_id': latest_id,
            'download_url': download_url,
            'time': latest_filename.split('_')[1]  # 提取时间部分
        }
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {e}")
        return None

def check_if_imported(filename):
    """检查文件是否已导入"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 从文件名提取时间
        # 格式: 2025-12-09_1246.txt -> 2025-12-09 12:46:00
        date_part, time_part = filename.replace('.txt', '').split('_')
        snapshot_time = f"{date_part} {time_part[:2]}:{time_part[2:]}:00"
        
        cursor.execute("""
            SELECT COUNT(*) FROM crypto_snapshots
            WHERE snapshot_time = ?
        """, (snapshot_time,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
        
    except Exception as e:
        logger.error(f"检查导入状态失败: {e}")
        return False

def download_and_import(file_info):
    """下载并导入TXT文件"""
    try:
        filename = file_info['filename']
        download_url = file_info['download_url']
        
        logger.info(f"开始下载: {filename}")
        
        # 下载文件
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        # 保存到临时文件
        temp_file = f'/tmp/{filename}'
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"文件已下载到: {temp_file}")
        
        # 转换编码为UTF-8
        temp_utf8_file = f'/tmp/{filename.replace(".txt", "_utf8.txt")}'
        os.system(f'iconv -f GBK -t UTF-8 "{temp_file}" > "{temp_utf8_file}"')
        
        # 使用manual_txt_import.py导入
        import_cmd = f'cd /home/user/webapp && python3 manual_txt_import.py "{temp_utf8_file}"'
        result = os.system(import_cmd)
        
        if result == 0:
            logger.info(f"✓ 成功导入: {filename}")
            # 清理临时文件
            os.remove(temp_file)
            os.remove(temp_utf8_file)
            return True
        else:
            logger.error(f"导入失败: {filename}")
            return False
            
    except Exception as e:
        logger.error(f"下载导入失败: {e}")
        return False

def main():
    """主循环"""
    logger.info("=" * 80)
    logger.info("自动Google Drive数据更新器启动")
    logger.info(f"检查间隔: {CHECK_INTERVAL}秒 ({CHECK_INTERVAL//60}分钟)")
    logger.info("=" * 80)
    
    while True:
        try:
            current_time = datetime.now(BEIJING_TZ)
            logger.info(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 开始检查...")
            
            # 获取最新文件
            file_info = get_latest_txt_file()
            
            if file_info:
                filename = file_info['filename']
                
                # 检查是否已导入
                if check_if_imported(filename):
                    logger.info(f"文件已导入，跳过: {filename}")
                else:
                    logger.info(f"发现新文件: {filename}")
                    success = download_and_import(file_info)
                    
                    if success:
                        logger.info("✓ 数据更新成功！")
                    else:
                        logger.warning("✗ 数据更新失败")
            else:
                logger.warning("未找到新文件")
            
            logger.info(f"下次检查时间: {CHECK_INTERVAL}秒后")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n收到停止信号，退出...")
            break
        except Exception as e:
            logger.error(f"主循环错误: {e}")
            logger.info(f"等待{CHECK_INTERVAL}秒后重试...")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
