"""Extract page text; render scanned PDFs and optionally run local Tesseract OCR.

Usage: python process_pdf.py PATH [--ocr]
Uses Poppler pdftoppm and, with --ocr, tesseract plus vie language data.
Important snippets are candidate matches, not automatically verified facts.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from pypdf import PdfReader

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('pdf',type=Path)
    parser.add_argument('--ocr',action='store_true')
    args=parser.parse_args()
    out=args.pdf.with_suffix('')
    out.mkdir(exist_ok=True)
    result=[]
    for n,page in enumerate(PdfReader(args.pdf).pages,1):
        text=page.extract_text() or ''
        method='embedded_text'
        status='extracted'
        if len(text.strip())<50:
            method='scan'
            status='needs_visual_read_or_ocr'
            if not shutil.which('pdftoppm'):
                raise RuntimeError('Poppler pdftoppm is required to render scanned PDFs.')
            png=out/f'page_{n}'
            subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-scale-to','1800','-png',str(args.pdf),str(png)],check=True)
            if args.ocr:
                if not shutil.which('tesseract'):
                    raise RuntimeError('Tesseract with vie language data is not configured; rendered page images remain available.')
                command=['tesseract',str(png)+'.png','stdout','-l','vie+eng']
                text=subprocess.run(command,check=True,capture_output=True,encoding='utf-8').stdout
                method='tesseract_vie_eng'
                status='ocr_requires_review'
        terms=['vốn điều lệ','ngành','địa chỉ','chủ sở hữu','người đại diện','năm tài chính','hiệu lực','giải thể']
        matches=[line for line in text.splitlines() if any(term in line.casefold() for term in terms)]
        result.append({'page':n,'method':method,'status':status,'text':text,'candidate_snippets':matches})
    (out/'pages.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'pages':len(result),'scan_pages':sum(r['method']=='scan' for r in result),'output':str(out)},ensure_ascii=False))

if __name__=='__main__':
    main()
