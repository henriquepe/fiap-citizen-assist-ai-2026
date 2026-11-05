"""Avaliação reproduzível: casos fixos, tempo medido e comparação de formatos."""
import csv
import json
import statistics
import subprocess
import sys
from time import perf_counter
from sistema import RAIZ,Assistente,carregar_base


def avaliar():
    assistente=Assistente(carregar_base(RAIZ/'data/base_conhecimento.json'))
    casos=json.loads((RAIZ/'data/perguntas_teste.json').read_text())
    linhas=[];comparacao=[]
    for t in casos:
        inicio=perf_counter()
        resposta=assistente.consultar(t['pergunta'])
        ms=(perf_counter()-inicio)*1000
        ok=resposta['estado']==t['estado_esperado'] and (t['id_esperado'] is None or resposta['ids']==[t['id_esperado']])
        texto=assistente.formatar(resposta)
        linhas.append({**t,'estado_obtido':resposta['estado'],'ids_obtidos':','.join(resposta['ids']),
                       'acerto':bool(ok),'tempo_ms':round(ms,6),'resposta_obtida':texto})
        if resposta['estado']=='respondida':
            a=assistente.formatar(resposta,'A');b=assistente.formatar(resposta,'B')
            comparacao.append(dict(caso=t['id'],modelo_a=a,modelo_b=b,
                                   a_tem_fonte='https://' in a,b_tem_fonte='https://' in b,
                                   a_tem_data='VERIFICADA EM:' in a,b_tem_data='VERIFICADA EM:' in b,
                                   a_tem_continuidade='CONTINUAR:' in a,b_tem_continuidade='CONTINUAR:' in b))
    resumo=dict(casos=len(linhas),acertos=sum(x['acerto'] for x in linhas),
                taxa_acerto_pct=100*sum(x['acerto'] for x in linhas)/len(linhas),
                tempo_medio_ms=statistics.mean(x['tempo_ms'] for x in linhas),
                tempo_maximo_ms=max(x['tempo_ms'] for x in linhas),
                data='2026-11-05',metodo='1 consulta local por caso, base carregada antes da medição; não inclui rede nem tempo humano')
    docs=RAIZ/'docs';docs.mkdir(exist_ok=True)
    (docs/'resultados_testes.json').write_text(json.dumps(linhas,ensure_ascii=False,indent=2))
    (docs/'indicadores.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2))
    (docs/'comparacao_prompts.json').write_text(json.dumps(comparacao,ensure_ascii=False,indent=2))
    with (docs/'resultados_testes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=linhas[0]);w.writeheader();w.writerows(linhas)
    # Roteiro de tarefas automatizado: não é pesquisa com uma pessoa real.
    tarefas=[
        ('Escolher Documentos e consultar um ID','/menu\n2\nD02\n/sair\n','primeira emissão em papel'),
        ('Recuperar-se de opção inválida','/menu\n9\nG01\n/sair\n','ASSUNTO: Como criar'),
        ('Desambiguar CIN pelo identificador','cin\nD03\n/sair\n','versão digital da CIN'),
        ('Perguntar fora do escopo e retornar','Qual a cotação do dólar?\n/menu\n1\nG03\n/sair\n','recuperação de senha'),
        ('Tratar pergunta vazia','\n/sair\n','Digite uma pergunta')
    ]
    resultados=[]
    for titulo,entrada,esperado in tarefas:
        inicio=perf_counter()
        r=subprocess.run([sys.executable,str(RAIZ/'src/sistema.py')],input=entrada,text=True,capture_output=True)
        resultados.append(dict(tarefa=titulo,roteiro=entrada,concluida=r.returncode==0 and esperado in r.stdout,
                               tempo_automatizado_ms=round((perf_counter()-inicio)*1000,3),transcricao=r.stdout))
    (docs/'roteiro_usabilidade.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2))
    print(json.dumps(resumo,ensure_ascii=False,indent=2))
    print(f'Roteiro de uso: {sum(x["concluida"] for x in resultados)}/{len(resultados)} tarefas concluídas.')
    for x in linhas:
        if not x['acerto']: print(f"LIMITAÇÃO {x['id']}: {x['pergunta']} → {x['estado_obtido']} {x['ids_obtidos']}")


if __name__=='__main__': avaliar()
