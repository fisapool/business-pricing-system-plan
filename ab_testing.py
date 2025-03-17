import numpy as np
import pandas as pd
from scipy import stats

class ABTest:
    def __init__(self, experiment_name, experiment_duration_days=14):
        self.experiment_name = experiment_name
        self.experiment_duration_days = experiment_duration_days
        self.control_group = []
        self.test_group = []
        
    def assign_group(self, item_id):
        # Deterministic assignment to ensure consistency
        return 'test' if hash(f"{self.experiment_name}_{item_id}") % 2 == 0 else 'control'
    
    def get_price(self, item_id, ml_price, standard_price):
        group = self.assign_group(item_id)
        if group == 'test':
            return ml_price
        else:
            return standard_price
    
    def record_sale(self, item_id, price, revenue, profit):
        group = self.assign_group(item_id)
        sale_data = {
            'item_id': item_id,
            'price': price,
            'revenue': revenue,
            'profit': profit,
            'timestamp': pd.Timestamp.now()
        }
        
        if group == 'test':
            self.test_group.append(sale_data)
        else:
            self.control_group.append(sale_data)
    
    def analyze_results(self):
        control_df = pd.DataFrame(self.control_group)
        test_df = pd.DataFrame(self.test_group)
        
        results = {
            'control_count': len(control_df),
            'test_count': len(test_df),
            'control_revenue': control_df['revenue'].sum(),
            'test_revenue': test_df['revenue'].sum(),
            'control_profit': control_df['profit'].sum(),
            'test_profit': test_df['profit'].sum(),
        }
        
        # Statistical significance
        if len(control_df) > 0 and len(test_df) > 0:
            t_stat, p_value = stats.ttest_ind(
                test_df['profit'],
                control_df['profit'],
                equal_var=False
            )
            results['p_value'] = p_value
            results['is_significant'] = p_value < 0.05
            results['lift_percentage'] = ((test_df['profit'].mean() / control_df['profit'].mean()) - 1) * 100
        
        return results 