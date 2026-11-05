# FIAP — Citizen Assist AI

## Grupo 7 · Global Solution 2 · 2026

**Integrante:** [Henrique Pires Espindola](https://github.com/henriquepe) — **RM568600**.  
**Coordenação:** [André Godoi Chiovato](https://www.linkedin.com/in/andregodoichiovato/). Tutoria: conforme cadastro acadêmico da turma.

## Descrição

Pessoas que não sabem por onde começar um serviço público precisam localizar orientação compreensível e verificar sua origem. Este protótipo de terminal recupera informações de uma base curada com **15 registros em três temas**: acesso digital, documentos e participação cidadã. Beneficia quem busca uma primeira orientação, sem coletar identificação nem realizar o serviço em seu nome.

A aplicação é acadêmica e não representa órgãos públicos. Não recebe documentos, não autentica cidadãos e não acessa contas governamentais. Sempre apresenta fonte e limite; informações atuais devem ser confirmadas no portal responsável.

## Organização e decisões técnicas

| Pasta | Conteúdo |
|---|---|
| `src/` | Sistema e avaliação reproduzível em Python |
| `data/` | Base curada e 30 perguntas de teste |
| `docs/` | Fontes, arquitetura, instruções A/B, uso de IA e evidências |
| `tests/` | Oito testes automatizados de invariantes e erros |

Somente biblioteca padrão do Python. JSON é legível e versionável; listas preservam a base, dicionários indexam IDs e hierarquia tema → subtema → registro. Cada assunto referencia pelo menos três assuntos relacionados. A busca normaliza acentos, usa sinônimos declarados e cobertura de termos ponderada por frequência inversa. Não existe LLM em execução. Pontuações próximas provocam desambiguação; cobertura insuficiente provoca abstenção. [Arquitetura e algoritmo](docs/arquitetura.md).

Foram comparadas duas instruções de resposta: A, concisa com fonte e aviso; B, estruturada com data e continuação. B é o padrão por tornar a origem e a navegação explícitas. Essa escolha decorre de comparação estrutural, não de preferência medida com usuários. [Instruções e comparação](docs/prompts.md).

## Executar

Python **3.10+**; validado em Python 3.14. Não requer chave, conta, pacote externo nem conexão para consultar a base já incluída.

```bash
python src/sistema.py
python src/sistema.py --pergunta "Como criar conta gov.br?"
python src/sistema.py --pergunta "D02" --modelo A
python src/avaliar.py
python -m unittest discover -s tests -v
```

No macOS/Linux, use `python3` se necessário. Execute da raiz do repositório. O programa também localiza a base a partir do próprio arquivo. Para outra base: `--base caminho.json`.

No menu, `/menu` apresenta três temas; informe 1, 2 ou 3. Digite um ID ou uma pergunta. `/todos` remove o filtro e `/sair` encerra. As mensagens não dependem de cor.

## Exemplos e erros

- `Como criar conta gov.br?` → orientação de criação, fonte oficial, data de verificação, relacionados e aviso.
- `D02` → primeira emissão da CIN em papel é gratuita; confirmação na fonte [Governo Digital](https://www.gov.br/governodigital/pt-br/identidade/cin).
- `cin` → apresenta assuntos possíveis; o usuário escolhe um ID, evitando resposta arbitrária.
- Entrada vazia → pede uma pergunta. Opção 9 no menu → informa opção inexistente.
- `Qual a cotação do dólar?` → informa ausência de resposta confiável e oferece temas.
- Base ausente/vazia/inconsistente → mensagem de falha de inicialização e código de saída 1.

Fonte e verificação referem-se à curadoria realizada em **05/11/2026**, não a consulta online automática. [Lista de fontes](docs/fontes.md).

## Testes, indicadores e limites

**28 acertos em 30 casos (93,33%)**, incluindo perguntas diretas, paráfrases, vazio, ambiguidade, privacidade e assunto fora da base. O tempo médio local foi aproximadamente **0,013 ms**, com a base já carregada e uma medição por caso. Não mede rede, experiência humana ou desempenho em produção. Os tempos variam a cada execução.

Duas paráfrases ficaram sem resposta: “Quero ver meus vínculos empregatícios” e “Quero agradecer pelo bom serviço”. Foram preservadas como falhas observadas. Cinco roteiros automatizados de uso foram concluídos; **não houve teste com pessoa real**. Oito testes de código passaram. [Plano, evidências e interpretação](docs/avaliacao.md).

A base pequena, o dicionário limitado de sinônimos e a ausência de atualização automática restringem a cobertura. Melhorias: ampliar a base com revisão periódica; validar novos sinônimos em conjunto separado; testar acessibilidade com pessoas; medir robustez em perguntas adversariais. A filtragem de dados pessoais cobre padrões comuns, não garante anonimização.

## Links e observações

- Vídeo de apresentação: **https://youtu.be/yWrGMyjaRxw** (YouTube, não listado).
- Uso de IA e validação: [docs/uso_ia.md](docs/uso_ia.md).
- **Participação na competição: [ ] Sim / [x] Não vamos participar.**

## Atribuição do modelo

Estrutura adaptada do [modelo oficial GLOBAL-SOLUTION-2](https://github.com/equipe1ccon/FIAP-PORTFOLIO-1CCON/tree/master/1CC-FEV/1CCOC/GLOBAL-SOLUTION-2), FIAP, sob [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). Foram substituídos os exemplos por dados, decisões e evidências deste projeto; pastas sem uso foram omitidas conforme orientação do modelo.
