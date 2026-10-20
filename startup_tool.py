"""Collect public source snapshots and screen startups against reviewable evidence.

No CAPTCHA solving. Prefer official tax evidence; reviewed TVPL fallback requires a recorded lookup failure.
Usage: startup_tool.py fetch --sources startup_sources.json
       startup_tool.py screen --as-of YYYY-MM-DD
"""
import argparse
import calendar
import csv
import hashlib
import ipaddress
import json
import re
import socket
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'data' / 'startups'
TAX_STATUS = 'NNT đang hoạt động (đã được cấp GCN ĐKT)'
ACTIVE_TAX_STATUSES = {TAX_STATUS, 'NNT đang hoạt động'}
DISCOVERY_TYPES = {'government', 'fund', 'competition'}


def normal(value):
    return ' '.join(unicodedata.normalize('NFC', value).casefold().split())


def public_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in {'http', 'https'} or not parts.hostname or parts.username or parts.password:
        raise ValueError('A public HTTP(S) URL without credentials is required')
    for address in socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == 'https' else 80)):
        if not ipaddress.ip_address(address[4][0]).is_global:
            raise ValueError('Private or local network targets are not allowed')
    return url


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.hidden += 1
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.text.append(data.strip())


def fetch(args):
    DATA.mkdir(parents=True, exist_ok=True)
    snapshots = DATA / 'sources'
    snapshots.mkdir(exist_ok=True)
    opener = urllib.request.build_opener(PublicRedirect())
    registry = json.loads(Path(args.sources).read_text(encoding='utf-8-sig'))
    results = []
    for source in registry:
        row = dict(source, fetched_at=datetime.now(timezone.utc).isoformat())
        try:
            public_url(source['url'])
            request = urllib.request.Request(source['url'], headers={'User-Agent': 'StartupEvidenceResearch/1.0', 'Accept': 'text/html'})
            with opener.open(request, timeout=40) as response:
                body = response.read(8_000_001)
                if len(body) > 8_000_000:
                    raise ValueError('Source exceeds 8 MB limit; download and inspect separately')
                if 'html' not in response.headers.get('Content-Type', ''):
                    raise ValueError('HTML collector only; inspect PDF/image separately')
                try:
                    html = body.decode(response.headers.get_content_charset() or 'utf-8', errors='replace')
                except LookupError:
                    # Some publishers send malformed charset labels such as utf-8,gbk.
                    html = body.decode('utf-8', errors='replace')
                    row['decode_fallback'] = 'utf-8: unsupported publisher charset'
                row['final_url'] = response.geturl()
            parser = Page()
            parser.feed(html)
            text = '\n'.join(parser.text).replace('\r\n', '\n').replace('\r', '\n').lstrip('\ufeff')
            key = hashlib.sha256(source['url'].encode()).hexdigest()[:20] + '_' + hashlib.sha256(body).hexdigest()
            (snapshots / f'{key}.html').write_bytes(body)
            (snapshots / f'{key}.txt').write_text(text, encoding='utf-8')
            row.update(status='fetched', snapshot=f'sources/{key}.txt', sha256=hashlib.sha256(text.encode()).hexdigest(),
                       links=sorted({urllib.parse.urljoin(row['final_url'], link) for link in parser.links if link.startswith(('http', '/'))}))
            if len(text.strip()) < 100:
                row['status'] = 'needs_browser_or_manual_read'
        except (OSError, ValueError, urllib.error.URLError) as error:
            row.update(status='fetch_failed', error=str(error))
        results.append(row)
        print(json.dumps({k: row[k] for k in ('id', 'status')}, ensure_ascii=False))
        time.sleep(1)
    manifest = DATA / 'source_manifest.json'
    previous = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    merged = {row['id']: row for row in previous}
    merged.update({row['id']: row for row in results})
    manifest.write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=2), encoding='utf-8')


def within(value, today, days):
    try:
        if re.fullmatch(r'\d{4}', value):
            year = int(value)
            return 0 <= (today-date(year, 12, 31)).days and (today-date(year, 1, 1)).days <= days
        if re.fullmatch(r'\d{4}-\d{2}', value):
            year, month = map(int, value.split('-'))
            first = date(year, month, 1)
            last = date(year, month, calendar.monthrange(year, month)[1])
            return 0 <= (today-last).days and (today-first).days <= days
        return 0 <= (today - date.fromisoformat(value[:10])).days <= days
    except (ValueError, TypeError):
        return False


