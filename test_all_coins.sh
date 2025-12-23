#!/bin/bash

symbols=(
    "BTC-USDT-SWAP" "ETH-USDT-SWAP" "XRP-USDT-SWAP" "BNB-USDT-SWAP"
    "SOL-USDT-SWAP" "LTC-USDT-SWAP" "DOGE-USDT-SWAP" "SUI-USDT-SWAP"
    "TRX-USDT-SWAP" "TON-USDT-SWAP" "ETC-USDT-SWAP" "BCH-USDT-SWAP"
    "HBAR-USDT-SWAP" "XLM-USDT-SWAP" "FIL-USDT-SWAP" "LINK-USDT-SWAP"
    "CRO-USDT-SWAP" "DOT-USDT-SWAP" "AAVE-USDT-SWAP" "UNI-USDT-SWAP"
    "NEAR-USDT-SWAP" "APT-USDT-SWAP" "CFX-USDT-SWAP" "CRV-USDT-SWAP"
    "STX-USDT-SWAP" "LDO-USDT-SWAP" "TAO-USDT-SWAP"
)

echo "Testing all 27 coin detail pages..."
echo "===================================="

for symbol in "${symbols[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/sar-slope/coin/${symbol}")
    if [ "$status" = "200" ]; then
        echo "✅ ${symbol}: OK"
    else
        echo "❌ ${symbol}: FAILED (HTTP $status)"
    fi
done

echo "===================================="
echo "Test completed!"
