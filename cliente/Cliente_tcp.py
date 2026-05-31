import socket

from shared.Constants import (
    HOST,
    GATEWAY_TCP_PORT,
    BUFFER
)


def enviar_mensagem_gateway(mensagem):
    cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        cliente.connect(
            (HOST, GATEWAY_TCP_PORT)
        )

        cliente.send(
            mensagem.encode()
        )

        resposta = cliente.recv(BUFFER).decode()

        return resposta

    except ConnectionRefusedError:
        return "Erro: não foi possível conectar ao Gateway."

    except Exception as erro:
        return f"Erro na comunicação com o Gateway: {erro}"

    finally:
        cliente.close()