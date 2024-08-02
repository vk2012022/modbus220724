import tkinter as tk
import logging
import struct
from pyModbusTCP.client import ModbusClient

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация Modbus клиента
client = ModbusClient(host='192.168.1.126', port=502, auto_open=True, timeout=10)

# Глобальная переменная для отслеживания первого подключения
first_connection = True

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
flags = [False] * 19

def toggle_flag(flag_index):
    """Переключение состояния флага и обновление меток."""
    global flags
    flags[flag_index] = not flags[flag_index]
    write_flag(client, flag_index, flags[flag_index])
    update_button_colors()

def update_labels():
    """Обновление меток и цветов кнопок в зависимости от состояния флагов."""
    try:
        flags[3] = read_flag(client, 3)
        flags[4] = read_flag(client, 4)
        label_opening.config(bg="orange" if flags[3] else "grey")
        label_closing.config(bg="orange" if flags[4] else "grey")

        flags[8] = read_flag(client, 8)
        flags[9] = read_flag(client, 9)
        label_opening2.config(bg="orange" if flags[8] else "grey")
        label_closing2.config(bg="orange" if flags[9] else "grey")

        flags[10] = read_flag(client, 10)
        label_boiler_relay.config(bg="orange" if flags[10] else "grey")

        for i in range(12, 15):
            flags[i] = read_flag(client, i)

        button_correction_radiators_plus.config(bg="orange" if flags[12] else "grey")
        button_correction_radiators_minus.config(bg="orange" if flags[13] else "grey")
        button_correction_floor_plus.config(bg="orange" if flags[14] else "grey")
        button_correction_floor_minus.config(bg="orange" if flags[15] else "grey")

        button_sensor_selection.config(bg="orange" if flags[16] else "grey")
        button_external_sensor_activation.config(bg="orange" if flags[17] else "grey")
        button_external_sensor_record.config(bg="orange" if flags[18] else "grey")

        update_button_colors()
        root.after(1000, update_labels)  # Обновление каждые 1 секунду
    except Exception as e:
        logger.error(f"Ошибка при обновлении меток: {e}")

def update_button_colors():
    """Обновление цветов кнопок в зависимости от их состояния."""
    button_auto.config(bg="orange" if flags[0] else "grey")
    button_open.config(bg="orange" if flags[1] else "grey")
    button_close.config(bg="orange" if flags[2] else "grey")

    button_auto2.config(bg="orange" if flags[5] else "grey")
    button_open2.config(bg="orange" if flags[6] else "grey")
    button_close2.config(bg="orange" if flags[7] else "grey")

    button_boiler_auto.config(bg="orange" if flags[11] else "grey")

