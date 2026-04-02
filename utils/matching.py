import json

def calculate_match(talent_row, job_row):
    talent_skills = json.loads(talent_row['skills'])
    job_skills = json.loads(job_row['required_skills'])
    
    common = len(set(talent_skills) & set(job_skills))
    skill_match = common / len(job_skills) if job_skills else 0
    
    # Normalized scores
    exp_score = min(talent_row['years_exp'] / 10, 1.0)
    rating_score = talent_row['rating'] / 5.0
    comp_score = talent_row['completion_rate'] / 100.0
    
    match_score = (
        0.45 * skill_match +
        0.25 * exp_score +
        0.20 * rating_score +
        0.10 * comp_score
    )
    return round(match_score * 100, 1)

def get_success_prob(score):
    if score > 80: return "High", "🟢"
    elif score > 60: return "Medium", "🟡"
    else: return "Low", "🔴"

def get_risk_level(completion, projects):
    if completion < 65: return "High Risk", "🔴"
    if projects > 18 and completion < 75: return "Burnout Risk", "🟠"
    return "Low Risk", "🟢"