# CoreTwo — Project Context

## What it is
MGA website for CoreTwo, a Belgian MGA enabling clients to transfer branch 21 pension reserves into branch 23 products.
Clients upload their mypension.be PDF extract; the site analyses eligibility and runs full online onboarding/subscription.

## Stack
- Flask 3 + Flask-Babel (fr/nl/en) + Flask-Login + Flask-WTF
- MySQL via SQLAlchemy (PyMySQL)
- Bootstrap 5 + custom CSS (navy/gold design system)
- pdfplumber for mypension.be PDF parsing

## Quick start
```
pip install -r requirements.txt
cp .env.example .env        # edit DB credentials
mysql -u root -p -e "CREATE DATABASE coretwo CHARACTER SET utf8mb4;"
pybabel compile -d translations
python run.py
```

## Structure
- `app/main/`   — public pages (home, about, how it works, faq, contact)
- `app/auth/`   — login, register
- `app/portal/` — dashboard + 6-step onboarding wizard
- `app/utils/`  — pdf_parser, eligibility, profile scoring
- `app/static/css/main.css` — full design system (CSS variables + components)
- `translations/fr|nl|en/` — Babel .po files

## Onboarding steps
1. Identity (NISS, DOB, phone)
2. Upload mypension.be extract (PDF)
3. Eligibility analysis (auto-parsed)
4. MiFID investor profile questionnaire (8 questions)
5. Product selection (branch 23, matched to profile)
6. E-signature & submission

## Design tokens
- Navy: #1B2A4A  Gold: #C9A84C  Teal: #2D7D6F
- Font: Inter (Google Fonts)
