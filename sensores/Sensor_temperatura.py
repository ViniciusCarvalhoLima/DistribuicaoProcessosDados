import random
import sys
import threading

from Sensor_base import SensorBase


class SensorTemperatura(SensorBase):
    def __init__(self):
        super().__init__(
            tipo_sensor="TEMP",
            intervalo=5
        )

    def gerar_dados(self):
        temperatura = random.randint(25, 35)
        umidade = random.randint(50, 90)

        return {
            "Temperatura": f"{temperatura}°C",
            "Umidade": f"{umidade}%"
        }

    def ouvir_comandos(self):
        while True:
            comando = input(
                "\nComando (ligar/desligar/sair): "
            ).lower()

            if comando == "desligar":
                self.desligar()

            elif comando == "ligar":
                if not self.ativo:
                    self.ativo = True
                    threading.Thread(target=self.iniciar).start()

            elif comando == "sair":
                self.desligar()

                print(
                    f"\n[{self.id_sensor}] Encerrando processo...\n"
                )

                sys.exit()

    def executar(self):
        threading.Thread(
            target=self.ouvir_comandos
        ).start()

        self.iniciar()


if __name__ == "__main__":
    sensor = SensorTemperatura()
    sensor.executar()