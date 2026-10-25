"""Build tidy CSVs from the raw INE JSON downloads in data/raw/.

Outputs in data/tidy/:
  iph_quarterly.csv -- long-per-period row with Total (H1), Novos (H11),
  Existentes (H12) YoY rates, quarterly rates and the Base-2025 index level.

Period strings like '1.o Trimestre de 2010' are parsed to '2010Q1'.
"""

import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'data', 'raw')
TIDY = os.path.join(HERE, 'data', 'tidy')

PERIOD_RE = re.compile(r'^(\d).{0,3}Trimestre de (\d{4})$')


def norm_period(p):
    m = PERIOD_RE.match(p.replace('º', 'o'))
    if not m:
        raise ValueError(f'unparsed period: {p!r}')
    return f'{m.group(2)}Q{m.group(1)}'


def load(var):
    d = json.load(open(os.path.join(RAW, f'ine_{var}.json'), encoding='utf-8'))
    return d['series']


def by_cat(series, period):
    """{dim_3: float-or-''} for one period."""
    out = {}
    for rec in (series.get(period) or []):
        v = rec.get('valor')
        out[rec['dim_3']] = float(v) if v not in (None, '', 'F', 'N') else ''
    return out


def main():
    os.makedirs(TIDY, exist_ok=True)
    yoy = load('0014767')
    qoq = load('0014766')
    idx = load('0014765')

    periods = sorted(set(yoy) | set(idx) | set(qoq),
                     key=lambda p: (int(norm_period(p)[:4]), int(norm_period(p)[5])))

    cols = ['periodo',
            'yoy_total_pct', 'yoy_novos_pct', 'yoy_existentes_pct',
            'qoq_total_pct', 'iph_index_base2025']
    rows = []
    for p in periods:
        y, i_, q = by_cat(yoy, p), by_cat(idx, p), by_cat(qoq, p)
        rows.append({
            'periodo': norm_period(p),
            'yoy_total_pct': y.get('H1', ''),
            'yoy_novos_pct': y.get('H11', ''),
            'yoy_existentes_pct': y.get('H12', ''),
            'qoq_total_pct': q.get('H1', ''),
            'iph_index_base2025': i_.get('H1', ''),
        })

    with open(os.path.join(TIDY, 'iph_quarterly.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

    # annual averages (mean of available quarters; provisional for partial years)
    years = {}
    for r in rows:
        yr = r['periodo'][:4]
        years.setdefault(yr, []).append(r)
    acols = ['ano', 'n_trimestres',
             'yoy_total_pct', 'yoy_novos_pct', 'yoy_existentes_pct',
             'iph_index_base2025']
    arows = []
    for yr in sorted(years):
        qs = years[yr]
        def avg(col):
            vals = [r[col] for r in qs if isinstance(r[col], float)]
            return round(sum(vals) / len(vals), 2) if vals else ''
        arows.append({
            'ano': yr,
            'n_trimestres': len(qs),
            'yoy_total_pct': avg('yoy_total_pct'),
            'yoy_novos_pct': avg('yoy_novos_pct'),
            'yoy_existentes_pct': avg('yoy_existentes_pct'),
            'iph_index_base2025': avg('iph_index_base2025'),
        })

    with open(os.path.join(TIDY, 'iph_annual.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=acols)
        w.writeheader()
        w.writerows(arows)

    print('wrote', len(rows), 'quarterly rows and', len(arows), 'annual rows')
    print(rows[0])
    print(rows[-1])


if __name__ == '__main__':
    main()