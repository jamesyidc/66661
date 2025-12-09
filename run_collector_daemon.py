#!/usr/bin/env python3
from panic_wash_realtime import RealTimePanicWashCollector

if __name__ == '__main__':
    collector = RealTimePanicWashCollector()
    collector.run_loop(interval=180)
