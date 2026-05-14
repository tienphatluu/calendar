import tkinter as tk
from tkinter import colorchooser
from tkcalendar import Calendar
import json, os, datetime, calendar, requests
from lunardate import LunarDate   # Thư viện lịch âm

NOTES_FILE = "notes.json"

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}   

def save_notes():
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def load_holidays(year):
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/VN"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            holidays = r.json()
            local_data = {}
            if os.path.exists("holidays.json"):
                with open("holidays.json", "r", encoding="utf-8") as f:
                    local_data = json.load(f)
            local_data[str(year)] = holidays
            with open("holidays.json", "w", encoding="utf-8") as f:
                json.dump(local_data, f, ensure_ascii=False, indent=2)
            return holidays
    except Exception:
        print("Không có mạng, dùng dữ liệu cục bộ.")

    if os.path.exists("holidays.json"):
        with open("holidays.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(str(year), [])
    return []

def show_notes(event, cal, note_text, lunar_label):
    day = cal.selection_get()
    day_iso = day.isoformat()
    note = notes.get(day_iso, {}).get("text", "")
    note_text.delete("1.0", tk.END)
    note_text.insert(tk.END, note)

    # Hiển thị ngày âm lịch riêng biệt
    try:
        lunar = LunarDate.fromSolarDate(day.year, day.month, day.day)
        lunar_label.config(text=f"Âm lịch: {lunar.day}/{lunar.month}/{lunar.year}")
    except Exception as e:
        lunar_label.config(text=f"Không thể chuyển đổi lịch âm: {e}")

def save_note(cal, note_text, color_var, listbox):
    day = cal.selection_get().isoformat()
    note = note_text.get("1.0", tk.END).strip()
    color = color_var.get()
    notes[day] = {"text": note, "color": color}
    refresh_events(cal)
    update_event_list(listbox)
    save_notes()

def delete_note(cal, note_text, listbox):
    day = cal.selection_get().isoformat()
    if day in notes:
        del notes[day]
        refresh_events(cal)
        update_event_list(listbox)
        save_notes()
    note_text.delete("1.0", tk.END)

def choose_color(color_var):
    color = colorchooser.askcolor()[1]
    if color:
        color_var.set(color)

def refresh_events(cal):
    cal.calevent_remove('all')
    month, year = cal.get_displayed_month()

    for d in calendar.Calendar().itermonthdates(year, month):
        if d.month == month:
            if d.weekday() == 5:
                cal.calevent_create(d, "Thứ 7", tags=f"sat{d}")
                cal.tag_config(f"sat{d}", background="lightgreen", foreground="black")
            elif d.weekday() == 6:
                cal.calevent_create(d, "Chủ nhật", tags=f"sun{d}")
                cal.tag_config(f"sun{d}", background="red", foreground="white")

    holidays = load_holidays(year)
    for h in holidays:
        try:
            d = datetime.date.fromisoformat(h["date"])
            if d.month == month:
                cal.calevent_create(d, h["localName"], tags=f"holiday{d}")
                cal.tag_config(f"holiday{d}", background="red", foreground="white")
        except Exception as e:
            print("Lỗi ngày lễ:", e)

    for d, ev in notes.items():
        try:
            cal.calevent_create(datetime.date.fromisoformat(d), ev["text"], tags=d)
            cal.tag_config(d, background=ev["color"])
        except Exception as e:
            print("Lỗi sự kiện:", e)

def update_event_list(listbox):
    listbox.delete(0, tk.END)
    for d, ev in sorted(notes.items()):
        listbox.insert(tk.END, f"{d}: {ev['text']} ({ev['color']})")

def on_list_select(event, cal):
    selection = event.widget.curselection()
    if selection:
        value = event.widget.get(selection[0])
        day_str = value.split(":")[0]
        try:
            day = datetime.date.fromisoformat(day_str)
            cal.selection_set(day)
        except Exception as e:
            print("Lỗi chọn ngày:", e)

def go_to_today(cal, note_text, lunar_label):
    now = datetime.datetime.now()
    cal.selection_set(now.date())
    note_text.delete("1.0", tk.END)
    note_text.insert(tk.END, f"Hôm nay: {now.date()}")

    try:
        lunar = LunarDate.fromSolarDate(now.year, now.month, now.day)
        lunar_label.config(text=f"Âm lịch: {lunar.day}/{lunar.month}/{lunar.year}")
    except Exception as e:
        lunar_label.config(text=f"Không thể chuyển đổi lịch âm: {e}")

    refresh_events(cal)

def update_clock(clock_label):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=f"⏰ {now}")
    clock_label.after(1000, lambda: update_clock(clock_label))

