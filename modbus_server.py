import socket, struct, select


def function_01(Tx_Slave_ID, Tx_Function_code, Tx_RegisterAddress, Tx_NumberAddress):
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
    Rx_packet = struct.unpack(">HHHBBB" + 'B' * (Rx_additional_len - 3), Rx)
    return Rx_packet