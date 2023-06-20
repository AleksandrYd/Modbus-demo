import socket, struct, select


def create_socket(ip, port):
    Client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создание сокета для приема
    try:
        Client_socket.connect((ip, port))  # Подключение созданного сокета к сокету слэйва
        return Client_socket
    except ConnectionRefusedError:
        print_error(11)
        return 0


def print_error(Rx_packet):  # Функция, выводящая на экран название ошибки
    if Rx_packet == -1:
        print("Error read single coil status")
    elif Rx_packet == -2:
        print("Timeout error or connection was lost")
    else:
        error_code = Rx_packet[5]
        match error_code:
            case 1:
                print("Принятый код функции не может быть обработан.")
            case 2:
                print("Адрес данных, указанный в запросе, недоступен.")
            case 3:
                print("Значение, содержащееся в поле данных запроса, является недопустимой величиной.")
            case 4:
                print("Невосстанавливаемая ошибка имела место, пока ведомое устройство "
                      "пыталось выполнить затребованное действие.")
            case 5:
                print("Ведомое устройство приняло запрос и обрабатывает его, но это требует много времени.")
            case 6:
                print("Ведомое устройство занято обработкой команды. Ведущее устройство должно повторить "
                      "сообщение позже, когда ведомое освободится.")
            case 7:
                print("Ведомое устройство не может выполнить программную функцию, заданную в запросе. "
                      "Этот код возвращается для не успешного программного запроса, "
                      "использующего функции с номерами 13 или 14. Ведущее устройство должно запросить "
                      "диагностическую информацию или информацию об ошибках от ведомого.")
            case 8:
                print("Ведомое устройство при чтении расширенной памяти обнаружило ошибку паритета. "
                      "Ведущее устройство может повторить запрос, но обычно в таких случаях требуется ремонт.")
            case 10:
                print("Шлюз неправильно настроен или перегружен запросами.")
            case 11:
                print("Slave устройства нет в сети или от него нет ответа.")


def print_rxpacket_01(Rx_register_values, first_address, numberAddress):
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
            if number_of_coil > numberAddress - 1:
                break


def function_01(Tx_Slave_ID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddress):
    # Добавление в массив данных для отправки
    TransferPacket.append(6)
    TransferPacket.append(Tx_Slave_ID)
    TransferPacket.append(Tx_Function_code)
    TransferPacket.append(Tx_RegisterAddress)
    TransferPacket.append(Tx_NumberAddress)

    # Конвертация целочисленного массива в байтовую строку
    Tx = struct.pack(">HHHBBHH", *TransferPacket)
    Client_socket.send(Tx)

    # Проверка сокета на наличие в нем данных в течение 0,5 секунд, если будет пусто, значит вывод ошибки
    ready = select.select([Client_socket], [], [], 0.5)
    if ready[0]:
        Rx = Client_socket.recv(4096)
    else:
        return -2

    # Считывание длины сообщения в пакете, содержащего необходимые данные
    Rx_additional_len_bin = str(Rx[4]) + str(Rx[5])
    Rx_additional_len = int((Rx_additional_len_bin), 16)
    Rx_packet = struct.unpack(">HHHBBB" + 'B' * (Rx_additional_len - 3), Rx)
    return Rx_packet


# Создание сокета для обмена информацией с эмулятором
Client_socket = create_socket('127.0.0.1', 502)

if Client_socket != 0:
   # Example = [0, 0, 6, 1, 1, 0, 5] - Пример пакета для modbus в целочисленном формате
   # Cоздание пакета для отправки слэйву с предзаданным transfer id, transaction id
    TransferPacket = [0, 0]
    print("Введите адрес устройства...")
    Tx_SlaveID = int(input())
    print("Введите код функции...")
    Tx_Function_code = int(input())

    match Tx_Function_code:
        case 1:
            print("Вы хотите считать дискретные выводы.")
            print("Введите адрес регистра...")
            Tx_RegisterAddress = int(input())
            print("Введите количество регистров")
            Tx_NumberAddresses = int(input())

            Rx_packet = function_01(Tx_SlaveID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddresses)

            # Если возвращен не целочисленный список с данными (код ошибки)
            # или изменен код функции (тоже случай пакета с ошибкой)
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

                print_rxpacket_01(Rx_Register_value, Tx_RegisterAddress, Tx_NumberAddresses)
        case _:
            print("Мы пока не знаем таких функций :(")

    Client_socket.close()
