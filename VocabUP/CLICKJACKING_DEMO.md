# Clickjacking demo trên VocabUP — không thêm chức năng vào ứng dụng

## Phạm vi

Trang nhận quà là website riêng, chạy trên cổng `4174`. Nó nhúng ứng dụng VocabUP thật ở cổng `5173` bằng hai iframe: một iframe xem trước để quan sát; một iframe phủ trong suốt để nhận cú nhấp. Trang mồi căn nút quà vào nút đăng xuất sẵn có trong thanh hồ sơ của VocabUP. VocabUP không được thêm nút tạo thẻ, API guest hoặc hành động demo nào.

Thao tác đăng xuất là có chủ ý để tạo tác động thấy được mà không sửa chức năng ứng dụng; dùng tài khoản thử nghiệm. Người dùng bấm nút quà nhưng thực tế đăng xuất khỏi VocabUP. Đây là clickjacking (thao tác ngoài ý muốn qua iframe), không phải đọc mật khẩu hay chuyển hướng.

## Chạy trên một máy

### 1. Tái hiện trạng thái cho phép nhúng

Trong `frontend/vite.config.ts`, tìm `server.headers`. Để tái hiện bản thiếu CSP, tạm comment dòng CSP:

```ts
// 'Content-Security-Policy': "frame-ancestors 'none'",
```

Lưu file. Mở PowerShell tại `D:\CSATTT\VocabUP` và chạy:

```powershell
npm.cmd run dev
```

Đăng nhập VocabUP tại `http://localhost:5173/login` bằng tài khoản thử nghiệm. Giữ tab đó mở.

### 2. Chạy website nhận quà riêng

Trong PowerShell thứ hai:

```powershell
cd D:\CSATTT\VocabUP
npm.cmd run demo:clickjacking-attacker
```

Mở URL được in ra, thường là `http://localhost:4174`. Dùng cửa sổ desktop rộng hơn 800px để sidebar VocabUP hiển thị.

1. Bấm **Xem trang VocabUP được nhúng** để thấy VocabUP trong iframe xem trước.
2. Đóng khung xem trước.
3. Bấm **NHẬN QUÀ NGAY**. Nút mồi nằm ngay trên nút hồ sơ/đăng xuất thật của VocabUP. Nội dung trang mồi không chuyển hướng; iframe đăng xuất phiên.
4. Chuyển sang tab VocabUP và tải lại. Bạn sẽ thấy phiên đã đăng xuất.

Nút xem trước và khung tấn công đều nhúng VocabUP; trang mồi ở cổng `4174` còn VocabUP ở `5173`, nên chúng là hai origin khác nhau. Để xác nhận response dễ bị nhúng, DevTools → Network → tải lại URL VocabUP trong iframe → chọn document và xem `Content-Security-Policy`. Khi dòng CSP được comment, Vite không gửi `frame-ancestors 'none'`.

### 3. Bật lại CSP để chứng minh cách sửa

Dừng Vite bằng `Ctrl+C`. Trong `frontend/vite.config.ts`, bỏ comment dòng CSP để bật bảo vệ lại:

```ts
'Content-Security-Policy': "frame-ancestors 'none'",
```

Khởi động lại `npm.cmd run dev`, rồi tải lại trang mồi. Nút xem trước mở ra vùng trống; Console cho biết trình duyệt chặn iframe. Bấm nút quà cũng không đăng xuất VocabUP. Mở trực tiếp `http://localhost:5173` vẫn hoạt động bình thường.

Không xóa file hay sửa dữ liệu VocabUP để lặp lại lượt này. Sau lượt dễ bị nhúng, đăng nhập lại trước khi demo lại.

## Demo miễn phí với hai máy cùng Wi-Fi/LAN

Ngrok Free không cho custom hostname. Có thể dùng chung IP LAN của máy B cho cả hai dịch vụ và tách bằng cổng: VocabUP ở `5173`, trang mồi ở `4174`. Khác cổng tạo origin khác nhau; cùng IP và scheme giữ ngữ cảnh cùng site cho cookie `SameSite=Strict`.

### Máy B — chạy cả VocabUP và trang mồi