def update_register_values():
    """Обновление значений регистров."""
    global first_connection
    try:
        logger.debug("Обновление значений регистров")

        def update_register_label_and_entry(address, count, label, entry):
            registers = read_registers(client, address, count)
            if registers:
                value = registers_to_float32(registers)
                label.config(text=f"{value:.1f}")
                if first_connection and entry is not None:
                    entry.delete(0, tk.END)
                    entry.insert(0, f"{value:.1f}")

        update_register_label_and_entry(18, 2, label_tx1_value, entry_tx1)
        update_register_label_and_entry(20, 2, label_ty1_value, entry_ty1)
        update_register_label_and_entry(22, 2, label_tx2_value, entry_tx2)
        update_register_label_and_entry(24, 2, label_ty2_value, entry_ty2)
        update_register_label_and_entry(12, 2, label_current_temp_value, None)
        update_register_label_and_entry(14, 2, label_required_temp_value, None)
        update_register_label_and_entry(16, 2, label_outdoor_temp_value, None)
        update_register_label_and_entry(0, 2, label_cycle_time_value, entry_cycle_time)
        update_register_label_and_entry(2, 2, label_full_cycle_time_value, entry_full_cycle_time)
        update_register_label_and_entry(4, 2, label_kp_value, entry_kp)
        update_register_label_and_entry(6, 2, label_ki_value, entry_ki)
        update_register_label_and_entry(8, 2, label_kd_value, entry_kd)
        update_register_label_and_entry(10, 2, label_dead_zone_value, entry_dead_zone)

        update_register_label_and_entry(26, 2, label_tx1_value2, entry_tx1_2)
        update_register_label_and_entry(28, 2, label_ty1_value2, entry_ty1_2)
        update_register_label_and_entry(30, 2, label_tx2_value2, entry_tx2_2)
        update_register_label_and_entry(32, 2, label_ty2_value2, entry_ty2_2)
        update_register_label_and_entry(36, 2, label_current_temp_value2, None)
        update_register_label_and_entry(34, 2, label_required_temp_value2, None)
        update_register_label_and_entry(16, 2, label_outdoor_temp_value2, None)
        update_register_label_and_entry(38, 2, label_cycle_time_value2, entry_cycle_time2)
        update_register_label_and_entry(40, 2, label_full_cycle_time_value2, entry_full_cycle_time2)
        update_register_label_and_entry(42, 2, label_kp_value2, entry_kp2)
        update_register_label_and_entry(44, 2, label_ki_value2, entry_ki2)
        update_register_label_and_entry(46, 2, label_kd_value2, entry_kd2)
        update_register_label_and_entry(48, 2, label_dead_zone_value2, entry_dead_zone2)

        update_register_label_and_entry(54, 2, label_boiler_temp_value, None)
        update_register_label_and_entry(50, 2, label_boiler_on_temp_value, entry_boiler_on_temp)
        update_register_label_and_entry(52, 2, label_boiler_off_temp_value, entry_boiler_off_temp)

        update_register_label_and_entry(56, 2, label_home_sensor_2_value, None)
        update_register_label_and_entry(58, 2, label_security_sensor_value, None)
        update_register_label_and_entry(60, 2, label_radiator_supply_sensor_value, None)
        update_register_label_and_entry(62, 2, label_floor_supply_sensor_value, None)

        if first_connection:
            first_connection = False

        root.after(10000, update_register_values)  # Обновление каждые 10 секунд
    except Exception as e:
        logger.error(f"Ошибка при обновлении значений регистров: {e}")

def write_input_values():
    """Запись значений из полей ввода в регистры."""
    try:
        value_tx1 = float(entry_tx1.get())
        if -80 <= value_tx1 <= 80:
            write_registers(client, 18, value_tx1)
        else:
            logger.error("Некорректное значение для T_X1. Допустимый диапазон: -80 до 80")

        value_ty1 = float(entry_ty1.get())
        if -80 <= value_ty1 <= 80:
            write_registers(client, 20, value_ty1)
        else:
            logger.error("Некорректное значение для T_Y1. Допустимый диапазон: -80 до 80")

        value_tx2 = float(entry_tx2.get())
        if -80 <= value_tx2 <= 80:
            write_registers(client, 22, value_tx2)
        else:
            logger.error("Некорректное значение для T_X2. Допустимый диапазон: -80 до 80")

        value_ty2 = float(entry_ty2.get())
        if -80 <= value_ty2 <= 80:
            write_registers(client, 24, value_ty2)
        else:
            logger.error("Некорректное значение для T_Y2. Допустимый диапазон: -80 до 80")

        update_register_values()  # Обновить значения на экране после записи
    except ValueError:
        logger.error("Некорректное значение в поле ввода")
    except Exception as e:
        logger.error(f"Ошибка при записи значений: {e}")

def write_new_register_values():
    """Запись значений из полей ввода в новые регистры."""
    try:
        value_cycle_time = float(entry_cycle_time.get())
        write_registers(client, 0, value_cycle_time)

        value_full_cycle_time = float(entry_full_cycle_time.get())
        write_registers(client, 2, value_full_cycle_time)

        value_kp = float(entry_kp.get())
        write_registers(client, 4, value_kp)

        value_ki = float(entry_ki.get())
        write_registers(client, 6, value_ki)

        value_kd = float(entry_kd.get())
        write_registers(client, 8, value_kd)

        value_dead_zone = float(entry_dead_zone.get())
        write_registers(client, 10, value_dead_zone)

        update_register_values()  # Обновить значения на экране после записи
    except ValueError:
        logger.error("Некорректное значение в поле ввода")
    except Exception as e:
        logger.error(f"Ошибка при записи новых значений: {e}")

