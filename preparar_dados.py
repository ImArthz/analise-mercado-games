from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pasta_base = Path(__file__).resolve().parent
caminho_csv = pasta_base / "vgsales.csv"

# carregando a base original do vgchartz/kaggle
df = pd.read_csv(caminho_csv)

print("Total de registros brutos:", len(df))
print("Nulos por coluna:\n", df.isna().sum())

# mantendo todas as colunas originais e tratando nulos
df_limpo = df.copy()
df_limpo["Publisher"] = df_limpo["Publisher"].fillna("Desconhecido")

# removendo registros sem ano de lancamento e filtrando ate 2016
# (como a coleta foi feita no fim de 2016, os anos de 2017 e 2020 tem apenas 4 registros soltos)
df_limpo = df_limpo.dropna(subset=["Year"]).copy()
df_limpo["Year"] = df_limpo["Year"].astype(int)
df_limpo = df_limpo[(df_limpo["Year"] >= 1980) & (df_limpo["Year"] <= 2016)].copy()

print("Total apos limpeza (1980-2016):", len(df_limpo))
vendas_totais = df_limpo["Global_Sales"].sum()
print(f"Volume global acumulado: {vendas_totais:.2f} milhoes de copias")

# agrupando as 31 plataformas em familias para leitura das geracoes
def classificar_familia(plat):
    if plat in ["PS", "PS2", "PS3", "PS4", "PSP", "PSV"]:
        return "PlayStation (Sony)"
    elif plat in ["NES", "SNES", "N64", "GC", "Wii", "WiiU"]:
        return "Nintendo (Console de Mesa)"
    elif plat in ["GB", "GBA", "DS", "3DS"]:
        return "Nintendo (Portatil)"
    elif plat in ["XB", "X360", "XOne"]:
        return "Xbox (Microsoft)"
    elif plat == "PC":
        return "PC"
    else:
        return "Sega / Atari / Outros"

df_limpo["Familia"] = df_limpo["Platform"].apply(classificar_familia)

# --- METRICAS EXATAS PARA O RELATORIO ---
vendas_ano = df_limpo.groupby("Year")["Global_Sales"].sum()
ano_pico_vendas = int(vendas_ano.idxmax())
valor_pico_vendas = float(vendas_ano.max())

qtd_ano = df_limpo.groupby("Year")["Name"].count()
ano_pico_jogos = int(qtd_ano.idxmax())
valor_pico_jogos = int(qtd_ano.max())

vendas_2006_2011 = df_limpo[(df_limpo["Year"] >= 2006) & (df_limpo["Year"] <= 2011)]["Global_Sales"].sum()
pct_era_ouro = (vendas_2006_2011 / vendas_totais) * 100

print(f"\nPico de vendas: {ano_pico_vendas} ({valor_pico_vendas:.2f}M) | Pico de lancamentos: {ano_pico_jogos} ({valor_pico_jogos} jogos)")
print(f"Periodo 2006-2011 representa {pct_era_ouro:.1f}% de todas as vendas da historia da base ({vendas_2006_2011:.2f}M)")

genero_reg = df_limpo.groupby("Genre")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]].sum()
genero_reg["NA_%"] = genero_reg["NA_Sales"] / genero_reg["Global_Sales"] * 100
genero_reg["EU_%"] = genero_reg["EU_Sales"] / genero_reg["Global_Sales"] * 100
genero_reg["JP_%"] = genero_reg["JP_Sales"] / genero_reg["Global_Sales"] * 100
genero_reg["Outros_%"] = genero_reg["Other_Sales"] / genero_reg["Global_Sales"] * 100
genero_reg = genero_reg.sort_values(by="JP_%", ascending=True)

print("\nDivisao regional por genero (%):")
print(genero_reg[["Global_Sales", "NA_%", "EU_%", "JP_%"]].round(1))

mediana_geral = df_limpo["Global_Sales"].median()
media_geral = df_limpo["Global_Sales"].mean()
q75_geral = df_limpo["Global_Sales"].quantile(0.75)
q90_geral = df_limpo["Global_Sales"].quantile(0.90)

