"""Deterministic HTML normalization. Acquisition belongs to host tools."""
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

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

