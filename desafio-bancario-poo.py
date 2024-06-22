import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


def menu():
    menu = """\n
    ######### BANCO BANQUITO ##########
    ############## MENU ###############
    [1]\tDepósito
    [2]\tSaque
    [3]\tExtrato Bancário
    [4]\tCriar Conta
    [5]\tListar Contas
    [6]\tCliente Novo
    [7]\tSair
    => """
    return input(textwrap.dedent(menu))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "5":
            listar_contas(contas)

        elif opcao == "6":
            criar_cliente(clientes)

        elif opcao == "7":
            break

        else: 
            print("\n!!!! Opção inválida! Favor informar uma das opções válidas em nosso menu inicial. !!!!")

def depositar(clientes):
    cpf = input("Informe o CPF do cliente da conta: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n**** Cliente não encontrado com o CPF informado! ****")
        return

    valor = float(input("Informe o valor para depósito em conta: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do cliente da conta: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!!! Cliente não econtrado com o CPF informado! !!!!")
        return
    
    valor = float(input("Informar valor do saque a ser efetuado: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente da conta: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!!! Cliente não localizado com o CPF informado! !!!!")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("\n########## EXTRATO BANCÁRIO ##########")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações recentes nesta conta."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}" 
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("#########################################")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente da conta: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n!!!! Cliente não encontrado com os dados informados, favor realizar nova tentativa. !!!!")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n#### Nova conta criada com sucesso! ####")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def criar_cliente(clientes):
    cpf = input("Informe o CPF (Somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n!!!! Cliente já existente com o CPF Informado! !!!!")
        return
    
    nome = input("Informe nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    endereco = input("Informar endereço do cliente da conta (rua, número, bairro, CEP, cidade/UF): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n#### Novo cliente criado com sucesso na base de dados! ####")

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n!!!! Cliente informado não possui conta bancária! !!!!")
        return
    
    # FIXME: não permite a escolha de conta pelo cliente.
    return cliente.contas[0]

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = [] 

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property       
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        saldo_excedido = valor > saldo

        if saldo_excedido:
            print("\n!!!! Erro na operação! Saldo insuficiente para prosseguir. !!!!")
        
        elif valor > 0:
            self._saldo -= valor
            print("\n#### Saque realizado com sucesso! ####")
            return True
        
        else:
            print("\n!!!! Erro na operação! O valor informado não e válido para executar a operação. !!!!")

        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n#### Depósito concluído! ####")
        else:
            print("\n!!!! Operação inválida! O valor informado não e válido. !!!!")
            return False
        
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )
           
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n!!!! Erro na operação! O valor do saque excedeu limite permitido para esta conta. !!!!")

        elif excedeu_saques:
            print("\n!!!! Erro na operação! Número máximo de saques permitidos foi atingido. !!!!")

        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """
    
class Historico:
    def __init__(self):
        self._transacoes = []

    @property 
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y"),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor 
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

main()

# datetime alterado em Class Historico, o formato utilizado durante a aula de reoslução não atendia.
# datetime alterado somente para o formato dd/mm/aaaa .



