"""Gera dados FICTÍCIOS para o painel, no mesmo formato de painel/data.js
e painel/mov.js — para demonstrar o dashboard sem expor caso real nenhum
(nome de parte, valor de causa, comarca etc. são todos inventados).

Uso:
    python gerar_mockup.py
    python -m http.server -d . 8000   # e abra painel.html
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
random.seed(42)

CLIENTES = ["Banco ABC Brasil S.A.", "Banco Santander S/A"]
FASES = ["Ajuizamento", "Conhecimento", "Encerramento", "Pré-processual"]
SITUACOES_POR_FASE = {
    "Ajuizamento": ["Em pesquisa patrimonial", "Pronto para elaborar inicial", "Aguardando protocolo"],
    "Conhecimento": ["Monitória — aguardando citação", "Cobrança — aguardando citação", "Aguardando recolhimento de custas"],
    "Encerramento": ["Encerrado sem ajuizamento", "Encerrado"],
    "Pré-processual": ["Aguardando solicitação de custas"],
}
VIAS = ["monitoria", "cobranca", "execucao"]
COMARCAS = ["Porto Alegre", "Caxias do Sul", "Canoas", "Pelotas", "Santa Maria", "Novo Hamburgo"]
TRIAGEM = ["incompleto", "erro", "processando", "feita", "sem_documentos"]
NOMES_FICTICIOS = [
    "José da Silva Exemplo", "Maria Modelo de Souza", "João Amostra Pereira",
    "Ana Fictícia Oliveira", "Carlos Teste Costa", "Fernanda Placeholder Lima",
]

def rand_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days), seconds=random.randint(0, 86399))

def build_cases(n, cliente, start_id):
    hoje = datetime(2026, 9, 15)
    inicio_base = datetime(2026, 6, 1)
    out = []
    for i in range(n):
        fase = random.choices(FASES, weights=[45, 15, 30, 2])[0]
        situacao = random.choice(SITUACOES_POR_FASE[fase])
        criado = rand_date(inicio_base, hoje)
        distribuido = None
        citado = None
        numero_processo = None
        if fase in ("Conhecimento", "Encerramento") or "protocolo" not in situacao:
            if random.random() < 0.55:
                distribuido = (criado + timedelta(days=random.randint(3, 40))).date().isoformat()
                numero_processo = f"5{random.randint(100000,999999)}-{random.randint(10,99)}.2026.8.21.{random.randint(1000,9999):04d}"
                if random.random() < 0.15:
                    citado = (datetime.fromisoformat(distribuido) + timedelta(days=random.randint(5, 30))).date().isoformat()
        out.append({
            "id": start_id + i,
            "n": f"CASO/2026/{start_id + i:05d}",
            "proc": numero_processo,
            "cli": cliente,
            "adv": random.choice(NOMES_FICTICIOS),
            "fase": fase,
            "sit": situacao,
            "com": random.choice(COMARCAS),
            "uf": "RS",
            "via": random.choice(VIAS),
            "just": "estadual",
            "dist": distribuido,
            "cit": citado,
            "criado": criado.strftime("%Y-%m-%d %H:%M:%S"),
            "valor": round(random.uniform(3000, 60000), 2),
            "triagem": random.choices(TRIAGEM, weights=[50, 15, 10, 15, 10])[0],
            "prio": random.choices(["0", "1", "2"], weights=[80, 15, 5])[0],
            "sist": random.choice(["pje", "esaj", None]),
        })
    return out

def build_movs(cases, n):
    hoje = datetime(2026, 9, 15, 14, 0, 0)
    tipos = ["andamento", "publicacao", "despacho", "decisao", "sentenca"]
    origens = ["api_tj", "dje", "manual", "robo"]
    out = []
    amostra = random.sample(cases, min(n, len(cases)))
    for i, caso in enumerate(amostra):
        criado = hoje - timedelta(hours=random.randint(1, 400))
        out.append({
            "id": i + 1,
            "casoId": caso["id"],
            "ref": caso["n"],
            "cli": caso["cli"],
            "proc": caso["proc"],
            "tipo": random.choice(tipos),
            "tipoPub": random.choice(["sentenca", "intimacao", "ato_ordinatorio", None]),
            "origem": random.choice(origens),
            "data": criado.date().isoformat(),
            "dataPub": criado.date().isoformat() if random.random() < 0.5 else None,
            "prazo": None,
            "lida": random.random() < 0.7,
            "criado": criado.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return out

def main():
    cases = build_cases(60, CLIENTES[0], 1) + build_cases(18, CLIENTES[1], 1000)
    movs = build_movs(cases, 12)

    (BASE_DIR / "data.js").write_text(
        "const CASES = " + json.dumps(cases, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    (BASE_DIR / "mov.js").write_text(
        "const MOVS = " + json.dumps(movs, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"casos ficticios: {len(cases)}")
    print(f"movimentacoes ficticias: {len(movs)}")

if __name__ == "__main__":
    main()
