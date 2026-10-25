# housing_prices_pt

Datasets on Portuguese housing prices from official sources (INE), stored as
tidy CSVs with a refresh script. Data for the power-aware/housing blog idea
and any future analysis.

## Data

- `data/tidy/iph_quarterly.csv` — quarterly, 2009Q1–2026Q2:
  - `yoy_total_pct`, `yoy_novos_pct`, `yoy_existentes_pct` — Índice de Preços
    da Habitação (IPH) homolog rates, Base 2025 (INE varcd 0014767)
  - `qoq_total_pct` — quarterly rate (INE varcd 0014766)
  - `iph_index_base2025` — index level, Base 2025=100 (INE varcd 0014765)
- `data/tidy/iph_annual.csv` — annual averages of the above (2026 is
  partial: 2 quarters, provisional).
- `data/raw/ine_*.json` — raw API responses (full audit trail, kept as-is).

The most recent quarter(s) can be provisional; re-running `fetch_ine.py`
picks up revisions.

## Source and licence

INE, Portugal — Índice de preços da habitação (Base 2025).
License: reutilizável com atribuição / CC BY 4.0.
Suggested citation: "INE, Índice de preços da habitação, Base 2025 (consultado 2026-10-25)".

- API: https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=<code>&Dim1=T&lang=PT
- Metainfo: https://smi.ine.pt/Indicador

Other reputable series (not included here yet):
- Pordata (same INE data + preço médio por m² from escrituras):
  https://www.pordata.pt/pt/estatisticas/habitacao
- Banco de Portugal — Estatísticas do mercado de habitação (median price
  per m² by region): https://www.bportugal.pt/
- Eurostat HPI for Portugal: https://ec.europa.eu/eurostat (prc_hpi_q)

## Usage

```bash
python3 fetch_ine.py    # refresh raw JSON (API is flaky: retries built in)
python3 build_tidy.py   # rebuild CSVs from raw JSON
```

Python 3.11+ stdlib only (no pandas on the host system).