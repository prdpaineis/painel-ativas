"""Gera os dados do Painel de Processos a partir do Odoo (leitura via XML-RPC).

Lê ../.env (ver AGENTE.md na raiz do projeto), busca os casos e movimentações
ativos e grava painel/data.js e painel/mov.js — os dois arquivos que
painel.html carrega para montar o dashboard.

Uso:
    pip install -r ../requirements.txt
    python gerar_painel.py

Depois é só abrir painel.html num servidor local (ex.: `python -m http.server`
nesta pasta) ou publicar o conteúdo como Artifact.
"""
import json
import os
import xmlrpc.client
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

URL = os.environ["ODOO_URL"]
DB = os.environ["ODOO_DB"]
LOGIN = os.environ["ODOO_LOGIN"]
KEY = os.environ["ODOO_API_KEY"]

CTX = {"lang": "pt_BR", "tz": "America/Sao_Paulo"}
BATCH = 200  # ver AGENTE.md secao 4: nunca traga tudo de uma vez

CASE_FIELDS = [
    "name", "numero_processo", "cliente_id", "parte_adversa_id", "fase_id",
    "situacao_id", "comarca_id", "estado_id", "via_processual", "justica",
    "data_distribuicao", "data_citacao", "create_date", "valor_causa",
    "triagem_status", "prioridade", "sistema_eletronico",
]

MOV_FIELDS = [
    "caso_id", "numero_processo", "tipo", "origem", "data", "data_publicacao",
    "prazo_judicial", "lida", "create_date", "tipo_publicacao",
]


def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, LOGIN, KEY, {})
    if not uid:
        raise SystemExit("Login recusado: confira ODOO_LOGIN / ODOO_API_KEY no .env")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

    def call(model, method, *args, **kwargs):
        kwargs.setdefault("context", CTX)
        return models.execute_kw(DB, uid, KEY, model, method, list(args), kwargs)

    return call


def fetch_all(call, model, domain, fields, order="create_date desc"):
    total = call(model, "search_count", domain)
    rows = []
    offset = 0
    while offset < total:
        rows.extend(call(model, "search_read", domain, fields=fields,
                          limit=BATCH, offset=offset, order=order))
        offset += BATCH
    return rows


def m2o_name(v):
    return v[1] if v else None


def build_cases_js(cases):
    out = [{
        "id": c["id"],
        "n": c["name"],
        "proc": c["numero_processo"] or None,
        "cli": m2o_name(c["cliente_id"]),
        "adv": m2o_name(c["parte_adversa_id"]),
        "fase": m2o_name(c["fase_id"]),
        "sit": m2o_name(c["situacao_id"]),
        "com": m2o_name(c["comarca_id"]),
        "uf": m2o_name(c["estado_id"]),
        "via": c["via_processual"] or None,
        "just": c["justica"] or None,
        "dist": c["data_distribuicao"] or None,
        "cit": c["data_citacao"] or None,
        "criado": c["create_date"],
        "valor": c["valor_causa"],
        "triagem": c["triagem_status"],
        "prio": c["prioridade"],
        "sist": c["sistema_eletronico"] or None,
    } for c in cases]
    return "const CASES = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"


def build_movs_js(movs, case_by_id):
    out = []
    for m in movs:
        caso_id = m["caso_id"][0] if m["caso_id"] else None
        caso = case_by_id.get(caso_id)
        out.append({
            "id": m["id"],
            "casoId": caso_id,
            "ref": caso["name"] if caso else None,
            "cli": m2o_name(caso["cliente_id"]) if caso else None,
            "proc": m["numero_processo"] or None,
            "tipo": m["tipo"],
            "tipoPub": m["tipo_publicacao"] or None,
            "origem": m["origem"],
            "data": m["data"] or None,
            "dataPub": m["data_publicacao"] or None,
            "prazo": m["prazo_judicial"] or None,
            "lida": m["lida"],
            "criado": m["create_date"],
        })
    return "const MOVS = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"


def main():
    call = connect()

    cases = fetch_all(call, "juridico.caso", [("active", "=", True)], CASE_FIELDS)
    (BASE_DIR / "data.js").write_text(build_cases_js(cases), encoding="utf-8")

    movs = fetch_all(call, "juridico.movimentacao", [("active", "=", True)], MOV_FIELDS)
    case_by_id = {c["id"]: c for c in cases}
    (BASE_DIR / "mov.js").write_text(build_movs_js(movs, case_by_id), encoding="utf-8")

    nao_lidas = sum(1 for m in movs if not m["lida"])
    print(f"casos ativos: {len(cases)}")
    print(f"movimentações: {len(movs)} ({nao_lidas} não lidas)")
    print(f"gravado em: {BASE_DIR / 'data.js'}")
    print(f"gravado em: {BASE_DIR / 'mov.js'}")


if __name__ == "__main__":
    main()
