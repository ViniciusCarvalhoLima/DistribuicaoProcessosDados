# Ponto principal do Gateway, iniciar TCP iniciar UDP iniciar multicast iniciar registro.import socket
import socket
import time

from shared.Constants import (
    MULTICAST_GROUP,
    MULTICAST_PORT
)


socket_gateway = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
    socket.IPPROTO_UDP
)

socket_gateway.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_MULTICAST_TTL,
    2
)

mensagem = "DESCOBRIR_SENSORES"

socket_gateway.sendto(
    mensagem.encode(),
    (MULTICAST_GROUP, MULTICAST_PORT)
)

print("\nProcurando sensores...\n")

socket_gateway.settimeout(5)

sensores_encontrados = []

inicio = time.time()

while time.time() - inicio < 5:
    try:
        resposta, endereco = socket_gateway.recvfrom(1024)

        resposta = resposta.decode()

        sensores_encontrados.append(resposta)

    except socket.timeout:
        break

print("Sensores encontrados:\n")

for sensor in sensores_encontrados:
    print(sensor)