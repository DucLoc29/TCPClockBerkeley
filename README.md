# Berkeley Time Synchronization Tool 

Ứng dụng đồng bộ thời gian vật lý trong hệ thống phân tán sử dụng **Thuật toán Berkeley**. Chương trình hỗ trợ giao tiếp qua Socket (TCP) và tương tác trực tiếp với đồng hồ hệ thống Windows 11.

---

## Thành viên thực hiện 
* **Nguyễn Đức Lộc** - Trưởng nhóm
* **Nguyễn Hữu Huynh**
* **Hứa Trung Kiên**
* **Đinh Văn Hưng**
* **Đinh Hoàng Trọng Khôi**
* **Nguyễn Văn Hiệu** 

## Giới thiệu đề tài
Dự án tập trung vào việc hiện thực hóa thuật toán Berkeley để đồng bộ hóa đồng hồ của các máy tính trong mạng nội bộ. Hệ thống không tin tưởng tuyệt đối vào bất kỳ máy tính nào (kể cả Master) mà dựa trên sự đồng thuận của tập thể để đưa ra mốc thời gian trung bình chính xác nhất cho toàn mạng.

## Tính năng nổi bật
* **Giao diện đồ họa (GUI):** Xây dựng bằng `Tkinter` trực quan, hiển thị nhật ký tính toán chi tiết.
* **Đồng bộ thời gian thực:** Can thiệp trực tiếp vào lệnh `time` của Windows 11 để cập nhật giờ vật lý.
* **Xử lý trễ mạng (RTT):** Áp dụng công thức $T_{real} = T_{reported} + \frac{RTT}{2}$ để đảm bảo độ chính xác cao.
* **Triệt tiêu lỗi múi giờ:** Sử dụng phương pháp tính toán theo giây địa phương (`Local Seconds`) để tránh sai lệch múi giờ (Timezone) giữa các máy ảo.
* **Nhật ký toán học:** Log hiển thị chi tiết các bước cộng/trừ/chia trung bình giúp dễ dàng kiểm chứng thuật toán.

## Yêu cầu hệ thống
* **Ngôn ngữ:** Python 3.x.
* **Quyền hạn:** Chạy ứng dụng với quyền **Administrator** (để thực thi lệnh đổi giờ hệ thống).
* **Môi trường:** Hoạt động tốt trên Windows 10/11 (Máy thật hoặc máy ảo VMware/VirtualBox).

## Hướng dẫn cài đặt và sử dụng

### 1. Khởi động Máy chủ (Master)
1. Mở Terminal (CMD/PowerShell) bằng quyền **Run as Administrator**.
2. Chạy lệnh: `python server_gui.py`.
3. Nhấn nút **"Bắt đầu Server"**.

### 2. Khởi động Máy khách (Slaves)
1. Mở Terminal bằng quyền **Run as Administrator** trên các máy cần đồng bộ.
2. Chạy lệnh: `python client_gui.py`.
3. Nhập địa chỉ **IP của Master** vào ô nhập liệu và nhấn **"Kết nối"**.

### 3. Quy trình đồng bộ
* Tại màn hình Master, nhấn nút **"Đồng bộ ngay"**.
* Hệ thống sẽ tự động thực hiện 4 bước:
    1. Thu thập thời gian từ các Slave.
    2. Tính toán độ lệch ($D_i$) so với Master.
    3. Tính độ lệch trung bình toàn hệ thống ($Avg\_Diff$).
    4. Gửi lệnh điều chỉnh (Offset) cho Slaves và Master tự cập nhật chính mình.

## Logic tính toán 
Hệ thống hiển thị log chi tiết các phép tính:
- **Độ lệch (Difference):** $D = Slave\_Time - Master\_Time$
- **Trung bình:** $Avg\_Diff = \frac{\sum D_i}{n}$
- **Bù trừ (Offset):** $Offset = Avg\_Diff - D_{của\_máy}$

---
