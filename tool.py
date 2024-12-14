import os
import requests
import json
import time
from colorama import init, Fore

# Khởi tạo colorama
init(autoreset=True)

# Khai báo cấu hình và global variables
API_KEY = None
COOKIES = {"facebook": "", "instagram": "", "tiktok": ""}
USER_NAME = None
BASE_URL = "https://traodoisub.com/api/"
TASK_TYPES = {
    "facebook": ["like", "follow", "share", "comment"],
    "instagram": ["follow", "like", "comment"],
    "tiktok": ["follow", "like"]
}

# Danh sách cấu hình đã lưu
configurations = []

# Hàm lấy tên người dùng từ API
def get_username(api_key):
    url = f"{BASE_URL}?access_token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data.get("name", "Không tên")
        except requests.exceptions.JSONDecodeError:
            print(Fore.RED + "Lỗi khi nhận tên người dùng.")
            return None
    else:
        print(Fore.RED + f"Lỗi API: {response.status_code}")
        return None

# Hàm kiểm tra cấu hình (Access Token và Cookies)
def check_config():
    global API_KEY, COOKIES
    if not API_KEY:
        print(Fore.RED + "⚠️ Bạn chưa nhập API Key. Vui lòng nhập lại.")
        return False
    for platform in COOKIES:
        if not COOKIES[platform]:
            print(Fore.RED + f"⚠️ Bạn chưa nhập cookie cho {platform}. Vui lòng nhập lại.")
            return False
    return True

