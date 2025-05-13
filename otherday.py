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

# Vùng chụp ảnh LDPlayer (thay đổi nếu cần)
SCREENSHOT_REGION = (660, 0, 630, 1078)  # (x, y, width, height)
SCREENSHOT_OFFSET_X = SCREENSHOT_REGION[0]
SCREENSHOT_OFFSET_Y = SCREENSHOT_REGION[1]

# Template ảnh biểu tượng
PLUS_ICON_TEMPLATE = "addButton.png"
X_ICON_TEMPLATE = "X_button.png"
PROFILE_ICON_TEMPLATE = "profile_icon.png"
GO_button_TEMPLATE ="GO_button.png"
FREE_ICON = "Free_icon.png"
SCROLL_ICON = "SCROLL_ICON.png"
GET_ICON = "GET.png"
pyautogui.PAUSE = 0.5


def run_command(command):
    return subprocess.run(command, capture_output=True, text=True, shell=True)


def connect_adb_to_ldplayer(port):
    print(f"[+] Kết nối ADB đến LDPlayer trên port {port}...")
    return run_command(f"{ADB_PATH} connect 127.0.0.1:{port}")

def capture_screenshot():
    screenshot = pyautogui.screenshot(region=SCREENSHOT_REGION)
    screenshot.save(SCREENSHOT_PATH)
    return SCREENSHOT_PATH


def input_unicode_text(text):
    print(f"[+] Nhập văn bản: {text}")
    pyperclip.copy(text)
    time.sleep(1)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


def detect_text_position(image_path, target_text, lang_list=['en', 'ja']):
    reader = easyocr.Reader(lang_list)
    image = np.array(Image.open(image_path))
    results = reader.readtext(image, detail=1)

    for (bbox, text, _) in results:
        print(f" - {text}")
        if target_text.lower() in text.lower():
            top_left, bottom_right = bbox[0], bbox[2]
            center_x = int((top_left[0] + bottom_right[0]) / 2) + SCREENSHOT_OFFSET_X
            center_y = int((top_left[1] + bottom_right[1]) / 2) + SCREENSHOT_OFFSET_Y
            print(f"[✓] Đã tìm thấy '{target_text}' tại ({center_x}, {center_y})")
            return center_x, center_y
    print(f"[x] Không tìm thấy '{target_text}'")
    return None


def detect_icon(screenshot_path, template_path):
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= 0.8:
        top_left = max_loc
        h, w = template_gray.shape
        center_x = top_left[0] + w // 2 + SCREENSHOT_OFFSET_X
        center_y = top_left[1] + h // 2 + SCREENSHOT_OFFSET_Y
        print(f"[✓] Tìm thấy icon tại ({center_x}, {center_y})")
        return center_x, center_y
    return None


def click_position(position, label):
    if position:
        pyautogui.moveTo(*position)
        pyautogui.click()
        print(f"[✓] Đã nhấn {label}")
    else:
        print(f"[x] Không tìm thấy {label}")


def click_button_by_text(text):
    print(f"[+] Đang tìm nút '{text}'...")
    image_path = capture_screenshot()
    position = detect_text_position(image_path, text)
    click_position(position, f"nút '{text}'")


def click_icon_by_template(template_path, label):
    print(f"[+] Tìm biểu tượng '{label}'...")
    image_path = capture_screenshot()
    position = detect_icon(image_path, template_path)
    click_position(position, f"biểu tượng '{label}'")
    return position is not None


def scroll_y(distance=300, duration=300):
    width, height = pyautogui.size()
    x = width // 2
    y_start = height // 2 + distance // 2
    y_end = height // 2 - distance // 2
    pyautogui.moveTo(x, y_start)
    pyautogui.dragTo(x, y_end, duration / 1000.0, button='left')
    time.sleep(1)

def scroll_x(distance=300, duration=300):
    width, height = pyautogui.size()
    y = height // 2
    x_start = width // 2 + distance // 2
    x_end = width // 2 - distance // 2

    pyautogui.moveTo(x_start, y)
    pyautogui.dragTo(x_end, y, duration / 1000.0, button='left')
    time.sleep(1)

def click_and_hold_icon(template_path, offset_y=300, duration=0.5):
    print(f"[+] Đang tìm biểu tượng từ template: {template_path}")
    screenshot_path = capture_screenshot()
    position = detect_icon(screenshot_path, template_path)

    if position:
        start_x, start_y = position
        end_x = start_x
        end_y = start_y + offset_y  # Kéo từ trên xuống dưới

        print(f"[✓] Kéo giữ từ ({start_x}, {start_y}) xuống ({end_x}, {end_y})")

        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        time.sleep(0.2)  # Giữ chuột một chút
        pyautogui.moveTo(end_x, end_y, duration=duration)
        pyautogui.mouseUp()

        print("[✓] Đã thực hiện kéo thả theo chiều dọc thành công.")
        return True
    else:
        print("[x] Không tìm thấy biểu tượng để kéo.")
        return False

def start_ldplayer():
    print("[+] Khởi động LDPlayer...")
    run_command(f'"{LDPLAYER_PATH}" launch --name "{EMULATOR_NAME}"')


def start_app(package_name, label):
    print(f"[+] Mở ứng dụng {label}...")
    run_command(f'"{LDPLAYER_PATH}" runapp --name "{EMULATOR_NAME}" --packagename {package_name}')


def main():
    start_ldplayer()
    time.sleep(30)

    start_app(PACKAGE_NAME1, "Piccoma")
    time.sleep(10)

    while click_icon_by_template(X_ICON_TEMPLATE, 'X'):
        time.sleep(2)

    click_icon_by_template(PROFILE_ICON_TEMPLATE, "profile")
    time.sleep(3)

    scroll_y(500)
    time.sleep(2)

    click_button_by_text("マンガ読んで")
    time.sleep(5)

    click_icon_by_template(GO_button_TEMPLATE,"GO")
    time.sleep(5)

    while click_icon_by_template(X_ICON_TEMPLATE, 'X'):
        time.sleep(2) 
    
    print("[+] Đang tìm biểu tượng FREE_ICON bằng cách scroll ngang...")
    while True:
        capture_screenshot()
        position = detect_icon(SCREENSHOT_PATH, FREE_ICON)
        if position:
            x, y = position
            pyautogui.moveTo(x, y)
            pyautogui.click()
            print("[✓] Đã nhấn vào biểu tượng FREE_ICON")
            break
        else:
            scroll_x(400)

    scroll_y(500)

    click_button_by_text("全")

    click_icon_by_template(SCREENSHOT_PATH,FREE_ICON)

    pyautogui.click()
    time.sleep(2)

    click_and_hold_icon(SCROLL_ICON, offset_y= 900)
    
    while click_icon_by_template(X_ICON_TEMPLATE, 'X'):
        time.sleep(2)


    click_button_by_text("イベントページで受け取る")
    time.sleep(5)

    click_icon_by_template(SCREENSHOT_PATH,GET_ICON)

if __name__ == "__main__":
    main()
