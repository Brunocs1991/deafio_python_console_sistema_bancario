import textwrap
from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class AccountsIterator:
    def __init__(self, accounts):
        self.accounts = accounts
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            account = self.accounts[self._index]
            return f"""\
            Agência:\t{account.agency}
            Número:\t\t{account.number}
            Titular:\t{account.client.name}
            Saldo:\t\tR$ {account.balance:.2f}
        """
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


class Client:
    def __init__(self, address):
        self.address = address
        self.accounts = []
        self.account_index = 0

    def perform_transaction(self, account, transaction):
        if len(account.history.transactions_of_day()) >= 10:
            print("\n@@@ Você atingiu o limite de transações diárias! @@@")
            return
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
    def __init__(self, number, client, limit=500, limit_withdrawals=3):
        super().__init__(number, client)
        self._limit = limit
        self._limit_withdrawals = limit_withdrawals

    def withdraw(self, value):
        number_withdrawals = len(
            [transaction for transaction in self.history.transactions if transaction["type"] == Withdraw.__name__]
        )

        exceeded_limit = value > self._limit
        exceeded_withdrawals = number_withdrawals >= self._limit_withdrawals

        if exceeded_limit:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif exceeded_withdrawals:
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
                "type": transaction.__class__.__name__,
                "value": transaction.value,
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def generate_report(self, transaction_type=None):
        for transaction in self._transactions:
            if transaction_type is None or transaction["type"].lower() == transaction_type.lower():
                yield transaction

    def transactions_of_day(self):

        actual_date = datetime.now().date()
        print(actual_date)
        transactions = []
        for transaction in self._transactions:
            transaction_date = datetime.strptime(transaction["date"], "%d-%m-%Y %H:%M:%S").date()
            if transaction_date == actual_date:
                transactions.append(transaction)
        return transactions


class Transaction(ABC):
    @property
    @abstractmethod
    def value(self):
        pass

    @abstractmethod
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


def log_transaction(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{datetime.now()}: {func.__name__.upper()}")
        return result

    return wrapper


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


def filter_client(cpf, clients):
    filtered_clients = [client for client in clients if client.cpf == cpf]
    return filtered_clients[0] if filtered_clients else None


def retrieve_client_account(client):
    if not client.accounts:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: does not allow client to choose the account
    return client.accounts[0]


@log_transaction
def deposit(clients):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    value = float(input("Informe o valor do depósito: "))
    transaction = Deposit(value)

    account = retrieve_client_account(client)
    if not account:
        return

    client.perform_transaction(account, transaction)


@log_transaction
def withdraw(clients):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    value = float(input("Informe o valor do saque: "))
    transaction = Withdraw(value)

    account = retrieve_client_account(client)
    if not account:
        return

    client.perform_transaction(account, transaction)


@log_transaction
def display_statement(clients):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    account = retrieve_client_account(client)
    if not account:
        return

    print("\n================ EXTRATO ================")
    statement = ""
    has_transaction = False
    for transaction in account.history.generate_report():
        has_transaction = True
        statement += f"\n{transaction['date']}\n{transaction['type']}:\n\tR$ {transaction['value']:.2f}"

    if not has_transaction:
        statement = "Não foram realizadas movimentações"

    print(statement)
    print(f"\nSaldo:\n\tR$ {account.balance:.2f}")
    print("==========================================")


@log_transaction
def create_client(clients):
    cpf = input("Informe o CPF (somente número): ")
    client = filter_client(cpf, clients)

    if client:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    name = input("Informe o nome completo: ")
    date_of_birth = input("Informe a data de nascimento (dd-mm-aaaa): ")
    address = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    client = NaturalPerson(name=name, date_of_birth=date_of_birth, cpf=cpf, address=address)

    clients.append(client)

    print("\n=== Cliente criado com sucesso! ===")


@log_transaction
def create_account(account_number, clients, accounts):
    cpf = input("Informe o CPF do cliente: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    account = CurrentAccount.new_account(client=client, number=account_number)
    accounts.append(account)
    client.accounts.append(account)

    print("\n=== Conta criada com sucesso! ===")


def list_accounts(accounts):
    for account in AccountsIterator(accounts):
        print("=" * 100)
        print(textwrap.dedent(str(account)))


def main():
    clients = []
    accounts = []

    while True:
        option = menu()

        if option == "d":
            deposit(clients)

        elif option == "s":
            withdraw(clients)

        elif option == "e":
            display_statement(clients)

        elif option == "nu":
            create_client(clients)

        elif option == "nc":
            account_number = len(accounts) + 1
            create_account(account_number, clients, accounts)

        elif option == "lc":
            list_accounts(accounts)

        elif option == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()
