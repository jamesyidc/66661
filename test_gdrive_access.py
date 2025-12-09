#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Google Drive 公共文件夹访问
"""

import requests
from bs4 import BeautifulSoup
import re

FOLDER_ID = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"

def test_folder_access():
    """测试访问公共文件夹"""
    print("="*70)
    print("测试 Google Drive 公共文件夹访问")
    print("="*70)
    print(f"文件夹ID: {FOLDER_ID}")
    print()
    
    # 方法1: 直接访问文件夹网页
    print("方法1: 访问文件夹网页")
    url = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
    print(f"URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字符")
        
        # 保存响应用于检查
        with open('/tmp/gdrive_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("响应已保存到: /tmp/gdrive_response.html")
        
        # 尝试查找文件夹或文件名称
        print("\n尝试从响应中提取信息...")
        
        # 查找日期格式 YYYY-MM-DD
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, response.text)
        if dates:
            dates = list(set(dates))
            dates.sort(reverse=True)
            print(f"✓ 发现日期模式: {dates[:5]}")
        else:
            print("✗ 未发现日期模式")
        
        # 查找 .txt 文件
        txt_pattern = r'["\']([^"\']*\.txt)["\']'
        txt_files = re.findall(txt_pattern, response.text)
        if txt_files:
            txt_files = list(set(txt_files))
            print(f"✓ 发现 .txt 文件: {txt_files[:5]}")
        else:
            print("✗ 未发现 .txt 文件")
            
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print("\n" + "="*70)
    print("建议:")
    print("1. 确保 Google Drive 文件夹的共享设置为'知道链接的任何人都可以查看'")
    print("2. 或者提供一个示例 txt 文件的内容，我可以直接使用")
    print("3. 或者将 txt 文件上传到其他公共存储（如 GitHub、Pastebin 等）")
    print("="*70)


if __name__ == '__main__':
    test_folder_access()
