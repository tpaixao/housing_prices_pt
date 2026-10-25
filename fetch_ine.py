"""Fetch INE Housing Price Index (IPH) series via the official INE JSON API.

Sources:
  https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=<code>&Dim1=T&lang=PT
Licence: reutilizável com atribuição (CC BY 4.0) - INE, Portugal.

Indicator codes (verified via IndicadorDsg metadata):
  0014767  IPH total - taxa de variacao homologa (YoY %)
  0014764/65/66 - adjacent IPH indicators (total index level / novos / existentes),
                  auto-detected below from the indicator description.
"""

import json
import time
import urllib.request
import os

UA = {'User-Agent': 'Mozilla/5.0 (housing_prices_pt project)'}
VARS = ['0014764', '0014765', '0014766', '0014767']
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'raw')


def fetch_json(url, retries=5):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e:  # API is known to be flaky: timeouts, 503s
            last = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f'failed after {retries} attempts: {last}')


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    summary = {}
    for var in VARS:
        # Dim1=T returns all available periods; explicit S3A codes fetch the
        # provisional most-recent quarters (Dim1=T sometimes lags on them)
        url = (f'https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd={var}'
               f'&Dim1=T,S3A2026Q1,S3A2026Q2&lang=PT')
        d = fetch_json(url)
        item = d[0]
        desc = item['IndicadorDsg']
        dados = item['Dados']
        # Dados is a dict {period_code: value} keyed "S3A2010Q1" for quarters, "S7A2009" for years
        out = {'varcd': var, 'indicador': desc,
               'data_extracao': item.get('DataExtracao'),
               'series': dados}
        fn = os.path.join(DATA_DIR, f'ine_{var}.json')
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        periods = sorted(dados.keys())
        summary[var] = {'desc': desc[:90], 'n': len(dados),
                        'first': periods[0] if periods else None,
                        'last': periods[-1] if periods else None}
    with open(os.path.join(DATA_DIR, '_meta.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    for var, s in summary.items():
        print(var, '|', s['n'], '|', s['first'], '->', s['last'], '|', s['desc'])


if __name__ == '__main__':
    main()