# Hàm lấy danh sách nhiệm vụ
def get_tasks(task_type):
    url = f"{BASE_URL}?fields={task_type}&access_token={API_KEY}"
    print(Fore.YELLOW + f"🔄 Đang lấy nhiệm vụ loại {task_type}...")

    try:
        response = requests.get(url, cookies=COOKIES)
        if response.status_code == 200:
            try:
                tasks = response.json()
                if isinstance(tasks, list):  # Kiểm tra nếu dữ liệu là danh sách
                    return tasks
                else:
                    print(Fore.RED + f"Không có nhiệm vụ {task_type} nào!")
                    return []
            except requests.exceptions.JSONDecodeError:
                print(Fore.RED + "Lỗi: Phản hồi không phải JSON. Nội dung nhận được là:")
                print(Fore.YELLOW + response.text)
                return []
        else:
            print(Fore.RED + f"Lỗi khi lấy nhiệm vụ {task_type}: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print(Fore.RED + f"Lỗi kết nối khi lấy nhiệm vụ: {str(e)}")
        return []

# Hàm thực hiện nhiệm vụ
def perform_task(task_id, task_type):
    url = f"{BASE_URL}?fields={task_type}_success&id={task_id}&access_token={API_KEY}"
    try:
        response = requests.get(url, cookies=COOKIES)
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("success"):
                    print(Fore.GREEN + f"✅ Hoàn thành nhiệm vụ {task_id} - {task_type}!")
                    print(Fore.CYAN + f"Điểm đã kiếm được: {result.get('points', 0)}")
                    return True, result.get("points", 0)
                else:
                    print(Fore.RED + f"❌ Lỗi nhiệm vụ {task_id}: {result.get('error', 'Không rõ lỗi')}")
                    return False, 0
            except requests.exceptions.JSONDecodeError:
                print(Fore.RED + "Lỗi: Phản hồi không phải JSON. Nội dung nhận được là:")
                print(Fore.YELLOW + response.text)
                return False, 0
        else:
            print(Fore.RED + f"❌ Lỗi khi thực hiện nhiệm vụ {task_id}: {response.status_code}, {response.text}")
            return False, 0
    except Exception as e:
        print(Fore.RED + f"Lỗi kết nối khi thực hiện nhiệm vụ: {str(e)}")
        return False, 0

# Hàm lấy cookie từ người dùng
def get_cookie(platform):
    return input(Fore.MAGENTA + f"🍪 Nhập Cookie {platform.capitalize()}: ")

# Hàm kiểm tra cookie hợp lệ cho các nền tảng
def check_cookie(platform, cookie):
    if platform == "facebook":
        url = "https://www.facebook.com/me"
    elif platform == "instagram":
        url = "https://www.instagram.com/accounts/edit/"
    elif platform == "tiktok":
        url = "https://www.tiktok.com/@username"
    else:
        print(Fore.RED + "Platform không hợp lệ.")
        return False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    cookies = {
        "cookie": cookie
    }

    response = requests.get(url, headers=headers, cookies=cookies)

    if response.status_code == 200:
        print(Fore.GREEN + f"✅ Cookie {platform.capitalize()} còn sống.")
        return True
    else:
        print(Fore.RED + f"❌ Cookie {platform.capitalize()} đã chết hoặc không hợp lệ.")
        return False

# Hàm liệt kê cấu hình và yêu cầu nhập lại nếu không có
def list_configurations():
    if not configurations:
        print(Fore.RED + "⚠️ Không có cấu hình nào đã lưu!")
        return None
    print(Fore.YELLOW + "--- Danh sách cấu hình đã lưu ---")
    for idx, config in enumerate(configurations, 1):
        print(Fore.CYAN + f"{idx}. {config['platform']} - Cookie: {config['cookie'][:20]}...")  # Hiển thị phần đầu của cookie
    try:
        choice = int(input(Fore.YELLOW + "Chọn cấu hình (nhập số) để sử dụng, hoặc 0 để quay lại: ").strip())
        if choice == 0:
            return None
        if 1 <= choice <= len(configurations):
            return configurations[choice - 1]
        else:
            print(Fore.RED + "⚠️ Lựa chọn không hợp lệ. Vui lòng thử lại.")
            return None
    except ValueError:
        print(Fore.RED + "⚠️ Lỗi nhập liệu. Vui lòng thử lại.")
        return None

# Hàm lưu cấu hình vào danh sách
def save_configuration(platform, cookie):
    configurations.append({"platform": platform, "cookie": cookie})

# Hàm xử lý nhiệm vụ của nền tảng
def process_platform_tasks(platform, task_count, delay):
    print(Fore.YELLOW + f"🔄 Đang xử lý nhiệm vụ cho nền tảng: {platform.capitalize()}")
    total_tasks = 0
    total_points = 0
    for task_type in TASK_TYPES[platform]:
        print(Fore.YELLOW + f"📌 Loại nhiệm vụ: {task_type}")
        tasks = get_tasks(task_type)
        if tasks:
            for task in tasks[:task_count]:  # Lấy số nhiệm vụ theo yêu cầu
                task_id = task.get("id")
                if task_id:
                    success, points = perform_task(task_id, task_type)
                    if success:
                        total_tasks += 1
                        total_points += points
                        time.sleep(delay)  # Tránh spam quá nhanh
            print(Fore.GREEN + f"✔️ Hoàn thành tất cả nhiệm vụ loại {task_type}!")
        else:
            print(Fore.RED + f"Không có nhiệm vụ nào cho loại {task_type}.")
    print(Fore.GREEN + f"✔️ Xong nhiệm vụ cho nền tảng: {platform.capitalize()}")
    return total_tasks, total_points

# Hàm đăng nhập và lấy thông tin
def login():
    global API_KEY, USER_NAME
    while True:
        API_KEY = input(Fore.MAGENTA + "🔑 Nhập API Key từ traodoisub.com: ").strip()
        USER_NAME = get_username(API_KEY)
        if USER_NAME:
            print(Fore.GREEN + f"Đăng nhập thành công! Chào {USER_NAME}")
            break
        else:
            print(Fore.RED + "Lỗi: API Key không hợp lệ, vui lòng thử lại!")

# Hàm hiển thị menu và lựa chọn công cụ
def main_menu():
    global API_KEY
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Xóa hết terminal
        print(Fore.CYAN + "--- TOOL TỰ ĐỘNG TRAODOISUB ---")
        print(Fore.GREEN + "1.1 - Facebook")
        print(Fore.GREEN + "1.2 - Instagram")
        print(Fore.GREEN + "1.3 - TikTok")
        print(Fore.RED + "0 - Thoát")
        
        try:
            choice = input(Fore.YELLOW + "Chọn công cụ bạn muốn sử dụng: ").strip()
            
            if choice == "1.1":
                platform = "facebook"
                cookie = get_cookie(platform)
                if check_cookie(platform, cookie):
                    save_configuration(platform, cookie)
            elif choice == "1.2":
                platform = "instagram"
                cookie = get_cookie(platform)
                if check_cookie(platform, cookie):
                    save_configuration(platform, cookie)
            elif choice == "1.3":
                platform = "tiktok"
                cookie = get_cookie(platform)
                if check_cookie(platform, cookie):
                    save_configuration(platform, cookie)
            elif choice == "0":
                break
            else:
                print(Fore.RED + "⚠️ Lựa chọn không hợp lệ! Thử lại.")
        except Exception as e:
            print(Fore.RED + f"Lỗi: {str(e)}")

# Hàm chính
if __name__ == "__main__":
    login()
    main_menu()
