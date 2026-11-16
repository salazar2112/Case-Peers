"""
Case OrbitShop - análise de cancelamentos
Reproduz todos os números do memo. Uso:
    python base.py                      (planilha na mesma pasta)
    python base.py caminho/da/base.xlsx (outra localização)
Saída: tabelas no terminal e gráficos na pasta graficos/.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")  # salva os gráficos em arquivo, sem abrir janela
import matplotlib.pyplot as plt
import pandas as pd

ARQ = sys.argv[1] if len(sys.argv) > 1 else "Base_Dados_OrbitShop_v3.xlsx"
PASTA_GRAFICOS = "graficos"
pd.set_option("display.width", 200)        # mostra tabelas largas sem cortar colunas
pd.set_option("display.max_columns", 20)
os.makedirs(PASTA_GRAFICOS, exist_ok=True)


def titulo(texto):
    print("\n" + "=" * 70 + f"\n{texto}\n" + "=" * 70)



# 1. CARGA

abas = ["Clientes", "Produtos", "Pedidos", "Itens_Pedido", "Tickets_Suporte", "Avaliacoes"]
df = {aba: pd.read_excel(ARQ, sheet_name=aba) for aba in abas}

clientes = df["Clientes"]
produtos = df["Produtos"]
pedidos = df["Pedidos"]
itens = df["Itens_Pedido"]
tickets = df["Tickets_Suporte"]
avaliacoes = df["Avaliacoes"]

# 2. LIMPEZA (decisões documentadas no README)

# Decisão 1: datas vêm como texto -> converter
clientes["data_cadastro"] = pd.to_datetime(clientes["data_cadastro"])
pedidos["data_pedido"] = pd.to_datetime(pedidos["data_pedido"])
tickets["data_abertura"] = pd.to_datetime(tickets["data_abertura"])
tickets["data_resolucao"] = pd.to_datetime(tickets["data_resolucao"])
avaliacoes["data_avaliacao"] = pd.to_datetime(avaliacoes["data_avaliacao"])

# Colunas auxiliares de tempo
pedidos["ano"] = pedidos["data_pedido"].dt.year
pedidos["mes"] = pedidos["data_pedido"].dt.to_period("M").astype(str)
tickets["mes"] = tickets["data_abertura"].dt.to_period("M").astype(str)

# Decisão 4: desconto vazio tratado como 0 
itens["valor_item"] = (
    itens["preco_praticado"] * itens["quantidade"] * (1 - itens["desconto_aplicado"].fillna(0))
)

# Flag de cancelamento (definição usada em todo o código: status "cancelado")
pedidos["cancelado"] = pedidos["status"] == "cancelado"

# Pedidos com dados do cliente (segmento e canal de aquisição)
ped_cli = pedidos.merge(clientes[["id", "segmento", "canal_aquisicao"]],
                        left_on="cliente_id", right_on="id", suffixes=("", "_cliente"))

# =====================================================================
# 3. RAIO-X DA BASE
# =====================================================================
titulo("RAIO-X DA BASE")
for nome, tabela in df.items():
    print(f"{nome}: {tabela.shape[0]} linhas | nulos: "
          f"{tabela.isna().sum()[tabela.isna().sum() > 0].to_dict()}")

print("\nDecisão 2 - data_resolucao vazia x status do ticket:")
print(pd.crosstab(tickets["status"], tickets["data_resolucao"].isna()))

print("\nDecisão 4 - desconto: itens com 0 explícito:", (itens["desconto_aplicado"] == 0).sum(),
      "| itens vazios:", itens["desconto_aplicado"].isna().sum())

# =====================================================================
# Q2 - DISTRIBUIÇÃO POR STATUS
# =====================================================================
titulo("Q2 - PEDIDOS POR STATUS")
q2 = pd.DataFrame({
    "pedidos": pedidos["status"].value_counts(),
    "percentual": (pedidos["status"].value_counts(normalize=True) * 100).round(1),
})
q2.loc["TOTAL"] = [q2["pedidos"].sum(), q2["percentual"].sum()]
q2["pedidos"] = q2["pedidos"].astype(int)
print(q2)

print("\nPor ano (quantidade):")
print(pd.crosstab(pedidos["status"], pedidos["ano"], margins=True, margins_name="TOTAL"))
print("\nPor ano (% dentro de cada ano):")
print((pd.crosstab(pedidos["status"], pedidos["ano"], normalize="columns") * 100).round(1))

perda = pedidos["status"].isin(["cancelado", "devolvido"]).mean() * 100
print(f"\nCancelados + devolvidos: {perda:.1f}% dos pedidos")

# Gráfico 1: distribuição geral
ordem = q2.drop("TOTAL")["percentual"].sort_values()
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(ordem.index, ordem.values, color="#4C72B0")
for i, v in enumerate(ordem.values):
    ax.text(v + 0.5, i, f"{v}%", va="center")
ax.set_xlabel("% do total de pedidos")
ax.set_title("Pedidos por status (jan/2023 a dez/2024, n = 15.000)")
plt.tight_layout()
plt.savefig(f"{PASTA_GRAFICOS}/q2_status.png", dpi=150)
plt.close()

# Gráfico 2: status mês a mês (mostra o "em trânsito" congelado)
mensal_status = pd.crosstab(pedidos["mes"], pedidos["status"])
ax = mensal_status.plot(figsize=(12, 5), marker="o")
ax.set_ylabel("Número de pedidos")
ax.set_title("Pedidos por status, mês a mês")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f"{PASTA_GRAFICOS}/q2_status_mensal.png", dpi=150)
plt.close()


# Q3 - CATEGORIAS: RECEITA x VOLUME (tabela de itens, usar com ressalva)

titulo("Q3 - CATEGORIAS (receita x volume)")
itens_cat = itens.merge(produtos[["id", "categoria"]],
                        left_on="produto_id", right_on="id", suffixes=("", "_produto"))
q3 = itens_cat.groupby("categoria").agg(
    receita=("valor_item", "sum"),
    unidades=("quantidade", "sum"),
    preco_medio=("preco_praticado", "mean"),
)
q3["receita_%"] = (q3["receita"] / q3["receita"].sum() * 100).round(1)
q3["unidades_%"] = (q3["unidades"] / q3["unidades"].sum() * 100).round(1)
q3["rank_receita"] = q3["receita"].rank(ascending=False).astype(int)
q3["rank_volume"] = q3["unidades"].rank(ascending=False).astype(int)
print(q3.sort_values("receita", ascending=False).round(1))
print("\nRessalva: preços médios implausíveis (ex.: Livros & Papelaria) -> "
      "ranking de receita é indicativo; o de volume é mais confiável.")


# Q4 - CANAIS DE AQUISIÇÃO

titulo("Q4 - CANAIS DE AQUISIÇÃO")
q4 = ped_cli.groupby("canal_aquisicao").agg(
    pedidos=("id", "size"),
    cancelados=("cancelado", "sum"),
    taxa_cancel=("cancelado", "mean"),
    ticket_medio=("valor_total", "mean"),  # fonte oficial (Q6)
    pct_com_cupom=("cupom_desconto", lambda s: (s == "sim").mean()),
)
q4["taxa_cancel"] = (q4["taxa_cancel"] * 100).round(1)
q4["pct_com_cupom"] = (q4["pct_com_cupom"] * 100).round(1)
q4["%_dos_pedidos"] = (q4["pedidos"] / q4["pedidos"].sum() * 100).round(1)
q4["%_dos_cancelamentos"] = (q4["cancelados"] / q4["cancelados"].sum() * 100).round(1)
print(q4.round(2).sort_values("taxa_cancel", ascending=False))

print("\nTaxa de cancelamento (%) por canal e ano:")
print((ped_cli.groupby(["canal_aquisicao", "ano"])["cancelado"].mean().unstack() * 100).round(1))


# Q5 - SAZONALIDADE

titulo("Q5 - VOLUME MENSAL")
mensal = pedidos.groupby("mes").size().rename("pedidos").to_frame()
mediana = mensal["pedidos"].median()
mensal["vs_mediana_%"] = ((mensal["pedidos"] / mediana - 1) * 100).round(1)
print(f"Mediana mensal: {mediana:.0f} pedidos")
print(mensal)

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(mensal.index, mensal["pedidos"], marker="o", color="#4C72B0")
ax.axhline(mediana, color="gray", linestyle="--", label=f"Mediana ({mediana:.0f})")
ax.set_title("Pedidos por mês (jan/2023 a dez/2024)")
ax.set_ylabel("Pedidos")
ax.legend()
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(f"{PASTA_GRAFICOS}/q5_volume_mensal.png", dpi=150)
plt.close()

nov23 = pedidos[pedidos["mes"] == "2023-11"]
demais = pedidos[pedidos["mes"] != "2023-11"]

# Teste 1: concentração na semana da Black Friday (24/11/2023)?
por_dia = nov23["data_pedido"].dt.day.value_counts().sort_index()
print(f"\nNov/2023 por dia: mín {por_dia.min()}, máx {por_dia.max()}, média {por_dia.mean():.1f}")
print("Semana 20-27/11:", por_dia.loc[20:27].sum(),
      "| esperado se uniforme:", round(len(nov23) * 8 / 30))


# Teste 2: perfil de nov/2023 x demais meses
def perfil(d):
    return pd.Series({
        "% cancelado": (d["status"] == "cancelado").mean() * 100,
        "% com cupom": (d["cupom_desconto"] == "sim").mean() * 100,
        "ticket médio": d["valor_total"].mean(),
    }).round(1)


print("\nPerfil nov/2023 x demais meses:")
print(pd.DataFrame({"nov/2023": perfil(nov23), "demais meses": perfil(demais)}))

# Teste 3: chamados de suporte por mês
print("\nChamados por mês:")
print(tickets.groupby("mes").size().to_string())

# Volume e cancelamentos por ano, sem nov/2023
print("\nSem nov/2023 (pedidos, cancelados, taxa %):")
print(demais.groupby("ano").agg(
    pedidos=("id", "size"),
    cancelados=("cancelado", "sum"),
    taxa=("cancelado", lambda s: round(s.mean() * 100, 1)),
))


# Q6 - VALOR_TOTAL x SOMA DOS ITENS

titulo("Q6 - VALOR_TOTAL x SOMA DOS ITENS")
soma_itens = itens.groupby("pedido_id")["valor_item"].sum().rename("soma_itens")
itens["valor_desconto"] = (
    itens["preco_praticado"] * itens["quantidade"] * itens["desconto_aplicado"].fillna(0)
)
soma_desc = itens.groupby("pedido_id")["valor_desconto"].sum().rename("soma_desconto")

comp = (ped_cli.merge(soma_itens, left_on="id", right_index=True, how="left")
               .merge(soma_desc, left_on="id", right_index=True, how="left"))
comp["diferenca"] = comp["valor_total"] - comp["soma_itens"]

print("Pedidos sem nenhum item:", comp["soma_itens"].isna().sum())
print("Pedidos sem valor_total (excluídos das contas de valor):", comp["valor_total"].isna().sum())
print("Batem (diferença até R$ 1):", (comp["diferenca"].abs() <= 1).sum())
print("Não batem:", (comp["diferenca"].abs() > 1).sum())
print(f"Soma valor_total: R$ {comp['valor_total'].sum():,.2f}")
print(f"Soma dos itens:   R$ {comp['soma_itens'].sum():,.2f}")

# Hipótese descartada: valor_total = total de desconto
print("\nCorrelação valor_total x soma do desconto:",
      round(comp["valor_total"].corr(comp["soma_desconto"]), 3))
print("Correlação valor_total x soma dos itens:",
      round(comp["valor_total"].corr(comp["soma_itens"]), 3))

# Triangulação: qual fonte reproduz "B2B vale ~6x mais" (fala da CEO)?
ticket = comp.groupby("segmento")[["valor_total", "soma_itens"]].mean()
print("\nTicket médio por segmento:")
print(ticket.round(2))
print("\nRazão B2B / B2C:")
print((ticket.loc["B2B"] / ticket.loc["B2C"]).round(2))

# Q7 - FORNECEDORES

titulo("Q7 - FORNECEDORES")
aval_forn = avaliacoes.merge(produtos[["id", "fornecedor"]],
                             left_on="produto_id", right_on="id", suffixes=("", "_produto"))
q7_aval = aval_forn.groupby("fornecedor").agg(
    avaliacoes=("nota", "size"),
    nota_media=("nota", "mean"),
    pct_notas_ruins=("nota", lambda s: (s <= 2).mean() * 100),
)

# Regra: um pedido "envolve" o fornecedor se tiver pelo menos um item dele
ped_forn = (itens.merge(produtos[["id", "fornecedor"]],
                        left_on="produto_id", right_on="id", suffixes=("", "_produto"))
                 [["pedido_id", "fornecedor"]].drop_duplicates())

print("Pedidos por número de fornecedores diferentes:")
print(ped_forn.groupby("pedido_id").size().value_counts().sort_index())

tick_forn = tickets.merge(ped_forn, on="pedido_id")
canc_forn = ped_forn.merge(pedidos[["id", "cancelado"]], left_on="pedido_id", right_on="id")

q7 = pd.DataFrame({
    "pedidos_envolvidos": ped_forn.groupby("fornecedor").size(),
    "chamados_por_1000_pedidos": tick_forn.groupby("fornecedor").size()
                                 / ped_forn.groupby("fornecedor").size() * 1000,
    "taxa_cancel_%": canc_forn.groupby("fornecedor")["cancelado"].mean() * 100,
}).join(q7_aval)
print("\nVisão completa por fornecedor:")
print(q7.round(1).sort_values("nota_media"))

# Q8 - CENÁRIO: PAID SEARCH COM A MESMA TAXA DOS OUTROS CANAIS

titulo("Q8 - POTENCIAL DA AÇÃO SOBRE PAID SEARCH (ação adiada no trade-off)")
ps = ped_cli[ped_cli["canal_aquisicao"] == "paid_search"]
outros_canais = ped_cli[ped_cli["canal_aquisicao"] != "paid_search"]

taxa_ps = ps["cancelado"].mean()
taxa_outros = outros_canais["cancelado"].mean()
evitaveis = len(ps) * (taxa_ps - taxa_outros)
ticket_canc_ps = ps.loc[ps["cancelado"], "valor_total"].mean()
nova_taxa = (ped_cli["cancelado"].sum() - evitaveis) / len(ped_cli)

print(f"Taxa paid search: {taxa_ps:.1%} | demais canais: {taxa_outros:.1%}")
print(f"Cancelamentos evitáveis em 24 meses: {evitaveis:.0f} (~{evitaveis / 2:.0f} por ano)")
print(f"Valor desses pedidos: R$ {evitaveis * ticket_canc_ps:,.0f} "
      f"(~R$ {evitaveis * ticket_canc_ps / 2:,.0f} por ano)")
print(f"Taxa geral de cancelamento: {ped_cli['cancelado'].mean():.1%} -> {nova_taxa:.1%}")

print(f"\nGráficos salvos em {PASTA_GRAFICOS}/")
