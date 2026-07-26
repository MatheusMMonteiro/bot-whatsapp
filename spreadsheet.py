import gspread


def retorna_contatos():
    # Conecta usando o arquivo de credenciais da Conta de Serviço
    gc = gspread.service_account(filename='credentials.json')

    # Abre a planilha pelo ID
    sh = gc.open_by_key("1COEMGNlRK4LC2X33nM_yegppP7dUX-Io48STykzmDqo")

    # Seleciona a primeira aba
    worksheet = sh.get_worksheet(0)

    # A) Pegar a mensagem fixa
    mensagem_padrao = worksheet.acell('F10').value

    # B) Pegar a lista de contatos
    contatos_raw = worksheet.get('A2:B25')

    # Cria a lista de dicionários com nome e telefone
    lista_contatos = []
    for linha in contatos_raw:
        if len(linha) >= 2 and linha[0].strip() and linha[1].strip():
            # Limpa o telefone mantendo apenas números
            telefone_limpo = "".join(filter(str.isdigit, str(linha[1])))

            # Adiciona o 55 do Brasil se não tiver
            if not telefone_limpo.startswith("55"):
                telefone_limpo = f"55{telefone_limpo}"

            lista_contatos.append({
                "nome": linha[0].strip(),
                "telefone": telefone_limpo
            })

    return {
        "mensagem": mensagem_padrao,
        "contatos": lista_contatos
    }
