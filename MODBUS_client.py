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
    elif Rx_packet == 11:
        print("Проблема при подключении, возможно, устройство отключено")
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


def function_03_04(Tx_Slave_ID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddress, Client_socket):
    TransferPacket = [0, 0]
    # Добавление в массив данных для отправки
    TransferPacket.append(6)
    TransferPacket.append(Tx_Slave_ID)
    TransferPacket.append(Tx_Function_code)
    TransferPacket.append(Tx_RegisterAddress)
    TransferPacket.append(Tx_NumberAddress)

    # Конвертация целочисленного массива в байтовую строку
    Tx = struct.pack(">HHHBBHH", *TransferPacket)
    Client_socket.send(Tx)

    # Проверка сокета на наличие в нем данных в течении 0,5 секунд, если будет пусто, значит вывод ошибки
    ready = select.select([Client_socket], [], [], 0.5)
    if ready[0]:
        Rx = Client_socket.recv(4096)
    else:
        return -2

    # Считывание длины сообщения в пакете, содержащего необходимые данные
    Rx_additional_len_bin = str(Rx[4]) + str(Rx[5])
    Rx_additional_len = int((Rx_additional_len_bin), 16)
    Rx_packet = struct.unpack(">HHHBBB" + 'H' * ((Rx_additional_len - 3) // 2), Rx)
    return Rx_packet
