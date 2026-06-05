import socket
import time
import threading
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))
import Mensagens_pb2

from shared.Constants import (
    MULTICAST_GROUP,
    MULTICAST_PORT,
    BUFFER
)

from gateway.Tcp_server import iniciar_servidor_tcp
from gateway.Udp_receber import iniciar_udp_receiver

sensores_registrados = {}
historico = {}


def registrar_sensor(registro_sensor):
    sensores_registrados[registro_sensor.id_sensor] = {
        "tipo": registro_sensor.tipo,
        "estado": registro_sensor.estado,
        "ip": registro_sensor.ip,
        "porta_comando": int(registro_sensor.porta_comando),
        "ultimo_contato": time.time()
    }


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

    comando_descoberta = Mensagens_pb2.Comando()
    comando_descoberta.acao = "DESCOBRIR_SENSORES"

    socket_gateway.sendto(
        comando_descoberta.SerializeToString(),
        (MULTICAST_GROUP, MULTICAST_PORT)
    )

    inicio = time.time()

    while time.time() - inicio < 3:
        try:
            dados_recebidos, endereco = socket_gateway.recvfrom(BUFFER)

            registro_sensor = Mensagens_pb2.RegistroSensor()
            registro_sensor.ParseFromString(dados_recebidos)

            registrar_sensor(registro_sensor)

        except socket.timeout:
            break

        except Exception as erro:
            print(f"Erro ao processar resposta multicast: {erro}")

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
            f"IP: {dados['ip']} | "
            f"Porta comando: {dados['porta_comando']}"
        )


def iniciar_gateway():
    print("\nGateway Inteligente iniciado.")
    print("Descoberta multicast ativa.\n")

    threading.Thread(
        target=iniciar_servidor_tcp,
        args=(sensores_registrados, historico),  
        daemon=True
    ).start()

    threading.Thread(
        target=iniciar_udp_receiver,
        args=(sensores_registrados, historico),  
        daemon=True
    ).start()

    while True:
        descobrir_sensores()
        atualizar_estado_sensores()
        exibir_sensores_registrados()
        time.sleep(5)

if __name__ == "__main__":
    iniciar_gateway()