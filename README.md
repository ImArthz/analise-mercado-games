# Desafio de Visualização de Dados — Mercado Global de Video Games (1980–2016)

Trabalho prático desenvolvido para a disciplina de Ciência dos Dados com o objetivo de explorar padrões históricos, diferenças regionais de consumo e a concentração de vendas na indústria de jogos eletrônicos.

**Link direto para o Dashboard Interativo (GitHub Pages):** [https://imarthz.github.io/analise-mercado-games/](https://imarthz.github.io/analise-mercado-games/)

## 1. Dataset e Fonte Original
- **Nome:** Video Game Sales (`vgsales.csv`)
- **Fonte:** [Kaggle — Video Game Sales (GregorySmith / VGChartz)](https://www.kaggle.com/datasets/gregorut/videogamesales)
- **Descrição:** Conjunto de dados com 16.598 registros de jogos lançados para 31 plataformas que superaram 100 mil cópias físicas vendidas. Contém título (`Name`), plataforma (`Platform`), ano de lançamento (`Year`), gênero (`Genre`), publicadora (`Publisher`) e vendas em milhões de unidades na América do Norte (`NA_Sales`), Europa (`EU_Sales`), Japão (`JP_Sales`), resto do mundo (`Other_Sales`) e total global (`Global_Sales`).

## 2. Estrutura de Arquivos Entregues
- `dashboard_interativo.html`: Relatório visual interativo completo (basta abrir em qualquer navegador com duplo clique para interagir com os 4 gráficos do Plotly e ler a análise).
- `analise_jogos.ipynb`: Jupyter Notebook com o passo a passo da exploração, tratamento dos dados, geração dos 4 gráficos e interpretação dos resultados.
- `preparar_dados.py`: Script em Python utilizado para limpar os dados, calcular as estatísticas e exportar o relatório HTML interativo.
- `vgsales.csv`: Cópia local do conjunto de dados utilizado.
- `requirements.txt`: Lista de pacotes do ambiente virtual Python (`pandas`, `plotly`, `nbformat`).

## 3. Resumo das Três Descobertas Principais
1. **A bolha de mídia física entre 2006 e 2011:** Apenas o intervalo de 6 anos entre 2006 e 2011 concentrou **40,8% de todas as vendas da história da base** (3.594,81 milhões de um total de 8.820,02 milhões de cópias entre 1980 e 2016), atingindo o pico de vendas em **2008** (678,90M) e o pico de lançamentos em **2009** (1.431 jogos), puxados pela geração Wii, Nintendo DS, PS3 e Xbox 360.
2. **Contraste cultural entre Japão e Ocidente (RPG vs. Shooter):** No gênero *Role-Playing* (RPG), o mercado japonês absorve **37,9% de todas as vendas mundiais** (350,2M), superando a América do Norte (35,3%) e a Europa (20,3%). Já no gênero *Shooter*, a participação japonesa cai para **3,7%**, enquanto América do Norte (56,0%) e Europa (30,3%) somam **86,3%** do consumo global.
3. **Efeito de cauda longa extrema:** Embora a média simples seja de 0,54 milhão de cópias por jogo, **75,7% dos títulos vendem menos de 500 mil cópias** e a mediana global é de apenas **0,17 milhão (170 mil unidades)**. No topo da pirâmide, o **top 1% dos jogos (163 títulos)** concentra **21,1%** de todas as vendas da indústria e o **top 5% (816 títulos)** concentra **44,6%**.

## 4. Como Executar o Código Localmente
Caso queira regerar o relatório HTML ou executar o notebook no ambiente virtual já configurado na pasta:

```powershell
.\.venv\Scripts\python.exe preparar_dados.py
```
