from experta import Fact
from knowledge.rules import LoanEligibility

def evaluate_loan_facts(facts):
    engine = LoanEligibility()
    engine.reset()
    engine.declare(
        Fact(income=facts['income']),
        Fact(debt=facts['debt']),
        Fact(sources=facts['sources']),
        Fact(credit_score=facts['credit_score']),
        Fact(bankruptcy=facts['bankruptcy']),
        Fact(insurance=facts['insurance'])
    )
    engine.run()
    # Check all rules
    rule_keys = ['income', 'dti', 'sources', 'credit', 'bankruptcy', 'insurance']
    results = {}
    for key in rule_keys:
        passed = engine.passed.get(key, False)
        explanation = next((e for e in engine.explanations if e[0].lower().replace(' ', '') == key or key in e[0].lower()), None)
        if explanation:
            results[key] = {'passed': passed, 'message': explanation[2]}
        else:
            # fallback messages
            msg_map = {
                'income': 'Minimum Annual Income must be ≥ $30,000',
                'dti': 'Debt-to-Income ratio must be ≤ 20%',
                'sources': 'Must have ≥ 2 income sources',
                'credit': 'Credit Score must be greater than 80',
                'bankruptcy': 'Must have no bankruptcies',
                'insurance': 'Must have insurance coverage'
            }
            results[key] = {'passed': False, 'message': msg_map[key]}
    approved = all(r['passed'] for r in results.values())
    return {'approved': approved, 'rules': results}
