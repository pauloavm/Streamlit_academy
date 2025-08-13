### Passo 1: Preparação dos Dados no Power BI (Power Query)

1.  **Abrir o Power BI Desktop** e ir em `Obter Dados` \> `Texto/CSV`.
2.  Selecione o arquivo `teste.csv` e clique em `Abrir`.
3.  Na janela de visualização dos dados, clique em `Transformar Dados`. Isso abrirá o editor do Power Query.
4.  **Corrigir o Tipo de Dados da Coluna `Data_Venda`:**
      * Selecione a coluna `Data_Venda`.
      * No menu `Página Inicial`, no grupo `Transformar`, clique em `Tipo de Dados`.
      * Mude o tipo de dados para `Data/Hora`. O Power Query irá aplicar a alteração, garantindo que você possa fazer análises de tempo.
5.  **Fechar e Aplicar:** Clique em `Fechar e Aplicar` no canto superior esquerdo para carregar os dados corrigidos no Power BI.

### Passo 2: Criação de Medidas (DAX)

Antes de criar os gráficos, é uma boa prática criar medidas DAX para os principais indicadores. Isso garante que os cálculos sejam precisos.

1.  No menu `Página Inicial`, clique em `Nova Medida`.

2.  Crie as seguintes medidas e salve-as:

      * **Receita Total** (Soma da coluna `Total_Venda`):
        ```dax
        Receita Total = SUM('teste'[Total_Venda])
        ```
      * **Quantidade Vendida** (Soma da coluna `Quantidade`):
        ```dax
        Quantidade Vendida = SUM('teste'[Quantidade])
        ```
      * **Ticket Médio** (Média da coluna `Total_Venda`):
        ```dax
        Ticket Médio = AVERAGE('teste'[Total_Venda])
        ```

### Passo 3: Criação das Visualizações para as 5 Perguntas

Agora você pode usar as medidas e as colunas do seu modelo para construir o dashboard. Siga as instruções abaixo para cada pergunta de negócio.

#### Pergunta 1: Receita por Categoria de Produto

  * **Visualização:** Gráfico de barras agrupadas ou Gráfico de colunas agrupadas.
  * **Campos:**
      * **Eixo:** `Categoria_Produto`
      * **Valores:** Arraste a medida `Receita Total` que você criou.

#### Pergunta 2: Top 5 Produtos Mais Vendidos

Você precisará de duas visualizações para responder a esta pergunta.

  * **Visualização 1 (Top 5 por Receita):** Gráfico de barras agrupadas.

  * **Campos:**

      * **Eixo:** `Produto`
      * **Valores:** Arraste a medida `Receita Total`.

  * **Filtro:** Vá para o painel de `Filtros`, selecione o filtro `Produto`, e em `Tipo de filtro`, escolha `N` superior. Insira `5` no campo `Mostrar itens` e arraste a medida `Receita Total` para o campo `Por valor`. Clique em `Aplicar filtro`.

  * **Visualização 2 (Top 5 por Quantidade):** Gráfico de barras agrupadas.

  * **Campos:**

      * **Eixo:** `Produto`
      * **Valores:** Arraste a medida `Quantidade Vendida`.

  * **Filtro:** Repita o mesmo processo do filtro anterior, mas arraste a medida `Quantidade Vendida` para o campo `Por valor`.

#### Pergunta 3: Vendas por País

  * **Visualização:** Gráfico de mapa. O Power BI reconhece automaticamente os nomes dos países.
  * **Campos:**
      * **Localização:** Arraste a coluna `País`.
      * **Tamanho:** Arraste a medida `Receita Total`.

#### Pergunta 4: Tendência de Vendas Mensais

  * **Visualização:** Gráfico de linhas.
  * **Campos:**
      * **Eixo:** Arraste a coluna `Data_Venda` e selecione `Mês` na hierarquia de datas.
      * **Valores:** Arraste a medida `Receita Total`.

#### Pergunta 5: Ticket Médio por Categoria

  * **Visualização:** Gráfico de barras agrupadas.
  * **Campos:**
      * **Eixo:** `Categoria_Produto`
      * **Valores:** Arraste a medida `Ticket Médio` que você criou.

### Passo 4: Finalização do Dashboard

  * **Organizar:** Posicione e redimensione os gráficos na tela do Power BI para criar um layout visualmente atraente.
  * **Títulos:** Adicione títulos claros e descritivos para cada visualização.
  * **Cartões:** Considere adicionar cartões (`Cartão`) na parte superior para exibir os valores totais de `Receita Total`, `Quantidade Vendida` e `Ticket Médio` como um resumo geral.
  * **Filtros:** Adicione filtros de página, como o `País` ou a `Categoria_Produto`, para permitir que o usuário explore os dados de forma interativa.
