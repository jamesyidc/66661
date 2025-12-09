#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据采集器 - 用于从实际API获取得分数据
当数据源API可用时，可以替换score_system.py中的模拟数据生成器
"""

import requests
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealScoreCollector:
    """真实得分数据采集器"""
    
    def __init__(self):
        # 数据源配置
        self.data_sources = {
            'source_1_19_coins': {
                'base_url': 'https://3000-i42fq2f1mk8544uuc8pew-5c13a017.sandbox.novita.ai',
                'api_port': 5011,
                'symbols': [
                    'BTC-USDT-SWAP', 'ETH-USDT-SWAP', 'BNB-USDT-SWAP',
                    'SOL-USDT-SWAP', 'DOT-USDT-SWAP', 'LINK-USDT-SWAP',
                    'ADA-USDT-SWAP', 'FIL-USDT-SWAP', 'DOGE-USDT-SWAP',
                    'ETC-USDT-SWAP', 'AVAX-USDT-SWAP', 'MATIC-USDT-SWAP',
                    'OKB-USDT-SWAP', 'PEPE-USDT-SWAP', 'SHIB-USDT-SWAP',
                    'ATOM-USDT-SWAP', 'XRP-USDT-SWAP', 'TRX-USDT-SWAP',
                    'LTC-USDT-SWAP'
                ]
            },
            'source_2_8_coins': {
                'base_url': 'https://3000-itkyuobnbphje7wgo4xbk-c07dda5e.sandbox.novita.ai',
                'api_port': 5011,
                'symbols': [
                    'FIL-USDT-SWAP', 'UNI-USDT-SWAP', 'TAO-USDT-SWAP',
                    'CFX-USDT-SWAP', 'BTC-USDT-SWAP', 'HBAR-USDT-SWAP',
                    'XLM-USDT-SWAP', 'BCH-USDT-SWAP'
                ]
            }
        }
        
        self.time_ranges = ['3m', '1h', '3h', '6h', '12h', '24h']
        self.timeout = 10  # API请求超时时间（秒）
    
    def get_api_url(self, source_config: Dict, symbol: str, time_range: str) -> str:
        """
        构建API URL
        
        根据实际API结构调整，示例格式：
        https://5011-xxx/api/depth/history/{symbol}?range={range}
        """
        base_url = source_config['base_url']
        port = source_config['api_port']
        
        # 将端口号替换到URL中
        if '3000-' in base_url:
            api_url = base_url.replace('3000-', f'{port}-')
        else:
            api_url = f"{base_url.split('://')[0]}://{port}-{base_url.split('://')[1].split('-', 1)[1]}"
        
        return f"{api_url}/api/depth/history/{symbol}?range={time_range}"
    
    def parse_score_from_response(self, data: Dict) -> Tuple[Optional[float], Optional[float]]:
        """
        从API响应中解析得分数据
        
        根据实际API响应格式调整解析逻辑
        
        示例响应格式1：
        {
            "symbol": "BTC-USDT-SWAP",
            "range": "3m",
            "long_score": 52.3,
            "short_score": 48.7,
            "timestamp": "2025-12-03T15:00:00Z"
        }
        
        示例响应格式2：
        {
            "data": {
                "scores": {
                    "long": 52.3,
                    "short": 48.7
                }
            }
        }
        """
        try:
            # 尝试多种可能的响应格式
            
            # 格式1：直接在根级别
            if 'long_score' in data and 'short_score' in data:
                return float(data['long_score']), float(data['short_score'])
            
            # 格式2：在data字段中
            if 'data' in data:
                if 'long_score' in data['data'] and 'short_score' in data['data']:
                    return float(data['data']['long_score']), float(data['data']['short_score'])
                
                if 'scores' in data['data']:
                    scores = data['data']['scores']
                    if 'long' in scores and 'short' in scores:
                        return float(scores['long']), float(scores['short'])
            
            # 格式3：在results或scores字段中
            if 'scores' in data:
                if 'long' in data['scores'] and 'short' in data['scores']:
                    return float(data['scores']['long']), float(data['scores']['short'])
            
            # 格式4：嵌套的score对象
            if 'score' in data:
                score = data['score']
                if 'long' in score and 'short' in score:
                    return float(score['long']), float(score['short'])
            
            # 如果都不匹配，记录警告
            logger.warning(f"无法解析得分数据，响应格式未知: {data.keys()}")
            return None, None
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"解析得分数据失败: {e}")
            return None, None
    
    def fetch_score(self, source_name: str, symbol: str, time_range: str) -> Tuple[Optional[float], Optional[float]]:
        """
        从指定数据源获取得分
        
        Args:
            source_name: 数据源名称
            symbol: 币种符号
            time_range: 时间范围
        
        Returns:
            (long_score, short_score) 或 (None, None) 如果失败
        """
        try:
            source_config = self.data_sources[source_name]
            url = self.get_api_url(source_config, symbol, time_range)
            
            logger.debug(f"请求 {source_name}: {symbol} {time_range}")
            logger.debug(f"URL: {url}")
            
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            long_score, short_score = self.parse_score_from_response(data)
            
            if long_score is not None and short_score is not None:
                logger.info(f"✅ {symbol} {time_range}: 做多={long_score:.2f}, 做空={short_score:.2f}")
                return long_score, short_score
            else:
                logger.warning(f"⚠️ {symbol} {time_range}: 无法解析得分")
                return None, None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ {symbol} {time_range}: 请求超时")
            return None, None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {symbol} {time_range}: 请求失败 - {e}")
            return None, None
        except Exception as e:
            logger.error(f"❌ {symbol} {time_range}: 未知错误 - {e}")
            return None, None
    
    def collect_all_scores(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """
        采集所有数据源的所有得分
        
        Returns:
            {
                'BTC-USDT-SWAP': {
                    '3m': (52.3, 48.7),
                    '1h': (51.2, 49.1),
                    ...
                },
                ...
            }
        """
        logger.info("🔄 开始采集所有得分数据...")
        start_time = datetime.now()
        
        all_scores = {}
        success_count = 0
        fail_count = 0
        
        # 合并所有数据源的币种列表（去重）
        all_symbols = set()
        source_for_symbol = {}  # 记录每个币种的数据源
        
        for source_name, source_config in self.data_sources.items():
            for symbol in source_config['symbols']:
                all_symbols.add(symbol)
                if symbol not in source_for_symbol:
                    source_for_symbol[symbol] = []
                source_for_symbol[symbol].append(source_name)
        
        logger.info(f"📊 总计 {len(all_symbols)} 个币种需要采集")
        
        # 对每个币种采集数据
        for symbol in sorted(all_symbols):
            all_scores[symbol] = {}
            
            # 尝试从该币种的数据源获取数据
            for source_name in source_for_symbol[symbol]:
                for time_range in self.time_ranges:
                    # 如果已经有这个时间范围的数据，跳过
                    if time_range in all_scores[symbol]:
                        continue
                    
                    long_score, short_score = self.fetch_score(source_name, symbol, time_range)
                    
                    if long_score is not None and short_score is not None:
                        all_scores[symbol][time_range] = (long_score, short_score)
                        success_count += 1
                    else:
                        fail_count += 1
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ 采集完成: 成功={success_count}, 失败={fail_count}, 耗时={elapsed_time:.2f}秒")
        
        return all_scores
    
    def get_merged_symbols(self) -> List[str]:
        """获取合并后的所有币种列表（去重）"""
        all_symbols = set()
        for source_config in self.data_sources.values():
            all_symbols.update(source_config['symbols'])
        return sorted(list(all_symbols))


# 使用示例
if __name__ == '__main__':
    # 创建采集器
    collector = RealScoreCollector()
    
    # 获取所有币种
    symbols = collector.get_merged_symbols()
    print(f"\n📊 合并后的币种列表（共 {len(symbols)} 个）:")
    for i, symbol in enumerate(symbols, 1):
        print(f"  {i}. {symbol}")
    
    # 测试单个请求
    print("\n🔍 测试单个请求:")
    long_score, short_score = collector.fetch_score(
        'source_2_8_coins', 
        'BTC-USDT-SWAP', 
        '3m'
    )
    
    if long_score and short_score:
        print(f"✅ 测试成功: 做多={long_score:.2f}, 做空={short_score:.2f}")
    else:
        print("❌ 测试失败: 无法获取数据")
    
    # 采集所有数据（注意：这会发起大量请求）
    # print("\n🔄 开始采集所有数据...")
    # all_scores = collector.collect_all_scores()
    # 
    # print(f"\n📈 采集结果摘要:")
    # for symbol, scores in list(all_scores.items())[:3]:  # 只显示前3个
    #     print(f"\n  {symbol}:")
    #     for time_range, (long, short) in scores.items():
    #         diff = long - short
    #         trend = "📈" if diff > 0 else "📉"
    #         print(f"    {time_range}: 做多={long:.2f}, 做空={short:.2f}, 差值={diff:+.2f} {trend}")
