from cliente.Cliente_tcp import enviar_mensagem_gateway



def exibir_menu():
    print("\n===== Cliente Analítico =====")
    print("1 - Listar sensores conectados")
    print("2 - Enviar comando para sensor")
    print("3 - Desligar todos os sensores")
    print("4 - Ligar todos os sensores")
    print("5 - Sair")

def listar_sensores():
    resposta = enviar_mensagem_gateway("LISTAR")
    print(resposta)


def enviar_comando():
    id_sensor = input("\nDigite o ID do sensor: ")

    print("\nComandos disponíveis:")
    print("- ligar")
    print("- frequencia|N  (ex: frequencia|5)")
    print("- desligar")
    print("- encerrar")

    comando = input("\nDigite o comando: ")

    mensagem = f"COMANDO|{id_sensor}|{comando}"

    resposta = enviar_mensagem_gateway(mensagem)

    print(f"\nResposta: {resposta}")


def iniciar_cliente():
    while True:
        exibir_menu()

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            listar_sensores()

        elif opcao == "2":
            enviar_comando()

        elif opcao == "3":
            desligar_todos_sensores()

        elif opcao == "4":
            ligar_todos_sensores()

        elif opcao == "5":
            print("\nEncerrando Cliente Analítico...")
            break

        else:
            print("\nOpção inválida.")

def desligar_todos_sensores():
    resposta = enviar_mensagem_gateway("DESLIGAR_TODOS")
    print(resposta)

def ligar_todos_sensores():
    resposta = enviar_mensagem_gateway("LIGAR_TODOS")
    print(resposta)


if __name__ == "__main__":
    iniciar_cliente()