def validate_evidence(evidence, today, directory=DATA):
    """Validate provenance mechanically; reviewed field records a human judgement."""
    errors = []
    path = (directory / evidence.get('snapshot', '')).resolve()
    if not path.is_relative_to(directory.resolve()) or not path.is_file():
        return ['missing_or_invalid_snapshot']
    text = path.read_text(encoding='utf-8-sig')
    if hashlib.sha256(text.encode()).hexdigest() != evidence.get('sha256'):
        errors.append('snapshot_hash_mismatch')
    if evidence.get('method') == 'image_transcription':
        image = (directory / evidence.get('image_file', '')).resolve()
        if not image.is_relative_to(directory.resolve()) or not image.is_file():
            errors.append('missing_original_image')
        elif hashlib.sha256(image.read_bytes()).hexdigest() != evidence.get('image_sha256'):
            errors.append('image_hash_mismatch')
    if evidence.get('method') == 'pdf_embedded_text':
        pdf = (directory / evidence.get('pdf_file', '')).resolve()
        if not pdf.is_relative_to(directory.resolve()) or not pdf.is_file():
            errors.append('missing_original_pdf')
        elif hashlib.sha256(pdf.read_bytes()).hexdigest() != evidence.get('pdf_sha256'):
            errors.append('pdf_hash_mismatch')
    quote = evidence.get('quote', '')
    if len(quote.strip()) < 10 or normal(quote) not in normal(text):
        errors.append('quote_not_in_snapshot')
    parsed = urllib.parse.urlsplit(evidence.get('url', ''))
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        errors.append('invalid_source_url')
    if not evidence.get('publisher_owner'):
        errors.append('missing_publisher_owner')
    if evidence.get('reviewed') is not True or not evidence.get('reviewer'):
        errors.append('needs_semantic_review')
    if not within(evidence.get('retrieved_at'), today, 30):
        errors.append('stale_or_missing_retrieval_date')
    if evidence.get('kind') in {'tax', 'tax_secondary'}:
        host = (parsed.hostname or '').lower()
        if evidence['kind'] == 'tax_secondary':
            if host != 'thuvienphapluat.vn' or not evidence.get('fallback_reason'):
                errors.append('invalid_tax_fallback')
        elif not (host == 'gdt.gov.vn' or host.endswith('.gdt.gov.vn')):
            errors.append('not_official_tax_source')
        if not within(evidence.get('checked_at'), today, 30):
            errors.append('stale_tax_check')
        for field in ('tax_id', 'legal_name', 'status'):
            if not evidence.get(field) or normal(evidence[field]) not in normal(text):
                errors.append(f'tax_{field}_not_in_snapshot')
            if not evidence.get(field) or normal(evidence[field]) not in normal(quote):
                errors.append(f'tax_{field}_not_in_quote')
        if not re.search(r'(?<!\d)' + re.escape(evidence.get('tax_id', '')) + r'(?![\d-])', quote):
            errors.append('tax_id_not_exact_in_quote')
        quoted_ids = set(re.findall(r'(?<!\d)\d{10}(?:-\d{3})?(?!\d)', quote))
        if quoted_ids != {evidence.get('tax_id')}:
            errors.append('tax_quote_not_single_entity')
    return errors