def write_input_values2():
    """Запись значений из полей ввода в регистры для второго контура."""
    try:
        value_tx1 = float(entry_tx1_2.get())
        if -80 <= value_tx1 <= 80:
            write_registers(client, 26, value_tx1)
        else:
            logger.error("Некорректное значение для X1. Допустимый диапазон: -80 до 80")

        value_ty1 = float(entry_ty1_2.get())
        if -80 <= value_ty1 <= 80:
            write_registers(client, 28, value_ty1)
        else:
            logger.error("Некорректное значение для Y1. Допустимый диапазон: -80 до 80")

        value_tx2 = float(entry_tx2_2.get())
        if -80 <= value_tx2 <= 80:
            write_registers(client, 30, value_tx2)
        else:
            logger.error("Некорректное значение для X2. Допустимый диапазон: -80 до 80")

        value_ty2 = float(entry_ty2_2.get())
        if -80 <= value_ty2 <= 80:
            write_registers(client, 32, value_ty2)
        else:
            logger.error("Некорректное значение для Y2. Допустимый диапазон: -80 до 80")

        update_register_values()  # Обновить значения на экране после записи
    except ValueError:
        logger.error("Некорректное значение в поле ввода")
    except Exception as e:
        logger.error(f"Ошибка при записи значений для второго контура: {e}")

def write_new_register_values2():
    """Запись значений из полей ввода в новые регистры для второго контура."""
    try:
        value_cycle_time = float(entry_cycle_time2.get())
        write_registers(client, 38, value_cycle_time)

        value_full_cycle_time = float(entry_full_cycle_time2.get())
        write_registers(client, 40, value_full_cycle_time)

        value_kp = float(entry_kp2.get())
        write_registers(client, 42, value_kp)

        value_ki = float(entry_ki2.get())
        write_registers(client, 44, value_ki)

        value_kd = float(entry_kd2.get())
        write_registers(client, 46, value_kd)

        value_dead_zone = float(entry_dead_zone2.get())
        write_registers(client, 48, value_dead_zone)

        update_register_values()  # Обновить значения на экране после записи
    except ValueError:
        logger.error("Некорректное значение в поле ввода")
    except Exception as e:
        logger.error(f"Ошибка при записи новых значений для второго контура: {e}")

def write_boiler_values():
    """Запись значений из полей ввода в регистры для бойлера."""
    try:
        value_boiler_on_temp = float(entry_boiler_on_temp.get())
        if 30 <= value_boiler_on_temp <= 50:
            write_registers(client, 50, value_boiler_on_temp)
        else:
            logger.error("Некорректное значение для ТЕМП ВКЛ НАГРЕВА ГВС. Допустимый диапазон: 30 до 50")

        value_boiler_off_temp = float(entry_boiler_off_temp.get())
        if 30 <= value_boiler_off_temp <= 50:
            write_registers(client, 52, value_boiler_off_temp)
        else:
            logger.error("Некорректное значение для ТЕМП ВЫКЛ НАГРЕВА ГВС. Допустимый диапазон: 30 до 50")

        update_register_values()  # Обновить значения на экране после записи
    except ValueError:
        logger.error("Некорректное значение в поле ввода")
    except Exception as e:
        logger.error(f"Ошибка при записи значений для бойлера: {e}")

# Настройка GUI
root = tk.Tk()
root.title("Панель управления Modbus")

# Первый контур
label_frame1 = tk.LabelFrame(root, text="Контур 1", padx=10, pady=5)
label_frame1.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

button_auto = tk.Button(label_frame1, text="АВТО", command=lambda: toggle_flag(0), bg="grey", width=20, height=2)
button_auto.grid(row=0, column=0, pady=5)

button_open = tk.Button(label_frame1, text="ОТКР", command=lambda: toggle_flag(1), bg="grey", width=20, height=2)
button_open.grid(row=1, column=0, pady=5)

button_close = tk.Button(label_frame1, text="ЗАКР", command=lambda: toggle_flag(2), bg="grey", width=20, height=2)
button_close.grid(row=2, column=0, pady=5)

