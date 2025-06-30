from experta import Fact
from knowledge.rules import LoanEligibility

def get_friendly_summary(passed_rules, failed_rules):
    """Generate a friendly summary of the decision"""
    if not failed_rules:
        return "Congratulations! Your application meets all our requirements."
    
    if len(failed_rules) >= 5:
        return "Unfortunately, your application needs significant improvement in multiple areas."
    
    summary = "Your application "
    if len(passed_rules) > 0:
        summary += f"shows strength in {len(passed_rules)} area{'s' if len(passed_rules) > 1 else ''}, but "
    
    summary += f"needs improvement in {len(failed_rules)} area{'s' if len(failed_rules) > 1 else ''}: "
    summary += ", ".join(failed_rules)
    return summary

def evaluate_loan_facts(facts):
    # Initialize the expert system
    engine = LoanEligibility()
    engine.reset()
    
    # Declare all facts
    engine.declare(
        Fact(income=facts['income']),
        Fact(debt=facts['debt']),
        Fact(sources=facts['sources']),
        Fact(credit_score=facts['credit_score']),
        Fact(bankruptcy=facts['bankruptcy']),
        Fact(insurance=facts['insurance'])
    )
    
    # Run the expert system
    engine.run()
    
    # Process results
    results = {}
    passed_rules = []
    failed_rules = []
    
    # Map rule keys to friendly names
    friendly_names = {
        'income': 'Annual Income',
        'dti': 'Debt-to-Income Ratio',
        'sources': 'Income Sources',
        'credit': 'Credit Score',
        'bankruptcy': 'Bankruptcy Status',
        'insurance': 'Insurance Coverage'
    }
    
    # Check all rules and organize results
    rule_keys = ['income', 'dti', 'sources', 'credit', 'bankruptcy', 'insurance']
    for key in rule_keys:
        passed = engine.passed.get(key, False)
        explanation = next((e for e in engine.explanations if e[0].lower().replace(' ', '') == key or key in e[0].lower()), None)
        
        if explanation:
            results[key] = {
                'passed': passed,
                'message': explanation[2],
                'friendly_name': friendly_names[key]
            }
        else:
            # Fallback messages with friendly names
            msg_map = {
                'income': 'Your annual income must be at least $30,000',
                'dti': 'Your total debt must not exceed 20% of your annual income',
                'sources': 'You must have at least 2 sources of income',
                'credit': 'Your credit score must be above 80',
                'bankruptcy': 'You must have no recent bankruptcies',
                'insurance': 'You must have valid insurance coverage'
            }
            results[key] = {
                'passed': False,
                'message': msg_map[key],
                'friendly_name': friendly_names[key]
            }
            
        if results[key]['passed']:
            passed_rules.append(friendly_names[key])
        else:
            failed_rules.append(friendly_names[key])
    
    # Generate the overall decision
    approved = all(r['passed'] for r in results.values())
    
    return {
        'approved': approved,
        'summary': get_friendly_summary(passed_rules, failed_rules),
        'rules': results,
        'passed_count': len(passed_rules),
        'total_rules': len(rule_keys)
    }
