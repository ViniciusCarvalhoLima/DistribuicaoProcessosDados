import time
from abc import ABC, abstractmethod
import socket
import struct
import threading


class SensorBase(ABC):
    contador_sensores = 0

    def __init__(self, tipo_sensor, intervalo=5):
        SensorBase.contador_sensores += 1

        self.id_sensor = (
            f"{tipo_sensor}_{SensorBase.contador_sensores:02d}"
        )

        self.tipo_sensor = tipo_sensor
        self.intervalo = intervalo
        self.ativo = True
        
    def iniciar(self):
        print(f"\n[{self.id_sensor}] Sensor iniciado.\n")

        while self.ativo:
            dados = self.gerar_dados()
            self.exibir_dados(dados)

            time.sleep(self.intervalo)

    def desligar(self):
        self.ativo = False
        print(f"\n[{self.id_sensor}] Sensor desligado.\n")

    @abstractmethod
    def gerar_dados(self):
        pass

    def exibir_dados(self, dados):
        print(f"[{self.id_sensor}] {dados}")



    def ouvir_descoberta(self):
        socket_multicast = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )

        socket_multicast.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        socket_multicast.bind(("", 5002))

        grupo = socket.inet_aton("224.1.1.1")

        mreq = struct.pack("4sL", grupo, socket.INADDR_ANY)

        socket_multicast.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            mreq
        )

        print(
            f"[{self.id_sensor}] Escutando descoberta multicast..."
        )

        while True:
            mensagem, endereco = socket_multicast.recvfrom(1024)

            mensagem = mensagem.decode()

            if mensagem == "DESCOBRIR_SENSORES":
                print(f"[{self.id_sensor}] Descoberta recebida!")

                resposta = (
                    f"{self.id_sensor}|"
                    f"{self.tipo_sensor}|"
                    f"{'ATIVO' if self.ativo else 'INATIVO'}"
                )

                socket_multicast.sendto(
                    resposta.encode(),
                    endereco
                )

