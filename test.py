import socket

def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # Установить тайм-аут в 5 секунд
    try:
        sock.connect((ip, port))
        print(f"Соединение с {ip}:{port} установлено успешно")
        return True
    except socket.error as e:
        print(f"Не удалось подключиться к {ip}:{port} - {e}")
        return False
    finally:
        sock.close()

# Проверьте соединение с вашим устройством
ip_address = '192.168.1.126'
port = 502
check_port(ip_address, port)
