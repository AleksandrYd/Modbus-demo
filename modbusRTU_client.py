import socket, struct, select, serial
from tkinter import messagebox

from serial import SerialException


def connect_to_serial_port(port):
    port = port  # Replace with the appropriate COM port name
    baudrate = 9600  # Replace with the desired baud rate
    try:
        ser = serial.Serial(port, baudrate=baudrate, bytesize=8, parity=serial.PARITY_NONE, stopbits=1,
                            timeout=0.5)  # Создание объекта для подключения к COM порту
        return ser
    except SerialException:
        print_error([0, 0, 0, 0, 0, 11])
        return 0


def crc_check(rxpacket, len):
    reg_crc = 0xFFFF
    for i in range(len):
        reg_crc ^= rxpacket[i]
        for j in range(8):
            if reg_crc & 0x01:
                reg_crc = (reg_crc >> 1) ^ 0xA001
            else:
                reg_crc = reg_crc >> 1
    return reg_crc


def print_error(Rx_packet):  # Функция, выводящая на экран название ошибки
    code_definitions = {-1: "Error read single coil status",
                        -2: "Timeout error or connection was lost",
                        1: "Принятый код функции не может быть обработан.",
                        2: "Адрес данных, указанный в запросе, недоступен.",
                        3: "Значение, содержащееся в поле данных запроса, является недопустимой величиной.",
                        4: "Невосстанавливаемая ошибка имела место, пока ведомое устройство "
                           "пыталось выполнить затребованное действие.",
                        5: "Ведомое устройство приняло запрос и обрабатывает его, но это требует много времени.",
                        6: "Ведомое устройство занято обработкой команды. Ведущее устройство должно повторить "
                           "сообщение позже, когда ведомое освободится.",
                        7: "Ведомое устройство не может выполнить программную функцию, заданную в запросе. "
                           "Этот код возвращается для не успешного программного запроса, "
                           "использующего функции с номерами 13 или 14. Ведущее устройство должно запросить "
                           "диагностическую информацию или информацию об ошибках от ведомого.",
                        8: "Ведомое устройство при чтении расширенной памяти обнаружило ошибку паритета. "
                           "Ведущее устройство может повторить запрос, но обычно в таких случаях требуется ремонт.",
                        10: "Шлюз неправильно настроен или перегружен запросами.",
                        11: "Slave устройства нет в сети или от него нет ответа."
                        }
    messagebox.showerror(title='Error', message=code_definitions[Rx_packet[5]])
    return 0


def print_rxpacket_01_02(Rx_register_values, first_address, numberofcoils):
    number_of_coil = first_address
    for i in range(len(Rx_register_values)):
        # Создание массива длиной 8 (так как данные приходят в формате одного байта, то есть по 8 бит)
        # для заполнения его данными из пакета modbus
        bin_array = [0] * 8
        array = bin(Rx_register_values[i])[2:]
        for num1 in range(len(array)):
            bin_array[num1] = int(array[len(array) - 1 - num1])
        for j in range(8):
            print(f"Регистр номер {number_of_coil} = {bin_array[j]}")
            number_of_coil += 1
            if number_of_coil > first_address + numberofcoils - 1:
                break


def print_rxpacket_03_04(Rx_register_value, first_address, numberofcoils):
    number_of_coil = first_address
    for i in range(numberofcoils):
        number = Rx_register_value[i]
        print(f"Регистр номер {number_of_coil} = {number}")
        number_of_coil += 1
        '''number_of_coil = first_address
    for i in range(0,numberofcoils*2,2):
        Hi = Rx_register_value[i]
        Lo = Rx_register_value[i+1]
        Hi_hex = hex(Hi)
        Lo_hex = hex(Lo)
        number_hex =  str(Hi_hex)[2:] + str(Lo_hex)[2:]

        number = int(number_hex,16)
        print(f"Регистр номер {number_of_coil} = {number}")
        number_of_coil += 1'''

    # создать считывание 10-х чисел из последовательности 16 битных чисел типа : старший байт-> 00 0b <- младший байт


