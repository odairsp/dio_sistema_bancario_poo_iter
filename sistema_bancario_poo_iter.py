from abc import ABC, abstractmethod
from datetime import datetime, timezone
import textwrap

class ContaIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            conta = self.contas[self._index]
            return f"""
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        """
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1

class Cliente:
    def __init__(self, endereco):
        
        self.endereco = endereco
        self.contas = []
   
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self,conta):
        self.contas.append(conta)
    
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._data_nascimento = data_nascimento
        self._cpf = cpf
    @property
    def cpf(self):
        return self._cpf
    @property
    def nome(self):
        return self._nome
    @property
    def data_nascimento(self):
        return self._data_nascimento

class Conta:
    
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

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
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"\n-- Depósito de R$ {valor:.2f} realizado com sucesso! --")
            return True
        else:
            print("\n-- ERRO - Valor inválido! Repita a operação! --")
        return False
    
    def sacar(self, valor):
        saldo = self.saldo
        sem_saldo = valor > saldo
        if sem_saldo:
            print(f"\n-- ERRO - Saldo = R$ {saldo:.2f} insuficiente! Digite outro valor! --")
            
        elif valor > 0:
            self._saldo -= valor
            print(f"\n-- Saque de R$ {valor:.2f} realizado com sucesso! --")
            return True
        
        else:  
            print("\n-- ERRO - Valor inválido! Repita a operação! --")
        return False   
        
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in 
             self._historico.transacoes if 
             transacao["tipo"] == Saque.__name__]
        )
        
        passou_saques = numero_saques >= self._limite_saques
        passou_limite = valor > self._limite
        
        if passou_limite:
            print(f"\n-- ERRO - Valor acima do limite de R$ {self._limite:.2f}.! Digite outro valor! --")
        elif passou_saques:
            print(f"\n-- ERRO - Excedeu quantidade de {self._limite_saques} saques diários! --")
        
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self) -> str:
        return f"""
            Agência:\t{self.agencia}
            C/C\t\t{self.numero}
            Titular\t{self.cliente.nome}
            {"-"*50}
        """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now(timezone.utc).strftime("%d/%m/%Y,%H:%M:%S"),
        })
        
    def tansacoes_do_dia(self):
        data_hoje = datetime.now(timezone.utc).date()
        transasoes_dia = [transacao for transacao in self._transacoes if datetime.strptime(transacao["data"],"%d/%m/%Y,%H:%M:%S" ).date() == data_hoje ]
    
        return transasoes_dia
    
    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao
       
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
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
        sucesso_transacao = conta.depositar(self._valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def log_decorador(funcao):
    def decora(*args, **kwargs):
        name_function =  str.join(" ",str.split(funcao.__name__, sep="_"))
        funcao(*args, **kwargs)
        print(f"{datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")} - {name_function.title()}", end="\n\n")
        input(" Press Enter para voltar! ".center(50, "-"))
    return decora
    
def menu(): 

    clientes = []
    contas = []

    menu =f"""\n
    {" BEM VINDO! ".center(50,"-")}\n
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [q] SAIR
    
    [nu] Novo Usuário
    [nc] Nova Conta
    [lc] Listar Contas
 
    Escolha uma opção => """
    return input(textwrap.dedent(menu))

def verifica_cliente(cpf, clientes):
    cliente = [cliente for cliente in clientes if cliente.cpf == cpf]
    return cliente[0] if cliente else None

def verifica_conta_cliente(cliente):
    if not cliente.contas:
        print(f"\n-- ERRO - Cliente: {cliente.nome}, não possui conta. --")
        input(" Press Enter para voltar! ".center(50, "-"))
        return
    return cliente.contas[0]

@log_decorador
def sacar(clientes):
    print(" SACAR ".center(50,"-")+"\n")
    cpf = input("Digite o CPF do cliente: => ")
    cliente = verifica_cliente(cpf, clientes)

    if not cliente:
        print("\n-- ERRO - Cliente não encontrado! --")
        return
    valor = float(input("Digite o valor para saque: => "))
    transacao = Saque(valor)  
    
    conta = verifica_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)
    
