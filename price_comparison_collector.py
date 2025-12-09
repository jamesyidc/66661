#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比价系统数据采集器
功能：
1. 从 crypto_coin_data 表获取最新的币种价格
2. 与 price_comparison 表中的基准价格比较
3. 自动更新创新高/创新低
4. 记录突破事件
5. 每10分钟（与主采集器同步）自动运行一次
"""

import sqlite3
import time
import logging
from datetime import datetime
import pytz

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/price_comparison_collector.log'),
        logging.StreamHandler()
    ]
)

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')
DB_PATH = 'crypto_data.db'

class PriceComparisonCollector:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def get_latest_prices(self):
        """从 crypto_coin_data 获取最新价格"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取最新快照时间
            cursor.execute("""
                SELECT MAX(snapshot_time) FROM crypto_coin_data
            """)
            latest_snapshot = cursor.fetchone()[0]
            
            if not latest_snapshot:
                logging.warning("⚠️ 没有找到最新的快照数据")
                conn.close()
                return {}
            
            # 获取该快照时间的所有币种价格
            cursor.execute("""
                SELECT symbol, current_price, update_time
                FROM crypto_coin_data
                WHERE snapshot_time = ?
            """, (latest_snapshot,))
            
            prices = {}
            for row in cursor.fetchall():
                symbol = row[0]
                current_price = row[1]
                update_time = row[2]
                
                if current_price and current_price > 0:
                    prices[symbol] = {
                        'price': current_price,
                        'update_time': update_time or latest_snapshot
                    }
            
            conn.close()
            logging.info(f"✅ 获取到 {len(prices)} 个币种的最新价格 (快照时间: {latest_snapshot})")
            return prices
            
        except Exception as e:
            logging.error(f"❌ 获取最新价格失败: {str(e)}")
            return {}
    
    def compare_and_update_prices(self, latest_prices):
        """比较并更新价格，返回突破事件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            beijing_time = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
            breakthrough_events = []
            
            for symbol, price_data in latest_prices.items():
                current_price = price_data['price']
                update_time = price_data['update_time']
                
                # 获取基准数据
                cursor.execute("""
                    SELECT coin_name, highest_price, highest_count, lowest_price, lowest_count
                    FROM price_comparison
                    WHERE coin_name = ?
                """, (symbol,))
                
                row = cursor.fetchone()
                
                if not row:
                    logging.debug(f"跳过 {symbol} - 没有基准数据")
                    continue
                
                coin_name, highest_price, highest_count, lowest_price, lowest_count = row
                old_highest_price = highest_price
                old_lowest_price = lowest_price
                
                # 价格比较逻辑
                action = 'in_range'
                
                if current_price > highest_price:
                    # 创新高
                    action = 'new_high'
                    old_highest_price = highest_price
                    highest_price = current_price
                    highest_count = 0
                    
                    event = {
                        'symbol': symbol,
                        'type': 'new_high',
                        'old_price': old_highest_price,
                        'new_price': current_price,
                        'time': beijing_time
                    }
                    breakthrough_events.append(event)
                    
                    # 记录突破事件
                    cursor.execute("""
                        INSERT INTO price_breakthrough_events
                        (coin_name, event_type, price, previous_extreme_price, event_time)
                        VALUES (?, ?, ?, ?, ?)
                    """, (symbol, 'new_high', current_price, old_highest_price, beijing_time))
                    
                    logging.info(f"🚀 {symbol} 创新高: ${old_highest_price:.6f} -> ${current_price:.6f}")
                    
                elif current_price < lowest_price:
                    # 创新低
                    action = 'new_low'
                    old_lowest_price = lowest_price
                    lowest_price = current_price
                    lowest_count = 0
                    
                    event = {
                        'symbol': symbol,
                        'type': 'new_low',
                        'old_price': old_lowest_price,
                        'new_price': current_price,
                        'time': beijing_time
                    }
                    breakthrough_events.append(event)
                    
                    # 记录突破事件
                    cursor.execute("""
                        INSERT INTO price_breakthrough_events
                        (coin_name, event_type, price, previous_extreme_price, event_time)
                        VALUES (?, ?, ?, ?, ?)
                    """, (symbol, 'new_low', current_price, old_lowest_price, beijing_time))
                    
                    logging.info(f"📉 {symbol} 创新低: ${old_lowest_price:.6f} -> ${current_price:.6f}")
                    
                else:
                    # 在区间内，增加计次
                    highest_count += 1
                    lowest_count += 1
                
                # 计算占比
                highest_ratio = round((current_price / highest_price) * 100, 2) if highest_price > 0 else 0
                lowest_ratio = round((current_price / lowest_price) * 100, 2) if lowest_price > 0 else 0
                
                # 更新数据库
                cursor.execute("""
                    UPDATE price_comparison
                    SET highest_price = ?,
                        highest_count = ?,
                        lowest_price = ?,
                        lowest_count = ?,
                        highest_ratio = ?,
                        lowest_ratio = ?,
                        last_update_time = ?
                    WHERE coin_name = ?
                """, (highest_price, highest_count, lowest_price, lowest_count,
                      highest_ratio, lowest_ratio, beijing_time, symbol))
            
            conn.commit()
            conn.close()
            
            logging.info(f"✅ 更新完成: {len(latest_prices)} 个币种, {len(breakthrough_events)} 个突破事件")
            return breakthrough_events
            
        except Exception as e:
            logging.error(f"❌ 比价更新失败: {str(e)}")
            return []
    
    def collect_once(self):
        """执行一次数据采集"""
        logging.info("=" * 60)
        logging.info("🔄 开始比价系统数据采集...")
        
        # 1. 获取最新价格
        latest_prices = self.get_latest_prices()
        
        if not latest_prices:
            logging.warning("⚠️ 没有获取到价格数据，跳过本次采集")
            return
        
        # 2. 比较并更新
        breakthrough_events = self.compare_and_update_prices(latest_prices)
        
        # 3. 输出突破事件汇总
        if breakthrough_events:
            logging.info("📢 突破事件汇总:")
            new_highs = [e for e in breakthrough_events if e['type'] == 'new_high']
            new_lows = [e for e in breakthrough_events if e['type'] == 'new_low']
            
            if new_highs:
                logging.info(f"   🚀 创新高 ({len(new_highs)}个): {', '.join([e['symbol'] for e in new_highs])}")
            if new_lows:
                logging.info(f"   📉 创新低 ({len(new_lows)}个): {', '.join([e['symbol'] for e in new_lows])}")
        else:
            logging.info("ℹ️  本次采集无突破事件")
        
        logging.info("✅ 比价系统数据采集完成")
    
    def run_daemon(self, interval=600):
        """
        守护进程模式运行
        
        参数:
            interval: 采集间隔（秒），默认600秒=10分钟（与主采集器同步）
        """
        logging.info(f"🚀 比价系统采集器启动，采集间隔: {interval}秒 ({interval//60}分钟)")
        
        while True:
            try:
                self.collect_once()
                logging.info(f"⏳ 等待 {interval} 秒后进行下一次采集...\n")
                time.sleep(interval)
            except KeyboardInterrupt:
                logging.info("⛔ 收到停止信号，退出采集器")
                break
            except Exception as e:
                logging.error(f"❌ 采集循环异常: {str(e)}")
                logging.info(f"⏳ 等待 {interval} 秒后重试...")
                time.sleep(interval)


if __name__ == '__main__':
    collector = PriceComparisonCollector()
    
    # 先执行一次立即采集
    collector.collect_once()
    
    # 启动守护进程（每10分钟采集一次，与主数据采集器同步）
    collector.run_daemon(interval=600)
