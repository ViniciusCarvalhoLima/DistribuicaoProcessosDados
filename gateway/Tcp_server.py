import socket

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

        conexao_sensor.send(
            comando.encode()
        )

        resposta_sensor = conexao_sensor.recv(BUFFER).decode()

        conexao_sensor.close()

        return resposta_sensor

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
        if len(partes) != 3:
            return "Formato inválido. Use: COMANDO|ID_SENSOR|COMANDO"

        id_sensor = partes[1]
        comando = partes[2].lower()

        return enviar_comando_para_sensor(
            sensores_registrados,
            id_sensor,
            comando
        )

    else:
        return "Comando inválido para o Gateway."


def iniciar_servidor_tcp(sensores_registrados):
    servidor = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    servidor.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    servidor.bind(
        (HOST, GATEWAY_TCP_PORT)
    )

    servidor.listen()

    print(
        f"Gateway TCP escutando na porta {GATEWAY_TCP_PORT}"
    )

    while True:
        cliente, endereco = servidor.accept()

        mensagem = cliente.recv(BUFFER).decode()

        print(f"\nCliente conectado: {endereco}")
        print(f"Mensagem recebida: {mensagem}")

        resposta = processar_mensagem_cliente(
            mensagem,
            sensores_registrados
        )

        cliente.send(
            resposta.encode()
        )

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