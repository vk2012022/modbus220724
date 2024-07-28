import tkinter as tk
import logging
import struct
import time
from pyModbusTCP.client import ModbusClient

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация Modbus клиента
client = ModbusClient(host='192.168.1.126', port=502, auto_open=True, timeout=10)


def float32_to_registers(value):
    """Преобразование float32 в два 16-битных регистра."""
    packed = struct.pack('>f', value)
    return struct.unpack('>HH', packed)


def registers_to_float32(registers):
    """Преобразование двух 16-битных регистров в float32."""
    packed = struct.pack('>HH', *registers)
    return struct.unpack('>f', packed)[0]


def ensure_connection():
    """Проверка и восстановление подключения к Modbus устройству."""
    if not client.is_open:
        if not client.open():
            logger.error("Не удалось установить соединение с устройством Modbus.")
            return False
        else:
            logger.info("Соединение с устройством Modbus установлено.")
    return True


def read_registers(client, address, count):
    """Чтение значения регистров по указанному адресу."""
    if ensure_connection():
        response = client.read_holding_registers(address, count)
        if response:
            return response
        else:
            logger.error(f"Ошибка чтения регистров по адресу {address}")
    return None


def write_registers(client, address, value):
    """Запись значения в регистры по указанному адресу."""
    if ensure_connection():
        registers = float32_to_registers(value)
        success = client.write_multiple_registers(address, registers)
        if not success:
            logger.error(f"Ошибка записи в регистры по адресу {address}")
        else:
            logger.debug(f"Успешная запись в регистры по адресу {address} со значением {value}")


def read_flag(client, address):
    """Чтение значения флага (катушки) по указанному адресу."""
    if ensure_connection():
        response = client.read_coils(address, 1)
        if response:
            return response[0]
        else:
            logger.error(f"Ошибка чтения флага по адресу {address}")
    return None


def write_flag(client, address, value):
    """Запись значения флага (катушки) по указанному адресу."""
    if ensure_connection():
        logger.debug(f"Попытка записи флага по адресу {address} со значением {value}")
        success = client.write_single_coil(address, value)
        if not success:
            logger.error(f"Ошибка записи флага по адресу {address}")
        else:
            logger.debug(f"Успешная запись флага по адресу {address}")


# Инициализация флагов
flags = [False, False, False, False, False]


# Функция для обновления флагов
def toggle_flag(flag_index):
    """Переключение состояния флага и обновление меток."""
    global flags
    flags[flag_index] = not flags[flag_index]
    write_flag(client, flag_index, flags[flag_index])
    update_button_colors()
    time.sleep(0.5)  # Задержка для предотвращения перегрузки


# Функция для обновления меток
def update_labels():
    """Обновление меток и цветов кнопок в зависимости от состояния флагов."""
    # Обновление состояния флагов ОТКРЫТИЕ и ЗАКРЫТИЕ
    flags[3] = read_flag(client, 3)
    flags[4] = read_flag(client, 4)
    label_opening.config(text=f"ОТКРЫТИЕ: {flags[3]}")
    label_closing.config(text=f"ЗАКРЫТИЕ: {flags[4]}")
    update_button_colors()

    root.after(1000, update_labels)  # Обновление каждые 1 секунду


def update_button_colors():
    """Обновление цветов кнопок в зависимости от их состояния."""
    button_auto.config(bg="green" if flags[0] else "red")
    button_open.config(bg="green" if flags[1] else "red")
    button_close.config(bg="green" if flags[2] else "red")


def update_register_values():
    """Обновление значений регистров."""
    logger.debug("Обновление значений регистров")

    def update_register_label(address, count, label):
        registers = read_registers(client, address, count)
        if registers:
            value = registers_to_float32(registers)
            label.config(text=f"{value:.1f}")

    update_register_label(18, 2, label_tx1_value)
    update_register_label(20, 2, label_ty1_value)
    update_register_label(22, 2, label_tx2_value)
    update_register_label(24, 2, label_ty2_value)
    update_register_label(12, 2, label_current_temp_value)
    update_register_label(14, 2, label_required_temp_value)

    root.after(5000, update_register_values)  # Обновление каждые 5 секунд


def write_input_values():
    """Запись значений из полей ввода в регистры."""
    try:
        value_tx1 = float(entry_tx1.get())
        if -80 <= value_tx1 <= 80:
            write_registers(client, 18, value_tx1)
        else:
            logger.error("Некорректное значение для T_X1. Допустимый диапазон: -80 до 80")
        time.sleep(1)  # Задержка между запросами

        value_ty1 = float(entry_ty1.get())
        if -80 <= value_ty1 <= 80:
            write_registers(client, 20, value_ty1)
        else:
            logger.error("Некорректное значение для T_Y1. Допустимый диапазон: -80 до 80")
        time.sleep(1)  # Задержка между запросами

        value_tx2 = float(entry_tx2.get())
        if -80 <= value_tx2 <= 80:
            write_registers(client, 22, value_tx2)
        else:
            logger.error("Некорректное значение для T_X2. Допустимый диапазон: -80 до 80")
        time.sleep(1)  # Задержка между запросами

        value_ty2 = float(entry_ty2.get())
        if -80 <= value_ty2 <= 80:
            write_registers(client, 24, value_ty2)
        else:
            logger.error("Некорректное значение для T_Y2. Допустимый диапазон: -80 до 80")

        update_register_values()  # Обновить значения на экране после записи
    except ValueError:
        logger.error("Некорректное значение в поле ввода")


