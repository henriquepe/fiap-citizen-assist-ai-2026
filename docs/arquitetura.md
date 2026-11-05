# Arquitetura e busca

## Fluxo

Arquivo JSON → validação → lista de registros → índices por ID/tema/termos → entrada → validação de consulta → filtro opcional → ranking → resposta, desambiguação ou abstenção → fonte e limites.

Cada registro contém `id`, `tema`, `subtema`, `pergunta`, `palavras_chave`, `orientacao`, `fonte`, `verificado_em` e `relacionados`. São 15 registros, cinco em cada tema. A hierarquia é implementada como dicionários aninhados; os relacionados formam um grafo dirigido de navegação. Não há busca de menor caminho. A validação recusa lista vazia, campos ausentes, tipos errados, IDs duplicados, referências inexistentes, data inválida e fonte fora de HTTPS gov.br. O domínio é uma barreira de origem, não prova automática da correção do conteúdo.

## Ranking reproduzível

1. Converter para minúsculas e remover acentos. Uniformizar gov.br e Fala.BR.
2. Remover palavras funcionais e aplicar pequeno mapa de sinônimos. Tokens únicos são conjuntos; repetição não aumenta a pontuação.
3. Indexar termos da pergunta canônica e palavras-chave, sem usar a orientação para inflar correspondência.
4. Peso de termo conhecido: `idf(t)=1+ln((N+1)/(df(t)+1))`, N=15.
5. Pontuação: soma dos pesos dos termos da consulta presentes no registro / soma dos pesos de todos os termos da consulta. Termos desconhecidos recebem `1+ln(N+1)`, penalizando consultas com muita informação não coberta.
6. Se a melhor cobertura for menor que 0,45, abster-se. Se outros resultados estiverem a menos de 0,13 do primeiro, mostrar até cinco IDs para escolha. Esses limiares são heurísticos, não probabilidades de correção.
7. Ordenar por pontuação, quantidade de termos comuns e ID para comportamento determinístico. O desempate por ID só ordena opções; não oculta ambiguidade. Consulta por ID válido seleciona diretamente o assunto, respeitando o filtro de tema.

Construção dos índices: O(total de termos). Consulta percorre os registros candidatos e ordena até N resultados: O(N·Q + N log N), com Q termos da consulta. Para 15 registros, a simplicidade favorece inspeção e manutenção. Não se justifica uma base vetorial ou um modelo remoto.

## Confiabilidade e privacidade

Entradas vazias, maiores que 500 caracteres, com controles ou padrões de CPF/e-mail/senha recebem mensagens específicas. A consulta não é persistida nem enviada a serviços. Os testes usam entradas fictícias. A proteção não reconhece todo dado pessoal possível: não digitar informações sensíveis. O terminal do usuário pode manter histórico visual.

A orientação é copiada do registro validado, sem geração de novos fatos. A resposta B inclui assunto, orientação, fonte, data de curadoria, três relacionados e aviso. A aplicação não verifica a disponibilidade da URL em tempo real. Links e regras devem ser revistos periodicamente; casos individuais exigem atendimento do órgão responsável.
