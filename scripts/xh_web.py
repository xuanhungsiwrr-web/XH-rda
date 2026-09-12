"""Source capture: compact MCP responses, full local evidence, no draft contamination."""
import hashlib
import ipaddress
import json
import os
import socket
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from xh_core import Project, encoded, stamp

def public_url(url):
    p = urlparse(url)
    if p.scheme not in ['http','https'] or not p.hostname or p.username or p.password:
        raise ValueError('Public HTTP(S) URL required')
    for item in socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == 'https' else 80), type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(item[4][0]).is_global:
            raise ValueError('Private/local network URL not allowed')
    return url

def fetch(url, limit=5_000_000):
    for _ in range(6):
        public_url(url)
        with requests.get(url, timeout=(10,30), stream=True, allow_redirects=False,
                          headers={'User-Agent':'XHReportSourceCollector/0.7'}) as r:
            if r.status_code in [301,302,303,307,308]:
                url = urljoin(url, r.headers['Location']); continue
            r.raise_for_status()
            if 'html' not in r.headers.get('Content-Type','').lower():
                raise ValueError('Not HTML; use a PDF/document ingestion adapter')
            chunks, size = [], 0
            for chunk in r.iter_content(65536):
                size += len(chunk)
                if size > limit: raise ValueError('Source exceeds size limit; no partial success')
                chunks.append(chunk)
            return b''.join(chunks), url
    raise ValueError('Too many redirects')

def clean_html(raw, url):
    soup = BeautifulSoup(raw, 'html.parser')
    for node in soup(['script','style','nav','footer','header','aside']): node.decompose()
    body = soup.find('main') or soup.find('article') or soup.body or soup
    for node in body.find_all(['h1','h2','h3','h4','h5','h6']):
        node.replace_with('\n' + '#' * int(node.name[1]) + ' ' + node.get_text(' ',strip=True) + '\n')
    links = []
    for a in body.find_all('a', href=True):
        dest = urljoin(url, a['href'])
        if urlparse(dest).scheme in ['http','https']:
            links.append(dest)
            a.replace_with('[' + a.get_text(' ',strip=True) + '](' + dest + ')')
    # Tables remain structured for numerical/standard extraction.
    for table in body.find_all('table'):
        rows = [[c.get_text(' ',strip=True).replace('|','\\|') for c in tr.find_all(['td','th'])]
                for tr in table.find_all('tr')]
        rows = [r for r in rows if r]
        if rows:
            width = max(map(len, rows)); rows = [r + [''] * (width-len(r)) for r in rows]
            lines = ['| ' + ' | '.join(r) + ' |' for r in rows]
            lines.insert(1, '| ' + ' | '.join(['---']*width) + ' |')
            table.replace_with('\n' + '\n'.join(lines) + '\n')
    text = body.get_text('\n', strip=True)
    if len(text.strip()) < 100: raise ValueError('Insufficient text; JS/login/blocked page may need another adapter')
    return text, list(dict.fromkeys(links))

def scrape(project, url, refresh=False):
    sid = hashlib.sha256(url.encode()).hexdigest()[:20]
    aid = 'web:' + sid
    if project.head(aid) and not refresh and not project.stale(aid):
        return {'cached': True, 'artifact': aid, 'path': project.head(aid)['path']}
    raw, final_url = fetch(url)
    text, links = clean_html(raw, final_url)
    r = project.put('html:' + sid, 'research/raw/' + sid + '.html', raw, 'system',
                    meta={'url':url, 'final_url':final_url, 'retrieved_at':stamp()})
    md = '# Source\n\n' + final_url + '\n\n' + text
    result = project.put(aid, 'research/pages/' + sid + '.md', md, 'system', ['html:' + sid],
        {'url':final_url, 'links':links, 'extraction':'HTML text, no claim of rendered-page completeness'})
    return {**result, 'chars':len(md), 'utf8_bytes':len(md.encode()), 'tokens':None,
            'next':'Retrieve relevant paragraphs; do not read whole page unless required'}

def legal_search(project, query, recency=None):
    key = os.getenv('PERPLEXITY_API_KEY')
    if not key: raise ValueError('PERPLEXITY_API_KEY unavailable; use another search adapter')
    if recency is not None and recency not in ['day','week','month','year']: raise ValueError('Invalid recency')
    base = os.getenv('XH_PERPLEXITY_BASE_URL','https://api.perplexity.ai').rstrip('/')
    if not base.startswith('https://'): raise ValueError('HTTPS endpoint required')
    payload = {'model':os.getenv('XH_PERPLEXITY_MODEL','sonar-pro'),
        'messages':[{'role':'system','content':'Find original Vietnamese legal/technical documents. '
            'Return document number, issuing authority, effective date, amendment/repeal status, '
            'applicability and direct source URLs. Distinguish unknown from verified. Do not invent clauses.'},
                    {'role':'user','content':query}],
        'search_domain_filter':['vanban.chinhphu.vn','congbao.chinhphu.vn','vbpl.vn','tieuchuan.vsqi.gov.vn'],
        'max_tokens':3000}
    if recency: payload['search_recency_filter'] = recency
    response = requests.post(base + '/chat/completions', json=payload,
        headers={'Authorization':'Bearer '+key}, timeout=60)
    response.raise_for_status()
    data = response.json()
    result = {'query':query, 'retrieved_at':stamp(), 'status':'unverified',
        'text':data['choices'][0]['message']['content'], 'citations':data.get('citations',[]),
        'search_results':data.get('search_results',[]), 'usage':data.get('usage')}
    sid = hashlib.sha256(encoded(payload)).hexdigest()[:20]
    artifact = project.put('legal-search:' + sid, 'research/legal/' + sid + '.json', encoded(result), 'system')
    return {**artifact, 'citations':result['citations'], 'usage':result['usage'],
            'next':'Check original text and applicability; search result is not legal approval'}
