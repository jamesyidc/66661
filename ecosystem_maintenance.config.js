module.exports = {
  apps: [
    // 磁盘监控 - 每小时执行一次
    {
      name: 'disk-monitor',
      script: 'disk_monitor.py',
      interpreter: 'python3',
      cron_restart: '0 * * * *',  // 每小时整点执行
      autorestart: false,
      watch: false,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'logs/disk-monitor-error.log',
      out_file: 'logs/disk-monitor-out.log',
      merge_logs: true
    },
    
    // 数据库维护 - 每6小时执行一次
    {
      name: 'db-maintenance',
      script: 'db_maintenance.py',
      interpreter: 'python3',
      cron_restart: '0 */6 * * *',  // 每6小时执行 (0:00, 6:00, 12:00, 18:00)
      autorestart: false,
      watch: false,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'logs/db-maintenance-error.log',
      out_file: 'logs/db-maintenance-out.log',
      merge_logs: true
    },
    
    // 日志清理 - 每天凌晨2点执行
    {
      name: 'log-cleanup',
      script: 'cleanup_logs.sh',
      interpreter: 'bash',
      cron_restart: '0 2 * * *',  // 每天凌晨2点
      autorestart: false,
      watch: false,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'logs/log-cleanup-error.log',
      out_file: 'logs/log-cleanup-out.log',
      merge_logs: true
    }
  ]
};
