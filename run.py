#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TMS 運輸管理系統啟動腳本
"""

from app import run_app

if __name__ == '__main__':
    print("=" * 50)
    print("TMS 運輸管理系統")
    print("=" * 50)
    print("系統正在啟動...")
    print("訪問地址: http://localhost:5000")
    print("按 Ctrl+C 停止服務")
    print("=" * 50)
    
    run_app()
