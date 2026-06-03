import socket
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'proto'))
import Mensagens_pb2



from shared.Constants import GATEWAY_UDP_PORT, BUFFER


def iniciar_udp_receiver(sensores_registrados):
    
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_udp.bind(("127.0.0.1", GATEWAY_UDP_PORT))

    print(f"[GATEWAY UDP] Aguardando dados na porta {GATEWAY_UDP_PORT}...")

    while True:
        dados, endereco = socket_udp.recvfrom(BUFFER)
        print(f"[DEBUG] de {endereco}: {dados[:50]}")  # ← aqui

        msg = Mensagens_pb2.DadosSensor()
        msg.ParseFromString(dados)

        print(f"\n[GATEWAY UDP] {msg.id_sensor} | {msg.tipo} | {msg.payload}")

        try:
            if msg.id_sensor in sensores_registrados:
                sensores_registrados[msg.id_sensor]["ultimo_contato"] = time.time()
                if sensores_registrados[msg.id_sensor]["estado"] != "INATIVO":
                    sensores_registrados[msg.id_sensor]["estado"] = "ATIVO"
        except Exception:
            pass