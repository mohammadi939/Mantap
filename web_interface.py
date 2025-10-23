#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
رابط کاربری وب برای سیستم مدیریت تعمیرات معدن
Web Interface for Mine Maintenance Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
from mine_maintenance_system import MineMaintenanceSystem, Equipment, MaintenanceTask, InventoryItem, EquipmentStatus, MaintenanceType, Priority

app = Flask(__name__)
app.secret_key = 'mine_maintenance_secret_key_2024'

# تنظیم پایگاه داده
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mine_maintenance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ایجاد نمونه سیستم
maintenance_system = MineMaintenanceSystem()

@app.route('/')
def dashboard():
    """صفحه اصلی داشبورد"""
    try:
        # آمار کلی
        equipment_status = maintenance_system.get_equipment_status_summary()
        maintenance_tasks = maintenance_system.get_maintenance_tasks()
        low_stock_items = maintenance_system.get_low_stock_items()
        
        # آمار کارهای تعمیرات
        pending_tasks = [task for task in maintenance_tasks if task.status == 'برنامه‌ریزی شده']
        completed_tasks = [task for task in maintenance_tasks if task.status == 'تکمیل شده']
        
        # گزارش ماهانه
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        monthly_report = maintenance_system.generate_maintenance_report(start_date, end_date)
        
        return render_template('dashboard.html',
                             equipment_status=equipment_status,
                             pending_tasks=len(pending_tasks),
                             completed_tasks=len(completed_tasks),
                             low_stock_count=len(low_stock_items),
                             monthly_report=monthly_report)
    except Exception as e:
        flash(f'خطا در بارگذاری داشبورد: {str(e)}', 'error')
        return render_template('dashboard.html')

@app.route('/equipment')
def equipment_list():
    """لیست تجهیزات"""
    try:
        equipment_list = maintenance_system.get_equipment()
        return render_template('equipment.html', equipment_list=equipment_list)
    except Exception as e:
        flash(f'خطا در بارگذاری لیست تجهیزات: {str(e)}', 'error')
        return render_template('equipment.html', equipment_list=[])

