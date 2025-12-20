#!/usr/bin/env python3
"""
支撑压力线系统数据备份工具
用途: 导出历史曲线图数据，方便数据恢复和快速部署
"""

import os
import sys
import sqlite3
import json
import gzip
from datetime import datetime, timedelta
import pytz

DB_PATH = os.path.join(os.path.dirname(__file__), 'crypto_data.db')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')

def ensure_backup_dir():
    """确保备份目录存在"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"✅ 创建备份目录: {BACKUP_DIR}")

def backup_snapshots(days=30, compress=True):
    """
    备份支撑压力线快照数据
    
    Args:
        days: 备份最近N天的数据 (默认30天)
        compress: 是否压缩 (默认True)
    
    Returns:
        备份文件路径
    """
    try:
        ensure_backup_dir()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 计算起始日期
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now_beijing = datetime.now(beijing_tz)
        start_date = (now_beijing - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"📊 开始备份数据...")
        print(f"  起始日期: {start_date}")
        print(f"  结束日期: {now_beijing.strftime('%Y-%m-%d')}")
        
        # 查询数据
        cursor.execute("""
            SELECT 
                id, snapshot_time, snapshot_date,
                scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                total_coins, created_at
            FROM support_resistance_snapshots
            WHERE snapshot_date >= ?
            ORDER BY snapshot_time ASC
        """, (start_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print(f"⚠️  没有找到数据")
            return None
        
        print(f"  找到 {len(rows)} 条记录")
        
        # 构建备份数据
        backup_data = {
            'version': '1.0',
            'backup_time': now_beijing.strftime('%Y-%m-%d %H:%M:%S'),
            'data_range': {
                'start': start_date,
                'end': now_beijing.strftime('%Y-%m-%d'),
                'days': days
            },
            'record_count': len(rows),
            'snapshots': []
        }
        
        for row in rows:
            snapshot = {
                'id': row[0],
                'snapshot_time': row[1],
                'snapshot_date': row[2],
                'scenario_1_count': row[3],
                'scenario_2_count': row[4],
                'scenario_3_count': row[5],
                'scenario_4_count': row[6],
                'scenario_1_coins': row[7],
                'scenario_2_coins': row[8],
                'scenario_3_coins': row[9],
                'scenario_4_coins': row[10],
                'total_coins': row[11],
                'created_at': row[12]
            }
            backup_data['snapshots'].append(snapshot)
        
        # 生成文件名
        timestamp = now_beijing.strftime('%Y%m%d_%H%M%S')
        filename = f"support_resistance_backup_{days}days_{timestamp}.json"
        
        if compress:
            filename += '.gz'
            filepath = os.path.join(BACKUP_DIR, filename)
            
            # 压缩保存
            json_str = json.dumps(backup_data, ensure_ascii=False, indent=2)
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(json_str)
            
            file_size = os.path.getsize(filepath)
            print(f"✅ 备份完成 (压缩)")
        else:
            filepath = os.path.join(BACKUP_DIR, filename)
            
            # 直接保存JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(filepath)
            print(f"✅ 备份完成")
        
        print(f"  文件路径: {filepath}")
        print(f"  文件大小: {file_size / 1024:.2f} KB")
        
        return filepath
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def restore_snapshots(backup_file, clear_existing=False):
    """
    从备份文件恢复数据
    
    Args:
        backup_file: 备份文件路径
        clear_existing: 是否清空现有数据 (默认False，追加模式)
    
    Returns:
        成功恢复的记录数
    """
    try:
        print(f"📥 开始恢复数据...")
        print(f"  备份文件: {backup_file}")
        
        # 读取备份文件
        if backup_file.endswith('.gz'):
            print(f"  解压缩中...")
            with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
        else:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
        
        print(f"  备份版本: {backup_data['version']}")
        print(f"  备份时间: {backup_data['backup_time']}")
        print(f"  记录数: {backup_data['record_count']}")
        print(f"  数据范围: {backup_data['data_range']['start']} ~ {backup_data['data_range']['end']}")
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 如果需要清空现有数据
        if clear_existing:
            print(f"⚠️  清空现有数据...")
            cursor.execute("DELETE FROM support_resistance_snapshots")
            conn.commit()
        
        # 插入数据
        print(f"📝 插入数据...")
        inserted_count = 0
        skipped_count = 0
        
        for snapshot in backup_data['snapshots']:
            try:
                # 检查是否已存在 (根据snapshot_time判断)
                cursor.execute("""
                    SELECT COUNT(*) FROM support_resistance_snapshots
                    WHERE snapshot_time = ?
                """, (snapshot['snapshot_time'],))
                
                exists = cursor.fetchone()[0] > 0
                
                if not exists:
                    cursor.execute("""
                        INSERT INTO support_resistance_snapshots (
                            snapshot_time, snapshot_date,
                            scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                            scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                            total_coins, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        snapshot['snapshot_time'],
                        snapshot['snapshot_date'],
                        snapshot['scenario_1_count'],
                        snapshot['scenario_2_count'],
                        snapshot['scenario_3_count'],
                        snapshot['scenario_4_count'],
                        snapshot['scenario_1_coins'],
                        snapshot['scenario_2_coins'],
                        snapshot['scenario_3_coins'],
                        snapshot['scenario_4_coins'],
                        snapshot['total_coins'],
                        snapshot['created_at']
                    ))
                    inserted_count += 1
                else:
                    skipped_count += 1
                
            except Exception as e:
                print(f"  ⚠️  插入记录失败: {snapshot['snapshot_time']} - {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ 恢复完成")
        print(f"  成功插入: {inserted_count} 条")
        print(f"  跳过重复: {skipped_count} 条")
        
        return inserted_count
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

