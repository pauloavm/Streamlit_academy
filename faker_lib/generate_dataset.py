import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Inicializando a Faker com várias localidades para ter clientes globais
locales = [
    "en_US",
    "pt_BR",
    "es_ES",
    "fr_FR",
    "de_DE",
    "ja_JP",
    "zh_CN",
    "it_IT",
    "ru_RU",
    "ko_KR",
    "pt_PT",
]
faker = Faker(locales)

# Definindo produtos, categorias e seus preços
produtos_eletronicos = {
    "Celulares": {
        "iPhone 13": 850.00,
        "Samsung Galaxy S22": 799.00,
        "Google Pixel 6": 699.00,
        "Xiaomi 12": 599.00,
        "OnePlus 10 Pro": 750.00,
    },
    "Acessórios": {
        "Carregador USB-C": 25.00,
        "Capa de Silicone": 15.00,
        "Fone de Ouvido Bluetooth": 50.00,
        "Smartwatch": 150.00,
        "Power Bank 10000mAh": 30.00,
        "Protetor de tela de vidro": 10.00,
    },
}

# Lista de todos os produtos e suas categorias
all_products = []
for category, products in produtos_eletronicos.items():
    for product, price in products.items():
        all_products.append(
            {"categoria": category, "produto": product, "preco_unitario": price}
        )


# Função para gerar um único registro de venda
def generate_sale_record(sale_id):
    locale = random.choice(locales)
    faker_locale = Faker(locale)

    customer_name = faker_locale.name()
    try:
        first_name = faker_locale.first_name().lower()
        last_name = faker_locale.last_name().lower()
        email_domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
        customer_email = f"{first_name}.{last_name}@{random.choice(email_domains)}"
    except AttributeError:
        customer_email = faker_locale.email()

    customer_country = faker_locale.country()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    sale_date = faker.date_time_between(start_date=start_date, end_date=end_date)
    selected_product = random.choice(all_products)
    product_category = selected_product["categoria"]
    product_name = selected_product["produto"]
    product_price = selected_product["preco_unitario"]
    quantity = random.randint(1, 5)
    total_sale = round(product_price * quantity, 2)

    return {
        "ID_Venda": sale_id,
        "Data_Venda": sale_date.strftime("%Y-%m-%d %H:%M:%S"),
        "ID_Cliente": faker.uuid4(),
        "Nome_Cliente": customer_name,
        "Email_Cliente": customer_email,
        "País": customer_country,
        "Categoria_Produto": product_category,
        "Produto": product_name,
        "Preço_Unitário": product_price,
        "Quantidade": quantity,
        "Total_Venda": total_sale,
    }


# Lógica para obter a quantidade de registros do usuário
try:
    num_records_input = input("Insira a quantidade de registros que deseja criar: ")
    num_records = int(num_records_input) if num_records_input.strip() else 10000
except (ValueError, EOFError):
    num_records = 10000

sales_data = [generate_sale_record(i) for i in range(1, num_records + 1)]
df = pd.DataFrame(sales_data)

# NOVO CÓDIGO AQUI: Permite ao usuário inserir o nome do arquivo
nome_arquivo = input("Insira o nome do arquivo (ex: 'meu_arquivo'): ")

# Garante que o nome do arquivo termine com a extensão .csv
if not nome_arquivo.endswith(".csv"):
    nome_arquivo += ".csv"

# Salvar o DataFrame no arquivo com o nome fornecido pelo usuário
df.to_csv(nome_arquivo, index=False, encoding="utf-8")

print(
    f"A base de dados '{nome_arquivo}' foi criada com sucesso com {num_records} registros."
)
print("\nPrimeiras 5 linhas do DataFrame:")
print(df.head())
