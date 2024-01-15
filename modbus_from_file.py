from MODBUS_client import create_socket, print_error, function_03_04

def from_bin_to_dec(x):
    s = ""
    while x > 0:
        s += x / 2 + s
        x = x // 2
    return x


# Создание сокета для обмена информацией с эмулятором
Client_socket = create_socket('127.0.0.1', 502)
amperage = []
relays_adresses = []
optrons_adresses = []
relays = []
optrons = []

with open("registers.txt") as file:
    # считывание количества регистров из файла
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
        amperage[i].append(file.readline().removesuffix("\n"))

with open("Relays_optrons.txt") as file:
    quantity_of_rel_reg = int(file.readline().removesuffix("\n"))
    for i in range(quantity_of_rel_reg):
        string = file.readline().removesuffix("\n")
        relays_adresses.append([string, 0, 0, 0])

    quantity_of_opt_reg = int(file.readline().removesuffix("\n"))
    for i in range(quantity_of_opt_reg):
        string = file.readline().removesuffix("\n")
        optrons_adresses.append([string, 0, 0, 0])

    file.readline()

    quantity_of_rel = int(file.readline().removesuffix("\n").removeprefix("Relays_"))
    for i in range(quantity_of_rel):
        string = file.readline().removesuffix("\n")
        relays.append([string, 0, 0, 0])

    file.readline()

    quantity_of_opt = int(file.readline().removesuffix("\n").removeprefix("Optrons_"))
    for i in range(quantity_of_opt):
        string = file.readline().removesuffix("\n")
        optrons.append([string, 0, 0, 0])

# разделение адресов регистров и названий оптронов и реле
numbers = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

for i in range(quantity_of_rel):
    relays[i][0] = relays[i][0].removeprefix("Control.Relay")
    num_relay = ""
    for letter in relays[i][0]:
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
            relays[i][0] = relays[i][0][length + 2:]
            break

for i in range(quantity_of_opt):
    optrons[i][0] = optrons[i][0].removeprefix("Control.Optron")
    num_optron = ""
    for letter in optrons[i][0]:
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
            optrons[i][0] = optrons[i][0][length + 2:]
            break

for i in range(quantity_of_rel_reg):
    name = ""
    for letter in relays_adresses[i][0]:
        if letter in numbers:
            relays_adresses[i][3]=int(letter)
        if letter == '-':
            relays_adresses[i][1] = int(relays_adresses[i][0][len(name) + 1:], 16)
            relays_adresses[i][0] = name
            break
        name += letter

for i in range(quantity_of_opt_reg):
    name = ""
    for letter in optrons_adresses[i][0]:
        if letter in numbers:
            optrons_adresses[i][3]=int(letter)
        if letter == '-':
            optrons_adresses[i][1] = int(optrons_adresses[i][0][len(name) + 1:], 16)
            optrons_adresses[i][0] = name
            break
        name += letter

# разделение адресов регистров и названий токов
for i in range(quantity_of_registers):
    k = 0
    name_register = ""
    for letter in amperage[i][0]:
        name_register += letter
        k += 1
        if letter == '-':
            name_register = name_register.removesuffix(" -")
            adress = int(amperage[i][0][k + 1:], 16)
            amperage[i][0] = name_register
            amperage[i].append(adress)
            amperage[i].append(0)
            break

if Client_socket != 0:
    # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
    # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
    Tx_SlaveID = 1
    Tx_Function_code = 4
    Tx_NumberAddresses = 1
    # считывание значений токов из эмулятора
    for i in range(quantity_of_registers):
        Tx_RegisterAddress = amperage[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses, Client_socket)
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

    # считывание состояний реле из эмулятора
    for i in range(quantity_of_rel_reg):
        Tx_RegisterAddress = relays_adresses[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses, Client_socket)
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
    # считывание состояний оптронов из эмулятора
    for i in range(quantity_of_opt_reg):
        Tx_RegisterAddress = optrons_adresses[i][1]
        Rx_packet = function_03_04(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses, Client_socket)
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

# Запись значений состояний реле из десятиричного числа
for i in range(quantity_of_rel_reg):
    for j in range(quantity_of_rel):
        if relays_adresses[i][3] == relays[j][1]:
            relays[j][3] = (relays_adresses[i][2] & 2**relays[j][2]) >> relays[j][2]
# Запись значений состояний оптронов из десятиричного числа
for i in range(quantity_of_opt_reg):
    for j in range(quantity_of_opt):
        if optrons_adresses[i][3] == optrons[j][1]:
            optrons[j][3] = (optrons_adresses[i][2] & 2**optrons[j][2]) >> optrons[j][2]

with open("results.txt", 'w') as file:
    file.write("Значения токов: \n")
    for i in range(quantity_of_registers):
        file.write(f"{amperage[i][0]} = {amperage[i][2]}А\n")
    file.write("\nСостояния реле: \n")
    for i in range(quantity_of_rel):
        file.write(f"{relays[i][0]} состояние - {relays[i][3]} \n")
    file.write("\nСостояния оптронов: \n")
    for i in range(quantity_of_opt):
        file.write(f"{optrons[i][0]} состояние - {optrons[i][3]} \n")
print(relays)
print(optrons)
print(amperage)