# чтение дискретных выходов(01) и входов(02)
def function_01_02(Tx_Slave_ID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddress, serial: serial.Serial):
    # Example = [1, 1, 0, 5, 1001] - Пример пакета для modbus в целочисленном формате
    TransferPacket = []
    buf_packet = []

    # Добавление в массив данных для отправки
    TransferPacket.append(Tx_Slave_ID)
    buf_packet.append(Tx_Slave_ID)
    TransferPacket.append(Tx_Function_code)
    buf_packet.append(Tx_Function_code)
    TransferPacket.append(Tx_RegisterAddress)
    buf_packet.append(0)
    buf_packet.append(Tx_RegisterAddress)
    TransferPacket.append(Tx_NumberAddress)
    buf_packet.append(0)
    buf_packet.append(Tx_NumberAddress)
    CRC = crc_check(buf_packet, 6)
    TransferPacket.append(CRC)

    # Конвертация целочисленного массива в байтовую строку
    Tx = struct.pack(">BBHHH", *TransferPacket)
    lower_byte = Tx[len(Tx) - 1].to_bytes()
    higher_byte = Tx[len(Tx) - 2].to_bytes()
    Tx = Tx[:-2]
    Tx += lower_byte
    Tx += higher_byte

    serial.write(Tx)

    Rx = serial.readline()
    # Считывание длины сообщения в пакете, содержащего необходимые данные
    Rx_additional_len_bin = str(Rx[2])
    Rx_additional_len = int((Rx_additional_len_bin), 16)
    Rx_packet = struct.unpack(">BBB" + 'B' * (Rx_additional_len) + 'H', Rx)
    Rx_CRC_rever = hex(Rx_packet[-1])
    Rx_lower_byte = Rx_CRC_rever[2:4]
    Rx_higher_byte = Rx_CRC_rever[4:]
    Rx_CRC = int(Rx_higher_byte + Rx_lower_byte, 16)
    # CRC приходит в реверснутом виде
    if Rx_CRC == crc_check(Rx_packet[:-2], 3 + Rx_additional_len):
        return Rx_packet
    else:
        return [0, 0, 0, 0, 0 - 2]


