from modbusRTU_client import connect_to_serial_port, print_error, function_03_04, crc_check
import struct
from datetime import datetime
import os

def create_log(name, value, type):
    if os.path.getsize('logs.txt') > 100 * 1024 * 1024:
        open('logs.txt', 'w+')

    with open('logs.txt', 'a', encoding='UTF-8') as file:
        if type == 'a':
            file.write(f"Ток:\t\t {name}\t Значение: {value} A\t  Время - {datetime.now().date()} {datetime.now().hour}:"
                       f"{datetime.now().minute}:{datetime.now().second} \n")
        elif type == 'r':
            file.write(f"Реле:\t\t {name}\t Значение: {value}\t Время - {datetime.now().date()} {datetime.now().hour}:"
                       f"{datetime.now().minute}:{datetime.now().second} \n")
        elif type == 'w':
            if value == 1:
                file.write(f"Предупр.:\t {name}\t Значение: {value}\t Время - {datetime.now().date()} {datetime.now().hour}:"
                       f"{datetime.now().minute}:{datetime.now().second} !!! \n")
            elif value == 0:
                file.write(f"Предупр.:\t {name}\t Значение: {value}\t Время - {datetime.now().date()} {datetime.now().hour}:"
                       f"{datetime.now().minute}:{datetime.now().second} \n")
        elif type == 'o':
            file.write(f"Оптрон:\t\t {name}\t Значение: {value}\t Время - {datetime.now().date()} {datetime.now().hour}:"
                       f"{datetime.now().minute}:{datetime.now().second} \n")


def read_registers_adress_from_file_into_array():
    with open("registers.txt", encoding='UTF-8') as file:
        # считывание количества регистров из файла
        amperage = []
        string = file.readline()
        n1 = ""
        for sign in string:
            if sign == '_':
                k = len(n1)
                quantity_of_registers = int(string[k + 1:])
            n1 += sign
        # считывание строк с названием и адресом регистров из файла
        for i in range(quantity_of_registers):
            amperage.append([])
            k = 0
            name_register = ""
            file_string = file.readline().removesuffix("\n")
            for letter in file_string:
                name_register += letter
                k += 1
                if letter == '-':
                    name_register = name_register.removesuffix(" -")
                    adress = int(file_string[k + 1:], 16)
                    amperage[i].append(name_register)
                    amperage[i].append(adress)
                    amperage[i].append(0)
                    break
        return amperage


def read_opt_rel_warn_from_file_into_arrays():
    relays_adresses = []
    optrons_adresses = []
    warnings_adresses = []
    relays = []
    optrons = []
    warnings = []
    numbers = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    with open("Relays_optrons.txt", encoding='UTF-8') as file:
        quantity_of_rel_reg = int(file.readline().removesuffix("\n"))
        for i in range(quantity_of_rel_reg):
            relays_adresses.append([0, 0, 0, 0])
            string = file.readline().removesuffix("\n")
            name = ""
            for letter in string:
                if letter in numbers:
                    relays_adresses[i][3] = int(letter)
                if letter == '-':
                    relays_adresses[i][1] = int(string[len(name) + 1:], 16)
                    relays_adresses[i][0] = name
                    break
                name += letter

        quantity_of_opt_reg = int(file.readline().removesuffix("\n"))
        for i in range(quantity_of_opt_reg):
            optrons_adresses.append([0, 0, 0, 0])
            string = file.readline().removesuffix("\n")
            name = ""
            for letter in string:
                if letter in numbers:
                    optrons_adresses[i][3] = int(letter)
                if letter == '-':
                    optrons_adresses[i][1] = int(string[len(name) + 1:], 16)
                    optrons_adresses[i][0] = name
                    break
                name += letter

        quantity_of_warn_reg = int(file.readline().removesuffix("\n"))
        for i in range(quantity_of_warn_reg):
            warnings_adresses.append([0, 0, 0, 0])
            string = file.readline().removesuffix("\n")
            name = ""
            for letter in string:
                if letter in numbers:
                    warnings_adresses[i][3] = int(letter)
                if letter == '-':
                    warnings_adresses[i][1] = int(string[len(name) + 1:], 16)
                    warnings_adresses[i][0] = name
                    break
                name += letter

        file.readline()

        quantity_of_rel = int(file.readline().removesuffix("\n").removeprefix("Relays_"))
        for i in range(quantity_of_rel):
            relays.append([0, 0, 0, 0])
            string = file.readline().removesuffix("\n").removeprefix("Control.Relay")
            num_relay = ""
            for letter in string:
                if letter in numbers:
                    num_relay += letter
                    continue
                elif letter == "_":
                    relays[i][1] = int(num_relay)
                    num_relay = ""
                    continue
                elif letter == " ":
                    relays[i][2] = int(num_relay)
                    length = len(str(relays[i][1]) + str(relays[i][2]))
                    relays[i][0] = string[length + 2:]
                    break

        file.readline()

        quantity_of_opt = int(file.readline().removesuffix("\n").removeprefix("Optrons_"))
        for i in range(quantity_of_opt):
            optrons.append([0, 0, 0, 0])
            string = file.readline().removesuffix("\n").removeprefix("Control.Optron")
            num_optron = ""
            for letter in string:
                if letter in numbers:
                    num_optron += letter
                    continue
                elif letter == "_":
                    optrons[i][1] = int(num_optron)
                    num_optron = ""
                    continue
                elif letter == " ":
                    optrons[i][2] = int(num_optron)
                    length = len(str(optrons[i][1]) + str(optrons[i][2]))
                    optrons[i][0] = string[length + 2:]
                    break

        file.readline()

        quantity_of_warn = int(file.readline().removesuffix("\n").removeprefix("Неисправности_"))
        for i in range(quantity_of_warn):
            warnings.append([0, 0, 0, 0])
            string = file.readline().removesuffix("\n").removeprefix("Control.WarningBuff_")
            num_warning = ""
            for letter in string:
                if letter in numbers:
                    num_warning += letter
                    continue
                elif letter == "_":
                    warnings[i][1] = int(num_warning)
                    num_warning = ""
                    continue
                elif letter == " ":
                    warnings[i][2] = int(num_warning)
                    length = len(str(warnings[i][1]) + str(warnings[i][2]))
                    warnings[i][0] = string[length + 2:]
                    break

    return optrons, optrons_adresses, relays, relays_adresses, warnings, warnings_adresses


