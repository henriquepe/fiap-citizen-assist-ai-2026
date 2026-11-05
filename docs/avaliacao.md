# Avaliação reproduzível

Data: 05/11/2026. Ambiente: Python 3.14, macOS, execução local. Não representa homologação do serviço público.

## Plano e critério

`data/perguntas_teste.json` contém 30 perguntas fixas com estado e ID esperados. São consultas diretas, paráfrases e limites: vazio, ambiguidade, falta de cobertura e dados pessoais. Um acerto exige estado esperado e, quando há resposta única, o ID exato. Essa métrica mede recuperação e controle de fluxo; não mede compreensão humana.

`python src/avaliar.py` registra pergunta, esperado, obtido, resposta completa, classificação e tempo em JSON/CSV. Mede-se uma chamada `consultar` por caso com `perf_counter`, depois de carregar a base, sem formatação, rede nem interação humana. Não há aquecimento estatístico ou repetições suficientes para estimar percentis confiáveis. Os tempos da execução original estão em `indicadores.json`.

Resultado: **28/30 = 93,33%**. Média local aproximadamente **0,013 ms**, máximo aproximadamente 0,106 ms na execução de referência. Reexecutar pode alterar o tempo, mas deve preservar a classificação.

## Falhas preservadas

| Caso | Pergunta | Esperado | Obtido | Interpretação |
|---|---|---|---|---|
| T25 | Quero ver meus vínculos empregatícios | D05 | sem_resposta | Vocabulário não coberto pelo mapa lexical |
| T26 | Quero agradecer pelo bom serviço | P03 | sem_resposta | Paráfrase sem correspondência suficiente |

As falhas são abstenções e não orientações factuais incorretas, mas continuam erros da tarefa. Acrescentar esses sinônimos pode melhorar o conjunto conhecido e também gerar ambiguidades; a avaliação seguinte deve usar perguntas novas, separadas das usadas para ajustar o algoritmo. O mesmo processo elaborou base e testes, criando viés favorável. Não se alega generalização a toda linguagem natural.

## Facilidade de uso por roteiro

Foi usada a alternativa de roteiro de tarefas prevista no enunciado, **sem participante humano**. Cinco sequências de entradas são executadas no programa real por subprocesso. Resultado: 5/5 concluídas, com transcrição em `roteiro_usabilidade.json`.

| Tarefa | Evidência de conclusão | Dificuldade identificada |
|---|---|---|
| Escolher Documentos e D02 | Orientação da primeira emissão | Precisa aprender os IDs |
| Digitar opção 9 e recuperar com G01 | Mensagem de erro e resposta posterior | Menu exige número, não o nome do tema |
| Perguntar “cin” e escolher D03 | Desambiguação e resposta digital | Uma pergunta ampla requer outro turno |
| Sair do escopo e voltar ao menu | Abstenção e recuperação de senha | Cobertura pequena pode frustrar |
| Enviar pergunta vazia | Solicitação de entrada válida | Não há exemplos contextuais na mensagem curta |

Tempos automatizados não são tempos de tarefa de uma pessoa. O sucesso do roteiro mostra navegação funcional, não usabilidade comprovada. A interface sem cores obrigatórias e com rótulos textuais favorece acesso, mas leitores de tela, alfabetização digital e compreensão ainda precisam ser avaliados.

## Testes de código e melhorias

Oito testes verificam carga/estrutura, referências e temas, dados inválidos, proteção de domínio, entradas, filtro e desambiguação, fontes e limites. A transcrição está em `testes_unitarios.txt`.

Melhorias prioritárias: (1) revisão periódica de conteúdo e links com responsável/data; (2) ampliar vocabulário e manter conjunto de avaliação independente; (3) testar com pessoas e tecnologia assistiva; (4) comparar limiares usando precisão, cobertura e custo de resposta errada. Uma futura API/LLM teria de preservar fontes e passar por avaliação adicional.
