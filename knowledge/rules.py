from experta import *

class LoanEligibility(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.explanations = []
        self.passed = {}

    @Rule(Fact(income=P(lambda x: x >= 30000)))
    def rule_income(self):
        self.passed['income'] = True
        self.explanations.append(('Minimum Annual Income', True, 'Income ≥ $30,000'))

    @Rule(Fact(income=MATCH.income), Fact(debt=MATCH.debt), TEST(lambda income, debt: income > 0 and (debt/income) <= 0.2))
    def rule_dti(self, income, debt):
        self.passed['dti'] = True
        self.explanations.append(('Debt-to-Income Ratio', True, 'Debt ≤ 20% of income'))

    @Rule(Fact(sources=P(lambda x: x >= 2)))
    def rule_sources(self):
        self.passed['sources'] = True
        self.explanations.append(('Income Sources', True, 'Sources ≥ 2'))

    @Rule(Fact(credit_score=P(lambda x: x > 80)))
    def rule_credit(self):
        self.passed['credit'] = True
        self.explanations.append(('Credit Score', True, 'Score > 80'))

    @Rule(Fact(bankruptcy=False))
    def rule_bankruptcy(self):
        self.passed['bankruptcy'] = True
        self.explanations.append(('Bankruptcy', True, 'No bankruptcy'))

    @Rule(Fact(insurance=True))
    def rule_insurance(self):
        self.passed['insurance'] = True
        self.explanations.append(('Insurance', True, 'Has insurance'))
