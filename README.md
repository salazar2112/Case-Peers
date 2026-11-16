# Case OrbitShop: análise de cancelamentos

Análise da base `Base_Dados_OrbitShop_v3.xlsx` (jan/2023 a dez/2024) para o case individual de Digital Consulting da Peers. O memo com as respostas está em `memo.pdf` (fonte: `memo.md`).

## Como reproduzir

Requisitos: Python 3.12 (ou superior) e a planilha na mesma pasta do código.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python base.py
```

O script imprime todas as tabelas no terminal e salva os gráficos na pasta `graficos/`.

## Estrutura

| Arquivo | Conteúdo |
| --- | --- |
| `memo.md` / `memo.pdf` | Memo de 1 página (Q1 a Q9 e uso de IA) |
| `base.py` | Todo o código, na ordem: carga, limpeza, raio-X e uma seção por pergunta |
| `achados.md` | Registro detalhado dos problemas de qualidade da base |
| `graficos/` | `q2_status.png`, `q2_status_mensal.png`, `q5_volume_mensal.png` |
| `requirements.txt` | Versões exatas das bibliotecas |

## Decisões de tratamento dos dados

| # | Problema encontrado | Registros | Decisão |
| --- | --- | --- | --- |
| 1 | Datas armazenadas como texto | todas | Convertidas com `pd.to_datetime` |
| 2 | `data_resolucao` vazia nos tickets abertos e escalados | 1.653 | Nulo esperado (chamado não resolvido); mantido |
| 3 | `comentario` vazio nas avaliações | 1.679 | Campo opcional; mantido |
| 4 | `desconto_aplicado` vazio nos itens | 301 (<1%) | Tratado como 0. Premissa declarada: existem 2.567 itens com 0 explícito, então o vazio é ambíguo |
| 5 | `valor_total` vazio nos pedidos | 79 (0,5%) | Excluídos das contas de valor, para não inventar dados |
| 6 | `valor_total` não bate com a soma dos itens | 14.919 de 14.921 | `valor_total` adotado como fonte oficial (ver abaixo) |
| 7 | Status "em_transito" em todos os meses desde jan/2023 | 1.371 (9,1%) | Mantido como desfecho desconhecido; taxa real pode estar subestimada |
| 8 | Preços médios implausíveis nos itens (ex.: livros a R$ 1.792) | todos | Itens usados só para proporções e rankings (Q3), com ressalva |

## Por que `valor_total` e não a soma dos itens

- A soma dos itens dá R$ 165,9 mi; o `valor_total`, R$ 38,4 mi. Só 2 pedidos batem.
- A correlação entre as duas fontes é ≈ 0 (−0,01). A hipótese "valor_total = desconto" foi testada e descartada (correlação −0,001).
- Triangulação com um fato dado pela CEO (pedido B2B vale ~6x o B2C): `valor_total` dá 6,15x; a soma dos itens dá 0,99x.
- Teste de sanidade: pela soma dos itens, o ticket médio de pessoa física seria R$ 11 mil; pelo `valor_total`, R$ 1,3 mil.

## Definições e premissas

- **Cancelamento:** status `cancelado`, contado pela data do pedido (a base não tem data de cancelamento). Devolvidos não entram, mas o memo mostra o efeito de somá-los (~24,5%).
- **Valor de um item:** `preco_praticado × quantidade × (1 − desconto_aplicado)`; o desconto é uma fração (máx. 0,30).
- **Pico mensal:** mês comparado com a mediana dos 24 meses (552 pedidos), não com a média, que é puxada pelo próprio pico.
- **Fornecedor x chamados:** um pedido "envolve" um fornecedor se tiver pelo menos um item dele. 67% dos pedidos têm mais de um fornecedor, então essa atribuição é indicativa.
- **Cenário da Q8:** cancelamentos evitáveis = pedidos de paid search × (taxa do paid search − taxa dos demais canais). É um potencial, não uma promessa.

## Onde está cada número do memo

| Número no memo | Seção do `base.py` |
| --- | --- |
| 16,9% cancelados; 1.407 → 1.130; 16,8% → 17,1% | Q2 |
| 4,2x em nov/2023; sem Black Friday; +12,5% sem nov/2023 | Q5 |
| R$ 38 mi vs R$ 166 mi; 6,15x vs 0,99x | Q6 e Triangulação |
| 9% em trânsito | Q2 (por ano e gráfico mensal) |
| Paid search 26% / 48% / 30,7% | Q4 |
| Pico de chamados nov–dez/2023 | Q5 (chamados por mês) |
| DeltaFornece nota 2,3 | Q7 |
| ~373 cancelamentos/ano, ~R$ 1 mi, taxa 11,9% | Q8 |

## Limitações

- A base não tem data de cancelamento nem histórico de status.
- Os números da Head de Growth (+40%) e do CFO (18% → 16%) não foram reproduzidos com nenhuma definição testada; seriam necessárias as consultas originais.
- A causa do pico de nov/2023 (duplicação, importação ou campanha) não pode ser confirmada com os dados disponíveis.
- Chamados são ligados ao pedido, não ao produto.

## Uso de IA

Detalhado no memo.
