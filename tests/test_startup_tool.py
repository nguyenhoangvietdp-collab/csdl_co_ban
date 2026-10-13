"""Small checks for approval gates. No live network or Sheet writes."""
import hashlib
import tempfile
import unittest
from datetime import date
from pathlib import Path
from startup_tool import TAX_STATUS, evaluate, validate_evidence, within


class Gates(unittest.TestCase):
    def test_month_precision_is_conservative(self):
        self.assertTrue(within('2026-06',date(2026,10,13),365))
        self.assertFalse(within('2026-10',date(2026,10,13),365))
        self.assertFalse(within('2025-06',date(2026,10,13),365))
        self.assertTrue(within('2025',date(2026,10,13),730))
        self.assertFalse(within('2025',date(2026,10,13),365))
        self.assertFalse(within('2026',date(2026,10,13),730))

    def test_full_gate_and_counterexamples(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            text = 'Sample Sample Company 0123456789 NNT đang hoạt động. Functional innovative robot prototype deployed for customer.'
            (root/'source.txt').write_text(text, encoding='utf-8')
            common = dict(snapshot='source.txt', sha256=hashlib.sha256(text.encode()).hexdigest(), quote=text,
                url='https://example.org/source', publisher_owner='Owner A', reviewed=True, reviewer='fixture',
                retrieved_at='2026-10-06', company_id='s1')
            evidence = [dict(common, id=kind, kind=kind) for kind in ('identity','startup','technology','product')]
            evidence += [dict(common, id='discovery', kind='discovery', published_at='2026-01-01', source_type='fund'),
                dict(common, id='counter', kind='counter_review', search_queries=['closure','dissolution'], review_note='fixture only'),
                dict(common, id='tax', kind='tax', url='https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp',
                     checked_at='2026-10-06', tax_id='0123456789', legal_name='Sample Company', status='NNT đang hoạt động'),
                dict(common, id='activity1', kind='activity', event_date='2026-05-01', origin_id='deployment'),
                dict(common, id='activity2', kind='activity', event_date='2026-06-01', origin_id='production', publisher_owner='Owner B')]
            company = dict(id='s1', brand='Sample', legal_name='Sample Company', tax_id='0123456789', country='VN', physical='yes')
            today = date(2026,10,6)
            self.assertEqual(evaluate(company, evidence, today, root)['decision'], 'approved')
            flagged = evidence+[dict(common,id='integrity',kind='source_integrity_flag')]
            self.assertIn('source_integrity_requires_resolution',evaluate(company,flagged,today,root)['reasons'])
            flagged[-1]['resolution']='Client corroboration reviewed in fixture'
            self.assertEqual(evaluate(company,flagged,today,root)['decision'],'approved')
            for field, value in [('checked_at','2024-01-01'), ('url','https://example.org/tax'),
                                 ('status','NNT ngừng hoạt động'), ('tax_id','9999999999')]:
                with self.subTest(field=field):
                    changed = [dict(e, **{field:value}) if e['kind']=='tax' else dict(e) for e in evidence]
                    self.assertEqual(evaluate(company, changed, today, root)['decision'], 'pending')
            same_origin = [dict(e, origin_id='deployment') if e['kind']=='activity' else dict(e) for e in evidence]
            self.assertEqual(evaluate(company, same_origin, today, root)['decision'], 'pending')
            inactive_text='Sample Company 0123456789 NNT ngừng HĐ nhưng chưa hoàn thành thủ tục chấm dứt hiệu lực MST'
            (root/'inactive.txt').write_text(inactive_text,encoding='utf-8')
            inactive=[dict(e,snapshot='inactive.txt',quote=inactive_text,sha256=hashlib.sha256(inactive_text.encode()).hexdigest(),
                status='NNT ngừng HĐ nhưng chưa hoàn thành thủ tục chấm dứt hiệu lực MST') if e['kind']=='tax' else dict(e) for e in evidence]
            self.assertEqual(evaluate(company,inactive,today,root)['decision'],'excluded_tax_entity')
            bad_quote = dict(common, quote='A quotation absent from the saved source')
            self.assertIn('quote_not_in_snapshot', validate_evidence(bad_quote, today, root))
            future = dict(common, retrieved_at='2027-01-01')
            self.assertIn('stale_or_missing_retrieval_date', validate_evidence(future, today, root))
            image_record = dict(common, method='image_transcription', image_file='missing.jpg')
            self.assertIn('missing_original_image', validate_evidence(image_record, today, root))
            pdf_record = dict(common, method='pdf_embedded_text', pdf_file='missing.pdf')
            self.assertIn('missing_original_pdf', validate_evidence(pdf_record, today, root))
            (root/'original.pdf').write_bytes(b'%PDF-fixture')
            pdf_record.update(pdf_file='original.pdf',pdf_sha256='wrong')
            self.assertIn('pdf_hash_mismatch', validate_evidence(pdf_record, today, root))
            pdf_record['pdf_sha256']=hashlib.sha256(b'%PDF-fixture').hexdigest()
            self.assertEqual(validate_evidence(pdf_record, today, root),[])

    def test_missing_evidence_cannot_approve(self):
        row = evaluate({'id':'s1', 'brand':'Sample', 'country':'VN', 'physical':'yes'}, [], date(2026,10,6))
        self.assertEqual(row['decision'], 'pending')
        self.assertIn('no_matching_official_tax_evidence', row['reasons'])

    def test_tax_aggregator_not_official(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            text = 'Sample Company 0123456789 ' + TAX_STATUS
            (root/'tax.txt').write_text(text, encoding='utf-8')
            evidence = dict(snapshot='tax.txt', sha256=hashlib.sha256(text.encode()).hexdigest(), quote=text,
                url='https://example.com/company', publisher_owner='Aggregator', reviewed=True, reviewer='test',
                retrieved_at='2026-10-06', checked_at='2026-10-06', kind='tax', tax_id='0123456789',
                legal_name='Sample Company', status=TAX_STATUS)
            errors = validate_evidence(evidence, date(2026,10,6), root)
            self.assertIn('not_official_tax_source', errors)
            evidence['url'] = 'https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp'
            self.assertEqual(validate_evidence(evidence, date(2026,10,6), root), [])
            evidence['checked_at'] = '2025-01-01'
            self.assertIn('stale_tax_check', validate_evidence(evidence, date(2026,10,6), root))


if __name__ == '__main__':
    unittest.main()
