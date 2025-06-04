import re
from RTS_APP.models import ScoringCriteria

def get_dynamic_scoring_rules():
    return {crit.keyword: crit.weight for crit in ScoringCriteria.objects.all()}

def score_resume(text):
    rules = get_dynamic_scoring_rules()
    patterns = {k: re.compile(rf'\b{k}\b', re.IGNORECASE) for k in rules}
    total_score = 0
    feedback = []
    missing = []

    for keyword, pattern in patterns.items():
        if pattern.search(text):
            total_score += rules[keyword]
            feedback.append(f"{keyword} skill detected (+{rules[keyword]}%)")
        else:
            missing.append(keyword)

    if missing:
        feedback.append("consider adding: " + ", ".join(missing))

    return {
        "score": min(total_score, 100),
        "comment": " | ".join(feedback)
    }
