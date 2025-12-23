// capture_console.js - 捕获页面控制台日志
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    const logs = [];
    
    // 捕获所有控制台消息
    page.on('console', msg => {
        const text = msg.text();
        logs.push(text);
        console.log(`[CONSOLE] ${text}`);
    });
    
    try {
        await page.goto('http://localhost:5000/symbol/UNI/v6', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        
        // 等待一会儿让JavaScript执行
        await page.waitForTimeout(3000);
        
        console.log('\n========== 汇总 ==========');
        console.log(`总共捕获 ${logs.length} 条日志`);
        
        // 过滤RSI相关日志
        const rsiLogs = logs.filter(log => log.includes('RSI检查') || log.includes('卖点1过滤') || log.includes('卖点1标记'));
        console.log(`\nRSI相关日志 (${rsiLogs.length} 条):`);
        rsiLogs.forEach(log => console.log(log));
        
    } catch (error) {
        console.error('错误:', error.message);
    } finally {
        await browser.close();
    }
})();
