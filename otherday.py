import subprocess
import time
import cv2
import easyocr
import pyautogui
from PIL import Image
import numpy as np
import os
import pyperclip

# Cấu hình
LDPLAYER_PATH = r"D:\LDPlayer\LDPlayer9\ldconsole.exe"
CLONE_APP_PATH = r"C:\Users\Admin\OneDrive\Desktop\dualaid-11.2.6.0-1.apk"
PICCOMA_APP_PATH = r"C:\Users\Admin\OneDrive\Desktop\ピッコマ-人気漫画や話題のコミックが毎日読めるマンガアプリ_7.7.1_APKPure.apk"
ADB_PATH = "adb"
ADB_PORT = 5557
EMULATOR_NAME = "LDPlayer-1"
PACKAGE_NAME1 = "jp.kakao.piccoma"
PACKAGE_NAME2 = "com.excelliance.dualaid"
SCREENSHOT_PATH = "screenshot.png"
PLUS_ICON_TEMPLATE = "addButton.png"
X_ICON_TEMPLATE = "X_button.png"
PROFILE_ICON_TEMPLATE = "profile_icon.png"
pyautogui.PAUSE = 0.5


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


def install_apk_via_adb(apk_path):
    if not os.path.exists(apk_path):
        print(f"[x] APK không tồn tại: {apk_path}")
        return
    print(f"[+] Đang cài APK: {apk_path}")
    result = run_command(f"{ADB_PATH} install -r \"{apk_path}\"")
    if result.returncode == 0:
        print("[✓] Cài APK thành công!")
    else:
        print("[x] Cài APK thất bại!")


def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save(SCREENSHOT_PATH)
    return SCREENSHOT_PATH


def input_unicode_text(text):
    print(f"[+] Đang nhập văn bản: {text}")
    pyperclip.copy(text)
    time.sleep(1)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")


def detect_text_position(image_path, target_text):
    reader = easyocr.Reader(['en', 'ja'])
    image = np.array(Image.open(image_path))
    results = reader.readtext(image, detail=1)

    for (bbox, text, _) in results:
        if target_text in text:
            top_left, bottom_right = bbox[0], bbox[2]
            center_x = int((top_left[0] + bottom_right[0]) / 2)
            center_y = int((top_left[1] + bottom_right[1]) / 2)
            print(f"[✓] Đã tìm thấy '{target_text}' tại vị trí ({center_x}, {center_y})")
            return center_x, center_y
    print(f"[x] Không tìm thấy '{target_text}'")
    return None


def click_button_by_text(target_text):
    print(f"[+] Đang tìm và nhấn nút có chữ '{target_text}'...")
    image_path = capture_screenshot()
    position = detect_text_position(image_path, target_text)

    if position:
        x, y = position
        pyautogui.moveTo(x, y)
        pyautogui.click()
        print(f"[✓] Đã nhấn nút '{target_text}'")
    else:
        print(f"[x] Không thể nhấn nút '{target_text}' vì không tìm thấy chữ.")
    time.sleep(2)


def start_ldplayer():
    print("[+] Đang khởi động LDPlayer...")
    run_command(f'"{LDPLAYER_PATH}" launch --name "{EMULATOR_NAME}"')


def add_app():
    connect_adb_to_ldplayer(ADB_PORT)
    install_apk_via_adb(CLONE_APP_PATH)
    install_apk_via_adb(PICCOMA_APP_PATH)


def start_app_clone():
    print(f"[+] Start app clone...")
    run_command(f'"{LDPLAYER_PATH}" runapp --name "{EMULATOR_NAME}" --packagename {PACKAGE_NAME2}')
    time.sleep(5)
    click_button_by_text("同意并继续")
    time.sleep(5)
    click_button_by_text("立即升级")
    time.sleep(5)
    click_button_by_text("INSTALL")
    time.sleep(8)
    click_button_by_text("OPEN")
    time.sleep(8)
    click_plus_icon()
    time.sleep(5)
    click_button_by_text("ピッコマ")
    time.sleep(5)
    click_button_by_text("添加")
    time.sleep(5)
    click_button_by_text("INSTALL")
    time.sleep(8)


def detect_icon(screenshot_path, template_path):
    screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    threshold = 0.8
    if max_val >= threshold:
        top_left = max_loc
        h, w = template_gray.shape
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        print(f"[✓] Đã tìm thấy biểu tượng tại vị trí ({center_x}, {center_y})")
        return center_x, center_y
    else:
        return None


def click_plus_icon():
    print("[+] Đang tìm và nhấn vào biểu tượng '+'...")
    screenshot_path = capture_screenshot()
    position = detect_icon(screenshot_path, PLUS_ICON_TEMPLATE)

    if position:
        x, y = position
        pyautogui.moveTo(x, y)
        pyautogui.click()
        print("[✓] Đã nhấn vào biểu tượng '+'")
    else:
        print("[x] Không thể nhấn vào biểu tượng '+' vì không tìm thấy.")


def click_x_icon():
    print("[+] Đang tìm và nhấn vào biểu tượng 'x'...")
    screenshot_path = capture_screenshot()
    position = detect_icon(screenshot_path, X_ICON_TEMPLATE)

    if position:
        x, y = position
        pyautogui.moveTo(x, y)
        pyautogui.click()
        print("[✓] Đã nhấn vào biểu tượng 'x'")
        return True
    else:
        print("[x] Không thể nhấn vào biểu tượng 'x' vì không tìm thấy.")
        return False

def click_profile_icon():
    print("[+] Đang tìm và nhấn vào biểu tượng 'profile'...")
    screenshot_path = capture_screenshot()
    position = detect_icon(screenshot_path, PROFILE_ICON_TEMPLATE)

    if position:
        x, y = position
        pyautogui.moveTo(x, y)
        pyautogui.click()
        print("[✓] Đã nhấn vào biểu tượng 'profile'")
        return True
    else:
        print("[x] Không thể nhấn vào biểu tượng 'profile' vì không tìm thấy.")
        return False

def scroll_y(distance=300, duration=300):
    print(f"[+] Thực hiện scroll theo chiều Y, khoảng cách: {distance}px")
    width, height = pyautogui.size()
    x = width // 2
    y_start = height // 2 + distance // 2
    y_end = height // 2 - distance // 2
    pyautogui.moveTo(x, y_start)
    pyautogui.dragTo(x, y_end, duration / 1000.0, button='left')
    time.sleep(1)


def start_piccoma():
    print(f"[+] Start app đọc truyện {PACKAGE_NAME1}...")
    run_command(f'"{LDPLAYER_PATH}" runapp --name "{EMULATOR_NAME}" --packagename {PACKAGE_NAME1}')


def main():
    start_ldplayer()
    time.sleep(30)

    start_piccoma() 
    time.sleep(10)

    # Lặp nhấn X nếu còn xuất hiện
    while True:
        if not click_x_icon():
            break
        time.sleep(3)

    click_profile_icon()
    time.sleep(5)

    scroll_y(500)  # Scroll xuống 500 pixel
    time.sleep(5)

    click_button_by_text("マンガ読んで") # nhấn vào ví
    time.sleep(10)
    click_button_by_text("GO")
    time.sleep(10)
if __name__ == "__main__":
    main()
