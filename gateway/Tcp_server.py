import socket
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))
import Mensagens_pb2

from shared.Constants import (
    HOST,
    GATEWAY_TCP_PORT,
    BUFFER
)


def formatar_lista_sensores(sensores_registrados):
    if not sensores_registrados:
        return "Nenhum sensor registrado."

    resposta = "\nSensores registrados:\n"

    for id_sensor, dados in sensores_registrados.items():
        resposta += (
            f"\nID: {id_sensor}"
            f"\nTipo: {dados['tipo']}"
            f"\nEstado: {dados['estado']}"
            f"\nPorta comando: {dados['porta_comando']}"
            f"\nÚltimo contato: {dados['ultimo_contato']}"
            f"\n"
        )

    return resposta


def enviar_comando_para_sensor(sensores_registrados, id_sensor, comando):
    if id_sensor not in sensores_registrados:
        return "Sensor não encontrado."

    dados_sensor = sensores_registrados[id_sensor]

    if dados_sensor["estado"] == "DESCONECTADO":
        return "Não foi possível enviar comando. Sensor desconectado."

    porta_comando = dados_sensor["porta_comando"]

    try:
        conexao_sensor = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        conexao_sensor.connect(
            (HOST, porta_comando)
        )

        comando_proto = Mensagens_pb2.Comando()
        comando_proto.id_sensor = id_sensor

        if comando.startswith("frequencia|"):
            partes_comando = comando.split("|")
            comando_proto.acao = "frequencia"
            comando_proto.parametro = partes_comando[1]

        else:
            comando_proto.acao = comando
            comando_proto.parametro = ""

        conexao_sensor.send(
            comando_proto.SerializeToString()
        )

        dados_resposta = conexao_sensor.recv(BUFFER)

        resposta_proto = Mensagens_pb2.Resposta()
        resposta_proto.ParseFromString(dados_resposta)

        conexao_sensor.close()

        if comando == "desligar":
            dados_sensor["estado"] = "INATIVO"

        elif comando == "ligar":
            dados_sensor["estado"] = "ATIVO"

        return resposta_proto.mensagem

    except ConnectionRefusedError:
        dados_sensor["estado"] = "DESCONECTADO"
        return "Erro: sensor não está aceitando conexão."

    except Exception as erro:
        return f"Erro ao enviar comando para sensor: {erro}"


def processar_mensagem_cliente(mensagem, sensores_registrados):
    partes = mensagem.split("|")

    acao = partes[0].upper()

    if acao == "LISTAR":
        return formatar_lista_sensores(sensores_registrados)

    elif acao == "DESLIGAR_TODOS":
        return desligar_todos_sensores(sensores_registrados)
    
    elif acao == "LIGAR_TODOS":
        return ligar_todos_sensores(sensores_registrados)

    elif acao == "COMANDO":
        if len(partes) < 3:
            return "Formato inválido. Use: COMANDO|ID_SENSOR|COMANDO"

        id_sensor = partes[1]
        comando = "|".join(partes[2:]).lower()

        return enviar_comando_para_sensor(
            sensores_registrados,
            id_sensor,
            comando
        )

    else:
        return "Comando inválido para o Gateway."


def iniciar_servidor_tcp(sensores_registrados):
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))
    import Mensagens_pb2

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, GATEWAY_TCP_PORT))
    servidor.listen()

    print(f"Gateway TCP escutando na porta {GATEWAY_TCP_PORT}")

    while True:
        cliente, endereco = servidor.accept()
        dados = cliente.recv(BUFFER)

        cmd = Mensagens_pb2.Comando()
        cmd.ParseFromString(dados)

        # reconstrói mensagem no formato interno
        if cmd.parametro:
            mensagem = f"{cmd.acao}|{cmd.id_sensor}|{cmd.parametro}"
        elif cmd.id_sensor:
            mensagem = f"{cmd.acao}|{cmd.id_sensor}"
        else:
            mensagem = cmd.acao

        print(f"\nCliente conectado: {endereco}")
        print(f"Mensagem recebida: {mensagem}")

        resultado = processar_mensagem_cliente(mensagem, sensores_registrados)

        resp = Mensagens_pb2.Resposta()
        resp.mensagem = resultado
        cliente.send(resp.SerializeToString())
        cliente.close()

def desligar_todos_sensores(sensores_registrados):
    if not sensores_registrados:
        return "Nenhum sensor registrado."

    respostas = "\nResultado ao desligar sensores:\n"

    for id_sensor, dados in sensores_registrados.items():
        if dados["estado"] == "DESCONECTADO":
            respostas += f"\n{id_sensor}: já está desconectado."
            continue

        resposta = enviar_comando_para_sensor(
            sensores_registrados,
            id_sensor,
            "desligar"
        )

        respostas += f"\n{id_sensor}: {resposta}"

    return respostas

def ligar_todos_sensores(sensores_registrados):
    if not sensores_registrados:
        return "Nenhum sensor registrado."

    respostas = "\nResultado ao ligar sensores:\n"

    for id_sensor, dados in sensores_registrados.items():
        if dados["estado"] == "DESCONECTADO":
            respostas += f"\n{id_sensor}: não foi possível ligar, sensor desconectado."
            continue

        resposta = enviar_comando_para_sensor(
            sensores_registrados,
            id_sensor,
            "ligar"
        )

        respostas += f"\n{id_sensor}: {resposta}"

    return respostas