import random
import os
import time
import threading

from sensores.Sensor_base import SensorBase


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

                    threading.Thread(
                        target=self.iniciar,
                        daemon=True
                    ).start()

            elif comando == "sair":
                self.desligar()

                print(
                    f"\n[{self.id_sensor}] Encerrando processo...\n"
                )

                os._exit(0)

            else:
                print("\nComando inválido.")

    def executar(self):
        threading.Thread(
            target=self.ouvir_comandos,
            daemon=True
        ).start()

        threading.Thread(
            target=self.ouvir_descoberta,
            daemon=True
        ).start()

        threading.Thread(
            target=self.iniciar,
            daemon=True
        ).start()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    sensor = SensorTemperatura()
    sensor.executar()