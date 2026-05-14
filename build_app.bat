@echo off
REM Di chuyển vào thư mục chứa make_calendar.py
cd /d E:\TAI_LIEU\AI\lich

REM Xóa build cũ (tùy chọn, để tránh rác)
rmdir /s /q build
rmdir /s /q dist
del make_calendar.spec

REM Build lại app.exe bằng PyInstaller
python -m PyInstaller --noconsole --onefile make_calendar.py

REM Copy file exe ra thư mục chính
copy dist\make_calendar.exe make_calendar.exe

echo ============================================
echo Build hoàn tất! File make_calendar.exe đã sẵn sàng.
echo Bạn có thể chạy trực tiếp bằng make_calendar.exe
echo ============================================
pause
