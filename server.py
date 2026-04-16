import socket
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import datetime

HOST = '0.0.0.0'
PORT = 5000
clients = {}

# --- CÁC HÀM QUY ĐỔI FORMAT GIỜ ---
def get_local_seconds():
    now = datetime.datetime.now()
    return now.hour * 3600 + now.minute * 60 + now.second + (now.microsecond / 1e6)

def seconds_to_hms(total_seconds):
    """Đổi giờ tuyệt đối thành [HH:MM:SS]"""
    total_seconds = int(total_seconds % 86400)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_duration(seconds):
    """Đổi số giây bù trừ thành khoảng thời gian [+/- HH:MM:SS.ms]"""
    sign = "+" if seconds >= 0 else "-"
    sec = abs(seconds)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{sign}{h:02d}:{m:02d}:{s:06.3f}"

class BerkeleyServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thuật toán Berkeley - Máy Chủ (Master)")
        self.root.geometry("850x650")

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=10)

        self.btn_start = tk.Button(self.btn_frame, text="Bắt đầu Server", command=self.start_server_thread, width=20)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_sync = tk.Button(self.btn_frame, text="Đồng bộ ngay", command=self.sync_clocks, state=tk.DISABLED, width=20)
        self.btn_sync.pack(side=tk.LEFT, padx=5)

        self.log_area = scrolledtext.ScrolledText(root, width=105, height=30, state='disabled', font=("Consolas", 10))
        self.log_area.pack(padx=10, pady=5)

        self.server_socket = None

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')

    def update_windows_time(self, offset_seconds):
        new_total_seconds = get_local_seconds() + offset_seconds
        new_time_str = seconds_to_hms(new_total_seconds)
        
        try:
            subprocess.run(["cmd", "/c", f"time {new_time_str}"], check=True)
            self.log(f"[!] THÀNH CÔNG: Master đã tự điều chỉnh về: [{new_time_str}]")
        except subprocess.CalledProcessError:
            self.log("[!] LỖI: Master không có quyền Admin để đổi giờ hệ thống.")

    def start_server_thread(self):
        self.btn_start.config(state=tk.DISABLED)
        self.btn_sync.config(state=tk.NORMAL)
        threading.Thread(target=self.run_server, daemon=True).start()

    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            self.log(f"[*] Server đang chạy tại cổng {PORT}. Đang chờ kết nối...")
            while True:
                conn, addr = self.server_socket.accept()
                clients[addr] = conn
                self.log(f"[+] Máy khách {addr} đã tham gia hệ thống.")
        except Exception as e:
            self.log(f"[!] Lỗi khởi động Server: {e}")

    def sync_clocks(self):
        if not clients:
            self.log("[!] Chưa có máy khách nào kết nối.")
            return
        threading.Thread(target=self.calculate_berkeley, daemon=True).start()

    def calculate_berkeley(self):
        self.log("\n" + "="*80)
        self.log(" TIẾN TRÌNH ĐỒNG BỘ THEO LOCAL SECONDS ")
        self.log("="*80)

        master_base_time = get_local_seconds()
        self.log(f"[*] Giờ gốc Master: [{seconds_to_hms(master_base_time)}]")

        differences = {'master': 0.0}
        client_data = {}

        self.log("\n--- BƯỚC 1 & 2: THU THẬP ĐỘ LỆCH ---")
        self.log(f"    - Master tự so với mình: D_master = {format_duration(0)}")

        for addr, conn in list(clients.items()):
            try:
                t0 = time.time()
                conn.sendall(b"GET_TIME") 
                
                resp = conn.recv(1024)
                if resp:
                    t1 = time.time()
                    slave_reported_time = float(resp.decode())
                    
                    rtt = t1 - t0
                    slave_estimated_time = slave_reported_time + (rtt / 2)
                    
                    diff = slave_estimated_time - master_base_time
                    differences[addr] = diff
                    client_data[addr] = diff
                    
                    self.log(f"    - Máy khách {addr}:")
                    self.log(f"      + Giờ báo: [{seconds_to_hms(slave_reported_time)}] | RTT: {format_duration(rtt)}")
                    self.log(f"      + Ước lượng thực tế: [{seconds_to_hms(slave_estimated_time)}]")
                    self.log(f"      => Độ lệch D = [{seconds_to_hms(slave_estimated_time)}] - [{seconds_to_hms(master_base_time)}] = {format_duration(diff)}")
            except Exception as e:
                self.log(f"[-] Mất kết nối với {addr}. Loại bỏ khỏi danh sách.")
                del clients[addr]

        num_mics = len(differences)
        if num_mics > 0:
            avg_diff = sum(differences.values()) / num_mics
            
            formula_str = " + ".join([f"({format_duration(d)})" for d in differences.values()])
            self.log("\n--- BƯỚC 3: TÍNH ĐỘ LỆCH TRUNG BÌNH (Avg_Diff) ---")
            self.log(f"    - Công thức: (\u03A3 Độ lệch) / Tổng số máy")
            self.log(f"    - [{formula_str}] / {num_mics}")
            self.log(f"    => Avg_Diff = {format_duration(avg_diff)}")

            self.log("\n--- BƯỚC 4: TÍNH OFFSET VÀ THỰC THI ĐIỀU CHỈNH ---")
            self.log("    - Công thức: Offset = Avg_Diff - D_của_máy")

            for addr, conn in clients.items():
                slave_diff = client_data[addr]
                final_offset = avg_diff - slave_diff
                try:
                    conn.sendall(f"SET_OFFSET:{final_offset}".encode())
                    self.log(f"    [>] Gửi Slave {addr}: {format_duration(avg_diff)} - ({format_duration(slave_diff)}) = {format_duration(final_offset)}")
                except:
                    pass

            master_diff = differences['master']
            master_final_offset = avg_diff - master_diff
            self.log(f"    [!] Master tự tính: {format_duration(avg_diff)} - ({format_duration(master_diff)}) = {format_duration(master_final_offset)}")
            self.update_windows_time(master_final_offset)

            self.log("\n" + "="*80)
            self.log(" ĐỒNG BỘ HOÀN TẤT ")
            self.log("="*80)

if __name__ == "__main__":
    root = tk.Tk()
    app = BerkeleyServerGUI(root)
    root.mainloop()