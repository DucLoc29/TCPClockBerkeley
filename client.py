import socket
import time
import subprocess
import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext

# --- CÁC HÀM QUY ĐỔI FORMAT GIỜ ---
def get_local_seconds():
    now = datetime.datetime.now()
    return now.hour * 3600 + now.minute * 60 + now.second + (now.microsecond / 1e6)

def seconds_to_hms(total_seconds):
    total_seconds = int(total_seconds % 86400)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_duration(seconds):
    sign = "+" if seconds >= 0 else "-"
    sec = abs(seconds)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{sign}{h:02d}:{m:02d}:{s:06.3f}"

class BerkeleyClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy Khách (Berkeley Slave)")
        self.root.geometry("650x450")

        frame = tk.Frame(root)
        frame.pack(pady=10)
        tk.Label(frame, text="IP Máy Chủ:").pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(frame, width=20)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_connect = tk.Button(frame, text="Kết nối", command=self.start_client_thread)
        self.btn_connect.pack(side=tk.LEFT)

        self.log_area = scrolledtext.ScrolledText(root, width=85, height=20, state='disabled', font=("Consolas", 10))
        self.log_area.pack(padx=10, pady=10)

        self.client_socket = None

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')

    def update_windows_time(self, offset_seconds):
        old_total_seconds = get_local_seconds()
        new_total_seconds = old_total_seconds + offset_seconds
        
        old_time_str = seconds_to_hms(old_total_seconds)
        new_time_str = seconds_to_hms(new_total_seconds)
        
        self.log(f"\n[+] Nhận lệnh bù trừ từ Server: {format_duration(offset_seconds)}")
        self.log(f"    -> Giờ hiện tại: [{old_time_str}]")
        self.log(f"    -> Giờ mới (sau bù trừ): [{new_time_str}]")
        self.log(f"    -> Chi tiết phép tính: [{old_time_str}] + ({format_duration(offset_seconds)}) = [{new_time_str}]")
        
        try:
            subprocess.run(["cmd", "/c", f"time {new_time_str}"], check=True)
            self.log(f"[*] ĐÃ ĐỔI GIỜ HỆ THỐNG THÀNH: [{new_time_str}]")
        except subprocess.CalledProcessError:
            self.log("[!] LỖI: Không có quyền Admin. Windows từ chối đổi giờ!")

    def start_client_thread(self):
        ip = self.ip_entry.get()
        self.btn_connect.config(state=tk.DISABLED)
        threading.Thread(target=self.run_client, args=(ip,), daemon=True).start()

    def run_client(self, server_ip):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((server_ip, 5000))
            self.log(f"[*] Đã kết nối thành công tới Server: {server_ip}")
            
            while True:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                    
                if data == "GET_TIME":
                    current_local_sec = get_local_seconds()
                    self.client_socket.sendall(str(current_local_sec).encode())
                    
                    time_str = seconds_to_hms(current_local_sec)
                    self.log(f"[>] Server hỏi giờ. Đã gửi: [{time_str}]")
                    
                elif data.startswith("SET_OFFSET:"):
                    offset = float(data.split(":")[1])
                    self.update_windows_time(offset)
                    
        except Exception as e:
            self.log(f"[!] Lỗi kết nối: {e}")
            self.btn_connect.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = BerkeleyClientGUI(root)
    root.mainloop()