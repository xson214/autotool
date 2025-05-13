import subprocess
import time
import pyautogui
import os

# ========== CẤU HÌNH ==========
LDPLAYER_PATH = r"D:\LDPlayer\LDPlayer9\ldconsole.exe"
CLONE_APP_PATH = r"C:\Users\Admin\OneDrive\Desktop\dualaid-11.2.6.0-1.apk"
PICCOMA_APP_PATH = r"C:\Users\Admin\OneDrive\Desktop\ピッコマ-人気漫画や話題のコミックが毎日読めるマンガアプリ_7.7.1_APKPure.apk"
ADB_PATH = "adb"
PACKAGE_NAME1 = "jp.kakao.piccoma"
PACKAGE_NAME2 = "com.excelliance.dualaid"
pyautogui.PAUSE = 0.5

# ========== NHẬP SỐ LƯỢNG LDPLAYER ==========
try:
    n = int(input("Nhập số lượng LDPlayer cần xử lý: "))
    LDPLAYER_LIST = [f"LDPlayer-{i}" for i in range(n)]
except ValueError:
    print("[x] Vui lòng nhập số nguyên hợp lệ.")
    exit(1)

# ========== HÀM PHỤ ==========
def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print("Error:", result.stderr.strip())
        return result
    except Exception as e:
        print("Exception:", e)
        return None

def connect_adb_to_ldplayer(port):
    print(f"[+] Kết nối ADB đến LDPlayer trên port {port}...")
    result = run_command(f"{ADB_PATH} connect 127.0.0.1:{port}")
    time.sleep(2)
    return result

def is_package_installed(package_name):
    print(f"[?] Kiểm tra gói đã cài: {package_name}")
    result = run_command(f"{ADB_PATH} shell pm list packages")
    if result and package_name in result.stdout:
        print(f"[✓] Đã cài: {package_name}")
        return True
    else:
        print(f"[x] Chưa cài: {package_name}")
        return False

def install_apk_via_adb(apk_path, package_name):
    if is_package_installed(package_name):
        print(f"[i] Bỏ qua cài đặt vì đã có: {package_name}")
        return

    if not os.path.exists(apk_path):
        print(f"[x] APK không tồn tại: {apk_path}")
        return

    print(f"[+] Đang cài APK: {apk_path}")
    result = run_command(f"{ADB_PATH} install -r \"{apk_path}\"")
    if result and result.returncode == 0:
        print("[✓] Cài APK thành công!")
    else:
        print("[x] Cài APK thất bại!")

def start_ldplayer(name):
    print(f"[+] Đang khởi động LDPlayer: {name}")
    run_command(f'"{LDPLAYER_PATH}" launch --name {name}')
    time.sleep(5)

def close_ldplayer(name):
    print(f"[+] Đóng LDPlayer: {name}")
    run_command(f'"{LDPLAYER_PATH}" quit --name {name}')

def start_piccoma():
    print(f"[+] Khởi chạy app Piccoma...")
    run_command(f'"{LDPLAYER_PATH}" runapp --name "{current_ldplayer}" --packagename {PACKAGE_NAME1}')
    time.sleep(3)

def send_ctrl_8_and_click():
    print("[+] Gửi Ctrl + 8 và nhấn chuột vào vị trí chỉ định.")
    pyautogui.hotkey('ctrl', '8')
    time.sleep(1)
    pyautogui.moveTo(1230, 463)  # Vị trí này bạn có thể điều chỉnh nếu cần
    pyautogui.click()

# ========== CHƯƠNG TRÌNH CHÍNH ==========
if __name__ == "__main__":
    for index, current_ldplayer in enumerate(LDPLAYER_LIST):
        current_port = 5555 + index + 1

        print(f"\n=== ▶ ĐANG XỬ LÝ {current_ldplayer} (port {current_port}) ===")
        start_ldplayer(current_ldplayer)
        time.sleep(20)

        connect_adb_to_ldplayer(current_port)
        time.sleep(2)

        install_apk_via_adb(CLONE_APP_PATH, PACKAGE_NAME2)
        time.sleep(10)
        install_apk_via_adb(PICCOMA_APP_PATH, PACKAGE_NAME1)
        time.sleep(10)

        print("[✓] Hoàn tất khởi động và kiểm tra app.")
        start_piccoma()
        time.sleep(8)

        send_ctrl_8_and_click()
        time.sleep(90)

        close_ldplayer(current_ldplayer)
        time.sleep(5)

    print("\n[✓] Đã xử lý xong tất cả LDPlayer.")
