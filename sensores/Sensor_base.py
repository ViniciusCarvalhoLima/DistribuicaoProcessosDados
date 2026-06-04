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
            dados_recebidos, endereco = socket_multicast.recvfrom(BUFFER)

            comando_descoberta = Mensagens_pb2.Comando()

            try:
                comando_descoberta.ParseFromString(dados_recebidos)
            except Exception:
                continue

            if comando_descoberta.acao == "DESCOBRIR_SENSORES":
                print(f"[{self.id_sensor}] Descoberta recebida!")

                resposta = Mensagens_pb2.RegistroSensor()
                resposta.id_sensor = self.id_sensor
                resposta.tipo = self.tipo_sensor
                resposta.estado = "ATIVO" if self.ativo else "INATIVO"
                resposta.porta_comando = self.porta_comando

                socket_multicast.sendto(
                    resposta.SerializeToString(),
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

            dados_recebidos = conexao.recv(BUFFER)

            comando_proto = Mensagens_pb2.Comando()
            comando_proto.ParseFromString(dados_recebidos)

            acao = comando_proto.acao.lower()
            parametro = comando_proto.parametro

            resposta_proto = Mensagens_pb2.Resposta()

            if acao == "ligar":
                self.ligar()
                resposta_proto.mensagem = "Sensor ligado com sucesso."

            elif acao == "desligar":
                self.desligar()
                resposta_proto.mensagem = "Sensor desligado com sucesso."

            elif acao == "frequencia":
                try:
                    novo_intervalo = int(parametro)
                    self.intervalo = novo_intervalo

                    self.notificar_gateway(
                        f"FREQUENCIA_ALTERADA|{novo_intervalo}"
                    )

                    resposta_proto.mensagem = (
                        f"Frequência alterada para {novo_intervalo}s."
                    )

                except ValueError:
                    resposta_proto.mensagem = (
                        "Parâmetro inválido. Use: frequencia|N"
                    )

            elif acao == "encerrar":
                resposta_proto.mensagem = "Sensor será encerrado."

                conexao.send(
                    resposta_proto.SerializeToString()
                )

                conexao.close()
                self.encerrar()

            else:
                resposta_proto.mensagem = "Comando inválido."

            conexao.send(
                resposta_proto.SerializeToString()
            )

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
            target=self.iniciar,
            daemon=True
        ).start()

        while True:
            time.sleep(1)