def get_configurations_from_modbus(first_adress, quantity_adresses, serial):
    if serial != 0:
        # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
        Tx_SlaveID = 1
        Tx_Function_code = 4
        Tx_NumberAddresses = quantity_adresses
    else:
        return 0
    # считывание значений токов из устройства
    Tx_RegisterAddress = first_adress
    Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses,
                               serial)
    Rx_MODBUS_address = Rx_packet[0]
    Rx_MODBUS_function = Rx_packet[1]
    Rx_Byte_count = Rx_packet[2]
    Rx_Register_values = Rx_packet[3:-1]

    if type(Rx_packet) == int or Rx_packet[1] != Tx_Function_code:
        print_error(Rx_packet)
    else:
        sirius_id = Rx_Register_values[0]

        #Перевод формата 0xEF05, где EF <-год 05 <-месяц
        buildDate = Rx_Register_values[1]

        build_year = int(round(buildDate/10000, 2) * 100 + 2000)
        build_month = buildDate % 100

        configuration = Rx_Register_values[2]

        version_hex = f'{Rx_Register_values[3]:x}'
        version_buf = f'0x{version_hex:0>4}'
        version = str(version_buf[2:4] + '.' + version_buf[4:])
        return sirius_id, build_year, build_month, configuration, version


def get_arr_amperage_from_modbus(amperage, first_adress, quantity_of_amperage_registers, serial, quantity_adresses):
    if serial != 0:
        # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
        Tx_SlaveID = 1
        Tx_Function_code = 4
        Tx_NumberAddresses = quantity_adresses
    else:
        return 0
    # считывание значений токов из устройства
    Tx_RegisterAddress = first_adress
    Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses,
                               serial)
    Rx_MODBUS_address = Rx_packet[0]
    Rx_MODBUS_function = Rx_packet[1]
    Rx_Byte_count = Rx_packet[2]
    Rx_Register_values = Rx_packet[3:-1]


    if type(Rx_packet) == int or Rx_packet[1] != Tx_Function_code:
        print_error(Rx_packet)
    else:
        for i in range(quantity_of_amperage_registers):
            number = Rx_Register_values[i*2]
            amperage[i][2] = number / 100
            create_log(amperage[i][0], amperage[i][2],'a')
    return amperage


def get_arr_relays_from_modbus(relays_adresses, quantity_of_rel_reg, quantity_of_rel, relays, serial):
    if serial != 0:
        # Example = [6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        Tx_SlaveID = 1
        Tx_Function_code = 4
        Tx_NumberAddresses = 1
    else:
        return 0
    # считывание состояний реле из эмулятора
    for i in range(quantity_of_rel_reg):
        Tx_RegisterAddress = relays_adresses[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses, serial)
        if type(Rx_packet) == int or Rx_packet[1] != Tx_Function_code:
            print_error(Rx_packet)
        else:
            Rx_MODBUS_address = Rx_packet[0]
            Rx_MODBUS_function = Rx_packet[1]
            Rx_Byte_count = Rx_packet[2]
            Rx_Register_value = Rx_packet[3:-1]

            number = Rx_Register_value[0]
            relays_adresses[i][2] = number
            # Запись значений состояний реле из десятиричного числа
            for j in range(quantity_of_rel):
                if relays_adresses[i][3] == relays[j][1]:
                    relays[j][3] = (relays_adresses[i][2] & 2 ** relays[j][2]) >> relays[j][2]
                    create_log(relays[j][0], relays[j][3],'r')
    return relays


