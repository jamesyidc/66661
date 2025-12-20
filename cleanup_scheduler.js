#!/usr/bin/env node
/**
 * 每日00:10清理未使用的父文件夹ID调度器
 * 使用Node.js实现定时任务
 */

const { spawn } = require('child_process');
const path = require('path');

// 脚本路径
const CLEANUP_SCRIPT = path.join(__dirname, 'cleanup_unused_folder_id.py');
const PYTHON_BIN = '/usr/bin/python3';

// 日志函数
function log(message) {
    const timestamp = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
    console.log(`[${timestamp}] ${message}`);
}

// 执行清理任务
function executeCleanup() {
    log('🧹 开始执行每日清理任务...');
    
    const cleanup = spawn(PYTHON_BIN, [CLEANUP_SCRIPT]);
    
    cleanup.stdout.on('data', (data) => {
        process.stdout.write(data);
    });
    
    cleanup.stderr.on('data', (data) => {
        process.stderr.write(data);
    });
    
    cleanup.on('close', (code) => {
        if (code === 0) {
            log('✅ 清理任务执行成功');
        } else {
            log(`❌ 清理任务执行失败，退出码: ${code}`);
        }
    });
}

// 执行父文件夹更新任务
function executeParentFolderUpdate() {
    log('📂 开始执行父文件夹ID更新任务...');
    
    const updateScript = path.join(__dirname, 'update_parent_folder_daily.py');
    const update = spawn(PYTHON_BIN, [updateScript]);
    
    update.stdout.on('data', (data) => {
        process.stdout.write(data);
    });
    
    update.stderr.on('data', (data) => {
        process.stderr.write(data);
    });
    
    update.on('close', (code) => {
        if (code === 0) {
            log('✅ 父文件夹ID更新任务执行成功');
        } else {
            log(`❌ 父文件夹ID更新任务执行失败，退出码: ${code}`);
        }
    });
}

// 检查是否到了00:10
function checkAndExecute() {
    const now = new Date();
    const beijingTime = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Shanghai' }));
    
    const hours = beijingTime.getHours();
    const minutes = beijingTime.getMinutes();
    
    // 每天00:10执行（允许00:10-00:11之间执行）
    if (hours === 0 && minutes === 10) {
        const key = beijingTime.toDateString();
        
        // 使用全局变量防止重复执行
        if (global.lastExecutionDate !== key) {
            global.lastExecutionDate = key;
            
            log('');
            log('='*60);
            log('⏰ 触发每日00:10定时任务');
            log('='*60);
            
            // 1. 先更新父文件夹ID
            executeParentFolderUpdate();
            
            // 2. 等待3秒后执行清理任务
            setTimeout(() => {
                executeCleanup();
            }, 3000);
        }
    }
}

// 启动调度器
log('🚀 启动每日清理调度器');
log('⏰ 执行时间: 每天 00:10 (北京时间)');
log('📂 清理脚本: ' + CLEANUP_SCRIPT);
log('');

// 每60秒检查一次时间
setInterval(checkAndExecute, 60 * 1000);

// 立即检查一次
checkAndExecute();

// 保持进程运行
process.on('SIGINT', () => {
    log('📛 收到停止信号，正在退出...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    log('📛 收到终止信号，正在退出...');
    process.exit(0);
});

log('✅ 调度器已启动，按 Ctrl+C 停止');
