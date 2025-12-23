// 测试时间格式化
const snapshot_time = "2025-12-12 12:48:00";
const utcTime = new Date(snapshot_time.replace(' ', 'T') + 'Z');
console.log("UTC时间对象:", utcTime);

// 方法1: toLocaleString
const timeStr1 = utcTime.toLocaleString('zh-CN', { 
    timeZone: 'Asia/Shanghai',
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
});
console.log("toLocaleString完整:", timeStr1);
console.log("split后:", timeStr1.split(' '));

// 方法2: 手动计算
const beijingTime = new Date(utcTime.getTime() + 8 * 60 * 60 * 1000);
const hours = beijingTime.getUTCHours().toString().padStart(2, '0');
const minutes = beijingTime.getUTCMinutes().toString().padStart(2, '0');
const timeStr2 = `${hours}:${minutes}`;
console.log("手动计算:", timeStr2);

// 方法3: 使用getHours而不是getUTCHours
const hours3 = beijingTime.getHours().toString().padStart(2, '0');
const minutes3 = beijingTime.getMinutes().toString().padStart(2, '0');
const timeStr3 = `${hours3}:${minutes3}`;
console.log("使用getHours:", timeStr3);