label_opening = tk.Canvas(label_frame1, width=40, height=40, bg="grey")
label_opening.grid(row=1, column=1, pady=5, padx=10)
label_closing = tk.Canvas(label_frame1, width=40, height=40, bg="grey")
label_closing.grid(row=2, column=1, pady=5, padx=10)

label_tx1 = tk.Label(label_frame1, text="T_X1:", font=("Arial", 12))
label_tx1.grid(row=3, column=0, pady=5, sticky="e")
label_tx1_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_tx1_value.grid(row=3, column=1, pady=5, sticky="w")

label_ty1 = tk.Label(label_frame1, text="T_Y1:", font=("Arial", 12))
label_ty1.grid(row=4, column=0, pady=5, sticky="e")
label_ty1_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_ty1_value.grid(row=4, column=1, pady=5, sticky="w")

label_tx2 = tk.Label(label_frame1, text="T_X2:", font=("Arial", 12))
label_tx2.grid(row=5, column=0, pady=5, sticky="e")
label_tx2_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_tx2_value.grid(row=5, column=1, pady=5, sticky="w")

label_ty2 = tk.Label(label_frame1, text="T_Y2:", font=("Arial", 12))
label_ty2.grid(row=6, column=0, pady=5, sticky="e")
label_ty2_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_ty2_value.grid(row=6, column=1, pady=5, sticky="w")

entry_tx1 = tk.Entry(label_frame1, font=("Arial", 12))
entry_tx1.grid(row=3, column=2, pady=5, padx=10)
entry_ty1 = tk.Entry(label_frame1, font=("Arial", 12))
entry_ty1.grid(row=4, column=2, pady=5, padx=10)
entry_tx2 = tk.Entry(label_frame1, font=("Arial", 12))
entry_tx2.grid(row=5, column=2, pady=5, padx=10)
entry_ty2 = tk.Entry(label_frame1, font=("Arial", 12))
entry_ty2.grid(row=6, column=2, pady=5, padx=10)

button_write = tk.Button(label_frame1, text="ЗАПИСАТЬ", command=write_input_values, bg="blue", fg="white", width=20, height=2)
button_write.grid(row=7, column=0, columnspan=3, pady=5)

button_correction_radiators_plus = tk.Button(label_frame1, text="КОРРЕКЦИЯ ПЛЮС", command=lambda: toggle_flag(12), bg="grey", width=20, height=2)
button_correction_radiators_plus.grid(row=8, column=0, columnspan=3, pady=5)

button_correction_radiators_minus = tk.Button(label_frame1, text="КОРРЕКЦИЯ МИНУС", command=lambda: toggle_flag(13), bg="grey", width=20, height=2)
button_correction_radiators_minus.grid(row=9, column=0, columnspan=3, pady=5)

