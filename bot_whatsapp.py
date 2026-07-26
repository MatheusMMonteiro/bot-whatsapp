import os
import requests
import time
from spreadsheet import retorna_contatos
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente Python
load_dotenv()

# Configurações do servidor local
API_URL = os.getenv("SERVER_URL")
API_KEY = os.getenv("AUTHENTICATION_API_KEY")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}


def obter_status_conexao():
    """Verifica o status da conexão da instância."""
    url = f"{API_URL}/instance/connectionState/{INSTANCE_NAME}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Retorna o estado (ex: "open", "close", "connecting")
            return data.get("instance", {}).get("state")
    except Exception as e:
        print(f"Erro ao consultar status da instância: {e}")
    return None


def criar_instancia():
    """Cria a instância no servidor local da Evolution API se não existir."""
    url = f"{API_URL}/instance/create"
    payload = {
        "instanceName": INSTANCE_NAME,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def obter_qrcode():
    """Obtém o QR Code para conectar o WhatsApp."""
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"
    response = requests.get(url, headers=headers)
    data = response.json()

    if "base64" in data or "code" in data:
        print("QR Code gerado. Acesse a resposta da API ou logs para escanear.")
    return data


def enviar_mensagem(numero, texto):
    """Envia uma mensagem de texto para um número específico."""
    url = f"{API_URL}/message/sendText/{INSTANCE_NAME}"

    payload = {
        "number": numero,
        "text": texto,
        "delay": 1200
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.json()


# --- Exemplo de Uso ---
if __name__ == "__main__":
    # 1. Checa o estado atual da conexão
    status = obter_status_conexao()
    print(f"Status atual da instância '{INSTANCE_NAME}': {status}")

    # Se a instância já estiver conectada ("open"), pula a criação e o QR Code
    if status == "open":
        print("Instância já está conectada e pronta para envio!")
    else:
        # Se não estiver aberta, tenta criar/conectar
        print("Instância não conectada. Inicializando processo de login...")
        criar_instancia()
        obter_qrcode()
        input("Após escanear o QR Code no seu celular, pressione Enter para continuar...")

    # 2. Lista de contatos para o envio
    dados = retorna_contatos()

    mensagem_padrao = dados["mensagem"]

    print(f"\nIniciando disparos para {len(dados['contatos'])} contatos...\n")

    # 3. Loop de envio
    for contato in dados["contatos"]:
        print(f"Enviando para {contato['nome']} - {contato['telefone']}")

        mensagem = f"Olá {contato['nome']},\n\n{mensagem_padrao}"

        status_code, resp = enviar_mensagem(contato['telefone'], mensagem)
        print(f"Status HTTP: {status_code}")

        # Intervalo de segurança (12 segundos)
        time.sleep(12)