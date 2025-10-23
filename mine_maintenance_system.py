#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سیستم مدیریت تعمیرات معدن
Mine Maintenance Management System

این سیستم برای مدیریت تعمیرات، تجهیزات و موجودی در معادن طراحی شده است.
"""

import sqlite3
import datetime
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EquipmentStatus(Enum):
    """وضعیت تجهیزات"""
    ACTIVE = "فعال"
    MAINTENANCE = "در حال تعمیر"
    BROKEN = "خراب"
    RETIRED = "بازنشسته"

class MaintenanceType(Enum):
    """نوع تعمیرات"""
    PREVENTIVE = "پیشگیرانه"
    CORRECTIVE = "اصلاحی"
    EMERGENCY = "اضطراری"
    PREDICTIVE = "پیش‌بینی‌کننده"

class Priority(Enum):
    """اولویت"""
    LOW = "کم"
    MEDIUM = "متوسط"
    HIGH = "بالا"
    CRITICAL = "بحرانی"

@dataclass
class Equipment:
    """کلاس تجهیزات معدن"""
    id: int
    name: str
    model: str
    serial_number: str
    location: str
    status: EquipmentStatus
    last_maintenance: Optional[datetime.datetime]
    next_maintenance: Optional[datetime.datetime]
    maintenance_interval_days: int
    cost: float
    purchase_date: datetime.datetime
    warranty_expiry: Optional[datetime.datetime]

@dataclass
class MaintenanceTask:
    """کلاس کار تعمیرات"""
    id: int
    equipment_id: int
    task_type: MaintenanceType
    priority: Priority
    description: str
    assigned_technician: str
    scheduled_date: datetime.datetime
    completed_date: Optional[datetime.datetime]
    status: str
    cost: float
    parts_used: List[str]
    notes: str

@dataclass
class InventoryItem:
    """کلاس موجودی قطعات"""
    id: int
    part_name: str
    part_number: str
    category: str
    quantity: int
    min_quantity: int
    unit_price: float
    supplier: str
    location: str

class MineMaintenanceSystem:
    """سیستم اصلی مدیریت تعمیرات معدن"""
    
    def __init__(self, db_path: str = "mine_maintenance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """ایجاد جداول پایگاه داده"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول تجهیزات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model TEXT NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL,
                last_maintenance TEXT,
                next_maintenance TEXT,
                maintenance_interval_days INTEGER NOT NULL,
                cost REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                warranty_expiry TEXT
            )
        ''')
        
        # جدول کارهای تعمیرات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER NOT NULL,
                task_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                description TEXT NOT NULL,
                assigned_technician TEXT NOT NULL,
                scheduled_date TEXT NOT NULL,
                completed_date TEXT,
                status TEXT NOT NULL,
                cost REAL DEFAULT 0,
                parts_used TEXT,
                notes TEXT,
                FOREIGN KEY (equipment_id) REFERENCES equipment (id)
            )
        ''')
        
        # جدول موجودی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_name TEXT NOT NULL,
                part_number TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                min_quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                supplier TEXT NOT NULL,
                location TEXT NOT NULL
            )
        ''')
        
        # جدول کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("پایگاه داده با موفقیت راه‌اندازی شد")
    
    def add_equipment(self, equipment: Equipment) -> bool:
        """افزودن تجهیز جدید"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO equipment (name, model, serial_number, location, status,
                                     last_maintenance, next_maintenance, maintenance_interval_days,
                                     cost, purchase_date, warranty_expiry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                equipment.name, equipment.model, equipment.serial_number,
                equipment.location, equipment.status.value,
                equipment.last_maintenance.isoformat() if equipment.last_maintenance else None,
                equipment.next_maintenance.isoformat() if equipment.next_maintenance else None,
                equipment.maintenance_interval_days, equipment.cost,
                equipment.purchase_date.isoformat(),
                equipment.warranty_expiry.isoformat() if equipment.warranty_expiry else None
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"تجهیز {equipment.name} با موفقیت اضافه شد")
            return True
        except Exception as e:
            logger.error(f"خطا در افزودن تجهیز: {e}")
            return False
    
    def get_equipment(self, equipment_id: int = None) -> List[Equipment]:
        """دریافت لیست تجهیزات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if equipment_id:
            cursor.execute('SELECT * FROM equipment WHERE id = ?', (equipment_id,))
        else:
            cursor.execute('SELECT * FROM equipment ORDER BY name')
        
        rows = cursor.fetchall()
        conn.close()
        
        equipment_list = []
        for row in rows:
            equipment = Equipment(
                id=row[0], name=row[1], model=row[2], serial_number=row[3],
                location=row[4], status=EquipmentStatus(row[5]),
                last_maintenance=datetime.datetime.fromisoformat(row[6]) if row[6] else None,
                next_maintenance=datetime.datetime.fromisoformat(row[7]) if row[7] else None,
                maintenance_interval_days=row[8], cost=row[9],
                purchase_date=datetime.datetime.fromisoformat(row[10]),
                warranty_expiry=datetime.datetime.fromisoformat(row[11]) if row[11] else None
            )
            equipment_list.append(equipment)
        
        return equipment_list
    
    def schedule_maintenance(self, task: MaintenanceTask) -> bool:
        """برنامه‌ریزی تعمیرات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO maintenance_tasks (equipment_id, task_type, priority, description,
                                            assigned_technician, scheduled_date, status, cost, parts_used, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.equipment_id, task.task_type.value, task.priority.value,
                task.description, task.assigned_technician, task.scheduled_date.isoformat(),
                task.status, task.cost, json.dumps(task.parts_used), task.notes
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"کار تعمیرات برای تجهیز {task.equipment_id} برنامه‌ریزی شد")
            return True
        except Exception as e:
            logger.error(f"خطا در برنامه‌ریزی تعمیرات: {e}")
            return False
    
    def get_maintenance_tasks(self, status: str = None) -> List[MaintenanceTask]:
        """دریافت لیست کارهای تعمیرات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM maintenance_tasks WHERE status = ? ORDER BY scheduled_date', (status,))
        else:
            cursor.execute('SELECT * FROM maintenance_tasks ORDER BY scheduled_date')
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task = MaintenanceTask(
                id=row[0], equipment_id=row[1], task_type=MaintenanceType(row[2]),
                priority=Priority(row[3]), description=row[4], assigned_technician=row[5],
                scheduled_date=datetime.datetime.fromisoformat(row[6]),
                completed_date=datetime.datetime.fromisoformat(row[7]) if row[7] else None,
                status=row[8], cost=row[9], parts_used=json.loads(row[10]) if row[10] else [],
                notes=row[11]
            )
            tasks.append(task)
        
        return tasks
    
    def add_inventory_item(self, item: InventoryItem) -> bool:
        """افزودن قطعه به موجودی"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO inventory (part_name, part_number, category, quantity,
                                    min_quantity, unit_price, supplier, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.part_name, item.part_number, item.category, item.quantity,
                item.min_quantity, item.unit_price, item.supplier, item.location
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"قطعه {item.part_name} به موجودی اضافه شد")
            return True
        except Exception as e:
            logger.error(f"خطا در افزودن قطعه: {e}")
            return False
    
    def get_low_stock_items(self) -> List[InventoryItem]:
        """دریافت قطعات با موجودی کم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM inventory WHERE quantity <= min_quantity')
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            item = InventoryItem(
                id=row[0], part_name=row[1], part_number=row[2], category=row[3],
                quantity=row[4], min_quantity=row[5], unit_price=row[6],
                supplier=row[7], location=row[8]
            )
            items.append(item)
        
        return items
    
    def generate_maintenance_report(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Dict:
        """تولید گزارش تعمیرات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # آمار کلی
        cursor.execute('''
            SELECT COUNT(*) FROM maintenance_tasks 
            WHERE scheduled_date BETWEEN ? AND ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        total_tasks = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM maintenance_tasks 
            WHERE scheduled_date BETWEEN ? AND ? AND status = 'تکمیل شده'
        ''', (start_date.isoformat(), end_date.isoformat()))
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT SUM(cost) FROM maintenance_tasks 
            WHERE scheduled_date BETWEEN ? AND ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        total_cost = cursor.fetchone()[0] or 0
        
        # تجهیزات با بیشترین تعمیرات
        cursor.execute('''
            SELECT e.name, COUNT(m.id) as task_count
            FROM equipment e
            LEFT JOIN maintenance_tasks m ON e.id = m.equipment_id
            WHERE m.scheduled_date BETWEEN ? AND ?
            GROUP BY e.id, e.name
            ORDER BY task_count DESC
            LIMIT 5
        ''', (start_date.isoformat(), end_date.isoformat()))
        top_equipment = cursor.fetchall()
        
        conn.close()
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} تا {end_date.strftime('%Y-%m-%d')}",
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_cost': total_cost,
            'top_equipment': top_equipment
        }
    
    def get_equipment_status_summary(self) -> Dict:
        """خلاصه وضعیت تجهیزات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT status, COUNT(*) FROM equipment GROUP BY status')
        status_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM equipment')
        total_equipment = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_equipment': total_equipment,
            'status_breakdown': status_counts,
            'active_percentage': (status_counts.get('فعال', 0) / total_equipment * 100) if total_equipment > 0 else 0
        }

def main():
    """تابع اصلی برای تست سیستم"""
    print("🏭 سیستم مدیریت تعمیرات معدن")
    print("=" * 50)
    
    # ایجاد نمونه سیستم
    system = MineMaintenanceSystem()
    
    # افزودن تجهیز نمونه
    sample_equipment = Equipment(
        id=0, name="حفار اصلی", model="CAT 320D", serial_number="CAT320D001",
        location="بخش A معدن", status=EquipmentStatus.ACTIVE,
        last_maintenance=datetime.datetime.now() - datetime.timedelta(days=30),
        next_maintenance=datetime.datetime.now() + datetime.timedelta(days=15),
        maintenance_interval_days=45, cost=500000.0,
        purchase_date=datetime.datetime(2020, 1, 15),
        warranty_expiry=datetime.datetime(2025, 1, 15)
    )
    
    system.add_equipment(sample_equipment)
    
    # افزودن کار تعمیرات نمونه
    sample_task = MaintenanceTask(
        id=0, equipment_id=1, task_type=MaintenanceType.PREVENTIVE,
        priority=Priority.MEDIUM, description="تعمیر دوره‌ای موتور",
        assigned_technician="احمد محمدی", scheduled_date=datetime.datetime.now() + datetime.timedelta(days=7),
        completed_date=None, status="برنامه‌ریزی شده", cost=5000.0,
        parts_used=["فیلتر هوا", "روغن موتور"], notes="تعمیر پیشگیرانه"
    )
    
    system.schedule_maintenance(sample_task)
    
    # نمایش آمار
    status_summary = system.get_equipment_status_summary()
    print(f"📊 آمار تجهیزات:")
    print(f"   کل تجهیزات: {status_summary['total_equipment']}")
    print(f"   درصد فعال: {status_summary['active_percentage']:.1f}%")
    
    # نمایش کارهای تعمیرات
    tasks = system.get_maintenance_tasks()
    print(f"\n🔧 کارهای تعمیرات ({len(tasks)} مورد):")
    for task in tasks:
        print(f"   - {task.description} (اولویت: {task.priority.value})")

if __name__ == "__main__":
    main()