temp_frame1 = tk.LabelFrame(label_frame1, text="Температуры", padx=5, pady=5)
temp_frame1.grid(row=10, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

label_current_temp = tk.Label(temp_frame1, text="Текущая температура:", font=("Arial", 12))
label_current_temp.grid(row=0, column=0, pady=5, sticky="e")
label_current_temp_value = tk.Label(temp_frame1, text="0.0", font=("Arial", 12))
label_current_temp_value.grid(row=0, column=1, pady=5, sticky="w")

label_required_temp = tk.Label(temp_frame1, text="Требуемая температура:", font=("Arial", 12))
label_required_temp.grid(row=1, column=0, pady=5, sticky="e")
label_required_temp_value = tk.Label(temp_frame1, text="0.0", font=("Arial", 12))
label_required_temp_value.grid(row=1, column=1, pady=5, sticky="w")

label_outdoor_temp = tk.Label(temp_frame1, text="Температура на улице:", font=("Arial", 12))
label_outdoor_temp.grid(row=2, column=0, pady=5, sticky="e")
label_outdoor_temp_value = tk.Label(temp_frame1, text="0.0", font=("Arial", 12))
label_outdoor_temp_value.grid(row=2, column=1, pady=5, sticky="w")

# Добавление новых полей и меток для регистров 0-1, 2-3, 4-5, 6-7, 8-9
label_cycle_time = tk.Label(label_frame1, text="ВРЕМЯ ЦИКЛА:", font=("Arial", 12))
label_cycle_time.grid(row=11, column=0, pady=5, sticky="e")
label_cycle_time_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_cycle_time_value.grid(row=11, column=1, pady=5, sticky="w")
entry_cycle_time = tk.Entry(label_frame1, font=("Arial", 12))
entry_cycle_time.grid(row=11, column=2, pady=5, padx=10)

label_full_cycle_time = tk.Label(label_frame1, text="ВРЕМЯ ПОЛНОГО ХОДА:", font=("Arial", 12))
label_full_cycle_time.grid(row=12, column=0, pady=5, sticky="e")
label_full_cycle_time_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_full_cycle_time_value.grid(row=12, column=1, pady=5, sticky="w")
entry_full_cycle_time = tk.Entry(label_frame1, font=("Arial", 12))
entry_full_cycle_time.grid(row=12, column=2, pady=5, padx=10)

label_kp = tk.Label(label_frame1, text="КОЭФФИЦИЕНТ П:", font=("Arial", 12))
label_kp.grid(row=13, column=0, pady=5, sticky="e")
label_kp_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_kp_value.grid(row=13, column=1, pady=5, sticky="w")
entry_kp = tk.Entry(label_frame1, font=("Arial", 12))
entry_kp.grid(row=13, column=2, pady=5, padx=10)

label_ki = tk.Label(label_frame1, text="КОЭФФИЦИЕНТ И:", font=("Arial", 12))
label_ki.grid(row=14, column=0, pady=5, sticky="e")
label_ki_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_ki_value.grid(row=14, column=1, pady=5, sticky="w")
entry_ki = tk.Entry(label_frame1, font=("Arial", 12))
entry_ki.grid(row=14, column=2, pady=5, padx=10)

label_kd = tk.Label(label_frame1, text="КОЭФФИЦИЕНТ Д:", font=("Arial", 12))
label_kd.grid(row=15, column=0, pady=5, sticky="e")
label_kd_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_kd_value.grid(row=15, column=1, pady=5, sticky="w")
entry_kd = tk.Entry(label_frame1, font=("Arial", 12))
entry_kd.grid(row=15, column=2, pady=5, padx=10)

label_dead_zone = tk.Label(label_frame1, text="ЗОНА НЕЧУВСТВИТЕЛЬНОСТИ:", font=("Arial", 12))
label_dead_zone.grid(row=16, column=0, pady=5, sticky="e")
label_dead_zone_value = tk.Label(label_frame1, text="0.0", font=("Arial", 12))
label_dead_zone_value.grid(row=16, column=1, pady=5, sticky="w")
entry_dead_zone = tk.Entry(label_frame1, font=("Arial", 12))
entry_dead_zone.grid(row=16, column=2, pady=5, padx=10)

# Добавление новой кнопки для записи только во вновь созданные регистры
button_write_new = tk.Button(label_frame1, text="ЗАПИСАТЬ ПИД", command=write_new_register_values, bg="green", fg="white", width=25, height=2)
button_write_new.grid(row=17, column=0, columnspan=3, pady=5)

# Второй контур
label_frame2 = tk.LabelFrame(root, text="Контур 2", padx=10, pady=5)
label_frame2.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

button_auto2 = tk.Button(label_frame2, text="АВТО", command=lambda: toggle_flag(5), bg="grey", width=20, height=2)
button_auto2.grid(row=0, column=0, pady=5)

button_open2 = tk.Button(label_frame2, text="ОТКР", command=lambda: toggle_flag(6), bg="grey", width=20, height=2)
button_open2.grid(row=1, column=0, pady=5)

button_close2 = tk.Button(label_frame2, text="ЗАКР", command=lambda: toggle_flag(7), bg="grey", width=20, height=2)
button_close2.grid(row=2, column=0, pady=5)

label_opening2 = tk.Canvas(label_frame2, width=40, height=40, bg="grey")
label_opening2.grid(row=1, column=1, pady=5, padx=10)
label_closing2 = tk.Canvas(label_frame2, width=40, height=40, bg="grey")
label_closing2.grid(row=2, column=1, pady=5, padx=10)

label_tx1_2 = tk.Label(label_frame2, text="X1:", font=("Arial", 12))
label_tx1_2.grid(row=3, column=0, pady=5, sticky="e")
label_tx1_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_tx1_value2.grid(row=3, column=1, pady=5, sticky="w")

label_ty1_2 = tk.Label(label_frame2, text="Y1:", font=("Arial", 12))
label_ty1_2.grid(row=4, column=0, pady=5, sticky="e")
label_ty1_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_ty1_value2.grid(row=4, column=1, pady=5, sticky="w")

label_tx2_2 = tk.Label(label_frame2, text="X2:", font=("Arial", 12))
label_tx2_2.grid(row=5, column=0, pady=5, sticky="e")
label_tx2_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_tx2_value2.grid(row=5, column=1, pady=5, sticky="w")

label_ty2_2 = tk.Label(label_frame2, text="Y2:", font=("Arial", 12))
label_ty2_2.grid(row=6, column=0, pady=5, sticky="e")
label_ty2_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_ty2_value2.grid(row=6, column=1, pady=5, sticky="w")

entry_tx1_2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_tx1_2.grid(row=3, column=2, pady=5, padx=10)
entry_ty1_2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_ty1_2.grid(row=4, column=2, pady=5, padx=10)
entry_tx2_2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_tx2_2.grid(row=5, column=2, pady=5, padx=10)
entry_ty2_2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_ty2_2.grid(row=6, column=2, pady=5, padx=10)

button_write2 = tk.Button(label_frame2, text="ЗАПИСАТЬ", command=write_input_values2, bg="blue", fg="white", width=20, height=2)
button_write2.grid(row=7, column=0, columnspan=3, pady=5)

button_correction_floor_plus = tk.Button(label_frame2, text="КОРРЕКЦИЯ ПЛЮС", command=lambda: toggle_flag(14), bg="grey", width=20, height=2)
button_correction_floor_plus.grid(row=8, column=0, columnspan=3, pady=5)

button_correction_floor_minus = tk.Button(label_frame2, text="КОРРЕКЦИЯ МИНУС", command=lambda: toggle_flag(15), bg="grey", width=20, height=2)
button_correction_floor_minus.grid(row=9, column=0, columnspan=3, pady=5)

temp_frame2 = tk.LabelFrame(label_frame2, text="Температуры", padx=5, pady=5)
temp_frame2.grid(row=10, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

label_current_temp2 = tk.Label(temp_frame2, text="Текущая температура:", font=("Arial", 12))
label_current_temp2.grid(row=0, column=0, pady=5, sticky="e")
label_current_temp_value2 = tk.Label(temp_frame2, text="0.0", font=("Arial", 12))
label_current_temp_value2.grid(row=0, column=1, pady=5, sticky="w")

label_required_temp2 = tk.Label(temp_frame2, text="Требуемая температура:", font=("Arial", 12))
label_required_temp2.grid(row=1, column=0, pady=5, sticky="e")
label_required_temp_value2 = tk.Label(temp_frame2, text="0.0", font=("Arial", 12))
label_required_temp_value2.grid(row=1, column=1, pady=5, sticky="w")

label_outdoor_temp2 = tk.Label(temp_frame2, text="Температура на улице:", font=("Arial", 12))
label_outdoor_temp2.grid(row=2, column=0, pady=5, sticky="e")
label_outdoor_temp_value2 = tk.Label(temp_frame2, text="0.0", font=("Arial", 12))
label_outdoor_temp_value2.grid(row=2, column=1, pady=5, sticky="w")

# Добавление новых полей и меток для регистров 38-39, 40-41, 42-43, 44-45, 46-47, 48-49
label_cycle_time2 = tk.Label(label_frame2, text="ВРЕМЯ ЦИКЛА:", font=("Arial", 12))
label_cycle_time2.grid(row=11, column=0, pady=5, sticky="e")
label_cycle_time_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_cycle_time_value2.grid(row=11, column=1, pady=5, sticky="w")
entry_cycle_time2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_cycle_time2.grid(row=11, column=2, pady=5, padx=10)

label_full_cycle_time2 = tk.Label(label_frame2, text="ВРЕМЯ ПОЛНОГО ХОДА:", font=("Arial", 12))
label_full_cycle_time2.grid(row=12, column=0, pady=5, sticky="e")
label_full_cycle_time_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_full_cycle_time_value2.grid(row=12, column=1, pady=5, sticky="w")
entry_full_cycle_time2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_full_cycle_time2.grid(row=12, column=2, pady=5, padx=10)

label_kp2 = tk.Label(label_frame2, text="КОЭФФИЦИЕНТ П:", font=("Arial", 12))
label_kp2.grid(row=13, column=0, pady=5, sticky="e")
label_kp_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_kp_value2.grid(row=13, column=1, pady=5, sticky="w")
entry_kp2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_kp2.grid(row=13, column=2, pady=5, padx=10)

label_ki2 = tk.Label(label_frame2, text="КОЭФФИЦИЕНТ И:", font=("Arial", 12))
label_ki2.grid(row=14, column=0, pady=5, sticky="e")
label_ki_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_ki_value2.grid(row=14, column=1, pady=5, sticky="w")
entry_ki2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_ki2.grid(row=14, column=2, pady=5, padx=10)

label_kd2 = tk.Label(label_frame2, text="КОЭФФИЦИЕНТ Д:", font=("Arial", 12))
label_kd2.grid(row=15, column=0, pady=5, sticky="e")
label_kd_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_kd_value2.grid(row=15, column=1, pady=5, sticky="w")
entry_kd2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_kd2.grid(row=15, column=2, pady=5, padx=10)

label_dead_zone2 = tk.Label(label_frame2, text="ЗОНА НЕЧУВСТВИТЕЛЬНОСТИ:", font=("Arial", 12))
label_dead_zone2.grid(row=16, column=0, pady=5, sticky="e")
label_dead_zone_value2 = tk.Label(label_frame2, text="0.0", font=("Arial", 12))
label_dead_zone_value2.grid(row=16, column=1, pady=5, sticky="w")
entry_dead_zone2 = tk.Entry(label_frame2, font=("Arial", 12))
entry_dead_zone2.grid(row=16, column=2, pady=5, padx=10)

# Добавление новой кнопки для записи только во вновь созданные регистры
button_write_new2 = tk.Button(label_frame2, text="ЗАПИСАТЬ ПИД", command=write_new_register_values2, bg="green", fg="white", width=25, height=2)
button_write_new2.grid(row=17, column=0, columnspan=3, pady=5)

# Панель для бойлера
label_frame_boiler = tk.LabelFrame(root, text="Бойлер", padx=10, pady=5)
label_frame_boiler.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

label_boiler_temp = tk.Label(label_frame_boiler, text="ТЕМПЕРАТУРА ГВС:", font=("Arial", 12))
label_boiler_temp.grid(row=0, column=0, pady=5, sticky="e")
label_boiler_temp_value = tk.Label(label_frame_boiler, text="0.0", font=("Arial", 12))
label_boiler_temp_value.grid(row=0, column=1, pady=5, sticky="w")

button_boiler_auto = tk.Button(label_frame_boiler, text="АВТО ГВС", command=lambda: toggle_flag(11), bg="grey", width=20, height=2)
button_boiler_auto.grid(row=1, column=0, columnspan=2, pady=5)

label_boiler_relay = tk.Canvas(label_frame_boiler, width=40, height=40, bg="grey")
label_boiler_relay.grid(row=2, column=1, pady=5, padx=10)
label_boiler_relay_text = tk.Label(label_frame_boiler, text="СОСТОЯНИЕ РЕЛЕ НАГРЕВА ГВС:", font=("Arial", 12))
label_boiler_relay_text.grid(row=2, column=0, pady=5, sticky="e")

label_boiler_on_temp = tk.Label(label_frame_boiler, text="ТЕМП ВКЛ НАГРЕВА ГВС:", font=("Arial", 12))
label_boiler_on_temp.grid(row=3, column=0, pady=5, sticky="e")
label_boiler_on_temp_value = tk.Label(label_frame_boiler, text="0.0", font=("Arial", 12))
label_boiler_on_temp_value.grid(row=3, column=1, pady=5, sticky="w")
entry_boiler_on_temp = tk.Entry(label_frame_boiler, font=("Arial", 12))
entry_boiler_on_temp.grid(row=3, column=2, pady=5, padx=10)

label_boiler_off_temp = tk.Label(label_frame_boiler, text="ТЕМП ВЫКЛ НАГРЕВА ГВС:", font=("Arial", 12))
label_boiler_off_temp.grid(row=4, column=0, pady=5, sticky="e")
label_boiler_off_temp_value = tk.Label(label_frame_boiler, text="0.0", font=("Arial", 12))
label_boiler_off_temp_value.grid(row=4, column=1, pady=5, sticky="w")
entry_boiler_off_temp = tk.Entry(label_frame_boiler, font=("Arial", 12))
entry_boiler_off_temp.grid(row=4, column=2, pady=5, padx=10)

button_write_boiler = tk.Button(label_frame_boiler, text="ЗАПИСЬ ГВС", command=write_boiler_values, bg="green", fg="white", width=25, height=2)
button_write_boiler.grid(row=5, column=0, columnspan=3, pady=5)

label_home_sensor_2 = tk.Label(label_frame_boiler, text="ДАТЧИК ТЕМПЕРАТУРЫ НА ДОМЕ №2:", font=("Arial", 12))
label_home_sensor_2.grid(row=6, column=0, pady=5, sticky="e")
label_home_sensor_2_value = tk.Label(label_frame_boiler, text="0.0", font=("Arial", 12))
label_home_sensor_2_value.grid(row=6, column=1, pady=5, sticky="w")

label_security_sensor = tk.Label(label_frame_boiler, text="ДАТЧИК ТЕМП НА КОТЕЛЬНОЙ ОХРАНЫ:", font=("Arial", 12))
label_security_sensor.grid(row=7, column=0, pady=5, sticky="e")
label_security_sensor_value = tk.Label(label_frame_boiler, text="0.0", font=("Arial", 12))
label_security_sensor_value.grid(row=7, column=1, pady=5, sticky="w")

label_radiator_supply_sensor = tk.Label(label_frame_boiler, text="НАРУЖНЫЙ ДАТЧИК ПОДАЧИ РАДИАТОРОВ:", font=("Arial", 12))
label_radiator_supply_sensor.grid(row=8, column=0, pady=5, sticky="e")
label_radiator_supply_sensor_value = tk.Label(label_frame_boiler, text="0.0", font=("Arial", 12))
label_radiator_supply_sensor_value.grid(row=8, column=1, pady=5, sticky="w")

label_floor_supply_sensor = tk.Label(label_frame_boiler, text="НАРУЖНЫЙ ДАТЧИК ПОДАЧИ ТЕПЛОГО ПОЛА:", font=("Arial", 12))
label_floor_supply_sensor.grid(row=9, column=0, pady=5, sticky="e")
label_floor_supply_sensor_value = tk.Label(label_frame_boiler, text="0.0", font=("Arial", 12))
label_floor_supply_sensor_value.grid(row=9, column=1, pady=5, sticky="w")

button_sensor_selection = tk.Button(label_frame_boiler, text="ВЫБОР ДАТЧИКОВ НА ДОМЕ 1 ИЛИ 2", command=lambda: toggle_flag(16), bg="grey", width=30, height=2)
button_sensor_selection.grid(row=10, column=0, pady=5)

button_external_sensor_activation = tk.Button(label_frame_boiler, text="ВКЛЮЧЕНИЕ ВНЕШНИХ ДАТЧИКОВ", command=lambda: toggle_flag(17), bg="grey", width=30, height=2)
button_external_sensor_activation.grid(row=11, column=0, pady=5)

button_external_sensor_record = tk.Button(label_frame_boiler, text="ЗАП РЕГ ВНЕШ ДАТЧИКОВ", command=lambda: toggle_flag(18), bg="grey", width=30, height=2)
button_external_sensor_record.grid(row=12, column=0, pady=5)

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
