const fs = require("fs");
const path = require("path");
const dgram = require("dgram");
const net = require("net");
const protobuf = require("protobufjs");

const caminhoConfig = path.join(__dirname, "..", "shared", "config.json");
const config = JSON.parse(fs.readFileSync(caminhoConfig, "utf8"));

const HOST = config.host;
const GATEWAY_UDP_PORT = config.gateway_udp_port;
const MULTICAST_PORT = config.multicast_port;
const MULTICAST_GROUP = config.multicast_group;
const PORTA_COMANDO = config.sensor_noise_port;

const ID_SENSOR = "ruido_01";
const TIPO_SENSOR = "RUIDO";

let ativo = true;
const intervalo = 5000;

const caminhoProto = path.join(__dirname, "..", "proto", "Mensagens.proto");
const root = protobuf.loadSync(caminhoProto);

const DadosSensor = root.lookupType("DadosSensor");
const Comando = root.lookupType("Comando");
const Resposta = root.lookupType("Resposta");
const RegistroSensor = root.lookupType("RegistroSensor");


function gerarDadosRuido() {
    const ruido = Math.floor(Math.random() * (95 - 40 + 1)) + 40;

    return {
        Ruido: `${ruido} dB`
    };
}


function enviarDadosUdp() {
    if (!ativo) {
        return;
    }

    const dados = gerarDadosRuido();

    console.log(`[${ID_SENSOR}]`, dados);

    const mensagem = DadosSensor.create({
    idSensor: ID_SENSOR,
    tipo: TIPO_SENSOR,
    payload: JSON.stringify(dados)
});

    const buffer = DadosSensor.encode(mensagem).finish();

    const socketUdp = dgram.createSocket("udp4");

    socketUdp.send(
        buffer,
        0,
        buffer.length,
        GATEWAY_UDP_PORT,
        HOST,
        () => {
            socketUdp.close();
        }
    );
}


function iniciarEnvioContinuo() {
    console.log(`\n[${ID_SENSOR}] Sensor de ruído iniciado.\n`);

    setInterval(() => {
        enviarDadosUdp();
    }, intervalo);
}


function iniciarDescobertaMulticast() {
    const socketMulticast = dgram.createSocket({
        type: "udp4",
        reuseAddr: true
    });

    socketMulticast.bind(MULTICAST_PORT, () => {
        socketMulticast.addMembership(MULTICAST_GROUP);

        console.log(
            `[${ID_SENSOR}] Escutando descoberta multicast na porta ${MULTICAST_PORT}...`
        );
    });

    socketMulticast.on("message", (mensagemRecebida, rinfo) => {
        try {
            const comando = Comando.decode(mensagemRecebida);

            if (comando.acao === "DESCOBRIR_SENSORES") {
                console.log(`[${ID_SENSOR}] Descoberta recebida!`);

                const registro = RegistroSensor.create({
                idSensor: ID_SENSOR,
                tipo: TIPO_SENSOR,
                estado: ativo ? "ATIVO" : "INATIVO",
                portaComando: PORTA_COMANDO,
                ip: HOST
            });

                const resposta = RegistroSensor.encode(registro).finish();

                socketMulticast.send(
                    resposta,
                    0,
                    resposta.length,
                    rinfo.port,
                    rinfo.address
                );
            }

        } catch (erro) {
            // Ignora mensagens que não sejam Protobuf válido
        }
    });
}


function iniciarServidorTcpComandos() {
    const servidor = net.createServer((conexao) => {
        conexao.on("data", (dadosRecebidos) => {
            let mensagemResposta = "";

            try {
                const comando = Comando.decode(dadosRecebidos);
                const acao = comando.acao.toLowerCase();

                if (acao === "ligar") {
                    ativo = true;
                    mensagemResposta = "Sensor de ruído ligado com sucesso.";
                    console.log(`[${ID_SENSOR}] Sensor ligado.`);
                }

                else if (acao === "desligar") {
                    ativo = false;
                    mensagemResposta = "Sensor de ruído desligado com sucesso.";
                    console.log(`[${ID_SENSOR}] Sensor desligado.`);
                }

                else if (acao === "encerrar") {
                    mensagemResposta = "Sensor de ruído será encerrado.";

                    const resposta = Resposta.create({
                        mensagem: mensagemResposta
                    });

                    const bufferResposta = Resposta.encode(resposta).finish();

                    conexao.write(bufferResposta, () => {
                        conexao.end();
                        console.log(`[${ID_SENSOR}] Encerrando processo...`);
                        process.exit(0);
                    });

                    return;
                }

                else if (acao === "frequencia") {
                    mensagemResposta = "Comando não suportado. Sensor de ruído não é configurável.";
                }

                else {
                    mensagemResposta = "Comando inválido.";
                }

            } catch (erro) {
                mensagemResposta = "Erro ao processar comando Protobuf.";
            }

            const resposta = Resposta.create({
                mensagem: mensagemResposta
            });

            const bufferResposta = Resposta.encode(resposta).finish();

            conexao.write(bufferResposta);
            conexao.end();
        });
    });

    servidor.listen(PORTA_COMANDO, HOST, () => {
        console.log(
            `[${ID_SENSOR}] Aguardando comandos TCP em ${HOST}:${PORTA_COMANDO}...`
        );
    });
}


function iniciarSensorRuido() {
    iniciarDescobertaMulticast();
    iniciarServidorTcpComandos();
    iniciarEnvioContinuo();
}


iniciarSensorRuido();