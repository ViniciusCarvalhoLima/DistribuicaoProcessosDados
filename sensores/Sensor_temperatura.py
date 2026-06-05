import random
import sys
from sensores.Sensor_base import SensorBase
from shared.Constants import PORTA_SENSOR_TEMP


class SensorTemperatura(SensorBase):
    def __init__(self, porta=PORTA_SENSOR_TEMP, id_sensor=None):
        super().__init__(
            tipo_sensor="TEMP",
            intervalo=5,
            porta_comando=porta
        )
        if id_sensor:
            self.id_sensor = id_sensor

    def gerar_dados(self):
        temperatura = random.randint(25, 35)
        umidade = random.randint(50, 90)
        return {
            "Temperatura": f"{temperatura}°C",
            "Umidade": f"{umidade}%"
        }


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else PORTA_SENSOR_TEMP
    id_sensor = sys.argv[2] if len(sys.argv) > 2 else None
    sensor = SensorTemperatura(porta=porta, id_sensor=id_sensor)
    sensor.executar_base()