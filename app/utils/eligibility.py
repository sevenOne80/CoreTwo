"""
Determines whether a user's pension reserves are eligible for transfer
from branch 21 to branch 23.
"""
import json


MIN_TRANSFER_AMOUNT = 1000.0


def compute_eligibility(parsed_data: dict) -> dict:
    contracts = parsed_data.get('contracts', [])
    branch21 = [c for c in contracts if c.get('is_branch21')]

    if not branch21:
        return {
            'eligible': False,
            'amount': 0,
            'institution': None,
            'contracts': [],
            'reason': 'no_branch21_contracts',
        }

    total_amount = sum(c.get('amount') or 0 for c in branch21)

    if total_amount < MIN_TRANSFER_AMOUNT:
        return {
            'eligible': False,
            'amount': total_amount,
            'institution': branch21[0].get('institution'),
            'contracts': branch21,
            'reason': 'amount_too_low',
        }

    return {
        'eligible': True,
        'amount': total_amount,
        'institution': branch21[0].get('institution'),
        'contracts': branch21,
        'reason': 'eligible',
    }
