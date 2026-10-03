# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from itertools import count
from math import isfinite
import os
from secrets import token_hex

app = Flask(__name__)
app.secret_key = os.environ.get("TMS_SECRET_KEY") or token_hex(32)

# 全域資料儲存（不使用資料庫）
cargo_data = []
routes_data = []
shipments_data = []
_cargo_ids = count(1)
_route_ids = count(1)
_shipment_ids = count(1)

class Cargo:
    def __init__(self, name, quantity, weight, description=""):
        self.id = next(_cargo_ids)
        self.name = name
        self.quantity = quantity
        self.weight = weight
        self.description = description
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Route:
    def __init__(self, name, start_point, end_point, waypoints=None):
        self.id = next(_route_ids)
        self.name = name
        self.start_point = start_point
        self.end_point = end_point
        self.waypoints = waypoints or []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Shipment:
    def __init__(self, cargo_id, route_id, status="待配送"):
        self.id = next(_shipment_ids)
        self.cargo_id = cargo_id
        self.route_id = route_id
        self.status = status
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _required_text(field, label):
    value = request.form.get(field, "").strip()
    if not value:
        flash(f"{label}不可空白！", "error")
        return None
    return value


def _cargo_form_values():
    name = _required_text("name", "貨物名稱")
    try:
        quantity = int(request.form.get("quantity", ""))
        weight = float(request.form.get("weight", ""))
    except (TypeError, ValueError):
        flash("數量必須是正整數，重量必須是非負數字！", "error")
        return None
    if quantity < 1 or not isfinite(weight) or weight < 0:
        flash("數量必須至少為 1，重量不可為負數！", "error")
        return None
    if name is None:
        return None
    return name, quantity, weight, request.form.get("description", "").strip()


def _route_form_values():
    values = [
        _required_text("name", "路線名稱"),
        _required_text("start_point", "路線起點"),
        _required_text("end_point", "路線終點"),
    ]
    if any(value is None for value in values):
        return None
    waypoints = [
        point.strip()
        for point in request.form.get("waypoints", "").split(",")
        if point.strip()
    ]
    return (*values, waypoints)

# 首頁路由
@app.route('/')
def index():
    # 計算統計資料
    total_cargo = len(cargo_data)
    total_routes = len(routes_data)
    total_shipments = len(shipments_data)
    
    # 計算總重量
    total_weight = sum(cargo.weight * cargo.quantity for cargo in cargo_data)
    
    # 獲取最近的貨物和路線
    recent_cargo = cargo_data[-5:] if cargo_data else []
    recent_routes = routes_data[-5:] if routes_data else []
    
    return render_template('index.html', 
                         total_cargo=total_cargo,
                         total_routes=total_routes,
                         total_shipments=total_shipments,
                         total_weight=total_weight,
                         recent_cargo=recent_cargo,
                         recent_routes=recent_routes)

# 貨物管理路由
@app.route('/cargo')
def cargo_list():
    search = request.args.get('search', '')
    if search:
        filtered_cargo = [c for c in cargo_data if search.lower() in c.name.lower()]
    else:
        filtered_cargo = cargo_data
    return render_template('cargo_list.html', cargo_list=filtered_cargo, search=search)

@app.route('/cargo/add', methods=['GET', 'POST'])
def cargo_add():
    if request.method == 'POST':
        values = _cargo_form_values()
        if values is None:
            return redirect(url_for('cargo_add'))
        name, quantity, weight, description = values
        
        new_cargo = Cargo(name, quantity, weight, description)
        cargo_data.append(new_cargo)
        flash('貨物 "{}" 已成功新增！'.format(name), 'success')
        return redirect(url_for('cargo_list'))
    
    return render_template('cargo_form.html', title='新增貨物')

@app.route('/cargo/edit/<int:cargo_id>', methods=['GET', 'POST'])
def cargo_edit(cargo_id):
    cargo = next((c for c in cargo_data if c.id == cargo_id), None)
    if not cargo:
        flash('找不到指定的貨物！', 'error')
        return redirect(url_for('cargo_list'))
    
    if request.method == 'POST':
        values = _cargo_form_values()
        if values is None:
            return redirect(url_for('cargo_edit', cargo_id=cargo_id))
        cargo.name, cargo.quantity, cargo.weight, cargo.description = values
        
        flash('貨物 "{}" 已成功更新！'.format(cargo.name), 'success')
        return redirect(url_for('cargo_list'))
    
    return render_template('cargo_form.html', title='編輯貨物', cargo=cargo)

@app.route('/cargo/delete/<int:cargo_id>', methods=['POST'])
def cargo_delete(cargo_id):
    global cargo_data
    if any(shipment.cargo_id == cargo_id for shipment in shipments_data):
        flash('此貨物已有配送紀錄，請先刪除相關配送後再操作！', 'error')
        return redirect(url_for('cargo_list'))
    if not any(cargo.id == cargo_id for cargo in cargo_data):
        flash('找不到指定的貨物！', 'error')
        return redirect(url_for('cargo_list'))
    cargo_data = [c for c in cargo_data if c.id != cargo_id]
    flash('貨物已成功刪除！', 'success')
    return redirect(url_for('cargo_list'))