n_top1 = int(len(df_limpo) * 0.01)
soma_top1 = df_limpo.nlargest(n_top1, "Global_Sales")["Global_Sales"].sum()
pct_top1 = (soma_top1 / vendas_totais) * 100

n_top5 = int(len(df_limpo) * 0.05)
soma_top5 = df_limpo.nlargest(n_top5, "Global_Sales")["Global_Sales"].sum()
pct_top5 = (soma_top5 / vendas_totais) * 100

abaixo_meio_milhao = (df_limpo["Global_Sales"] < 0.5).mean() * 100

print(f"\nMediana: {mediana_geral:.2f}M | Media: {media_geral:.2f}M | Q75: {q75_geral:.2f}M | Q90: {q90_geral:.2f}M")
print(f"Jogos que vendem menos de 500 mil copias: {abaixo_meio_milhao:.1f}%")
print(f"Top 1% ({n_top1} jogos) = {pct_top1:.1f}% das vendas | Top 5% ({n_top5} jogos) = {pct_top5:.1f}% das vendas")

# --- CONSTRUCAO DAS 4 VISUALIZACOES ---
paleta_familias = {
    "PlayStation (Sony)": "#2563eb",
    "Nintendo (Console de Mesa)": "#dc2626",
    "Nintendo (Portatil)": "#f59e0b",
    "Xbox (Microsoft)": "#16a34a",
    "PC": "#7c3aed",
    "Sega / Atari / Outros": "#64748b"
}

# 1. Grafico de area empilhada: evolucao temporal por familia de console (1985-2016)
df_tempo = (
    df_limpo[df_limpo["Year"] >= 1985]
    .groupby(["Year", "Familia"], as_index=False)["Global_Sales"]
    .sum()
)

fig1 = px.area(
    df_tempo,
    x="Year",
    y="Global_Sales",
    color="Familia",
    color_discrete_map=paleta_familias,
    labels={
        "Year": "Ano de Lançamento",
        "Global_Sales": "Vendas Globais (milhões de cópias)",
        "Familia": "Família de Plataforma"
    },
    title="1. Evolução das Vendas Globais por Família de Plataforma (1985–2016)"
)
fig1.update_traces(mode="lines", hovertemplate="<b>%{fullData.name}</b><br>Ano: %{x}<br>Vendas: %{y:.2f}M<extra></extra>")
fig1.update_layout(
    template="plotly_white",
    hovermode="x unified",
    title=dict(y=0.95, x=0.01, xanchor="left", yanchor="top"),
    legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5),
    margin=dict(t=70, l=55, r=30, b=90),
    height=480
)
fig1.add_vline(x=2008, line_dash="dash", line_color="#334155", annotation_text="Pico histórico: 2008 (678.9M)", annotation_position="top left")

# 2. Barras horizontais 100% empilhadas: diferenca cultural entre mercados por genero
df_reg_long = genero_reg.reset_index().melt(
    id_vars=["Genre", "Global_Sales"],
    value_vars=["NA_%", "EU_%", "JP_%", "Outros_%"],
    var_name="Regiao",
    value_name="Percentual"
)
mapa_nomes_reg = {
    "NA_%": "América do Norte",
    "EU_%": "Europa",
    "JP_%": "Japão",
    "Outros_%": "Resto do Mundo"
}
df_reg_long["Regiao_Nome"] = df_reg_long["Regiao"].map(mapa_nomes_reg)