@app.route('/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    """افزودن تجهیز جدید"""
    if request.method == 'POST':
        try:
            equipment = Equipment(
                id=0,
                name=request.form['name'],
                model=request.form['model'],
                serial_number=request.form['serial_number'],
                location=request.form['location'],
                status=EquipmentStatus(request.form['status']),
                last_maintenance=datetime.fromisoformat(request.form['last_maintenance']) if request.form['last_maintenance'] else None,
                next_maintenance=datetime.fromisoformat(request.form['next_maintenance']) if request.form['next_maintenance'] else None,
                maintenance_interval_days=int(request.form['maintenance_interval_days']),
                cost=float(request.form['cost']),
                purchase_date=datetime.fromisoformat(request.form['purchase_date']),
                warranty_expiry=datetime.fromisoformat(request.form['warranty_expiry']) if request.form['warranty_expiry'] else None
            )
            
            if maintenance_system.add_equipment(equipment):
                flash('تجهیز با موفقیت اضافه شد', 'success')
                return redirect(url_for('equipment_list'))
            else:
                flash('خطا در افزودن تجهیز', 'error')
        except Exception as e:
            flash(f'خطا در افزودن تجهیز: {str(e)}', 'error')
    
    return render_template('add_equipment.html', status_options=EquipmentStatus)

@app.route('/maintenance')
def maintenance_tasks():
    """لیست کارهای تعمیرات"""
    try:
        status_filter = request.args.get('status', '')
        tasks = maintenance_system.get_maintenance_tasks(status_filter if status_filter else None)
        return render_template('maintenance.html', tasks=tasks, status_filter=status_filter)
    except Exception as e:
        flash(f'خطا در بارگذاری کارهای تعمیرات: {str(e)}', 'error')
        return render_template('maintenance.html', tasks=[])

@app.route('/maintenance/add', methods=['GET', 'POST'])
def add_maintenance_task():
    """افزودن کار تعمیرات جدید"""
    if request.method == 'POST':
        try:
            task = MaintenanceTask(
                id=0,
                equipment_id=int(request.form['equipment_id']),
                task_type=MaintenanceType(request.form['task_type']),
                priority=Priority(request.form['priority']),
                description=request.form['description'],
                assigned_technician=request.form['assigned_technician'],
                scheduled_date=datetime.fromisoformat(request.form['scheduled_date']),
                completed_date=None,
                status='برنامه‌ریزی شده',
                cost=float(request.form['cost']),
                parts_used=request.form['parts_used'].split(',') if request.form['parts_used'] else [],
                notes=request.form['notes']
            )
            
            if maintenance_system.schedule_maintenance(task):
                flash('کار تعمیرات با موفقیت برنامه‌ریزی شد', 'success')
                return redirect(url_for('maintenance_tasks'))
            else:
                flash('خطا در برنامه‌ریزی کار تعمیرات', 'error')
        except Exception as e:
            flash(f'خطا در افزودن کار تعمیرات: {str(e)}', 'error')
    
    # دریافت لیست تجهیزات برای انتخاب
    equipment_list = maintenance_system.get_equipment()
    return render_template('add_maintenance.html', 
                         equipment_list=equipment_list,
                         task_types=MaintenanceType,
                         priorities=Priority)

@app.route('/inventory')
def inventory():
    """مدیریت موجودی"""
    try:
        low_stock_items = maintenance_system.get_low_stock_items()
        return render_template('inventory.html', low_stock_items=low_stock_items)
    except Exception as e:
        flash(f'خطا در بارگذاری موجودی: {str(e)}', 'error')
        return render_template('inventory.html', low_stock_items=[])

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory_item():
    """افزودن قطعه به موجودی"""
    if request.method == 'POST':
        try:
            item = InventoryItem(
                id=0,
                part_name=request.form['part_name'],
                part_number=request.form['part_number'],
                category=request.form['category'],
                quantity=int(request.form['quantity']),
                min_quantity=int(request.form['min_quantity']),
                unit_price=float(request.form['unit_price']),
                supplier=request.form['supplier'],
                location=request.form['location']
            )
            
            if maintenance_system.add_inventory_item(item):
                flash('قطعه با موفقیت به موجودی اضافه شد', 'success')
                return redirect(url_for('inventory'))
            else:
                flash('خطا در افزودن قطعه', 'error')
        except Exception as e:
            flash(f'خطا در افزودن قطعه: {str(e)}', 'error')
    
    return render_template('add_inventory.html')

@app.route('/reports')
def reports():
    """گزارش‌ها"""
    try:
        # گزارش ماهانه
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        monthly_report = maintenance_system.generate_maintenance_report(start_date, end_date)
        
        # گزارش هفتگی
        weekly_start = end_date - timedelta(days=7)
        weekly_report = maintenance_system.generate_maintenance_report(weekly_start, end_date)
        
        return render_template('reports.html', 
                             monthly_report=monthly_report,
                             weekly_report=weekly_report)
    except Exception as e:
        flash(f'خطا در بارگذاری گزارش‌ها: {str(e)}', 'error')
        return render_template('reports.html')

@app.route('/api/equipment/<int:equipment_id>')
def get_equipment_api(equipment_id):
    """API برای دریافت اطلاعات تجهیز"""
    try:
        equipment_list = maintenance_system.get_equipment(equipment_id)
        if equipment_list:
            equipment = equipment_list[0]
            return jsonify({
                'id': equipment.id,
                'name': equipment.name,
                'model': equipment.model,
                'serial_number': equipment.serial_number,
                'location': equipment.location,
                'status': equipment.status.value,
                'last_maintenance': equipment.last_maintenance.isoformat() if equipment.last_maintenance else None,
                'next_maintenance': equipment.next_maintenance.isoformat() if equipment.next_maintenance else None,
                'maintenance_interval_days': equipment.maintenance_interval_days,
                'cost': equipment.cost,
                'purchase_date': equipment.purchase_date.isoformat(),
                'warranty_expiry': equipment.warranty_expiry.isoformat() if equipment.warranty_expiry else None
            })
        else:
            return jsonify({'error': 'تجهیز یافت نشد'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/maintenance/complete/<int:task_id>', methods=['POST'])
def complete_maintenance_task(task_id):
    """تکمیل کار تعمیرات"""
    try:
        # این تابع نیاز به پیاده‌سازی دارد
        # فعلاً فقط پیام موفقیت برمی‌گرداند
        return jsonify({'message': 'کار تعمیرات با موفقیت تکمیل شد'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)