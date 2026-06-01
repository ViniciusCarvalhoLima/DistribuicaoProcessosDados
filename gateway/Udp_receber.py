# Recebe dados dos sensores.
import socket

from shared.Constants import (
    GATEWAY_UDP_PORT,
    BUFFER
)


def iniciar_udp_receiver():
    socket_udp = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    socket_udp.bind(("127.0.0.1", GATEWAY_UDP_PORT))

    print(f"[GATEWAY UDP] Aguardando dados na porta {GATEWAY_UDP_PORT}...")

    while True:
        dados, endereco = socket_udp.recvfrom(BUFFER)

        mensagem = dados.decode()

        print(f"\n[GATEWAY UDP] Dados recebidos: {endereco}:")
        print(mensagem)