fig2 = px.bar(
    df_reg_long,
    x="Percentual",
    y="Genre",
    color="Regiao_Nome",
    orientation="h",
    color_discrete_map={
        "América do Norte": "#1d4ed8",
        "Europa": "#0ea5e9",
        "Japão": "#e11d48",
        "Resto do Mundo": "#94a3b8"
    },
    labels={
        "Percentual": "Participação nas Vendas do Gênero (%)",
        "Genre": "Gênero",
        "Regiao_Nome": "Mercado"
    },
    title="2. Divisão Regional de Vendas por Gênero (Ordenado pelo Peso do Mercado Japonês)"
)
fig2.update_traces(hovertemplate="<b>%{y}</b> — %{fullData.name}<br>Fatia: %{x:.1f}%<extra></extra>")
fig2.update_layout(
    barmode="stack",
    template="plotly_white",
    title=dict(y=0.95, x=0.01, xanchor="left", yanchor="top"),
    xaxis=dict(ticksuffix="%", range=[0, 100]),
    legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    margin=dict(t=70, l=110, r=30, b=90),
    height=500
)

# 3. Treemap hierarquico interativo (Genre -> Platform -> Top 5 jogos de cada combinacao)
top_jogos_plat = (
    df_limpo.sort_values("Global_Sales", ascending=False)
    .groupby(["Genre", "Platform"], as_index=False)
    .head(5)
)
fig3 = px.treemap(
    top_jogos_plat,
    path=[px.Constant("Mercado Global (Top 5 por Plataforma/Gênero)"), "Genre", "Platform", "Name"],
    values="Global_Sales",
    color="Genre",
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={"Global_Sales": "Vendas Globais (M)", "Genre": "Gênero"},
    title="3. Mapa Hierárquico de Sucessos: Gênero → Plataforma → Títulos Líderes (Clique para Explorar)"
)
fig3.update_traces(
    hovertemplate="<b>%{label}</b><br>Vendas acumuladas: %{value:.2f} milhões<extra></extra>",
    root_color="#f1f5f9"
)
fig3.update_layout(
    template="plotly_white",
    margin=dict(t=60, l=20, r=20, b=20),
    height=540
)

# 4. Boxplot em escala logaritmica + destaque para os blockbusters (>15M)
ordem_generos = (
    df_limpo.groupby("Genre")["Global_Sales"]
    .median()
    .sort_values(ascending=False)
    .index.tolist()
)

cores_box = px.colors.qualitative.Prism
fig4 = go.Figure()
for idx, gen in enumerate(ordem_generos):
    sub = df_limpo[df_limpo["Genre"] == gen]
    fig4.add_trace(
        go.Box(
            y=sub["Global_Sales"],
            x=[gen] * len(sub),
            name=gen,
            boxpoints=False,
            showlegend=False,
            marker_color=cores_box[idx % len(cores_box)],
            line=dict(width=1.5),
            hoverinfo="y+name"
        )
    )

# adicionando os super hits (>15 milhoes) como pontos interativos individuais
hits = df_limpo[df_limpo["Global_Sales"] >= 15.0].copy()
fig4.add_trace(
    go.Scatter(
        x=hits["Genre"],
        y=hits["Global_Sales"],
        mode="markers",
        name="Megassucessos (≥ 15M cópias — passe o mouse para ver o jogo)",
        marker=dict(size=9, color="#dc2626", symbol="diamond", line=dict(width=1, color="white")),
        text=hits["Name"] + " (" + hits["Platform"] + ", " + hits["Year"].astype(str) + ")",
        hovertemplate="<b>%{text}</b><br>Gênero: %{x}<br>Vendas Globais: %{y:.2f}M<extra></extra>"
    )
)

fig4.update_layout(
    title=dict(
        text="4. A Cauda Longa dos Jogos: Distribuição por Gênero (Escala Log) e Megassucessos",
        y=0.95,
        x=0.01,
        xanchor="left",
        yanchor="top"
    ),
    template="plotly_white",
    yaxis=dict(
        title="Vendas Globais em Milhões (Escala Logarítmica)",
        type="log",
        tickvals=[0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 80],
        ticktext=["0.01M", "0.05M", "0.1M", "0.2M", "0.5M", "1M", "2M", "5M", "10M", "20M", "50M", "80M"]
    ),
    xaxis=dict(
        title="Gênero (ordenado pela mediana de vendas)",
        categoryorder="array",
        categoryarray=ordem_generos
    ),
    showlegend=True,
    legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5),
    margin=dict(t=70, l=65, r=30, b=90),
    height=520
)

