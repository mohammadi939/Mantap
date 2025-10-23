#!/bin/bash

# اسکریپت راه‌اندازی سیستم مدیریت تعمیرات معدن
# Mine Maintenance Management System Startup Script

echo "🏭 راه‌اندازی سیستم مدیریت تعمیرات معدن"
echo "========================================"

# بررسی وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 یافت نشد. لطفاً Python3 را نصب کنید."
    exit 1
fi

# بررسی وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 یافت نشد. لطفاً pip3 را نصب کنید."
    exit 1
fi

echo "✅ Python3 و pip3 یافت شد"

# نصب وابستگی‌ها
echo "📦 نصب وابستگی‌ها..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ وابستگی‌ها با موفقیت نصب شد"
else
    echo "❌ خطا در نصب وابستگی‌ها"
    exit 1
fi

# اجرای تست سیستم
echo "🧪 اجرای تست سیستم..."
python3 test_system.py

if [ $? -eq 0 ]; then
    echo "✅ تست سیستم با موفقیت تکمیل شد"
else
    echo "❌ خطا در تست سیستم"
    exit 1
fi

# راه‌اندازی رابط کاربری وب
echo "🌐 راه‌اندازی رابط کاربری وب..."
echo "سیستم در حال راه‌اندازی است..."
echo "برای دسترسی به سیستم، مرورگر را باز کنید و به آدرس زیر بروید:"
echo "http://localhost:5000"
echo ""
echo "برای توقف سیستم، Ctrl+C را فشار دهید"
echo ""

# اجرای رابط کاربری
python3 web_interface.py