# --- Tính số ngày giữa 2 mốc ---
def calc_days_between(entry1, entry2, result_label):
    try:
        d1 = datetime.datetime.strptime(entry1.get(), "%d/%m/%Y").date()
        d2 = datetime.datetime.strptime(entry2.get(), "%d/%m/%Y").date()
        diff = abs((d2 - d1).days)
        result_label.config(text=f"Số ngày giữa hai mốc: {diff} ngày")
    except Exception as e:
        result_label.config(text=f"Lỗi nhập liệu: {e}")

# ------------------ MAIN ------------------
root = tk.Tk()
root.title("Professional Calendar GUI")

notes = load_notes()
today = datetime.datetime.now()

cal = Calendar(
    root,
    selectmode="day",
    year=today.year,
    month=today.month,
    day=today.day,
    font=("Times New Roman", 16)
)
cal.pack(pady=10)

note_text = tk.Text(root, height=2, width=50, font=("Times New Roman", 14))
note_text.pack()

lunar_label = tk.Label(root, font=("Times New Roman", 14), fg="purple")
lunar_label.pack()

color_var = tk.StringVar(value="yellow")
# Tạo frame chứa 2 nút
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

color_btn = tk.Button(btn_frame, text="Choose Event Color", command=lambda: choose_color(color_var))
color_btn.pack(side="left", padx=5)

today_btn = tk.Button(btn_frame, text="Go to Today", command=lambda: go_to_today(cal, note_text, lunar_label))
today_btn.pack(side="left", padx=5)


cal.bind("<<CalendarSelected>>", lambda e: show_notes(e, cal, note_text, lunar_label))
cal.bind("<<CalendarMonthChanged>>", lambda e: refresh_events(cal))

listbox = tk.Listbox(root, width=60, height=5, font=("Times New Roman", 12))
listbox.pack(pady=10)
listbox.bind("<<ListboxSelect>>", lambda e: on_list_select(e, cal))

# Thay vì save_btn.pack() và delete_btn.pack() riêng lẻ
btn_save_frame = tk.Frame(root)
btn_save_frame.pack(pady=5)

save_btn = tk.Button(btn_save_frame, text="Save Note",
                     command=lambda: save_note(cal, note_text, color_var, listbox))
save_btn.pack(side="left", padx=5)

delete_btn = tk.Button(btn_save_frame, text="Delete Note",
                       command=lambda: delete_note(cal, note_text, listbox))
delete_btn.pack(side="left", padx=5)

# Khung tính số ngày giữa 2 mốc
frame_days = tk.Frame(root)
frame_days.pack(pady=10)

# Gom Ngày 1 và Ngày 2 vào cùng một hàng
tk.Label(frame_days, text="Ngày 1 (dd/mm/yyyy):").pack(side="left")
entry_date1 = tk.Entry(frame_days, width=12)
entry_date1.pack(side="left", padx=5)

tk.Label(frame_days, text="Ngày 2 (dd/mm/yyyy):").pack(side="left")
entry_date2 = tk.Entry(frame_days, width=12)
entry_date2.pack(side="left", padx=5)

# Kết quả và nút tính số ngày đặt bên dưới
result_label = tk.Label(root, text="", font=("Times New Roman", 12), fg="green")
result_label.pack(pady=5)

calc_btn = tk.Button(root, text="Tính số ngày",
                     command=lambda: calc_days_between(entry_date1, entry_date2, result_label))
calc_btn.pack(pady=5)

# Đồng hồ ở góc dưới
clock_label = tk.Label(root, font=("Times New Roman", 14), fg="blue")
clock_label.pack(side="bottom", pady=5)
update_clock(clock_label)

refresh_events(cal)
update_event_list(listbox)

root.mainloop()
