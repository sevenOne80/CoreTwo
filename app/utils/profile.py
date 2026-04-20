"""
MiFID-inspired investor profile scoring.
Questions cover: investment horizon, objective, loss tolerance,
reaction to drop, financial knowledge, experience, income stability,
savings proportion.
"""

PROFILE_THRESHOLDS = [
    (20, 'defensive'),
    (38, 'conservative'),
    (56, 'balanced'),
    (74, 'dynamic'),
    (100, 'aggressive'),
]

# Max score per question (sum = 100 pts when all max chosen)
QUESTION_WEIGHTS = {
    'q1': [2, 6, 10, 14, 18],   # horizon
    'q2': [2, 5, 9, 14],         # objective
    'q3': [2, 5, 9, 13, 18],     # loss tolerance
    'q4': [2, 5, 9, 13],         # reaction drop
    'q5': [2, 5, 9, 13],         # knowledge
    'q6': [2, 5, 9, 13],         # experience
    'q7': [2, 5, 10],             # income stability
    'q8': [2, 5, 9, 11],          # savings proportion
}


def compute_investor_profile(answers: dict) -> dict:
    score = 0
    for key, weights in QUESTION_WEIGHTS.items():
        raw = answers.get(key, '1')
        try:
            idx = int(raw) - 1
            idx = max(0, min(idx, len(weights) - 1))
            score += weights[idx]
        except (ValueError, TypeError):
            score += weights[0]

    profile_type = 'balanced'
    for threshold, ptype in PROFILE_THRESHOLDS:
        if score <= threshold:
            profile_type = ptype
            break

    return {'score': score, 'type': profile_type}
