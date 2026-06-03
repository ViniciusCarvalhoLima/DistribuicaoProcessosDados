import socket
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))
import Mensagens_pb2

from shared.Constants import HOST, GATEWAY_TCP_PORT, BUFFER


def enviar_mensagem_gateway(mensagem):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, GATEWAY_TCP_PORT))

        cmd = Mensagens_pb2.Comando()
        partes = mensagem.split("|")
        cmd.acao = partes[0]
        cmd.id_sensor = partes[1] if len(partes) > 1 else ""
        cmd.parametro = "|".join(partes[2:]) if len(partes) > 2 else ""

        cliente.send(cmd.SerializeToString())

        dados = cliente.recv(BUFFER)
        resp = Mensagens_pb2.Resposta()
        resp.ParseFromString(dados)

        return resp.mensagem

    except ConnectionRefusedError:
        return "Erro: não foi possível conectar ao Gateway."
    except Exception as erro:
        return f"Erro na comunicação com o Gateway: {erro}"
    finally:
        cliente.close()