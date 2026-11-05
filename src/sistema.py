"""Citizen Assist AI — recuperação local de orientações, sem geração de fatos."""
import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

RAIZ=Path(__file__).resolve().parents[1]
AVISO='Protótipo acadêmico, sem vínculo com órgãos públicos. Confirme os requisitos atuais na fonte oficial. Não informe dados pessoais.'
STOP=set('a o as os um uma uns umas de do da dos das no na nos nas em e para por com que qual quais como onde quero preciso posso minha meu seus suas eu ao se sobre saber fazer ter esta este'.split())
SINONIMOS={'cadastrar':'criar','cadastro':'criar','cadastre':'criar','criacao':'criar',
           'perdi':'recuperar','esqueci':'recuperar','esquecida':'recuperar','recuperacao':'recuperar',
           'custos':'custo','preco':'custo','pagar':'custo','custa':'custo','gratis':'gratuita',
           'digital':'digital','ctps':'trabalho','carteira':'carteira','reclamar':'reclamacao',
           'elogiar':'elogio','sugerir':'sugestao','melhoria':'sugestao','acompanhar':'acompanhar',
           'andamento':'acompanhar','consultar':'consulta','solicitar':'solicitacao','duplo':'duas',
           'fator':'etapas','2fa':'etapas','senha':'senha','proteger':'seguranca','identidade':'cin'}


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD',texto.lower()) if not unicodedata.combining(c))


def tokens(texto):
    texto=normalizar(texto).replace('gov.br','govbr').replace('gov br','govbr').replace('fala.br','falabr').replace('fala br','falabr')
    return {SINONIMOS.get(t,t) for t in re.findall(r'[a-z0-9]+',texto) if t not in STOP}


class BaseInvalida(ValueError): pass


def carregar_base(caminho):
    try:
        dados=json.loads(Path(caminho).read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError) as e:
        raise BaseInvalida('Base ausente, ilegível ou JSON inválido.') from e
    if not isinstance(dados,list) or not dados:
        raise BaseInvalida('A base precisa conter uma lista não vazia.')
    ids=set()
    campos=('id','tema','subtema','pergunta','palavras_chave','orientacao','fonte','verificado_em','relacionados')
    for r in dados:
        if not isinstance(r,dict) or any(k not in r for k in campos):
            raise BaseInvalida('Registro sem campos obrigatórios.')
        if any(not isinstance(r[k],str) or not r[k].strip() for k in ('id','tema','subtema','pergunta','orientacao','fonte','verificado_em')):
            raise BaseInvalida('Campo textual vazio ou inválido.')
        if r['id'] in ids: raise BaseInvalida('Identificador duplicado.')
        ids.add(r['id'])
        for campo in ('palavras_chave','relacionados'):
            if not isinstance(r[campo],list) or any(not isinstance(x,str) or not x.strip() for x in r[campo]):
                raise BaseInvalida('Listas inválidas.')
        if not r['palavras_chave']: raise BaseInvalida('Informe palavras-chave.')
        u=urlparse(r['fonte'])
        if u.scheme!='https' or not u.hostname or not (u.hostname=='gov.br' or u.hostname.endswith('.gov.br')):
            raise BaseInvalida('A fonte deve ser uma página HTTPS oficial gov.br.')
        try: date.fromisoformat(r['verificado_em'])
        except ValueError as e: raise BaseInvalida('Data de verificação inválida.') from e
    if any(x not in ids for r in dados for x in r['relacionados']):
        raise BaseInvalida('Há relação apontando para registro inexistente.')
    return dados