1. Trên máy B chạy `ipconfig`, lấy IPv4 của Wi-Fi, ví dụ `192.168.1.20`. Hai máy cần ở cùng mạng riêng. Dùng địa chỉ IP thật của máy B, không dùng `localhost`.
2. Để tái hiện trạng thái cho phép nhúng, trong `frontend/vite.config.ts` comment dòng `'Content-Security-Policy': "frame-ancestors 'none'"`.
3. Terminal VocabUP trên B:

   ```powershell
   cd D:\CSATTT\VocabUP
   $env:CLICKJACKING_LAN_IP = '192.168.1.20'
   $env:FRONTEND_URL = 'http://192.168.1.20:5173'
   npm.cmd run dev
   ```

   Thay `192.168.1.20` bằng IP máy B. Vite chỉ bind vào IP đó; cấu hình tự thêm IP vào `allowedHosts`. Backend nhận origin frontend từ `FRONTEND_URL`.

4. Đăng nhập tài khoản demo trên máy A tại `http://192.168.1.20:5173/login`.
5. Terminal thứ hai trên máy B, chạy trang mồi cùng target IP:

   ```powershell
   cd D:\CSATTT\VocabUP
   $env:CLICKJACKING_LAN_IP = '192.168.1.20'
   $env:CLICKJACKING_TARGET_URL = 'http://192.168.1.20:5173/dashboard'
   $env:CLICKJACKING_ATTACKER_HOST = '192.168.1.20'
   npm.cmd run demo:clickjacking-attacker
   ```

6. Máy A mở `http://192.168.1.20:4174`, xem trước VocabUP, đóng xem trước rồi bấm nhận quà. Nếu Windows Firewall hỏi, chỉ cho phép Node trên mạng **Private**.

Để thử bản đã sửa, dừng Vite trên B, bỏ comment dòng CSP, khởi động lại với cùng hai biến `CLICKJACKING_LAN_IP` và `FRONTEND_URL`. Tải lại trang mồi trên A; iframe bị chặn và nút quà không đăng xuất.

Nếu hai máy không cùng Wi-Fi, cần một VPN riêng để máy A truy cập IP riêng của máy B; không dùng IP public trực tiếp. Nếu không có LAN/VPN, ngrok Free không thể cung cấp cặp custom hostname cùng site cần cho thao tác đăng xuất xác thực.

## Code cần chỉ cho giảng viên

- `frontend/lab/clickjacking-attacker.html`: website mồi độc lập. `preview-frame` là iframe xem trước; `target-frame` phủ trong suốt; `.claim` đặt nút quà tại tọa độ của nút hồ sơ VocabUP.
- `frontend/lab/server.mjs`: server trang mồi, điền URL VocabUP vào hai placeholder `__VOCABUP_URL__`.
- `frontend/vite.config.ts`: dòng `Content-Security-Policy` trong `server.headers` là chỗ bật/tắt CSP dev. Comment dòng đó để tái hiện; bỏ comment để chặn iframe.
- `frontend/vite.config.ts`: `CLICKJACKING_LAN_IP` chỉ cấu hình bind/allowed host cho demo mạng nội bộ; không thêm chức năng vào ứng dụng.
- `frontend/lab/server.mjs`: khi có `CLICKJACKING_LAN_IP`, server trang mồi bind vào đúng IP LAN và chỉ cho target HTTP trùng IP đó.
- `backend/src/index.ts`: Helmet vẫn đặt `frameAncestors: ["'none'"]` ở backend. Không cần sửa file backend cho demo này.

## Trình bày kết quả

> Em không thêm chức năng vào VocabUP. Em chỉ thay đổi CSP để tái hiện và khắc phục khả năng nhúng. Trang nhận quà là website riêng, nhúng trang VocabUP thật bằng iframe. Khi chưa có `frame-ancestors`, cú nhấp vào nút quà rơi vào nút đăng xuất sẵn có trong VocabUP. Sau khi bật `frame-ancestors 'none'`, trình duyệt chặn iframe và thao tác đó không còn xảy ra.

Đây là kiểm thử có chủ đích trên ứng dụng local do nhóm sở hữu. Clickjacking khiến người dùng thực hiện thao tác ngoài ý muốn; bản thân nó không cho trang mồi đọc nội dung iframe khác origin hay lấy mật khẩu. Dùng tài khoản thử nghiệm và đăng nhập lại sau khi kiểm thử.
