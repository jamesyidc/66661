#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化Google Drive数据采集器
使用Playwright浏览器自动化，完全解决动态加载问题
"""

import asyncio
from playwright.async_api import async_playwright
import re
from datetime import datetime
import pytz
import os

class AutoGDriveCollector:
    """自动Google Drive数据采集器"""
    
    def __init__(self, root_folder_id: str):
        self.root_folder_id = root_folder_id
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        self.browser = None
        self.context = None
        self.page = None
        
    async def init_browser(self):
        """初始化浏览器"""
        if not self.browser:
            p = await async_playwright().start()
            self.browser = await p.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            print("✅ 浏览器已启动")
    
    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            print("✅ 浏览器已关闭")
    
    async def find_today_folder_id(self):
        """查找今天日期的文件夹ID"""
        await self.init_browser()
        
        today = datetime.now(self.beijing_tz).strftime('%Y-%m-%d')
        url = f"https://drive.google.com/drive/folders/{self.root_folder_id}"
        
        print(f"\n查找日期文件夹: {today}")
        await self.page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        
        # 使用JavaScript查找今天的文件夹
        js_result = await self.page.evaluate(f'''() => {{
            const folders = [];
            const elements = document.querySelectorAll('[data-id]');
            elements.forEach(el => {{
                const text = el.textContent || '';
                const id = el.getAttribute('data-id');
                if (text.includes('{today}') && id) {{
                    folders.push(id);
                }}
            }});
            return folders;
        }}''')
        
        if js_result and len(js_result) > 0:
            folder_id = js_result[0]
            print(f"✅ 找到文件夹ID: {folder_id}")
            return folder_id
        
        print(f"❌ 未找到 {today} 文件夹")
        return None
    
    async def get_latest_file_from_folder(self, folder_id: str):
        """从文件夹获取最新的TXT文件"""
        await self.init_browser()
        
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        print(f"\n访问文件夹: {url}")
        
        await self.page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        
        content = await self.page.content()
        
        # 提取所有TXT文件
        pattern = r'(2025-\d{2}-\d{2}_\d{4}\.txt)'
        matches = re.findall(pattern, content)
        
        if not matches:
            print("❌ 未找到任何TXT文件")
            return None
        
        unique_files = list(set(matches))
        print(f"✅ 找到 {len(unique_files)} 个文件")
        
        # 解析并排序
        file_list = []
        for filename in unique_files:
            try:
                match = re.match(r'(\d{4}-\d{2}-\d{2})_(\d{4})\.txt', filename)
                if match:
                    date_str = match.group(1)
                    time_str = match.group(2)
                    file_datetime = datetime.strptime(
                        f"{date_str} {time_str[:2]}:{time_str[2:]}", 
                        "%Y-%m-%d %H:%M"
                    )
                    file_list.append({
                        'filename': filename,
                        'datetime': file_datetime,
                        'time_str': f"{time_str[:2]}:{time_str[2:]}"
                    })
            except:
                pass
        
        if not file_list:
            return None
        
        # 按时间倒序
        file_list.sort(key=lambda x: x['datetime'], reverse=True)
        latest = file_list[0]
        
        now = datetime.now(self.beijing_tz)
        time_diff = (now.replace(tzinfo=None) - latest['datetime']).total_seconds() / 60
        
        print(f"最新文件: {latest['filename']}")
        print(f"文件时间: {latest['time_str']}")
        print(f"时间差: {time_diff:.1f} 分钟")
        
        return latest
    
    async def download_file_content(self, folder_id: str, filename: str):
        """
        尝试下载文件内容
        注意：由于Google Drive的限制，无法直接下载，需要找到文件的直接下载链接
        """
        # 这里需要更复杂的逻辑来获取文件内容
        # 暂时返回None，表示需要其他方法
        print(f"⚠️ 无法直接下载文件内容，需要文件的直接分享链接")
        return None
    
    async def collect_latest_data(self):
        """采集最新数据的完整流程"""
        now = datetime.now(self.beijing_tz)
        print(f"{'='*60}")
        print(f"开始数据采集")
        print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 1. 找到今天的文件夹
            folder_id = await self.find_today_folder_id()
            if not folder_id:
                return None
            
            # 2. 获取最新文件
            latest_file = await self.get_latest_file_from_folder(folder_id)
            if not latest_file:
                return None
            
            # 3. 返回文件信息
            return {
                'folder_id': folder_id,
                'filename': latest_file['filename'],
                'file_time': latest_file['datetime'],
                'time_str': latest_file['time_str']
            }
            
        except Exception as e:
            print(f"❌ 采集失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

async def main():
    """测试函数"""
    collector = AutoGDriveCollector("1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV")
    
    try:
        result = await collector.collect_latest_data()
        
        if result:
            print(f"\n{'='*60}")
            print("✅ 采集成功")
            print(f"{'='*60}")
            print(f"文件夹ID: {result['folder_id']}")
            print(f"文件名: {result['filename']}")
            print(f"文件时间: {result['time_str']}")
        else:
            print(f"\n{'='*60}")
            print("❌ 采集失败")
            print(f"{'='*60}")
    finally:
        await collector.close_browser()

if __name__ == "__main__":
    asyncio.run(main())
