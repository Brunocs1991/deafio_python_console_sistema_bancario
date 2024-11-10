import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class Client:
    def __init__(self, address):
        self.address = address
        self.accounts: list[Account] = []

    def perform_transaction(self, account, transaction):
        transaction.register(account)

    def add_account(self, account):
        self.accounts.append(account)


class NaturalPerson(Client):
    def __init__(self, name, date_of_birth, cpf, address):
        super().__init__(address)
        self.name = name
        self.date_of_birth = date_of_birth
        self.cpf = cpf


class Account:
    def __init__(self, number, client):
        self._balance = 0
        self._number = number
        self._agency = "0001"
        self._client = client
        self._history = History()

    @classmethod
    def new_account(cls, client, number):
        return cls(number, client)

    @property
    def balance(self):
        return self._balance

    @property
    def number(self):
        return self._number

    @property
    def agency(self):
        return self._agency

    @property
    def client(self):
        return self._client

    @property
    def history(self):
        return self._history

    def withdraw(self, value):
        balance = self.balance
        exceeded_balance = value > balance

        if exceeded_balance:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        elif value > 0:
            self._balance -= value
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False

    def deposit(self, value):
        if value > 0:
            self._balance += value
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        return True


class CurrentAccount(Account):
    def __init__(self, number, client, limit=500, limit_withdraw=3):
        super().__init__(number, client)
        self._limit = limit
        self._limit_withdraw = limit_withdraw

    def withdraw(self, value):
        number_withdraw = len(
            [transaction for transaction in self.history.transactions if transaction["tipo"] == Withdraw.__name__]
        )

        exceeded_limit = value > self._limit
        exceeded_withdraw = number_withdraw >= self._limit_withdraw

        if exceeded_limit:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif exceeded_withdraw:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().withdraw(value)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agency}
            C/C:\t\t{self.number}
            Titular:\t{self.client.name}
        """


class History:
    def __init__(self):
        self._transactions = []

    @property
    def transactions(self):
        return self._transactions

    def add_transaction(self, transaction):
        self._transactions.append(
            {
                "tipo": transaction.__class__.__name__,
                "valor": transaction.value,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transaction(ABC):
    @property
    def value(self):
        pass

    @staticmethod
    def register(self, account):
        pass


class Withdraw(Transaction):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def register(self, account):
        success_transaction = account.withdraw(self.value)

        if success_transaction:
            account.history.add_transaction(self)


class Deposit(Transaction):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def register(self, account):
        success_transaction = account.deposit(self.value)

        if success_transaction:
            account.history.add_transaction(self)


def menu():
    menu_str = """\n
    ================ MENU ================
    [d]\t\tDepositar
    [s]\t\tSacar
    [e]\t\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\t\tSair
    => """
    return input(textwrap.dedent(menu_str))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.accounts:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: client not permitted select account
    return cliente.accounts[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposit(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.perform_transaction(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Withdraw(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.perform_transaction(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.history.transactions

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.balance:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = NaturalPerson(name=nome, date_of_birth=data_nascimento, cpf=cpf, address=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = CurrentAccount.new_account(client=cliente, number=numero_conta)
    contas.append(conta)
    cliente.accounts.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()