# Чтение аналоговых выходов(03) и входов(04)
def function_03_04(Tx_Slave_ID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddress, serial):
    TransferPacket = []
    buf_packet = []

    # Добавление в массив данных для отправки
    TransferPacket.append(Tx_Slave_ID)
    buf_packet.append(Tx_Slave_ID)
    TransferPacket.append(Tx_Function_code)
    buf_packet.append(Tx_Function_code)
    TransferPacket.append(Tx_RegisterAddress)
    buf_packet.append(Tx_RegisterAddress)
    TransferPacket.append(Tx_NumberAddress)
    buf_packet.append(Tx_NumberAddress)
    packet_for_CRC = struct.pack(">BBHH", *buf_packet)
    CRC = crc_check(packet_for_CRC, len(packet_for_CRC))
    TransferPacket.append(CRC)

    # Конвертация целочисленного массива в байтовую строку
    Tx = struct.pack(">BBHHH", *TransferPacket)
    lower_byte = Tx[len(Tx) - 1].to_bytes()
    higher_byte = Tx[len(Tx) - 2].to_bytes()
    Tx = Tx[:-2]
    Tx += lower_byte
    Tx += higher_byte

    serial.write(Tx)

    # Проверка порта на наличие в нем данных в течении 1 секунд, если будет пусто, значит вывод ошибки
    Rx = serial.read(100)
    # Считывание длины сообщения в пакете, содержащего необходимые данные
    try:
        Rx_additional_len_bin = hex(Rx[2])
    except:
        return [0, 0, 0, 0, 0, 11]
    if Rx[1] != Tx_Function_code:
        print_error([0, 0, 0, 0, 0, Rx[2]])

    Rx_additional_len = int((Rx_additional_len_bin), 16)
    Rx_packet = struct.unpack(">BBB" + 'H' * ((Rx_additional_len) // 2) + 'H', Rx)

    Rx_CRC_rever_hex = f'{Rx_packet[-1]:x}'
    Rx_CRC_rever = f'0x{Rx_CRC_rever_hex:0>4}'

    Rx_lower_byte = Rx_CRC_rever[2:4]
    Rx_higher_byte = Rx_CRC_rever[4:]
    Rx_CRC = int(Rx_higher_byte + Rx_lower_byte, 16)

    # CRC приходит в реверснутом виде
    if Rx_CRC == crc_check(Rx[:-2], 3 + Rx_additional_len):
        return Rx_packet
    else:
        return [0, 0, 0, 0, 0, -2]


# Запись одного дискретного выхода
def function_05(Tx_Slave_ID, Tx_Function_code, Tx_RegisterAddress, Tx_value_of_coil, serial):
    TransferPacket = []
    buf_packet = []

    # Добавление в массив данных для отправки
    TransferPacket.append(Tx_Slave_ID)
    buf_packet.append(Tx_Slave_ID)

    TransferPacket.append(Tx_Function_code)
    buf_packet.append(Tx_Function_code)

    TransferPacket.append(Tx_RegisterAddress)
    buf_packet.append(Tx_RegisterAddress)

    TransferPacket.append(Tx_value_of_coil)
    buf_packet.append(Tx_value_of_coil)

    packet_for_CRC = struct.pack(">BBHH", *buf_packet)
    CRC = crc_check(packet_for_CRC, len(packet_for_CRC))
    TransferPacket.append(CRC)

    # Конвертация целочисленного массива в байтовую строку
    Tx = struct.pack(">BBHHH", *TransferPacket)
    lower_byte = Tx[len(Tx) - 1].to_bytes()
    higher_byte = Tx[len(Tx) - 2].to_bytes()
    Tx = Tx[:-2]
    Tx += lower_byte
    Tx += higher_byte

    serial.write(Tx)
    # Проверка порта на наличие в нем данных в течении 1 секунд, если будет пусто, значит вывод ошибки
    Rx = serial.read(100)

    # Считывание длины сообщения в пакете, содержащего необходимые данные
    Rx_packet = struct.unpack(">BBB" + 'H' + 'H', Rx)
    Rx_CRC_rever = hex(Rx_packet[-1])
    Rx_lower_byte = Rx_CRC_rever[2:4]
    Rx_higher_byte = Rx_CRC_rever[4:]
    Rx_CRC = int(Rx_higher_byte + Rx_lower_byte, 16)
    # CRC приходит в реверснутом виде
    if Rx_CRC == crc_check(Rx_packet[:-1], 5):
        return Rx_packet
    else:
        return [0, 0, 0, 0, 0 - 2]


# Запись одного аналогового выхода
def function_06(Tx_Slave_ID, Tx_Function_code, Tx_RegisterAddress, Tx_value_of_coil, serial):
    TransferPacket = []
    buf_packet = []

    # Добавление в массив данных для отправки
    TransferPacket.append(Tx_Slave_ID)
    buf_packet.append(Tx_Slave_ID)

    TransferPacket.append(Tx_Function_code)
    buf_packet.append(Tx_Function_code)

    TransferPacket.append(Tx_RegisterAddress)
    buf_packet.append(Tx_RegisterAddress)

    TransferPacket.append(Tx_value_of_coil)
    buf_packet.append(Tx_value_of_coil)

    packet_for_CRC = struct.pack(">BBHH", *buf_packet)
    CRC = crc_check(packet_for_CRC, len(packet_for_CRC))
    TransferPacket.append(CRC)

    # Конвертация целочисленного массива в байтовую строку
    Tx = struct.pack(">BBHHH", *TransferPacket)
    lower_byte = Tx[len(Tx) - 1].to_bytes()
    higher_byte = Tx[len(Tx) - 2].to_bytes()
    Tx = Tx[:-2]
    Tx += lower_byte
    Tx += higher_byte

    serial.write(Tx)
    # Проверка порта на наличие в нем данных в течении 1 секунд, если будет пусто, значит вывод ошибки
    Rx = serial.readline()

    # Считывание длины сообщения в пакете, содержащего необходимые данные
    Rx_packet = struct.unpack(">BBB" + 'H' + 'H', Rx)
    Rx_CRC_rever = hex(Rx_packet[-1])
    Rx_lower_byte = Rx_CRC_rever[2:4]
    Rx_higher_byte = Rx_CRC_rever[4:]
    Rx_CRC = int(Rx_higher_byte + Rx_lower_byte, 16)
    # CRC приходит в реверснутом виде
    if Rx_CRC == crc_check(Rx_packet[:-1], 5):
        return Rx_packet
    else:
        return [0, 0, 0, 0, 0 - 2]
