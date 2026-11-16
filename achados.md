# Achados de qualidade da base

| # | Tabela | Coluna | Achado | Registros | Decisão |
|---|---|---|---|---|---|
| 1 | Todas | colunas de data | Datas armazenadas como texto | - | Convertidas com pd.to_datetime |
| 2 | Tickets_Suporte | data_resolucao | Vazia em todos os tickets abertos/escalados e só neles | 1.653 | Nulo esperado, mantido. Obs.: 41% dos tickets não resolvidos |
| 3 | Avaliacoes | comentario | Comentário vazio (campo opcional) | 1.679 | Nulo esperado, mantido |
| 4 | Itens_Pedido | desconto_aplicado | Vazio, ambíguo: existem 2.567 itens com 0 explícito, então vazio não significa necessariamente "sem desconto" | 301 (<1%) | [sua decisão + justificativa] |
| 5 | Pedidos | valor_total | Vazio | 79 | [sua decisão] |
| 6 | Pedidos x Itens_Pedido | valor_total vs soma dos itens | Só 2 de 14.921 pedidos batem; itens somam R$ 165,9 mi vs R$ 38,4 mi; correlação ≈ 0 | 14.919 | valor_total adotado como fonte oficial: reproduz B2B ≈ 6x (6,15x) e ticket B2C plausível; itens dão 0,99x e B2C de R$ 11 mil |
| 7 | Pedidos | status | Pedidos "em_transito" em todos os meses, inclusive jan/2023 (quase 2 anos depois): status provavelmente não atualizado | 1.371 (9,1%) | Mantidos como "desfecho desconhecido"; taxa de cancelamento real pode estar subestimada |
| 8 | Itens_Pedido | preco_praticado | Preços médios implausíveis e homogêneos entre categorias (ex.: Livros R$ 1.792, Alimentos R$ 1.356) | todas | Reforça #6: itens usados só para proporções/rankings, com ressalva |
