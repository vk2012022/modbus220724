import logging
import struct
from pyModbusTCP.client import ModbusClient

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def float32_to_registers(value):
    """Преобразование float32 в два 16-битных регистра."""
    packed = struct.pack('>f', value)
    return struct.unpack('>HH', packed)


def registers_to_float32(registers):
    """Преобразование двух 16-битных регистров в float32."""
    packed = struct.pack('>HH', *registers)
    return struct.unpack('>f', packed)[0]


def read_register(client, address):
    response = client.read_holding_registers(address, 2)
    if response:
        return registers_to_float32(response)
    else:
        logger.error(f"Ошибка чтения регистра по адресу {address}")
        return None


def write_register(client, address, value):
    registers = float32_to_registers(value)
    success = client.write_multiple_registers(address, registers)
    if not success:
        logger.error(f"Ошибка записи регистра по адресу {address}")


def read_flag(client, address):
    response = client.read_coils(address, 1)
    if response:
        return response[0]
    else:
        logger.error(f"Ошибка чтения флага по адресу {address}")
        return None


def write_flag(client, address, value):
    success = client.write_single_coil(address, value)
    if not success:
        logger.error(f"Ошибка записи флага по адресу {address}")


def main():
    client = ModbusClient(host='192.168.1.126', port=502, auto_open=False, timeout=10)

    if not client.open():
        logger.error("Не удалось установить соединение с устройством.")
        return

    while True:
        print("\nВыберите действие:")
        print("1: Чтение регистра (Holding Registers)")
        print("2: Запись регистра (Holding Registers)")
        print("3: Чтение флага (Coil)")
        print("4: Запись флага (Coil)")
        print("5: Выход")

        choice = input("Введите номер действия: ")

        if choice == '1':
            address = int(input("Введите адрес регистра: "))
            value = read_register(client, address)
            if value is not None:
                print(f"Значение регистра {address}: {value}")

        elif choice == '2':
            address = int(input("Введите адрес регистра: "))
            value = float(input("Введите новое значение float32: "))
            write_register(client, address, value)
            print(f"Записано значение {value} в регистр {address}")

        elif choice == '3':
            address = int(input("Введите адрес флага: "))
            value = read_flag(client, address)
            if value is not None:
                print(f"Значение флага {address}: {value}")

        elif choice == '4':
            address = int(input("Введите адрес флага: "))
            while True:
                flag_value = input("Введите новое значение флага (True/False): ").lower()
                if flag_value == 'true':
                    value = True
                    break
                elif flag_value == 'false':
                    value = False
                    break
                else:
                    print("Неверное значение. Введите 'True' или 'False'.")
            write_flag(client, address, value)
            print(f"Записано значение {value} в флаг {address}")

        elif choice == '5':
            break

        else:
            print("Неверный выбор, попробуйте снова.")

    client.close()
    logger.info("Соединение закрыто.")


if __name__ == '__main__':
    main()
