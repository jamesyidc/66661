#!/usr/bin/env python3
"""
加密货币数据分析系统 - 完全仿照参考页面风格
"""
from flask import Flask, render_template_string, render_template, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime, timedelta
import json
import pytz

app = Flask(__name__)
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

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
                        <th>--%</th>
                        <th>排行</th>
                        <th>当前价格</th>
                        <th>最高占比</th>
                        <th>最低占比</th>
                    </tr>
                </thead>
                <tbody id="dataTableBody">
                    <tr>
                        <td colspan="16" class="loading">正在加载数据...</td>
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
                    bottom: '60px',  // 增加底部空间给横轴标签
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
                        fontSize: 11,
                        rotate: 0,  // 不旋转，水平显示
                        interval: 0,  // 显示所有标签
                        margin: 10
                    },
                    axisTick: {
                        show: true,
                        lineStyle: { color: '#3a3d5c' }
                    },
                    splitLine: { show: false }
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
            
            // 更新表格
            const tbody = document.getElementById('dataTableBody');
            if (data.coins && data.coins.length > 0) {
                let html = '';
                data.coins.forEach((coin, idx) => {
                    const changeClass = coin.change > 0 ? 'value-positive' : (coin.change < 0 ? 'value-negative' : 'value-neutral');
                    const change24Class = coin.change_24h > 0 ? 'value-positive' : (coin.change_24h < 0 ? 'value-negative' : 'value-neutral');
                    const priorityClass = 'priority-' + coin.priority.replace('等级', '');
                    
                    const rushUpTag = coin.rush_up > 0 ? '<span class="status-tag rise">' + coin.rush_up + '</span>' : coin.rush_up;
                    const rushDownTag = coin.rush_down > 0 ? '<span class="status-tag fall">' + coin.rush_down + '</span>' : coin.rush_down;
                    
                    html += '<tr>';
                    html += '<td class="' + priorityClass + '">' + coin.priority + '</td>';
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
                    html += '<td>--</td>';
                    html += '<td>' + coin.rank + '</td>';
                    html += '<td>' + coin.current_price.toFixed(4) + '</td>';
                    html += '<td>' + coin.ratio1 + '</td>';
                    html += '<td>' + coin.ratio2 + '</td>';
                    html += '</tr>';
                });
                tbody.innerHTML = html;
            } else {
                tbody.innerHTML = '<tr><td colspan="16" class="loading">暂无数据</td></tr>';
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
            ORDER BY snapshot_time DESC
            LIMIT 2
        """)
        latest_records = cursor.fetchall()
        
        last_update_time = '-'
        current_round_rush_up = 0
        current_round_rush_down = 0
        
        if latest_records and len(latest_records) >= 1:
            last_update_time = latest_records[0][0].split(' ')[1][:5]
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
                snapshot_time, rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down, price_lowest, price_newhigh,
                count_score_display, count_score_type, rise_24h_count, fall_24h_count
            FROM crypto_snapshots
            WHERE snapshot_time LIKE ?
            ORDER BY snapshot_time DESC
            LIMIT 1
        """, (f"{query_time}%",))
        
        snapshot = cursor.fetchone()
        
        if not snapshot:
            conn.close()
            return jsonify({'error': f'未找到 {query_time} 的数据'})
        
        (snapshot_time, rush_up, rush_down, diff, count, ratio, status,
         round_rush_up, round_rush_down, price_lowest, price_newhigh,
         count_score_display, count_score_type, rise_24h_count, fall_24h_count) = snapshot
        
        cursor.execute("""
            SELECT 
                symbol, change, rush_up, rush_down, update_time,
                high_price, high_time, decline, change_24h, rank,
                current_price, ratio1, ratio2, priority_level
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
                'ratio1': row[11],
                'ratio2': row[12],
                'priority': row[13]
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
                snapshot_time, rush_up, rush_down, diff, count, ratio, status,
                round_rush_up, round_rush_down, price_lowest, price_newhigh,
                count_score_display, count_score_type, rise_24h_count, fall_24h_count
            FROM crypto_snapshots
            ORDER BY snapshot_time DESC
            LIMIT 1
        """)
        
        snapshot = cursor.fetchone()
        
        if not snapshot:
            conn.close()
            return jsonify({'error': '数据库中暂无数据'})
        
        (snapshot_time, rush_up, rush_down, diff, count, ratio, status,
         round_rush_up, round_rush_down, price_lowest, price_newhigh,
         count_score_display, count_score_type, rise_24h_count, fall_24h_count) = snapshot
        
        cursor.execute("""
            SELECT 
                symbol, change, rush_up, rush_down, update_time,
                high_price, high_time, decline, change_24h, rank,
                current_price, ratio1, ratio2, priority_level
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
                'ratio1': row[11],
                'ratio2': row[12],
                'priority': row[13]
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
            ORDER BY snapshot_time ASC
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
            ORDER BY snapshot_time DESC
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
            
            # 先查询指定时间之前的记录
            cursor.execute('''
                SELECT record_time, panic_index, hour_24_people, total_position, hour_1_amount, hour_24_amount
                FROM panic_wash_index
                WHERE record_time <= ?
                ORDER BY record_time DESC
                LIMIT ?
            ''', (query_time, half_limit))
            before_rows = cursor.fetchall()
            
            # 再查询指定时间之后的记录
            cursor.execute('''
                SELECT record_time, panic_index, hour_24_people, total_position, hour_1_amount, hour_24_amount
                FROM panic_wash_index
                WHERE record_time > ?
                ORDER BY record_time ASC
                LIMIT ?
            ''', (query_time, half_limit))
            after_rows = cursor.fetchall()
            
            # 合并结果并按时间倒序排列
            rows = list(before_rows) + list(reversed(after_rows))
        else:
            # 默认查询：最新的N条记录
            cursor.execute('''
                SELECT record_time, panic_index, hour_24_people, total_position, hour_1_amount, hour_24_amount
                FROM panic_wash_index
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
            query_last_time = query_last_time.split(' ')[1][:5]  # 只取HH:MM
        
        # 2. 交易信号监控模块统计
        cursor.execute("SELECT COUNT(*) FROM trading_signals")
        signal_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT record_date) FROM trading_signals")
        signal_days = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(record_time) FROM trading_signals")
        signal_last_time = cursor.fetchone()[0] or '-'
        if signal_last_time != '-':
            signal_last_time = signal_last_time.split(' ')[1][:5]  # 只取HH:MM
        
        # 3. 恐慌清洗指数模块统计
        cursor.execute("SELECT COUNT(*) FROM panic_wash_index")
        panic_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT DATE(record_time)) FROM panic_wash_index")
        panic_days = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(record_time) FROM panic_wash_index")
        panic_last_time = cursor.fetchone()[0] or '-'
        if panic_last_time != '-':
            panic_last_time = panic_last_time.split(' ')[1][:5]  # 只取HH:MM
        
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
            SELECT coin_name, highest_price, highest_count, lowest_price, lowest_count,
                   highest_ratio, lowest_ratio, last_update_time
            FROM price_comparison
            ORDER BY display_order
        ''')
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
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
                'coin_name': row[0],
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
            FROM price_comparison
            WHERE coin_name = ?
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
            UPDATE price_comparison
            SET highest_price = ?,
                highest_count = ?,
                lowest_price = ?,
                lowest_count = ?,
                highest_ratio = ?,
                lowest_ratio = ?,
                last_update_time = ?
            WHERE coin_name = ?
        ''', (highest_price, highest_count, lowest_price, lowest_count, 
              highest_ratio, lowest_ratio, beijing_time, coin_name))
        
        # 如果发生创新高或创新低，记录事件
        if action in ['new_high', 'new_low']:
            cursor.execute('''
                INSERT INTO price_breakthrough_events 
                (coin_name, event_type, price, event_time, previous_extreme_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (coin_name, action, new_price, beijing_time, 
                  old_highest_price if action == 'new_high' else old_lowest_price))
        
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
    """
    try:
        from datetime import datetime, timedelta
        import pytz
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        
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
            SELECT coin_name, highest_price, lowest_price
            FROM price_comparison
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
                    UPDATE price_comparison
                    SET highest_ratio = ?,
                        lowest_ratio = ?,
                        last_update_time = ?
                    WHERE coin_name = ?
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
    """数据采集监控页面"""
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
            ORDER BY snapshot_time DESC
            LIMIT 1
        ''')
        snapshot = cursor.fetchone()
        
        if not snapshot:
            return jsonify({'success': False, 'error': '暂无快照数据'})
        
        rush_up, rush_down, diff, count, snapshot_time = snapshot
        
        # 获取全网持仓量（从恐慌清洗指数表）
        cursor.execute('''
            SELECT total_position
            FROM panic_wash_index
            ORDER BY record_time DESC
            LIMIT 1
        ''')
        holdings_row = cursor.fetchone()
        holdings = holdings_row[0] if holdings_row else 100  # 默认100亿
        
        # 获取做多做空信号（从交易信号表）
        cursor.execute('''
            SELECT long_signals, short_signals
            FROM trading_signals
            ORDER BY record_time DESC
            LIMIT 1
        ''')
        signals_row = cursor.fetchone()
        long_signals = signals_row[0] if signals_row else 0
        short_signals = signals_row[1] if signals_row else 0
        
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
        
        # 优先级≥4 means 等级1,2,3,4 (priority_level values: '等级1', '等级2', etc.)
        priority_high_coins = [c[0] for c in coin_data if c[3] in ['等级1', '等级2', '等级3', '等级4']]
        priority_high_count = len(priority_high_coins)
        
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
            'new_low_today': new_low_today,
            'new_high_today': new_high_today,
            'count': count,
            'snapshot_time': snapshot_time
        }
        
        # 计算星星系统
        results = calculate_star_system(data)
        
        # 添加币种列表到结果中
        coin_lists = {
            'only_rush_up_coins': only_rush_up_coins,
            'rush_up_gt_down_coins': rush_up_gt_down_coins,
            'priority_high_coins': priority_high_coins,
            'only_rush_down_coins': only_rush_down_coins
        }
        
        return jsonify({
            'success': True,
            'data': results,
            'raw_data': data,
            'coin_lists': coin_lists,
            'update_time': snapshot_time
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
                'close': row[5]
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

@app.route('/api/index/history')
def api_index_history():
    """获取历史数据 - 基于K线数据"""
    try:
        limit = int(request.args.get('limit', 100))
        
        conn = sqlite3.connect('crypto_data.db')
        cursor = conn.cursor()
        
        # 获取最近的K线数据
        cursor.execute('''
            SELECT timestamp, index_value, close_price
            FROM crypto_index_klines
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
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
        conn.close()
        
        # 构造返回数据
        data_list = []
        for row in rows:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