# Настройка GUI
root = tk.Tk()
root.title("Панель управления Modbus")

button_auto = tk.Button(root, text="АВТО", command=lambda: toggle_flag(0), bg="red", width=20, height=2)
button_auto.grid(row=0, column=0, columnspan=2, pady=10)

button_open = tk.Button(root, text="ОТКР", command=lambda: toggle_flag(1), bg="red", width=20, height=2)
button_open.grid(row=1, column=0, columnspan=2, pady=10)

button_close = tk.Button(root, text="ЗАКР", command=lambda: toggle_flag(2), bg="red", width=20, height=2)
button_close.grid(row=2, column=0, columnspan=2, pady=10)

label_opening = tk.Label(root, text="ОТКРЫТИЕ: False", font=("Arial", 12))
label_opening.grid(row=3, column=0, columnspan=2, pady=10)

label_closing = tk.Label(root, text="ЗАКРЫТИЕ: False", font=("Arial", 12))
label_closing.grid(row=4, column=0, columnspan=2, pady=10)

label_tx1 = tk.Label(root, text="T_X1:", font=("Arial", 12))
label_tx1.grid(row=5, column=0, pady=10, sticky="e")
label_tx1_value = tk.Label(root, text="0.0", font=("Arial", 12))
label_tx1_value.grid(row=5, column=1, pady=10, sticky="w")

label_ty1 = tk.Label(root, text="T_Y1:", font=("Arial", 12))
label_ty1.grid(row=6, column=0, pady=10, sticky="e")
label_ty1_value = tk.Label(root, text="0.0", font=("Arial", 12))
label_ty1_value.grid(row=6, column=1, pady=10, sticky="w")

label_tx2 = tk.Label(root, text="T_X2:", font=("Arial", 12))
label_tx2.grid(row=7, column=0, pady=10, sticky="e")
label_tx2_value = tk.Label(root, text="0.0", font=("Arial", 12))
label_tx2_value.grid(row=7, column=1, pady=10, sticky="w")

label_ty2 = tk.Label(root, text="T_Y2:", font=("Arial", 12))
label_ty2.grid(row=8, column=0, pady=10, sticky="e")
label_ty2_value = tk.Label(root, text="0.0", font=("Arial", 12))
label_ty2_value.grid(row=8, column=1, pady=10, sticky="w")

label_current_temp = tk.Label(root, text="Текущая температура:", font=("Arial", 12))
label_current_temp.grid(row=9, column=0, pady=10, sticky="e")
label_current_temp_value = tk.Label(root, text="0.0", font=("Arial", 12))
label_current_temp_value.grid(row=9, column=1, pady=10, sticky="w")

label_required_temp = tk.Label(root, text="Требуемая температура:", font=("Arial", 12))
label_required_temp.grid(row=10, column=0, pady=10, sticky="e")
label_required_temp_value = tk.Label(root, text="0.0", font=("Arial", 12))
label_required_temp_value.grid(row=10, column=1, pady=10, sticky="w")

entry_tx1 = tk.Entry(root, font=("Arial", 12))
entry_tx1.grid(row=5, column=2, pady=10, padx=10)
entry_ty1 = tk.Entry(root, font=("Arial", 12))
entry_ty1.grid(row=6, column=2, pady=10, padx=10)
entry_tx2 = tk.Entry(root, font=("Arial", 12))
entry_tx2.grid(row=7, column=2, pady=10, padx=10)
entry_ty2 = tk.Entry(root, font=("Arial", 12))
entry_ty2.grid(row=8, column=2, pady=10, padx=10)

button_write = tk.Button(root, text="ЗАПИСАТЬ", command=write_input_values, bg="blue", fg="white", width=20, height=2)
button_write.grid(row=11, column=0, columnspan=3, pady=10)

# Инициализация состояний флагов и цветов кнопок
update_labels()

# Проверка подключения
if not client.is_open:
    if not client.open():
        logger.error("Не удалось установить соединение с устройством Modbus.")
    else:
        logger.info("Соединение с устройством Modbus установлено.")

# Запуск обновления значений регистров
update_register_values()

root.mainloop()

# Закрытие соединения с клиентом при завершении
client.close()
logger.info("Соединение закрыто.")
