# Painel de Processos

Dashboard estático (HTML+JS, sem build) que lê a carteira de processos do Odoo
(módulo `juridico_escritorio`) e publica um painel por cliente, com KPIs do mês,
tendência de entrada×distribuição, movimentações não lidas e tabela de casos.

Publicado via GitHub Pages a partir de `docs/`.

## Atualização automática

`.github/workflows/atualizar-painel.yml` roda `docs/gerar_painel.py` todo dia às
07:00 (horário de Brasília), regrava `docs/data.js` e `docs/mov.js` e commita o
resultado — o GitHub Pages republica sozinho. Também pode ser disparado manualmente
pela aba **Actions** do repositório (`workflow_dispatch`).

As credenciais do Odoo (`ODOO_URL`, `ODOO_DB`, `ODOO_LOGIN`, `ODOO_API_KEY`) ficam
como **Secrets** do repositório (Settings → Secrets and variables → Actions),
nunca em arquivo versionado.

## Rodar localmente

```
pip install -r requirements.txt
cp .env.example .env   # preencha as credenciais do Odoo
cd docs
python gerar_painel.py
python -m http.server   # abra http://localhost:8000
```

## Estrutura

```
docs/
  index.html       # o painel em si (servido pelo GitHub Pages)
  gerar_painel.py   # busca dados no Odoo e grava data.js / mov.js
  data.js, mov.js   # gerados — não editar à mão
  mockup/           # cópia com dados fake, para testar o layout sem tocar no Odoo
```
