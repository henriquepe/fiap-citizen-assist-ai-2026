# Dois modelos de instrução de resposta

As instruções abaixo foram implementadas como formatação determinística em `Assistente.formatar`, sem chamada a um modelo externo. Elas orientam exclusivamente a apresentação de informação já presente na base.

## Modelo A — orientação concisa

> Papel: assistente acadêmico de orientação cidadã. Receba um registro validado. Apresente sua orientação sem acrescentar fatos. Inclua a URL oficial e o aviso de ausência de vínculo institucional. Se não houver correspondência confiável, informe o limite e sugira temas. Não solicite dados pessoais.

Formato: orientação → fonte → aviso. Vantagem: menor volume textual. Limite: não explicita a data de curadoria nem oferece navegação direta por relacionados.

## Modelo B — orientação estruturada (adotado)

> Papel: assistente acadêmico de orientação cidadã. Use somente o registro recuperado e validado. Organize em ASSUNTO, ORIENTAÇÃO, FONTE, VERIFICADA EM, CONTINUAR e LIMITES. Preserve a data da curadoria, sem tratá-la como atualização automática. Mostre assuntos relacionados por ID. Diante de empate, solicite escolha; sem cobertura, diga que não sabe. Não invente etapas, prazos, documentos ou custos, e não solicite dados pessoais.

Formato explícito facilita localizar origem e próximo passo; maior extensão pode exigir simplificação em telas pequenas. A validação da busca ocorre antes da formatação, portanto A e B compartilham a taxa de acerto e as abstenções.

## Comparação executada

`src/avaliar.py` gera os dois textos para cada pergunta respondida do conjunto de 30 casos. As saídas literais e os critérios estão em `comparacao_prompts.json`: presença de URL, data identificada e continuidade. Ambos têm fonte e aviso; somente B apresenta data e relacionados. Nos casos G01, D02 e P01, por exemplo, o conteúdo factual se mantém e a estrutura muda. Não se mediu preferência, tempo de leitura ou compreensão humana.

A escolha de B é técnica e provisória: rastreabilidade e navegação são requisitos do projeto. Um teste com pessoas deve confirmar a clareza e comparar uma versão resumida com expansão opcional.