@log_decorador
def depositar(clientes):
    print(" DEPOSITAR ".center(50,"-")+"\n")
    cpf = input("Digite o CPF do cliente: => ")
    cliente = verifica_cliente(cpf, clientes)

    if not cliente:
        print("\n-- ERRO - Cliente não encontrado! --")
        return
    valor = float(input("Digite o valor para depósito: => "))
    transacao = Deposito(valor)  
    
    conta = verifica_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)
    
@log_decorador
def ver_extrato(clientes):
    print(" EXTRATO ".center(50,"-")+"\n")
    cpf = input("Digite o CPF do cliente: => ")
    cliente = verifica_cliente(cpf, clientes)

    if not cliente:
        print("\n-- ERRO - Cliente não encontrado! --")
        return
   
    conta: Conta = verifica_conta_cliente(cliente)
    if not conta:
        return
    print(" EXTRATO ".center(50,"-")+"\n")
    transacoes = conta.historico.transacoes
    extrato = ""
    if not transacoes:
        extrato = "\n-- Não foram feitas transações nesta conta. --"
    else: 
        menu = f"""
        Escolha o tipo de extrato: 
        
        [1] Depósitos
        [2] Saques
        [3] Todos
        
        => 
        """
        tipos_extratos = {"1": "deposito", "2":"saque", "3": None }
        tipo_extrato = input(textwrap.dedent(menu))

        for transacao in conta.historico.gerar_relatorio(tipos_extratos[tipo_extrato] if tipo_extrato in tipos_extratos else None):
            extrato += f"{transacao["data"]}\t {transacao["tipo"]}: ".ljust(35)+f"R$ {transacao["valor"]:.2f}".rjust(15)+"\n"
    print(extrato)
    print(f"{"".center(50, "-")}\nSaldo:\n\tR$ {conta.saldo:.2f}")
    
@log_decorador
def novo_cliente(clientes): 
    print(" CRIAR CLIENTE ".center(50,"-")+"\n")
    cpf = input("Digite o CPF do cliente: => ")
    cliente = verifica_cliente(cpf, clientes)

    if cliente:
        print("ERRO - CPF já cadastrado!")
        return
    nome = input("Nome completo: => ").title()
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): => ")
    endereco = input("Endereco (rua, nro - bairro - cidade/sigla estado)")

    cliente = PessoaFisica(nome=nome,data_nascimento=data_nascimento,cpf=cpf,endereco=endereco)
    clientes.append(cliente)
    print(f"\n-- Cliente '{nome.title()}', criado com sucesso! --")
   
@log_decorador   
def nova_conta(numero_conta, clientes, contas):
    cpf = input("Digite o CPF do cliente: => ")
    cliente = verifica_cliente(cpf, clientes)

    if not cliente:
        print("ERRO - Cliente não encontrado!")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n-- Conta criada com sucesso! --")
    
@log_decorador
def listar_contas(contas):
    print(f"\n{" Contas Cadastradas! ".center(50, "-")}")
    
    for conta in ContaIterador(contas):
        print(textwrap.dedent(str(conta)))
    
    
def program():
    clientes = []
    contas = []

    while True:
        print()        
        opcao = menu()
        
        if opcao == "d":
            depositar(clientes)            
            
        elif opcao == "s":
            sacar(clientes)
                
        elif opcao == "e":
            ver_extrato(clientes)  
            
        elif opcao == "nu":
            novo_cliente(clientes)
            
        elif opcao == "nc":
            numero_conta = len(contas)+1
            nova_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            
            listar_contas(contas)

        elif opcao == "q":
            break
            
        
        else:
            print("Opção inválida, tente novamente!")
        
    print("Obrigado por usar nosso sistema!\n")

program()
