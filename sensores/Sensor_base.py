import time
import socket
import struct
import threading
import os
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))
import Mensagens_pb2



from abc import ABC, abstractmethod
from shared.Constants import MULTICAST_GROUP, MULTICAST_PORT, BUFFER, HOST


class SensorBase(ABC):
    contador_sensores = 0

    def __init__(self, tipo_sensor, intervalo=5, porta_comando=6000):
        SensorBase.contador_sensores += 1

        self.id_sensor = f"{tipo_sensor}_{SensorBase.contador_sensores:02d}".lower()
        self.tipo_sensor = tipo_sensor
        self.intervalo = intervalo
        self.porta_comando = porta_comando
        self.ativo = True

    def iniciar(self):
        print(f"\n[{self.id_sensor}] Sensor iniciado.\n")

        while True:
            if self.ativo:
                dados = self.gerar_dados()
                self.exibir_dados(dados)
                self.enviar_dados_udp(dados)


            time.sleep(self.intervalo)

    def desligar(self):
        self.ativo = False
        print(f"\n[{self.id_sensor}] Sensor desligado.\n")

    def enviar_dados_udp(self, dados):

        msg = Mensagens_pb2.DadosSensor()
        msg.id_sensor = self.id_sensor
        msg.tipo = self.tipo_sensor
        msg.payload = str(dados)

        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_udp.sendto(msg.SerializeToString(), ("127.0.0.1", 5001))
        socket_udp.close()

    
    def ligar(self):
        self.ativo = True
        print(f"\n[{self.id_sensor}] Sensor ligado.\n")

    def encerrar(self):
        print(f"\n[{self.id_sensor}] Encerrando processo...\n")
        os._exit(0)

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

        socket_multicast.bind(("", MULTICAST_PORT))

        grupo = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack("4sL", grupo, socket.INADDR_ANY)

        socket_multicast.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            mreq
        )

        print(f"[{self.id_sensor}] Escutando descoberta multicast...")

        while True:
            mensagem, endereco = socket_multicast.recvfrom(BUFFER)
            mensagem = mensagem.decode()

            if mensagem == "DESCOBRIR_SENSORES":
                print(f"[{self.id_sensor}] Descoberta recebida!")

                resposta = (
                    f"{self.id_sensor}|"
                    f"{self.tipo_sensor}|"
                    f"{'ATIVO' if self.ativo else 'INATIVO'}|"
                    f"{self.porta_comando}"
                )

                socket_multicast.sendto(
                    resposta.encode(),
                    endereco
                )

    def ouvir_comandos_tcp(self):
        servidor = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        servidor.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        servidor.bind((HOST, self.porta_comando))
        servidor.listen()

        print(
            f"[{self.id_sensor}] Aguardando comandos TCP na porta {self.porta_comando}..."
        )

        while True:
            conexao, endereco = servidor.accept()

            comando = conexao.recv(BUFFER).decode().lower()

            if comando == "ligar":
                self.ligar()
                resposta = "Sensor ligado com sucesso."

            elif comando == "desligar":
                self.desligar()
                resposta = "Sensor desligado com sucesso."

            elif comando.startswith("frequencia|"):
                try:
                    novo_intervalo = int(comando.split("|")[1])
                    self.intervalo = novo_intervalo
                    self.notificar_gateway(f"FREQUENCIA_ALTERADA|{novo_intervalo}")
                    resposta = f"Frequência alterada para {novo_intervalo}s."
                except (IndexError, ValueError):
                    resposta = "Formato inválido. Use: frequencia|N"

            elif comando == "encerrar":
                resposta = "Sensor será encerrado."
                conexao.send(resposta.encode())
                conexao.close()
                self.encerrar()

            else:
                resposta = "Comando inválido."

            conexao.send(resposta.encode())
            conexao.close()

    def notificar_gateway(self, evento):
        try:
            msg = Mensagens_pb2.DadosSensor()
            msg.id_sensor = self.id_sensor
            msg.tipo = self.tipo_sensor
            msg.payload = evento

            socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_udp.sendto(msg.SerializeToString(), ("127.0.0.1", 5001))
            socket_udp.close()
            print(f"[{self.id_sensor}] Notificação enviada: {evento}")
        except Exception as e:
            print(f"[{self.id_sensor}] Erro ao notificar gateway: {e}")

    def executar_base(self):
        threading.Thread(
            target=self.ouvir_descoberta,
            daemon=True
        ).start()

        threading.Thread(
            target=self.ouvir_comandos_tcp,
            daemon=True
        ).start()

        threading.Thread(
            target=self.ouvir_comandos_locais,
            daemon=True
        ).start()

        threading.Thread(
            target=self.iniciar,
            daemon=True
        ).start()

        while True:
            time.sleep(1)

    def ouvir_comandos_locais(self):
        while True:
            comando = input(
                "\nComando local (ligar/desligar/sair): "
            ).lower()

            if comando == "ligar":
                self.ligar()

            elif comando == "desligar":
                self.desligar()

            elif comando == "sair":
                self.encerrar()

            else:
                print("\nComando inválido.")