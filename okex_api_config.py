"""
OKEx API 配置文件
包含 API 密钥和基本配置
"""

# OKEx API 凭据
OKEX_API_KEY = "d0807489-6236-46a1-80a1-1f8014f3ef42"
OKEX_SECRET_KEY = "097EE45634C0FFE58E2DB1D71B17CE53"
OKEX_PASSPHRASE = "Zy255436.$"

# API 端点
OKEX_REST_URL = "https://www.okx.com"
OKEX_WS_PUBLIC_URL = "wss://ws.okx.com:8443/ws/v5/public"
OKEX_WS_PRIVATE_URL = "wss://ws.okx.com:8443/ws/v5/private"

# 配置
SIMULATED = False  # False = 实盘, True = 模拟盘

print("✅ OKEx API 配置文件已创建")
