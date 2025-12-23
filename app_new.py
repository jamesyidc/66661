#!/usr/bin/env python3
"""
加密货币数据分析系统 - 完全仿照参考页面风格
"""
from flask import Flask, render_template_string, render_template, request, jsonify, send_from_directory, make_response
import sqlite3
from datetime import datetime, timedelta
import json
import pytz
import os

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# K线图服务URL配置
CHART_BASE_URL = "https://5000-iz6uddj6rs3xe48ilsyqq-2e1b9533.sandbox.novita.ai"

# 主页面HTML - 完全仿照参考设计
MAIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密货币数据历史回看</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: #1e2139;
            color: #fff;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 0;
        }
        
        /* 顶部导航栏 */
        .top-nav {
            background: #2a2d47;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            justify-content: space-between;
        }
        
        .nav-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .nav-right {
            display: flex;
            gap: 10px;
        }
        
        /* 系统导航栏 */
        .systems-nav {
            background: linear-gradient(135deg, #2a2d47 0%, #3a3d5c 100%);
            padding: 15px 20px;
            border-bottom: 2px solid #3b7dff;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .systems-nav-title {
            font-size: 14px;
            font-weight: 600;
            color: #8b92b8;
            margin-right: 10px;
        }
        
        .system-link {
            background: rgba(59, 125, 255, 0.1);
            border: 1px solid rgba(59, 125, 255, 0.3);
            color: #00d4ff;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .system-link:hover {
            background: rgba(59, 125, 255, 0.2);
            border-color: #3b7dff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 125, 255, 0.3);
        }
        
        .system-link.featured {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: #fff;
        }
        
        .system-link.featured:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        .home-btn {
            background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
            color: #fff;
            border: none;
            padding: 8px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .home-btn:hover {
            background: linear-gradient(135deg, #0099ff 0%, #00d4ff 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
        }
        
        .nav-brand {
            display: flex;
            align-items: center;
            gap: 8px;
            background: #3b7dff;
            padding: 6px 15px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .nav-title {
            font-size: 18px;
            font-weight: 500;
            color: #fff;
            margin-left: 10px;
        }
        
        /* 控制栏 */
        .control-bar {
            background: #2a2d47;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
            border-bottom: 1px solid #3a3d5c;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-label {
            color: #8b92b8;
            font-size: 13px;
        }
        
        .control-input {
            background: #1e2139;
            border: 1px solid #3a3d5c;
            color: #fff;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 13px;
            outline: none;
        }
        
        .control-input:focus {
            border-color: #3b7dff;
        }
        
        .control-btn {
            background: #3b7dff;
            border: none;
            color: white;
            padding: 7px 18px;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .control-btn:hover {
            background: #2563eb;
        }
        
        .control-btn.secondary {
            background: #4a5178;
        }
        
        .control-btn.secondary:hover {
            background: #5a6188;
        }
        
        /* 数据统计栏 */
        .stats-bar {
            background: #2a2d47;
            padding: 12px 20px;
            display: flex;
            gap: 25px;
            flex-wrap: wrap;
            border-bottom: 1px solid #3a3d5c;
            font-size: 13px;
        }
        
        .stat-item {
            display: flex;
            gap: 5px;
        }
        
        .stat-label {
            color: #8b92b8;
        }
        
        .stat-value {
            color: #fff;
            font-weight: 500;
            margin-left: 8px;
        }
        
        .stat-value.rise {
            color: #10b981;
        }
        
        .stat-value.fall {
            color: #ef4444;
        }
        
        /* 次级统计栏 */
        .secondary-stats {
            background: #1e2139;
            padding: 10px 20px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 13px;
        }
        
        /* 时间轴容器 - 竖直布局 */
        .timeline-container {
            background: #2a2d47;
            padding: 15px 20px;
            border-top: 1px solid #3a3d5c;
            max-height: 500px;  /* 增加高度以显示更多信息 */
            overflow-y: auto;
        }
        
        .timeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            position: sticky;
            top: 0;
            background: #2a2d47;
            padding-bottom: 10px;
            border-bottom: 1px solid #3a3d5c;
        }
        
        .timeline-title {
            color: #8b92b8;
            font-size: 13px;
            font-weight: 500;
        }
        
        .timeline-info {
            color: #3b7dff;
            font-size: 12px;
        }
        
        /* 竖直时间轴轨道 */
        .timeline-track {
            position: relative;
            padding-left: 30px;
            margin-top: 10px;
        }
        
        /* 竖直线 */
        .timeline-line {
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #3a3d5c;
        }
        
        /* 竖直排列的时间点容器 */
        .timeline-points {
            display: flex;
            flex-direction: column;
            gap: 20px;  /* 增加间距以容纳更多信息 */
        }
        
        /* 时间点项 */
        .timeline-point {
            position: relative;
            display: flex;
            align-items: flex-start;  /* 改为顶部对齐，适应多行内容 */
            cursor: pointer;
            padding: 10px 12px;  /* 增加padding */
            border-radius: 4px;
            transition: all 0.3s;
            min-height: 80px;  /* 最小高度确保显示多行信息 */
        }
        
        .timeline-point:hover {
            background: rgba(59, 125, 255, 0.1);
        }
        
        /* 时间点圆圈 */
        .timeline-point::before {
            content: '';
            position: absolute;
            left: -22px;
            width: 12px;
            height: 12px;
            background: #3b7dff;
            border: 2px solid #2a2d47;
            border-radius: 50%;
            transition: all 0.3s;
            z-index: 2;
        }
        
        .timeline-point:hover::before {
            width: 16px;
            height: 16px;
            left: -24px;
            background: #2563eb;
            box-shadow: 0 0 10px rgba(59, 125, 255, 0.5);
        }
        
        .timeline-point.active::before {
            background: #10b981;
            width: 16px;
            height: 16px;
            left: -24px;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
        }
        
        /* 时间标签 */
        .timeline-label {
            color: #8b92b8;
            font-size: 12px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .timeline-point:hover .timeline-label {
            color: #fff;
        }
        
        .timeline-point.active .timeline-label {
            color: #10b981;
            font-weight: 500;
        }
        
        .timeline-label-time {
            font-size: 13px;
            font-weight: 500;
        }
        
        .timeline-label-stats {
            font-size: 11px;
            opacity: 0.85;
            line-height: 1.5;
            color: #a0aec0;
            max-width: 600px;  /* 限制最大宽度 */
        }
        
        .timeline-label-stats div {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* 图表区域 */
        .chart-section {
            background: #2a2d47;
            margin: 0;
            padding: 20px;
        }
        
        .chart-title {
            color: #8b92b8;
            font-size: 14px;
            margin-bottom: 15px;
            text-align: center;
        }
        
        #mainChart {
            width: 100%;
            height: 450px;  /* 增加高度，让图表更清晰 */
        }
        
        /* 数据列表标题 */
        .data-list-header {
            background: #2a2d47;
            padding: 12px 20px;
            color: #3b7dff;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* 表格容器 */
        .table-container {
            background: #1e2139;
            overflow-x: auto;
        }
        
        /* 数据表格 */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }
        
        .data-table thead {
            background: #ef4444;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .data-table th {
            padding: 10px 8px;
            text-align: center;
            font-weight: 500;
            color: #fff;
            border-right: 1px solid #dc2626;
            white-space: nowrap;
        }
        
        .data-table tbody tr {
            border-bottom: 1px solid #2a2d47;
        }
        
        .data-table tbody tr:hover {
            background: #2a2d47;
        }
        
        .data-table td {
            padding: 8px 6px;
            text-align: center;
            border-right: 1px solid #2a2d47;
            white-space: nowrap;
        }
        
        /* 操作列 */
        .action-btn {
            background: #ef4444;
            border: none;
            color: white;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 11px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .action-btn:hover {
            background: #dc2626;
        }
        
        /* 币种名称 */
        .coin-symbol {
            font-weight: 600;
            color: #fff;
        }
        
        /* 数值颜色 */
        .value-positive {
            color: #ef4444;
        }
        
        .value-negative {
            color: #10b981;
        }
        
        .value-neutral {
            color: #8b92b8;
        }
        
        /* 状态标签 */
        .status-tag {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }
        
        .status-tag.rise {
            background: #dc2626;
            color: white;
        }
        
        .status-tag.fall {
            background: #10b981;
            color: white;
        }
        
        /* 优先级颜色 */
        .priority-1 { color: #ff0000; font-weight: bold; }
        .priority-2 { color: #ff6600; font-weight: bold; }
        .priority-3 { color: #ff9900; }
        .priority-4 { color: #ffcc00; }
        .priority-5 { color: #99cc00; }
        .priority-6 { color: #8b92b8; }
        
        /* 加载状态 */
        .loading {
            text-align: center;
            padding: 40px;
            color: #8b92b8;
            font-size: 14px;
        }
        
        /* 响应式 */
        @media (max-width: 768px) {
            .control-bar {
                flex-direction: column;
                align-items: stretch;
            }
            
            .stats-bar {
                flex-direction: column;
                gap: 10px;
            }
            
            .data-table {
                font-size: 11px;
            }
            
            .data-table th,
            .data-table td {
                padding: 6px 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 顶部导航 -->
        <div class="top-nav">
            <div class="nav-left">
                <div class="nav-brand">
                    <span>📊</span> 数据回看
                </div>
                <div class="nav-title">加密货币数据历史回看</div>
            </div>
            <div class="nav-right">
                <button class="home-btn" onclick="window.location.href='/'">
                    <span>🏠</span> 返回首页
                </button>
            </div>
        </div>
        
        <!-- 系统导航栏 -->
        <div class="systems-nav">
            <div class="systems-nav-title">快速访问:</div>
            <a href="/sar-slope" class="system-link featured">
                <span>📈</span> SAR斜率系统
            </a>
            <a href="/kline-indicators" class="system-link">
                <span>📊</span> K线指标系统
            </a>
            <a href="/support-resistance" class="system-link">
                <span>📉</span> 支撑阻力系统
            </a>
            <a href="/position-system" class="system-link">
                <span>💼</span> 仓位系统
            </a>
            <a href="/gdrive-monitor-status" class="system-link">
                <span>☁️</span> Google Drive监控
            </a>
            <a href="/crypto-index" class="system-link">
                <span>📈</span> 指数系统
            </a>
            <a href="/coin-pool" class="system-link">
                <span>🏊</span> 币池系统
            </a>
            <a href="/price-comparison" class="system-link">
                <span>💱</span> 比价系统
            </a>
            <a href="/fund-monitor" class="system-link featured">
                <span>💰</span> 资金监控系统
            </a>
        </div>
        
        <!-- 控制栏 -->
        <div class="control-bar">
            <div class="control-group">
                <span class="control-label">选项日期:</span>
                <input type="date" id="queryDate" class="control-input">
            </div>
            
            <div class="control-group">
                <span class="control-label">时间选择:</span>
                <input type="time" id="queryTime" class="control-input" value="00:00">
            </div>
            
            <div class="control-group">
                <span class="control-label">至</span>
                <input type="time" id="endTime" class="control-input" value="23:59">
            </div>
            
            <button class="control-btn" onclick="queryData()">🔍 查询</button>
            <button class="control-btn secondary" onclick="loadToday()">📊 今天</button>
            <button class="control-btn secondary" onclick="loadLatest()">📡 立即加载</button>
            <button class="control-btn secondary" onclick="batchImportData()" id="batchImportBtn">📥 批量导入今日数据</button>
        </div>
        
        <!-- 主要统计栏 -->
        <div class="stats-bar">
            <div class="stat-item">
                <span class="stat-label">运算时间:</span>
                <span class="stat-value" id="calcTime">2025-12-06 13:42:42</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">急涨:</span>
                <span class="stat-value rise" id="rushUp">1</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">急跌:</span>
                <span class="stat-value fall" id="rushDown">22</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">本轮急涨:</span>
                <span class="stat-value" id="roundRushUp">1</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">本轮急跌:</span>
                <span class="stat-value" id="roundRushDown">22</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">计次:</span>
                <span class="stat-value" id="countTimes">10</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">计次得分:</span>
                <span class="stat-value" id="countScore">☆☆☆</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">状态:</span>
                <span class="stat-value" id="status">震荡无序</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">比值:</span>
                <span class="stat-value" id="ratio">10</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">差值:</span>
                <span class="stat-value" id="diff">-21</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">比价最低:</span>
                <span class="stat-value" id="priceLowest">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">比价创新高:</span>
                <span class="stat-value" id="priceNewhigh">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">24h涨≥10%:</span>
                <span class="stat-value rise" id="rise24hCount">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">24h跌≤-10%:</span>
                <span class="stat-value fall" id="fall24hCount">0</span>
            </div>

        </div>
        
        <!-- 次级统计栏 -->
        <div class="secondary-stats">
            <div class="stat-item">
                <span class="stat-label">已回调历史: 无</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">回调天数: 168 秒/0次</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">时间偏限: 2025-12-04 10:22:00 ~ 2025-12-04 18:32:00</span>
            </div>
        </div>
        
        <!-- 图表区域 -->
        <div class="chart-section">
            <div class="chart-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div class="chart-title">急涨/急跌历史趋势图</div>
                <div class="chart-pagination" style="display: flex; gap: 10px; align-items: center;">
                    <span id="chartTimeRange" style="color: #8b92b8; font-size: 12px;"></span>
                    <button id="btnPrevPage" class="page-btn" style="padding: 5px 12px; background: #3a3d5c; color: #8b92b8; border: 1px solid #4a4d6c; border-radius: 4px; cursor: pointer;" disabled>
                        ◀ 上一页
                    </button>
                    <span id="chartPageInfo" style="color: #8b92b8; font-size: 12px;">第1页</span>
                    <button id="btnNextPage" class="page-btn" style="padding: 5px 12px; background: #3a3d5c; color: #8b92b8; border: 1px solid #4a4d6c; border-radius: 4px; cursor: pointer;" disabled>
                        下一页 ▶
                    </button>
                </div>
            </div>
            <div id="mainChart"></div>
        </div>
        
        <!-- 时间轴 - 放在图表下方 -->
        <div class="timeline-container">
            <div class="timeline-header">
                <span class="timeline-title">历史数据时间轴</span>
                <span class="timeline-info" id="timelineInfo">加载中...</span>
            </div>
            <div class="timeline-track">
                <div class="timeline-line"></div>
                <div id="timelinePoints" class="timeline-points"></div>
            </div>
        </div>
        
        <!-- 数据列表标题 -->
        <div class="data-list-header">
            <span>📋</span> 币列表
        </div>
        
        <!-- 数据表格 -->
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>优先级</th>
                        <th>序号</th>
                        <th>币名</th>
                        <th>涨跌</th>
                        <th>急涨</th>
                        <th>急跌</th>
                        <th>更新时间</th>
                        <th>历史高点</th>
                        <th>高点时间</th>
                        <th>跌幅</th>
                        <th>24h%</th>
                        <th>排行</th>
                        <th>当前价格</th>
                        <th>最高占比</th>
                        <th>最低占比</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody">
                    <tr>
                        <td colspan="15" class="loading">正在加载数据...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // 初始化图表
        const chart = echarts.init(document.getElementById('mainChart'));
        
        // 初始化日期
        const today = new Date();
        document.getElementById('queryDate').valueAsDate = today;
        
        // 图表配置
        function updateChart(data) {
            const option = {
                backgroundColor: 'transparent',
                grid: {
                    left: '50px',
                    right: '50px',
                    bottom: '120px',  // 增加底部空间给旋转的横轴标签
                    top: '50px',
                    containLabel: true
                },
                tooltip: {
                    trigger: 'axis',  // 改为axis触发，显示同一时间点所有数据
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    borderColor: '#3a3d5c',
                    borderWidth: 1,
                    textStyle: { color: '#fff', fontSize: 12 },
                    axisPointer: {
                        type: 'cross',
                        crossStyle: {
                            color: '#8b92b8'
                        }
                    },
                    formatter: function(params) {
                        if (!params || params.length === 0) return '';
                        const time = params[0].axisValue;
                        let html = `<div style="padding: 8px;">
                            <div style="font-weight: bold; margin-bottom: 8px; font-size: 13px; border-bottom: 1px solid #3a3d5c; padding-bottom: 5px;">${time}</div>`;
                        
                        params.forEach(item => {
                            html += `<div style="margin-top: 5px; display: flex; align-items: center; justify-content: space-between; gap: 15px;">
                                <span style="display: flex; align-items: center;">
                                    <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${item.color}; margin-right: 8px;"></span>
                                    ${item.seriesName}
                                </span>
                                <span style="color: ${item.color}; font-weight: bold;">${item.value}</span>
                            </div>`;
                        });
                        
                        html += '</div>';
                        return html;
                    }
                },
                legend: {
                    data: ['急涨', '急跌', '差值(急涨-急跌)', '计次'],
                    top: 10,
                    left: 'center',
                    textStyle: { color: '#8b92b8', fontSize: 13 },
                    itemWidth: 30,
                    itemHeight: 14,
                    itemGap: 20
                },
                xAxis: {
                    type: 'category',
                    data: data.times || [],
                    axisLine: { 
                        lineStyle: { color: '#3a3d5c', width: 1 }
                    },
                    axisLabel: { 
                        color: '#8b92b8',
                        fontSize: 10,
                        rotate: 45,  // 旋转45度，避免重叠
                        interval: 0,  // 显示所有标签
                        margin: 12,
                        align: 'right',  // 右对齐
                        verticalAlign: 'middle'
                    },
                    axisTick: {
                        show: true,
                        lineStyle: { color: '#3a3d5c' }
                    },
                    splitLine: { 
                        show: true,  // 显示分隔线
                        lineStyle: {
                            color: '#3a3d5c',
                            type: 'solid',  // 实线
                            width: 1,
                            opacity: 0.3
                        }
                    }
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '数量',
                        nameTextStyle: { 
                            color: '#8b92b8', 
                            fontSize: 12,
                            padding: [0, 0, 0, 10]
                        },
                        axisLine: { 
                            show: true,
                            lineStyle: { color: '#3a3d5c' } 
                        },
                        axisLabel: { 
                            color: '#8b92b8', 
                            fontSize: 11 
                        },
                        splitLine: { 
                            lineStyle: { 
                                color: '#3a3d5c', 
                                type: 'dashed',
                                opacity: 0.5
                            } 
                        }
                    },
                    {
                        type: 'value',
                        name: '计次',
                        nameTextStyle: { 
                            color: '#3b7dff', 
                            fontSize: 12,
                            padding: [0, 10, 0, 0]
                        },
                        axisLine: { 
                            show: true,
                            lineStyle: { color: '#3a3d5c' } 
                        },
                        axisLabel: { 
                            color: '#3b7dff', 
                            fontSize: 11 
                        },
                        splitLine: { show: false }
                    }
                ],
                series: [
                    {
                        name: '急涨',
                        type: 'line',
                        data: data.rush_up || [],
                        smooth: true,
                        connectNulls: true,  // 连接所有数据点，形成连续线段
                        lineStyle: {
                            width: 3,
                            color: '#ef4444'
                        },
                        itemStyle: { 
                            color: '#ef4444',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    },
                    {
                        name: '急跌',
                        type: 'line',
                        data: data.rush_down || [],
                        smooth: true,
                        connectNulls: true,  // 连接所有数据点，形成连续线段
                        lineStyle: {
                            width: 3,
                            color: '#10b981'
                        },
                        itemStyle: { 
                            color: '#10b981',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    },
                    {
                        name: '差值(急涨-急跌)',
                        type: 'line',
                        data: data.diff || [],
                        smooth: true,
                        connectNulls: true,  // 连接所有数据点，形成连续线段
                        lineStyle: {
                            width: 3,
                            color: '#fbbf24'
                        },
                        itemStyle: { 
                            color: '#fbbf24',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    },
                    {
                        name: '计次',
                        type: 'line',
                        yAxisIndex: 1,
                        data: data.count || [],
                        smooth: true,
                        connectNulls: true,  // 连接所有数据点，形成连续线段
                        lineStyle: {
                            width: 3,
                            color: '#3b7dff'
                        },
                        itemStyle: { 
                            color: '#3b7dff',
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        symbolSize: 8,
                        emphasis: {
                            scale: true,
                            scaleSize: 12
                        }
                    }
                ]
            };
            
            chart.setOption(option);
        }
        
        // 查询数据
        function queryData() {
            const date = document.getElementById('queryDate').value;
            const time = document.getElementById('queryTime').value;
            const datetime = date + ' ' + time;
            
            fetch('/api/query?time=' + encodeURIComponent(datetime))
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('❌ ' + data.error);
                        return;
                    }
                    updateUI(data);
                    loadChartData();  // 加载所有历史数据趋势图
                })
                .catch(error => {
                    alert('查询失败: ' + error);
                });
        }
        
        // 加载今天
        function loadToday() {
            const today = new Date();
            document.getElementById('queryDate').valueAsDate = today;
            queryData();
        }
        
        // 加载最新
        function loadLatest() {
            fetch('/api/latest')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('❌ ' + data.error);
                        return;
                    }
                    updateUI(data);
                    loadChartData();  // 加载所有历史数据趋势图
                })
                .catch(error => {
                    alert('加载失败: ' + error);
                });
        }
        
        // 批量导入今日数据
        function batchImportData() {
            const btn = document.getElementById('batchImportBtn');
            const originalText = btn.innerHTML;
            
            // 禁用按钮并显示加载状态
            btn.disabled = true;
            btn.innerHTML = '⏳ 正在批量导入...';
            btn.style.opacity = '0.6';
            btn.style.cursor = 'not-allowed';
            
            fetch('/api/query/batch-import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const stats = data.stats;
                    let message = `✅ 批量导入完成！\n\n`;
                    message += `📊 统计结果：\n`;
                    message += `   总文件数: ${stats.total}\n`;
                    message += `   ✅ 成功导入: ${stats.success}\n`;
                    message += `   ℹ️  已存在: ${stats.exists}\n`;
                    if (stats.invalid > 0) {
                        message += `   ⚠️  无效数据: ${stats.invalid}\n`;
                    }
                    if (stats.error > 0) {
                        message += `   ❌ 失败: ${stats.error}\n`;
                    }
                    
                    alert(message);
                    
                    // 如果有新数据导入，则刷新页面数据
                    if (stats.success > 0) {
                        loadToday();
                    }
                } else {
                    alert('❌ 批量导入失败: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ 批量导入失败: ' + error);
            })
            .finally(() => {
                // 恢复按钮状态
                btn.disabled = false;
                btn.innerHTML = originalText;
                btn.style.opacity = '1';
                btn.style.cursor = 'pointer';
            });
        }
        
        // 加载涨跌速数据
        function loadPriceSpeedData() {
            fetch('/api/price-speed/latest')
                .then(response => response.json())
                .then(response => {
                    if (response.success && response.data) {
                        const data = response.data;
                        
                        // 统计各级别数量
                        const upCount = data.filter(coin => 
                            coin.alert_level && coin.alert_level.includes('up') && coin.alert_level !== 'normal'
                        ).length;
                        
                        const downCount = data.filter(coin => 
                            coin.alert_level && coin.alert_level.includes('down') && coin.alert_level !== 'normal'
                        ).length;
                        
                        const normalCount = data.filter(coin => 
                            coin.alert_level === 'normal'
                        ).length;
                        
                        // 更新UI (已移除急涨速、急跌速、正常统计)
                    }
                })
                .catch(err => {
                    console.error('加载涨跌速数据失败:', err);
                    // 如果失败，显示默认值 (已移除急涨速、急跌速、正常统计)
                });
        }
        
        // 更新UI
        function updateUI(data) {
            document.getElementById('calcTime').textContent = data.snapshot_time;
            document.getElementById('rushUp').textContent = data.rush_up;
            document.getElementById('rushDown').textContent = data.rush_down;
            document.getElementById('roundRushUp').textContent = data.round_rush_up || data.rush_up;
            document.getElementById('roundRushDown').textContent = data.round_rush_down || data.rush_down;
            document.getElementById('countTimes').textContent = data.count;
            document.getElementById('countScore').textContent = data.count_score_display || '---';
            document.getElementById('status').textContent = data.status;
            document.getElementById('ratio').textContent = data.ratio;
            document.getElementById('diff').textContent = data.diff;
            document.getElementById('priceLowest').textContent = data.price_lowest || 0;
            document.getElementById('priceNewhigh').textContent = data.price_newhigh || 0;
            document.getElementById('rise24hCount').textContent = data.rise_24h_count || 0;
            document.getElementById('fall24hCount').textContent = data.fall_24h_count || 0;
            
            // 加载涨跌速数据
            loadPriceSpeedData();
            
            // 更新表格
            const tbody = document.getElementById('dataTableBody');
            if (data.coins && data.coins.length > 0) {
                let html = '';
                data.coins.forEach((coin, idx) => {
                    const changeClass = coin.change > 0 ? 'value-positive' : (coin.change < 0 ? 'value-negative' : 'value-neutral');
                    const change24Class = coin.change_24h > 0 ? 'value-positive' : (coin.change_24h < 0 ? 'value-negative' : 'value-neutral');
                    const priority = coin.priority || '未知';
                    const priorityClass = 'priority-' + priority.replace('等级', '');
                    
                    const rushUpTag = coin.rush_up > 0 ? '<span class="status-tag rise">' + coin.rush_up + '</span>' : coin.rush_up;
                    const rushDownTag = coin.rush_down > 0 ? '<span class="status-tag fall">' + coin.rush_down + '</span>' : coin.rush_down;
                    
                    html += '<tr>';
                    html += '<td class="' + priorityClass + '">' + priority + '</td>';
                    html += '<td>' + (idx + 1) + '</td>';
                    html += '<td class="coin-symbol">' + coin.symbol + '</td>';
                    html += '<td class="' + changeClass + '">' + coin.change.toFixed(2) + '</td>';
                    html += '<td>' + rushUpTag + '</td>';
                    html += '<td>' + rushDownTag + '</td>';
                    html += '<td>' + coin.update_time + '</td>';
                    html += '<td>' + coin.high_price.toFixed(2) + '</td>';
                    html += '<td>' + coin.high_time + '</td>';
                    html += '<td class="value-negative">' + coin.decline.toFixed(2) + '</td>';
                    html += '<td class="' + change24Class + '">' + coin.change_24h.toFixed(2) + '</td>';
                    html += '<td>' + coin.rank + '</td>';
                    html += '<td>' + coin.current_price.toFixed(4) + '</td>';
                    html += '<td>' + (coin.ratio1 || 'N/A') + '</td>';
                    html += '<td>' + (coin.ratio2 || 'N/A') + '</td>';
                    html += '</tr>';
                });
                tbody.innerHTML = html;
            } else {
                tbody.innerHTML = '<tr><td colspan="15" class="loading">暂无数据</td></tr>';
            }
        }
        
        // 加载图表数据
        // 当前页码（全局变量）
        let currentPage = 0;
        
        function loadChartData(page = 0) {
            // 加载指定页的历史数据点（12小时/页，显示所有数据点）
            currentPage = page;
            fetch(`/api/chart?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(data.error);
                        return;
                    }
                    updateChart(data);
                    
                    // 更新分页信息
                    document.getElementById('chartPageInfo').textContent = 
                        `第${page + 1}/${data.total_pages}页`;
                    document.getElementById('chartTimeRange').textContent = 
                        `${data.time_range.start} - ${data.time_range.end}`;
                    
                    // 更新按钮状态
                    document.getElementById('btnPrevPage').disabled = !data.has_prev;
                    document.getElementById('btnNextPage').disabled = !data.has_next;
                })
                .catch(error => {
                    console.error('图表加载失败:', error);
                });
        }
        
        // 翻页按钮事件
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('btnPrevPage').addEventListener('click', function() {
                loadChartData(currentPage + 1);  // 上一页（更早的数据）
            });
            
            document.getElementById('btnNextPage').addEventListener('click', function() {
                loadChartData(currentPage - 1);  // 下一页（更新的数据）
            });
        });
        
        // 页面加载时自动加载最新数据
        // 加载时间轴数据 - 竖直布局
        function loadTimeline() {
            fetch('/api/timeline')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('timelineInfo').textContent = data.error;
                        return;
                    }
                    
                    document.getElementById('timelineInfo').textContent = 
                        `共 ${data.snapshots.length} 个数据点`;
                    
                    const pointsContainer = document.getElementById('timelinePoints');
                    pointsContainer.innerHTML = '';
                    
                    // 时间从上到下：最早的在上面，最新的在下面
                    data.snapshots.forEach((snapshot, index) => {
                        const point = document.createElement('div');
                        point.className = 'timeline-point';
                        point.setAttribute('data-time', snapshot.snapshot_time);
                        
                        // 最后一个（最新的）标记为激活
                        if (index === data.snapshots.length - 1) {
                            point.classList.add('active');
                        }
                        
                        const label = document.createElement('div');
                        label.className = 'timeline-label';
                        
                        // 时间显示
                        const timeSpan = document.createElement('div');
                        timeSpan.className = 'timeline-label-time';
                        timeSpan.textContent = snapshot.snapshot_time;
                        
                        // 统计信息显示 - 显示所有关键字段
                        const statsSpan = document.createElement('div');
                        statsSpan.className = 'timeline-label-stats';
                        
                        // 第一行：急涨、急跌、计次、得分
                        const line1 = `急涨:${snapshot.rush_up} 急跌:${snapshot.rush_down} 计次:${snapshot.count} ${snapshot.count_score_display || ''}`;
                        
                        // 第二行：状态、比值、差值
                        const line2 = `状态:${snapshot.status || ''} 比值:${snapshot.ratio || 0} 差值:${snapshot.diff}`;
                        
                        // 第三行：本轮、比价、24h
                        const line3 = `本轮急涨:${snapshot.round_rush_up || 0} 本轮急跌:${snapshot.round_rush_down || 0} 24h涨≥10%:${snapshot.rise_24h_count || 0} 24h跌≤-10%:${snapshot.fall_24h_count || 0}`;
                        
                        statsSpan.innerHTML = `
                            <div style="margin-bottom: 2px;">${line1}</div>
                            <div style="margin-bottom: 2px;">${line2}</div>
                            <div>${line3}</div>
                        `;
                        
                        label.appendChild(timeSpan);
                        label.appendChild(statsSpan);
                        point.appendChild(label);
                        
                        point.onclick = function() {
                            // 移除所有激活状态
                            document.querySelectorAll('.timeline-point').forEach(p => {
                                p.classList.remove('active');
                            });
                            // 激活当前点
                            this.classList.add('active');
                            // 加载数据
                            loadSnapshotData(snapshot.snapshot_time);
                        };
                        
                        pointsContainer.appendChild(point);
                    });
                })
                .catch(error => {
                    console.error('加载时间轴失败:', error);
                    document.getElementById('timelineInfo').textContent = '加载失败';
                });
        }
        
        // 加载指定快照的数据
        function loadSnapshotData(snapshotTime) {
            fetch('/api/query?time=' + encodeURIComponent(snapshotTime))
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    updateUI(data);
                    updateChart(data);
                    
                    // 更新时间轴激活状态
                    document.querySelectorAll('.timeline-point').forEach(point => {
                        point.classList.remove('active');
                    });
                    event.target.classList.add('active');
                })
                .catch(error => console.error('加载数据失败:', error));
        }
        
        window.onload = function() {
            loadLatest();
            loadTimeline();
        };
        
        // 响应式调整
        window.addEventListener('resize', function() {
            chart.resize();
        });
    </script>
</body>
</html>
"""

# API路由保持不变，使用之前的代码
@app.route('/')
def index():
    """首页 - 功能导航"""
    return render_template('index.html')

@app.route('/query')
def query_page():
    """历史数据查询页面"""
    return render_template_string(MAIN_HTML)

@app.route('/chart')
def chart_page():
    """趋势图表页面"""
    return render_template_string(MAIN_HTML)

@app.route('/timeline')
def timeline_page():
    """时间轴页面"""
    return render_template_string(MAIN_HTML)

@app.route('/status')
def status_page():
    """系统状态页面"""
    return render_template('status.html')

@app.route('/panic')
def panic_page():
    """恐慌清洗指数页面"""
    return render_template('panic_new.html')

@app.route('/api/panic/latest')
def api_panic_latest():
    """恐慌清洗指数最新数据API"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 使用新的 panic_wash_index 表
        cursor.execute('''
            SELECT record_time, panic_index, hour_24_people, total_position, 
                   hour_1_amount, hour_24_amount
            FROM panic_wash_index 
            ORDER BY record_time DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            panic_index_percentage = row[1]  # 百分比形式（如 8.67）
            # 如果是整数就不显示小数部分，否则保留2位小数
            panic_index = int(panic_index_percentage) if panic_index_percentage == int(panic_index_percentage) else round(panic_index_percentage, 2)
            
            people_wan = round(row[2] / 10000, 2)  # 人 -> 万人（去掉4个0）
            position_yi = round(row[3] / 100000000, 2)  # 美元 -> 亿美元（去掉8个0 = 除以1亿）
            hour_1_amount_usd = row[4]  # 1小时爆仓金额（美元）
            hour_24_amount_usd = row[5]  # 24小时爆仓金额（美元）
            
            # 单位转换：美元 -> 万美元
            hour_1_amount_wan = round(hour_1_amount_usd / 10000, 2)  # 美元 -> 万美元（去掉4个0）
            hour_24_amount_wan = round(hour_24_amount_usd / 10000, 2)  # 美元 -> 万美元（去掉4个0）
            
            # 根据恐慌指数确定等级（现在使用百分比形式判断：8.67% 在低恐慌范围）
            if panic_index_percentage < 5:
                panic_level = '低恐慌'
                level_color = 'green'
            elif panic_index_percentage < 10:
                panic_level = '中度恐慌'
                level_color = 'yellow'
            else:
                panic_level = '高度恐慌'
                level_color = 'red'
            
            return jsonify({
                'success': True,
                'data': {
                    'record_time': row[0],
                    'panic_index': panic_index,
                    'panic_level': panic_level,
                    'level_color': level_color,
                    'hour_24_people': people_wan,
                    'total_position': position_yi,
                    'hour_1_amount': hour_1_amount_wan,  # 返回万美元
                    'hour_24_amount': hour_24_amount_wan,  # 返回万美元
                    'market_zone': f'{people_wan}万人/{position_yi}亿美元'
                }
            })
        else:
            return jsonify({'success': False, 'error': '暂无数据'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def api_stats():
    """统计数据API - 包含本轮急涨急跌和恐慌清洗指数"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM crypto_snapshots")
        total_records = cursor.fetchone()[0]
        
        # 今日记录数
        today = datetime.now(BEIJING_TZ).date().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM crypto_snapshots WHERE snapshot_date = ?", (today,))
        today_records = cursor.fetchone()[0]
        
        # 数据天数
        cursor.execute("SELECT COUNT(DISTINCT snapshot_date) FROM crypto_snapshots")
        data_days = cursor.fetchone()[0]
        
        # 获取最新两条记录用于计算本轮差值
        cursor.execute("""
            SELECT snapshot_time, rush_up, rush_down, round_rush_up, round_rush_down
            FROM crypto_snapshots
            ORDER BY snapshot_date DESC, snapshot_time DESC
            LIMIT 2
        """)
        latest_records = cursor.fetchall()
        
        last_update_time = '-'
        current_round_rush_up = 0
        current_round_rush_down = 0
        
        if latest_records and len(latest_records) >= 1:
            # snapshot_time 格式: "2025-12-10 16:35:00", 提取时间部分 HH:MM
            time_str = latest_records[0][0]
            if time_str:
                # 如果包含日期，提取时间部分（格式：YYYY-MM-DD HH:MM:SS）
                if ' ' in time_str:
                    last_update_time = time_str.split(' ')[1][:5]  # 提取 HH:MM
                else:
                    # 如果只有时间（格式：HH:MM:SS）
                    last_update_time = time_str[:5]
            else:
                last_update_time = '-'
            current_rush_up = latest_records[0][1]
            current_rush_down = latest_records[0][2]
            
            if len(latest_records) >= 2:
                prev_rush_up = latest_records[1][1]
                prev_rush_down = latest_records[1][2]
                
                # 本轮急涨 = 当前急涨 - 上一轮急涨
                current_round_rush_up = current_rush_up - prev_rush_up
                # 本轮急跌 = 当前急跌 - 上一轮急跌
                current_round_rush_down = current_rush_down - prev_rush_down
        
        # 获取恐慌清洗指数（从新的独立采集表）
        cursor.execute("""
            SELECT panic_index, hour_24_people, total_position, record_time
            FROM panic_wash_index
            ORDER BY record_time DESC
            LIMIT 1
        """)
        panic_data = cursor.fetchone()
        
        panic_indicator = '-'
        panic_color = 'gray'
        panic_trend_rating = 0
        panic_market_zone = '-'
        panic_people_wan = 0
        panic_position_yi = 0
        
        if panic_data:
            panic_indicator = panic_data[0]  # 恐慌指数（百分比）
            panic_people_wan = round(panic_data[1] / 10000, 2)  # 爆仓人数（万人）
            panic_position_yi = round(panic_data[2] / 100000000, 2)  # 持仓量（亿美元）
            
            # 根据恐慌指数设置颜色（现在是百分比形式：如8.67%）
            if panic_indicator < 5:
                panic_color = '绿'  # 低恐慌（<5%）
            elif panic_indicator < 10:
                panic_color = '黄'  # 中恐慌（5-10%）
            else:
                panic_color = '红'  # 高恐慌（>10%）
            
            # 市场区间描述
            panic_market_zone = f"{panic_people_wan}万人/{panic_position_yi}亿美元"
        
        conn.close()
        
        return jsonify({
            'total_records': total_records,
            'today_records': today_records,
            'data_days': data_days,
            'last_update_time': last_update_time,
            'current_round_rush_up': current_round_rush_up,
            'current_round_rush_down': current_round_rush_down,
            'panic_indicator': panic_indicator,
            'panic_color': panic_color,
            'panic_trend_rating': panic_trend_rating,
            'panic_market_zone': panic_market_zone
        })
    except Exception as e:
        return jsonify({
            'total_records': 0,
            'today_records': 0,
            'data_days': 0,
            'last_update_time': '-',
            'current_round_rush_up': 0,
            'current_round_rush_down': 0,
            'panic_indicator': '-',
            'panic_color': 'gray',
            'panic_trend_rating': 0,
            'panic_market_zone': '-',
            'error': str(e)
        })

@app.route('/api/homepage/summary')
def api_homepage_summary():
    """首页聚合数据API - 一次返回所有首页需要的数据"""
    try:
        result = {
            'success': True,
            'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 1. 统计栏数据（本轮急涨急跌和恐慌指数）
        cursor.execute("SELECT COUNT(*) FROM crypto_snapshots")
        total_records = cursor.fetchone()[0]
        
        today = datetime.now(BEIJING_TZ).date().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM crypto_snapshots WHERE snapshot_date = ?", (today,))
        today_records = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT snapshot_time, rush_up, rush_down
            FROM crypto_snapshots
            ORDER BY snapshot_date DESC, snapshot_time DESC
            LIMIT 2
        """)
        latest_records = cursor.fetchall()
        
        last_update_time = '-'
        current_round_rush_up = 0
        current_round_rush_down = 0
        
        if latest_records and len(latest_records) >= 1:
            time_str = latest_records[0][0]
            if time_str and ' ' in time_str:
                last_update_time = time_str.split(' ')[1][:5]
            current_rush_up = latest_records[0][1]
            current_rush_down = latest_records[0][2]
            
            if len(latest_records) >= 2:
                prev_rush_up = latest_records[1][1]
                prev_rush_down = latest_records[1][2]
                current_round_rush_up = current_rush_up - prev_rush_up
                current_round_rush_down = current_rush_down - prev_rush_down
        
        cursor.execute("""
            SELECT panic_index, hour_24_people, total_position
            FROM panic_wash_index
            ORDER BY record_time DESC
            LIMIT 1
        """)
        panic_data = cursor.fetchone()
        
        panic_indicator = '-'
        panic_color = 'gray'
        panic_market_zone = '-'
        
        if panic_data:
            panic_indicator = panic_data[0]
            panic_people_wan = round(panic_data[1] / 10000, 2)
            panic_position_yi = round(panic_data[2] / 100000000, 2)
            
            if panic_indicator < 5:
                panic_color = '绿'
            elif panic_indicator < 10:
                panic_color = '黄'
            else:
                panic_color = '红'
            
            panic_market_zone = f"{panic_people_wan}万人/{panic_position_yi}亿美元"
        
        result['stats'] = {
            'total_records': total_records,
            'today_records': today_records,
            'last_update_time': last_update_time,
            'current_round_rush_up': current_round_rush_up,
            'current_round_rush_down': current_round_rush_down,
            'panic_indicator': panic_indicator,
            'panic_color': panic_color,
            'panic_market_zone': panic_market_zone
        }
        
        # 2. 模块统计数据
        cursor.execute("SELECT MIN(snapshot_date), MAX(snapshot_date) FROM crypto_snapshots")
        date_range = cursor.fetchone()
        data_days = 0
        if date_range and date_range[0] and date_range[1]:
            data_days = (datetime.strptime(date_range[1], '%Y-%m-%d') - 
                        datetime.strptime(date_range[0], '%Y-%m-%d')).days + 1
        
        cursor.execute("SELECT MAX(snapshot_time) FROM crypto_snapshots")
        last_snapshot = cursor.fetchone()
        last_update = last_snapshot[0] if last_snapshot else '-'
        
        result['modules_stats'] = {
            'query_module': {
                'total_records': total_records,
                'data_days': data_days,
                'last_update': last_update
            }
        }
        
        # 3. 价格突破统计（创新高/创新低）
        cursor.execute("""
            SELECT event_type, COUNT(*) 
            FROM price_breakthrough_events 
            WHERE DATE(event_time) = ?
            GROUP BY event_type
        """, (today,))
        breakthrough_today = dict(cursor.fetchall())
        
        result['price_breakthrough'] = {
            'today': {
                'new_high': breakthrough_today.get('new_high', 0),
                'new_low': breakthrough_today.get('new_low', 0)
            }
        }
        
        # 4. V1V2成交系统数据（从实际API获取或占位）
        # 暂时使用占位数据，后续可以调用原有的v1v2 API
        result['v1v2_system'] = {
            'v1_count': 0,
            'v2_count': 0,
            'update_time': last_update
        }
        
        # 5. 支撑压力线系统数据
        cursor.execute("""
            SELECT 
                symbol, 
                alert_scenario_1, alert_scenario_2, alert_scenario_3, alert_scenario_4,
                position_s2_r1, position_s1_r2, position_s1_r1
            FROM support_resistance_levels
            WHERE record_time = (SELECT MAX(record_time) FROM support_resistance_levels)
        """)
        sr_data = cursor.fetchall()
        
        scenario1_coins = []
        scenario2_coins = []
        scenario3_coins = []
        scenario4_coins = []
        
        for row in sr_data:
            symbol, s1, s2, s3, s4, pos_s2_r1, pos_s1_r2, pos_s1_r1 = row
            coin_symbol = symbol.replace('USDT', '')
            
            if s1:
                scenario1_coins.append({'symbol': coin_symbol, 'position': pos_s2_r1})
            if s2:
                scenario2_coins.append({'symbol': coin_symbol, 'position': pos_s1_r2})
            if s3:
                scenario3_coins.append({'symbol': coin_symbol, 'position': pos_s1_r2})
            if s4:
                scenario4_coins.append({'symbol': coin_symbol, 'position': pos_s1_r1})
        
        result['support_resistance'] = {
            'total_count': len(sr_data),
            'scenario1_coins': scenario1_coins,
            'scenario2_coins': scenario2_coins,
            'scenario3_coins': scenario3_coins,
            'scenario4_coins': scenario4_coins,
            'update_time': last_update
        }
        
        # 6. 交易信号系统数据
        # 简化版本，返回基本计数
        result['trading_signals'] = {
            'buy_point_1_count': 0,
            'buy_point_2_count': 0,
            'total_coins': 27,
            'update_time': last_update
        }
        
        # 7. 1分钟涨跌速数据（占位，需要实际数据源）
        result['price_speed'] = {
            'up_count': 0,
            'down_count': 0,
            'update_time': last_update
        }
        
        # 8. 监控状态
        cursor.execute("""
            SELECT snapshot_time 
            FROM crypto_snapshots 
            ORDER BY snapshot_date DESC, snapshot_time DESC 
            LIMIT 1
        """)
        latest_snapshot_row = cursor.fetchone()
        latest_snapshot_time = latest_snapshot_row[0] if latest_snapshot_row else None
        
        need_collection = False
        minutes_since_last = None
        
        if latest_snapshot_time:
            latest_dt = datetime.strptime(latest_snapshot_time, '%Y-%m-%d %H:%M:%S')
            latest_dt = BEIJING_TZ.localize(latest_dt)
            now = datetime.now(BEIJING_TZ)
            minutes_since_last = (now - latest_dt).total_seconds() / 60
            
            if minutes_since_last > 15:
                need_collection = True
        
        result['monitor_status'] = {
            'need_collection': need_collection,
            'latest_snapshot': latest_snapshot_time,
            'minutes_since_last': round(minutes_since_last, 1) if minutes_since_last else None
        }
        
        # 9. Google Drive检测器状态（占位）
        result['gdrive_detector'] = {
            'detector_running': False,
            'file_timestamp': None,
            'delay_minutes': None,
            'latest_file': None
        }
        
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        })

@app.route('/api/query')
def api_query():
    """查询API"""
    query_time = request.args.get('time', '')
    if not query_time:
        return jsonify({'error': '请提供查询时间'})
    
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                snapshot_date, snapshot_time, rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down, price_lowest, price_newhigh,
                count_score_display, count_score_type, rise_24h_count, fall_24h_count
            FROM crypto_snapshots
            WHERE snapshot_time LIKE ?
            ORDER BY snapshot_date DESC, snapshot_time DESC
            LIMIT 1
        """, (f"{query_time}%",))
        
        snapshot = cursor.fetchone()
        
        if not snapshot:
            conn.close()
            return jsonify({'error': f'未找到 {query_time} 的数据'})
        
        (snapshot_date, snapshot_time, rush_up, rush_down, diff, count, ratio, status,
         round_rush_up, round_rush_down, price_lowest, price_newhigh,
         count_score_display, count_score_type, rise_24h_count, fall_24h_count) = snapshot
        
        # snapshot_time已经是完整的日期时间，无需拼接
        # 格式: '2025-12-09 22:40:00'
        
        cursor.execute("""
            SELECT 
                symbol, change, rush_up, rush_down, update_time,
                high_price, high_time, decline, change_24h, rank,
                current_price, priority_level, ratio1, ratio2
            FROM crypto_coin_data
            WHERE snapshot_time = ?
            ORDER BY index_order ASC
        """, (snapshot_time,))
        
        coins = []
        for row in cursor.fetchall():
            coins.append({
                'symbol': row[0],
                'change': row[1],
                'rush_up': row[2],
                'rush_down': row[3],
                'update_time': row[4],
                'high_price': row[5],
                'high_time': row[6],
                'decline': row[7],
                'change_24h': row[8],
                'rank': row[9],
                'current_price': row[10],
                'priority': row[11],
                'ratio1': row[12],
                'ratio2': row[13]
            })
        
        conn.close()
        
        return jsonify({
            'snapshot_time': snapshot_time,
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'count': count,
            'ratio': ratio,
            'status': status,
            'round_rush_up': round_rush_up,
            'round_rush_down': round_rush_down,
            'price_lowest': price_lowest,
            'price_newhigh': price_newhigh,
            'count_score_display': count_score_display,
            'count_score_type': count_score_type,
            'rise_24h_count': rise_24h_count,
            'fall_24h_count': fall_24h_count,
            'coins': coins
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/latest')
def api_latest():
    """获取最新数据API"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                snapshot_date, snapshot_time, rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down, price_lowest, price_newhigh,
                count_score_display, count_score_type, rise_24h_count, fall_24h_count
            FROM crypto_snapshots
            ORDER BY snapshot_date DESC, snapshot_time DESC
            LIMIT 1
        """)
        
        snapshot = cursor.fetchone()
        
        if not snapshot:
            conn.close()
            return jsonify({'error': '数据库中暂无数据'})
        
        (snapshot_date, snapshot_time, rush_up, rush_down, diff, count, ratio, status,
         round_rush_up, round_rush_down, price_lowest, price_newhigh,
         count_score_display, count_score_type, rise_24h_count, fall_24h_count) = snapshot
        
        # snapshot_time已经是完整的日期时间，无需拼接
        # 格式: '2025-12-09 22:40:00'
        
        cursor.execute("""
            SELECT 
                symbol, change, rush_up, rush_down, update_time,
                high_price, high_time, decline, change_24h, rank,
                current_price, priority_level, ratio1, ratio2
            FROM crypto_coin_data
            WHERE snapshot_time = ?
            ORDER BY index_order ASC
        """, (snapshot_time,))
        
        coins = []
        for row in cursor.fetchall():
            coins.append({
                'symbol': row[0],
                'change': row[1],
                'rush_up': row[2],
                'rush_down': row[3],
                'update_time': row[4],
                'high_price': row[5],
                'high_time': row[6],
                'decline': row[7],
                'change_24h': row[8],
                'rank': row[9],
                'current_price': row[10],
                'priority': row[11],
                'ratio1': row[12],
                'ratio2': row[13]
            })
        
        conn.close()
        
        return jsonify({
            'snapshot_time': snapshot_time,
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'count': count,
            'ratio': ratio,
            'status': status,
            'round_rush_up': round_rush_up,
            'round_rush_down': round_rush_down,
            'price_lowest': price_lowest,
            'price_newhigh': price_newhigh,
            'count_score_display': count_score_display,
            'count_score_type': count_score_type,
            'rise_24h_count': rise_24h_count,
            'fall_24h_count': fall_24h_count,
            'coins': coins
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/chart')
def api_chart():
    """图表数据API - 支持分页的12小时趋势图数据（显示所有数据点）"""
    try:
        from datetime import datetime, timedelta
        
        # 获取分页参数
        page = request.args.get('page', '0')  # 默认第0页（最新）
        page = int(page)
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取所有历史数据点，按时间升序排列
        cursor.execute("""
            SELECT 
                snapshot_time, rush_up, rush_down, diff, count
            FROM crypto_snapshots
            ORDER BY snapshot_date ASC, snapshot_time ASC
        """)
        
        all_data = cursor.fetchall()
        conn.close()
        
        if not all_data:
            return jsonify({'error': '无数据'})
        
        # 转换为datetime对象
        all_points = []
        for row in all_data:
            dt = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            all_points.append({
                'time': dt,
                'formatted_time': dt.strftime('%m-%d %H:%M'),
                'rush_up': row[1],
                'rush_down': row[2],
                'diff': row[3],
                'count': row[4]
            })
        
        # 计算总页数（每页12小时）
        earliest = all_points[0]['time']
        latest = all_points[-1]['time']
        total_hours = (latest - earliest).total_seconds() / 3600
        total_pages = max(1, int(total_hours / 12) + 1)
        
        # 确保page在有效范围内
        if page < 0:
            page = 0
        if page >= total_pages:
            page = total_pages - 1
        
        # 计算当前页的时间范围（从最新往前推）
        # page=0 是最新的12小时，page=1 是之前的12小时，以此类推
        page_end_time = latest - timedelta(hours=12 * page)
        page_start_time = page_end_time - timedelta(hours=12)
        
        # 筛选当前页的数据点
        page_points = [
            p for p in all_points 
            if page_start_time <= p['time'] <= page_end_time
        ]
        
        # 如果当前页没有数据，返回空数组
        if not page_points:
            return jsonify({
                'times': [],
                'rush_up': [],
                'rush_down': [],
                'diff': [],
                'count': [],
                'page': page,
                'total_pages': total_pages,
                'has_prev': page < total_pages - 1,
                'has_next': page > 0,
                'time_range': {
                    'start': page_start_time.strftime('%Y-%m-%d %H:%M'),
                    'end': page_end_time.strftime('%Y-%m-%d %H:%M')
                }
            })
        
        # 提取数据
        times = [p['formatted_time'] for p in page_points]
        rush_up = [p['rush_up'] for p in page_points]
        rush_down = [p['rush_down'] for p in page_points]
        diff = [p['diff'] for p in page_points]
        count = [p['count'] for p in page_points]
        
        return jsonify({
            'times': times,
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'count': count,
            'page': page,
            'total_pages': total_pages,
            'has_prev': page < total_pages - 1,  # 有上一页（更早的数据）
            'has_next': page > 0,  # 有下一页（更新的数据）
            'time_range': {
                'start': page_start_time.strftime('%Y-%m-%d %H:%M'),
                'end': page_end_time.strftime('%Y-%m-%d %H:%M')
            },
            'data_count': len(page_points)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/timeline')
def api_timeline():
    """获取所有历史数据点API - 返回完整的统计数据"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 查询所有字段 - 倒序排列（时间晚的在上，时间早的在下）
        cursor.execute("""
            SELECT 
                id, snapshot_time, snapshot_date,
                rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down,
                price_lowest, price_newhigh, ratio_diff,
                init_rush_up, init_rush_down,
                count_score_display, count_score_type,
                rise_24h_count, fall_24h_count,
                green_count, percentage, filename
            FROM crypto_snapshots
            ORDER BY snapshot_date DESC, snapshot_time DESC
        """)
        
        snapshots = []
        for row in cursor.fetchall():
            snapshots.append({
                'id': row[0],
                'snapshot_time': row[1],
                'snapshot_date': row[2],
                # 主要统计
                'rush_up': row[3],
                'rush_down': row[4],
                'diff': row[5],
                'count': row[6],
                'ratio': row[7],
                'status': row[8],
                # 本轮数据
                'round_rush_up': row[9],
                'round_rush_down': row[10],
                # 比价数据
                'price_lowest': row[11],
                'price_newhigh': row[12],
                'ratio_diff': row[13],
                # 初始数据
                'init_rush_up': row[14],
                'init_rush_down': row[15],
                # 计次得分
                'count_score_display': row[16],
                'count_score_type': row[17],
                # 24小时涨跌
                'rise_24h_count': row[18],
                'fall_24h_count': row[19],
                # 其他
                'green_count': row[20],
                'percentage': row[21],
                'filename': row[22]
            })
        
        conn.close()
        
        return jsonify({
            'snapshots': snapshots,
            'total': len(snapshots)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)})

# ==================== 交易信号监控 API ====================

@app.route('/signals')
def signals_page():
    """交易信号监控页面"""
    return render_template('signals.html')

@app.route('/popup-demo')
def popup_demo():
    """弹窗效果演示页面"""
    with open('popup_demo.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/signals/stats')
def api_signals_stats():
    """获取信号统计数据"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最新记录
        cursor.execute('''
            SELECT record_time, long_signals, short_signals, 
                   total_signals, long_ratio, short_ratio
            FROM trading_signals
            ORDER BY record_time DESC
            LIMIT 1
        ''')
        latest = cursor.fetchone()
        
        # 获取总记录数
        cursor.execute('SELECT COUNT(*) FROM trading_signals')
        total_records = cursor.fetchone()[0]
        
        conn.close()
        
        if latest:
            return jsonify({
                'success': True,
                'data': {
                    'latest_time': latest[0],
                    'latest_long': latest[1],
                    'latest_short': latest[2],
                    'latest_total': latest[3],
                    'long_ratio': latest[4],
                    'short_ratio': latest[5],
                    'total_records': total_records
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '暂无数据'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/signals/chart')
def api_signals_chart():
    """获取图表数据（支持分页和时间范围）"""
    try:
        page = int(request.args.get('page', 0))
        time_range = request.args.get('range', '12h')
        
        # 计算时间范围对应的数据点数量（每3分钟一个点）
        range_minutes = {
            '1h': 60,
            '6h': 360,
            '12h': 720,
            '24h': 1440
        }
        
        minutes = range_minutes.get(time_range, 720)
        points_per_page = minutes // 3  # 每3分钟一个数据点
        offset = page * points_per_page
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取总记录数
        cursor.execute('SELECT COUNT(*) FROM trading_signals')
        total = cursor.fetchone()[0]
        total_pages = (total + points_per_page - 1) // points_per_page
        
        # 获取分页数据
        cursor.execute('''
            SELECT record_time, long_signals, short_signals, total_signals
            FROM trading_signals
            ORDER BY record_time DESC
            LIMIT ? OFFSET ?
        ''', (points_per_page, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        # 反转顺序，使时间从早到晚
        rows.reverse()
        
        data = [{
            'time': row[0].split(' ')[1][:5],  # 只取时分
            'long_signals': row[1],
            'short_signals': row[2],
            'total_signals': row[3]
        } for row in rows]
        
        return jsonify({
            'success': True,
            'data': data,
            'page': page,
            'total_pages': total_pages,
            'range': time_range
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/signals/history')
def api_signals_history():
    """获取历史记录列表"""
    try:
        limit = int(request.args.get('limit', 50))
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT record_time, long_signals, short_signals,
                   total_signals, long_ratio, short_ratio
            FROM trading_signals
            ORDER BY record_time DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = [{
            'record_time': row[0],
            'long_signals': row[1],
            'short_signals': row[2],
            'total_signals': row[3],
            'long_ratio': row[4],
            'short_ratio': row[5]
        } for row in rows]
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/liquidation/30days')
def api_liquidation_30days():
    """30日爆仓数据API"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, long_amount, short_amount, total_amount, updated_at
            FROM liquidation_30days
            ORDER BY date DESC
            LIMIT 30
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'date': row[0],
                'long_amount': round(row[1] / 100000000, 2),  # 转换为亿
                'short_amount': round(row[2] / 100000000, 2),
                'total_amount': round(row[3] / 100000000, 2),
                'updated_at': row[4]
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/panic/history')
def api_panic_history():
    """恐慌清洗指数历史数据API（支持时间查询）"""
    try:
        limit = int(request.args.get('limit', 50))
        query_time = request.args.get('time', None)  # 可选的时间查询参数
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        if query_time:
            # 时间范围查询：查询指定时间前后的数据
            half_limit = limit // 2
            
            # 先查询指定时间之前的记录（过滤掉异常数据）
            cursor.execute('''
                SELECT record_time, panic_index, hour_24_people, total_position, hour_1_amount, hour_24_amount
                FROM panic_wash_index
                WHERE record_time <= ?
                  AND panic_index > 0 
                  AND hour_24_people > 0 
                  AND total_position > 1000000000
                  AND hour_1_amount > 100000
                  AND hour_24_amount > 1000000
                ORDER BY record_time DESC
                LIMIT ?
            ''', (query_time, half_limit))
            before_rows = cursor.fetchall()
            
            # 再查询指定时间之后的记录（过滤掉异常数据）
            cursor.execute('''
                SELECT record_time, panic_index, hour_24_people, total_position, hour_1_amount, hour_24_amount
                FROM panic_wash_index
                WHERE record_time > ?
                  AND panic_index > 0 
                  AND hour_24_people > 0 
                  AND total_position > 1000000000
                  AND hour_1_amount > 100000
                  AND hour_24_amount > 1000000
                ORDER BY record_time ASC
                LIMIT ?
            ''', (query_time, half_limit))
            after_rows = cursor.fetchall()
            
            # 合并结果并按时间倒序排列（最新的在前面）
            rows = list(before_rows) + list(reversed(after_rows))
        else:
            # 默认查询：最新的N条记录（过滤掉异常数据，最新的在前面）
            # total_position > 1000000000 表示大于10亿（原始值以美元计）
            # hour_1_amount > 100000 表示大于10万（原始值以美元计）
            # hour_24_amount > 1000000 表示大于100万（原始值以美元计）
            cursor.execute('''
                SELECT record_time, panic_index, hour_24_people, total_position, hour_1_amount, hour_24_amount
                FROM panic_wash_index
                WHERE panic_index > 0 
                  AND hour_24_people > 0 
                  AND total_position > 1000000000
                  AND hour_1_amount > 100000
                  AND hour_24_amount > 1000000
                ORDER BY record_time DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
        
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'record_time': row[0],
                'panic_index': row[1],
                'hour_24_people': round(row[2] / 10000, 2),  # 转换为万人
                'total_position': round(row[3] / 100000000, 2),  # 转换为亿美元
                'hour_1_amount': round(row[4] / 10000, 2),  # 转换为万美元
                'hour_24_amount': round(row[5] / 10000, 2)  # 转换为万美元
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'query_time': query_time  # 返回查询的时间
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/modules/stats')
def api_modules_stats():
    """获取所有模块的统计信息"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 1. 历史数据查询模块统计
        cursor.execute("SELECT COUNT(*) FROM crypto_snapshots")
        query_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT snapshot_date) FROM crypto_snapshots")
        query_days = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(snapshot_time) FROM crypto_snapshots")
        query_last_time = cursor.fetchone()[0] or '-'
        if query_last_time != '-':
            # 处理时间格式：可能是 "HH:MM:SS" 或 "YYYY-MM-DD HH:MM:SS"
            if ' ' in query_last_time:
                query_last_time = query_last_time.split(' ')[1][:5]  # 取HH:MM
            else:
                query_last_time = query_last_time[:5]  # 已经是HH:MM:SS，取HH:MM
        
        # 2. 交易信号监控模块统计
        cursor.execute("SELECT COUNT(*) FROM trading_signals")
        signal_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT record_date) FROM trading_signals")
        signal_days = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(record_time) FROM trading_signals")
        signal_last_time = cursor.fetchone()[0] or '-'
        if signal_last_time != '-':
            # 处理时间格式：可能是 "HH:MM:SS" 或 "YYYY-MM-DD HH:MM:SS"
            if ' ' in signal_last_time:
                signal_last_time = signal_last_time.split(' ')[1][:5]  # 取HH:MM
            else:
                signal_last_time = signal_last_time[:5]  # 已经是HH:MM:SS，取HH:MM
        
        # 3. 恐慌清洗指数模块统计
        cursor.execute("SELECT COUNT(*) FROM panic_wash_index")
        panic_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT DATE(record_time)) FROM panic_wash_index")
        panic_days = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(record_time) FROM panic_wash_index")
        panic_last_time = cursor.fetchone()[0] or '-'
        if panic_last_time != '-':
            # 处理时间格式：可能是 "HH:MM:SS" 或 "YYYY-MM-DD HH:MM:SS"
            if ' ' in panic_last_time:
                panic_last_time = panic_last_time.split(' ')[1][:5]  # 取HH:MM
            else:
                panic_last_time = panic_last_time[:5]  # 已经是HH:MM:SS，取HH:MM
        
        conn.close()
        
        return jsonify({
            'success': True,
            'query_module': {
                'total_records': query_total,
                'data_days': query_days,
                'last_update': query_last_time
            },
            'signal_module': {
                'total_records': signal_total,
                'data_days': signal_days,
                'last_update': signal_last_time
            },
            'panic_module': {
                'total_records': panic_total,
                'data_days': panic_days,
                'last_update': panic_last_time
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/price-comparison')
def price_comparison_page():
    """比价系统页面"""
    return render_template('price_comparison.html')

@app.route('/api/price-comparison/list')
def api_price_comparison_list():
    """获取比价系统所有币种数据 - 按用户指定顺序，使用北京时间"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, highest_price, highest_count, lowest_price, lowest_count,
                   highest_ratio, lowest_ratio, last_update_time
            FROM price_baseline
            ORDER BY display_order
        ''')
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
            # 从 symbol 提取币种名称 (例如: BTC-USDT-SWAP -> BTC)
            symbol = row[0]
            coin_name = symbol.split('-')[0] if symbol else ''
            
            # 转换时间为北京时间格式
            update_time = row[7]
            if update_time:
                try:
                    # 如果数据库时间是UTC，需要转换
                    from datetime import datetime
                    import pytz
                    dt = datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
                    # 假设数据库存的是北京时间，直接使用
                    beijing_time = update_time
                except:
                    beijing_time = update_time
            else:
                beijing_time = None
            
            data.append({
                'coin_name': coin_name,
                'symbol': symbol,
                'highest_price': row[1],
                'highest_count': row[2],
                'lowest_price': row[3],
                'lowest_count': row[4],
                'highest_ratio': row[5],
                'lowest_ratio': row[6],
                'last_update_time': beijing_time
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/price-comparison/update', methods=['POST'])
def api_price_comparison_update():
    """更新币种价格并进行比价判断
    
    逻辑:
    - 新价格 > 最高价: 更新最高价，最高计次清零
    - 新价格 < 最低价: 更新最低价，最低计次清零  
    - 最低价 <= 新价格 <= 最高价: 两个计次都+1
    """
    try:
        data = request.get_json()
        coin_name = data.get('coin_name')
        new_price = float(data.get('price'))
        
        if not coin_name or new_price is None:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: coin_name 或 price'
            })
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取当前币种的最高价和最低价
        cursor.execute('''
            SELECT highest_price, highest_count, lowest_price, lowest_count
            FROM price_baseline
            WHERE symbol = ?
        ''', (coin_name,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': f'币种 {coin_name} 不存在'
            })
        
        highest_price, highest_count, lowest_price, lowest_count = row
        old_highest_price = highest_price
        old_lowest_price = lowest_price
        
        # 价格比较逻辑
        action = ''
        if new_price > highest_price:
            # 新价格创新高
            old_highest_price = highest_price
            highest_price = new_price
            highest_count = 0
            action = 'new_high'
        elif new_price < lowest_price:
            # 新价格创新低
            old_lowest_price = lowest_price
            lowest_price = new_price
            lowest_count = 0
            action = 'new_low'
        else:
            # 价格在区间内
            highest_count += 1
            lowest_count += 1
            action = 'in_range'
        
        # 计算占比
        # 最高价占比 = (当前价 / 最高价) × 100
        highest_ratio = round((new_price / highest_price) * 100, 2) if highest_price > 0 else 0
        # 最低价占比 = (当前价 / 最低价) × 100
        lowest_ratio = round((new_price / lowest_price) * 100, 2) if lowest_price > 0 else 0
        
        # 更新数据库 - 使用北京时间
        from datetime import datetime
        import pytz
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            UPDATE price_baseline
            SET highest_price = ?,
                highest_count = ?,
                lowest_price = ?,
                lowest_count = ?,
                highest_ratio = ?,
                lowest_ratio = ?,
                last_update_time = ?
            WHERE symbol = ?
        ''', (highest_price, highest_count, lowest_price, lowest_count, 
              highest_ratio, lowest_ratio, beijing_time, coin_name))
        
        # 如果发生创新高或创新低，记录事件
        if action in ['new_high', 'new_low']:
            cursor.execute('''
                INSERT INTO price_breakthrough_events 
                (symbol, event_type, price, event_time)
                VALUES (?, ?, ?, ?)
            ''', (coin_name, action, new_price, beijing_time))
            
            # 更新统计表缓存（清除今天的缓存，下次查询时会重新计算）
            today_date = beijing_tz.localize(datetime.now()).strftime('%Y-%m-%d')
            cursor.execute('''
                DELETE FROM price_comparison_stats
                WHERE stat_date = ?
            ''', (today_date,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'action': action,
            'data': {
                'coin_name': coin_name,
                'new_price': new_price,
                'highest_price': highest_price,
                'highest_count': highest_count,
                'lowest_price': lowest_price,
                'lowest_count': lowest_count
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/price-comparison/breakthrough-stats')
def api_breakthrough_stats():
    """获取创新高/低统计
    
    返回:
    - 当天创新高次数、创新低次数
    - 3天内创新高次数、创新低次数
    - 7天内创新高次数、创新低次数
    
    优先从统计表读取，如果没有则实时计算并保存
    """
    try:
        from datetime import datetime, timedelta
        import pytz
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        today_date = now.strftime('%Y-%m-%d')
        
        # 先尝试从统计表读取今天的数据
        cursor.execute('''
            SELECT today_new_high, today_new_low, 
                   three_days_new_high, three_days_new_low,
                   seven_days_new_high, seven_days_new_low
            FROM price_comparison_stats
            WHERE stat_date = ?
        ''', (today_date,))
        
        cached_stats = cursor.fetchone()
        
        # 如果缓存存在且不超过5分钟，直接返回
        if cached_stats:
            conn.close()
            return jsonify({
                'success': True,
                'data': {
                    'today': {
                        'new_high': cached_stats[0],
                        'new_low': cached_stats[1]
                    },
                    'three_days': {
                        'new_high': cached_stats[2],
                        'new_low': cached_stats[3]
                    },
                    'seven_days': {
                        'new_high': cached_stats[4],
                        'new_low': cached_stats[5]
                    }
                },
                'from_cache': True
            })
        
        # 如果没有缓存，实时计算
        # 计算时间边界
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        three_days_ago = now - timedelta(days=3)
        seven_days_ago = now - timedelta(days=7)
        
        # 转换为字符串格式
        today_start_str = today_start.strftime('%Y-%m-%d %H:%M:%S')
        three_days_ago_str = three_days_ago.strftime('%Y-%m-%d %H:%M:%S')
        seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')
        
        # 当天统计
        cursor.execute('''
            SELECT event_type, COUNT(*) 
            FROM price_breakthrough_events 
            WHERE event_time >= ?
            GROUP BY event_type
        ''', (today_start_str,))
        today_stats = dict(cursor.fetchall())
        
        # 3天统计
        cursor.execute('''
            SELECT event_type, COUNT(*) 
            FROM price_breakthrough_events 
            WHERE event_time >= ?
            GROUP BY event_type
        ''', (three_days_ago_str,))
        three_days_stats = dict(cursor.fetchall())
        
        # 7天统计
        cursor.execute('''
            SELECT event_type, COUNT(*) 
            FROM price_breakthrough_events 
            WHERE event_time >= ?
            GROUP BY event_type
        ''', (seven_days_ago_str,))
        seven_days_stats = dict(cursor.fetchall())
        
        # 保存统计结果到数据库
        cursor.execute('''
            INSERT OR REPLACE INTO price_comparison_stats
            (stat_date, today_new_high, today_new_low, 
             three_days_new_high, three_days_new_low,
             seven_days_new_high, seven_days_new_low, record_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            today_date,
            today_stats.get('new_high', 0),
            today_stats.get('new_low', 0),
            three_days_stats.get('new_high', 0),
            three_days_stats.get('new_low', 0),
            seven_days_stats.get('new_high', 0),
            seven_days_stats.get('new_low', 0),
            now.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'today': {
                    'new_high': today_stats.get('new_high', 0),
                    'new_low': today_stats.get('new_low', 0)
                },
                'three_days': {
                    'new_high': three_days_stats.get('new_high', 0),
                    'new_low': three_days_stats.get('new_low', 0)
                },
                'seven_days': {
                    'new_high': seven_days_stats.get('new_high', 0),
                    'new_low': seven_days_stats.get('new_low', 0)
                }
            },
            'from_cache': False
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/price-comparison/breakthrough-logs')
def api_breakthrough_logs():
    """获取创新高/低详细日志
    
    参数:
    - limit: 返回记录数量，默认50
    - days: 查询最近N天的记录，默认7天
    - coin: 筛选特定币种
    - type: 筛选类型 (new_high/new_low)
    
    返回:
    - 时间、币名、事件类型(创新高/创新低)、价格、之前极值价格
    """
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # 获取参数
        limit = request.args.get('limit', 50, type=int)
        days = request.args.get('days', 7, type=int)
        coin_filter = request.args.get('coin', None)
        type_filter = request.args.get('type', None)
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 构建查询
        query = '''
            SELECT symbol, event_type, price, event_time
            FROM price_breakthrough_events
            WHERE 1=1
        '''
        params = []
        
        # 时间过滤
        if days > 0:
            beijing_tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(beijing_tz)
            cutoff_time = now - timedelta(days=days)
            cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
            query += ' AND event_time >= ?'
            params.append(cutoff_str)
        
        # 币种过滤
        if coin_filter:
            query += ' AND symbol = ?'
            params.append(coin_filter)
        
        # 类型过滤
        if type_filter in ['new_high', 'new_low']:
            query += ' AND event_type = ?'
            params.append(type_filter)
        
        query += ' ORDER BY event_time DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # 格式化结果
        logs = []
        for row in results:
            symbol, event_type, price, event_time = row
            # 从 symbol 提取币种名称
            coin_name = symbol.split('-')[0] if symbol else ''
            logs.append({
                'coin_name': coin_name,
                'symbol': symbol,
                'event_type': event_type,
                'event_label': '创新高' if event_type == 'new_high' else '创新低',
                'price': price,
                'event_time': event_time
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': logs,
            'count': len(logs),
            'filters': {
                'days': days,
                'coin': coin_filter,
                'type': type_filter,
                'limit': limit
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/price-comparison/update-ratios')
def api_update_price_ratios():
    """批量更新所有币种的价格占比
    
    从最新快照数据获取当前价格，计算并更新占比:
    - 最高价占比 = (当前价 / 最高价) × 100%
    - 最低价占比 = (当前价 / 最低价) × 100%
    """
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最新快照时间
        cursor.execute('SELECT MAX(snapshot_time) FROM crypto_coin_data')
        latest_time = cursor.fetchone()[0]
        
        if not latest_time:
            return jsonify({
                'success': False,
                'error': '没有找到快照数据'
            })
        
        # 获取最新快照的所有币种价格
        cursor.execute('''
            SELECT symbol, current_price
            FROM crypto_coin_data
            WHERE snapshot_time = ?
        ''', (latest_time,))
        
        current_prices = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 获取所有币种的最高价和最低价
        cursor.execute('''
            SELECT symbol, highest_price, lowest_price
            FROM price_baseline
        ''')
        
        from datetime import datetime
        import pytz
        beijing_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        updated_count = 0
        update_details = []
        
        for row in cursor.fetchall():
            coin_name, highest_price, lowest_price = row
            
            # 查找当前价格
            current_price = current_prices.get(coin_name)
            
            if current_price is not None and current_price > 0:
                # 计算占比
                highest_ratio = round((current_price / highest_price) * 100, 2) if highest_price > 0 else 0
                lowest_ratio = round((current_price / lowest_price) * 100, 2) if lowest_price > 0 else 0
                
                # 更新数据库
                cursor.execute('''
                    UPDATE price_baseline
                    SET highest_ratio = ?,
                        lowest_ratio = ?,
                        last_update_time = ?
                    WHERE symbol = ?
                ''', (highest_ratio, lowest_ratio, current_time, coin_name))
                
                updated_count += 1
                update_details.append({
                    'coin_name': coin_name,
                    'current_price': current_price,
                    'highest_ratio': highest_ratio,
                    'lowest_ratio': lowest_ratio
                })
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功更新 {updated_count} 个币种的占比',
            'snapshot_time': latest_time,
            'updated_count': updated_count,
            'details': update_details[:10]  # 只返回前10个作为示例
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/monitor/data-collection')
def api_monitor_data_collection():
    """监控数据采集状态"""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
        # 获取最新快照时间
        cursor.execute('SELECT MAX(snapshot_time) FROM crypto_snapshots')
        latest_snapshot = cursor.fetchone()[0]
        
        if not latest_snapshot:
            return jsonify({
                'success': False,
                'error': '数据库中没有任何快照数据',
                'status': 'no_data'
            })
        
        # 计算时间差
        latest_time = datetime.strptime(latest_snapshot, '%Y-%m-%d %H:%M:%S')
        latest_time = beijing_tz.localize(latest_time)
        time_diff_minutes = (now - latest_time).total_seconds() / 60
        
        # 获取今天的采集次数
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_start_str = today_start.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT COUNT(*) FROM crypto_snapshots 
            WHERE snapshot_time >= ?
        ''', (today_start_str,))
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        # 判断状态
        status = 'normal'
        message = '数据采集正常'
        alert_level = 'success'
        
        if time_diff_minutes > 20:
            status = 'critical'
            message = f'严重: 已经 {time_diff_minutes:.1f} 分钟没有新数据'
            alert_level = 'danger'
        elif time_diff_minutes > 15:
            status = 'warning'
            message = f'警告: 已经 {time_diff_minutes:.1f} 分钟没有新数据'
            alert_level = 'warning'
        
        # 计算预期采集次数（每10分钟一次）
        expected_count = int((now.hour * 60 + now.minute) / 10)
        
        return jsonify({
            'success': True,
            'status': status,
            'message': message,
            'alert_level': alert_level,
            'data': {
                'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'latest_snapshot': latest_snapshot,
                'time_diff_minutes': round(time_diff_minutes, 1),
                'today_count': today_count,
                'expected_count': expected_count,
                'collection_rate': round((today_count / expected_count * 100) if expected_count > 0 else 0, 1)
            }
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/monitor')
def monitor_page():
    """数据采集监控页面（增强版）- 支持执行日志、开关控制、刷新间隔"""
    return render_template('unified_monitor_enhanced.html')

@app.route('/monitor-old')
def monitor_page_old():
    """原始监控页面（旧版）"""
    return render_template('monitor.html')

@app.route('/star-system')
def star_system_page():
    """星星系统页面"""
    return render_template('star_system.html')

@app.route('/api/star-system/data')
def api_star_system_data():
    """获取星星系统所有指标数据"""
    try:
        import sys
        sys.path.insert(0, '/home/user/webapp')
        from star_system import calculate_star_system
        from datetime import datetime, timedelta
        import pytz
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        beijing_tz = pytz.timezone('Asia/Shanghai')
        
        # 获取最新快照数据
        cursor.execute('''
            SELECT rush_up, rush_down, diff, count, snapshot_time
            FROM crypto_snapshots
            ORDER BY snapshot_date DESC, snapshot_time DESC
            LIMIT 1
        ''')
        snapshot = cursor.fetchone()
        
        if not snapshot:
            return jsonify({'success': False, 'error': '暂无快照数据'})
        
        rush_up, rush_down, diff, count, snapshot_time = snapshot
        
        # 确保数值不为None
        rush_up = rush_up if rush_up is not None else 0
        rush_down = rush_down if rush_down is not None else 0
        diff = diff if diff is not None else 0
        count = count if count is not None else 0
        
        # 获取全网持仓量（从恐慌清洗指数表）
        cursor.execute('''
            SELECT total_position
            FROM panic_wash_index
            ORDER BY record_time DESC
            LIMIT 1
        ''')
        holdings_row = cursor.fetchone()
        holdings = holdings_row[0] if holdings_row and holdings_row[0] is not None else 10000000000  # 默认100亿（元）
        
        # 获取做多做空信号（从交易信号表）
        cursor.execute('''
            SELECT long_signals, short_signals
            FROM trading_signals
            ORDER BY record_time DESC
            LIMIT 1
        ''')
        signals_row = cursor.fetchone()
        long_signals = signals_row[0] if signals_row and signals_row[0] is not None else 0
        short_signals = signals_row[1] if signals_row and signals_row[1] is not None else 0
        
        # 获取今日创新高新低次数
        today_start = datetime.now(beijing_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        today_start_str = today_start.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT event_type, COUNT(*) 
            FROM price_breakthrough_events 
            WHERE event_time >= ?
            GROUP BY event_type
        ''', (today_start_str,))
        today_breakthrough = dict(cursor.fetchall())
        new_high_today = today_breakthrough.get('new_high', 0)
        new_low_today = today_breakthrough.get('new_low', 0)
        
        # 获取币种统计数据（从最新快照的详细数据）
        cursor.execute('''
            SELECT symbol, rush_up, rush_down, priority_level
            FROM crypto_coin_data
            WHERE snapshot_time = ?
        ''', (snapshot_time,))
        coin_data = cursor.fetchall()
        
        # 统计特殊情况并记录具体币种
        only_rush_up_coins = [c[0] for c in coin_data if c[1] > 0 and c[2] == 0]
        only_rush_up_count = len(only_rush_up_coins)
        
        rush_up_gt_down_coins = [c[0] for c in coin_data if c[1] > c[2]]
        rush_up_gt_down_count = len(rush_up_gt_down_coins)
        
        only_rush_down_coins = [c[0] for c in coin_data if c[1] == 0 and c[2] > 0]
        only_rush_down_count = len(only_rush_down_coins)
        
        rush_down_gt_up_coins = [c[0] for c in coin_data if c[2] > c[1]]
        rush_down_gt_up_count = len(rush_down_gt_up_coins)
        
        # 优先级≥4 means 等级1,2,3,4 (priority_level values: '等级1', '等级2', etc.)
        priority_high_coins = [c[0] for c in coin_data if c[3] in ['等级1', '等级2', '等级3', '等级4']]
        priority_high_count = len(priority_high_coins)
        
        # ========== 新增功能3: 位置系统平均位置（在conn.close()之前查询） ==========
        try:
            # 计算48小时前的北京时间
            hours_ago_48 = datetime.now(beijing_tz) - timedelta(hours=48)
            hours_ago_48_str = hours_ago_48.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                SELECT 
                    AVG(position_4h) as avg_4h,
                    AVG(position_12h) as avg_12h,
                    AVG(position_24h) as avg_24h,
                    AVG(position_48h) as avg_48h
                FROM position_system
                WHERE record_time >= ?
            """, (hours_ago_48_str,))
            pos_row = cursor.fetchone()
            
            position_avg = {
                '4h': round(pos_row[0], 2) if pos_row and pos_row[0] else 0,
                '12h': round(pos_row[1], 2) if pos_row and pos_row[1] else 0,
                '24h': round(pos_row[2], 2) if pos_row and pos_row[2] else 0,
                '48h': round(pos_row[3], 2) if pos_row and pos_row[3] else 0
            }
        except Exception as e:
            position_avg = {'4h': 0, '12h': 0, '24h': 0, '48h': 0}
            print(f"位置系统平均位置查询错误: {e}")
        
        # ========== 新增功能4: 创新高/创新低统计（在conn.close()之前查询） ==========
        try:
            # 当天统计（今天0点到现在）
            today_start = datetime.now(beijing_tz).replace(hour=0, minute=0, second=0, microsecond=0)
            today_start_str = today_start.strftime('%Y-%m-%d %H:%M:%S')
            
            # 3天统计
            three_days_ago = datetime.now(beijing_tz) - timedelta(days=3)
            three_days_ago_str = three_days_ago.strftime('%Y-%m-%d %H:%M:%S')
            
            # 7天统计
            seven_days_ago = datetime.now(beijing_tz) - timedelta(days=7)
            seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')
            
            # 查询当天创新高/创新低
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN event_type = 'new_high' THEN 1 ELSE 0 END) as today_high,
                    SUM(CASE WHEN event_type = 'new_low' THEN 1 ELSE 0 END) as today_low
                FROM price_breakthrough_events
                WHERE event_time >= ?
            """, (today_start_str,))
            today_bt = cursor.fetchone()
            
            # 查询3天创新高/创新低
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN event_type = 'new_high' THEN 1 ELSE 0 END) as three_days_high,
                    SUM(CASE WHEN event_type = 'new_low' THEN 1 ELSE 0 END) as three_days_low
                FROM price_breakthrough_events
                WHERE event_time >= ?
            """, (three_days_ago_str,))
            three_days_bt = cursor.fetchone()
            
            # 查询7天创新高/创新低
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN event_type = 'new_high' THEN 1 ELSE 0 END) as seven_days_high,
                    SUM(CASE WHEN event_type = 'new_low' THEN 1 ELSE 0 END) as seven_days_low
                FROM price_breakthrough_events
                WHERE event_time >= ?
            """, (seven_days_ago_str,))
            seven_days_bt = cursor.fetchone()
            
            breakthrough_stats = {
                'today': {
                    'new_high': today_bt[0] if today_bt and today_bt[0] else 0,
                    'new_low': today_bt[1] if today_bt and today_bt[1] else 0
                },
                'three_days': {
                    'new_high': three_days_bt[0] if three_days_bt and three_days_bt[0] else 0,
                    'new_low': three_days_bt[1] if three_days_bt and three_days_bt[1] else 0
                },
                'seven_days': {
                    'new_high': seven_days_bt[0] if seven_days_bt and seven_days_bt[0] else 0,
                    'new_low': seven_days_bt[1] if seven_days_bt and seven_days_bt[1] else 0
                }
            }
        except Exception as e:
            breakthrough_stats = {
                'today': {'new_high': 0, 'new_low': 0},
                'three_days': {'new_high': 0, 'new_low': 0},
                'seven_days': {'new_high': 0, 'new_low': 0}
            }
            print(f"创新高/创新低统计查询错误: {e}")
        
        conn.close()
        
        # 准备数据给星星系统计算
        data = {
            'rush_up': rush_up,
            'rush_down': rush_down,
            'diff': diff,
            'holdings': holdings,
            'long_signals': long_signals,
            'short_signals': short_signals,
            'only_rush_up_count': only_rush_up_count,
            'rush_up_gt_down_count': rush_up_gt_down_count,
            'priority_high_count': priority_high_count,
            'only_rush_down_count': only_rush_down_count,
            'rush_down_gt_up_count': rush_down_gt_up_count,
            'new_low_today': new_low_today,
            'new_high_today': new_high_today,
            'count': count,
            'snapshot_time': snapshot_time
        }
        
        # 计算星星系统
        results = calculate_star_system(data)
        
        # 保存到历史记录表（每次调用API时保存）
        try:
            import json as json_lib
            cursor.execute('''
                INSERT INTO star_system_history 
                (timestamp, total_stars, solid_stars, hollow_stars, solid_percentage, hollow_percentage, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot_time,
                results.get('total_stars', 0),
                results.get('solid_stars', 0),
                results.get('hollow_stars', 0),
                results.get('solid_percentage', 0),
                results.get('hollow_percentage', 0),
                json_lib.dumps(results, ensure_ascii=False)
            ))
            conn.commit()
        except Exception as save_err:
            print(f"保存历史数据失败: {save_err}")
        
        # 添加币种列表到结果中
        coin_lists = {
            'only_rush_up_coins': only_rush_up_coins,
            'rush_up_gt_down_coins': rush_up_gt_down_coins,
            'priority_high_coins': priority_high_coins,
            'only_rush_down_coins': only_rush_down_coins,
            'rush_down_gt_up_coins': rush_down_gt_up_coins
        }
        
        # ========== 新增功能1: V1/V2币种统计 ==========
        try:
            conn_v1v2 = sqlite3.connect('v1v2_data.db')
            cursor_v1v2 = conn_v1v2.cursor()
            
            coins_list = ['BTC', 'ETH', 'XRP', 'SOL', 'BNB', 'LTC', 'DOGE', 'SUI', 'TRX', 'TON', 
                         'ETC', 'BCH', 'HBAR', 'XLM', 'FIL', 'ADA', 'LINK', 'CRO', 'DOT', 'UNI',
                         'NEAR', 'APT', 'CFX', 'CRV', 'STX', 'LDO', 'TAO', 'AAVE']
            
            v1_coins_list = []
            v2_coins_list = []
            
            for coin in coins_list:
                try:
                    cursor_v1v2.execute(f"""
                        SELECT level FROM volume_{coin.lower()}
                        ORDER BY id DESC LIMIT 1
                    """)
                    row = cursor_v1v2.fetchone()
                    if row and row[0] == 'V1':
                        v1_coins_list.append(coin)
                    elif row and row[0] == 'V2':
                        v2_coins_list.append(coin)
                except:
                    pass
            
            conn_v1v2.close()
        except:
            v1_coins_list = []
            v2_coins_list = []
        
        # ========== 新增功能2: 1分钟涨跌速预警统计 ==========
        try:
            conn_ps = sqlite3.connect('price_speed_data.db')
            cursor_ps = conn_ps.cursor()
            
            # 获取各类型预警的币种
            cursor_ps.execute("""
                SELECT alert_type, symbol
                FROM latest_price_speed
                WHERE alert_type != 'NORMAL'
            """)
            
            alert_coins = {
                'super_strong_up': [],
                'very_strong_up': [],
                'strong_up': [],
                'general_up': [],
                'super_strong_down': [],
                'very_strong_down': [],
                'strong_down': [],
                'general_down': []
            }
            
            for alert_type, symbol in cursor_ps.fetchall():
                if alert_type == 'SUPER_STRONG_UP':
                    alert_coins['super_strong_up'].append(symbol)
                elif alert_type == 'VERY_STRONG_UP':
                    alert_coins['very_strong_up'].append(symbol)
                elif alert_type == 'STRONG_UP':
                    alert_coins['strong_up'].append(symbol)
                elif alert_type == 'GENERAL_UP':
                    alert_coins['general_up'].append(symbol)
                elif alert_type == 'SUPER_STRONG_DOWN':
                    alert_coins['super_strong_down'].append(symbol)
                elif alert_type == 'VERY_STRONG_DOWN':
                    alert_coins['very_strong_down'].append(symbol)
                elif alert_type == 'STRONG_DOWN':
                    alert_coins['strong_down'].append(symbol)
                elif alert_type == 'GENERAL_DOWN':
                    alert_coins['general_down'].append(symbol)
            
            conn_ps.close()
        except:
            alert_coins = {
                'super_strong_up': [],
                'very_strong_up': [],
                'strong_up': [],
                'general_up': [],
                'super_strong_down': [],
                'very_strong_down': [],
                'strong_down': [],
                'general_down': []
            }
        
        return jsonify({
            'success': True,
            'data': results,
            'raw_data': data,
            'coin_lists': coin_lists,
            'update_time': snapshot_time,
            # 新增数据
            'v1v2_data': {
                'v1_coins': v1_coins_list,
                'v1_count': len(v1_coins_list),
                'v2_coins': v2_coins_list,
                'v2_count': len(v2_coins_list)
            },
            'price_speed_alerts': {
                'up': {
                    'super_strong': {'count': len(alert_coins['super_strong_up']), 'coins': alert_coins['super_strong_up']},
                    'very_strong': {'count': len(alert_coins['very_strong_up']), 'coins': alert_coins['very_strong_up']},
                    'strong': {'count': len(alert_coins['strong_up']), 'coins': alert_coins['strong_up']},
                    'general': {'count': len(alert_coins['general_up']), 'coins': alert_coins['general_up']}
                },
                'down': {
                    'super_strong': {'count': len(alert_coins['super_strong_down']), 'coins': alert_coins['super_strong_down']},
                    'very_strong': {'count': len(alert_coins['very_strong_down']), 'coins': alert_coins['very_strong_down']},
                    'strong': {'count': len(alert_coins['strong_down']), 'coins': alert_coins['strong_down']},
                    'general': {'count': len(alert_coins['general_down']), 'coins': alert_coins['general_down']}
                }
            },
            'position_avg': position_avg,
            'breakthrough_stats': breakthrough_stats
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

# ==================== 星星系统历史数据 API ====================
@app.route('/api/star-system/history')
def api_star_system_history():
    """获取星星系统历史数据"""
    try:
        date = request.args.get('date')  # 格式: YYYY-MM-DD
        limit = int(request.args.get('limit', 100))
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        if date:
            # 查询指定日期的数据
            start_time = f"{date} 00:00:00"
            end_time = f"{date} 23:59:59"
            cursor.execute('''
                SELECT id, timestamp, total_stars, solid_stars, hollow_stars, 
                       solid_percentage, hollow_percentage, raw_data
                FROM star_system_history
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (start_time, end_time, limit))
        else:
            # 查询最近的记录
            cursor.execute('''
                SELECT id, timestamp, total_stars, solid_stars, hollow_stars, 
                       solid_percentage, hollow_percentage, raw_data
                FROM star_system_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        
        history_data = []
        for row in rows:
            try:
                import json as json_lib
                raw_data = json_lib.loads(row[7]) if row[7] else {}
            except:
                raw_data = {}
            
            history_data.append({
                'id': row[0],
                'timestamp': row[1],
                'total_stars': row[2],
                'solid_stars': row[3],
                'hollow_stars': row[4],
                'solid_percentage': row[5],
                'hollow_percentage': row[6],
                'details': raw_data
            })
        
        # 获取可用日期列表
        cursor.execute('''
            SELECT DISTINCT DATE(timestamp) as date
            FROM star_system_history
            ORDER BY date DESC
            LIMIT 30
        ''')
        available_dates = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': history_data,
            'available_dates': available_dates,
            'total_records': len(history_data)
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

# ==================== 数据采集监控 API ====================
@app.route('/api/monitor/status')
def api_monitor_status():
    """获取数据采集监控状态"""
    import subprocess
    try:
        result = subprocess.run(
            ['python3', 'monitor_data_collection.py', 'status'],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=10
        )
        status = json.loads(result.stdout)
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/monitor/history')
def api_monitor_history():
    """获取采集历史"""
    import subprocess
    try:
        hours = request.args.get('hours', '2')
        result = subprocess.run(
            ['python3', 'monitor_data_collection.py', 'history', hours],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=10
        )
        history = json.loads(result.stdout)
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/monitor/trigger', methods=['POST'])
def api_monitor_trigger():
    """手动触发数据采集"""
    import subprocess
    try:
        result = subprocess.run(
            ['python3', 'monitor_data_collection.py', 'force'],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        collection_result = json.loads(result.stdout) if result.stdout else {}
        return jsonify({
            'success': result.returncode == 0,
            'result': collection_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/monitor/check', methods=['POST'])
def api_monitor_check():
    """检查并自动恢复数据采集"""
    import subprocess
    try:
        result = subprocess.run(
            ['python3', 'monitor_data_collection.py', 'check'],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        check_result = json.loads(result.stdout) if result.stdout else {}
        return jsonify({
            'success': True,
            'result': check_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==================== 多模块监控 API ====================
@app.route('/api/monitor/all-modules')
def api_monitor_all_modules():
    """获取所有模块监控状态"""
    import subprocess
    try:
        result = subprocess.run(
            ['python3', 'multi_module_monitor.py', 'status'],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=10
        )
        # 从stdout提取JSON部分（跳过前面的文本输出）
        output = result.stdout
        # 找到JSON开始的位置
        json_start = output.find('{')
        if json_start >= 0:
            json_str = output[json_start:]
            statuses = json.loads(json_str)
            return jsonify({
                'success': True,
                'modules': statuses
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No JSON output found'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/monitor/check-all', methods=['POST'])
def api_monitor_check_all():
    """检查并自动恢复所有模块"""
    import subprocess
    try:
        result = subprocess.run(
            ['python3', 'multi_module_monitor.py', 'check', '--silent'],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时（多个模块可能需要更长时间）
        )
        check_result = json.loads(result.stdout) if result.stdout else {}
        return jsonify({
            'success': True,
            'result': check_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/monitor/force-update/<module_key>', methods=['POST'])
def api_monitor_force_update(module_key):
    """强制更新指定模块"""
    import subprocess
    try:
        result = subprocess.run(
            ['python3', 'multi_module_monitor.py', 'force', module_key],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        update_result = json.loads(result.stdout) if result.stdout else {}
        return jsonify({
            'success': result.returncode == 0,
            'result': update_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==================== 得分系统 API ====================
from score_calculator import ScoreCalculator

@app.route('/control-center')
def control_center_page():
    """深度图得分页面（控制中心）"""
    return render_template('control_center.html')

@app.route('/depth-score')
def depth_score_page():
    """深度图得分页面"""
    return render_template('depth_score.html')

@app.route('/depth-chart')
def depth_chart_page():
    """深度图可视化页面"""
    return render_template('depth_chart.html')

@app.route('/score-overview')
def score_overview_page():
    """平均分页面"""
    return render_template('score_overview.html')

@app.route('/crypto-index')
def crypto_index_page():
    """OKEX加密指数页面"""
    return render_template('crypto_index.html')

@app.route('/api/depth-scores')
def api_depth_scores():
    """获取深度得分数据"""
    try:
        timeframe = int(request.args.get('timeframe', 24))
        limit = int(request.args.get('limit', 50))
        
        calculator = ScoreCalculator()
        scores = calculator.calculate_all_coins_depth_scores(timeframe, limit)
        
        # 计算平均分
        avg_score = sum(s['score'] for s in scores) / len(scores) if scores else 0
        
        return jsonify({
            'success': True,
            'data': {
                'scores': scores,
                'total_coins': len(scores),
                'average_score': round(avg_score, 2),
                'timeframe': f'{timeframe}h'
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/depth-chart-data')
def api_depth_chart_data():
    """获取深度图表数据"""
    try:
        timeframe = int(request.args.get('timeframe', 24))
        top_n = int(request.args.get('top_n', 20))
        
        calculator = ScoreCalculator()
        chart_data = calculator.get_depth_chart_data(timeframe, top_n)
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/market-average-score')
def api_market_average_score():
    """获取市场平均得分"""
    try:
        timeframe = int(request.args.get('timeframe', 24))
        
        calculator = ScoreCalculator()
        market_score = calculator.calculate_average_market_score(timeframe)
        
        return jsonify({
            'success': True,
            'data': market_score
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/okex-crypto-index')
def api_okex_crypto_index():
    """获取OKEX加密货币指数"""
    try:
        calculator = ScoreCalculator()
        index_data = calculator.calculate_okex_crypto_index()
        
        return jsonify({
            'success': True,
            'data': index_data
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

# ============================================================================
# OKEX加密指数页面专用API端点
# ============================================================================

@app.route('/api/index/start', methods=['POST'])
def api_index_start():
    """启动指数监控"""
    return jsonify({
        'success': True,
        'message': '指数监控已启动'
    })

@app.route('/api/index/current')
def api_index_current():
    """获取当前指数值 - 基于27币种加权指数"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最新的K线数据
        cursor.execute('''
            SELECT timestamp, index_value, open_price, high_price, low_price, close_price
            FROM crypto_index_klines
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        
        # 获取有多少个币种有有效的基准价格
        cursor.execute('SELECT COUNT(*) FROM crypto_index_base_prices WHERE base_price > 0')
        valid_components = cursor.fetchone()[0]
        
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'message': '暂无指数数据，请等待数据采集'
            })
        
        current_value = row[1]
        base_value = 1000.00
        change = current_value - base_value
        change_percent = (change / base_value) * 100
        
        # 获取BTC的4个周期平均位置数据
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT position_4h, position_12h, position_24h, position_48h
            FROM position_system
            WHERE symbol = 'BTC-USDT-SWAP'
            ORDER BY record_time DESC
            LIMIT 1
        ''')
        position_row = cursor.fetchone()
        conn.close()
        
        # 准备周期位置数据
        period_positions = {}
        if position_row:
            period_positions = {
                'position_4h': round(position_row[0], 2) if position_row[0] else None,
                'position_12h': round(position_row[1], 2) if position_row[1] else None,
                'position_24h': round(position_row[2], 2) if position_row[2] else None,
                'position_48h': round(position_row[3], 2) if position_row[3] else None
            }
        
        return jsonify({
            'success': True,
            'data': {
                'value': current_value,
                'base_value': base_value,
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'valid_components': valid_components,
                'timestamp': row[0],
                'open': row[2],
                'high': row[3],
                'low': row[4],
                'close': row[5],
                'period_positions': period_positions
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'获取指数失败: {str(e)}',
            'traceback': traceback.format_exc()
        })

@app.route('/api/index/components')
def api_index_components():
    """获取成分详情 - 27币种权重明细"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取所有币种的基准价格和权重
        cursor.execute('''
            SELECT coin_id, base_price, weight
            FROM crypto_index_base_prices
            ORDER BY weight DESC, coin_id
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # 币种名称映射
        coin_name_map = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'ripple': 'XRP',
            'binancecoin': 'BNB', 'solana': 'SOL', 'litecoin': 'LTC',
            'dogecoin': 'DOGE', 'sui': 'SUI', 'tron': 'TRX',
            'the-open-network': 'TON', 'ethereum-classic': 'ETC',
            'bitcoin-cash': 'BCH', 'hedera-hashgraph': 'HBAR',
            'stellar': 'XLM', 'filecoin': 'FIL', 'chainlink': 'LINK',
            'crypto-com-chain': 'CRO', 'polkadot': 'DOT', 'aave': 'AAVE',
            'uniswap': 'UNI', 'near': 'NEAR', 'aptos': 'APT',
            'conflux-token': 'CFX', 'curve-dao-token': 'CRV',
            'stacks': 'STX', 'lido-dao': 'LDO', 'bittensor': 'TAO'
        }
        
        # 获取当前价格（从CoinGecko）- 简化版，仅用基准价格模拟
        import requests
        try:
            coin_ids = ','.join([r[0] for r in rows])
            response = requests.get(
                'https://api.coingecko.com/api/v3/simple/price',
                params={'ids': coin_ids, 'vs_currencies': 'usd'},
                timeout=5
            )
            current_prices = response.json() if response.status_code == 200 else {}
        except:
            current_prices = {}
        
        # 构建成分数据（以对象形式返回，key为币种symbol）
        components = {}
        for row in rows:
            coin_id = row[0]
            symbol = coin_name_map.get(coin_id, coin_id.upper())
            base_price = row[1]
            weight = row[2]
            
            # 获取当前价格
            current_price = current_prices.get(coin_id, {}).get('usd', base_price)
            price_change = ((current_price - base_price) / base_price * 100) if base_price > 0 else 0
            weighted_contribution = price_change * weight
            
            components[symbol] = {
                'name': symbol,
                'coin_id': coin_id,
                'price': current_price,
                'base_price': base_price,
                'weight': weight,
                'weight_percent': f"{weight*100:.2f}%",
                'change_percent': round(price_change, 2),
                'weighted_contribution': round(weighted_contribution, 3)
            }
        
        return jsonify({
            'success': True,
            'total_coins': len(components),
            'data': components
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'获取成分失败: {str(e)}',
            'traceback': traceback.format_exc()
        })

@app.route('/test-refresh')
def test_refresh():
    """测试刷新页面 - 用于验证缓存问题"""
    return render_template('test_refresh.html')

@app.route('/test-btc-eth')
def test_btc_eth():
    """测试BTC和ETH数据显示"""
    return render_template('test_btc_eth.html')

@app.route('/api/index/history')
def api_index_history():
    """获取历史数据 - 基于K线数据，支持分页（12小时一页）"""
    try:
        page = int(request.args.get('page', 1))  # 当前页，默认第1页
        hours_per_page = 12  # 每页12小时
        records_per_hour = 60  # 每小时60条（1分钟K线）
        page_size = hours_per_page * records_per_hour  # 每页720条
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取总记录数
        cursor.execute('SELECT COUNT(*) FROM crypto_index_klines')
        total_records = cursor.fetchone()[0]
        
        # 计算总页数
        total_pages = (total_records + page_size - 1) // page_size
        
        # 确保页码有效
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
        
        # 计算偏移量（从最新数据开始倒数）
        offset = (page - 1) * page_size
        
        # 获取当前页的K线数据
        cursor.execute('''
            SELECT timestamp, index_value, close_price
            FROM crypto_index_klines
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (page_size, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({
                'success': False,
                'message': '暂无历史数据'
            })
        
        history = []
        base_value = 1000.00
        for row in rows:
            index_value = row[1]
            change_percent = ((index_value - base_value) / base_value * 100)
            history.append({
                'time': row[0],
                'value': index_value,
                'close': row[2],
                'change_percent': round(change_percent, 2)
            })
        
        history.reverse()  # 时间正序
        
        return jsonify({
            'success': True,
            'total': len(history),
            'total_records': total_records,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size,
            'data': history
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'获取历史失败: {str(e)}',
            'traceback': traceback.format_exc()
        })

@app.route('/api/index/klines')
def api_index_klines():
    """获取K线数据 - 5分钟K线"""
    try:
        limit = int(request.args.get('limit', 100))
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最近的K线数据
        cursor.execute('''
            SELECT timestamp, open_price, high_price, low_price, close_price, index_value
            FROM crypto_index_klines
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({
                'success': False,
                'message': '暂无K线数据，请等待数据采集'
            })
        
        klines = []
        for row in rows:
            klines.append({
                'timestamp': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'value': row[5]
            })
        
        klines.reverse()  # 时间正序
        
        return jsonify({
            'success': True,
            'total': len(klines),
            'interval': '5m',
            'data': klines
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'获取K线失败: {str(e)}',
            'traceback': traceback.format_exc()
        })

# ==================== 位置系统 API ====================

@app.route('/position-system')
def position_system():
    """位置系统页面"""
    return render_template('position_system.html')

@app.route('/api/position/latest')
def api_position_latest():
    """获取最新位置数据"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最新的记录时间
        cursor.execute('SELECT MAX(record_time) FROM position_system')
        latest_time = cursor.fetchone()[0]
        
        if not latest_time:
            return jsonify({
                'success': False,
                'message': '暂无数据'
            })
        
        # 获取该时间的所有币种数据
        cursor.execute('''
            SELECT symbol, current_price,
                   position_4h, position_12h, position_24h, position_48h,
                   high_4h, low_4h, high_12h, low_12h, high_24h, low_24h, high_48h, low_48h
            FROM position_system
            WHERE record_time = ?
            ORDER BY symbol
        ''', (latest_time,))
        
        rows = cursor.fetchall()
        
        # 构造返回数据
        data_list = []
        symbol_set = set()
        for row in rows:
            symbol_set.add(row[0])
            data_list.append({
                'symbol': row[0],
                'current_price': row[1],
                'position_4h': row[2],
                'position_12h': row[3],
                'position_24h': row[4],
                'position_48h': row[5],
                'high_4h': row[6],
                'low_4h': row[7],
                'high_12h': row[8],
                'low_12h': row[9],
                'high_24h': row[10],
                'low_24h': row[11],
                'high_48h': row[12],
                'low_48h': row[13]
            })
        
        # 检查BTC和ETH是否存在，如果不存在则从最近记录中补充
        missing_coins = []
        if 'BTC-USDT-SWAP' not in symbol_set:
            missing_coins.append('BTC-USDT-SWAP')
        if 'ETH-USDT-SWAP' not in symbol_set:
            missing_coins.append('ETH-USDT-SWAP')
        
        if missing_coins:
            for coin in missing_coins:
                cursor.execute('''
                    SELECT symbol, current_price,
                           position_4h, position_12h, position_24h, position_48h,
                           high_4h, low_4h, high_12h, low_12h, high_24h, low_24h, high_48h, low_48h
                    FROM position_system
                    WHERE symbol = ?
                    ORDER BY record_time DESC
                    LIMIT 1
                ''', (coin,))
                coin_row = cursor.fetchone()
                if coin_row:
                    data_list.append({
                        'symbol': coin_row[0],
                        'current_price': coin_row[1],
                        'position_4h': coin_row[2],
                        'position_12h': coin_row[3],
                        'position_24h': coin_row[4],
                        'position_48h': coin_row[5],
                        'high_4h': coin_row[6],
                        'low_4h': coin_row[7],
                        'high_12h': coin_row[8],
                        'low_12h': coin_row[9],
                        'high_24h': coin_row[10],
                        'low_24h': coin_row[11],
                        'high_48h': coin_row[12],
                        'low_48h': coin_row[13]
                    })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'record_time': latest_time,
            'total_count': len(data_list),
            'data': data_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })

@app.route('/api/position/summary')
def api_position_summary():
    """获取位置统计摘要"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最新的记录时间
        cursor.execute('SELECT MAX(record_time) FROM position_system')
        latest_time = cursor.fetchone()[0]
        
        if not latest_time:
            return jsonify({
                'success': False,
                'message': '暂无数据'
            })
        
        # 统计各周期的平均位置
        cursor.execute('''
            SELECT 
                AVG(position_4h) as avg_4h,
                AVG(position_12h) as avg_12h,
                AVG(position_24h) as avg_24h,
                AVG(position_48h) as avg_48h,
                COUNT(*) as total_count
            FROM position_system
            WHERE record_time = ?
        ''', (latest_time,))
        
        row = cursor.fetchone()
        
        # 统计各区间的币种数量（以24h为例）
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN position_24h >= 80 THEN 1 ELSE 0 END) as high_zone,
                SUM(CASE WHEN position_24h >= 50 AND position_24h < 80 THEN 1 ELSE 0 END) as mid_high_zone,
                SUM(CASE WHEN position_24h >= 20 AND position_24h < 50 THEN 1 ELSE 0 END) as mid_low_zone,
                SUM(CASE WHEN position_24h < 20 THEN 1 ELSE 0 END) as low_zone
            FROM position_system
            WHERE record_time = ?
        ''', (latest_time,))
        
        zone_counts = cursor.fetchone()
        
        # 新增：统计各周期>=95%的币种数量
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN position_4h >= 95 THEN 1 ELSE 0 END) as count_4h_ge95,
                SUM(CASE WHEN position_12h >= 95 THEN 1 ELSE 0 END) as count_12h_ge95,
                SUM(CASE WHEN position_24h >= 95 THEN 1 ELSE 0 END) as count_24h_ge95,
                SUM(CASE WHEN position_48h >= 95 THEN 1 ELSE 0 END) as count_48h_ge95
            FROM position_system
            WHERE record_time = ?
        ''', (latest_time,))
        
        ge95_counts = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'record_time': latest_time,
            'averages': {
                '4h': round(row[0], 2) if row[0] else 0,
                '12h': round(row[1], 2) if row[1] else 0,
                '24h': round(row[2], 2) if row[2] else 0,
                '48h': round(row[3], 2) if row[3] else 0
            },
            'total_count': row[4],
            'zone_distribution_24h': {
                'high': zone_counts[0] or 0,      # 80-100%
                'mid_high': zone_counts[1] or 0,  # 50-80%
                'mid_low': zone_counts[2] or 0,   # 20-50%
                'low': zone_counts[3] or 0        # 0-20%
            },
            'high_position_counts': {
                '4h': ge95_counts[0] or 0,   # 4小时>=95%
                '12h': ge95_counts[1] or 0,  # 12小时>=95%
                '24h': ge95_counts[2] or 0,  # 24小时>=95%
                '48h': ge95_counts[3] or 0   # 48小时>=95%
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计失败: {str(e)}'
        })

@app.route('/api/position/history/<symbol>')
def api_position_history(symbol):
    """获取指定币种的历史位置数据"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最近24小时的数据
        cursor.execute('''
            SELECT record_time, current_price,
                   position_4h, position_12h, position_24h, position_48h
            FROM position_system
            WHERE symbol = ?
            ORDER BY record_time DESC
            LIMIT 288
        ''', (symbol,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'time': row[0],
                'price': row[1],
                '4h': row[2],
                '12h': row[3],
                '24h': row[4],
                '48h': row[5]
            })
        
        history.reverse()  # 时间正序
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'data': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取历史失败: {str(e)}'
        })

@app.route('/api/position/stats/latest')
def api_position_stats_latest():
    """获取最新的位置统计数据（低于1%的币种数量）"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最新的统计数据
        cursor.execute('''
            SELECT record_time, count_below_1_4h, count_below_1_12h, 
                   count_below_1_24h, count_below_1_48h, total_coins
            FROM position_system_stats
            ORDER BY record_time DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'message': '暂无统计数据'
            })
        
        return jsonify({
            'success': True,
            'record_time': row[0],
            'stats': {
                '4h': {'below_1': row[1], 'total': row[5]},
                '12h': {'below_1': row[2], 'total': row[5]},
                '24h': {'below_1': row[3], 'total': row[5]},
                '48h': {'below_1': row[4], 'total': row[5]}
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        })

@app.route('/api/position/stats/history')
def api_position_stats_history():
    """获取统计数据历史记录"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', default=100, type=int)
        start_time = request.args.get('start_time', default=None, type=str)
        end_time = request.args.get('end_time', default=None, type=str)
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 构建查询条件
        query = '''
            SELECT record_time, count_below_1_4h, count_below_1_12h, 
                   count_below_1_24h, count_below_1_48h, total_coins
            FROM position_system_stats
            WHERE 1=1
        '''
        params = []
        
        if start_time:
            query += ' AND record_time >= ?'
            params.append(start_time)
        
        if end_time:
            query += ' AND record_time <= ?'
            params.append(end_time)
        
        query += ' ORDER BY record_time DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'time': row[0],
                '4h': {'below_1': row[1], 'total': row[5]},
                '12h': {'below_1': row[2], 'total': row[5]},
                '24h': {'below_1': row[3], 'total': row[5]},
                '48h': {'below_1': row[4], 'total': row[5]}
            })
        
        history.reverse()  # 时间正序
        
        return jsonify({
            'success': True,
            'count': len(history),
            'data': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取历史统计失败: {str(e)}'
        })

@app.route('/v1v2-volume')
def v1v2_volume():
    """V1V2成交量系统页面"""
    return render_template('v1v2_volume.html')

@app.route('/v1v2-monitor')
def v1v2_monitor():
    """V1V2成交额监控页面"""
    return render_template('v1v2_monitor.html')

@app.route('/api/v1v2/latest')
def api_v1v2_latest():
    """获取所有币种的最新V1V2数据"""
    try:
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect('v1v2_data.db')
        cursor = conn.cursor()
        
        # 27个币种配置
        coins_config = {
            'BTC': {'v1': 200000, 'v2': 100000},
            'ETH': {'v1': 1300000, 'v2': 500000},
            'XRP': {'v1': 200000, 'v2': 87000},
            'SOL': {'v1': 351620, 'v2': 246380},
            'BNB': {'v1': 2388300, 'v2': 1737500},
            'LTC': {'v1': 50000, 'v2': 15000},
            'DOGE': {'v1': 150000, 'v2': 60000},
            'SUI': {'v1': 2000000, 'v2': 800000},
            'TRX': {'v1': 13280, 'v2': 6022},
            'TON': {'v1': 350000, 'v2': 200000},
            'ETC': {'v1': 12000, 'v2': 2000},
            'BCH': {'v1': 103500, 'v2': 50000},
            'HBAR': {'v1': 103500, 'v2': 40000},
            'XLM': {'v1': 103500, 'v2': 30000},
            'FIL': {'v1': 5003500, 'v2': 3700000},
            'ADA': {'v1': 67210, 'v2': 44230},
            'LINK': {'v1': 280000, 'v2': 200000},
            'CRO': {'v1': 100000, 'v2': 40000},
            'DOT': {'v1': 300000, 'v2': 250000},
            'UNI': {'v1': 140000, 'v2': 100000},
            'NEAR': {'v1': 100000, 'v2': 50000},
            'APT': {'v1': 300000, 'v2': 200000},
            'CFX': {'v1': 300000, 'v2': 250000},
            'CRV': {'v1': 1500000, 'v2': 1000000},
            'STX': {'v1': 50000, 'v2': 30000},
            'LDO': {'v1': 1000000, 'v2': 600000},
            'TAO': {'v1': 300000, 'v2': 180000}
        }
        
        result = []
        update_time = None
        
        for symbol, thresholds in coins_config.items():
            table_name = f'volume_{symbol.lower()}'
            
            try:
                # 获取最新一条记录（按ID降序，确保获取最新插入的数据）
                cursor.execute(f'''
                    SELECT volume, collect_time, level, timestamp
                    FROM {table_name}
                    ORDER BY id DESC
                    LIMIT 1
                ''')
                
                row = cursor.fetchone()
                
                if row:
                    result.append({
                        'symbol': symbol,
                        'volume': row[0],
                        'collect_time': row[1],
                        'level': row[2],
                        'v1': thresholds['v1'],
                        'v2': thresholds['v2']
                    })
                    
                    if not update_time:
                        update_time = row[1]
                        
            except sqlite3.OperationalError:
                # 表不存在,跳过
                continue
        
        conn.close()
        
        # 按级别排序: V1 > V2 > NONE
        level_order = {'V1': 0, 'V2': 1, 'NONE': 2}
        result.sort(key=lambda x: (level_order.get(x['level'], 3), -x['volume']))
        
        return jsonify({
            'success': True,
            'count': len(result),
            'data': result,
            'update_time': update_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })

@app.route('/v1v2-settings')
def v1v2_settings():
    """V1V2阈值设置页面"""
    return render_template('v1v2_settings.html')

@app.route('/api/v1v2/settings', methods=['GET', 'POST'])
def api_v1v2_settings():
    """获取或更新V1V2阈值设置"""
    import json
    import os
    
    SETTINGS_FILE = 'v1v2_settings.json'
    
    # 默认配置
    DEFAULT_SETTINGS = {
        'BTC': {'v1': 200000, 'v2': 100000},
        'ETH': {'v1': 1300000, 'v2': 500000},
        'XRP': {'v1': 200000, 'v2': 87000},
        'SOL': {'v1': 351620, 'v2': 246380},
        'BNB': {'v1': 2388300, 'v2': 1737500},
        'LTC': {'v1': 50000, 'v2': 15000},
        'DOGE': {'v1': 150000, 'v2': 60000},
        'SUI': {'v1': 2000000, 'v2': 800000},
        'TRX': {'v1': 13280, 'v2': 6022},
        'TON': {'v1': 350000, 'v2': 200000},
        'ETC': {'v1': 12000, 'v2': 2000},
        'BCH': {'v1': 103500, 'v2': 50000},
        'HBAR': {'v1': 103500, 'v2': 40000},
        'XLM': {'v1': 103500, 'v2': 30000},
        'FIL': {'v1': 5003500, 'v2': 3700000},
        'ADA': {'v1': 67210, 'v2': 44230},
        'LINK': {'v1': 280000, 'v2': 200000},
        'CRO': {'v1': 100000, 'v2': 40000},
        'DOT': {'v1': 300000, 'v2': 250000},
        'UNI': {'v1': 140000, 'v2': 100000},
        'NEAR': {'v1': 100000, 'v2': 50000},
        'APT': {'v1': 300000, 'v2': 200000},
        'CFX': {'v1': 300000, 'v2': 250000},
        'CRV': {'v1': 1500000, 'v2': 1000000},
        'STX': {'v1': 50000, 'v2': 30000},
        'LDO': {'v1': 1000000, 'v2': 600000},
        'TAO': {'v1': 300000, 'v2': 180000}
    }
    
    if request.method == 'GET':
        # 读取设置
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = DEFAULT_SETTINGS
                # 保存默认设置
                with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True,
                'settings': settings
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'读取设置失败: {str(e)}'
            })
    
    elif request.method == 'POST':
        # 更新设置
        try:
            data = request.get_json()
            new_settings = data.get('settings', {})
            
            # 验证数据
            for symbol, config in new_settings.items():
                if 'v1' not in config or 'v2' not in config:
                    return jsonify({
                        'success': False,
                        'message': f'币种 {symbol} 配置不完整'
                    })
                
                # 确保V1 > V2
                if config['v1'] <= config['v2']:
                    return jsonify({
                        'success': False,
                        'message': f'币种 {symbol}: V1阈值必须大于V2阈值'
                    })
            
            # 保存设置
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_settings, f, indent=2, ensure_ascii=False)
            
            # 触发采集器重新加载配置（通过创建标记文件）
            with open('.v1v2_settings_updated', 'w') as f:
                f.write(str(int(time.time())))
            
            return jsonify({
                'success': True,
                'message': '设置已保存，采集器将在下次采集时使用新配置'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'保存设置失败: {str(e)}'
            })

@app.route('/api/v1v2/statistics')
def api_v1v2_statistics():
    """获取V1V2信号统计数据（1h/3h/12h/1day/3day/7day）"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect('v1v2_data.db', timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
        cursor = conn.cursor()
        
        # 获取所有币种表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'volume_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 定义时间范围
        now = datetime.now()
        time_ranges = {
            '1h': now - timedelta(hours=1),
            '3h': now - timedelta(hours=3),
            '12h': now - timedelta(hours=12),
            '1day': now - timedelta(days=1),
            '3day': now - timedelta(days=3),
            '7day': now - timedelta(days=7)
        }
        
        statistics = []
        
        for table_name in tables:
            symbol = table_name.replace('volume_', '').upper()
            
            try:
                coin_stats = {
                    'symbol': symbol,
                    '1h': {'v1': 0, 'v2': 0, 'total': 0},
                    '3h': {'v1': 0, 'v2': 0, 'total': 0},
                    '12h': {'v1': 0, 'v2': 0, 'total': 0},
                    '1day': {'v1': 0, 'v2': 0, 'total': 0},
                    '3day': {'v1': 0, 'v2': 0, 'total': 0},
                    '7day': {'v1': 0, 'v2': 0, 'total': 0}
                }
                
                # 对每个时间范围进行统计
                for period, start_time in time_ranges.items():
                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 统计V1和V2的次数（只统计V1和V2）
                    cursor.execute(f"""
                        SELECT level, COUNT(*) 
                        FROM {table_name} 
                        WHERE collect_time >= ? AND level IN ('V1', 'V2')
                        GROUP BY level
                    """, (start_time_str,))
                    
                    counts = dict(cursor.fetchall())
                    v1_count = counts.get('V1', 0)
                    v2_count = counts.get('V2', 0)
                    
                    coin_stats[period]['v1'] = v1_count
                    coin_stats[period]['v2'] = v2_count
                    coin_stats[period]['total'] = v1_count + v2_count
                
                statistics.append(coin_stats)
                
            except sqlite3.OperationalError:
                # 表不存在或出错，跳过
                continue
        
        conn.close()
        
        # 按7天总信号数排序
        statistics.sort(key=lambda x: x['7day']['total'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'statistics': statistics,
                'update_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'total_coins': len(statistics)
            }
        })
        
    except Exception as e:
        import traceback
        print(f"❌ V1V2统计API错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500

@app.route('/price-speed-monitor')
def price_speed_monitor():
    """1分钟涨跌速监控页面"""
    return render_template('price_speed_monitor.html')

@app.route('/api/price-speed/latest')
def api_price_speed_latest():
    """获取所有币种的最新涨跌速数据"""
    try:
        import sqlite3
        from datetime import datetime
        import pytz
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        conn = sqlite3.connect('price_speed_data.db')
        cursor = conn.cursor()
        
        # 获取所有币种的最新数据
        cursor.execute('''
            SELECT symbol, current_price, previous_price, change_percent, 
                   alert_level, alert_type, timestamp
            FROM latest_price_speed
            ORDER BY symbol
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'symbol': row[0],
                'current_price': row[1],
                'previous_price': row[2],
                'change_percent': row[3],
                'alert_level': row[4],
                'alert_type': row[5],
                'timestamp': row[6]
            })
        
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data,
            'update_time': datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取涨跌速数据失败: {str(e)}',
            'data': []
        })

@app.route('/api/price-speed/history/<symbol>')
def api_price_speed_history(symbol):
    """获取指定币种的历史涨跌速数据"""
    try:
        import sqlite3
        
        # 获取查询参数
        limit = request.args.get('limit', 100, type=int)
        
        conn = sqlite3.connect('price_speed_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT current_price, previous_price, change_percent, 
                   alert_level, alert_type, timestamp
            FROM price_speed_alerts
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'current_price': row[0],
                'previous_price': row[1],
                'change_percent': row[2],
                'alert_level': row[3],
                'alert_type': row[4],
                'timestamp': row[5]
            })
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取历史数据失败: {str(e)}',
            'data': []
        })

# ============================================================================
# Google Drive TXT检测器 API
# ============================================================================

@app.route('/gdrive-detector')
def gdrive_detector_page():
    """Google Drive检测器页面"""
    return render_template('gdrive_detector.html')

@app.route('/test-gdrive-status')
def test_gdrive_status():
    """Google Drive状态测试页面"""
    return render_template('test_gdrive_status.html')

@app.route('/gdrive-detector-fresh')
def gdrive_detector_fresh():
    """Google Drive检测器页面（无缓存版本）"""
    import time
    return render_template('gdrive_detector_fresh.html', timestamp=int(time.time()))

@app.route('/opening-logic')
def opening_logic_page():
    """开仓逻辑系统页面"""
    from flask import make_response
    response = make_response(render_template('opening_logic.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/opening-logic/suggestion')
def opening_logic_suggestion():
    """获取开仓建议API"""
    try:
        from opening_logic import get_opening_suggestion
        result = get_opening_suggestion()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gdrive-detector/status')
def gdrive_detector_status():
    """获取Google Drive检测器状态"""
    try:
        import subprocess
        import re
        import requests
        from datetime import datetime
        import pytz
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
        # 检查检测器进程是否运行
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        detector_running = ('gdrive_txt_detector.py' in result.stdout or 
                          'gdrive_final_detector.py' in result.stdout or
                          'gdrive_smart_detector.py' in result.stdout)
        
        # 从数据库读取最新数据时间戳
        file_timestamp = None
        delay_minutes = None
        
        try:
            import sqlite3
            db_path = '/home/user/webapp/crypto_data.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT snapshot_time FROM crypto_snapshots ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                file_timestamp = result[0]
                # 计算延迟 - 数据库时间是北京时间
                try:
                    last_time = datetime.strptime(file_timestamp, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    last_time = datetime.strptime(file_timestamp, '%Y-%m-%d %H:%M:%S.%f')
                
                # 数据库存储的是北京时间，直接与北京时间比较
                last_time_beijing = beijing_tz.localize(last_time)
                delay_seconds = (now - last_time_beijing).total_seconds()
                delay_minutes = delay_seconds / 60
        except:
            pass
        
        # 读取日志获取检查次数
        check_count = 0
        last_check_time = None
        try:
            with open('/home/user/webapp/gdrive_final_detector.log', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if '检查 #' in line:
                        match = re.search(r'检查 #(\d+)', line)
                        if match:
                            check_count = int(match.group(1))
                    if re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line):
                        # 提取时间戳
                        match = re.search(r'(2025-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        if match:
                            last_check_time = match.group(1)
        except:
            pass
        
        # 从配置文件读取所有文件夹ID
        root_folder_odd = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"  # 默认值
        root_folder_even = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"  # 默认值
        folder_id = None  # 子账号文件夹ID（今日文件夹）
        
        try:
            import json
            config_file = '/home/user/webapp/daily_folder_config.json'
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 读取单数/双数父文件夹ID
                if 'root_folder_odd' in config:
                    root_folder_odd = config['root_folder_odd']
                if 'root_folder_even' in config:
                    root_folder_even = config['root_folder_even']
                # 🆕 读取子账号文件夹ID（今日文件夹）
                if 'folder_id' in config:
                    folder_id = config['folder_id']
        except:
            pass
        
        # 如果配置文件中没有子账号文件夹ID，尝试从日志读取
        if not folder_id:
            try:
                with open('/home/user/webapp/gdrive_final_detector.log', 'r') as f:
                    lines = f.readlines()
                    for line in reversed(lines[-100:]):  # 只看最近100行
                        # 提取文件夹ID（子账号）
                        if '今日文件夹' in line or '子文件夹' in line:
                            match = re.search(r'([A-Za-z0-9_-]{20,})', line)
                            if match and match.group(1) != root_folder_odd and match.group(1) != root_folder_even:
                                folder_id = match.group(1)
                                break
            except:
                pass
        
        return jsonify({
            'success': True,
            'data': {
                'detector_running': detector_running,
                'file_timestamp': file_timestamp,
                'delay_minutes': delay_minutes,
                'check_count': check_count,
                'last_check_time': last_check_time,
                'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'folder_id': folder_id,
                'root_folder_odd': root_folder_odd,
                'root_folder_even': root_folder_even,
                'today_date': now.strftime('%Y年%m月%d日')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        })

@app.route('/api/gdrive-detector/txt-files')
def gdrive_detector_txt_files():
    """获取今天的TXT文件列表"""
    try:
        import requests
        import re
        from datetime import datetime
        import pytz
        import json
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        today = datetime.now(beijing_tz).strftime('%Y-%m-%d')
        
        # 从配置文件读取今天的文件夹ID
        folder_id = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"  # 默认值
        try:
            config_file = '/home/user/webapp/daily_folder_config.json'
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('current_date') == today and 'folder_id' in config:
                    folder_id = config['folder_id']
        except:
            pass
        
        url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
        
        response = requests.get(url, timeout=10)
        content = response.text
        
        # 查找今天所有的TXT文件
        pattern = rf'>{today}_(\d{{4}})\.txt<'
        matches = re.findall(pattern, content)
        
        # 排序（从新到旧）
        times_sorted = sorted(matches, reverse=True)
        filenames = [f"{today}_{time}.txt" for time in times_sorted]
        
        return jsonify({
            'success': True,
            'files': filenames,
            'count': len(filenames),
            'date': today,
            'folder_id': folder_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'files': [],
            'count': 0
        })

@app.route('/api/gdrive-detector/logs')
def gdrive_detector_logs():
    """获取检测器日志"""
    try:
        lines = request.args.get('lines', 50, type=int)
        
        # 尝试多个日志文件
        log_files = [
            '/home/user/webapp/gdrive_final_detector.log',
            '/home/user/webapp/gdrive_txt_detector.log',
            '/home/user/webapp/gdrive_smart_detector.log'
        ]
        
        log_content = None
        total_lines = 0
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    log_content = ''.join(all_lines[-lines:] if len(all_lines) > lines else all_lines)
                    total_lines = len(all_lines)
                    break
            except FileNotFoundError:
                continue
        
        if log_content is not None:
            return jsonify({
                'success': True,
                'logs': log_content,
                'total_lines': total_lines
            })
        else:
            return jsonify({
                'success': True,
                'logs': '日志文件不存在',
                'total_lines': 0
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'logs': ''
        })

@app.route('/api/gdrive-detector/config', methods=['GET'])
def gdrive_detector_get_config():
    """获取Google Drive配置"""
    try:
        import json
        config_file = '/home/user/webapp/daily_folder_config.json'
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/gdrive-detector/config', methods=['POST'])
def gdrive_detector_update_config():
    """更新Google Drive配置（父文件夹共享链接）"""
    try:
        import json
        import re
        import requests
        from datetime import datetime
        import pytz
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
        data = request.get_json()
        parent_folder_url = data.get('parent_folder_url', '')
        
        # 从URL中提取文件夹ID
        match = re.search(r'folders/([A-Za-z0-9_-]+)', parent_folder_url)
        if not match:
            return jsonify({
                'success': False,
                'message': '无效的Google Drive文件夹链接'
            })
        
        parent_folder_id = match.group(1)
        
        # 获取父文件夹内的今日文件夹
        today_str = now.strftime('%Y-%m-%d')
        url = f"https://drive.google.com/embeddedfolderview?id={parent_folder_id}"
        response = requests.get(url, timeout=10)
        content = response.text
        
        # 查找今日日期文件夹
        folder_pattern = rf'>{today_str}<'
        if today_str not in content:
            return jsonify({
                'success': False,
                'message': f'父文件夹中未找到今日文件夹: {today_str}'
            })
        
        # 提取今日文件夹ID
        # 查找包含今日日期的文件夹链接
        folder_id_pattern = rf'"([A-Za-z0-9_-]{{20,}})"[^>]*>{today_str}<'
        folder_match = re.search(folder_id_pattern, content)
        
        if not folder_match:
            # 尝试另一种模式
            folder_id_pattern = rf'https://drive\.google\.com/drive/folders/([A-Za-z0-9_-]+)[^>]*>{today_str}<'
            folder_match = re.search(folder_id_pattern, content)
        
        if not folder_match:
            return jsonify({
                'success': False,
                'message': f'无法从父文件夹中提取今日文件夹ID: {today_str}'
            })
        
        today_folder_id = folder_match.group(1)
        
        # 验证今日文件夹是否包含TXT文件
        txt_url = f"https://drive.google.com/embeddedfolderview?id={today_folder_id}"
        txt_response = requests.get(txt_url, timeout=10)
        txt_content = txt_response.text
        
        # 查找TXT文件
        txt_pattern = rf'>{today_str}_(\d{{4}})\.txt<'
        txt_matches = re.findall(txt_pattern, txt_content)
        
        if not txt_matches:
            return jsonify({
                'success': False,
                'message': f'今日文件夹中未找到TXT文件'
            })
        
        # 获取最新的TXT文件
        latest_txt_time = sorted(txt_matches, reverse=True)[0]
        latest_txt = f"{today_str}_{latest_txt_time}.txt"
        
        # 更新配置文件
        config_file = '/home/user/webapp/daily_folder_config.json'
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        
        # 判断今天是单数还是双数日期
        day_of_month = now.day
        is_odd_day = day_of_month % 2 == 1
        
        # 更新配置
        config['parent_folder_url'] = parent_folder_url
        config['parent_folder_id'] = parent_folder_id
        config['current_date'] = today_str
        config['data_date'] = today_str
        config['folder_id'] = today_folder_id
        config['folder_name'] = today_str
        config['latest_txt'] = latest_txt
        config['txt_count'] = len(txt_matches)
        config['last_update'] = now.strftime('%Y-%m-%d %H:%M:%S')
        config['update_reason'] = '通过配置页面更新父文件夹'
        config['last_manual_update'] = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 根据单双数更新对应的父文件夹ID
        if is_odd_day:
            config['root_folder_odd'] = parent_folder_id
        else:
            config['root_folder_even'] = parent_folder_id
        
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': '配置更新成功',
            'data': {
                'parent_folder_id': parent_folder_id,
                'today_folder_id': today_folder_id,
                'today_date': today_str,
                'txt_count': len(txt_matches),
                'latest_txt': latest_txt,
                'is_odd_day': is_odd_day
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/gdrive-detector/trigger-update', methods=['POST'])
def gdrive_detector_trigger_update():
    """触发手动更新检测"""
    try:
        import subprocess
        import time
        
        # 运行检测脚本一次
        result = subprocess.run(
            ['python3', '/home/user/webapp/gdrive_final_detector.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'success': True,
            'message': '检测已执行',
            'output': result.stdout[:500] if result.stdout else '',
            'error': result.stderr[:500] if result.stderr else ''
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': '检测超时（30秒）'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/gdrive-config')
def gdrive_config_page():
    """Google Drive配置页面"""
    return render_template('gdrive_config.html')

# ==================== 统一监控页面 ====================
@app.route('/unified-monitor')
def unified_monitor():
    """统一采集监控页面"""
    return render_template('unified_monitor.html')

@app.route('/unified-monitor-enhanced')
def monitor_enhanced():
    """统一采集监控页面（增强版）- 带执行日志和开关控制"""
    return render_template('unified_monitor_enhanced.html')

# ==================== 综合采集器监控 API ====================
@app.route('/api/collectors/status')
def api_collectors_status():
    """获取所有采集器的运行状态"""
    try:
        import subprocess
        result = subprocess.run(
            ['python3', 'get_all_collectors_status.py'],
            cwd='/home/user/webapp',
            capture_output=True,
            text=True,
            timeout=10
        )
        status_list = json.loads(result.stdout)
        
        # 统计状态
        total = len(status_list)
        normal = sum(1 for s in status_list if s['status'] == 'normal')
        warning = sum(1 for s in status_list if s['status'] == 'warning')
        error = sum(1 for s in status_list if s['status'] in ['error', 'stopped', 'no_data'])
        
        return jsonify({
            'success': True,
            'collectors': status_list,
            'summary': {
                'total': total,
                'normal': normal,
                'warning': warning,
                'error': error
            },
            'timestamp': datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/favicon.ico')
def favicon():
    """处理favicon请求，避免404错误"""
    return '', 204  # 返回无内容状态码

# ============================================================================
# 币种选择和评分系统
# ============================================================================

@app.route('/coin-pool')
def coin_pool_page():
    """币种池页面 - 从星星系统筛选的优质币种池"""
    response = make_response(render_template('coin_pool.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ============================================================================
# 支撑压力线系统
# ============================================================================

@app.route('/support-resistance')
def support_resistance_page():
    """支撑压力线系统页面"""
    response = make_response(render_template('support_resistance.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/trading-signals')
def trading_signals_page():
    """决策-交易信号系统页面"""
    response = make_response(render_template('trading_signals.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def track_trading_signal(symbol, buy_point_type, suggested_position):
    """跟踪交易信号的首次触发时间"""
    from datetime import datetime
    import pytz
    import sqlite3
    
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    signal_key = f"{symbol}_{buy_point_type}"
    
    # 使用独立的数据库连接
    conn_track = sqlite3.connect('crypto_data.db')
    conn_track.row_factory = sqlite3.Row
    cursor_track = conn_track.cursor()
    
    try:
        # 检查该信号是否已存在
        cursor_track.execute('''
            SELECT id, first_triggered_at, suggested_position 
            FROM trading_signal_history 
            WHERE signal_key = ? AND is_active = 1
        ''', (signal_key,))
        
        existing = cursor_track.fetchone()
        
        if existing:
            # 更新最后更新时间
            cursor_track.execute('''
                UPDATE trading_signal_history 
                SET last_updated_at = ?, suggested_position = ?
                WHERE id = ?
            ''', (now.strftime('%Y-%m-%d %H:%M:%S'), suggested_position, existing['id']))
            conn_track.commit()
            return {
                'first_triggered_at': existing['first_triggered_at'],
                'initial_position': str(int(float(existing['suggested_position'].replace('%', '')) * 0.3)) + '%'
            }
        else:
            # 插入新信号
            cursor_track.execute('''
                INSERT INTO trading_signal_history 
                (signal_key, symbol, buy_point_type, suggested_position, 
                 first_triggered_at, last_updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (signal_key, symbol, buy_point_type, suggested_position,
                  now.strftime('%Y-%m-%d %H:%M:%S'), 
                  now.strftime('%Y-%m-%d %H:%M:%S')))
            conn_track.commit()
            return {
                'first_triggered_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                'initial_position': str(int(float(suggested_position.replace('%', '')) * 0.3)) + '%'
            }
    finally:
        conn_track.close()

def check_no_new_low_5min(symbol):
    """检查创新低后连续5个5分钟K线不创新低"""
    import sqlite3
    from datetime import datetime, timedelta
    
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    try:
        # 统一格式：FIL -> FIL-USDT-SWAP
        symbol_full = f"{symbol}-USDT-SWAP" if not symbol.endswith('-USDT-SWAP') else symbol
        symbol_short = symbol.replace('-USDT-SWAP', '')
        
        # 获取最近的创新低事件
        cursor.execute('''
            SELECT event_time, price
            FROM price_breakthrough_events
            WHERE symbol = ? AND event_type = 'new_low'
            ORDER BY event_time DESC
            LIMIT 1
        ''', (symbol_short,))
        
        last_new_low = cursor.fetchone()
        if not last_new_low:
            return False
        
        new_low_time = datetime.strptime(last_new_low[0], '%Y-%m-%d %H:%M:%S')
        new_low_price = last_new_low[1]
        
        # 获取创新低之后的5个5分钟K线
        cursor.execute('''
            SELECT low, timestamp
            FROM okex_kline_ohlc
            WHERE symbol = ?
              AND timeframe = '5m'
              AND datetime(timestamp/1000, 'unixepoch') > datetime(?)
            ORDER BY timestamp ASC
            LIMIT 5
        ''', (symbol_full, new_low_time.strftime('%Y-%m-%d %H:%M:%S')))
        
        klines_after = cursor.fetchall()
        
        # 需要有5根K线
        if len(klines_after) < 5:
            return False
        
        # 检查这5根K线是否都没有创新低
        for low, ts in klines_after:
            if low < new_low_price:
                return False
        
        return True
    finally:
        conn.close()

def get_1h_rsi(symbol):
    """获取1小时RSI"""
    import sqlite3
    
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    try:
        # 统一格式
        symbol_full = f"{symbol}-USDT-SWAP" if not symbol.endswith('-USDT-SWAP') else symbol
        
        cursor.execute('''
            SELECT rsi_14
            FROM okex_technical_indicators
            WHERE symbol = ? AND timeframe IN ('1h', '1H')
            ORDER BY record_time DESC
            LIMIT 1
        ''', (symbol_full,))
        
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def check_consecutive_oscillation_5min(symbol):
    """检查5分钟周期连续3个震荡≤0.5% 且涨跌在0%到+0.25%之间（不包括负涨跌）"""
    import sqlite3
    
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    try:
        # 统一格式
        symbol_full = f"{symbol}-USDT-SWAP" if not symbol.endswith('-USDT-SWAP') else symbol
        
        # 获取最近3根5分钟K线
        cursor.execute('''
            SELECT open, high, low, close
            FROM okex_kline_ohlc
            WHERE symbol = ?
              AND timeframe = '5m'
            ORDER BY timestamp DESC
            LIMIT 3
        ''', (symbol_full,))
        
        klines = cursor.fetchall()
        
        if len(klines) < 3:
            return False
        
        # 检查每根K线
        for open_price, high, low, close in klines:
            if open_price == 0:
                return False
            
            # 震荡幅度 = (最高-最低) / 开盘 * 100
            oscillation = ((high - low) / open_price) * 100 if open_price > 0 else 999
            
            # 涨跌幅 = (收盘-开盘) / 开盘 * 100（保留正负，不取绝对值）
            change = ((close - open_price) / open_price) * 100
            
            # 任何一根不满足条件就返回False
            # 涨跌幅必须在 0% 到 +0.25% 之间，震荡幅度 <= 0.50%
            if change < 0 or change > 0.25 or oscillation > 0.5:
                return False
        
        return True
    finally:
        conn.close()

def deactivate_missing_signals(active_signal_keys):
    """将不再满足条件的信号标记为失效"""
    from datetime import datetime
    import pytz
    import sqlite3
    
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    try:
        # 获取所有当前活跃的信号
        cursor.execute('SELECT signal_key FROM trading_signal_history WHERE is_active = 1')
        all_active = [row[0] for row in cursor.fetchall()]
        
        # 找出不在当前信号列表中的信号（即条件不再满足的信号）
        signals_to_deactivate = [sig for sig in all_active if sig not in active_signal_keys]
        
        # 标记这些信号为失效
        for signal_key in signals_to_deactivate:
            cursor.execute('''
                UPDATE trading_signal_history 
                SET is_active = 0, last_updated_at = ?
                WHERE signal_key = ? AND is_active = 1
            ''', (now.strftime('%Y-%m-%d %H:%M:%S'), signal_key))
        
        conn.commit()
        return len(signals_to_deactivate)
    finally:
        conn.close()

@app.route('/api/trading-signals/analyze')
def api_trading_signals_analyze():
    """分析交易信号 - 做多买点1/2/3"""
    try:
        from datetime import datetime, timedelta
        import pytz
        from opening_logic import get_opening_suggestion
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
        # 0. 获取开仓逻辑建议（用于买点3仓位计算）
        try:
            opening_logic_data = get_opening_suggestion()
            opening_position = opening_logic_data.get('position_info', {})
            opening_can_long = opening_logic_data.get('can_long', False)
            opening_position_percent = opening_position.get('position_percent', 0)
        except Exception as e:
            print(f"获取开仓逻辑失败: {e}")
            opening_can_long = False
            opening_position_percent = 0
        
        # 1. 获取支撑压力线数据
        cursor.execute('''
            SELECT symbol, current_price, support_line_1, support_line_2, resistance_line_1,
                   distance_to_support_1, distance_to_support_2, distance_to_resistance_1,
                   position_s2_r1, record_time
            FROM support_resistance_levels
            WHERE id IN (
                SELECT MAX(id) 
                FROM support_resistance_levels 
                GROUP BY symbol
            )
        ''')
        sr_data = {row['symbol']: dict(row) for row in cursor.fetchall()}
        
        # 2. 获取价格突破数据(创新低统计 - 最近7天)
        seven_days_ago = now - timedelta(days=7)
        cursor.execute('''
            SELECT symbol, COUNT(*) as count
            FROM price_breakthrough_events
            WHERE event_type = 'new_low'
              AND event_time >= ?
            GROUP BY symbol
        ''', (seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),))
        breakthrough_data = {row['symbol']: row['count'] for row in cursor.fetchall()}
        
        # 3. 获取最新快照数据(急涨急跌、计次得分)
        cursor.execute('''
            SELECT c.symbol, c.rush_up, c.rush_down, c.current_price,
                   s.count_score_display, s.count_score_type
            FROM crypto_coin_data c
            JOIN crypto_snapshots s ON c.snapshot_id = s.id
            WHERE c.id IN (
                SELECT MAX(id) 
                FROM crypto_coin_data 
                GROUP BY symbol
            )
        ''')
        coin_data = {row['symbol']: dict(row) for row in cursor.fetchall()}
        
        # 3.5 获取K线指标数据 (5分钟RSI、SAR位置、SAR象限)
        cursor.execute('''
            SELECT symbol, rsi_14, sar_position, sar_quadrant, sar_count_label
            FROM okex_technical_indicators
            WHERE timeframe = '5m'
              AND (symbol, record_time) IN (
                SELECT symbol, MAX(record_time)
                FROM okex_technical_indicators
                WHERE timeframe = '5m'
                GROUP BY symbol
            )
        ''')
        kline_indicators = {}
        for row in cursor.fetchall():
            # 统一格式：FIL-USDT-SWAP -> FIL
            symbol_short = row['symbol'].replace('-USDT-SWAP', '')
            kline_indicators[symbol_short] = {
                'rsi_5m': row['rsi_14'],
                'sar_position': row['sar_position'],  # 'bullish' 或 'bearish'
                'sar_quadrant': row['sar_quadrant'],  # 1-4象限
                'sar_count_label': row['sar_count_label']  # 例如 "多头12"
            }
        
        # 4. 获取位置系统数据（BTC/ETH的4h/12h/24h/48h周期位置）
        cursor.execute('''
            SELECT symbol, position_4h, position_12h, position_24h, position_48h
            FROM position_system
            WHERE symbol IN ('BTC', 'ETH')
              AND id IN (
                SELECT MAX(id) 
                FROM position_system 
                GROUP BY symbol
            )
        ''')
        position_data = {}
        for row in cursor.fetchall():
            symbol = row['symbol']
            positions = [
                row['position_4h'], row['position_12h'], 
                row['position_24h'], row['position_48h']
            ]
            # 统计有多少个周期位置 < 10%
            low_position_count = sum(1 for p in positions if p is not None and p < 10)
            position_data[symbol] = low_position_count
        
        conn.close()
        
        # 检查BTC和ETH是否至少有5个周期 < 10%
        # 由于只有4个周期，我们改为检查BTC和ETH加起来是否有5个以上
        btc_low = position_data.get('BTC', 0)
        eth_low = position_data.get('ETH', 0)
        total_low_positions = btc_low + eth_low
        condition6_pass = total_low_positions >= 5
        
        # 5. 统计接近支撑线的币种数量（用于买点3条件6）
        # 接近支撑1：距离支撑线1 <= 某个阈值（例如10%）
        # 接近支撑2：距离支撑线2 <= 某个阈值（例如10%）
        near_support_1_count = 0
        near_support_2_count = 0
        
        for symbol, sr in sr_data.items():
            dist_s1 = sr.get('distance_to_support_1')
            dist_s2 = sr.get('distance_to_support_2')
            
            # 统计接近支撑1的币种（距离 <= 10%）
            if dist_s1 is not None and dist_s1 <= 10:
                near_support_1_count += 1
            
            # 统计接近支撑2的币种（距离 <= 10%）
            if dist_s2 is not None and dist_s2 <= 10:
                near_support_2_count += 1
        
        # 买点3条件6：接近支撑1的币种数 >= 8 或 接近支撑2的币种数 >= 8
        condition6_support_system = near_support_1_count >= 8 or near_support_2_count >= 8
        
        # 6. 分析信号
        signals = []
        buy_point_1_count = 0
        buy_point_2_count = 0
        buy_point_3_count = 0
        
        for symbol, sr in sr_data.items():
            coin_name = symbol.replace('USDT', '')
            coin = coin_data.get(coin_name, {})
            kline = kline_indicators.get(coin_name, {})
            
            # 获取创新低次数
            new_lows = breakthrough_data.get(coin_name, 0)
            
            # 获取计次得分
            score_display = coin.get('count_score_display', '---')
            score_type = coin.get('count_score_type', '中性')
            
            # 获取急涨急跌
            rush_up = coin.get('rush_up', 0) or 0
            rush_down = coin.get('rush_down', 0) or 0
            rush_diff = rush_up - rush_down
            
            # 获取K线指标数据
            rsi_5m = kline.get('rsi_5m')
            sar_position = kline.get('sar_position')  # 'bullish' / 'bearish'
            sar_quadrant = kline.get('sar_quadrant')  # 1-4
            sar_count_label = kline.get('sar_count_label', '')
            
            # 解析空头/多头数量（从 "空头20" 或 "多头12" 中提取数字）
            sar_count = 0
            if sar_count_label:
                import re
                match = re.search(r'(\d+)', sar_count_label)
                if match:
                    sar_count = int(match.group(1))
            
            # 通用条件判断
            condition1 = new_lows < 3  # 创新低 < 3 【买点1/2/3适用】
            condition2 = '★' in score_display or '⭐' in score_display  # 计次得分是星星 【买点1/2适用】
            condition3 = rush_diff > 0  # 急涨 - 急跌 > 0 【买点1/2适用】
            condition4 = rsi_5m is not None and rsi_5m < 20  # 5分钟RSI < 20 【买点1适用】（修改为使用5分钟RSI）
            condition5 = rush_diff > -15  # 急涨 - 急跌 > -15 【买点3适用】
            condition6 = condition6_pass  # BTC/ETH至少5个周期 < 10% 【买点3适用】
            
            # 新增条件（基于K线指标）
            condition_sar_bearish = sar_position == 'bearish'  # 空头趋势
            condition_sar_count = sar_count > 20  # 空头数量>20
            condition_sar_quadrant3 = sar_quadrant == 3  # SAR第三象限
            condition_rsi_low = rsi_5m is not None and rsi_5m < 30  # 5分钟RSI<30 【买点2适用】
            
            # 买点3专用条件检查
            condition_no_new_low_5m = check_no_new_low_5min(coin_name)  # 创新低后连续5个5分钟K线不创新低
            rsi_1h = get_1h_rsi(coin_name)  # 获取1小时RSI
            condition_rsi_1h_low = rsi_1h is not None and rsi_1h < 15  # 1小时RSI<15
            condition_oscillation_3 = check_consecutive_oscillation_5min(coin_name)  # 连续3个震荡
            
            # 获取距离支撑线1的距离（用于买点1）
            distance = sr.get('distance_to_support_1')
            
            # 判断各个买点
            buy_point_1 = False
            buy_point_2 = False
            buy_point_3 = False
            
            # 买点1: 达到支撑线1 (距离 < 5%) + 条件1234
            if (distance is not None and distance <= 5 and 
                condition1 and condition2 and condition3 and condition4):
                buy_point_1 = True
                buy_point_1_count += 1
            
            # 买点2: 回调买入
            # 条件：条件123 + 空头>20 + 5分钟SAR第三象限 + 5分钟RSI<30
            if (condition1 and condition2 and condition3 and 
                condition_sar_count and condition_sar_quadrant3 and condition_rsi_low):
                buy_point_2 = True
                buy_point_2_count += 1
            
            # 买点3: 空转多买入（重新定义条件）
            # 6个必须条件：
            # 1. 创新低后连续5个5分钟K线不创新低
            # 2. 1小时RSI < 15
            # 3. 5分钟周期连续3个震荡≤0.5% 且涨跌<0.25%
            # 4. SAR空头数量 > 20
            # 5. 5分钟SAR在第三象限
            # 6. 支撑压力线系统：接近支撑1的币种数 >= 8 或 接近支撑2的币种数 >= 8
            if (condition_no_new_low_5m and 
                condition_rsi_1h_low and 
                condition_oscillation_3 and 
                condition_sar_count and 
                condition_sar_quadrant3 and 
                condition6_support_system):  # 使用全局条件
                buy_point_3 = True
                buy_point_3_count += 1
            
            # 只保留有信号的币种
            if buy_point_1 or buy_point_2 or buy_point_3:
                # 详细的条件判断结果 - 用于透明化显示
                detailed_conditions = {
                    'buy_point_1_conditions': {
                        'distance_to_support': {'value': distance, 'threshold': '≤ 5%', 'pass': distance is not None and distance <= 5, 'desc': '距离支撑线1'},
                        'condition1': {'value': new_lows, 'threshold': '< 3', 'pass': condition1, 'desc': '7天创新低次数'},
                        'condition2': {'value': score_display, 'threshold': '包含★或⭐', 'pass': condition2, 'desc': '计次得分显示'},
                        'condition3': {'value': round(rush_diff, 2), 'threshold': '> 0', 'pass': condition3, 'desc': '急涨-急跌'},
                        'condition4': {'value': round(rsi_5m, 2) if rsi_5m else None, 'threshold': '< 20', 'pass': condition4, 'desc': '5分钟RSI'}
                    },
                    'buy_point_2_conditions': {
                        'condition1': {'value': new_lows, 'threshold': '< 3', 'pass': condition1, 'desc': '7天创新低次数'},
                        'condition2': {'value': score_display, 'threshold': '包含★或⭐', 'pass': condition2, 'desc': '计次得分显示'},
                        'condition3': {'value': round(rush_diff, 2), 'threshold': '> 0', 'pass': condition3, 'desc': '急涨-急跌'},
                        'sar_count': {'value': sar_count, 'threshold': '> 20', 'pass': condition_sar_count, 'desc': 'SAR空头数量'},
                        'sar_quadrant': {'value': sar_quadrant, 'threshold': '= 3', 'pass': condition_sar_quadrant3, 'desc': 'SAR第三象限'},
                        'rsi_5m': {'value': round(rsi_5m, 2) if rsi_5m else None, 'threshold': '< 30', 'pass': condition_rsi_low, 'desc': '5分钟RSI'}
                    },
                    'buy_point_3_conditions': {
                        'no_new_low_5m': {'value': '是' if condition_no_new_low_5m else '否', 'threshold': '是', 'pass': condition_no_new_low_5m, 'desc': '创新低后连续5个5分钟K线不创新低'},
                        'rsi_1h': {'value': round(rsi_1h, 2) if rsi_1h else None, 'threshold': '< 15', 'pass': condition_rsi_1h_low, 'desc': '1小时RSI'},
                        'oscillation_3': {'value': '是' if condition_oscillation_3 else '否', 'threshold': '是', 'pass': condition_oscillation_3, 'desc': '连续3个震荡≤0.5% 且涨跌<0.25%'},
                        'sar_count': {'value': sar_count, 'threshold': '> 20', 'pass': condition_sar_count, 'desc': 'SAR空头数量'},
                        'sar_quadrant': {'value': sar_quadrant, 'threshold': '= 3', 'pass': condition_sar_quadrant3, 'desc': '5分钟SAR第三象限'},
                        'support_system': {'value': f'接近支撑1: {near_support_1_count}个, 接近支撑2: {near_support_2_count}个', 'threshold': '接近支撑1 ≥ 8个 或 接近支撑2 ≥ 8个', 'pass': condition6_support_system, 'desc': '支撑压力线系统'}
                    }
                }
                
                # 确定买点类型和建议仓位
                buy_point_type = None
                suggested_position = None
                position_calculation_note = None
                buy_times = None  # 分批买入次数
                
                if buy_point_1:
                    buy_point_type = 'buy_point_1'
                    suggested_position = '30%'
                    buy_times = 3  # 买点1分3次买入
                    position_calculation_note = '买点1固定仓位，分3次买入'
                    
                elif buy_point_3:
                    buy_point_type = 'buy_point_3'
                    buy_times = 2  # 买点3分2次买入
                    # 买点3特殊仓位逻辑
                    if opening_can_long and opening_position_percent > 0:
                        # 情况2：开仓逻辑允许开仓
                        # 买点3仓位 = 开仓逻辑建议 + 20%，最高70%
                        bp3_position = min(opening_position_percent + 20, 70)
                        suggested_position = f'{int(bp3_position)}%'
                        position_calculation_note = f'开仓逻辑{int(opening_position_percent)}% + 买点3加成20% = {int(bp3_position)}% (上限70%)，分2次买入'
                    else:
                        # 情况1：开仓逻辑不允许开仓
                        # 买点3可额外开20%
                        suggested_position = '20%'
                        position_calculation_note = '开仓逻辑不允许，买点3可额外开20%，分2次买入'
                        
                elif buy_point_2:
                    buy_point_type = 'buy_point_2'
                    suggested_position = '20%'
                    buy_times = 2  # 买点2分2次买入
                    position_calculation_note = '买点2固定仓位，分2次买入'
                
                # 跟踪信号历史，获取首次触发时间和首次开仓建议
                tracking_info = track_trading_signal(coin_name, buy_point_type, suggested_position)
                
                signals.append({
                    'symbol': coin_name,
                    'current_price': sr.get('current_price', 0),
                    'support_line_1': sr.get('support_line_1'),
                    'distance_to_support_1': distance,
                    'buy_point_1': buy_point_1,
                    'buy_point_2': buy_point_2,
                    'buy_point_3': buy_point_3,
                    'suggested_position': suggested_position,
                    'buy_times': buy_times,  # 新增：分批买入次数
                    'position_calculation_note': position_calculation_note,  # 新增：仓位计算说明
                    'opening_logic_position': f'{int(opening_position_percent)}%' if opening_can_long else '不允许',  # 新增：开仓逻辑建议
                    'first_triggered_at': tracking_info['first_triggered_at'],  # 新增：首次触发时间
                    'initial_position': tracking_info['initial_position'],  # 新增：首次开仓建议(总仓位的30%)
                    'conditions': {
                        'condition1_pass': condition1,
                        'condition2_pass': condition2,
                        'condition3_pass': condition3,
                        'new_lows': new_lows,
                        'score_display': score_display,
                        'rush_diff': round(rush_diff, 2)
                    },
                    'kline_indicators': {
                        'rsi_5m': round(rsi_5m, 2) if rsi_5m else None,
                        'sar_position': sar_position,
                        'sar_quadrant': sar_quadrant,
                        'sar_count': sar_count,
                        'sar_count_label': sar_count_label
                    },
                    'detailed_conditions': detailed_conditions  # 新增：详细条件判断结果
                })
        
        # 按买点1 > 买点3 > 买点2 优先级排序，同优先级按距支撑线距离排序
        def sort_key(x):
            priority = 0
            if x['buy_point_1']:
                priority = 3
            elif x['buy_point_3']:
                priority = 2
            elif x['buy_point_2']:
                priority = 1
            distance = x['distance_to_support_1'] if x['distance_to_support_1'] is not None else 999
            return (-priority, distance)
        
        signals.sort(key=sort_key)
        
        # 收集当前所有活跃信号的signal_key
        active_signal_keys = []
        for signal in signals:
            coin_name = signal['symbol']
            if signal['buy_point_1']:
                active_signal_keys.append(f"{coin_name}_buy_point_1")
            elif signal['buy_point_3']:
                active_signal_keys.append(f"{coin_name}_buy_point_3")
            elif signal['buy_point_2']:
                active_signal_keys.append(f"{coin_name}_buy_point_2")
        
        # 将不再满足条件的信号标记为失效
        deactivated_count = deactivate_missing_signals(active_signal_keys)
        
        # 买点规则说明 - 透明化展示
        buy_point_rules = {
            'buy_point_1': {
                'name': '买点1 - 支撑线买入',
                'suggested_position': '30%',
                'buy_times': 3,  # 分3次买入
                'conditions': [
                    {'id': '距离支撑线', 'rule': '距离支撑线1 ≤ 5%', 'priority': 'high'},
                    {'id': '创新低', 'rule': '7天创新低次数 < 3', 'priority': 'high'},
                    {'id': '计次得分', 'rule': '计次得分显示包含★或⭐', 'priority': 'medium'},
                    {'id': '急涨急跌', 'rule': '急涨 - 急跌 > 0', 'priority': 'medium'},
                    {'id': 'RSI 5m', 'rule': '5分钟RSI < 20', 'priority': 'high'}
                ],
                'description': '价格接近支撑线时的买入机会，风险较低，建议分3次买入'
            },
            'buy_point_2': {
                'name': '买点2 - 回调买入',
                'suggested_position': '20%',
                'buy_times': 2,  # 分2次买入
                'conditions': [
                    {'id': '创新低', 'rule': '7天创新低次数 < 3', 'priority': 'high'},
                    {'id': '计次得分', 'rule': '计次得分显示包含★或⭐', 'priority': 'medium'},
                    {'id': '急涨急跌', 'rule': '急涨 - 急跌 > 0', 'priority': 'medium'},
                    {'id': 'SAR空头数', 'rule': 'SAR空头数量 > 20', 'priority': 'high'},
                    {'id': 'SAR象限', 'rule': 'SAR在第三象限', 'priority': 'high'},
                    {'id': 'RSI 5m', 'rule': '5分钟RSI < 30', 'priority': 'high'}
                ],
                'description': '市场回调时的买入机会，需要技术指标确认，建议分2次买入'
            },
            'buy_point_3': {
                'name': '买点3 - 空转多买入',
                'suggested_position': '最多20% (如无开仓逻辑建议)',
                'buy_times': 2,  # 分2次买入
                'conditions': [
                    {'id': '5分钟不创新低', 'rule': '创新低后连续5个5分钟K线不创新低', 'priority': 'high'},
                    {'id': '1h RSI', 'rule': '1小时RSI < 15', 'priority': 'high'},
                    {'id': '连续震荡', 'rule': '5分钟周期连续3个震荡≤0.5% 且涨跌<0.25%', 'priority': 'high'},
                    {'id': 'SAR空头数', 'rule': 'SAR空头持续数量 > 20', 'priority': 'high'},
                    {'id': 'SAR象限', 'rule': '5分钟SAR在第三象限', 'priority': 'high'},
                    {'id': '支撑压力线', 'rule': '接近支撑1的币种数 ≥ 8个 或 接近支撑2的币种数 ≥ 8个', 'priority': 'high'}
                ],
                'description': '极度超卖后的空转多买入机会，严格条件筛选（需市场整体接近支撑线），建议分2次买入'
            }
        }
        
        return jsonify({
            'success': True,
            'data': {
                'signals': signals,
                'buy_point_1_count': buy_point_1_count,
                'buy_point_2_count': buy_point_2_count,
                'buy_point_3_count': buy_point_3_count,
                'total_coins': len(sr_data),
                'update_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'buy_point_rules': buy_point_rules,  # 新增：买点规则说明
                'opening_logic_info': {  # 新增：开仓逻辑信息
                    'can_long': opening_can_long,
                    'position_percent': opening_position_percent,
                    'suggestion': f'{int(opening_position_percent)}%' if opening_can_long else '不允许开仓'
                },
                'notes': {
                    'buy_point_1': '✅ 支撑线买入 (距离<5%) + 创新低<3 + 计次得分⭐/★ + 急涨>急跌 + 5分钟RSI<20 - 已更新使用5分钟RSI',
                    'buy_point_2': '✅ 回调买入 (条件1-3 + 空头>20 + 5分钟SAR第三象限 + 5分钟RSI<30) - 已集成K线指标',
                    'buy_point_3': '✅ 空转多买入 (5个5分钟不创新低 + 1h RSI<15 + 连续3个震荡 + SAR空头>20 + SAR第3象限) - 严格条件',
                    'buy_point_3_position': '📊 买点3仓位规则：若开仓逻辑允许，则为 开仓逻辑仓位+20% (上限70%)；若开仓逻辑不允许，则额外开20%',
                    'data_integration': '✅ 已集成kline-indicators数据：5分钟RSI、SAR位置、SAR象限、SAR计数',
                    'data_limitation': '⚠️ 仍需补充：连续5个5分钟K线不创新低、连续3个震荡条件'
                }
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trading-signals/buy-points')
def api_trading_signals_buy_points():
    """获取当前所有买点信号（简化版API）"""
    try:
        import sqlite3
        from datetime import datetime
        import pytz
        
        # 调用现有的分析函数
        response = api_trading_signals_analyze()
        
        # 如果返回的是Response对象，获取其JSON数据
        if hasattr(response, 'get_json'):
            data = response.get_json()
        else:
            import json
            data = json.loads(response[0])
        
        if not data.get('success'):
            return jsonify({
                'success': False,
                'message': '获取买点数据失败',
                'error': data.get('error', 'Unknown error')
            }), 500
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
        # 提取买点信号
        signals_data = data.get('data', {})
        buy_signals = signals_data.get('signals', [])
        
        # 按买点类型分组
        buy_point_1 = [s for s in buy_signals if s.get('buy_point') == 1]
        buy_point_2 = [s for s in buy_signals if s.get('buy_point') == 2]
        buy_point_3 = [s for s in buy_signals if s.get('buy_point') == 3]
        
        # 简化信号数据
        def simplify_signal(signal):
            return {
                'symbol': signal.get('symbol'),
                'buy_point': signal.get('buy_point'),
                'current_price': signal.get('current_price'),
                'suggested_position': signal.get('suggested_position'),
                'buy_times': signal.get('buy_times'),
                'distance_to_support': signal.get('distance_to_support_1'),
                'conditions_met': signal.get('conditions_met'),
                'score_display': signal.get('score_display'),
                'sar_position': signal.get('sar_position'),
                'rsi_5m': signal.get('rsi_5m'),
                'rsi_1h': signal.get('rsi_1h'),
                'recommended': signal.get('recommended', False)
            }
        
        result = {
            'success': True,
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_signals': len(buy_signals),
                'buy_point_1_count': len(buy_point_1),
                'buy_point_2_count': len(buy_point_2),
                'buy_point_3_count': len(buy_point_3)
            },
            'buy_points': {
                'buy_point_1': [simplify_signal(s) for s in buy_point_1],
                'buy_point_2': [simplify_signal(s) for s in buy_point_2],
                'buy_point_3': [simplify_signal(s) for s in buy_point_3]
            },
            'all_signals': [simplify_signal(s) for s in buy_signals],
            'rules': signals_data.get('buy_point_rules', {})
        }
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print(f"获取买点信号失败: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': '获取买点信号失败',
            'error': str(e)
        }), 500

@app.route('/api/trading-signals/history')
def api_trading_signals_history():
    """获取历史信号（已失效的信号）"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        import pytz
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
        # 获取最近7天内失效的信号
        seven_days_ago = now - timedelta(days=7)
        
        cursor.execute('''
            SELECT signal_key, symbol, buy_point_type, suggested_position,
                   first_triggered_at, last_updated_at
            FROM trading_signal_history
            WHERE is_active = 0
              AND last_updated_at >= ?
            ORDER BY last_updated_at DESC
            LIMIT 50
        ''', (seven_days_ago.strftime('%Y-%m-%d %H:%M:%S'),))
        
        history_signals = []
        for row in cursor.fetchall():
            # 计算信号持续时间
            first_time = datetime.strptime(row['first_triggered_at'], '%Y-%m-%d %H:%M:%S')
            last_time = datetime.strptime(row['last_updated_at'], '%Y-%m-%d %H:%M:%S')
            duration_minutes = int((last_time - first_time).total_seconds() / 60)
            
            buy_point_name = {
                'buy_point_1': '买点1',
                'buy_point_2': '买点2',
                'buy_point_3': '买点3'
            }.get(row['buy_point_type'], '未知')
            
            history_signals.append({
                'symbol': row['symbol'],
                'buy_point_type': buy_point_name,
                'suggested_position': row['suggested_position'],
                'initial_position': str(int(float(row['suggested_position'].replace('%', '')) * 0.3)) + '%',
                'first_triggered_at': row['first_triggered_at'],
                'last_updated_at': row['last_updated_at'],
                'duration_minutes': duration_minutes
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'history_signals': history_signals,
                'total_count': len(history_signals),
                'update_time': now.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/support-resistance/latest')
def api_support_resistance_latest():
    """获取最新的支撑压力线数据"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取最新的快照数据
        cursor.execute('''
            SELECT 
                snapshot_time,
                scenario_1_coins,
                scenario_2_coins,
                scenario_3_coins,
                scenario_4_coins
            FROM support_resistance_snapshots
            ORDER BY created_at DESC
            LIMIT 1
        ''')
        
        snapshot_row = cursor.fetchone()
        if not snapshot_row:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'No snapshot data available'
            })
        
        import json
        
        update_time = snapshot_row['snapshot_time']
        
        # 获取所有监控的币种（27个）
        MONITORED_SYMBOLS = [
            'BTC-USDT-SWAP', 'ETH-USDT-SWAP', 'XRP-USDT-SWAP', 'BNB-USDT-SWAP',
            'SOL-USDT-SWAP', 'LTC-USDT-SWAP', 'DOGE-USDT-SWAP', 'SUI-USDT-SWAP',
            'TRX-USDT-SWAP', 'TON-USDT-SWAP', 'ETC-USDT-SWAP', 'BCH-USDT-SWAP',
            'HBAR-USDT-SWAP', 'XLM-USDT-SWAP', 'FIL-USDT-SWAP', 'LINK-USDT-SWAP',
            'CRO-USDT-SWAP', 'DOT-USDT-SWAP', 'AAVE-USDT-SWAP', 'UNI-USDT-SWAP',
            'NEAR-USDT-SWAP', 'APT-USDT-SWAP', 'CFX-USDT-SWAP', 'CRV-USDT-SWAP',
            'STX-USDT-SWAP', 'LDO-USDT-SWAP', 'TAO-USDT-SWAP'
        ]
        
        # 获取每个币种的最新价格
        placeholders = ','.join(['?' for _ in MONITORED_SYMBOLS])
        cursor.execute(f'''
            SELECT symbol, close as current_price, timestamp
            FROM okex_kline_ohlc
            WHERE timeframe = '5m'
            AND symbol IN ({placeholders})
            AND (symbol, timestamp) IN (
                SELECT symbol, MAX(timestamp)
                FROM okex_kline_ohlc
                WHERE timeframe = '5m'
                AND symbol IN ({placeholders})
                GROUP BY symbol
            )
            ORDER BY symbol
        ''', MONITORED_SYMBOLS + MONITORED_SYMBOLS)
        
        price_rows = cursor.fetchall()
        price_dict = {row['symbol']: row['current_price'] for row in price_rows}
        
        # 解析4种情况的币种数据，构建alert字典
        alert_dict = {}
        for scenario_num in range(1, 5):
            coins_json = snapshot_row[f'scenario_{scenario_num}_coins']
            if coins_json:
                try:
                    coins = json.loads(coins_json)
                    for coin in coins:
                        symbol = coin['symbol']
                        if symbol not in alert_dict:
                            alert_dict[symbol] = {
                                'support_1': 0,
                                'support_2': 0,
                                'resistance_1': 0,
                                'resistance_2': 0,
                                'position_s2_r1': None,
                                'position_s1_r2': None,
                                'position_s1_r2_upper': None,
                                'position_s1_r1': None,
                                'alert_scenario_1': False,
                                'alert_scenario_2': False,
                                'alert_scenario_3': False,
                                'alert_scenario_4': False
                            }
                        
                        # 从当前币种数据中更新支撑/压力线值（合并所有场景的数据）
                        if 'support_1' in coin and coin['support_1']:
                            alert_dict[symbol]['support_1'] = coin['support_1']
                        if 'support_2' in coin and coin['support_2']:
                            alert_dict[symbol]['support_2'] = coin['support_2']
                        if 'resistance_1' in coin and coin['resistance_1']:
                            alert_dict[symbol]['resistance_1'] = coin['resistance_1']
                        if 'resistance_2' in coin and coin['resistance_2']:
                            alert_dict[symbol]['resistance_2'] = coin['resistance_2']
                        
                        # 设置对应情况的alert和position
                        if scenario_num == 1:
                            alert_dict[symbol]['alert_scenario_1'] = True
                            alert_dict[symbol]['position_s2_r1'] = coin.get('position', 0)
                        elif scenario_num == 2:
                            alert_dict[symbol]['alert_scenario_2'] = True
                            alert_dict[symbol]['position_s1_r2'] = coin.get('position', 0)
                        elif scenario_num == 3:
                            alert_dict[symbol]['alert_scenario_3'] = True
                            alert_dict[symbol]['position_s1_r2_upper'] = coin.get('position', 0)
                        elif scenario_num == 4:
                            alert_dict[symbol]['alert_scenario_4'] = True
                            alert_dict[symbol]['position_s1_r1'] = coin.get('position', 0)
                except:
                    pass
        
        # 获取所有币种的支撑/压力线数据（从support_resistance_levels表）
        # 将币种格式从 'BTC-USDT-SWAP' 转换为 'BTCUSDT'
        symbols_for_levels = [s.replace('-USDT-SWAP', 'USDT') for s in MONITORED_SYMBOLS]
        placeholders_levels = ','.join(['?' for _ in symbols_for_levels])
        
        # Get the latest record for each symbol using a subquery
        cursor.execute(f'''
            SELECT srl.symbol, srl.current_price, srl.support_line_1, srl.support_line_2, 
                   srl.resistance_line_1, srl.resistance_line_2,
                   srl.position_7d, srl.position_48h,
                   srl.alert_7d_low, srl.alert_7d_high,
                   srl.alert_48h_low, srl.alert_48h_high,
                   srl.support_1_days, srl.support_2_hours,
                   srl.resistance_1_days, srl.resistance_2_hours,
                   srl.baseline_price_24h, srl.price_change_24h, srl.change_percent_24h
            FROM support_resistance_levels srl
            INNER JOIN (
                SELECT symbol, MAX(record_time) as max_time
                FROM support_resistance_levels
                WHERE symbol IN ({placeholders_levels})
                GROUP BY symbol
            ) latest ON srl.symbol = latest.symbol AND srl.record_time = latest.max_time
        ''', symbols_for_levels)
        
        sr_levels_rows = cursor.fetchall()
        sr_levels_dict = {}
        for row in sr_levels_rows:
            symbol = row['symbol']  # 已经是 BTCUSDT 格式
            sr_levels_dict[symbol] = {
                'current_price': row['current_price'] or 0,  # 从数据库读取current_price
                'support_1': row['support_line_1'] or 0,
                'support_2': row['support_line_2'] or 0,
                'resistance_1': row['resistance_line_1'] or 0,
                'resistance_2': row['resistance_line_2'] or 0,
                'position_7d': row['position_7d'] or 0,
                'position_48h': row['position_48h'] or 0,
                'alert_7d_low': row['alert_7d_low'] or False,
                'alert_7d_high': row['alert_7d_high'] or False,
                'alert_48h_low': row['alert_48h_low'] or False,
                'alert_48h_high': row['alert_48h_high'] or False,
                'support_1_days': row['support_1_days'] or 0,
                'support_2_hours': row['support_2_hours'] or 0,
                'resistance_1_days': row['resistance_1_days'] or 0,
                'resistance_2_hours': row['support_2_hours'] or 0,
                'baseline_price_24h': row['baseline_price_24h'] or 0,
                'price_change_24h': row['price_change_24h'] or 0,
                'change_percent_24h': row['change_percent_24h'] or 0
            }
        
        # 构建结果：所有27个币种
        result_data = []
        for symbol in MONITORED_SYMBOLS:
            alert_info = alert_dict.get(symbol, {})
            symbol_usdt = symbol.replace('-USDT-SWAP', 'USDT')
            
            # 优先使用alert_info中的支撑/压力线数据，如果没有则使用sr_levels_dict中的数据
            sr_data = sr_levels_dict.get(symbol_usdt, {})
            # 使用数据库中的current_price，而不是实时查询的价格（保持数据一致性）
            current_price = sr_data.get('current_price', 0) or price_dict.get(symbol, 0)
            support_1 = alert_info.get('support_1', 0) or sr_data.get('support_1', 0)
            support_2 = alert_info.get('support_2', 0) or sr_data.get('support_2', 0)
            resistance_1 = alert_info.get('resistance_1', 0) or sr_data.get('resistance_1', 0)
            resistance_2 = alert_info.get('resistance_2', 0) or sr_data.get('resistance_2', 0)
            
            # 计算距离百分比（使用实时价格）
            distance_to_support_1 = ((current_price - support_1) / support_1) * 100 if support_1 > 0 else 0
            distance_to_support_2 = ((current_price - support_2) / support_2) * 100 if support_2 > 0 else 0
            distance_to_resistance_1 = ((resistance_1 - current_price) / current_price) * 100 if current_price > 0 else 0
            distance_to_resistance_2 = ((resistance_2 - current_price) / current_price) * 100 if current_price > 0 else 0
            
            coin_data = {
                'symbol': symbol_usdt,
                'current_price': current_price,
                'support_line_1': support_1,
                'support_line_2': support_2,
                'resistance_line_1': resistance_1,
                'resistance_line_2': resistance_2,
                'distance_to_support_1': distance_to_support_1,
                'distance_to_support_2': distance_to_support_2,
                'distance_to_resistance_1': distance_to_resistance_1,
                'distance_to_resistance_2': distance_to_resistance_2,
                'position_7d': sr_data.get('position_7d', 0),  # 7天位置百分比
                'position_48h': sr_data.get('position_48h', 0),  # 48小时位置百分比
                'support_1_days': sr_data.get('support_1_days', 0),  # 7天最低价发生在N天前
                'support_2_hours': sr_data.get('support_2_hours', 0),  # 48h最低价发生在N小时前
                'resistance_1_days': sr_data.get('resistance_1_days', 0),  # 7天最高价发生在N天前
                'resistance_2_hours': sr_data.get('resistance_2_hours', 0),  # 48h最高价发生在N小时前
                'alert_7d_low': sr_data.get('alert_7d_low', False),  # 7天低位预警
                'alert_7d_high': sr_data.get('alert_7d_high', False),  # 7天高位预警
                'alert_48h_low': sr_data.get('alert_48h_low', False),  # 48h低位预警
                'alert_48h_high': sr_data.get('alert_48h_high', False),  # 48h高位预警
                'baseline_price_24h': sr_data.get('baseline_price_24h', 0),  # 今日基准价格（北京时间0点）
                'price_change_24h': sr_data.get('price_change_24h', 0),  # 24小时涨跌额
                'change_percent_24h': sr_data.get('change_percent_24h', 0),  # 24小时涨跌幅%
                'position_s2_r1': alert_info.get('position_s2_r1'),
                'position_s1_r2': alert_info.get('position_s1_r2'),
                'position_s1_r2_upper': alert_info.get('position_s1_r2_upper'),
                'position_s1_r1': alert_info.get('position_s1_r1'),
                'alert_scenario_1': alert_info.get('alert_scenario_1', False),
                'alert_scenario_2': alert_info.get('alert_scenario_2', False),
                'alert_scenario_3': alert_info.get('alert_scenario_3', False),
                'alert_scenario_4': alert_info.get('alert_scenario_4', False),
                'alert_triggered': any([
                    alert_info.get('alert_scenario_1', False),
                    alert_info.get('alert_scenario_2', False),
                    alert_info.get('alert_scenario_3', False),
                    alert_info.get('alert_scenario_4', False)
                ]),
                'record_time': update_time
            }
            result_data.append(coin_data)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result_data,
            'count': len(result_data),
            'update_time': update_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/support-resistance/history/<symbol>')
def api_support_resistance_history(symbol):
    """获取指定币种的历史支撑压力线数据"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                symbol,
                current_price,
                support_line_1,
                support_line_2,
                resistance_line_1,
                resistance_line_2,
                distance_to_support_1,
                distance_to_support_2,
                distance_to_resistance_1,
                distance_to_resistance_2,
                record_time
            FROM support_resistance_levels
            WHERE symbol = ?
            AND datetime(record_time) >= datetime('now', '+8 hours', ? || ' hours')
            ORDER BY record_time DESC
        ''', (symbol, -hours))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'symbol': row['symbol'],
                'current_price': row['current_price'],
                'support_line_1': row['support_line_1'],
                'support_line_2': row['support_line_2'],
                'resistance_line_1': row['resistance_line_1'],
                'resistance_line_2': row['resistance_line_2'],
                'distance_to_support_1': row['distance_to_support_1'],
                'distance_to_support_2': row['distance_to_support_2'],
                'distance_to_resistance_1': row['distance_to_resistance_1'],
                'distance_to_resistance_2': row['distance_to_resistance_2'],
                'record_time': row['record_time']
            })
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/support-resistance/snapshots')
def api_support_resistance_snapshots():
    """获取支撑压力线快照历史数据（用于时间轴和趋势图）"""
    try:
        import json
        from datetime import datetime, timedelta
        import pytz
        
        date = request.args.get('date')  # 格式: 2025-12-13
        start_hour = request.args.get('start_hour', type=int)  # 0-23
        end_hour = request.args.get('end_hour', type=int)  # 0-23
        start_time = request.args.get('start_time')  # 格式: 2025-12-13 00:00:00
        end_time = request.args.get('end_time')  # 格式: 2025-12-13 12:00:00
        get_all = request.args.get('all', 'false').lower() == 'true'  # 获取所有历史数据
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询条件
        if get_all:
            # 获取所有历史数据（用于全局趋势图）
            cursor.execute('''
                SELECT 
                    snapshot_time, snapshot_date,
                    scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                    scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                    total_coins
                FROM support_resistance_snapshots
                ORDER BY snapshot_time ASC
            ''')
        elif start_time and end_time:
            # 获取指定时间范围的数据（用于翻页查看）
            cursor.execute('''
                SELECT 
                    snapshot_time, snapshot_date,
                    scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                    scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                    total_coins
                FROM support_resistance_snapshots
                WHERE snapshot_time >= ? AND snapshot_time < ?
                ORDER BY snapshot_time ASC
            ''', (start_time, end_time))
        elif date and start_hour is not None and end_hour is not None:
            # 🆕 支持按小时范围查询（北京时间）
            # 注意：数据库存储的已经是北京时间，直接使用即可
            
            # 构造北京时间范围字符串
            beijing_start_str = f"{date} {start_hour:02d}:00:00"
            
            # 处理 end_hour = 24 的情况（24:00 = 次日 00:00）
            if end_hour >= 24:
                from datetime import timedelta
                beijing_start_dt = datetime.strptime(beijing_start_str, "%Y-%m-%d %H:%M:%S")
                beijing_end_dt = beijing_start_dt + timedelta(hours=(end_hour - start_hour))
                beijing_end_str = beijing_end_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                beijing_end_str = f"{date} {end_hour:02d}:00:00"
            
            cursor.execute('''
                SELECT 
                    snapshot_time, snapshot_date,
                    scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                    scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                    total_coins
                FROM support_resistance_snapshots
                WHERE snapshot_time >= ? AND snapshot_time < ?
                ORDER BY snapshot_time ASC
            ''', (beijing_start_str, beijing_end_str))
        elif date:
            # 获取指定日期的所有数据
            cursor.execute('''
                SELECT 
                    snapshot_time, snapshot_date,
                    scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                    scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                    total_coins
                FROM support_resistance_snapshots
                WHERE snapshot_date = ?
                ORDER BY snapshot_time ASC
            ''', (date,))
        else:
            # 获取最近12小时的数据
            cursor.execute('''
                SELECT 
                    snapshot_time, snapshot_date,
                    scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                    scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                    total_coins
                FROM support_resistance_snapshots
                WHERE snapshot_time >= datetime('now', '-12 hours')
                ORDER BY snapshot_time ASC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # 数据库中存储的已经是北京时间，直接使用
        data = []
        for row in rows:
            data.append({
                'snapshot_time': row['snapshot_time'],  # 数据库存储的是北京时间
                'snapshot_date': row['snapshot_date'],
                'scenario_1_count': row['scenario_1_count'],
                'scenario_2_count': row['scenario_2_count'],
                'scenario_3_count': row['scenario_3_count'],
                'scenario_4_count': row['scenario_4_count'],
                'scenario_1_coins': json.loads(row['scenario_1_coins']) if row['scenario_1_coins'] else [],
                'scenario_2_coins': json.loads(row['scenario_2_coins']) if row['scenario_2_coins'] else [],
                'scenario_3_coins': json.loads(row['scenario_3_coins']) if row['scenario_3_coins'] else [],
                'scenario_4_coins': json.loads(row['scenario_4_coins']) if row['scenario_4_coins'] else [],
                'total_coins': row['total_coins']
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'date': date,
            'start_time': start_time,
            'end_time': end_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/support-resistance/latest-signal')
def api_support_resistance_latest_signal():
    """获取最新快照数据并检测是否触发信号"""
    try:
        import json
        from datetime import datetime
        import pytz
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取最新的快照
        cursor.execute('''
            SELECT 
                snapshot_time, snapshot_date,
                scenario_1_count, scenario_2_count, scenario_3_count, scenario_4_count,
                scenario_1_coins, scenario_2_coins, scenario_3_coins, scenario_4_coins,
                total_coins
            FROM support_resistance_snapshots
            ORDER BY snapshot_time DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'message': '暂无快照数据'
            })
        
        # 注意：数据库中存储的已经是北京时间，不需要再次转换
        # 数据采集脚本使用 datetime.now(pytz.timezone('Asia/Shanghai')) 存储
        snapshot_time_str = row['snapshot_time']  # 已经是北京时间
        
        scenario_1 = row['scenario_1_count'] or 0
        scenario_2 = row['scenario_2_count'] or 0
        scenario_3 = row['scenario_3_count'] or 0
        scenario_4 = row['scenario_4_count'] or 0
        
        # 检测信号
        # 抄底信号：情况1 >= 8 AND 情况2 >= 8（两个条件都要满足）
        buy_signal = scenario_1 >= 8 and scenario_2 >= 8
        
        # 逃顶信号：(情况3 + 情况4) >= 8（总和满足即可）
        sell_signal = (scenario_3 + scenario_4) >= 8
        
        result = {
            'success': True,
            'snapshot_time': snapshot_time_str,  # 直接使用数据库中的北京时间
            'snapshot_date': row['snapshot_date'],
            'scenario_1_count': scenario_1,
            'scenario_2_count': scenario_2,
            'scenario_3_count': scenario_3,
            'scenario_4_count': scenario_4,
            'scenario_1_coins': json.loads(row['scenario_1_coins']) if row['scenario_1_coins'] else [],
            'scenario_2_coins': json.loads(row['scenario_2_coins']) if row['scenario_2_coins'] else [],
            'scenario_3_coins': json.loads(row['scenario_3_coins']) if row['scenario_3_coins'] else [],
            'scenario_4_coins': json.loads(row['scenario_4_coins']) if row['scenario_4_coins'] else [],
            'total_coins': row['total_coins'],
            'signals': {
                'buy': buy_signal,
                'sell': sell_signal,
                'buy_count': scenario_1 + scenario_2 if buy_signal else 0,
                'sell_count': scenario_3 + scenario_4 if sell_signal else 0
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/support-resistance/dates')
def api_support_resistance_dates():
    """获取有快照数据的所有日期列表"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT snapshot_date
            FROM support_resistance_snapshots
            ORDER BY snapshot_date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        dates = [row[0] for row in rows]
        
        return jsonify({
            'success': True,
            'dates': dates,
            'count': len(dates)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

# =====================================================
# OKEx K线指标系统 API路由
# =====================================================

@app.route('/kline-indicators')
def kline_indicators_page():
    """K线指标系统监控页面"""
    return render_template('kline_indicators.html')

@app.route('/api/kline-indicators/latest')
def api_kline_indicators_latest():
    """
    获取最新的技术指标数据
    
    参数：
        - symbol: 币种（可选，如BTC-USDT-SWAP）
        - timeframe: 时间周期（可选，5m或1h）
    """
    try:
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if symbol:
            conditions.append('symbol = ?')
            params.append(symbol)
        if timeframe:
            conditions.append('timeframe = ?')
            params.append(timeframe)
        
        # 构建WHERE子句
        if conditions:
            where_clause = f"WHERE {' AND '.join(conditions)} AND"
        else:
            where_clause = "WHERE"
        
        # 获取每个币种+时间周期的最新数据
        cursor.execute(f'''
            SELECT 
                symbol, timeframe, current_price, rsi_14, 
                sar, sar_position, sar_quadrant, sar_count_label,
                bb_upper, bb_middle, bb_lower, record_time
            FROM okex_technical_indicators
            {where_clause} id IN (
                SELECT MAX(id)
                FROM okex_technical_indicators
                GROUP BY symbol, timeframe
            )
            ORDER BY symbol, timeframe
        ''', params)
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'symbol': row['symbol'],
                'timeframe': row['timeframe'],
                'current_price': row['current_price'],
                'rsi_14': row['rsi_14'],
                'sar': row['sar'],
                'sar_position': row['sar_position'],
                'sar_quadrant': row['sar_quadrant'],
                'sar_count_label': row['sar_count_label'],
                'bb_upper': row['bb_upper'],
                'bb_middle': row['bb_middle'],
                'bb_lower': row['bb_lower'],
                'record_time': row['record_time']
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'timestamp': datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/kline-indicators/collector-status')
def api_kline_indicators_status():
    """获取采集器运行状态"""
    try:
        conn = sqlite3.connect('crypto_data.db', timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取最新采集时间
        cursor.execute('''
            SELECT MAX(record_time) as last_collection
            FROM okex_technical_indicators
        ''')
        row = cursor.fetchone()
        last_collection = row['last_collection'] if row else None
        
        # 统计数据量
        cursor.execute('SELECT COUNT(*) as count_indicators FROM okex_technical_indicators')
        count_indicators = cursor.fetchone()['count_indicators']
        
        # 统计不同时间周期的数量
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN timeframe = '5m' THEN 1 ELSE 0 END) as count_5m,
                SUM(CASE WHEN timeframe = '1H' THEN 1 ELSE 0 END) as count_1h
            FROM okex_technical_indicators
        ''')
        row = cursor.fetchone()
        count_5m = row['count_5m'] or 0
        count_1h = row['count_1h'] or 0
        
        conn.close()
        
        # 计算状态（数据库存储的是北京时间）
        if last_collection:
            # 数据库中的时间是北京时间，需要与北京时间比较
            import pytz
            beijing_tz = pytz.timezone('Asia/Shanghai')
            last_time = datetime.strptime(last_collection, '%Y-%m-%d %H:%M:%S')
            now_beijing = datetime.now(beijing_tz).replace(tzinfo=None)
            delta_minutes = (now_beijing - last_time).total_seconds() / 60
            status = 'running' if delta_minutes < 10 else 'stopped'
        else:
            status = 'not_started'
            delta_minutes = None
        
        return jsonify({
            'success': True,
            'status': status,
            'last_collection_time': last_collection,
            'minutes_since_last': round(delta_minutes, 1) if delta_minutes else None,
            'data_counts': {
                'kline_5m': count_5m,
                'kline_1h': count_1h,
                'indicators': count_indicators
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def cleanup_expired_signals():
    """
    清理2小时之前的过期信号
    将 is_valid 设置为 0
    """
    try:
        conn = sqlite3.connect('crypto_data.db', timeout=5.0)
        cursor = conn.cursor()
        
        from datetime import datetime, timedelta
        cutoff_time = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 清理买点4过期信号
        cursor.execute('''
            UPDATE buy_point_4_signals
            SET is_valid = 0
            WHERE is_valid = 1 AND confirm_time < ?
        ''', (cutoff_time,))
        buy_point_4_cleaned = cursor.rowcount
        
        # 清理卖点1过期信号
        cursor.execute('''
            UPDATE sell_point_1_signals
            SET is_valid = 0
            WHERE is_valid = 1 AND mark_time < ?
        ''', (cutoff_time,))
        sell_point_1_cleaned = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return {
            'buy_point_4_cleaned': buy_point_4_cleaned,
            'sell_point_1_cleaned': sell_point_1_cleaned
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/api/kline-indicators/signals')
def api_kline_indicators_signals():
    """
    返回K线指标信号（2小时时间窗口）
    数据完全从数据库读取，不进行实时检测
    - 买点4: 从 buy_point_4_signals 表读取（RSI < 20）
    - 卖点1: 从 sell_point_1_signals 表读取（RSI >= 60）
    """
    try:
        conn = sqlite3.connect('crypto_data.db', timeout=10.0)
        cursor = conn.cursor()
        
        from datetime import datetime, timedelta
        now = datetime.now()
        cutoff_time = (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 初始化信号容器
        signals = {
            'buy_point_4': [],      # 买点4（从数据库读取）
            'sell_point_1': []      # 卖点1（从数据库读取）
        }
        
        # 1. 读取买点4信号（不查询当前价格，使用信号时的价格）
        cursor.execute('''
            SELECT symbol, low_price, low_time, confirm_time, 
                   signal_generated_at, confirm_rsi
            FROM buy_point_4_signals
            WHERE is_valid = 1 
              AND confirm_rsi IS NOT NULL 
              AND confirm_rsi < 20
              AND confirm_time >= ?
            ORDER BY confirm_time DESC
            LIMIT 100
        ''', (cutoff_time,))
        
        for row in cursor.fetchall():
            signals['buy_point_4'].append({
                'symbol': row[0],
                'price': row[1],
                'low_7d': row[1],
                'low_time': row[2],
                'confirm_time': row[3],
                'signal_generated_at': row[4],
                'confirm_rsi': row[5],
                'current_price': row[1],  # 使用确认时的价格
                'distance': 0.0  # 信号时刻距离为0
            })
        
        # 2. 读取卖点1信号（不查询当前价格）
        cursor.execute('''
            SELECT symbol, high_price, high_time, mark_price, 
                   mark_time, mark_rsi, signal_generated_at
            FROM sell_point_1_signals
            WHERE is_valid = 1 
              AND mark_rsi IS NOT NULL 
              AND mark_rsi >= 60
              AND mark_time >= ?
            ORDER BY mark_time DESC
            LIMIT 100
        ''', (cutoff_time,))
        
        for row in cursor.fetchall():
            signals['sell_point_1'].append({
                'symbol': row[0],
                'high_price': row[1],
                'high_time': row[2],
                'mark_price': row[3],
                'mark_time': row[4],
                'mark_rsi': row[5],
                'signal_generated_at': row[6],
                'current_price': row[3],  # 使用标记时的价格
                'distance': 0.0  # 信号时刻距离为0
            })
        
        conn.close()
        
        # 统计信号数量
        signal_counts = {k: len(v) for k, v in signals.items()}
        
        # 异步清理过期信号（不阻塞响应）
        import threading
        threading.Thread(target=cleanup_expired_signals, daemon=True).start()
        
        return jsonify({
            'success': True,
            'data': {
                'signals': signals,
                'counts': signal_counts,
                'update_time': now.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/kline-indicators-tv/latest')
def api_kline_indicators_tv_latest():
    """
    获取TradingView直接获取的K线指标数据（不计算）
    支持参数: symbol, timeframe
    数据源: TradingView (OKX交易所)
    """
    try:
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if symbol:
            conditions.append('symbol = ?')
            params.append(symbol)
        if timeframe:
            conditions.append('timeframe = ?')
            params.append(timeframe)
        
        # 构建WHERE子句
        if conditions:
            where_clause = f"WHERE {' AND '.join(conditions)}"
        else:
            where_clause = ""
        
        # 获取每个币种+时间周期的最新数据
        query = f'''
            SELECT 
                symbol, timeframe, current_price, rsi_14, 
                sar, bb_upper, bb_middle, bb_lower,
                ema_10, ema_20, recommendation,
                buy_signals, sell_signals, neutral_signals,
                record_time
            FROM okex_tv_indicators
            {where_clause}
            ORDER BY symbol, timeframe
        '''
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            # Calculate SAR position
            sar_position = None
            if row['sar'] and row['current_price']:
                sar_position = 'bullish' if row['current_price'] > row['sar'] else 'bearish'
            
            # Calculate BB middle if not provided
            bb_middle = row['bb_middle']
            if not bb_middle and row['bb_upper'] and row['bb_lower']:
                bb_middle = (row['bb_upper'] + row['bb_lower']) / 2
            
            data.append({
                'symbol': row['symbol'],
                'timeframe': row['timeframe'],
                'current_price': row['current_price'],
                'rsi_14': row['rsi_14'],
                'sar': row['sar'],
                'sar_position': sar_position,
                'bb_upper': row['bb_upper'],
                'bb_middle': bb_middle,
                'bb_lower': row['bb_lower'],
                'ema_10': row['ema_10'],
                'ema_20': row['ema_20'],
                'recommendation': row['recommendation'],
                'buy_signals': row['buy_signals'],
                'sell_signals': row['sell_signals'],
                'neutral_signals': row['neutral_signals'],
                'record_time': row['record_time'],
                'data_source': 'TradingView (直接获取, 不计算)'
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'data_source': 'TradingView API (OKX Exchange)',
            'note': '所有技术指标均直接从TradingView获取，不进行本地计算',
            'timestamp': datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/kline-indicators-tv/collector-status')
def api_kline_indicators_tv_status():
    """获取TradingView指标采集器运行状态"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='okex_tv_collector_status'
        ''')
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': True,
                'status': 'not_initialized',
                'message': 'TradingView collector not initialized yet'
            })
        
        # 获取采集状态
        cursor.execute('''
            SELECT last_collect_time, total_indicators_count, status
            FROM okex_tv_collector_status
            WHERE id = 1
        ''')
        
        row = cursor.fetchone()
        
        # 统计数据量
        cursor.execute('SELECT COUNT(*) FROM okex_tv_indicators')
        count_indicators = cursor.fetchone()[0]
        
        conn.close()
        
        status = row['status'] if row else 'stopped'
        last_collection = row['last_collect_time'] if row else None
        
        return jsonify({
            'success': True,
            'status': status,
            'last_collection_time': last_collection,
            'total_indicators': count_indicators,
            'data_source': 'TradingView (直接获取)',
            'note': 'RSI, SAR, 布林带均直接从TradingView获取，不计算'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 币种详情页面 ====================

@app.route('/symbol/<symbol>')
def symbol_detail(symbol):
    """币种详情页面 - 自动重定向到v6以避开浏览器缓存"""
    from flask import redirect, url_for
    return redirect(url_for('symbol_detail_v6', symbol=symbol), code=302)

@app.route('/api/symbol/<symbol>/kline')
def api_symbol_kline(symbol):
    """获取币种K线数据（10天）- 使用okex_technical_indicators表"""
    try:
        timeframe = request.args.get('timeframe', '5m')  # 5m 或 1H
        
        # 将symbol转换为标准格式
        if not symbol.endswith('-USDT-SWAP'):
            symbol = f"{symbol}-USDT-SWAP"
        
        # 转换timeframe格式: 5m -> 5m, 1h -> 1H (数据库中使用大写H)
        db_timeframe = timeframe.upper() if timeframe == '1h' else timeframe
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 根据时间周期设置limit
        if timeframe == '5m':
            # 10天的5分钟K线 = 10 * 24 * 12 = 2880根
            limit = 2880
        else:  # 1h
            # 10天的1小时K线 = 10 * 24 = 240根
            limit = 240
        
        # 从okex_kline_ohlc表获取真实的OHLC K线数据
        # 先按时间降序取最新的N条，然后反转为升序
        cursor.execute('''
            SELECT timestamp, open, high, low, close, volume
            FROM (
                SELECT timestamp, open, high, low, close, volume
                FROM okex_kline_ohlc
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp DESC
                LIMIT ?
            )
            ORDER BY timestamp ASC
        ''', (symbol, db_timeframe, limit))
        
        rows = cursor.fetchall()
        
        # 如果OHLC表没有数据，回退到indicators_history表
        if not rows:
            cursor.execute('''
                SELECT timestamp, current_price
                FROM (
                    SELECT timestamp, current_price
                    FROM okex_indicators_history
                    WHERE symbol = ? AND timeframe = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
                ORDER BY timestamp ASC
            ''', (symbol, db_timeframe, limit))
            
            rows_indicators = cursor.fetchall()
            kline_data = []
            
            for i, row in enumerate(rows_indicators):
                timestamp = int(row[0]) if row[0] else 0
                close_price = float(row[1]) if row[1] else 0
                
                # 模拟OHLC
                open_price = close_price * (1 + 0.001 * (i % 3 - 1))
                high_price = close_price * 1.002
                low_price = close_price * 0.998
                volume = close_price * 10
                
                kline_data.append({
                    'timestamp': timestamp,
                    'data': [open_price, high_price, low_price, close_price],  # 标准K线格式: OHLC
                    'volume': volume
                })
        else:
            # 使用真实OHLC数据
            kline_data = []
            for row in rows:
                timestamp = int(row[0]) if row[0] else 0
                open_price = float(row[1]) if row[1] else 0
                high_price = float(row[2]) if row[2] else 0
                low_price = float(row[3]) if row[3] else 0
                close_price = float(row[4]) if row[4] else 0
                volume = float(row[5]) if row[5] else 0
                
                kline_data.append({
                    'timestamp': timestamp,
                    'data': [open_price, high_price, low_price, close_price],  # 标准K线格式: OHLC
                    'volume': volume
                })
        
        # 查询技术标记数据（窄幅震荡、高低点、SAR、RSI、布林带等）
        cursor.execute('''
            SELECT timestamp, is_narrow_range, change_percent, range_percent, consecutive_count,
                   is_7d_high, is_7d_low, is_48h_high, is_48h_low,
                   rsi_14, sar, sar_position, sar_quadrant, sar_count_label,
                   bb_upper, bb_middle, bb_lower, is_buy_point_4
            FROM kline_technical_markers
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp ASC
        ''', (symbol, db_timeframe))
        
        marker_rows = cursor.fetchall()
        markers_dict = {}
        for marker_row in marker_rows:
            ts = int(marker_row[0]) if marker_row[0] else 0
            markers_dict[ts] = {
                'is_narrow_range': bool(marker_row[1]),
                'change_percent': float(marker_row[2]) if marker_row[2] else 0,
                'range_percent': float(marker_row[3]) if marker_row[3] else 0,
                'consecutive_count': int(marker_row[4]) if marker_row[4] else 0,
                'is_7d_high': bool(marker_row[5]),
                'is_7d_low': bool(marker_row[6]),
                'is_48h_high': bool(marker_row[7]),
                'is_48h_low': bool(marker_row[8]),
                'rsi_14': float(marker_row[9]) if marker_row[9] else None,
                'sar': float(marker_row[10]) if marker_row[10] else None,
                'sar_position': marker_row[11],
                'sar_quadrant': int(marker_row[12]) if marker_row[12] else None,
                'sar_count_label': marker_row[13],
                'bb_upper': float(marker_row[14]) if marker_row[14] else None,
                'bb_middle': float(marker_row[15]) if marker_row[15] else None,
                'bb_lower': float(marker_row[16]) if marker_row[16] else None,
                'is_buy_point_4': bool(marker_row[17])
            }
        
        # 将标记数据合并到K线数据中
        for item in kline_data:
            ts = item['timestamp']
            if ts in markers_dict:
                item['markers'] = markers_dict[ts]
        
        conn.close()
        
        # 创建响应对象并添加缓存头
        response = jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'data': kline_data,
            'count': len(kline_data)
        })
        
        # 添加HTTP缓存头（缓存60秒，因为数据每60秒更新一次）
        response.headers['Cache-Control'] = 'public, max-age=60'
        response.headers['Vary'] = 'Accept-Encoding'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/symbol/<symbol>/indicators')
def api_symbol_indicators(symbol):
    """获取币种技术指标数据 - 使用okex_technical_indicators表"""
    try:
        timeframe = request.args.get('timeframe', '5m')
        
        # 将symbol转换为标准格式
        if not symbol.endswith('-USDT-SWAP'):
            symbol = f"{symbol}-USDT-SWAP"
        
        # 转换timeframe格式: 5m -> 5m, 1h -> 1H
        db_timeframe = timeframe.upper() if timeframe == '1h' else timeframe
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 设置limit
        limit = 2880 if timeframe == '5m' else 240
        
        # 从okex_indicators_history表获取历史指标数据
        cursor.execute('''
            SELECT created_at, current_price, rsi_14, sar, sar_position, sar_count_label,
                   bb_upper, bb_middle, bb_lower, timestamp
            FROM okex_indicators_history
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (symbol, db_timeframe, limit))
        
        rows = cursor.fetchall()
        
        indicators = []
        for row in rows:
            # 使用数据库中的timestamp字段（毫秒）
            timestamp = int(row[9]) if row[9] else 0
            
            indicators.append({
                'timestamp': timestamp,
                'price': float(row[1]) if row[1] else None,
                'rsi': float(row[2]) if row[2] else None,
                'sar': float(row[3]) if row[3] else None,
                'sar_position': row[4],
                'sar_label': row[5],
                'bb_upper': float(row[6]) if row[6] else None,
                'bb_middle': float(row[7]) if row[7] else None,
                'bb_lower': float(row[8]) if row[8] else None,
                'time_str': row[0]  # 保留时间字符串用于调试
            })
        
        conn.close()
        
        # 创建响应对象并添加缓存头
        response = jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'data': indicators,
            'count': len(indicators)
        })
        
        # 添加HTTP缓存头（缓存60秒，因为数据每60秒更新一次）
        response.headers['Cache-Control'] = 'public, max-age=60'
        response.headers['Vary'] = 'Accept-Encoding'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/signals/recent')
def api_signals_recent():
    """获取最近2小时内的交易信号，按类型分类"""
    try:
        from datetime import datetime, timedelta
        import json
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 计算2小时前的时间
        two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取2小时内的信号
        cursor.execute('''
            SELECT record_time, long_signals, short_signals, 
                   today_new_high, today_new_low, raw_data
            FROM trading_signals
            WHERE record_time >= ?
            ORDER BY record_time DESC
        ''', (two_hours_ago,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # 分类统计
        signals_by_type = {
            'long': [],  # 做多信号
            'short': [],  # 做空信号
            'new_high': [],  # 新高信号
            'new_low': []  # 新低信号
        }
        
        for row in rows:
            record_time = row[0]
            long_count = row[1] or 0
            short_count = row[2] or 0
            new_high = row[3] or 0
            new_low = row[4] or 0
            raw_data = json.loads(row[5]) if row[5] else {}
            
            if long_count > 0:
                signals_by_type['long'].append({
                    'time': record_time,
                    'count': long_count,
                    'detail': raw_data.get('breakdown', {})
                })
            
            if short_count > 0:
                signals_by_type['short'].append({
                    'time': record_time,
                    'count': short_count,
                    'detail': raw_data.get('breakdown', {})
                })
            
            if new_high > 0:
                signals_by_type['new_high'].append({
                    'time': record_time,
                    'count': new_high
                })
            
            if new_low > 0:
                signals_by_type['new_low'].append({
                    'time': record_time,
                    'count': new_low
                })
        
        # 计算汇总
        summary = {
            'long_total': sum(s['count'] for s in signals_by_type['long']),
            'short_total': sum(s['count'] for s in signals_by_type['short']),
            'new_high_total': sum(s['count'] for s in signals_by_type['new_high']),
            'new_low_total': sum(s['count'] for s in signals_by_type['new_low']),
            'time_range': two_hours_ago
        }
        
        return jsonify({
            'success': True,
            'signals': signals_by_type,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/symbol/<symbol>/extremes')
def api_symbol_extremes(symbol):
    """获取币种的48小时和7天高低点"""
    try:
        from datetime import datetime, timedelta
        
        timeframe = request.args.get('timeframe', '5m')
        
        # 将symbol转换为标准格式
        if not symbol.endswith('-USDT-SWAP'):
            symbol = f"{symbol}-USDT-SWAP"
        
        # 转换timeframe格式
        db_timeframe = timeframe.upper() if timeframe == '1h' else timeframe
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 计算时间范围（毫秒时间戳）
        now_ms = int(datetime.now().timestamp() * 1000)
        hours_48_ago_ms = int((datetime.now() - timedelta(hours=48)).timestamp() * 1000)
        days_7_ago_ms = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
        
        # 获取48小时内的高低点
        cursor.execute('''
            SELECT timestamp, open, high, low, close
            FROM okex_kline_ohlc
            WHERE symbol = ? AND timeframe = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (symbol, db_timeframe, hours_48_ago_ms))
        
        rows_48h = cursor.fetchall()
        
        # 获取7天内的高低点
        cursor.execute('''
            SELECT timestamp, open, high, low, close
            FROM okex_kline_ohlc
            WHERE symbol = ? AND timeframe = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (symbol, db_timeframe, days_7_ago_ms))
        
        rows_7d = cursor.fetchall()
        conn.close()
        
        # 计算48小时高低点
        extremes_48h = {'high': None, 'low': None, 'high_time': None, 'low_time': None}
        if rows_48h:
            max_price = max(row[2] for row in rows_48h)  # high
            min_price = min(row[3] for row in rows_48h)  # low
            
            for row in rows_48h:
                if row[2] == max_price:
                    extremes_48h['high'] = max_price
                    extremes_48h['high_time'] = row[0]
                if row[3] == min_price:
                    extremes_48h['low'] = min_price
                    extremes_48h['low_time'] = row[0]
        
        # 计算7天高低点
        extremes_7d = {'high': None, 'low': None, 'high_time': None, 'low_time': None}
        if rows_7d:
            max_price = max(row[2] for row in rows_7d)  # high
            min_price = min(row[3] for row in rows_7d)  # low
            
            for row in rows_7d:
                if row[2] == max_price:
                    extremes_7d['high'] = max_price
                    extremes_7d['high_time'] = row[0]
                if row[3] == min_price:
                    extremes_7d['low'] = min_price
                    extremes_7d['low_time'] = row[0]
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'extremes_48h': extremes_48h,
            'extremes_7d': extremes_7d
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/test-chart')
def test_chart():
    """测试K线图渲染"""
    with open('test_chart_render.html', 'r', encoding='utf-8') as f:
        return f.read()

# ==================== 新版本路由 - 强制刷新 ====================

@app.route('/symbol/<symbol>/v6')
def symbol_detail_v6(symbol):
    """币种详情页面 v6.0 - 全新路由避开缓存"""
    from datetime import datetime
    from flask import make_response
    
    cache_buster = datetime.now().strftime('%Y%m%d%H%M%S')
    response = make_response(render_template('symbol_detail_v6.html', symbol=symbol, cache_buster=cache_buster))
    
    # 禁用HTML页面缓存，确保每次都加载最新代码
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/symbol/<symbol>/v7')
def symbol_detail_v7(symbol):
    """币种详情页面 v7.0 - 全新路由避开缓存，简化调试"""
    from datetime import datetime
    from flask import make_response
    
    cache_buster = datetime.now().strftime('%Y%m%d%H%M%S')
    response = make_response(render_template('symbol_detail_v7.html', symbol=symbol, cache_buster=cache_buster))
    
    # 禁用HTML页面缓存，确保每次都加载最新代码
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/symbol/<symbol>/v8')
def symbol_detail_v8(symbol):
    """币种详情页面 v8.0 - 彻底避开所有浏览器缓存"""
    from datetime import datetime
    from flask import make_response
    
    cache_buster = datetime.now().strftime('%Y%m%d%H%M%S')
    response = make_response(render_template('symbol_detail_v8.html', symbol=symbol, cache_buster=cache_buster))
    
    # 最强缓存禁用策略
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response

@app.route('/kline/<symbol>')
def kline_chart(symbol):
    """全新的K线图路由 - 完全独立的地址"""
    from datetime import datetime
    from flask import make_response
    
    cache_buster = datetime.now().strftime('%Y%m%d%H%M%S')
    response = make_response(render_template('kline_chart.html', symbol=symbol, cache_buster=cache_buster))
    
    # 强制禁用所有缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response

@app.route('/test-xlm-data')
def test_xlm_data():
    """XLM数据诊断测试页"""
    return render_template('test_xlm_data.html')

@app.route('/chart/<symbol>')
def chart_new(symbol):
    """全新K线图 - 从零开始，简单清晰"""
    from datetime import datetime
    from flask import make_response
    
    cache_buster = datetime.now().strftime('%Y%m%d%H%M%S')
    response = make_response(render_template('chart_new.html', symbol=symbol, cache_buster=cache_buster))
    
    # 强制禁用所有缓存
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

# ==================== Google Drive 监控状态 API ====================

@app.route('/gdrive-monitor-status')
def gdrive_monitor_status_page():
    """Google Drive 监控状态页面 - 11分钟超时保险机制可视化"""
    return render_template('gdrive_monitor_status.html')

@app.route('/api/gdrive-monitor/status')
def api_gdrive_monitor_status():
    """获取 Google Drive 监控状态的实时数据"""
    import os
    import json
    from datetime import datetime
    import pytz
    import re
    import requests
    from bs4 import BeautifulSoup
    
    try:
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
        # 读取配置文件
        config_file = '/home/user/webapp/daily_folder_config.json'
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 🆕 扫描 Google Drive 中的实际文件
        gdrive_dates = {}
        gdrive_scan_error = None
        try:
            ROOT_FOLDER_ID = "1jFGGlGP5KEVhAxpCNxFIYEFI5-cDOBjM"
            url = f"https://drive.google.com/embeddedfolderview?id={ROOT_FOLDER_ID}"
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            all_links = soup.find_all('a', href=True)
            pattern = re.compile(r'(\d{4}-\d{2}-\d{2})_(\d{4})\.txt')
            
            for link in all_links:
                text = link.get_text(strip=True)
                match = pattern.match(text)
                if match:
                    date = match.group(1)
                    if date not in gdrive_dates:
                        gdrive_dates[date] = 0
                    gdrive_dates[date] += 1
        except Exception as e:
            gdrive_scan_error = str(e)
        
        # 读取日志文件获取最新状态
        log_file = '/home/user/webapp/gdrive_final_detector.log'
        latest_file = None
        latest_file_time = None
        check_count = 0
        last_file_found_time = None
        recovery_count = 0
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 分析日志
                for line in reversed(lines[-500:]):  # 只看最近500行
                    # 查找最新文件
                    if '最新文件名 =' in line and not latest_file:
                        match = re.search(r'最新文件名 = (.+\.txt)', line)
                        if match:
                            latest_file = match.group(1)
                            # 提取时间戳
                            time_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                            if time_match:
                                latest_file_time = time_match.group(1)
                    
                    # 查找检查次数
                    if '检查 #' in line:
                        match = re.search(r'检查 #(\d+)', line)
                        if match:
                            check_count = max(check_count, int(match.group(1)))
                    
                    # 查找恢复触发
                    if '触发11分钟超时恢复机制' in line:
                        recovery_count += 1
                    
                    # 查找最后找到文件的时间
                    if '找到' in line and 'TXT文件' in line and not last_file_found_time:
                        match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                        if match:
                            last_file_found_time = match.group(1)
        
        # 计算距上次找到文件的时间
        time_since_last_file = 0
        if last_file_found_time:
            try:
                last_time = datetime.strptime(last_file_found_time, '%Y-%m-%d %H:%M:%S')
                last_time = beijing_tz.localize(last_time)
                time_since_last_file = (now - last_time).total_seconds()
            except:
                pass
        
        # 获取数据库记录数
        db_records = 0
        try:
            import sqlite3
            conn = sqlite3.connect('crypto_data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM crypto_snapshots WHERE snapshot_date = ?", (now.strftime('%Y-%m-%d'),))
            db_records = cursor.fetchone()[0]
            conn.close()
        except:
            pass
        
        # 计算系统运行时长 (从最早的日志时间戳开始)
        uptime_seconds = 0
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', first_line)
                if match:
                    start_time = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    start_time = beijing_tz.localize(start_time)
                    uptime_seconds = (now - start_time).total_seconds()
        
        # 🆕 判断数据源状态
        today_str = now.strftime('%Y-%m-%d')
        data_source_status = 'unknown'
        data_source_message = ''
        
        if gdrive_dates:
            latest_gdrive_date = max(gdrive_dates.keys())
            if latest_gdrive_date == today_str:
                data_source_status = 'active'
                data_source_message = f'✅ 数据源正常，今天有 {gdrive_dates[today_str]} 个文件'
            else:
                days_old = (datetime.strptime(today_str, '%Y-%m-%d') - datetime.strptime(latest_gdrive_date, '%Y-%m-%d')).days
                data_source_status = 'stale'
                data_source_message = f'⚠️  数据源已停更 {days_old} 天，最新数据：{latest_gdrive_date}'
        elif gdrive_scan_error:
            data_source_status = 'error'
            data_source_message = f'❌ 无法访问 Google Drive: {gdrive_scan_error}'
        else:
            data_source_status = 'empty'
            data_source_message = '❌ Google Drive 中没有任何数据文件'
        
        return jsonify({
            'success': True,
            'time_since_last_file': time_since_last_file,
            'current_folder_id': config.get('folder_id', 'N/A'),
            'folder_date': config.get('current_date', '--'),
            'latest_file': latest_file or '--',
            'file_time': latest_file_time or '--',
            'gdrive_dates': gdrive_dates,  # 🆕 Google Drive 中的日期分布
            'data_source_status': data_source_status,  # 🆕 数据源状态
            'data_source_message': data_source_message,  # 🆕 数据源状态消息
            'today_date': today_str,  # 🆕 当前日期
            'root_folder_odd': config.get('root_folder_odd', 'N/A'),  # 🆕 单数日期父文件夹
            'root_folder_even': config.get('root_folder_even', 'N/A'),  # 🆕 双数日期父文件夹
            'recovery_count': recovery_count,
            'check_count': check_count,
            'files_found': check_count,  # 简化处理
            'db_records': db_records,
            'last_update': now.strftime('%H:%M:%S'),
            'uptime_seconds': uptime_seconds,
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 每日00:10任务状态 API ====================

@app.route('/daily-tasks-status')
def daily_tasks_status_page():
    """每日00:10任务执行状态页面"""
    return render_template('daily_tasks_status.html')

@app.route('/api/daily-tasks/status')
def api_daily_tasks_status():
    """获取每日00:10任务的执行状态"""
    import os
    import json
    from datetime import datetime
    import pytz
    
    try:
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        today_str = now.strftime('%Y-%m-%d')
        
        # 读取配置文件
        config_file = '/home/user/webapp/daily_folder_config.json'
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 父文件夹更新任务状态
        parent_folder_update = {
            'status': config.get('auto_update_status', 'pending'),
            'last_update': config.get('last_auto_update', '--'),
            'parent_folder_id': config.get('root_folder_odd') or config.get('root_folder_even', '--'),
            'child_folder_id': config.get('folder_id', '--'),
            'url': config.get('parent_folder_url', '--')
        }
        
        # 清理任务状态
        cleanup = {
            'last_cleanup': config.get('last_cleanup', None),
            'cleanup_reason': config.get('cleanup_reason', '--'),
            'root_folder_odd': config.get('root_folder_odd'),
            'root_folder_even': config.get('root_folder_even')
        }
        
        return jsonify({
            'success': True,
            'today_date': today_str,
            'parent_folder_update': parent_folder_update,
            'cleanup': cleanup
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-tasks/logs')
def api_daily_tasks_logs():
    """获取每日任务的执行日志"""
    import os
    
    try:
        log_file = '/home/user/webapp/parent_folder_update.log'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 只返回最近100行
                logs = [line.rstrip() for line in lines[-100:]]
        
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 文件夹更新监控 API ====================

@app.route('/folder-update-monitor')
def folder_update_monitor():
    """文件夹更新监控页面"""
    return render_template('folder_update_monitor.html')

@app.route('/api/folder-update-status')
def api_folder_update_status():
    """获取文件夹更新状态"""
    import os
    import json
    
    try:
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        today_str = now.strftime('%Y-%m-%d')
        
        # 读取配置文件
        config_file = '/home/user/webapp/daily_folder_config.json'
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        config_date = config.get('current_date', 'unknown')
        need_update = config_date != today_str
        
        return jsonify({
            'success': True,
            'data': {
                'config_date': config_date,
                'today_date': today_str,
                'folder_id': config.get('folder_id', 'N/A'),
                'latest_txt': config.get('latest_txt', 'N/A'),
                'txt_count': config.get('txt_count', 0),
                'last_updated': config.get('last_updated', 'N/A'),
                'need_update': need_update,
                'message': '配置日期与今天不匹配' if need_update else '配置正常'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/trigger-folder-update', methods=['POST'])
def api_trigger_folder_update():
    """触发文件夹更新"""
    import subprocess
    import os
    
    try:
        script_path = '/home/user/webapp/auto_update_today_folder.py'
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'message': '更新脚本不存在'
            }), 404
        
        # 执行更新脚本
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # 读取更新后的配置
            config_file = '/home/user/webapp/daily_folder_config.json'
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return jsonify({
                'success': True,
                'data': {
                    'folder_id': config.get('folder_id'),
                    'date': config.get('current_date'),
                    'latest_txt': config.get('latest_txt'),
                    'txt_count': config.get('txt_count', 0)
                },
                'message': '更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'更新失败: {result.stderr}'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': '更新超时（60秒）'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/list-recent-folders')
def api_list_recent_folders():
    """列出最近的文件夹"""
    import requests
    from bs4 import BeautifulSoup
    import re
    
    try:
        parent_folder_id = "1j8YV6KysUCmgcmASFOxztWWIE1Vq-kYV"
        url = f"https://drive.google.com/embeddedfolderview?id={parent_folder_id}"
        
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        folders = []
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if '/folders/' in href:
                match = re.search(r'/folders/([a-zA-Z0-9_-]+)', href)
                if match:
                    folder_id = match.group(1)
                    # 检查是否是日期文件夹
                    if re.search(r'\d{4}-\d{2}-\d{2}', text):
                        folders.append({
                            'name': text,
                            'id': folder_id
                        })
        
        # 排序（最新的在前）
        folders.sort(key=lambda x: x['name'], reverse=True)
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        today = datetime.now(beijing_tz).strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'data': {
                'folders': folders[:10],  # 只返回最近10个
                'today': today
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/get-update-log')
def api_get_update_log():
    """获取更新日志"""
    import os
    
    try:
        log_file = '/home/user/webapp/auto_update_folder.log'
        log_content = ''
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 只返回最近200行
                log_content = ''.join(lines[-200:])
        
        return jsonify({
            'success': True,
            'data': {
                'log': log_content or '暂无日志'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# 旧的telegram-dashboard路由已废弃，使用下方新版本
# @app.route('/telegram-dashboard')
# def telegram_dashboard():
#     """Telegram信号推送系统监控面板"""
#     import time
#     cache_buster = int(time.time())
#     return render_template('telegram_dashboard.html', cache_buster=cache_buster)

@app.route('/api/telegram/status')
def telegram_status():
    """获取Telegram监控系统状态"""
    try:
        import subprocess
        import os
        
        # 检查进程是否运行（检查telegram_signal_system.py而不是tg_signal_monitor.py）
        result = subprocess.run(
            ['pgrep', '-f', 'telegram_signal_system.py'],
            capture_output=True,
            text=True
        )
        
        is_running = bool(result.stdout.strip())
        pid = result.stdout.strip() if is_running else None
        
        # 获取数据库统计
        db_stats = {}
        if os.path.exists('tg_signals.db'):
            conn = sqlite3.connect('tg_signals.db', timeout=5.0)
            cursor = conn.cursor()
            
            # 获取总发送数
            cursor.execute("SELECT COUNT(*) FROM signal_history")
            total_sent = cursor.fetchone()[0]
            
            # 获取最近1小时发送数
            cursor.execute("""
                SELECT COUNT(*) FROM signal_history 
                WHERE sent_time >= datetime('now', '-1 hour', 'localtime')
            """)
            sent_1h = cursor.fetchone()[0]
            
            # 获取今天发送数
            cursor.execute("""
                SELECT COUNT(*) FROM signal_history 
                WHERE date(sent_time) = date('now', 'localtime')
            """)
            sent_today = cursor.fetchone()[0]
            
            # 获取各类信号统计
            cursor.execute("""
                SELECT signal_type, COUNT(*) as count
                FROM signal_history
                GROUP BY signal_type
            """)
            signal_counts = dict(cursor.fetchall())
            
            # 获取最新发送时间
            cursor.execute("""
                SELECT sent_time FROM signal_history 
                ORDER BY created_at DESC LIMIT 1
            """)
            last_sent = cursor.fetchone()
            last_sent_time = last_sent[0] if last_sent else None
            
            conn.close()
            
            db_stats = {
                'total_sent': total_sent,
                'sent_1h': sent_1h,
                'sent_today': sent_today,
                'signal_counts': signal_counts,
                'last_sent_time': last_sent_time
            }
        
        # 返回扁平化的数据结构，符合前端期待的格式
        return jsonify({
            'success': True,
            'is_running': is_running,
            'pid': pid,
            'status': '运行中' if is_running else '未运行',
            'total_sent': db_stats.get('total_sent', 0),
            'sent_1h': db_stats.get('sent_1h', 0),
            'sent_today': db_stats.get('sent_today', 0),
            'last_sent_time': db_stats.get('last_sent_time'),
            'last_update': db_stats.get('last_sent_time', '未知'),
            'signal_counts': signal_counts,
            'last_messages': [],  # 前端需要的字段
            # 同时保留嵌套格式以兼容其他可能的调用
            'data': {
                'is_running': is_running,
                'pid': pid,
                'database_stats': db_stats
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/telegram/history')
def telegram_history():
    """获取Telegram信号发送历史"""
    try:
        import os
        
        if not os.path.exists('tg_signals.db'):
            return jsonify({
                'success': False,
                'error': '数据库不存在'
            }), 404
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        signal_type = request.args.get('type', '')
        
        conn = sqlite3.connect('tg_signals.db', timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询
        where_clause = ""
        params = []
        if signal_type:
            where_clause = "WHERE signal_type = ?"
            params.append(signal_type)
        
        # 获取总数
        cursor.execute(f"SELECT COUNT(*) FROM signal_history {where_clause}", params)
        total = cursor.fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * limit
        cursor.execute(f"""
            SELECT id, signal_type, symbol, signal_name, signal_data, sent_time, created_at
            FROM signal_history
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row['id'],
                'signal_type': row['signal_type'],
                'symbol': row['symbol'],
                'signal_name': row['signal_name'],
                'signal_data': row['signal_data'],
                'sent_time': row['sent_time'],
                'created_at': row['created_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'records': records,
                'total': total,
                'page': page,
                'limit': limit,
                'pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/coins/realtime-status')
def api_coins_realtime_status():
    """
    获取所有币种的实时状态
    包括：当前价格（来自最新K线）、7天高低点、涨跌幅、交易信号及发生时间
    """
    try:
        import pytz
        conn = sqlite3.connect('crypto_data.db', timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        
        # 定义27个币种
        symbols = [
            'AAVE', 'APT', 'BCH', 'BNB', 'BTC', 'CRV', 'DOGE', 'DOT', 'ETC', 'ETH', 'FIL',
            'HBAR', 'LDO', 'LINK', 'LTC', 'NEAR', 'SOL', 'SUI', 'TAO', 'TON', 'TRX',
            'XLM', 'XRP', 'CFX', 'CRO', 'STX', 'UNI'
        ]
        
        results = []
        
        for symbol_short in symbols:
            symbol = f"{symbol_short}-USDT-SWAP"
            
            # 1. 获取最新K线数据（当前价格）
            cursor.execute('''
                SELECT timestamp, close, open
                FROM okex_kline_ohlc
                WHERE symbol = ? AND timeframe = '5m'
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (symbol,))
            latest_kline = cursor.fetchone()
            
            if not latest_kline:
                continue
            
            current_price = latest_kline['close']
            open_price = latest_kline['open']
            latest_time = datetime.fromtimestamp(latest_kline['timestamp'] / 1000, tz=beijing_tz)
            
            # 计算涨跌幅
            change_pct = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0
            
            # 2. 获取7天高低点
            cursor.execute('''
                SELECT MAX(high) as high_7d, MIN(low) as low_7d
                FROM okex_kline_ohlc
                WHERE symbol = ? AND timeframe = '5m'
                AND timestamp >= ?
            ''', (symbol, int((datetime.now() - timedelta(days=7)).timestamp() * 1000)))
            extremes = cursor.fetchone()
            
            high_7d = extremes['high_7d'] if extremes and extremes['high_7d'] else current_price
            low_7d = extremes['low_7d'] if extremes and extremes['low_7d'] else current_price
            
            # 3. 检查最近2小时的交易信号
            two_hours_ago = datetime.now(beijing_tz) - timedelta(hours=2)
            
            cursor.execute('''
                SELECT record_time, long_signals, short_signals, today_new_high, today_new_low
                FROM trading_signals
                WHERE record_time >= ?
                ORDER BY record_time DESC
                LIMIT 1
            ''', (two_hours_ago.strftime('%Y-%m-%d %H:%M:%S'),))
            signal_row = cursor.fetchone()
            
            signal_type = None
            signal_time = None
            
            if signal_row:
                signal_time_dt = datetime.strptime(signal_row['record_time'], '%Y-%m-%d %H:%M:%S')
                signal_time_dt = beijing_tz.localize(signal_time_dt)
                signal_time = signal_time_dt.strftime('%m-%d %H:%M')
                
                # 判断信号类型
                if signal_row['long_signals'] > 0 or signal_row['today_new_low'] > 0:
                    signal_type = 'buy'
                elif signal_row['short_signals'] > 0 or signal_row['today_new_high'] > 0:
                    signal_type = 'sell'
            
            results.append({
                'symbol': symbol_short,
                'current_price': current_price,
                'high_7d': high_7d,
                'low_7d': low_7d,
                'change_pct': change_pct,
                'signal_type': signal_type,  # 'buy' or 'sell' or None
                'signal_time': signal_time,  # K线时间，格式：'MM-DD HH:MM'
                'latest_update': latest_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'timestamp': datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sell-point-1/save', methods=['POST'])
def api_sell_point_1_save():
    """
    保存卖点1信号到数据库
    
    请求体格式:
    {
        "symbol": "BTC",
        "high_price": 90000.0,
        "high_time": "2025-12-15 14:30:00",
        "high_index": 1000,
        "mark_price": 89500.0,
        "mark_time": "2025-12-15 15:00:00",
        "mark_index": 1006,
        "mark_rsi": 65.5
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400
        
        # 验证必需字段
        required_fields = ['symbol', 'high_price', 'high_time', 'high_index', 
                          'mark_price', 'mark_time', 'mark_index', 'mark_rsi']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }), 400
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 检查是否已存在相同的信号（避免重复插入）
        cursor.execute('''
            SELECT id FROM sell_point_1_signals
            WHERE symbol = ? AND mark_time = ? AND is_valid = 1
        ''', (data['symbol'], data['mark_time']))
        
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return jsonify({
                'success': True,
                'message': '信号已存在',
                'signal_id': existing[0]
            })
        
        # 插入新信号
        now = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO sell_point_1_signals (
                symbol, high_price, high_time, high_index,
                mark_price, mark_time, mark_index, mark_rsi,
                signal_generated_at, is_valid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            data['symbol'],
            data['high_price'],
            data['high_time'],
            data['high_index'],
            data['mark_price'],
            data['mark_time'],
            data['mark_index'],
            data['mark_rsi'],
            now
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '卖点1信号保存成功',
            'signal_id': signal_id
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sell-point-1/latest')
def api_sell_point_1_latest():
    """
    获取最新的卖点1信号
    
    参数:
        - symbol: 币种（可选，如BTC）
        - hours: 时间范围（可选，默认24小时）
    """
    try:
        symbol = request.args.get('symbol')
        hours = int(request.args.get('hours', 24))
        
        conn = sqlite3.connect('crypto_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询
        beijing_tz = pytz.timezone('Asia/Shanghai')
        cutoff_time = (datetime.now(beijing_tz) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        if symbol:
            cursor.execute('''
                SELECT * FROM sell_point_1_signals
                WHERE symbol = ? AND mark_time >= ? AND is_valid = 1
                ORDER BY mark_time DESC
            ''', (symbol, cutoff_time))
        else:
            cursor.execute('''
                SELECT * FROM sell_point_1_signals
                WHERE mark_time >= ? AND is_valid = 1
                ORDER BY mark_time DESC
            ''', (cutoff_time,))
        
        rows = cursor.fetchall()
        conn.close()
        
        signals = []
        for row in rows:
            signals.append({
                'id': row['id'],
                'symbol': row['symbol'],
                'high_price': row['high_price'],
                'high_time': row['high_time'],
                'high_index': row['high_index'],
                'mark_price': row['mark_price'],
                'mark_time': row['mark_time'],
                'mark_index': row['mark_index'],
                'mark_rsi': row['mark_rsi'],
                'signal_generated_at': row['signal_generated_at'],
                'created_at': row['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': signals,
            'count': len(signals),
            'timestamp': datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/telegram-dashboard')
def telegram_dashboard():
    """Telegram信号推送系统仪表板"""
    return render_template('telegram_signal_dashboard.html')

@app.route('/cache-help')
def cache_help():
    """缓存清除帮助页面"""
    return render_template('cache_clear_guide.html')

@app.route('/api/telegram/signals/support-resistance')
def api_telegram_support_resistance():
    """获取支撑压力线信号（2小时内）"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect('telegram_signals.db')
        cursor = conn.cursor()
        
        # 获取2小时内的信号
        two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT signal_type, symbol, price, signal_time, sent_at
            FROM support_resistance_signals
            WHERE sent_at >= ?
            ORDER BY sent_at DESC
        ''', (two_hours_ago,))
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'signal_type': row[0],
                'symbol': row[1],
                'price': row[2],
                'signal_time': row[3],
                'sent_at': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'signals': signals,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/telegram/signals/count-alerts')
def api_telegram_count_alerts():
    """获取计次预警（2小时内）"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect('telegram_signals.db')
        cursor = conn.cursor()
        
        two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT record_time, count_value, threshold, full_data, sent_at
            FROM count_alerts
            WHERE sent_at >= ?
            ORDER BY sent_at DESC
        ''', (two_hours_ago,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'record_time': row[0],
                'count_value': row[1],
                'threshold': row[2],
                'full_data': row[3],
                'sent_at': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/telegram/signals/trading')
def api_telegram_trading():
    """获取交易信号（2小时内）"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect('telegram_signals.db')
        cursor = conn.cursor()
        
        two_hours_ago = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            SELECT signal_type, symbol, price, signal_time, rsi, sent_at
            FROM trading_signals
            WHERE sent_at >= ?
            ORDER BY sent_at DESC
        ''', (two_hours_ago,))
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'signal_type': row[0],
                'symbol': row[1],
                'price': row[2],
                'signal_time': row[3],
                'rsi': row[4],
                'sent_at': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'signals': signals,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/telegram/signals/stats')
def api_telegram_stats():
    """获取发送统计"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect('telegram_signals.db')
        cursor = conn.cursor()
        
        # 总发送数
        cursor.execute('SELECT COUNT(*) FROM support_resistance_signals')
        support_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM count_alerts')
        alert_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM trading_signals')
        trade_count = cursor.fetchone()[0]
        total = support_count + alert_count + trade_count
        
        # 最近1小时
        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('SELECT COUNT(*) FROM support_resistance_signals WHERE sent_at >= ?', (one_hour_ago,))
        support_1h = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM count_alerts WHERE sent_at >= ?', (one_hour_ago,))
        alert_1h = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM trading_signals WHERE sent_at >= ?', (one_hour_ago,))
        trade_1h = cursor.fetchone()[0]
        last_hour = support_1h + alert_1h + trade_1h
        
        # 今日发送
        today_start = datetime.now().strftime('%Y-%m-%d 00:00:00')
        cursor.execute('SELECT COUNT(*) FROM support_resistance_signals WHERE sent_at >= ?', (today_start,))
        support_today = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM count_alerts WHERE sent_at >= ?', (today_start,))
        alert_today = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM trading_signals WHERE sent_at >= ?', (today_start,))
        trade_today = cursor.fetchone()[0]
        today = support_today + alert_today + trade_today
        
        # 最后推送时间
        cursor.execute('''
            SELECT MAX(sent_at) FROM (
                SELECT sent_at FROM support_resistance_signals
                UNION ALL
                SELECT sent_at FROM count_alerts
                UNION ALL
                SELECT sent_at FROM trading_signals
            )
        ''')
        last_time = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total': total,
            'last_hour': last_hour,
            'today': today,
            'last_time': last_time
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/telegram/system/status')
def api_telegram_system_status():
    """获取Telegram推送系统状态"""
    try:
        import subprocess
        # 检查进程是否运行
        result = subprocess.run(['pgrep', '-f', 'telegram_signal_system.py'], 
                               capture_output=True, text=True)
        is_running = bool(result.stdout.strip())
        pid = result.stdout.strip() if is_running else None
        
        return jsonify({
            'success': True,
            'running': is_running,
            'pid': pid,
            'message': '系统运行中' if is_running else '系统未运行'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/telegram/start', methods=['POST'])
def api_telegram_start():
    """启动Telegram推送系统"""
    try:
        import subprocess
        result = subprocess.run(['./start_telegram_signal_system.sh'], 
                               capture_output=True, text=True, cwd='/home/user/webapp')
        return jsonify({
            'success': True,
            'message': '系统已启动',
            'output': result.stdout
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/telegram/stop', methods=['POST'])
def api_telegram_stop():
    """停止Telegram推送系统"""
    try:
        import subprocess
        result = subprocess.run(['./stop_telegram_signal_system.sh'], 
                               capture_output=True, text=True, cwd='/home/user/webapp')
        return jsonify({
            'success': True,
            'message': '系统已停止',
            'output': result.stdout
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/query/latest')
def api_query_latest():
    """获取最新查询数据API（用于计次预警）"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                snapshot_time, rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down, price_lowest, price_newhigh,
                count_score_display, rise_24h_count, fall_24h_count
            FROM crypto_snapshots
            ORDER BY snapshot_date DESC, snapshot_time DESC
            LIMIT 1
        """)
        
        snapshot = cursor.fetchone()
        conn.close()
        
        if not snapshot:
            return jsonify({'success': False, 'error': '暂无数据'})
        
        return jsonify({
            'success': True,
            'data': {
                '运算时间': snapshot[0],
                '急涨': snapshot[1],
                '急跌': snapshot[2],
                '差值': snapshot[3],
                '计次': snapshot[4],
                '比值': snapshot[5],
                '状态': snapshot[6],
                '本轮急涨': snapshot[7],
                '本轮急跌': snapshot[8],
                '比价最低': snapshot[9],
                '比价创新高': snapshot[10],
                '计次得分': snapshot[11],
                '24h涨≥10%': snapshot[12],
                '24h跌≤-10%': snapshot[13]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/support-resistance/export', methods=['POST'])
def api_support_resistance_export():
    """导出支撑阻力位数据"""
    try:
        import subprocess
        import os
        
        script_path = '/home/user/webapp/export_support_resistance_data.py'
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': '导出脚本不存在'
            })
        
        # 执行导出脚本
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': '导出失败',
                'output': result.stderr
            })
        
        # 从输出中提取导出文件路径
        export_file = None
        for line in result.stdout.split('\n'):
            if '导出文件:' in line:
                export_file = line.split('导出文件:')[-1].strip()
                break
        
        if not export_file or not os.path.exists(export_file):
            return jsonify({
                'success': False,
                'error': '找不到导出文件'
            })
        
        # 获取文件信息
        file_size = os.path.getsize(export_file)
        file_size_mb = file_size / (1024 * 1024)
        filename = os.path.basename(export_file)
        
        return jsonify({
            'success': True,
            'message': '导出成功',
            'file_path': export_file,
            'filename': filename,
            'file_size': file_size,
            'file_size_mb': round(file_size_mb, 2),
            'download_url': f'/api/support-resistance/download/{filename}'
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': '导出超时'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/support-resistance/download/<filename>')
def api_support_resistance_download(filename):
    """下载导出的数据文件"""
    try:
        export_dir = '/home/user/webapp/exports'
        file_path = os.path.join(export_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        return send_from_directory(export_dir, filename, as_attachment=True)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/support-resistance/import', methods=['POST'])
def api_support_resistance_import():
    """导入支撑阻力位数据"""
    try:
        import subprocess
        import os
        from werkzeug.utils import secure_filename
        
        # 检查是否有上传的文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            })
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            })
        
        # 检查是否清空现有数据
        clear_existing = request.form.get('clear_existing', 'false').lower() == 'true'
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        upload_dir = '/home/user/webapp/uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # 执行导入脚本
        script_path = '/home/user/webapp/import_support_resistance_data.py'
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': '导入脚本不存在'
            })
        
        # 构建命令
        cmd = ['python3', script_path, file_path]
        if clear_existing:
            cmd.append('--clear')
        
        # 执行导入
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # 删除上传的临时文件
        try:
            os.remove(file_path)
        except:
            pass
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': '导入失败',
                'output': result.stderr or result.stdout
            })
        
        # 从输出中提取统计信息
        stats = {
            'tables': 0,
            'records': 0
        }
        
        for line in result.stdout.split('\n'):
            if '表数量:' in line:
                try:
                    stats['tables'] = int(line.split(':')[-1].strip())
                except:
                    pass
            elif '总记录数:' in line:
                try:
                    stats['records'] = int(line.split(':')[-1].strip().replace(',', ''))
                except:
                    pass
        
        return jsonify({
            'success': True,
            'message': '导入成功',
            'stats': stats,
            'output': result.stdout
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': '导入超时'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/query/batch-import', methods=['POST'])
def api_query_batch_import():
    """批量导入当天所有TXT文件数据"""
    try:
        import subprocess
        import os
        
        # 执行批量导入脚本
        script_path = '/home/user/webapp/batch_import_daily_txt.py'
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': '批量导入脚本不存在'
            })
        
        # 使用subprocess运行脚本
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        # 解析输出结果
        output_lines = result.stdout.split('\n')
        
        # 提取统计信息
        stats = {
            'total': 0,
            'success': 0,
            'exists': 0,
            'invalid': 0,
            'error': 0
        }
        
        for line in output_lines:
            if '总文件数:' in line:
                stats['total'] = int(line.split(':')[-1].strip())
            elif '成功导入:' in line:
                stats['success'] = int(line.split(':')[-1].strip())
            elif '已存在:' in line:
                stats['exists'] = int(line.split(':')[-1].strip())
            elif '无效数据:' in line:
                stats['invalid'] = int(line.split(':')[-1].strip())
            elif '失败:' in line and '❌' in line:
                stats['error'] = int(line.split(':')[-1].strip())
        
        return jsonify({
            'success': True,
            'message': '批量导入完成',
            'stats': stats,
            'output': result.stdout
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': '批量导入超时（超过5分钟）'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/test-simple')
def test_simple():
    """简单测试页面 - 验证window.onload和ECharts基础功能"""
    return render_template('test_simple.html')

@app.route('/api/chart-config')
def chart_config():
    """获取K线图配置URL"""
    return jsonify({
        'success': True,
        'chart_base_url': CHART_BASE_URL,
        'example': f"{CHART_BASE_URL}/chart/BTC"
    })

@app.route('/gdrive-config')
def gdrive_config():
    """Google Drive配置管理页面"""
    return render_template('gdrive_config.html')

@app.route('/api/gdrive-config/get')
def gdrive_config_get():
    """获取当前Google Drive配置"""
    try:
        import json
        config_file = '/home/user/webapp/daily_folder_config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gdrive-config/update', methods=['POST'])
def gdrive_config_update():
    """更新Google Drive文件夹配置"""
    try:
        import json
        from datetime import datetime
        
        data = request.get_json()
        parent_folder_url = data.get('parent_folder_url', '')
        
        if not parent_folder_url:
            return jsonify({
                'success': False,
                'error': '请提供Google Drive文件夹链接'
            }), 400
        
        # 提取文件夹ID
        import re
        folder_id_match = re.search(r'/folders/([a-zA-Z0-9_-]+)', parent_folder_url)
        if not folder_id_match:
            return jsonify({
                'success': False,
                'error': '无法从链接中提取文件夹ID，请检查链接格式'
            }), 400
        
        root_folder_id = folder_id_match.group(1)
        
        # 读取现有配置
        config_file = '/home/user/webapp/daily_folder_config.json'
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        
        # 更新配置
        beijing_time = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        today = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')
        
        # 根据日期判断是单数还是双数
        day_of_month = datetime.now(BEIJING_TZ).day
        is_odd_day = day_of_month % 2 == 1
        
        if is_odd_day:
            config['root_folder_odd'] = root_folder_id
        else:
            config['root_folder_even'] = root_folder_id
        
        config['parent_folder_url'] = parent_folder_url
        config['last_manual_update'] = beijing_time
        config['last_updated'] = beijing_time
        config['update_reason'] = f'手动更新{"单数" if is_odd_day else "双数"}日期父文件夹'
        
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'配置已更新 ({"单数" if is_odd_day else "双数"}日期父文件夹)',
            'config': config
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/gdrive-config/manual-trigger', methods=['POST'])
def gdrive_manual_trigger():
    """手动触发数据采集"""
    try:
        import subprocess
        import os
        
        # 运行gdrive_final_detector.py一次
        script_path = '/home/user/webapp/gdrive_final_detector.py'
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': f'脚本不存在: {script_path}'
            }), 404
        
        # 在后台运行一次检测
        process = subprocess.Popen(
            ['python3', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd='/home/user/webapp'
        )
        
        # 等待最多5秒
        try:
            stdout, stderr = process.communicate(timeout=5)
            return jsonify({
                'success': True,
                'message': '手动触发成功，数据采集已开始',
                'output': stdout.decode('utf-8', errors='ignore')[:500]
            })
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': True,
                'message': '手动触发成功，数据采集正在后台运行'
            })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/gdrive-config/latest-data')
def gdrive_latest_data():
    """获取最新数据时间和状态"""
    try:
        import sqlite3
        from datetime import datetime
        
        db_path = '/home/user/webapp/crypto_data.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取最新数据
        cursor.execute("""
            SELECT snapshot_time, rush_up, rush_down, count, status, created_at
            FROM crypto_snapshots
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({
                'success': True,
                'has_data': False,
                'message': '暂无数据'
            })
        
        snapshot_time = result[0]
        created_at = result[5]
        
        # 计算延迟（分钟）
        now = datetime.now(BEIJING_TZ)
        try:
            snapshot_dt = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S')
            snapshot_dt = BEIJING_TZ.localize(snapshot_dt)
        except:
            snapshot_dt = datetime.strptime(snapshot_time, '%Y-%m-%d %H:%M:%S.%f')
            snapshot_dt = BEIJING_TZ.localize(snapshot_dt)
        
        delay_minutes = (now - snapshot_dt).total_seconds() / 60
        
        return jsonify({
            'success': True,
            'has_data': True,
            'data': {
                'snapshot_time': snapshot_time,
                'rush_up': result[1],
                'rush_down': result[2],
                'count': result[3],
                'status': result[4],
                'created_at': created_at,
                'delay_minutes': round(delay_minutes, 1)
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ==================== SAR斜率系统 V2.0 API ====================

@app.route('/sar-slope')
def sar_slope_page():
    """SAR斜率系统V2.0页面"""
    return render_template('sar_slope_v2.html')

@app.route('/api/sar-slope/latest')
def api_sar_slope_latest_v2():
    """获取所有币种的最新SAR斜率数据（V2.0）"""
    try:
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取每个币种的最新记录
        cursor.execute("""
            SELECT 
                s.symbol,
                s.datetime_beijing,
                s.sar_value,
                s.sar_direction,
                s.sequence_number,
                s.sar_diff,
                s.sar_diff_percent,
                s.avg_1day,
                s.avg_3day,
                s.avg_7day,
                s.avg_15day,
                s.is_anomaly,
                s.anomaly_type,
                s.deviation_percent,
                s.is_extreme,
                s.extreme_type,
                s.price_open,
                s.price_close,
                s.timestamp
            FROM sar_slope_v2 s
            INNER JOIN (
                SELECT symbol, MAX(timestamp) as max_timestamp
                FROM sar_slope_v2
                GROUP BY symbol
            ) latest ON s.symbol = latest.symbol AND s.timestamp = latest.max_timestamp
            ORDER BY s.symbol
        """)
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'symbol': row[0],
                'datetime': row[1],
                'sar_value': round(row[2], 6) if row[2] else None,
                'direction': row[3],
                'sequence': row[4],
                'diff': round(row[5], 6) if row[5] else None,
                'diff_percent': round(row[6], 6) if row[6] else None,
                'avg_1day': round(row[7], 6) if row[7] else None,
                'avg_3day': round(row[8], 6) if row[8] else None,
                'avg_7day': round(row[9], 6) if row[9] else None,
                'avg_15day': round(row[10], 6) if row[10] else None,
                'is_anomaly': bool(row[11]),
                'anomaly_type': row[12],
                'deviation_percent': round(row[13], 2) if row[13] else None,
                'is_extreme': bool(row[14]),
                'extreme_type': row[15],
                'price_open': round(row[16], 2) if row[16] else None,
                'price_close': round(row[17], 2) if row[17] else None,
                'timestamp': row[18]
            })
        
        # 统计信息
        long_count = sum(1 for r in results if r['direction'] == 'long')
        short_count = sum(1 for r in results if r['direction'] == 'short')
        anomaly_count = sum(1 for r in results if r['is_anomaly'])
        
        stats = {
            'total_symbols': len(results),
            'long_count': long_count,
            'short_count': short_count,
            'anomaly_count': anomaly_count
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'stats': stats,
            'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/sar-slope/history/<symbol>')
def api_sar_slope_history_v2(symbol):
    """获取指定币种的SAR斜率历史数据"""
    try:
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 1000))
        
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                timestamp,
                datetime_beijing,
                sar_value,
                sar_direction,
                sequence_number,
                sar_diff,
                sar_diff_percent,
                avg_3day,
                is_anomaly,
                is_extreme,
                price_open,
                price_close
            FROM sar_slope_v2
            WHERE symbol = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (symbol, start_time, limit))
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'timestamp': row[0],
                'datetime': row[1],
                'sar_value': round(row[2], 6) if row[2] else None,
                'direction': row[3],
                'sequence': row[4],
                'diff': round(row[5], 6) if row[5] else None,
                'diff_percent': round(row[6], 6) if row[6] else None,
                'avg_3day': round(row[7], 6) if row[7] else None,
                'is_anomaly': bool(row[8]),
                'is_extreme': bool(row[9]),
                'price_open': round(row[10], 2) if row[10] else None,
                'price_close': round(row[11], 2) if row[11] else None
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'days': days,
            'data': results,
            'count': len(results)
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/sar-slope/coin/<symbol>')
def sar_slope_coin_detail(symbol):
    """单币种SAR详细数据页面"""
    return render_template('sar_slope_coin_detail.html', symbol=symbol)

@app.route('/api/sar-slope/coin/<symbol>/detail')
def api_sar_slope_coin_detail(symbol):
    """获取单币种的5分钟级别详细SAR数据"""
    try:
        hours = int(request.args.get('hours', 24))  # 默认24小时
        limit = int(request.args.get('limit', 500))
        
        start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取详细的5分钟数据
        cursor.execute("""
            SELECT 
                timestamp,
                datetime_beijing,
                sar_value,
                sar_direction,
                sequence_number,
                sar_diff,
                sar_diff_percent,
                avg_1day,
                avg_3day,
                avg_7day,
                avg_15day,
                is_anomaly,
                anomaly_type,
                deviation_percent,
                is_extreme,
                extreme_type,
                price_open,
                price_close
            FROM sar_slope_v2
            WHERE symbol = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (symbol, start_time, limit))
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'timestamp': row[0],
                'datetime': row[1],
                'sar_value': round(row[2], 6) if row[2] else None,
                'direction': row[3],
                'sequence': row[4],
                'diff': round(row[5], 6) if row[5] else None,
                'diff_percent': round(row[6], 6) if row[6] else None,
                'avg_1day': round(row[7], 6) if row[7] else None,
                'avg_3day': round(row[8], 6) if row[8] else None,
                'avg_7day': round(row[9], 6) if row[9] else None,
                'avg_15day': round(row[10], 6) if row[10] else None,
                'is_anomaly': bool(row[11]),
                'anomaly_type': row[12],
                'deviation_percent': round(row[13], 2) if row[13] else None,
                'is_extreme': bool(row[14]),
                'extreme_type': row[15],
                'price_open': round(row[16], 6) if row[16] else None,
                'price_close': round(row[17], 6) if row[17] else None
            })
        
        # 获取方向转换历史
        cursor.execute("""
            SELECT 
                change_timestamp,
                change_datetime_beijing,
                from_direction,
                to_direction,
                sar_value_at_change,
                price_at_change,
                previous_duration
            FROM sar_direction_changes
            WHERE symbol = ? AND change_timestamp >= ?
            ORDER BY change_timestamp DESC
            LIMIT 50
        """, (symbol, start_time))
        
        change_rows = cursor.fetchall()
        changes = []
        for row in change_rows:
            changes.append({
                'timestamp': row[0],
                'datetime': row[1],
                'from_direction': row[2],
                'to_direction': row[3],
                'sar_value': round(row[4], 6) if row[4] else None,
                'price': round(row[5], 6) if row[5] else None,
                'duration': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'hours': hours,
            'data': results,
            'direction_changes': changes,
            'count': len(results),
            'timestamp': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ==================== 资金监控系统 API ====================

@app.route('/api/fund-monitor/latest', methods=['GET'])
def fund_monitor_latest():
    """获取最新的资金监控数据（所有币种，所有时间周期）"""
    try:
        conn = sqlite3.connect('fund_monitor.db')
        cursor = conn.cursor()
        
        # 获取每个币种、每个时间周期的最新数据
        cursor.execute('''
            SELECT symbol, interval_type, timestamp, collect_time, volume, 
                   avg_3day, deviation_percent, is_abnormal
            FROM fund_monitor_aggregated
            WHERE (symbol, interval_type, timestamp) IN (
                SELECT symbol, interval_type, MAX(timestamp)
                FROM fund_monitor_aggregated
                GROUP BY symbol, interval_type
            )
            ORDER BY symbol, interval_type
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # 按币种组织数据
        data_by_symbol = {}
        for row in rows:
            symbol = row[0]
            if symbol not in data_by_symbol:
                data_by_symbol[symbol] = {
                    '15min': None,
                    '30min': None,
                    '60min': None
                }
            
            interval_type = row[1]
            data_by_symbol[symbol][interval_type] = {
                'timestamp': row[2],
                'collect_time': row[3],
                'volume': round(row[4], 2),
                'avg_3day': round(row[5], 2) if row[5] is not None else None,
                'deviation_percent': round(row[6], 2) if row[6] is not None else None,
                'is_abnormal': bool(row[7])
            }
        
        return jsonify({
            'success': True,
            'data': data_by_symbol,
            'update_time': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/fund-monitor/history/<symbol>', methods=['GET'])
def fund_monitor_history(symbol):
    """获取指定币种的历史数据"""
    try:
        interval_type = request.args.get('interval', '15min')  # 默认15分钟
        hours = int(request.args.get('hours', 24))  # 默认24小时
        
        conn = sqlite3.connect('fund_monitor.db')
        cursor = conn.cursor()
        
        # 计算时间范围
        end_time = int(datetime.now(BEIJING_TZ).timestamp() * 1000)
        start_time = end_time - (hours * 60 * 60 * 1000)
        
        cursor.execute('''
            SELECT timestamp, collect_time, volume, avg_3day, 
                   deviation_percent, is_abnormal
            FROM fund_monitor_aggregated
            WHERE symbol = ?
            AND interval_type = ?
            AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (symbol.upper(), interval_type, start_time))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'timestamp': row[0],
                'collect_time': row[1],
                'volume': round(row[2], 2),
                'avg_3day': round(row[3], 2) if row[3] is not None else None,
                'deviation_percent': round(row[4], 2) if row[4] is not None else None,
                'is_abnormal': bool(row[5])
            })
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'interval_type': interval_type,
            'hours': hours,
            'data': history
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/fund-monitor/abnormal', methods=['GET'])
def fund_monitor_abnormal():
    """获取当前所有异常数据"""
    try:
        conn = sqlite3.connect('fund_monitor.db')
        cursor = conn.cursor()
        
        # 获取最新异常数据
        cursor.execute('''
            SELECT symbol, interval_type, timestamp, collect_time, 
                   volume, avg_3day, deviation_percent
            FROM fund_monitor_aggregated
            WHERE is_abnormal = 1
            AND (symbol, interval_type, timestamp) IN (
                SELECT symbol, interval_type, MAX(timestamp)
                FROM fund_monitor_aggregated
                WHERE is_abnormal = 1
                GROUP BY symbol, interval_type
            )
            ORDER BY ABS(deviation_percent) DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        abnormal_list = []
        for row in rows:
            abnormal_list.append({
                'symbol': row[0],
                'interval_type': row[1],
                'timestamp': row[2],
                'collect_time': row[3],
                'volume': round(row[4], 2),
                'avg_3day': round(row[5], 2) if row[5] is not None else None,
                'deviation_percent': round(row[6], 2)
            })
        
        return jsonify({
            'success': True,
            'count': len(abnormal_list),
            'data': abnormal_list,
            'update_time': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/fund-monitor/config', methods=['GET', 'POST'])
def fund_monitor_config():
    """获取或更新资金监控配置"""
    config_file = 'fund_monitor_config.json'
    
    try:
        if request.method == 'GET':
            # 读取配置
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    'threshold_percentage': 20.0,
                    'lookback_days': 3,
                    'collection_interval': 300
                }
            
            return jsonify({
                'success': True,
                'config': config
            })
        
        elif request.method == 'POST':
            # 更新配置
            data = request.json
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': '请提供配置数据'
                }), 400
            
            # 读取现有配置或使用默认值
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    'threshold_percentage': 20.0,
                    'lookback_days': 3,
                    'collection_interval': 300
                }
            
            # 更新配置
            if 'threshold_percentage' in data:
                config['threshold_percentage'] = float(data['threshold_percentage'])
            if 'lookback_days' in data:
                config['lookback_days'] = int(data['lookback_days'])
            if 'collection_interval' in data:
                config['collection_interval'] = int(data['collection_interval'])
            
            # 保存配置
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True,
                'message': '配置已更新',
                'config': config
            })
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/fund-monitor/abnormal-history', methods=['GET'])
def fund_monitor_abnormal_history():
    """查询异常数据历史记录"""
    try:
        # 获取查询参数
        date = request.args.get('date')  # 格式：YYYY-MM-DD
        start_date = request.args.get('start_date')  # 格式：YYYY-MM-DD
        end_date = request.args.get('end_date')  # 格式：YYYY-MM-DD
        symbol = request.args.get('symbol')  # 币种
        interval = request.args.get('interval')  # 时间周期
        severity = request.args.get('severity')  # 严重程度
        deviation_type = request.args.get('type')  # surge或drop
        limit = int(request.args.get('limit', 100))  # 返回记录数
        
        conn = sqlite3.connect('fund_monitor.db')
        cursor = conn.cursor()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if date:
            conditions.append('collect_date = ?')
            params.append(date)
        elif start_date and end_date:
            conditions.append('collect_date BETWEEN ? AND ?')
            params.extend([start_date, end_date])
        elif start_date:
            conditions.append('collect_date >= ?')
            params.append(start_date)
        elif end_date:
            conditions.append('collect_date <= ?')
            params.append(end_date)
        
        if symbol:
            conditions.append('symbol = ?')
            params.append(symbol.upper())
        
        if interval:
            conditions.append('interval_type = ?')
            params.append(interval)
        
        if severity:
            conditions.append('severity = ?')
            params.append(severity)
        
        if deviation_type:
            conditions.append('deviation_type = ?')
            params.append(deviation_type)
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        
        # 执行查询
        query = f'''
            SELECT id, symbol, interval_type, timestamp, collect_time, collect_date,
                   volume, avg_3day, deviation_percent, deviation_type, severity
            FROM fund_monitor_abnormal_history
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 格式化结果
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'symbol': row[1],
                'interval_type': row[2],
                'timestamp': row[3],
                'collect_time': row[4],
                'collect_date': row[5],
                'volume': round(row[6], 2),
                'avg_3day': round(row[7], 2),
                'deviation_percent': round(row[8], 2),
                'deviation_type': row[9],
                'severity': row[10]
            })
        
        # 统计信息
        cursor.execute(f'''
            SELECT COUNT(*) FROM fund_monitor_abnormal_history
            WHERE {where_clause}
        ''', params[:-1])  # 去掉limit参数
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'returned_count': len(history),
            'data': history
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/fund-monitor/abnormal-dates', methods=['GET'])
def fund_monitor_abnormal_dates():
    """获取有异常数据的日期列表"""
    try:
        conn = sqlite3.connect('fund_monitor.db')
        cursor = conn.cursor()
        
        # 查询所有有异常数据的日期及其统计
        cursor.execute('''
            SELECT collect_date, 
                   COUNT(*) as count,
                   COUNT(DISTINCT symbol) as affected_coins,
                   AVG(ABS(deviation_percent)) as avg_deviation
            FROM fund_monitor_abnormal_history
            GROUP BY collect_date
            ORDER BY collect_date DESC
        ''')
        
        rows = cursor.fetchall()
        
        dates = []
        for row in rows:
            dates.append({
                'date': row[0],
                'count': row[1],
                'affected_coins': row[2],
                'avg_deviation': round(row[3], 2)
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'dates': dates
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/fund-monitor/abnormal-timeline', methods=['GET'])
def fund_monitor_abnormal_timeline():
    """获取异常数据时间轴（按小时聚合）"""
    try:
        date = request.args.get('date')  # YYYY-MM-DD
        
        if not date:
            return jsonify({
                'success': False,
                'error': '请提供date参数'
            }), 400
        
        conn = sqlite3.connect('fund_monitor.db')
        cursor = conn.cursor()
        
        # 查询指定日期的所有异常数据
        cursor.execute('''
            SELECT symbol, interval_type, collect_time, volume, 
                   avg_3day, deviation_percent, deviation_type, severity
            FROM fund_monitor_abnormal_history
            WHERE collect_date = ?
            ORDER BY collect_time ASC
        ''', (date,))
        
        rows = cursor.fetchall()
        
        # 按小时分组
        timeline = {}
        for row in rows:
            collect_time = row[2]
            hour = collect_time[:13]  # YYYY-MM-DD HH
            
            if hour not in timeline:
                timeline[hour] = []
            
            timeline[hour].append({
                'symbol': row[0],
                'interval_type': row[1],
                'time': collect_time,
                'volume': round(row[3], 2),
                'avg_3day': round(row[4], 2),
                'deviation_percent': round(row[5], 2),
                'deviation_type': row[6],
                'severity': row[7]
            })
        
        # 转换为列表格式
        timeline_list = []
        for hour, events in sorted(timeline.items()):
            timeline_list.append({
                'hour': hour,
                'count': len(events),
                'events': events
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'date': date,
            'timeline': timeline_list
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/fund-monitor', methods=['GET'])
def fund_monitor_page():
    """资金监控系统前端页面"""
    return render_template('fund_monitor.html')

@app.route('/fund-monitor-history', methods=['GET'])
def fund_monitor_history_page():
    """资金监控异常历史查询页面"""
    return render_template('fund_monitor_history.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