class Assistente:
    def __init__(self,dados):
        self.dados=dados
        self.por_id={r['id']:r for r in dados}
        self.documentos={r['id']:tokens(r['pergunta']+' '+' '.join(r['palavras_chave'])) for r in dados}
        frequencia=Counter(t for ts in self.documentos.values() for t in ts)
        self.idf={t:1+math.log((len(dados)+1)/(n+1)) for t,n in frequencia.items()}
        self.hierarquia={}
        for r in dados:
            self.hierarquia.setdefault(r['tema'],{}).setdefault(r['subtema'],[]).append(r['id'])

    def consultar(self,pergunta,tema=None):
        if not pergunta.strip(): return dict(estado='vazia',ids=[],mensagem='Digite uma pergunta ou escolha um tema.')
        if len(pergunta)>500: return dict(estado='invalida',ids=[],mensagem='Use até 500 caracteres.')
        if any(ord(c)<32 for c in pergunta): return dict(estado='invalida',ids=[],mensagem='Use texto em uma única linha, sem caracteres de controle.')
        if re.search(r'\b\d{3}[. ]?\d{3}[. ]?\d{3}[- ]?\d{2}\b|\S+@\S+|minha senha (?:e|é|:)\s*\S+',pergunta,re.I):
            return dict(estado='privacidade',ids=[],mensagem='Remova CPF, e-mail ou senha. Faça apenas uma pergunta geral; o texto não será gravado.')
        if tema is not None and tema not in self.hierarquia:
            return dict(estado='invalida',ids=[],mensagem='Tema inexistente. Use o menu de temas.')
        candidatos=[r for r in self.dados if tema is None or r['tema']==tema]
        identificador=pergunta.strip().upper()
        if identificador in self.por_id and self.por_id[identificador] in candidatos:
            return dict(estado='respondida',ids=[identificador],score=1.0)
        consulta=tokens(pergunta)
        if not consulta: return dict(estado='sem_resposta',ids=[],mensagem='Não há termos suficientes. Seja mais específico.')
        ranking=[]
        denominador=sum(self.idf.get(t,1+math.log(len(self.dados)+1)) for t in consulta)
        for r in candidatos:
            termos=self.documentos[r['id']]
            comum=consulta & termos
            score=sum(self.idf[t] for t in comum)/denominador
            if comum: ranking.append((score,len(comum),r['id']))
        ranking.sort(key=lambda x:(-x[0],-x[1],x[2]))
        if not ranking or ranking[0][0]<0.45:
            return dict(estado='sem_resposta',ids=[],mensagem='Não encontrei orientação confiável nesta base. Consulte um dos temas do menu ou um canal oficial.')
        primeiro=ranking[0]
        proximos=[x for x in ranking if primeiro[0]-x[0]<0.13]
        if len(proximos)>1:
            return dict(estado='ambigua',ids=[x[2] for x in proximos[:5]],mensagem='Encontrei mais de um assunto. Escolha um identificador para continuar.')
        return dict(estado='respondida',ids=[primeiro[2]],score=round(primeiro[0],3))

    def formatar(self,resultado,modelo='B'):
        if resultado['estado']!='respondida':
            opcoes='\n'.join(f"  {i}: {self.por_id[i]['pergunta']}" for i in resultado['ids'])
            return resultado['mensagem']+('\n'+opcoes if opcoes else '')+'\nTemas: '+', '.join(self.hierarquia)+'\n'+AVISO
        r=self.por_id[resultado['ids'][0]]
        if modelo=='A':
            return f"{r['orientacao']}\nFonte: {r['fonte']}\n{AVISO}"
        relacionados='; '.join(f"{i} — {self.por_id[i]['pergunta']}" for i in r['relacionados'])
        return (f"ASSUNTO: {r['pergunta']}\nORIENTAÇÃO: {r['orientacao']}\n"
                f"FONTE: {r['fonte']}\nVERIFICADA EM: {r['verificado_em']}\n"
                f"CONTINUAR: {relacionados}\nLIMITES: {AVISO}")


def executar_menu(assistente):
    print('CITIZEN ASSIST AI | Orientação cidadã com fontes\n'+AVISO)
    temas=list(assistente.hierarquia)
    tema=None
    while True:
        print('\n/menu: temas | /todos: remover filtro | /sair: encerrar | Digite pergunta ou ID')
        try: entrada=input('Você: ').strip()
        except (EOFError,KeyboardInterrupt): print('\nAté logo.'); return
        if entrada=='/sair': return
        if entrada=='/todos': tema=None; print('Todos os temas disponíveis.'); continue
        if entrada=='/menu':
            for n,t in enumerate(temas,1): print(f'{n}. {t}')
            try: escolha=input('Número do tema: ').strip()
            except (EOFError,KeyboardInterrupt): return
            if not escolha.isdigit() or not 1<=int(escolha)<=len(temas):
                print('Opção inexistente. Escolha um dos números apresentados.');continue
            tema=temas[int(escolha)-1]
            for sub,ids in assistente.hierarquia[tema].items():
                print(sub+':')
                for i in ids: print(f"  {i} — {assistente.por_id[i]['pergunta']}")
            continue
        resultado=assistente.consultar(entrada,tema)
        print(assistente.formatar(resultado))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,default=RAIZ/'data/base_conhecimento.json')
    p.add_argument('--pergunta');p.add_argument('--modelo',choices=['A','B'],default='B')
    args=p.parse_args()
    try: assistente=Assistente(carregar_base(args.base))
    except BaseInvalida as erro: print('Não foi possível iniciar:',erro,file=sys.stderr);return 1
    if args.pergunta is not None: print(assistente.formatar(assistente.consultar(args.pergunta),args.modelo))
    else: executar_menu(assistente)
    return 0


if __name__=='__main__': raise SystemExit(main())
