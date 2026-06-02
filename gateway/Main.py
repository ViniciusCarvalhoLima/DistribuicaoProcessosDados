import socket
import time
import threading

from shared.Constants import (
    MULTICAST_GROUP,
    MULTICAST_PORT,
    BUFFER
)

from gateway.Tcp_server import iniciar_servidor_tcp
from gateway.Udp_receber import iniciar_udp_receiver

sensores_registrados = {}


def registrar_sensor(resposta_sensor):
    try:
        id_sensor, tipo_sensor, estado_sensor, porta_comando = resposta_sensor.split("|")

        sensores_registrados[id_sensor] = {
            "tipo": tipo_sensor,
            "estado": estado_sensor,
            "porta_comando": int(porta_comando),
            "ultimo_contato": time.time()
        }

    except ValueError:
        print(f"Resposta inválida recebida: {resposta_sensor}")


def descobrir_sensores():
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

    socket_gateway.settimeout(3)

    mensagem = "DESCOBRIR_SENSORES"

    socket_gateway.sendto(
        mensagem.encode(),
        (MULTICAST_GROUP, MULTICAST_PORT)
    )

    inicio = time.time()

    while time.time() - inicio < 3:
        try:
            resposta, endereco = socket_gateway.recvfrom(BUFFER)
            resposta = resposta.decode()

            registrar_sensor(resposta)

        except socket.timeout:
            break

    socket_gateway.close()


def atualizar_estado_sensores():
    tempo_atual = time.time()

    for id_sensor, dados in sensores_registrados.items():
        tempo_sem_resposta = tempo_atual - dados["ultimo_contato"]

        if tempo_sem_resposta > 10:
            dados["estado"] = "DESCONECTADO"


def exibir_sensores_registrados():
    print("\nSensores registrados:")

    if not sensores_registrados:
        print("- Nenhum sensor registrado")
        return

    for id_sensor, dados in sensores_registrados.items():
        print(
            f"- {id_sensor} | "
            f"Tipo: {dados['tipo']} | "
            f"Estado: {dados['estado']} | "
            f"Porta comando: {dados['porta_comando']}"
        )


def iniciar_gateway():
    print("\nGateway Inteligente iniciado.")
    print("Descoberta multicast ativa.\n")

    threading.Thread(
        target=iniciar_servidor_tcp,
        args=(sensores_registrados,),
        daemon=True
    ).start()

    threading.Thread(
        target=iniciar_udp_receiver,
        daemon=True
    ).start()

    while True:
        descobrir_sensores()
        atualizar_estado_sensores()
        exibir_sensores_registrados()
        time.sleep(5)

if __name__ == "__main__":
    iniciar_gateway()
    threading.Thread(
    target=iniciar_udp_receiver,
    daemon=True
).start()