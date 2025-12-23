const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // 监听所有控制台消息
    const consoleMessages = [];
    page.on('console', msg => {
        const text = msg.text();
        consoleMessages.push(text);
        console.log('浏览器控制台:', text);
    });
    
    try {
        console.log('正在访问页面...');
        await page.goto('http://localhost:5000/symbol/UNI/v6', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        
        console.log('\n等待图表渲染...');
        await page.waitForTimeout(3000);
        
        // 提取关键的过滤日志
        console.log('\n========== RSI过滤日志 ==========');
        const rsiLogs = consoleMessages.filter(msg => msg.includes('[RSI检查]') || msg.includes('[卖点1过滤]'));
        rsiLogs.forEach(log => console.log(log));
        
        console.log('\n========== 标记结果 ==========');
        const markerLogs = consoleMessages.filter(msg => msg.includes('[做多卖点1检测]') || msg.includes('[卖点1标记]'));
        markerLogs.forEach(log => console.log(log));
        
        // 统计总共有多少个卖点1被标记
        const sellPointMarkers = consoleMessages.filter(msg => msg.includes('[卖点1标记]'));
        console.log(`\n总共标记了 ${sellPointMarkers.length} 个卖点1`);
        
        // 检查是否有RSI<50但仍然被标记的情况
        console.log('\n========== 异常检测 ==========');
        let foundIssue = false;
        for (const log of sellPointMarkers) {
            const match = log.match(/最高点idx=(\d+), RSI=([\d.]+), 标记点idx=(\d+), RSI=([\d.]+)/);
            if (match) {
                const highPointRsi = parseFloat(match[2]);
                if (highPointRsi < 50) {
                    console.log(`❌ 发现异常: 最高点RSI=${highPointRsi} < 50，但仍被标记！`);
                    console.log(`   完整日志: ${log}`);
                    foundIssue = true;
                }
            }
        }
        
        if (!foundIssue) {
            console.log('✅ 未发现RSI<50的异常标记');
        }
        
    } catch (error) {
        console.error('诊断过程出错:', error);
    } finally {
        await browser.close();
    }
})();