def list_backups():
    """列出所有备份文件"""
    try:
        if not os.path.exists(BACKUP_DIR):
            print("📁 备份目录不存在")
            return []
        
        files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('support_resistance_backup_')]
        
        if not files:
            print("📁 没有找到备份文件")
            return []
        
        print(f"📋 备份文件列表:")
        print(f"{'序号':4s} | {'文件名':50s} | {'大小':10s} | {'修改时间':20s}")
        print("-" * 90)
        
        files.sort(reverse=True)  # 最新的在前
        
        for idx, filename in enumerate(files, 1):
            filepath = os.path.join(BACKUP_DIR, filename)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            print(f"{idx:4d} | {filename:50s} | {size/1024:8.2f}KB | {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return files
        
    except Exception as e:
        print(f"❌ 列出备份文件失败: {e}")
        return []

def export_csv(days=7, output_file=None):
    """
    导出数据为CSV格式 (用于Excel分析)
    
    Args:
        days: 导出最近N天的数据
        output_file: 输出文件路径
    
    Returns:
        CSV文件路径
    """
    try:
        import csv
        
        ensure_backup_dir()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 计算起始日期
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now_beijing = datetime.now(beijing_tz)
        start_date = (now_beijing - timedelta(days=days)).strftime('%Y-%m-%d')
        
        print(f"📊 导出CSV数据...")
        print(f"  起始日期: {start_date}")
        
        # 查询数据
        cursor.execute("""
            SELECT 
                snapshot_time, snapshot_date,
                scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                total_coins
            FROM support_resistance_snapshots
            WHERE snapshot_date >= ?
            ORDER BY snapshot_time ASC
        """, (start_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print(f"⚠️  没有找到数据")
            return None
        
        # 生成文件名
        if output_file is None:
            timestamp = now_beijing.strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(BACKUP_DIR, f"support_resistance_export_{days}days_{timestamp}.csv")
        
        # 写入CSV
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                '快照时间',
                '日期',
                '情况1(接近支撑2)',
                '情况2(接近支撑1)',
                '情况3(接近压力2)',
                '情况4(接近压力1)',
                '总币种数'
            ])
            
            # 写入数据
            for row in rows:
                writer.writerow(row)
        
        print(f"✅ CSV导出完成")
        print(f"  文件路径: {output_file}")
        print(f"  记录数: {len(rows)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ CSV导出失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='支撑压力线系统数据备份工具')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'export-csv'], 
                        help='操作: backup(备份), restore(恢复), list(列表), export-csv(导出CSV)')
    parser.add_argument('--days', type=int, default=30, help='备份/导出天数 (默认30天)')
    parser.add_argument('--file', type=str, help='恢复时指定备份文件')
    parser.add_argument('--no-compress', action='store_true', help='不压缩备份文件')
    parser.add_argument('--clear', action='store_true', help='恢复时清空现有数据')
    
    args = parser.parse_args()
    
    print("="*80)
    print("🗄️  支撑压力线系统数据备份工具")
    print("="*80)
    
    if args.action == 'backup':
        print(f"\n📦 执行备份 (最近 {args.days} 天)")
        backup_file = backup_snapshots(days=args.days, compress=not args.no_compress)
        if backup_file:
            print(f"\n✅ 备份成功: {backup_file}")
    
    elif args.action == 'restore':
        if not args.file:
            print("\n❌ 请使用 --file 参数指定备份文件")
            sys.exit(1)
        
        if not os.path.exists(args.file):
            print(f"\n❌ 备份文件不存在: {args.file}")
            sys.exit(1)
        
        print(f"\n📥 执行恢复")
        if args.clear:
            print("⚠️  警告: 将清空现有数据!")
            confirm = input("是否继续? (yes/no): ")
            if confirm.lower() != 'yes':
                print("已取消")
                sys.exit(0)
        
        count = restore_snapshots(args.file, clear_existing=args.clear)
        if count > 0:
            print(f"\n✅ 恢复成功: {count} 条记录")
    
    elif args.action == 'list':
        print(f"\n📋 列出备份文件")
        list_backups()
    
    elif args.action == 'export-csv':
        print(f"\n📊 导出CSV (最近 {args.days} 天)")
        csv_file = export_csv(days=args.days)
        if csv_file:
            print(f"\n✅ CSV导出成功: {csv_file}")
    
    print("\n" + "="*80)
