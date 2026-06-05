import socket
import math
import time
import ast
import sys, os
import subprocess

processos_sensores = {}
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))
import Mensagens_pb2

from shared.Constants import HOST, GATEWAY_TCP_PORT, BUFFER


def formatar_lista_sensores(sensores_registrados):
    if not sensores_registrados:
        return "Nenhum sensor registrado."

    resposta = "\nSensores registrados:\n"

    for id_sensor, dados in sensores_registrados.items():
        resposta += (
            f"\nID: {id_sensor}"
            f"\nTipo: {dados['tipo']}"
            f"\nEstado: {dados['estado']}"
            f"\nIP: {dados['ip']}"
            f"\nPorta comando: {dados['porta_comando']}"
            f"\n"
        )

    return resposta

def criar_sensor(tipo, porta, id_sensor=None):
    tipo = tipo.upper()

    if tipo == "RUIDO":
        caminho_js = os.path.join(os.path.dirname(__file__), '..', 'sensores', 'Sensor_ruido.js')
        args = ["node", caminho_js, porta]
        if id_sensor:
            args.append(id_sensor)
    else:
        tipos_validos = {
            "TEMP": "sensores.Sensor_temperatura",
            "AR": "sensores.Sensor_ar",
        }
        if tipo not in tipos_validos:
            return "Tipo inválido. Use: TEMP, AR ou RUIDO."
        args = [sys.executable, "-m", tipos_validos[tipo], porta]
        if id_sensor:
            args.append(id_sensor)

    try:
        processo = subprocess.Popen(
            args,
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        processos_sensores[porta] = processo
        return f"Sensor {tipo} iniciado na porta {porta}."
    except Exception as e:
        return f"Erro ao iniciar sensor: {e}"
    
def calcular_media(historico, id_sensor, campo):
    if id_sensor not in historico or not historico[id_sensor]:
        return f"Sem dados para {id_sensor}."

    hora_atual = time.time()
    valores = []

    for leitura in historico[id_sensor]:
        if hora_atual - leitura["timestamp"] <= 3600:
            try:
                payload = ast.literal_eval(leitura["payload"])
                
                valor_campo = obter_valor_campo(payload, campo)

                if valor_campo is None:
                    continue

                raw = valor_campo.split()[0]

                raw = raw.replace("°C", "").replace("°", "").replace("%", "")
                valor = float(raw)
                valores.append(valor)
            except Exception:
                pass

    if not valores:
        return f"Sem dados na última hora para {id_sensor}/{campo}."

    media = sum(valores) / len(valores)
    return f"Média de {campo} ({id_sensor}) última hora: {media:.1f} ({len(valores)} leituras)"


def calcular_desvio(historico, id_sensor, campo):
    if id_sensor not in historico or not historico[id_sensor]:
        return f"Sem dados para {id_sensor}."

    hora_atual = time.time()
    valores = []

    for leitura in historico[id_sensor]:
        if hora_atual - leitura["timestamp"] <= 86400:
            try:
                payload = ast.literal_eval(leitura["payload"])

                valor_campo = obter_valor_campo(payload, campo)

                if valor_campo is None:
                    continue

                raw = valor_campo.split()[0]
                raw = raw.replace("°C", "").replace("°", "").replace("%", "")

                valor = float(raw)
                valores.append(valor)
            except Exception:
                pass

    if not valores:
        return f"Sem dados nas últimas 24h para {id_sensor}/{campo}."

    media = sum(valores) / len(valores)
    variancia = sum((x - media) ** 2 for x in valores) / len(valores)
    desvio = math.sqrt(variancia)
    return f"Desvio padrão de {campo} ({id_sensor}) 24h: {desvio:.1f} ({len(valores)} leituras)"


def sensor_maior_variacao(historico, campo):
    if not historico:
        return "Sem dados históricos."

    resultado = {}

    for id_sensor, leituras in historico.items():
        valores = []

        for leitura in leituras:
            try:
                payload = ast.literal_eval(leitura["payload"])

                valor_campo = obter_valor_campo(payload, campo)

                if valor_campo is None:
                    continue

                raw = valor_campo.split()[0]
                raw = raw.replace("°C", "").replace("°", "").replace("%", "")

                valor = float(raw)
                valores.append(valor)

            except Exception:
                pass

        if len(valores) >= 2:
            resultado[id_sensor] = max(valores) - min(valores)

    if not resultado:
        return f"Dados insuficientes para calcular variação de {campo}."

    sensor = max(resultado, key=resultado.get)

    return (
        f"Sensor com maior variação em {campo}: "
        f"{sensor} (variação: {resultado[sensor]:.1f})"
    )


def enviar_comando_para_sensor(sensores_registrados, id_sensor, comando):
    if id_sensor not in sensores_registrados:
        return "Sensor não encontrado."

    dados_sensor = sensores_registrados[id_sensor]

    if dados_sensor["estado"] == "DESCONECTADO":
        return "Não foi possível enviar comando. Sensor desconectado."

    porta_comando = dados_sensor["porta_comando"]
    ip_sensor = dados_sensor["ip"]

    try:
        conexao_sensor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexao_sensor.connect((ip_sensor, porta_comando))

        comando_proto = Mensagens_pb2.Comando()
        comando_proto.id_sensor = id_sensor

        if comando.startswith("frequencia|"):
            partes_comando = comando.split("|")
            comando_proto.acao = "frequencia"
            comando_proto.parametro = partes_comando[1]
        else:
            comando_proto.acao = comando
            comando_proto.parametro = ""

        conexao_sensor.send(comando_proto.SerializeToString())

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


def processar_mensagem_cliente(mensagem, sensores_registrados, historico):
    partes = mensagem.split("|")
    acao = partes[0].upper()

    if acao == "LISTAR":
        return formatar_lista_sensores(sensores_registrados)
    
    elif acao == "MEDIA":
        if len(partes) < 3:
            return "Formato inválido. Use: MEDIA|ID_SENSOR|CAMPO"
        return calcular_media(historico, partes[1], partes[2])
    
    elif acao == "DESVIO":
        if len(partes) < 3:
            return "Formato inválido. Use: DESVIO|ID_SENSOR|CAMPO"
        return calcular_desvio(historico, partes[1], partes[2])
    
    elif acao == "MAIOR_VARIACAO":
        if len(partes) < 2:
            return "Formato inválido. Use: MAIOR_VARIACAO|CAMPO"
        return sensor_maior_variacao(historico, partes[1])
    
    elif acao == "DESLIGAR_TODOS":
        return desligar_todos_sensores(sensores_registrados)
    
    elif acao == "LIGAR_TODOS":
        return ligar_todos_sensores(sensores_registrados)
    
    elif acao == "CRIAR_SENSOR":
        if len(partes) < 3:
            return "Formato inválido. Use: CRIAR_SENSOR|TIPO|PORTA|ID"
        id_sensor = partes[3] if len(partes) > 3 else None
        return criar_sensor(partes[1], partes[2], id_sensor)
    
    elif acao == "COMANDO":
        if len(partes) < 3:
            return "Formato inválido. Use: COMANDO|ID_SENSOR|COMANDO"
        id_sensor = partes[1]
        comando = "|".join(partes[2:]).lower()
        return enviar_comando_para_sensor(sensores_registrados, id_sensor, comando)
    else:
        return "Comando inválido para o Gateway."


def iniciar_servidor_tcp(sensores_registrados, historico):
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

        if cmd.parametro:
            mensagem = f"{cmd.acao}|{cmd.id_sensor}|{cmd.parametro}"
        elif cmd.id_sensor:
            mensagem = f"{cmd.acao}|{cmd.id_sensor}"
        else:
            mensagem = cmd.acao

        print(f"\nCliente conectado: {endereco}")
        print(f"Mensagem recebida: {mensagem}")

        resultado = processar_mensagem_cliente(mensagem, sensores_registrados, historico)

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

        resposta = enviar_comando_para_sensor(sensores_registrados, id_sensor, "desligar")
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

        resposta = enviar_comando_para_sensor(sensores_registrados, id_sensor, "ligar")
        respostas += f"\n{id_sensor}: {resposta}"

    return respostas

def obter_valor_campo(payload, campo):
    for chave, valor in payload.items():
        if chave.lower() == campo.lower():
            return valor

    return None