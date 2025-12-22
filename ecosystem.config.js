module.exports = {
  apps : [{
    script: 'index.js',
    watch: '.'
  }, {
    script: './service-worker/',
    watch: ['./service-worker']
  }],

  deploy : {
    production : {
      user : 'SSH_USERNAME',
      host : 'SSH_HOSTMACHINE',
      ref  : 'origin/master',
      repo : 'GIT_REPOSITORY',
      path : 'DESTINATION_PATH',
      'pre-deploy-local': '',
      'post-deploy' : 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': ''
    }
  }
};

    // 自动更新文件夹配置 - 每小时执行
    {
      name: 'auto-folder-update',
      script: 'auto_update_folder_config.py',
      interpreter: 'python3',
      cron_restart: '*/10 * * * *',  // 每10分钟执行一次(增加频率)
      autorestart: false,
      watch: false,
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: 'logs/auto-folder-update-error.log',
      out_file: 'logs/auto-folder-update-out.log',
      merge_logs: true
    }
  ]
};
