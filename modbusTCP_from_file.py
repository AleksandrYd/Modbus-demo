from modbusTCP_client import create_socket, print_error, function_03_04
import struct, select

def read_registers_adress_from_file_into_array():
    with open("registers.txt") as file:
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
    with open("Relays_optrons.txt") as file:
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


def get_arr_amperage_from_modbus(amperage, quantity_of_amperage_registers, client_socket):
    if client_socket != 0:
        # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
        Tx_SlaveID = 1
        Tx_Function_code = 4
        Tx_NumberAddresses = 1
    else:
        return 0
        # считывание значений токов из эмулятора
    for i in range(quantity_of_amperage_registers):
        Tx_RegisterAddress = amperage[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses,
                                   client_socket)
        if type(Rx_packet) == int or Rx_packet[4] != Tx_Function_code:
            print_error(Rx_packet)
        else:
            Rx_Transaction_ID = Rx_packet[0]
            Rx_Protocol_ID = Rx_packet[1]
            Rx_Message_length = Rx_packet[2]
            Rx_MODBUS_address = Rx_packet[3]
            Rx_MODBUS_function = Rx_packet[4]
            Rx_Byte_count = Rx_packet[5]
            Rx_Register_value = Rx_packet[6:]
            number = Rx_Register_value[0]
            amperage[i][2] = number / 100
    return amperage


def get_arr_relays_from_modbus(relays_adresses, quantity_of_rel_reg, quantity_of_rel, relays, client_socket):
    if client_socket != 0:
            # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
            # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
            Tx_SlaveID = 1
            Tx_Function_code = 4
            Tx_NumberAddresses = 1
    else:
        return 0
    # считывание состояний реле из эмулятора
    for i in range(quantity_of_rel_reg):
        Tx_RegisterAddress = relays_adresses[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses, client_socket)
        if type(Rx_packet) == int or Rx_packet[4] != Tx_Function_code:
            print_error(Rx_packet)
        else:
            Rx_Transaction_ID = Rx_packet[0]
            Rx_Protocol_ID = Rx_packet[1]
            Rx_Message_length = Rx_packet[2]
            Rx_MODBUS_address = Rx_packet[3]
            Rx_MODBUS_function = Rx_packet[4]
            Rx_Byte_count = Rx_packet[5]
            Rx_Register_value = Rx_packet[6:]

            number = Rx_Register_value[0]
            relays_adresses[i][2] = number
        # Запись значений состояний реле из десятиричного числа
            for j in range(quantity_of_rel):
                if relays_adresses[i][3] == relays[j][1]:
                    relays[j][3] = (relays_adresses[i][2] & 2 ** relays[j][2]) >> relays[j][2]
    return relays


def get_arr_optrons_from_modbus(optrons_adresses, quantity_of_opt_reg, quantity_of_opt, optrons, client_socket):
    if client_socket != 0:
        # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
        Tx_SlaveID = 1
        Tx_Function_code = 4
        Tx_NumberAddresses = 1
    else:
        return 0
    # считывание состояний оптронов из эмулятора
    for i in range(quantity_of_opt_reg):
        Tx_RegisterAddress = optrons_adresses[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses, client_socket)
        if type(Rx_packet) == int or Rx_packet[4] != Tx_Function_code:
            print_error(Rx_packet)
        else:
            Rx_Transaction_ID = Rx_packet[0]
            Rx_Protocol_ID = Rx_packet[1]
            Rx_Message_length = Rx_packet[2]
            Rx_MODBUS_address = Rx_packet[3]
            Rx_MODBUS_function = Rx_packet[4]
            Rx_Byte_count = Rx_packet[5]
            Rx_Register_value = Rx_packet[6:]

            number = Rx_Register_value[0]
            optrons_adresses[i][2] = number
        # Запись значений состояний оптронов из десятиричного числа
        for j in range(quantity_of_opt):
            if optrons_adresses[i][3] == optrons[j][1]:
                optrons[j][3] = (optrons_adresses[i][2] & 2 ** optrons[j][2]) >> optrons[j][2]
    return optrons


def get_arr_warnings_from_modbus(warning_adresses, quantity_of_warn_reg, quantity_of_warn, warnings, client_socket):
    if client_socket != 0:
        # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
        # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
        # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
        Tx_SlaveID = 1
        Tx_Function_code = 4
        Tx_NumberAddresses = 4

        # считывание состояний оптронов из эмулятора
        Tx_RegisterAddress = warning_adresses[0][1]

        # Добавление в массив данных для отправки
        TransferPacket = [0, 0]
        TransferPacket.append(6)
        TransferPacket.append(Tx_SlaveID)
        TransferPacket.append(Tx_Function_code)
        TransferPacket.append(Tx_RegisterAddress)
        TransferPacket.append(Tx_NumberAddresses)

        # Конвертация целочисленного массива в байтовую строку
        Tx = struct.pack(">HHHBBHH", *TransferPacket)

        client_socket.send(Tx)

        # Проверка сокета на наличие в нем данных в течении 0,5 секунд, если будет пусто, значит вывод ошибки
        ready = select.select([client_socket], [], [], 0.5)
        if ready[0]:
            Rx = client_socket.recv(4096)
        else:
            print('blin')

        # Считывание длины сообщения в пакете, содержащего необходимые данные
        Rx_additional_len_bin = str(Rx[4]) + str(Rx[5])
        Rx_additional_len = int((Rx_additional_len_bin), 16)
        Rx_packet = struct.unpack(">HHHBBBQ", Rx)


        if type(Rx_packet) == int or Rx_packet[4] != Tx_Function_code:
            print_error(Rx_packet)
        else:
            Rx_Transaction_ID = Rx_packet[0]
            Rx_Protocol_ID = Rx_packet[1]
            Rx_Message_length = Rx_packet[2]
            Rx_MODBUS_address = Rx_packet[3]
            Rx_MODBUS_function = Rx_packet[4]
            Rx_Byte_count = Rx_packet[5]
            Rx_Register_value = Rx_packet[6:]

            number = Rx_Register_value[0]
            warning_adresses[0][2] = number
        # Запись значений состояний оптронов из десятиричного числа
        for j in range(quantity_of_warn):
            warnings[j][3] = (warning_adresses[0][2] & 2 ** warnings[j][2]) >> warnings[j][2]
        return warnings

'''
client_socket = create_socket('127.0.0.1', 502)

amperage = read_registers_adress_from_file_into_array()
quantity_of_amperage_registers = len(amperage)

optrons, optrons_adresses, relays_adresses, relays = read_opt_rel_from_file_into_arrays()
quantity_of_rel = len(relays)
quantity_of_rel_reg = len(optrons_adresses)
quantity_of_opt = len(optrons)
quantity_of_opt_reg = len(optrons_adresses)

relays_with_values_from_modbus = get_arr_relays_from_modbus(relays_adresses, quantity_of_rel_reg, quantity_of_rel, relays, client_socket)
optrons_with_values_from_modbus = get_arr_optrons_from_modbus(optrons_adresses, quantity_of_opt_reg, quantity_of_opt, optrons, client_socket)
amperage_with_values_from_modbus = get_arr_amperage_from_modbus(amperage, quantity_of_amperage_registers, client_socket)

print(amperage)
'''
'''
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

