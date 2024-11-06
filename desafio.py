import textwrap

def menu():
    menu_options = """\n
    ================= MENU =================
    [d]\t\tDepositar
    [s]\t\tSacar
    [e]\t\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\t\tSair
    => """
    return input(textwrap.dedent(menu_options))


def deposit(balance, value, extract,/):
    if value > 0:
        balance += value
        extract += f"Depósito:\t R$ {value:.2f}\n"
        print(f"\n=== Depósito realizado com sucesso! ===")
    else:
        print(f"\n@@@ Operação falhou! o valor informado é inválido, @@@")

    return balance, extract

def withdraw(*, balance, value, extract, limit, number_withdrawals, limit_withdrawals):
    exceeded_balance = value > balance
    exceeded_limit = value > limit
    exceeded_withdrawals = number_withdrawals >= limit_withdrawals

    if exceeded_balance:
        print(f"\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
    elif exceeded_limit:
        print(f"\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
    elif exceeded_withdrawals:
        print(f"\n@@@ Operação falhou! Você atingiu o limite de saques. @@@")
    elif value > 0:
        balance -= value
        extract += f"Saque:\t\t R$ {value:.2f}\n"
        number_withdrawals += 1
        print(f"\n=== Saque realizado com sucesso! ===")
    else:
        print(f"\n@@@ Operação falhou! o valor informado é inválido, @@@")
    return balance, extract

def display_extract(balance, /, *, extract):
    print("\n================= Extrato =================")
    print("Não foram realizadas movimentações." if not extract else extract)
    print(f"\nSaldo atual:\t\t R$ {balance:.2f}")
    print("=========================================")

def create_user(users):
    cpf = input("Digite o CPF (somente números): ")
    user = filter_users(cpf, users)

    if user:
        print("\n@@@ Usuário já cadastrado! @@@")
        return

    name = input("Digite o nome completo: ")
    date_of_birth = input("Digite a data de nascimento (dd-mm-aaaa): ")
    address = input("Digite o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    users.append({"nome": name, "cpf": cpf, "data_nascimento": date_of_birth, "endereco": address})
    print("\n=== Usuário cadastrado com sucesso! ===")

def filter_users(cpf, users):
    filtered_users = [user for user in users if user["cpf"] == cpf]
    return filtered_users[0] if filtered_users else None

def create_account(agency, number_account, users):
    cpf = input("Digite o CPF (somente números): ")
    user =  filter_users(cpf, users)
    if user:
        print("\n === Conta criada com sucesso! ===")
        return {"agencia": agency, "numero": number_account, "usuario": user}
    print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")

def list_accounts(accounts):
    for account in accounts:
        linha = f"""\
        Agência:\t{account["agencia"]}
        C/C:\t\t{account["numero"]}
        Titular:\t{account["usuario"]["nome"]}
        """
        print("=" * 100)
        print(textwrap.dedent(linha))

def main():
    LIMIT_WITHDRAWALS = 3
    AGENCY = "0001"

    balance = 0
    limit = 500
    extract = ""
    number_withdrawals = 0
    users = []
    accounts = []

    while True:
        option = menu()

        if option == 'd':
            value = float(input("Digite o valor do depósito: "))
            balance, extract = deposit(balance, value, extract)
        elif option == 's':
            value = float(input("Digite o valor do saque: "))
            balance, extract = withdraw(
                balance=balance,
                value=value,
                extract=extract,
                limit=limit,
                number_withdrawals=number_withdrawals,
                limit_withdrawals=LIMIT_WITHDRAWALS
            )

        elif option == 'e':
            display_extract(balance, extract=extract)

        elif option == 'nu':
            create_user(users)

        elif option == 'nc':
            number_account = len(accounts) + 1
            account = create_account(AGENCY, number_account, users)
            if account:
                accounts.append(account)

        elif option == 'lc':
            list_accounts(accounts)

        elif option == 'q':
            break

main()
