**Para:** Helena Vasconcelos
**De:** Felipe Augusto Maruski Salazar
**Assunto:** Arrumar a métrica de cancelamento

**Q1. Perguntas antes dos dados**
1. Camila, o aumento de 40% é no número absoluto de pedidos cancelados ou na taxa?
2. Quais status cada um considera "cancelado", e contam pedidos ou R$?
3. Os cancelamentos foram atribuídos pela data do pedido ou do cancelamento, e qual período cada relatório compara?

**Recomendação (Q8).** Arrumar a casa: definir uma métrica oficial de cancelamento (status, unidade e data de referência) e reconciliar pedidos e itens antes de reabrir o data room. A rodada parou por números divergentes; sem números válidos, nenhuma estratégia se sustenta.

**Por quê**

**1. Os números atuais não se sustentam (Q2, Q5, Q6).** O "1 em 6" do fundo é real (16,9%), mas nenhum número da diretoria é reproduzível; provavelmente, cada área usa sua definição. Pela data do pedido, os cancelados caem 20% (1.407 → 1.130) e a taxa sobe de 16,8% para 17,1%; sem nov/2023 (4,2x o normal), a quantidade sobe 12,5%. O valor_total diverge dos itens em 99,9% dos pedidos (R$ 38 mi vs R$ 166 mi); adoto o valor_total, único que reproduz o B2B 6x maior (6,15x vs 0,99x). 9% dos pedidos estão "em trânsito" desde jan/2023: a taxa pode estar subestimada.

**2. O problema real está concentrado (Q4).** Paid search gera 26% dos pedidos e 48% dos cancelamentos (30,7% vs ~12%), com ticket e cupom iguais.

**3. Outras explicações não se sustentam (Q3, Q7).** O pico de chamados (nov–dez/2023) segue o volume de novembro; a DeltaFornece tem as piores notas (2,3), mas não mais chamados. Os rankings de categoria divergem, mas o de receita usa preços implausíveis; confio no de volume.

**Trade-off.** Adiamos a revisão do paid search, que pode evitar até ~373 cancelamentos por ano (~R$ 1 mi em pedidos) e levar a taxa a 11,9%. É a próxima ação.

**O que falta (Q9).** Não reproduzi os números da diretoria nem medi a taxa real. Pediria: (1) consultas de Growth e Financeiro; (2) histórico de status com datas; (3) origem de nov/2023 e da divergência de valores.

**Uso de IA.** Usei o Claude, com case e base como contexto, para gerar código, criticar minhas perguntas e refinar respostas passo a passo; conferi cada número na saída. Ele supôs que o volume crescera (estava estável) e afirmou a causa da divergência como fato; tratei como hipótese. A triangulação do "6x" inverteu minha intuição de confiar nos itens.
