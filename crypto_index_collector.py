#!/usr/bin/env python3
"""
加密货币指数采集器
- 27个币种加权指数
- 起始点数: 1000点
- 5分钟K线数据
- 从CoinGecko API获取价格（避免OKX限流）
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
        logging.FileHandler('/home/user/webapp/crypto_index_collector.log'),
        logging.StreamHandler()
    ]
)

# CoinGecko API（免费，无需密钥）
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

# 27个币种及其权重
COIN_WEIGHTS = {
    'bitcoin': 0.10,      # BTC 10%
    'ethereum': 0.07,     # ETH 7%
    'ripple': 0.0332,     # XRP 3.32%
    'binancecoin': 0.0332,  # BNB 3.32%
    'solana': 0.0332,     # SOL 3.32%
    'litecoin': 0.0332,   # LTC 3.32%
    'dogecoin': 0.0332,   # DOGE 3.32%
    'sui': 0.0332,        # SUI 3.32%
    'tron': 0.0332,       # TRX 3.32%
    'the-open-network': 0.0332,  # TON 3.32%
    'ethereum-classic': 0.0332,  # ETC 3.32%
    'bitcoin-cash': 0.0332,      # BCH 3.32%
    'hedera-hashgraph': 0.0332,  # HBAR 3.32%
    'stellar': 0.0332,    # XLM 3.32%
    'filecoin': 0.0332,   # FIL 3.32%
    'chainlink': 0.0332,  # LINK 3.32%
    'crypto-com-chain': 0.0332,  # CRO 3.32%
    'polkadot': 0.0332,   # DOT 3.32%
    'aave': 0.0332,       # AAVE 3.32%
    'uniswap': 0.0332,    # UNI 3.32%
    'near': 0.0332,       # NEAR 3.32%
    'aptos': 0.0332,      # APT 3.32%
    'conflux-token': 0.0332,     # CFX 3.32%
    'curve-dao-token': 0.0332,   # CRV 3.32%
    'stacks': 0.0332,     # STX 3.32%
    'lido-dao': 0.0332,   # LDO 3.32%
    'bittensor': 0.0332   # TAO 3.32%
}

# 起始点数
BASE_INDEX = 1000.0

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')


class CryptoIndexCollector:
    def __init__(self):
        self.db_path = '/home/user/webapp/crypto_data.db'
        self.init_database()
        self.base_prices = None  # 基准价格（首次采集时的价格）
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建指数K线表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_index_klines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                index_value REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp)
            )
        ''')
        
        # 创建基准价格表（用于计算指数变化）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_index_base_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL UNIQUE,
                base_price REAL NOT NULL,
                weight REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ 数据库初始化完成")
    
    def fetch_prices(self):
        """从CoinGecko获取所有币种的当前价格"""
        try:
            coin_ids = ','.join(COIN_WEIGHTS.keys())
            params = {
                'ids': coin_ids,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = {}
            for coin_id in COIN_WEIGHTS.keys():
                if coin_id in data and 'usd' in data[coin_id]:
                    prices[coin_id] = data[coin_id]['usd']
                else:
                    logging.warning(f"⚠️  未获取到 {coin_id} 的价格")
            
            logging.info(f"✅ 成功获取 {len(prices)}/27 个币种价格")
            return prices
            
        except Exception as e:
            logging.error(f"❌ 获取价格失败: {str(e)}")
            return None
    
    def load_base_prices(self):
        """加载基准价格"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT coin_id, base_price FROM crypto_index_base_prices")
        rows = cursor.fetchall()
        
        if rows:
            base_prices = {row[0]: row[1] for row in rows}
            conn.close()
            logging.info(f"✅ 加载基准价格: {len(base_prices)} 个币种")
            return base_prices
        
        conn.close()
        return None
    
    def save_base_prices(self, prices):
        """保存基准价格（首次运行时）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for coin_id, price in prices.items():
            weight = COIN_WEIGHTS.get(coin_id, 0)
            cursor.execute('''
                INSERT OR REPLACE INTO crypto_index_base_prices (coin_id, base_price, weight)
                VALUES (?, ?, ?)
            ''', (coin_id, price, weight))
        
        conn.commit()
        conn.close()
        logging.info(f"✅ 保存基准价格: {len(prices)} 个币种")
    
    def calculate_index(self, current_prices, base_prices):
        """
        计算加权指数
        
        公式: Index = BASE_INDEX * Σ(weight_i * (current_price_i / base_price_i))
        """
        if not current_prices or not base_prices:
            return None
        
        weighted_sum = 0.0
        for coin_id, weight in COIN_WEIGHTS.items():
            if coin_id in current_prices and coin_id in base_prices:
                price_ratio = current_prices[coin_id] / base_prices[coin_id]
                weighted_sum += weight * price_ratio
        
        index_value = BASE_INDEX * weighted_sum
        return round(index_value, 2)
    
    def collect_kline_data(self):
        """采集5分钟K线数据"""
        try:
            # 获取当前价格
            current_prices = self.fetch_prices()
            if not current_prices or len(current_prices) < 20:  # 至少要有20个币种有价格
                logging.error(f"❌ 价格数据不足: {len(current_prices) if current_prices else 0}/27")
                return False
            
            # 加载或初始化基准价格
            if self.base_prices is None:
                self.base_prices = self.load_base_prices()
                
                if self.base_prices is None:
                    # 首次运行，设置当前价格为基准价格
                    self.save_base_prices(current_prices)
                    self.base_prices = current_prices
                    logging.info("🎯 首次运行，设置基准价格")
            
            # 计算当前指数值
            index_value = self.calculate_index(current_prices, self.base_prices)
            if index_value is None:
                logging.error("❌ 指数计算失败")
                return False
            
            # 获取5分钟时间窗口的数据（这里简化处理，实际应该收集5分钟内的tick数据）
            # 由于我们每5分钟采集一次，open=close=index_value, high/low也近似为index_value
            # 如果需要更精确的OHLC，需要在5分钟内多次采集
            now = datetime.now(BEIJING_TZ)
            timestamp = now.strftime('%Y-%m-%d %H:%M:00')
            
            # 简化版：open/high/low/close都使用当前值
            # TODO: 改进为在5分钟内采集多个点来计算真实的OHLC
            open_price = index_value
            high_price = index_value
            low_price = index_value
            close_price = index_value
            
            # 保存K线数据
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO crypto_index_klines 
                (timestamp, open_price, high_price, low_price, close_price, index_value)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, open_price, high_price, low_price, close_price, index_value))
            
            conn.commit()
            conn.close()
            
            logging.info(f"✅ 指数采集成功: {timestamp} | 指数值: {index_value:.2f}")
            return True
            
        except Exception as e:
            logging.error(f"❌ 采集K线数据失败: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return False
    
    def run_daemon(self, interval=300):
        """
        守护进程模式运行
        
        参数:
            interval: 采集间隔（秒），默认300秒=5分钟
        """
        logging.info(f"🚀 加密货币指数采集器启动，采集间隔: {interval}秒 (5分钟)")
        
        # 首次采集
        logging.info("📊 执行首次指数采集...")
        self.collect_kline_data()
        
        # 定期采集
        while True:
            try:
                time.sleep(interval)
                logging.info("📊 开始采集指数数据...")
                self.collect_kline_data()
                
            except KeyboardInterrupt:
                logging.info("⏹️  收到停止信号，退出采集器")
                break
            except Exception as e:
                logging.error(f"❌ 采集过程出错: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再继续


if __name__ == '__main__':
    collector = CryptoIndexCollector()
    collector.run_daemon(interval=300)  # 5分钟=300秒
