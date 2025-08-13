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
    # Selecionar uma localidade aleatória para os dados do cliente
    locale = random.choice(locales)
    faker_locale = Faker(locale)

    customer_name = faker_locale.name()
    customer_email = faker_locale.email()
    customer_country = faker_locale.country()

    # Gerar uma data de venda aleatória no último ano
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    sale_date = faker.date_time_between(start_date=start_date, end_date=end_date)

    # Selecionar um produto aleatório da nossa lista
    selected_product = random.choice(all_products)
    product_category = selected_product["categoria"]
    product_name = selected_product["produto"]
    product_price = selected_product["preco_unitario"]

    # Gerar quantidade e calcular o total da venda
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


# Gerar 10.000 registros de vendas
num_records = 10000  # alterar para o número desejado
sales_data = [generate_sale_record(i) for i in range(1, num_records + 1)]

# Criar o DataFrame com Pandas
df = pd.DataFrame(sales_data)
nome_arquivo = "vendas_eletronicos.csv"

# O DataFrame 'df' é criado...
df.to_csv(nome_arquivo, index=False)

# Exibir informações sobre a base de dados criada
print(
    f"A base de dados '{nome_arquivo}' foi criada com sucesso com {num_records} registros."
)
print("\nPrimeiras 5 linhas do DataFrame:")
print(df.head())
