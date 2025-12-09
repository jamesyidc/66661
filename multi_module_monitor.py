#!/usr/bin/env python3
"""
多模块监控系统
监控所有数据采集模块的更新状态，自动触发强制更新
"""

import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
import pytz
import json

BEIJING_TZ = pytz.timezone('Asia/Shanghai')
DB_PATH = 'crypto_data.db'

# 模块配置
MODULES_CONFIG = {
    'crypto_snapshots': {
        'name': '历史数据查询',
        'page_url': '/query',
        'table': 'crypto_coin_data',
        'time_column': 'snapshot_time',
        'expected_interval': 10,  # 预期更新间隔（分钟）
        'max_delay': 12,  # 最大允许延迟（分钟）
        'trigger_script': 'collect_and_store.py',
        'icon': '📊',
        'description': '间隔10分钟，超过12分钟干预'
    },
    'trading_signals': {
        'name': '交易信号监控',
        'page_url': '/signals',
        'table': 'trading_signals',
        'time_column': 'created_at',
        'expected_interval': 3,  # 预期更新间隔（分钟）
        'max_delay': 5,  # 最大允许延迟（分钟）
        'trigger_script': 'signal_control.sh',
        'trigger_args': ['restart'],
        'icon': '📈',
        'description': '间隔3分钟，超过5分钟干预'
    },
    'panic_wash_index': {
        'name': '恐慌清洗指数',
        'page_url': '/panic',
        'table': 'panic_wash_index',
        'time_column': 'created_at',
        'expected_interval': 3,  # 预期更新间隔（分钟）
        'max_delay': 5,  # 最大允许延迟（分钟）
        'trigger_script': 'panic_wash_control.sh',
        'trigger_args': ['restart'],
        'icon': '⚠️',
        'description': '间隔3分钟，超过5分钟干预'
    },
    'price_comparison': {
        'name': '比价系统',
        'page_url': '/price-comparison',
        'table': 'price_comparison',
        'time_column': 'last_update_time',
        'expected_interval': 10,  # 预期更新间隔（分钟）
        'max_delay': 12,  # 最大允许延迟（分钟）
        'trigger_script': None,  # 依赖crypto_snapshots更新
        'depends_on': 'crypto_snapshots',  # 依赖crypto_snapshots
        'icon': '💱',
        'description': '间隔10分钟，超过12分钟干预（依赖历史数据查询）'
    },
    'star_system': {
        'name': '星星系统',
        'page_url': '/star-system',
        'table': 'crypto_coin_data',  # 使用crypto_coin_data作为数据源
        'time_column': 'snapshot_time',
        'expected_interval': 10,  # 预期更新间隔（分钟）与crypto_snapshots一致
        'max_delay': 12,  # 最大允许延迟（分钟）与crypto_snapshots一致
        'trigger_script': None,  # 实时计算，无需采集脚本
        'depends_on': 'crypto_snapshots',  # 依赖crypto_snapshots
        'icon': '⭐',
        'description': '实时计算，依赖历史数据查询（间隔10分钟）'
    }
}

def get_module_latest_time(module_config):
    """获取模块最新数据时间"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = f"""
            SELECT {module_config['time_column']}
            FROM {module_config['table']}
            ORDER BY {module_config['time_column']} DESC
            LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            time_str = result[0]
            # 处理不同的时间格式
            if 'T' in time_str:
                # ISO格式
                latest_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                latest_time = latest_time.astimezone(BEIJING_TZ).replace(tzinfo=None)
            else:
                # 标准格式
                latest_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            return latest_time
        return None
    except Exception as e:
        print(f"❌ 获取{module_config['name']}最新时间失败: {e}")
        return None

