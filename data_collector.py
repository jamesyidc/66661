#!/usr/bin/env python3
"""
数据采集器 - 定时从Google Drive读取数据并保存到数据库
按照TXT文件标记的时间晚1分钟执行采集
"""

import time
import sys
from datetime import datetime, timedelta
import pytz
from monitor_data_reader import MonitorDataReader
from crypto_database import CryptoDatabase

class DataCollector:
    """数据采集器"""
    
    def __init__(self):
        """初始化数据采集器"""
        self.reader = MonitorDataReader()
        self.db = CryptoDatabase()
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        self.last_signal_time = None
        self.last_panic_time = None
        
        print("="*60)
        print("数据采集器已启动")
        print("="*60)
        print(f"启动时间: {datetime.now(self.beijing_tz).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"采集策略: 按照TXT时间晚1分钟采集")
        print("="*60 + "\n")
    
    def parse_time_from_txt(self, time_str: str) -> datetime:
        """
        解析TXT文件中的时间字符串
        
        Args:
            time_str: 时间字符串，格式如 "2025-12-02 21:14:40"
            
        Returns:
            datetime对象（北京时间）
        """
        try:
            # 解析时间字符串
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            # 设置为北京时区
            dt = self.beijing_tz.localize(dt)
            return dt
        except Exception as e:
            print(f"❌ 解析时间失败: {e}")
            return None
    
    def should_collect_signal(self, signal_data: dict) -> bool:
        """
        判断是否应该采集信号数据
        
        逻辑：
        1. TXT文件中的时间标记为数据生成时间
        2. 我们在该时间晚1分钟后采集
        3. 避免重复采集相同时间的数据
        
        Args:
            signal_data: 信号数据字典
            
        Returns:
            True表示应该采集，False表示跳过
        """
        try:
            txt_time_str = signal_data['update_time']
            txt_time = self.parse_time_from_txt(txt_time_str)
            
            if not txt_time:
                return False
            
            # 如果这是我们第一次看到的时间，记录它
            if self.last_signal_time is None:
                self.last_signal_time = txt_time
                print(f"ℹ️  首次采集信号数据，TXT时间: {txt_time_str}")
                return True
            
            # 如果TXT时间比上次采集的时间晚，说明有新数据
            if txt_time > self.last_signal_time:
                print(f"✅ 发现新的信号数据！")
                print(f"   上次时间: {self.last_signal_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   本次时间: {txt_time_str}")
                self.last_signal_time = txt_time
                return True
            
            # 数据没有更新，跳过
            return False
            
        except Exception as e:
            print(f"❌ 判断采集失败: {e}")
            return False
    
    def should_collect_panic(self, panic_data: dict) -> bool:
        """
        判断是否应该采集恐慌清洗数据
        
        Args:
            panic_data: 恐慌清洗数据字典
            
        Returns:
            True表示应该采集，False表示跳过
        """
        try:
            txt_time_str = panic_data['update_time']
            txt_time = self.parse_time_from_txt(txt_time_str)
            
            if not txt_time:
                return False
            
            # 如果这是我们第一次看到的时间，记录它
            if self.last_panic_time is None:
                self.last_panic_time = txt_time
                print(f"ℹ️  首次采集恐慌清洗数据，TXT时间: {txt_time_str}")
                return True
            
            # 如果TXT时间比上次采集的时间晚，说明有新数据
            if txt_time > self.last_panic_time:
                print(f"✅ 发现新的恐慌清洗数据！")
                print(f"   上次时间: {self.last_panic_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   本次时间: {txt_time_str}")
                self.last_panic_time = txt_time
                return True
            
            # 数据没有更新，跳过
            return False
            
        except Exception as e:
            print(f"❌ 判断采集失败: {e}")
            return False
    
    def collect_signal_data(self):
        """采集信号数据"""
        try:
            # 读取数据
            signal_data = self.reader.get_signal_data()
            
            # 判断是否应该采集
            if not self.should_collect_signal(signal_data):
                return
            
            # 保存到数据库
            success = self.db.save_signal_data(signal_data)
            
            if success:
                print(f"✅ 信号数据已保存到数据库")
                print(f"   做空: {signal_data['short']} (变化: {signal_data['short_change']})")
                print(f"   做多: {signal_data['long']} (变化: {signal_data['long_change']})")
            else:
                print(f"❌ 保存信号数据失败")
                
        except Exception as e:
            print(f"❌ 采集信号数据异常: {e}")
    
    def collect_panic_data(self):
        """采集恐慌清洗数据"""
        try:
            # 读取数据
            panic_data = self.reader.get_panic_data()
            
            # 判断是否应该采集
            if not self.should_collect_panic(panic_data):
                return
            
            # 保存到数据库
            success = self.db.save_panic_data(panic_data)
            
            if success:
                print(f"✅ 恐慌清洗数据已保存到数据库")
                print(f"   恐慌指标: {panic_data['panic_indicator']}")
                print(f"   趋势评级: {panic_data['trend_rating']}")
                print(f"   市场区间: {panic_data['market_zone']}")
            else:
                print(f"❌ 保存恐慌清洗数据失败")
                
        except Exception as e:
            print(f"❌ 采集恐慌清洗数据异常: {e}")
    
    def run_once(self):
        """执行一次数据采集"""
        now = datetime.now(self.beijing_tz)
        print(f"\n{'='*60}")
        print(f"开始采集数据 - {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 采集信号数据
        print("\n📊 采集信号数据...")
        self.collect_signal_data()
        
        # 采集恐慌清洗数据
        print("\n📊 采集恐慌清洗数据...")
        self.collect_panic_data()
        
        print(f"\n{'='*60}")
        print(f"采集完成")
        print(f"{'='*60}\n")
    
    def run_forever(self, interval_seconds=60):
        """
        持续运行数据采集器
        
        Args:
            interval_seconds: 采集间隔（秒），默认60秒
        """
        print(f"采集间隔: {interval_seconds}秒")
        print(f"持续运行中... (按 Ctrl+C 停止)\n")
        
        try:
            while True:
                self.run_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\n⚠️  收到停止信号，数据采集器正在关闭...")
            print("✅ 数据采集器已停止\n")
        except Exception as e:
            print(f"\n❌ 数据采集器异常: {e}")
            raise


def main():
    """主函数"""
    collector = DataCollector()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            # 仅执行一次
            collector.run_once()
        elif sys.argv[1] == '--interval':
            # 指定间隔
            if len(sys.argv) > 2:
                interval = int(sys.argv[2])
                collector.run_forever(interval)
            else:
                print("❌ 错误: --interval 需要指定秒数")
                print("用法: python3 data_collector.py --interval 60")
        else:
            print("用法:")
            print("  python3 data_collector.py                  # 默认60秒间隔持续运行")
            print("  python3 data_collector.py --once           # 仅执行一次")
            print("  python3 data_collector.py --interval 60    # 指定间隔（秒）")
    else:
        # 默认60秒间隔持续运行
        collector.run_forever(60)


if __name__ == '__main__':
    main()
