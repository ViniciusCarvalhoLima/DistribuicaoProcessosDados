import random

from sensores.Sensor_base import SensorBase
from shared.Constants import PORTA_SENSOR_TEMP


class SensorTemperatura(SensorBase):
    def __init__(self):
        super().__init__(
            tipo_sensor="TEMP",
            intervalo=5,
            porta_comando=PORTA_SENSOR_TEMP
        )

    def gerar_dados(self):
        temperatura = random.randint(25, 35)
        umidade = random.randint(50, 90)

        return {
            "Temperatura": f"{temperatura}°C",
            "Umidade": f"{umidade}%"
        }


if __name__ == "__main__":
    sensor = SensorTemperatura()
    sensor.executar_base()