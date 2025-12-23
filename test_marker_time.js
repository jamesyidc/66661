// 模拟前端时间转换代码
const snapshot_time_1 = "2025-12-12 12:06:00";
const snapshot_time_2 = "2025-12-12 12:48:00";

function convertToBeijingTime(snapshotTime) {
    const utcTime = new Date(snapshotTime.replace(' ', 'T') + 'Z');
    const beijingTime = new Date(utcTime.getTime() + 8 * 60 * 60 * 1000);
    const hours = beijingTime.getUTCHours().toString().padStart(2, '0');
    const minutes = beijingTime.getUTCMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

console.log("快照1:", snapshot_time_1, "UTC -> 北京时间:", convertToBeijingTime(snapshot_time_1));
console.log("快照2:", snapshot_time_2, "UTC -> 北京时间:", convertToBeijingTime(snapshot_time_2));
