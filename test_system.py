#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست سیستم مدیریت تعمیرات معدن
Test Script for Mine Maintenance Management System
"""

from mine_maintenance_system import MineMaintenanceSystem, Equipment, MaintenanceTask, InventoryItem, EquipmentStatus, MaintenanceType, Priority
from datetime import datetime, timedelta
import json

def test_system():
    """تست کامل سیستم"""
    print("🧪 شروع تست سیستم مدیریت تعمیرات معدن")
    print("=" * 60)
    
    # ایجاد نمونه سیستم
    system = MineMaintenanceSystem("test_mine.db")
    
    # تست 1: افزودن تجهیزات
    print("\n1️⃣ تست افزودن تجهیزات...")
    
    equipment_list = [
        Equipment(
            id=0, name="حفار اصلی", model="CAT 320D", serial_number="CAT320D001",
            location="بخش A معدن", status=EquipmentStatus.ACTIVE,
            last_maintenance=datetime.now() - timedelta(days=30),
            next_maintenance=datetime.now() + timedelta(days=15),
            maintenance_interval_days=45, cost=500000.0,
            purchase_date=datetime(2020, 1, 15),
            warranty_expiry=datetime(2025, 1, 15)
        ),
        Equipment(
            id=0, name="لودر", model="CAT 950M", serial_number="CAT950M001",
            location="بخش B معدن", status=EquipmentStatus.ACTIVE,
            last_maintenance=datetime.now() - timedelta(days=15),
            next_maintenance=datetime.now() + timedelta(days=30),
            maintenance_interval_days=45, cost=350000.0,
            purchase_date=datetime(2021, 3, 10),
            warranty_expiry=datetime(2026, 3, 10)
        ),
        Equipment(
            id=0, name="کامیون", model="Volvo FMX", serial_number="VOLVO001",
            location="بخش C معدن", status=EquipmentStatus.MAINTENANCE,
            last_maintenance=datetime.now() - timedelta(days=5),
            next_maintenance=datetime.now() + timedelta(days=10),
            maintenance_interval_days=30, cost=400000.0,
            purchase_date=datetime(2019, 8, 20),
            warranty_expiry=None
        )
    ]
    
    for equipment in equipment_list:
        if system.add_equipment(equipment):
            print(f"   ✅ تجهیز '{equipment.name}' اضافه شد")
        else:
            print(f"   ❌ خطا در افزودن تجهیز '{equipment.name}'")
    
    # تست 2: افزودن کارهای تعمیرات
    print("\n2️⃣ تست افزودن کارهای تعمیرات...")
    
    maintenance_tasks = [
        MaintenanceTask(
            id=0, equipment_id=1, task_type=MaintenanceType.PREVENTIVE,
            priority=Priority.MEDIUM, description="تعمیر دوره‌ای موتور",
            assigned_technician="احمد محمدی", 
            scheduled_date=datetime.now() + timedelta(days=7),
            completed_date=None, status="برنامه‌ریزی شده", cost=5000.0,
            parts_used=["فیلتر هوا", "روغن موتور"], notes="تعمیر پیشگیرانه"
        ),
        MaintenanceTask(
            id=0, equipment_id=2, task_type=MaintenanceType.CORRECTIVE,
            priority=Priority.HIGH, description="تعمیر سیستم هیدرولیک",
            assigned_technician="علی رضایی", 
            scheduled_date=datetime.now() + timedelta(days=3),
            completed_date=None, status="برنامه‌ریزی شده", cost=15000.0,
            parts_used=["پمپ هیدرولیک", "شلنگ فشار قوی"], notes="تعمیر اضطراری"
        ),
        MaintenanceTask(
            id=0, equipment_id=3, task_type=MaintenanceType.EMERGENCY,
            priority=Priority.CRITICAL, description="تعمیر ترمز",
            assigned_technician="محمد کریمی", 
            scheduled_date=datetime.now() + timedelta(days=1),
            completed_date=None, status="در حال انجام", cost=25000.0,
            parts_used=["کالیپر ترمز", "لنت ترمز"], notes="تعمیر فوری"
        )
    ]
    
    for task in maintenance_tasks:
        if system.schedule_maintenance(task):
            print(f"   ✅ کار تعمیرات '{task.description}' برنامه‌ریزی شد")
        else:
            print(f"   ❌ خطا در برنامه‌ریزی کار '{task.description}'")
    
    # تست 3: افزودن موجودی
    print("\n3️⃣ تست افزودن موجودی...")
    
    inventory_items = [
        InventoryItem(
            id=0, part_name="فیلتر هوا", part_number="AIR001",
            category="فیلتر", quantity=50, min_quantity=10,
            unit_price=150000.0, supplier="تامین‌کننده A", location="انبار 1"
        ),
        InventoryItem(
            id=0, part_name="روغن موتور", part_number="OIL001",
            category="روغن", quantity=25, min_quantity=5,
            unit_price=80000.0, supplier="تامین‌کننده B", location="انبار 2"
        ),
        InventoryItem(
            id=0, part_name="لنت ترمز", part_number="BRAKE001",
            category="ترمز", quantity=3, min_quantity=5,
            unit_price=500000.0, supplier="تامین‌کننده C", location="انبار 1"
        )
    ]
    
    for item in inventory_items:
        if system.add_inventory_item(item):
            print(f"   ✅ قطعه '{item.part_name}' اضافه شد")
        else:
            print(f"   ❌ خطا در افزودن قطعه '{item.part_name}'")
    
    # تست 4: دریافت آمار
    print("\n4️⃣ تست دریافت آمار...")
    
    # آمار تجهیزات
    equipment_status = system.get_equipment_status_summary()
    print(f"   📊 کل تجهیزات: {equipment_status['total_equipment']}")
    print(f"   📊 وضعیت تجهیزات: {equipment_status['status_breakdown']}")
    print(f"   📊 درصد فعال: {equipment_status['active_percentage']:.1f}%")
    
    # کارهای تعمیرات
    tasks = system.get_maintenance_tasks()
    print(f"   🔧 کل کارهای تعمیرات: {len(tasks)}")
    
    # قطعات کم موجود
    low_stock = system.get_low_stock_items()
    print(f"   ⚠️ قطعات کم موجود: {len(low_stock)}")
    for item in low_stock:
        print(f"      - {item.part_name}: {item.quantity} (حداقل: {item.min_quantity})")
    
    # تست 5: گزارش‌گیری
    print("\n5️⃣ تست گزارش‌گیری...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    report = system.generate_maintenance_report(start_date, end_date)
    
    print(f"   📈 دوره گزارش: {report['period']}")
    print(f"   📈 کل کارها: {report['total_tasks']}")
    print(f"   📈 کارهای تکمیل شده: {report['completed_tasks']}")
    print(f"   📈 نرخ تکمیل: {report['completion_rate']:.1f}%")
    print(f"   📈 هزینه کل: {report['total_cost']:,.0f} ریال")
    
    # تست 6: نمایش لیست‌ها
    print("\n6️⃣ تست نمایش لیست‌ها...")
    
    # لیست تجهیزات
    equipment_list = system.get_equipment()
    print(f"   📋 لیست تجهیزات ({len(equipment_list)} مورد):")
    for equipment in equipment_list:
        print(f"      - {equipment.name} ({equipment.model}) - {equipment.status.value}")
    
    # لیست کارهای تعمیرات
    tasks = system.get_maintenance_tasks()
    print(f"   📋 لیست کارهای تعمیرات ({len(tasks)} مورد):")
    for task in tasks:
        print(f"      - {task.description} (اولویت: {task.priority.value}) - {task.status}")
    
    print("\n✅ تست سیستم با موفقیت تکمیل شد!")
    print("=" * 60)

def demo_web_interface():
    """دموی رابط کاربری وب"""
    print("\n🌐 راه‌اندازی رابط کاربری وب...")
    print("برای مشاهده رابط کاربری:")
    print("1. دستور زیر را اجرا کنید:")
    print("   python web_interface.py")
    print("2. مرورگر را باز کنید")
    print("3. به آدرس http://localhost:5000 بروید")
    print("\nویژگی‌های رابط کاربری:")
    print("   📊 داشبورد با آمار کلی")
    print("   🔧 مدیریت تجهیزات")
    print("   🛠️ برنامه‌ریزی تعمیرات")
    print("   📦 مدیریت موجودی")
    print("   📈 گزارش‌گیری و آمار")

if __name__ == "__main__":
    test_system()
    demo_web_interface()