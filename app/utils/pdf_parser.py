"""
Parser for mypension.be PDF extracts.
mypension.be is the Belgian federal pension portal — the extract is a structured
PDF summarizing all pension contracts (pillar 2 and 3) per citizen.
"""
import re
import pdfplumber


def parse_pension_extract(file_path: str) -> dict:
    """
    Extract structured data from a mypension.be PDF.
    Returns a dict with the parsed fields.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            full_text = '\n'.join(
                page.extract_text() or '' for page in pdf.pages
            )
    except Exception as e:
        return {'error': str(e), 'raw_text': ''}

    return {
        'name': _extract_name(full_text),
        'national_number': _extract_niss(full_text),
        'extract_date': _extract_date(full_text),
        'contracts': _extract_contracts(full_text),
        'raw_text': full_text,
    }


def _extract_name(text: str) -> str:
    patterns = [
        r'Nom\s*/\s*Naam\s*[:\-]\s*(.+)',
        r'Naam\s*[:\-]\s*(.+)',
        r'Name\s*[:\-]\s*(.+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''


def _extract_niss(text: str) -> str:
    # Belgian NISS: YY.MM.DD-XXX.CC or without dots/dashes
    match = re.search(r'\b(\d{2}[.\-]?\d{2}[.\-]?\d{2}[.\-]?\d{3}[.\-]?\d{2})\b', text)
    return match.group(1) if match else ''


def _extract_date(text: str) -> str:
    patterns = [
        r"Date\s+d['\u2019]extraction\s*[:\-]\s*(\d{2}[/.\-]\d{2}[/.\-]\d{4})",
        r'Extractiedatum\s*[:\-]\s*(\d{2}[/.\-]\d{2}[/.\-]\d{4})',
        r'(\d{2}[/.\-]\d{2}[/.\-]\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ''


def _extract_contracts(text: str) -> list:
    """
    Detect branch 21 contracts from the extract text.
    mypension.be lists contracts per institution with reserve amounts.
    """
    contracts = []

    # Split by institution block — typical pattern: institution name followed by contract details
    institution_pattern = re.compile(
        r'(?P<institution>[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜÇ][^\n]{3,60})\n'
        r'(?P<details>(?:(?!(?:[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜÇ][^\n]{3,60})\n)[\s\S])*)',
        re.MULTILINE
    )

    amount_pattern = re.compile(r'([\d\s]+[,.][\d]{2})\s*€?', re.IGNORECASE)
    branch21_keywords = [
        'branche 21', 'tak 21', 'branch 21',
        'rendement garanti', 'gegarandeerd rendement',
        'assurance épargne', 'spaarverzekering',
        'taux garanti', 'gegarandeerde rente',
    ]

    for match in institution_pattern.finditer(text):
        institution = match.group('institution').strip()
        details = match.group('details')

        details_lower = details.lower()
        is_branch21 = any(kw in details_lower for kw in branch21_keywords)

        amounts = amount_pattern.findall(details)
        amount = None
        if amounts:
            raw = amounts[-1].replace(' ', '').replace(',', '.')
            try:
                amount = float(raw)
            except ValueError:
                pass

        if institution and len(institution) > 4:
            contracts.append({
                'institution': institution,
                'is_branch21': is_branch21,
                'amount': amount,
                'details': details.strip()[:300],
            })

    return contracts