# exportando os graficos em HTML embutido no relatorio visual final
html_fig1 = pio.to_html(fig1, full_html=False, include_plotlyjs="cdn")
html_fig2 = pio.to_html(fig2, full_html=False, include_plotlyjs=False)
html_fig3 = pio.to_html(fig3, full_html=False, include_plotlyjs=False)
html_fig4 = pio.to_html(fig4, full_html=False, include_plotlyjs=False)

html_completo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Análise Visual — Mercado Global de Video Games (1980–2016)</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --border: #e2e8f0;
      --accent: #1d4ed8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}
    header {{
      background: #0f172a;
      color: #f8fafc;
      padding: 2.5rem 1.5rem;
      border-bottom: 4px solid #2563eb;
    }}
    .container {{
      max-width: 1140px;
      margin: 0 auto;
      padding: 1.5rem;
    }}
    header .container {{ padding: 0; }}
    h1 {{ margin: 0 0 0.5rem 0; font-size: 1.9rem; font-weight: 700; }}
    header p {{ margin: 0; color: #cbd5e1; font-size: 1rem; max-width: 820px; }}
    .meta-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-top: 1.2rem;
      font-size: 0.85rem;
      color: #94a3b8;
    }}
    .meta-bar a {{ color: #60a5fa; text-decoration: none; }}
    .meta-bar a:hover {{ text-decoration: underline; }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      margin: 1.2rem 0 2rem 0;
    }}
    .kpi-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.1rem 1.25rem;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}
    .kpi-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); font-weight: 600; }}
    .kpi-value {{ font-size: 1.65rem; font-weight: 700; color: var(--text); margin: 0.25rem 0; }}
    .kpi-sub {{ font-size: 0.82rem; color: var(--muted); }}
    .section-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.5rem;
      margin-bottom: 1.75rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    h2 {{
      margin-top: 0;
      font-size: 1.3rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.6rem;
      color: #1e293b;
    }}
    h3 {{ font-size: 1.05rem; margin: 1.1rem 0 0.4rem 0; color: #1e293b; }}
    p {{ margin: 0.5rem 0 0.9rem 0; color: #334155; }}
    .note-box {{
      background: #f1f5f9;
      border-left: 4px solid #2563eb;
      padding: 0.9rem 1.1rem;
      border-radius: 0 6px 6px 0;
      font-size: 0.93rem;
      color: #1e293b;
      margin-top: 0.8rem;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.25rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
      margin-top: 0.5rem;
    }}
    th, td {{
      text-align: left;
      padding: 0.55rem 0.75rem;
      border-bottom: 1px solid var(--border);
    }}
    th {{ background: #f8fafc; font-weight: 600; color: #475569; }}
    footer {{
      text-align: center;
      font-size: 0.85rem;
      color: var(--muted);
      padding: 1.5rem 0 2.5rem 0;
    }}
  </style>
</head>
<body>
  <header>
    <div class="container">
      <h1>Mercado Global de Video Games (1980–2016): Ciclos, Cultura Regional e Concentração</h1>
      <p>Exploração visual da base histórica de vendas de jogos físicos, investigando a transição entre gerações de consoles, o contraste de consumo entre Oriente e Ocidente e o efeito de cauda longa nas vendas.</p>
      <div class="meta-bar">
        <span><strong>Disciplina:</strong> Ciência dos Dados — Desafio de Visualização de Dados</span>
        <span><strong>Dataset:</strong> <a href="https://www.kaggle.com/datasets/gregorut/videogamesales" target="_blank">Video Game Sales (Kaggle / VGChartz)</a></span>
        <span><strong>Ferramentas:</strong> Python, Pandas e Plotly</span>
      </div>
    </div>
  </header>

  <main class="container">
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Jogos Analisados (1980–2016)</div>
        <div class="kpi-value">{len(df_limpo):,}</div>
        <div class="kpi-sub">de {len(df):,} registros brutos na base</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Vendas Globais Acumuladas</div>
        <div class="kpi-value">{vendas_totais:,.1f}M</div>
        <div class="kpi-sub">milhões de cópias físicas vendidas</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Pico Histórico do Mercado</div>
        <div class="kpi-value">{ano_pico_vendas} ({valor_pico_vendas:.1f}M)</div>
        <div class="kpi-sub">{valor_pico_jogos} títulos lançados no mesmo ano</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Mediana vs. Média por Jogo</div>
        <div class="kpi-value">{mediana_geral:.2f}M vs {media_geral:.2f}M</div>
        <div class="kpi-sub">top 1% concentra {pct_top1:.1f}% das vendas</div>
      </div>
    </div>

    <section class="section-card">
      <h2>1. Contexto, Fonte dos Dados e Preparação</h2>
      <p>O conjunto de dados utilizado é o <strong>Video Game Sales</strong>, compilado por Gregory Smith a partir dos registros públicos do portal <em>VGChartz</em> e disponibilizado no Kaggle (<a href="https://www.kaggle.com/datasets/gregorut/videogamesales" target="_blank">link da fonte original</a>). A base reúne jogos que ultrapassaram a marca de 100 mil cópias vendidas globalmente, trazendo plataforma de lançamento, ano, gênero, publicadora (<em>publisher</em>) e o volume de vendas discriminado entre América do Norte (<code>NA_Sales</code>), Europa (<code>EU_Sales</code>), Japão (<code>JP_Sales</code>), resto do mundo (<code>Other_Sales</code>) e total global (<code>Global_Sales</code>), todos expressos em milhões de unidades.</p>
      <p>Na etapa de limpeza e preparação, preservamos todas as colunas originais e tratamos duas questões pontuais: (1) 271 registros que não possuíam ano de lançamento preenchido foram removidos para não distorcer a série histórica; (2) como a raspagem original dos dados ocorreu no final de 2016, os anos de 2017 e 2020 continham apenas 4 registros isolados e foram filtrados, mantendo a janela consolidada de 1980 a 2016 ({len(df_limpo):,} jogos). Já os 58 casos de <code>Publisher</code> em branco foram preenchidos como <em>Desconhecido</em> para evitar perda desnecessária de dados nas análises por gênero e plataforma.</p>
    </section>

    <section class="section-card">
      <h2>2. Visualizações Interativas e Investigação</h2>
      <p>Passe o cursor sobre os gráficos para consultar os valores detalhados, clique nos itens da legenda para isolar séries específicas ou clique nos blocos do mapa hierárquico (Gráfico 3) para navegar pelos níveis.</p>
      {html_fig1}
      <div class="note-box">
        <strong>Leitura do Gráfico 1:</strong> A série histórica mostra como a indústria saltou de um patamar de ~200 milhões de cópias anuais no fim dos anos 1990 para quase 680 milhões em 2008, puxada simultaneamente pela popularização dos controles de movimento (Nintendo Wii), pelos portáteis (Nintendo DS) e pela disputa entre PS3 e Xbox 360.
      </div>
    </section>

    <section class="section-card">
      {html_fig2}
      <div class="note-box">
        <strong>Leitura do Gráfico 2:</strong> Ordenando os gêneros pela participação japonesa, fica visível que o mercado não é homogêneo. Enquanto jogos de tiro (<em>Shooter</em>) e esportes têm menos de 11% de suas vendas no Japão e mais de 50% na América do Norte, o gênero <em>Role-Playing</em> (RPG) obtém 37,9% de toda a sua receita global apenas no mercado japonês.
      </div>
    </section>

    <section class="section-card">
      {html_fig3}
      <div class="note-box">
        <strong>Leitura do Gráfico 3 (Interativo — Clique nas caixas):</strong> O treemap permite cruzar três dimensões simultaneamente (gênero, console e título). Ao clicar em <em>Sports</em> ou <em>Platform</em>, nota-se como a Nintendo domina o topo dos jogos individuais mais vendidos com títulos empacotados ou familiares (como <em>Wii Sports</em> com 82,74M e <em>Super Mario Bros.</em> com 40,24M), enquanto <em>Action</em> e <em>Shooter</em> têm vendas distribuídas entre PS2, PS3 e Xbox 360 (liderados pela série <em>Grand Theft Auto</em> e <em>Call of Duty</em>).
      </div>
    </section>

    <section class="section-card">
      {html_fig4}
      <div class="note-box">
        <strong>Leitura do Gráfico 4:</strong> O uso da escala logarítmica no eixo vertical é indispensável porque a distribuição real é altamente assimétrica. A mediana geral da indústria é de apenas {mediana_geral:.2f} milhão (170 mil cópias), mas cada gênero possui poucos títulos que vendem de 50 a 400 vezes mais que um lançamento mediano.
      </div>
    </section>

    <section class="section-card">
      <h2>3. Três Descobertas Principais a partir dos Dados</h2>
      <div class="grid-2">
        <div>
          <h3>Descoberta 1: A bolha de lançamentos e o pico de mídia física entre 2006 e 2011</h3>
          <p>Ao cruzar o volume de vendas e a quantidade de lançamentos por ano (Gráfico 1), observa-se que apenas o intervalo de 6 anos entre <strong>2006 e 2011</strong> concentrou <strong>{pct_era_ouro:.1f}% de todas as cópias vendidas</strong> em 37 anos de dados ({vendas_2006_2011:,.1f} milhões de um total de {vendas_totais:,.1f} milhões). O ápice ocorreu em <strong>2008</strong> ({valor_pico_vendas:.1f}M de cópias) e <strong>2009</strong> ({valor_pico_jogos} jogos lançados). A partir de 2012, as vendas de mídia física caem de forma contínua em todas as famílias de consoles devido à transição para distribuição digital e jogos mobile.</p>

          <h3>Descoberta 2: O abismo cultural entre Japão e Ocidente em RPGs vs. Shooters</h3>
          <p>A decomposição proporcional por gênero (Gráfico 2) comprova que o gosto do consumidor japonês segue uma dinâmica própria. No gênero <strong>Role-Playing (RPG)</strong>, o Japão responde por <strong>37,9% das vendas mundiais</strong> (350,2 milhões de cópias), superando a América do Norte (35,3%) e a Europa (20,3%), impulsionado por franquias como <em>Pokémon</em>, <em>Final Fantasy</em> e <em>Dragon Quest</em>. No extremo oposto, em <strong>Shooter</strong> (jogos de tiro em primeira/terceira pessoa), a fatia japonesa despenca para apenas <strong>3,7%</strong>, enquanto América do Norte (56,0%) e Europa (30,3%) somam mais de 86% do consumo mundial.</p>
        </div>
        <div>
          <h3>Descoberta 3: Um mercado de cauda longa extrema onde 5% dos jogos geram 44,6% das vendas</h3>
          <p>A análise da distribuição (Gráfico 4) mostra que a média simples ({media_geral:.2f}M por jogo) engana: <strong>{abaixo_meio_milhao:.1f}% dos jogos da base vendem menos de 500 mil cópias</strong>, e a mediana global é de apenas <strong>{mediana_geral:.2f} milhão (170 mil unidades)</strong>. Enquanto isso, o <strong>top 1% dos títulos ({n_top1} jogos)</strong> acumula <strong>{pct_top1:.1f}% de todas as vendas da indústria</strong> ({soma_top1:,.1f}M de cópias), e o top 5% ({n_top5} jogos) responde por <strong>{pct_top5:.1f}%</strong> do mercado total ({soma_top5:,.1f}M). Na prática, poucos megassucessos financiam o ecossistema inteiro de cada geração de console.</p>

          <h3>Resumo Comparativo por Gênero</h3>
          <table>
            <thead>
              <tr>
                <th>Gênero</th>
                <th>Total Global (M)</th>
                <th>Fatia NA</th>
                <th>Fatia EU</th>
                <th>Fatia JP</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Action</td><td>1.722,9M</td><td>50,0%</td><td>30,0%</td><td>9,2%</td></tr>
              <tr><td>Sports</td><td>1.309,2M</td><td>51,2%</td><td>28,4%</td><td>10,3%</td></tr>
              <tr><td>Shooter</td><td>1.026,2M</td><td>56,0%</td><td>30,3%</td><td>3,7%</td></tr>
              <tr><td>Role-Playing</td><td>923,8M</td><td>35,3%</td><td>20,3%</td><td>37,9%</td></tr>
              <tr><td>Platform</td><td>829,2M</td><td>53,8%</td><td>24,2%</td><td>15,8%</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="section-card">
      <h2>4. Justificativa das Ferramentas e Limitações dos Dados</h2>
      <div class="grid-2">
        <div>
          <h3>Por que Python + Plotly e estes 4 tipos visuais?</h3>
          <p>Optamos por trabalhar com <strong>Python (Pandas + Plotly)</strong> exportado tanto em Jupyter Notebook quanto em relatório HTML interativo porque essa combinação garante reprodutibilidade do tratamento dos dados e permite que qualquer pessoa explore os gráficos diretamente no navegador (usando zoom, filtro de legendas e inspeção via <em>hover</em>) sem depender de licenças comerciais de BI.</p>
          <p>Quanto aos tipos de gráfico: (1) o <strong>gráfico de área empilhada</strong> foi escolhido por representar variáveis contínuas no tempo, exibindo tanto o total da indústria quanto a troca de liderança entre famílias de consoles; (2) as <strong>barras horizontais 100% empilhadas</strong> normalizam o tamanho total de cada gênero e permitem comparar diretamente a proporção cultural de cada região; (3) o <strong>Treemap interativo</strong> resolve o problema de visualizar uma hierarquia de três níveis (Gênero → Console → Jogo) em um único espaço com suporte a <em>drill-down</em>; e (4) o <strong>Boxplot em escala logarítmica combinado com pontos de dispersão</strong> evita que os grandes <em>outliers</em> esmaguem a visualização das caixas interquartis.</p>
        </div>
        <div>
          <h3>Limitações Conhecidas do Dataset</h3>
          <p>Qualquer conclusão extraída desta base deve considerar quatro limitações importantes:</p>
          <p>1. <strong>Foco exclusivo em mídia física:</strong> Os dados do VGChartz contabilizam vendas de unidades em varejo físico. A queda acentuada observada entre 2011 e 2016 reflete a migração dos jogadores para lojas digitais (Steam, PS Store, Xbox Live) e não uma retração real do setor de jogos.<br>
          2. <strong>Corte de entrada em 100 mil cópias:</strong> Como a base só registra títulos que superaram 0,10M de vendas (ou próximo disso), milhares de jogos independentes menores não entram na conta, o que significa que a concentração real da indústria é ainda mais acentuada.<br>
          3. <strong>Jogos bundled (inclusos no console):</strong> O líder isolado da base, <em>Wii Sports</em> (82,74M), vinha incluso na caixa do console Nintendo Wii na América do Norte e Europa, o que infla artificialmente sua comparação com jogos vendidos avulsos.<br>
          4. <strong>Ausência de receitas recorrentes:</strong> O dataset mede cópias vendidas, ignorando microtransações, assinaturas e DLCs.</p>
        </div>
      </div>
    </section>
  </main>

  <footer>
    Trabalho Prático de Ciência dos Dados — Visualização de Dados | Base: Video Game Sales (Kaggle / VGChartz)
  </footer>
</body>
</html>
"""

caminho_html = pasta_base / "dashboard_interativo.html"
caminho_html.write_text(html_completo, encoding="utf-8")
print(f"\nRelatorio HTML gerado com sucesso em: {caminho_html}")
