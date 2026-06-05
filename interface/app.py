import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from ttkthemes import ThemedTk

from cliente.Cliente_tcp import enviar_mensagem_gateway


class ClienteGrafico:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Cliente Analítico - Cidade Inteligente")
        self.janela.geometry("920x760")
        self.janela.resizable(False, False)

        self.configurar_estilo()
        self.criar_interface()

    def configurar_estilo(self):
        estilo = ttk.Style()

        estilo.configure("TButton", font=("Segoe UI", 10), padding=6)
        estilo.configure("TLabel", font=("Segoe UI", 10))
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def criar_interface(self):
        container = ttk.Frame(self.janela)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        self.frame_principal = ttk.Frame(canvas, padding=20)

        self.frame_principal.bind(
            "<Configure>",
            lambda evento: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        janela_canvas = canvas.create_window((0, 0), window=self.frame_principal, anchor="n")

        def centralizar_conteudo(evento):
            canvas.itemconfig(janela_canvas, width=920)
            canvas.coords(janela_canvas, evento.width // 2, 0)

        canvas.bind("<Configure>", centralizar_conteudo)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all(
            "<MouseWheel>",
            lambda evento: canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")
        )

        ttk.Label(
            self.frame_principal,
            text="Cliente Analítico - Cidade Inteligente",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(0, 15))

        self.criar_area_sensores(self.frame_principal)
        self.criar_area_criar_sensor(self.frame_principal)
        self.criar_area_comandos(self.frame_principal)
        self.criar_area_comandos_globais(self.frame_principal)
        self.criar_area_consultas(self.frame_principal)
        self.criar_area_resultado(self.frame_principal)

    def criar_area_sensores(self, frame_principal):
        frame = ttk.LabelFrame(frame_principal, text="Sensores", padding=15)
        frame.pack(fill="x", pady=8)

        ttk.Button(
            frame,
            text="Listar sensores conectados",
            command=self.listar_sensores
        ).pack(fill="x")

    def criar_area_criar_sensor(self, frame_principal):
        frame = ttk.LabelFrame(frame_principal, text="Criar novo sensor", padding=15)
        frame.pack(fill="x", pady=8)

        linha_tipo = ttk.Frame(frame)
        linha_tipo.pack(fill="x", pady=5)
        ttk.Label(linha_tipo, text="Tipo:", width=14).pack(side="left")
        self.combo_tipo_sensor = ttk.Combobox(
            linha_tipo, values=["TEMP", "AR", "RUIDO"], state="readonly", width=20
        )
        self.combo_tipo_sensor.pack(side="left")
        self.combo_tipo_sensor.current(0)

        linha_porta = ttk.Frame(frame)
        linha_porta.pack(fill="x", pady=5)
        ttk.Label(linha_porta, text="Porta:", width=14).pack(side="left")
        self.entrada_porta_sensor = ttk.Entry(linha_porta, width=20)
        self.entrada_porta_sensor.pack(side="left")

        linha_id = ttk.Frame(frame)
        linha_id.pack(fill="x", pady=5)
        ttk.Label(linha_id, text="ID (opcional):", width=14).pack(side="left")
        self.entrada_id_sensor = ttk.Entry(linha_id, width=20)
        self.entrada_id_sensor.pack(side="left")

        ttk.Button(frame, text="Criar sensor", command=self.criar_sensor).pack(fill="x", pady=8)

        ttk.Label(
            frame,
            text="Porta deve ser única (ex: 6003, 6004...)",
            font=("Segoe UI", 10)
        ).pack(anchor="w")

    def criar_area_comandos(self, frame_principal):
        frame = ttk.LabelFrame(frame_principal, text="Enviar comando para sensor", padding=15)
        frame.pack(fill="x", pady=8)

        ttk.Label(frame, text="ID do sensor:").grid(row=0, column=0, sticky="w", pady=5)
        self.entrada_sensor = ttk.Entry(frame, width=35)
        self.entrada_sensor.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text="Comando:").grid(row=1, column=0, sticky="w", pady=5)
        self.entrada_comando = ttk.Entry(frame, width=35)
        self.entrada_comando.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(
            frame, text="Enviar comando", command=self.enviar_comando
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(
            frame,
            text="Exemplos: Ligar, Desligar, Encerrar, Frequencia|N",
            font=("Segoe UI", 10)
        ).grid(row=3, column=0, columnspan=2, sticky="w")

        frame.columnconfigure(1, weight=1)

    def criar_area_comandos_globais(self, frame_principal):
        frame = ttk.LabelFrame(frame_principal, text="Comandos globais", padding=15)
        frame.pack(fill="x", pady=8)

        ttk.Button(
            frame, text="Desligar todos os sensores", command=self.desligar_todos
        ).grid(row=0, column=0, padx=5, sticky="ew")

        ttk.Button(
            frame, text="Ligar todos os sensores", command=self.ligar_todos
        ).grid(row=0, column=1, padx=5, sticky="ew")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def criar_area_consultas(self, frame_principal):
        frame = ttk.LabelFrame(frame_principal, text="Consultas analíticas", padding=15)
        frame.pack(fill="x", pady=8)

        linha_sensor = ttk.Frame(frame)
        linha_sensor.pack(fill="x", pady=5)
        ttk.Label(linha_sensor, text="ID do sensor:", width=14).pack(side="left")
        self.entrada_sensor_consulta = ttk.Entry(linha_sensor)
        self.entrada_sensor_consulta.pack(side="left", fill="x", expand=True)

        linha_campo = ttk.Frame(frame)
        linha_campo.pack(fill="x", pady=5)
        ttk.Label(linha_campo, text="Campo:", width=14).pack(side="left")
        self.entrada_campo = ttk.Entry(linha_campo)
        self.entrada_campo.pack(side="left", fill="x", expand=True)

        linha_botoes = ttk.Frame(frame)
        linha_botoes.pack(fill="x", pady=10)

        ttk.Button(linha_botoes, text="Média", command=self.consultar_media).pack(
            side="left", fill="x", expand=True, padx=5
        )
        ttk.Button(linha_botoes, text="Desvio padrão", command=self.consultar_desvio).pack(
            side="left", fill="x", expand=True, padx=5
        )
        ttk.Button(linha_botoes, text="Maior variação", command=self.consultar_maior_variacao).pack(
            side="left", fill="x", expand=True, padx=5
        )

        ttk.Label(
            frame,
            text="Exemplos de campo: Temperatura, Umidade, CO2, COVs, Ruido",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(5, 0))

    def criar_area_resultado(self, frame_principal):
        frame = ttk.LabelFrame(frame_principal, text="Resultado", padding=10)
        frame.pack(fill="both", expand=True, pady=8)

        self.caixa_resultado = ScrolledText(
            frame, height=12, width=90, wrap="word",
            font=("Consolas", 10), bg="white", fg="black"
        )
        self.caixa_resultado.pack(fill="both", expand=True)
        self.mostrar_resposta("Aguardando ação...")

    def mostrar_resposta(self, resposta):
        texto = str(resposta).strip() or "Nenhuma resposta recebida."
        self.caixa_resultado.delete("1.0", tk.END)
        self.caixa_resultado.insert("1.0", texto)
        self.caixa_resultado.see("1.0")
        self.caixa_resultado.update()

    def listar_sensores(self):
        self.mostrar_resposta(enviar_mensagem_gateway("LISTAR"))

    def enviar_comando(self):
        id_sensor = self.entrada_sensor.get().strip()
        comando = self.entrada_comando.get().strip()

        if not id_sensor or not comando:
            self.mostrar_resposta("Informe o ID do sensor e o comando.")
            return

        self.mostrar_resposta(enviar_mensagem_gateway(f"COMANDO|{id_sensor}|{comando}"))

    def desligar_todos(self):
        self.mostrar_resposta(enviar_mensagem_gateway("DESLIGAR_TODOS"))

    def ligar_todos(self):
        self.mostrar_resposta(enviar_mensagem_gateway("LIGAR_TODOS"))

    def criar_sensor(self):
        tipo = self.combo_tipo_sensor.get()
        porta = self.entrada_porta_sensor.get().strip()
        id_sensor = self.entrada_id_sensor.get().strip()

        if not porta:
            self.mostrar_resposta("Informe a porta do sensor.")
            return

        if id_sensor:
            mensagem = f"CRIAR_SENSOR|{tipo}|{porta}|{id_sensor}"
        else:
            mensagem = f"CRIAR_SENSOR|{tipo}|{porta}"

        self.mostrar_resposta(enviar_mensagem_gateway(mensagem))

    def consultar_media(self):
        id_sensor = self.entrada_sensor_consulta.get().strip()
        campo = self.entrada_campo.get().strip()

        if not id_sensor or not campo:
            self.mostrar_resposta("Informe o ID do sensor e o campo.")
            return

        self.mostrar_resposta(enviar_mensagem_gateway(f"MEDIA|{id_sensor}|{campo}"))

    def consultar_desvio(self):
        id_sensor = self.entrada_sensor_consulta.get().strip()
        campo = self.entrada_campo.get().strip()

        if not id_sensor or not campo:
            self.mostrar_resposta("Informe o ID do sensor e o campo.")
            return

        self.mostrar_resposta(enviar_mensagem_gateway(f"DESVIO|{id_sensor}|{campo}"))

    def consultar_maior_variacao(self):
        campo = self.entrada_campo.get().strip()

        if not campo:
            self.mostrar_resposta("Informe o campo para calcular a maior variação.")
            return

        self.mostrar_resposta(enviar_mensagem_gateway(f"MAIOR_VARIACAO|{campo}"))


if __name__ == "__main__":
    janela = ThemedTk(theme="black")
    app = ClienteGrafico(janela)
    janela.mainloop()