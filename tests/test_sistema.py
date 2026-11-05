import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from sistema import RAIZ,Assistente,BaseInvalida,carregar_base


class Confiabilidade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados=carregar_base(RAIZ/'data/base_conhecimento.json')
        cls.a=Assistente(cls.dados)

    def test_base_minima_e_relacoes(self):
        self.assertGreaterEqual(len(self.dados),15)
        self.assertGreaterEqual(len(self.a.hierarquia),3)
        self.assertTrue(all(len(x['relacionados'])>=3 for x in self.dados))

    def test_recuperacao_cita_fonte_da_base(self):
        r=self.a.consultar('Esqueci a senha gov.br')
        self.assertEqual(r['ids'],['G03'])
        s=self.a.formatar(r)
        self.assertIn(self.a.por_id['G03']['fonte'],s)
        self.assertIn('2026-11-05',s)

    def test_ambiguidade_nao_escolhe_por_conta_propria(self):
        r=self.a.consultar('cin')
        self.assertEqual(r['estado'],'ambigua')
        self.assertEqual(set(r['ids']),{'D01','D02','D03'})

    def test_pergunta_fora_da_base_nao_inventa(self):
        r=self.a.consultar('Cotação dólar euro amanhã')
        self.assertEqual(r['estado'],'sem_resposta')
        self.assertEqual(r['ids'],[])

    def test_privacidade_e_entradas(self):
        for q in ('meu CPF 12345678900','e-mail teste@example.org','minha senha é segredo'):
            self.assertEqual(self.a.consultar(q)['estado'],'privacidade')
        self.assertEqual(self.a.consultar('')['estado'],'vazia')
        self.assertEqual(self.a.consultar('x'*501)['estado'],'invalida')
        self.assertEqual(self.a.consultar('\x1b[31mtexto')['estado'],'invalida')

    def test_filtro_de_tema(self):
        self.assertEqual(self.a.consultar('G01','Documentos')['estado'],'sem_resposta')
        self.assertEqual(self.a.consultar('D02','Documentos')['ids'],['D02'])

    def test_json_invalido_ausente_e_vazio(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'base.json'
            with self.assertRaises(BaseInvalida): carregar_base(p)
            for texto in ('', '[]','{errado}', '{}'):
                p.write_text(texto)
                with self.assertRaises(BaseInvalida): carregar_base(p)

    def test_campos_fontes_e_relacoes_invalidos(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'base.json'
            for campo,valor in [('orientacao',''),('fonte','https://gov.br.example.com'),('verificado_em','amanhã'),('relacionados',['Z99'])]:
                dados=copy.deepcopy(self.dados);dados[0][campo]=valor
                p.write_text(json.dumps(dados))
                with self.assertRaises(BaseInvalida): carregar_base(p)


if __name__=='__main__': unittest.main(verbosity=2)