def get_module_record_count(module_config):
    """获取模块记录总数"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = f"SELECT COUNT(*) FROM {module_config['table']}"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def check_module_status(module_key, module_config):
    """检查单个模块的状态"""
    now = datetime.now(BEIJING_TZ).replace(tzinfo=None)
    latest_time = get_module_latest_time(module_config)
    record_count = get_module_record_count(module_config)
    
    if latest_time is None:
        return {
            'module_key': module_key,
            'module_name': module_config['name'],
            'icon': module_config['icon'],
            'need_update': True,
            'status': 'no_data',
            'reason': '数据库中没有数据',
            'latest_time': None,
            'minutes_since_last': None,
            'expected_interval': module_config['expected_interval'],
            'record_count': record_count
        }
    
    time_diff = (now - latest_time).total_seconds() / 60
    expected_interval = module_config['expected_interval']
    max_delay = module_config['max_delay']
    
    need_update = time_diff >= max_delay
    
    # 判断状态
    if need_update:
        status = 'outdated'
        reason = f'距离上次更新已经 {time_diff:.1f} 分钟，超过了最大允许延迟 {max_delay} 分钟'
    else:
        status = 'normal'
        reason = '更新正常'
    
    result = {
        'module_key': module_key,
        'module_name': module_config['name'],
        'icon': module_config['icon'],
        'page_url': module_config.get('page_url', ''),
        'description': module_config.get('description', ''),
        'need_update': need_update,
        'status': status,
        'reason': reason,
        'latest_time': latest_time.strftime('%Y-%m-%d %H:%M:%S'),
        'minutes_since_last': round(time_diff, 1),
        'expected_interval': expected_interval,
        'max_delay': max_delay,
        'overdue_minutes': round(time_diff - max_delay, 1) if need_update else 0,
        'record_count': record_count,
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 如果模块依赖其他模块，添加依赖信息
    if 'depends_on' in module_config:
        result['depends_on'] = module_config['depends_on']
        result['trigger_script'] = None  # 依赖模块不直接触发
    
    return result

def trigger_module_update(module_key, module_config):
    """触发模块更新"""
    print(f"\n{'='*80}")
    print(f"🚀 触发{module_config['name']}更新...")
    print(f"{'='*80}")
    
    # 检查是否有依赖模块
    if 'depends_on' in module_config:
        depends_on = module_config['depends_on']
        print(f"ℹ️  {module_config['name']}依赖于{MODULES_CONFIG[depends_on]['name']}")
        print(f"   将触发依赖模块的更新...")
        
        # 触发被依赖模块的更新
        dependency_config = MODULES_CONFIG[depends_on]
        if dependency_config.get('trigger_script'):
            return trigger_module_update(depends_on, dependency_config)
        else:
            return {
                'success': False,
                'message': f'{module_config["name"]}依赖于{dependency_config["name"]}，但依赖模块无更新脚本',
                'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
            }
    
    # 检查是否有触发脚本
    script = module_config.get('trigger_script')
    if not script:
        return {
            'success': False,
            'message': f'{module_config["name"]}没有配置更新脚本（可能需要手动更新或依赖其他模块）',
            'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    try:
        args = module_config.get('trigger_args', [])
        
        # 构建命令
        if script.endswith('.sh'):
            cmd = ['bash', script] + args
        else:
            cmd = ['python3', script] + args
        
        result = subprocess.run(
            cmd,
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"\n✅ {module_config['name']}更新成功!")
            if result.stdout:
                print(result.stdout)
            return {
                'success': True,
                'message': f'{module_config["name"]}更新成功',
                'output': result.stdout,
                'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            print(f"\n❌ {module_config['name']}更新失败! (退出码: {result.returncode})")
            if result.stderr:
                print("错误信息:", result.stderr)
            return {
                'success': False,
                'message': f'{module_config["name"]}更新失败 (退出码: {result.returncode})',
                'error': result.stderr,
                'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
            }
    except subprocess.TimeoutExpired:
        print(f"\n⏱️  {module_config['name']}更新超时（超过5分钟）")
        return {
            'success': False,
            'message': f'{module_config["name"]}更新超时',
            'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"\n❌ 触发{module_config['name']}更新时发生错误: {e}")
        return {
            'success': False,
            'message': f'触发{module_config["name"]}更新失败: {str(e)}',
            'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        }

def check_all_modules(silent=False):
    """检查所有模块状态"""
    if not silent:
        print("\n" + "="*80)
        print("🔍 检查所有模块状态...")
        print("="*80)
    
    results = {}
    
    for module_key, module_config in MODULES_CONFIG.items():
        status = check_module_status(module_key, module_config)
        results[module_key] = status
        
        if not silent:
            icon = module_config['icon']
            name = module_config['name']
            status_icon = '✅' if not status['need_update'] else '⚠️'
            
            print(f"\n{icon} {name}:")
            print(f"   状态: {status_icon} {status['reason']}")
            if status['latest_time']:
                print(f"   最新数据: {status['latest_time']}")
                print(f"   距今: {status['minutes_since_last']} 分钟")
            print(f"   记录数: {status['record_count']}")
    
    return results

def check_and_recover_all(silent=False):
    """检查所有模块并自动恢复"""
    statuses = check_all_modules(silent=silent)
    
    updates_triggered = []
    
    for module_key, status in statuses.items():
        if status['need_update']:
            module_config = MODULES_CONFIG[module_key]
            
            if not silent:
                print(f"\n⚠️  检测到{module_config['name']}需要更新!")
                if status.get('overdue_minutes'):
                    print(f"   超期时间: {status['overdue_minutes']} 分钟")
            
            # 触发更新
            update_result = trigger_module_update(module_key, module_config)
            updates_triggered.append({
                'module_key': module_key,
                'module_name': module_config['name'],
                'status': status,
                'update_result': update_result
            })
    
    return {
        'all_statuses': statuses,
        'updates_triggered': updates_triggered,
        'total_modules': len(statuses),
        'outdated_modules': sum(1 for s in statuses.values() if s['need_update']),
        'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
    }

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'status':
            # 只检查状态，不触发更新
            statuses = check_all_modules(silent=False)
            print("\n" + json.dumps(statuses, indent=2, ensure_ascii=False))
            
            # 如果有模块需要更新，返回非0退出码
            need_update = any(s['need_update'] for s in statuses.values())
            sys.exit(1 if need_update else 0)
        
        elif command == 'check':
            # 检查并自动恢复所有模块
            silent = '--silent' in sys.argv
            result = check_and_recover_all(silent=silent)
            
            if not silent:
                print("\n" + json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(result, ensure_ascii=False))
            
            sys.exit(0)
        
        elif command == 'force':
            # 强制更新指定模块
            if len(sys.argv) > 2:
                module_key = sys.argv[2]
                if module_key in MODULES_CONFIG:
                    result = trigger_module_update(module_key, MODULES_CONFIG[module_key])
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    sys.exit(0 if result['success'] else 1)
                else:
                    print(f"❌ 未知模块: {module_key}")
                    print(f"可用模块: {', '.join(MODULES_CONFIG.keys())}")
                    sys.exit(1)
            else:
                print("用法: python3 multi_module_monitor.py force <module_key>")
                print(f"可用模块: {', '.join(MODULES_CONFIG.keys())}")
                sys.exit(1)
        
        else:
            print(f"未知命令: {command}")
            print("\n用法:")
            print("  python3 multi_module_monitor.py status   - 查看所有模块状态")
            print("  python3 multi_module_monitor.py check    - 检查并自动恢复所有模块")
            print("  python3 multi_module_monitor.py force <module_key> - 强制更新指定模块")
            sys.exit(1)
    else:
        # 默认：检查并自动恢复
        result = check_and_recover_all(silent=False)
        sys.exit(0)

if __name__ == '__main__':
    main()
