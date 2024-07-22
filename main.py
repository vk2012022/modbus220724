from pymodbus.client import ModbusTcpClient
import struct

# Настройки подключения
ip_address = '192.168.1.100'  # IP-адрес устройства
port = 502                    # Порт по умолчанию для Modbus

# Функция для создания клиента и подключения
def create_modbus_client(ip, port):
    client = ModbusTcpClient(ip, port)
    if not client.connect():
        print(f"Не удалось подключиться к устройству по адресу {ip}:{port}")
        return None
    return client

# Функция для чтения float32 регистров
def read_float32_register(client, address, unit=1):
    try:
        response = client.read_holding_registers(address, 2, unit=unit)
        if response.isError():
            print(f"Ошибка чтения регистров: {response}")
        else:
            # Преобразование данных в float32
            registers = response.registers
            float_value = struct.unpack('>f', struct.pack('>HH', registers[0], registers[1]))[0]
            return float_value
    except Exception as e:
        print(f"Ошибка при чтении регистра: {e}")

# Функция для записи float32 в регистры
def write_float32_register(client, address, value, unit=1):
    try:
        # Преобразование float32 в два 16-битных регистра
        packed_value = struct.pack('>f', value)
        registers = struct.unpack('>HH', packed_value)
        response = client.write_registers(address, registers, unit=unit)
        if response.isError():
            print(f"Ошибка записи регистра: {response}")
        else:
            print(f"Регистры записаны успешно: {value}")
    except Exception as e:
        print(f"Ошибка при записи регистра: {e}")

# Функция для чтения флагов (дискретных входов)
def read_coil(client, address, unit=1):
    try:
        response = client.read_coils(address, 1, unit=unit)
        if response.isError():
            print(f"Ошибка чтения флагов: {response}")
        else:
            return response.bits[0]
    except Exception as e:
        print(f"Ошибка при чтении флага: {e}")

# Функция для записи флагов (дискретных выходов)
def write_coil(client, address, value, unit=1):
    try:
        response = client.write_coil(address, value, unit=unit)
        if response.isError():
            print(f"Ошибка записи флага: {response}")
        else:
            print(f"Флаг записан успешно: {value}")
    except Exception as e:
        print(f"Ошибка при записи флага: {e}")

# Создание и подключение клиента
client = create_modbus_client(ip_address, port)
if client:
    while True:
        print("\nВыберите действие:")
        print("1: Чтение регистра")
        print("2: Запись регистра")
        print("3: Чтение флага")
        print("4: Запись флага")
        print("5: Выход")

        choice = input("Введите номер действия: ")

        if choice == '1':
            register_address = int(input("Введите адрес регистра: "))
            float_value = read_float32_register(client, register_address)
            print(f"Прочитанное значение float32 регистра {register_address}: {float_value}")

        elif choice == '2':
            register_address = int(input("Введите адрес регистра: "))
            new_float_value = float(input("Введите новое значение float32: "))
            write_float32_register(client, register_address, new_float_value)

        elif choice == '3':
            coil_address = int(input("Введите адрес флага: "))
            coil_value = read_coil(client, coil_address)
            print(f"Прочитанное значение флага {coil_address}: {coil_value}")

        elif choice == '4':
            coil_address = int(input("Введите адрес флага: "))
            new_coil_value = input("Введите новое значение флага (True/False): ").strip().lower() == 'true'
            write_coil(client, coil_address, new_coil_value)

        elif choice == '5':
            break

        else:
            print("Неверный выбор, попробуйте снова.")

    # Отключение от устройства
    client.close()