# 路線管理路由
@app.route('/routes')
def routes_list():
    search = request.args.get('search', '')
    if search:
        filtered_routes = [r for r in routes_data if search.lower() in r.name.lower()]
    else:
        filtered_routes = routes_data
    return render_template('routes_list.html', routes_list=filtered_routes, search=search)

@app.route('/routes/add', methods=['GET', 'POST'])
def routes_add():
    if request.method == 'POST':
        values = _route_form_values()
        if values is None:
            return redirect(url_for('routes_add'))
        name, start_point, end_point, waypoints = values
        
        new_route = Route(name, start_point, end_point, waypoints)
        routes_data.append(new_route)
        flash('路線 "{}" 已成功新增！'.format(name), 'success')
        return redirect(url_for('routes_list'))
    
    return render_template('routes_form.html', title='新增路線')

@app.route('/routes/edit/<int:route_id>', methods=['GET', 'POST'])
def routes_edit(route_id):
    route = next((r for r in routes_data if r.id == route_id), None)
    if not route:
        flash('找不到指定的路線！', 'error')
        return redirect(url_for('routes_list'))
    
    if request.method == 'POST':
        values = _route_form_values()
        if values is None:
            return redirect(url_for('routes_edit', route_id=route_id))
        route.name, route.start_point, route.end_point, route.waypoints = values
        
        flash('路線 "{}" 已成功更新！'.format(route.name), 'success')
        return redirect(url_for('routes_list'))
    
    return render_template('routes_form.html', title='編輯路線', route=route)

@app.route('/routes/delete/<int:route_id>', methods=['POST'])
def routes_delete(route_id):
    global routes_data
    if any(shipment.route_id == route_id for shipment in shipments_data):
        flash('此路線已有配送紀錄，請先刪除相關配送後再操作！', 'error')
        return redirect(url_for('routes_list'))
    if not any(route.id == route_id for route in routes_data):
        flash('找不到指定的路線！', 'error')
        return redirect(url_for('routes_list'))
    routes_data = [r for r in routes_data if r.id != route_id]
    flash('路線已成功刪除！', 'success')
    return redirect(url_for('routes_list'))

# 配送管理路由
@app.route('/shipments')
def shipments_list():
    # 為每個配送添加貨物和路線資訊
    shipments_with_details = []
    for shipment in shipments_data:
        cargo = next((c for c in cargo_data if c.id == shipment.cargo_id), None)
        route = next((r for r in routes_data if r.id == shipment.route_id), None)
        shipments_with_details.append({
            'shipment': shipment,
            'cargo': cargo,
            'route': route
        })
    
    return render_template('shipments_list.html', shipments=shipments_with_details)

@app.route('/shipments/assign', methods=['GET', 'POST'])
def shipments_assign():
    if request.method == 'POST':
        try:
            cargo_id = int(request.form.get('cargo_id', ''))
            route_id = int(request.form.get('route_id', ''))
        except (TypeError, ValueError):
            flash('請選擇有效的貨物和路線！', 'error')
            return redirect(url_for('shipments_assign'))
        
        # 檢查貨物和路線是否存在
        cargo = next((c for c in cargo_data if c.id == cargo_id), None)
        route = next((r for r in routes_data if r.id == route_id), None)
        
        if not cargo or not route:
            flash('請選擇有效的貨物和路線！', 'error')
            return redirect(url_for('shipments_assign'))
        
        # 檢查是否已經分配過
        existing = next((s for s in shipments_data if s.cargo_id == cargo_id and s.route_id == route_id), None)
        if existing:
            flash('此貨物已經分配到該路線！', 'error')
            return redirect(url_for('shipments_assign'))
        
        new_shipment = Shipment(cargo_id, route_id)
        shipments_data.append(new_shipment)
        flash('貨物 "{}" 已成功分配到路線 "{}"！'.format(cargo.name, route.name), 'success')
        return redirect(url_for('shipments_list'))
    
    return render_template('shipments_assign.html', cargo_list=cargo_data, routes_list=routes_data)

@app.route('/shipments/update_status/<int:shipment_id>/<status>', methods=['POST'])
def shipments_update_status(shipment_id, status):
    shipment = next((s for s in shipments_data if s.id == shipment_id), None)
    allowed_transitions = {
        '待配送': {'配送中', '已取消'},
        '配送中': {'已送達', '已取消'},
    }
    if shipment is None:
        flash('找不到指定的配送紀錄！', 'error')
    elif status not in allowed_transitions.get(shipment.status, set()):
        flash('此配送狀態轉換不合法！', 'error')
    else:
        shipment.status = status
        flash('配送狀態已更新！', 'success')
    return redirect(url_for('shipments_list'))

@app.route('/shipments/delete/<int:shipment_id>', methods=['POST'])
def shipments_delete(shipment_id):
    global shipments_data
    if not any(shipment.id == shipment_id for shipment in shipments_data):
        flash('找不到指定的配送紀錄！', 'error')
        return redirect(url_for('shipments_list'))
    shipments_data = [s for s in shipments_data if s.id != shipment_id]
    flash('配送記錄已刪除！', 'success')
    return redirect(url_for('shipments_list'))

def run_app():
    app.run(
        debug=os.environ.get("TMS_DEBUG") == "1",
        host=os.environ.get("TMS_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )


if __name__ == '__main__':
    run_app()