def get_arr_optrons_from_modbus(optrons_adresses, quantity_of_opt_reg, quantity_of_opt, optrons, serial):
    if serial != 0:
        # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву
        Tx_SlaveID = 1
        Tx_Function_code = 4
        Tx_NumberAddresses = 1
    else:
        return 0
    # считывание состояний оптронов из эмулятора
    for i in range(quantity_of_opt_reg):
        Tx_RegisterAddress = optrons_adresses[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses, serial)
        if type(Rx_packet) == int or Rx_packet[1] != Tx_Function_code:
            print_error(Rx_packet)
        else:
            Rx_MODBUS_address = Rx_packet[0]
            Rx_MODBUS_function = Rx_packet[1]
            Rx_Byte_count = Rx_packet[2]
            Rx_Register_value = Rx_packet[3:-1]

            number = Rx_Register_value[0]
            optrons_adresses[i][2] = number
        # Запись значений состояний оптронов из десятиричного числа
        for j in range(quantity_of_opt):
            if optrons_adresses[i][3] == optrons[j][1]:
                optrons[j][3] = (optrons_adresses[i][2] & 2 ** optrons[j][2]) >> optrons[j][2]
                create_log(optrons[j][0], optrons[j][3],'o')
    return optrons


def get_arr_warnings_from_modbus(warning_adresses, quantity_of_warn_reg, quantity_of_warn, warnings, serial):
    if serial != 0:
        # Example = [1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id

        Tx_SlaveID = 1
        Tx_Function_code = 3
        Tx_value_of_coil = 4

        # считывание состояний оптронов из эмулятора
        Tx_RegisterAddress = warning_adresses[0][1]

        # Добавление в массив данных для отправки
        TransferPacket = []
        buf_packet = []

        # Добавление в массив данных для отправки
        TransferPacket.append(Tx_SlaveID)
        buf_packet.append(Tx_SlaveID)

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

        # Проверка сокета на наличие в нем данных в течении 0,5 секунд, если будет пусто, значит вывод ошибки

        Rx = serial.read(100)

        # Считывание длины сообщения в пакете, содержащего необходимые данные
        Rx_additional_len_bin = str(Rx[2])
        Rx_additional_len = int((Rx_additional_len_bin), 16)
        Rx_packet = struct.unpack(">BBBHHHHH", Rx)

        if type(Rx_packet) == int or Rx_packet[1] != Tx_Function_code:
            print_error(Rx_packet)
        else:
            Rx_MODBUS_address = Rx_packet[0]
            Rx_MODBUS_function = Rx_packet[1]
            Rx_Byte_count = Rx_packet[2]
            Rx_Register_values = Rx_packet[3:-1]

            warning_adresses[0][2] = Rx_Register_values
        # Запись значений состояний оптронов из десятиричного числа
        for k in range(4):
            for j in range(16):
                warnings[k*16 + j][3] = (warning_adresses[0][2][k] & 2 ** warnings[j][2]) >> warnings[j][2]
                create_log(warnings[j][0],warnings[j][3],'w')
                if k == 3:
                    g =[]
                if k*16 + j == quantity_of_warn-1:
                    break
        return warnings

'''
serial = connect_to_serial_port("COM2")

amperage = read_registers_adress_from_file_into_array()

quantity_of_amperage_registers = len(amperage)

optrons, optrons_adresses, relays, relays_adresses, warnings, warnings_adresses = read_opt_rel_warn_from_file_into_arrays()

first_adress = amperage[0][1]
second_adress = amperage[-1][1]

quantity_adresses = second_adress - first_adress + 1
print(quantity_adresses)
'''
'''
quantity_of_rel = len(relays)
quantity_of_rel_reg = len(optrons_adresses)
quantity_of_opt = len(optrons)
quantity_of_opt_reg = len(optrons_adresses)

relays_with_values_from_modbus = get_arr_relays_from_modbus(relays_adresses, quantity_of_rel_reg, quantity_of_rel, relays, serial)
print(relays_with_values_from_modbus)
optrons_with_values_from_modbus = get_arr_optrons_from_modbus(optrons_adresses, quantity_of_opt_reg, quantity_of_opt, optrons, serial)
print(optrons_with_values_from_modbus)

amperage_with_values_from_modbus = get_arr_amperage_from_modbus(first_adress, quantity_of_amperage_registers, serial,
                                                                quantity_adresses)
print(amperage)

with open("results.txt", 'w') as file:
    file.write("Значения токов: \n")
    for i in range(quantity_of_amperage_registers):
        file.write(f"{amperage_with_values_from_modbus[i][0]} = {amperage_with_values_from_modbus[i][2]} А\n")
    file.write("\nСостояния реле: \n")
    for i in range(quantity_of_rel):
        file.write(f"{relays_with_values_from_modbus[i][0]} состояние - {relays_with_values_from_modbus[i][3]} \n")
    file.write("\nСостояния оптронов: \n")
    for i in range(quantity_of_opt):
        file.write(f"{optrons_with_values_from_modbus[i][0]} состояние - {optrons_with_values_from_modbus[i][3]} \n")
'''
