#!/usr/bin/env python3
"""
交易信号采集器
- 每3分钟从filtered-signals API采集做多/做空信号数量
- 存储到数据库，支持历史查询
- 生成12小时曲线图
"""

import sqlite3
import requests
import time
import json
from datetime import datetime, timedelta
import logging
import pytz

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/signal_collector.log'),
        logging.StreamHandler()
    ]
)

# API基础URL
BASE_URL = "https://8080-im9p8x4s7ohv1llw8snop-dfc00ec5.sandbox.novita.ai"

class SignalCollector:
    def __init__(self, db_path='crypto_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_time TEXT NOT NULL,
                record_date TEXT NOT NULL,
                long_signals INTEGER DEFAULT 0,
                short_signals INTEGER DEFAULT 0,
                total_signals INTEGER DEFAULT 0,
                long_ratio REAL DEFAULT 0,
                short_ratio REAL DEFAULT 0,
                today_new_high INTEGER DEFAULT 0,
                today_new_low INTEGER DEFAULT 0,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引加速查询
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_record_time 
            ON trading_signals(record_time)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_record_date 
            ON trading_signals(record_date)
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ 数据库初始化完成")
    
    def fetch_signals(self):
        """从API获取信号数据"""
        try:
            # 1. 获取首页统计数据（今日新高、新低）
            summary_url = f"{BASE_URL}/api/kline/summary"
            summary_resp = requests.get(summary_url, timeout=30)
            summary_data = summary_resp.json()
            
            today_new_high = 0
            today_new_low = 0
            
            if summary_data.get('data') and len(summary_data['data']) > 0:
                first_record = summary_data['data'][0]
                today_new_high = first_record.get('today_rise_count', 0)
                today_new_low = first_record.get('today_crash_count', 0)
            
            # 2. 直接使用 stats-js 接口获取信号统计（已应用RSI过滤）
            stats_js_url = f"{BASE_URL}/api/filtered-signals/stats-js"
            stats_resp = requests.get(stats_js_url, timeout=30)
            stats_data = stats_resp.json()
            
            # 从 summary 中获取信号统计
            summary = stats_data.get('summary', {})
            long_signals = summary.get('long', 0)
            short_signals = summary.get('short', 0)
            total_signals = summary.get('total', 0)
            
            # 计算比例
            long_ratio = (long_signals / total_signals * 100) if total_signals > 0 else 0
            short_ratio = (short_signals / total_signals * 100) if total_signals > 0 else 0
            
            # 获取详细分类统计
            breakdown = stats_data.get('breakdown', {})
            
            result = {
                'long_signals': long_signals,
                'short_signals': short_signals,
                'total_signals': total_signals,
                'long_ratio': round(long_ratio, 2),
                'short_ratio': round(short_ratio, 2),
                'today_new_high': today_new_high,
                'today_new_low': today_new_low,
                'raw_data': json.dumps({
                    'summary': summary,
                    'breakdown': breakdown,
                    'filters': stats_data.get('filters', {})
                })
            }
            
            logging.info(f"✅ 信号采集成功: 总信号={total_signals}, 做多={long_signals}, 做空={short_signals}")
            return result
            
        except Exception as e:
            logging.error(f"❌ 信号采集失败: {str(e)}")
            return None
    
    def get_last_signal(self):
        """获取最后一条信号记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT long_signals, short_signals, total_signals, record_time
                FROM trading_signals 
                ORDER BY id DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'long_signals': row[0],
                    'short_signals': row[1],
                    'total_signals': row[2],
                    'record_time': row[3]
                }
            return None
            
        except Exception as e:
            logging.error(f"❌ 获取最后一条记录失败: {str(e)}")
            return None
    
    def validate_signal_data(self, signal_data):
        """
        验证信号数据是否有效
        如果前一次有信号，但新数据做多=0且做空=0，则认为数据未刷新完成
        """
        # 获取上一次记录
        last_signal = self.get_last_signal()
        
        # 如果没有历史记录，直接返回有效
        if not last_signal:
            return True
        
        # 检查新数据是否为零信号
        new_long = signal_data['long_signals']
        new_short = signal_data['short_signals']
        new_total = signal_data['total_signals']
        
        # 检查上一次是否有信号
        last_long = last_signal['long_signals']
        last_short = last_signal['short_signals']
        last_total = last_signal['total_signals']
        
        # 如果上一次有信号（总信号>0），但新数据做多=0且做空=0
        if last_total > 0 and new_long == 0 and new_short == 0:
            logging.warning(f"⚠️  数据验证失败: 前一次有信号(做多={last_long}, 做空={last_short}), 但新数据全为0")
            logging.warning(f"   上次记录时间: {last_signal['record_time']}")
            logging.warning(f"   判断: 数据未刷新完成，拒绝保存")
            return False
        
        # 数据有效
        return True
    
    def save_signal(self, signal_data):
        """保存信号数据到数据库（使用北京时间）"""
        if not signal_data:
            return False
        
        # 验证数据有效性
        if not self.validate_signal_data(signal_data):
            logging.info("🔄 数据无效，将在下次采集时重新获取")
            return False
        
        try:
            # 使用北京时间
            beijing_tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(beijing_tz)
            record_time = now.strftime('%Y-%m-%d %H:%M:%S')
            record_date = now.strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trading_signals (
                    record_time, record_date, long_signals, short_signals,
                    total_signals, long_ratio, short_ratio,
                    today_new_high, today_new_low, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_time,
                record_date,
                signal_data['long_signals'],
                signal_data['short_signals'],
                signal_data['total_signals'],
                signal_data['long_ratio'],
                signal_data['short_ratio'],
                signal_data['today_new_high'],
                signal_data['today_new_low'],
                signal_data['raw_data']
            ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"💾 数据保存成功: {record_time}")
            return True
            
        except Exception as e:
            logging.error(f"❌ 数据保存失败: {str(e)}")
            return False
    
    def collect_once(self, max_retries=3, retry_delay=10):
        """
        执行一次采集
        max_retries: 最大重试次数（如果数据未刷新完成）
        retry_delay: 重试间隔（秒）
        """
        for attempt in range(max_retries):
            signal_data = self.fetch_signals()
            
            if not signal_data:
                logging.error(f"❌ 第 {attempt + 1} 次采集失败，无法获取数据")
                if attempt < max_retries - 1:
                    logging.info(f"⏳ 等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                continue
            
            # 尝试保存数据（会自动验证）
            if self.save_signal(signal_data):
                logging.info(f"✅ 数据采集并保存成功（第 {attempt + 1} 次尝试）")
                return True
            else:
                # 数据验证失败（可能是未刷新完成）
                if attempt < max_retries - 1:
                    logging.info(f"🔄 第 {attempt + 1} 次采集数据无效，等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    logging.error(f"❌ 已达到最大重试次数 ({max_retries})，本轮采集失败")
        
        return False
    
    def run_daemon(self, interval=180):
        """
        守护进程模式运行
        interval: 采集间隔（秒），默认180秒=3分钟
        """
        logging.info(f"🚀 信号采集守护进程启动，采集间隔: {interval}秒")
        
        while True:
            try:
                self.collect_once()
                logging.info(f"⏳ 等待 {interval} 秒后进行下一次采集...")
                time.sleep(interval)
            except KeyboardInterrupt:
                logging.info("⛔ 收到停止信号，退出采集")
                break
            except Exception as e:
                logging.error(f"❌ 采集过程出错: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再试

def main():
    collector = SignalCollector()
    
    # 立即执行一次采集
    logging.info("📊 执行首次信号采集...")
    collector.collect_once()
    
    # 启动守护进程（3分钟间隔）
    collector.run_daemon(interval=180)

if __name__ == '__main__':
    main()
