from experta import *

class LoanEligibility(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.explanations = []
        self.passed = {}

    def format_money(self, amount):
        return f"${amount:,.2f}"

    @Rule(Fact(income=MATCH.income))
    def rule_income(self, income):
        passed = income >= 30000
        self.passed['income'] = passed
        if passed:
            explanation = (
                'Annual Income', 
                True, 
                f"Your annual income of {self.format_money(income)} meets our minimum requirement of $30,000"
            )
        else:
            explanation = (
                'Annual Income', 
                False, 
                f"Your annual income of {self.format_money(income)} is below our minimum requirement of $30,000"
            )
        self.explanations.append(explanation)

    @Rule(Fact(income=MATCH.income), Fact(debt=MATCH.debt))
    def rule_dti(self, income, debt):
        if income > 0:
            ratio = (debt / income) * 100
            passed = ratio <= 20
            self.passed['dti'] = passed
            if passed:
                explanation = (
                    'Debt-to-Income Ratio', 
                    True, 
                    f"Your debt-to-income ratio of {ratio:.1f}% is within our acceptable limit of 20%"
                )
            else:
                explanation = (
                    'Debt-to-Income Ratio', 
                    False, 
                    f"Your debt-to-income ratio of {ratio:.1f}% exceeds our maximum limit of 20%"
                )
        else:
            self.passed['dti'] = False
            explanation = (
                'Debt-to-Income Ratio', 
                False, 
                "Unable to calculate debt-to-income ratio with zero income"
            )
        self.explanations.append(explanation)

    @Rule(Fact(sources=MATCH.sources))
    def rule_sources(self, sources):
        passed = sources >= 2
        self.passed['sources'] = passed
        if passed:
            explanation = (
                'Income Sources', 
                True, 
                f"Having {sources} income sources meets our requirement of at least 2 sources"
            )
        else:
            explanation = (
                'Income Sources', 
                False, 
                f"Having {sources} income source{'s' if sources != 1 else ''} does not meet our minimum requirement of 2 sources"
            )
        self.explanations.append(explanation)

    @Rule(Fact(credit_score=MATCH.score))
    def rule_credit(self, score):
        passed = score > 80
        self.passed['credit'] = passed
        if passed:
            explanation = (
                'Credit Score', 
                True, 
                f"Your credit score of {score} is above our minimum requirement of 80"
            )
        else:
            explanation = (
                'Credit Score', 
                False, 
                f"Your credit score of {score} is below our minimum requirement of 80"
            )
        self.explanations.append(explanation)

    @Rule(Fact(bankruptcy=MATCH.status))
    def rule_bankruptcy(self, status):
        passed = not status
        self.passed['bankruptcy'] = passed
        if passed:
            explanation = (
                'Bankruptcy', 
                True, 
                "No bankruptcy history found - this is good!"
            )
        else:
            explanation = (
                'Bankruptcy', 
                False, 
                "We found a bankruptcy record which affects your eligibility"
            )
        self.explanations.append(explanation)

    @Rule(Fact(insurance=MATCH.status))
    def rule_insurance(self, status):
        passed = status
        self.passed['insurance'] = passed
        if passed:
            explanation = (
                'Insurance', 
                True, 
                "You have the required insurance coverage"
            )
        else:
            explanation = (
                'Insurance', 
                False, 
                "You need to have valid insurance coverage to qualify"
            )
        self.explanations.append(explanation)
