import time
from abc import ABC, abstractmethod


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