import json


WEIGHTS = {
    "skill":      0.38,
    "experience": 0.22,
    "rating":     0.16,
    "completion": 0.10,
    "skill_test": 0.09,
    "reviews":    0.05,
}


def _parse_skills(val) -> list:
    if isinstance(val, list):
        return val
    try:
        return json.loads(val)
    except Exception:
        return []


def calculate_match(talent_row, job_row) -> float:
    """Return 0-100 match score."""
    talent_skills = _parse_skills(talent_row["skills"])
    job_skills    = _parse_skills(job_row["required_skills"])

    if not job_skills:
        return 0.0

    common = len(set(s.lower() for s in talent_skills) &
                 set(s.lower() for s in job_skills))
    skill_match = common / len(job_skills)

    exp_required  = job_row.get("experience_required", 3)
    exp_score     = min(talent_row["years_exp"] / max(exp_required, 1), 1.0)
    rating_score  = talent_row["rating"] / 5.0
    comp_score    = talent_row["completion_rate"] / 100.0
    test_score    = float(talent_row.get("skill_test_score", 0) or 0) / 100.0
    review_score  = float(talent_row.get("review_score", 0) or 0) / 100.0

    raw = (
        WEIGHTS["skill"]      * skill_match +
        WEIGHTS["experience"] * exp_score   +
        WEIGHTS["rating"]     * rating_score +
        WEIGHTS["completion"] * comp_score +
        WEIGHTS["skill_test"] * test_score +
        WEIGHTS["reviews"]    * review_score
    )
    return round(raw * 100, 1)


def get_breakdown(talent_row, job_row) -> dict:
    """Return individual factor scores (0-100)."""
    talent_skills = _parse_skills(talent_row["skills"])
    job_skills    = _parse_skills(job_row["required_skills"])

    if not job_skills:
        return {k: 0 for k in WEIGHTS}

    common = len(set(s.lower() for s in talent_skills) &
                 set(s.lower() for s in job_skills))
    skill_match  = round(common / len(job_skills) * 100, 1)
    exp_required = job_row.get("experience_required", 3)
    exp_score    = round(min(talent_row["years_exp"] / max(exp_required, 1), 1.0) * 100, 1)
    rating_score = round(talent_row["rating"] / 5.0 * 100, 1)
    comp_score   = round(talent_row["completion_rate"], 1)
    test_score   = round(float(talent_row.get("skill_test_score", 0) or 0), 1)
    review_score = round(float(talent_row.get("review_score", 0) or 0), 1)

    return {
        "Skill Match":      skill_match,
        "Experience Fit":   exp_score,
        "Peer Ratings":     rating_score,
        "Completion Rate":  comp_score,
        "Skill Tests":      test_score,
        "Employer Reviews": review_score,
    }


def get_success_prob(match_score: float) -> tuple[float, str]:
    """Returns (probability %, emoji) based on match score."""
    if match_score >= 80:
        prob = round(match_score * 0.95, 1)
        return prob, "🟢"
    elif match_score >= 65:
        prob = round(match_score * 0.88, 1)
        return prob, "🟡"
    else:
        prob = round(match_score * 0.78, 1)
        return prob, "🔴"


def get_risk_level(talent_row) -> tuple[str, str]:
    """Returns (label, css_class)."""
    comp  = talent_row["completion_rate"]
    projs = talent_row["projects"]

    if comp < 65:
        return "High Risk", "risk-hi"
    if projs > 18 and comp < 75:
        return "Burnout Risk", "risk-me"
    if comp >= 85:
        return "Low Risk", "risk-lo"
    return "Moderate", "risk-me"


def score_class(score: float) -> str:
    if score >= 78:
        return "sp-h"
    elif score >= 60:
        return "sp-m"
    return "sp-l"


def rank_talents_for_job(talents_df, job_row, top_n: int = 10):
    """Return sorted list of (talent_row, score)."""
    results = []
    for _, t in talents_df.iterrows():
        score = calculate_match(t, job_row)
        results.append((t, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]
