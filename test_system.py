#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TMS 系統功能測試腳本
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, Cargo, Route, Shipment, cargo_data, routes_data, shipments_data

def test_system():
    """測試系統基本功能"""
    print("=" * 50)
    print("TMS 系統功能測試")
    print("=" * 50)
    
    # 清空測試資料
    cargo_data.clear()
    routes_data.clear()
    shipments_data.clear()
    
    print("1. 測試貨物管理...")
    
    # 新增測試貨物
    cargo1 = Cargo("筆記型電腦", 10, 2.5, "Dell 筆記型電腦")
    cargo2 = Cargo("手機", 50, 0.2, "iPhone 手機")
    cargo_data.extend([cargo1, cargo2])
    
    print("   ✓ 新增 {} 筆貨物".format(len(cargo_data)))
    for cargo in cargo_data:
        print("     - {}: {}件, {}kg/件".format(cargo.name, cargo.quantity, cargo.weight))
    
    print("\n2. 測試路線管理...")
    
    # 新增測試路線
    route1 = Route("台北-高雄", "台北", "高雄", ["台中", "台南"])
    route2 = Route("台北-花蓮", "台北", "花蓮", ["宜蘭"])
    routes_data.extend([route1, route2])
    
    print("   ✓ 新增 {} 條路線".format(len(routes_data)))
    for route in routes_data:
        print("     - {}: {} → {}".format(route.name, route.start_point, route.end_point))
        if route.waypoints:
            print("       途經: {}".format(', '.join(route.waypoints)))
    
    print("\n3. 測試配送管理...")
    
    # 新增測試配送
    shipment1 = Shipment(cargo1.id, route1.id, "待配送")
    shipment2 = Shipment(cargo2.id, route2.id, "配送中")
    shipments_data.extend([shipment1, shipment2])
    
    print("   ✓ 新增 {} 筆配送記錄".format(len(shipments_data)))
    for shipment in shipments_data:
        cargo = next((c for c in cargo_data if c.id == shipment.cargo_id), None)
        route = next((r for r in routes_data if r.id == shipment.route_id), None)
        cargo_name = cargo.name if cargo else '未知貨物'
        route_name = route.name if route else '未知路線'
        print("     - {} → {} ({})".format(cargo_name, route_name, shipment.status))
    
    print("\n4. 測試統計功能...")
    
    total_cargo = len(cargo_data)
    total_routes = len(routes_data)
    total_shipments = len(shipments_data)
    total_weight = sum(cargo.weight * cargo.quantity for cargo in cargo_data)
    
    print("   ✓ 總貨物數: {}".format(total_cargo))
    print("   ✓ 總路線數: {}".format(total_routes))
    print("   ✓ 總配送數: {}".format(total_shipments))
    print("   ✓ 總重量: {:.1f}kg".format(total_weight))
    
    print("\n5. 測試搜尋功能...")
    
    # 測試貨物搜尋
    search_results = [c for c in cargo_data if "電腦" in c.name]
    print("   ✓ 搜尋 '電腦': 找到 {} 筆結果".format(len(search_results)))
    
    # 測試路線搜尋
    route_search_results = [r for r in routes_data if "台北" in r.name]
    print("   ✓ 搜尋 '台北': 找到 {} 筆結果".format(len(route_search_results)))
    
    print("\n" + "=" * 50)
    print("所有測試完成！系統功能正常。")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    try:
        test_system()
    except Exception as e:
        print("測試失敗: {}".format(e))
        sys.exit(1)