def evaluate(company, evidence, today, directory=DATA):
    matched = [e for e in evidence if e.get('company_id') == company['id']]
    valid = [e for e in matched if not validate_evidence(e, today, directory)]
    reasons = []
    tax_id = company.get('tax_id', '')
    if not re.fullmatch(r'\d{10}', tax_id):
        reasons.append('missing_parent_company_tax_id')
    tax = [e for e in valid if e.get('kind') in {'tax', 'tax_secondary'} and e.get('tax_id') == tax_id
           and normal(e.get('legal_name', '')) == normal(company.get('legal_name', ''))]
    if not tax:
        reasons.append('no_matching_official_tax_evidence')
    elif any(e.get('status') not in ACTIVE_TAX_STATUSES | {'Đang hoạt động'} for e in tax):
        reasons.append('tax_inactive_or_conflicting_status')
    if any(e.get('kind') == 'negative_activity' for e in valid):
        reasons.append('negative_activity_requires_resolution')
    if any(e.get('kind') == 'source_integrity_flag' and not e.get('resolution') for e in valid):
        reasons.append('source_integrity_requires_resolution')
    if not any(e.get('kind') == 'counter_review' and len(e.get('search_queries', [])) >= 2
               and e.get('review_note') for e in valid):
        reasons.append('counter_evidence_review_missing')
    identity = [e for e in valid if e.get('kind') == 'identity' and
                all(normal(company.get(k, '')) in normal(e['quote']) and company.get(k) for k in ('brand', 'legal_name'))]
    if not identity:
        reasons.append('brand_legal_entity_mapping_unverified')
    if not any(e.get('kind') == 'discovery' and e.get('source_type') in DISCOVERY_TYPES
               and within(e.get('published_at'), today, 730) for e in valid):
        reasons.append('no_recent_fund_government_contest_publication')
    for kind in ('startup', 'technology', 'product'):
        if not any(e.get('kind') == kind for e in valid):
            reasons.append(f'{kind}_unverified')
    if company.get('country') != 'VN':
        reasons.append('vietnam_legal_entity_unverified')
    activity = [e for e in valid if e.get('kind') == 'activity' and within(e.get('event_date'), today, 365)]
    if len({e['publisher_owner'] for e in activity}) < 2:
        reasons.append('need_two_independent_recent_activity_publishers')
    if len({e.get('origin_id') for e in activity if e.get('origin_id')}) < 2:
        reasons.append('need_two_distinct_activity_origins')
    if company.get('physical') not in {'yes', 'hybrid', 'no'}:
        reasons.append('product_classification_unreviewed')
    decision = 'excluded_tax_entity' if 'tax_inactive_or_conflicting_status' in reasons else ('pending' if reasons else 'approved')
    return dict(company, decision=decision, reasons='; '.join(reasons),
                valid_evidence=len(valid), invalid_evidence=len(matched)-len(valid),
                priority={'yes': 2, 'hybrid': 1, 'no': 0}.get(company.get('physical'), -1), as_of=today.isoformat())


def screen(args):
    today = date.fromisoformat(args.as_of)
    with Path(args.candidates).open(encoding='utf-8-sig', newline='') as handle:
        candidates = list(csv.DictReader(handle))
    if len({c['id'] for c in candidates}) != len(candidates):
        raise ValueError('Duplicate candidate ID')
    ids = [c['tax_id'] for c in candidates if c.get('tax_id')]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate tax IDs; merge company aliases first')
    path = Path(args.evidence)
    evidence = [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()] if path.exists() else []
    if len({e['id'] for e in evidence}) != len(evidence):
        raise ValueError('Duplicate evidence ID')
    rows = [evaluate(c, evidence, today) for c in candidates]
    approved = sorted((r for r in rows if r['decision']=='approved'), key=lambda r: (-r['priority'], r['id']))[:50]
    DATA.mkdir(parents=True, exist_ok=True)
    for name, values in [('screening', rows), ('approved_50', approved)]:
        fields = list(rows[0]) if rows else ['id', 'decision']
        with (DATA / f'{name}.csv').open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(values)
    report = {'as_of': today.isoformat(), 'candidates':len(rows), 'approved':len(approved),
              'target':50, 'complete':len(approved)==50, 'pending':sum(r['decision']=='pending' for r in rows),
              'excluded_tax_entity':sum(r['decision']=='excluded_tax_entity' for r in rows)}
    (DATA / 'screening_summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    collect = sub.add_parser('fetch')
    collect.add_argument('--sources', default=str(ROOT/'startup_sources.json'))
    collect.set_defaults(run=fetch)
    review = sub.add_parser('screen')
    review.add_argument('--as-of', required=True)
    review.add_argument('--candidates', default=str(DATA/'candidates.csv'))
    review.add_argument('--evidence', default=str(DATA/'evidence.jsonl'))
    review.set_defaults(run=screen)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
