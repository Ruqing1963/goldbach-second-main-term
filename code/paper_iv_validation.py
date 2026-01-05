"""
Paper IV Validation Script
The Second Main Term in Hardy-Littlewood Formula

Author: Ruqing Chen
Email: ruqing@hotmail.com
Repository: https://github.com/Ruqing1963/goldbach-second-main-term
"""

import numpy as np
import pandas as pd
from scipy.special import expi
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

class GoldbachValidator:
    """Validator for the Dirichlet character correction to Hardy-Littlewood."""
    
    def __init__(self):
        self.c2 = 0.66016181584686957  # Twin prime constant
        
    def get_chi(self, n_array, p):
        """Calculate Legendre symbol (n/p)."""
        chi = np.zeros(len(n_array))
        rems = n_array % p
        if p == 3:
            chi[rems == 1] = 1
            chi[rems == 2] = -1
        elif p == 5:
            chi[np.isin(rems, [1, 4])] = 1
            chi[np.isin(rems, [2, 3])] = -1
        elif p == 7:
            chi[np.isin(rems, [1, 2, 4])] = 1
            chi[np.isin(rems, [3, 5, 6])] = -1
        return chi
    
    def dirichlet_regression(self, df):
        """Fit Dirichlet character model to bias data."""
        # Calculate characters
        df['chi3'] = self.get_chi(df['N'].values, 3)
        df['chi5'] = self.get_chi(df['N'].values, 5)
        df['chi7'] = self.get_chi(df['N'].values, 7)
        df['chi3_5'] = df['chi3'] * df['chi5']
        df['chi3_7'] = df['chi3'] * df['chi7']
        df['chi5_7'] = df['chi5'] * df['chi7']
        
        # Filter valid samples (coprime to 105)
        mask = (df['chi3'] != 0) & (df['chi5'] != 0) & (df['chi7'] != 0)
        df_valid = df[mask].copy()
        
        # Regression
        features = ['chi3', 'chi5', 'chi7', 'chi3_5', 'chi3_7', 'chi5_7']
        X = df_valid[features]
        y = df_valid['Bias']
        
        model = LinearRegression()
        model.fit(X, y)
        
        print("="*60)
        print("Dirichlet Character Regression Results")
        print("="*60)
        print(f"\nR² Score: {model.score(X, y):.4f}")
        print(f"Intercept (c₀): {model.intercept_:+.5f}")
        print("\nFitted Coefficients:")
        for name, coef in zip(features, model.coef_):
            print(f"  {name:<8}: {coef:+.6f}")
        
        return model
    
    def mod30_analysis(self, df):
        """Analyze bias by N mod 30."""
        df['mod30'] = df['N'] % 30
        stats = df.groupby('mod30')['Bias'].agg(['mean', 'std', 'count'])
        
        print("\n" + "="*60)
        print("Mod 30 Spectral Analysis")
        print("="*60)
        
        surplus = stats['mean'].nlargest(5)
        deficit = stats['mean'].nsmallest(5)
        
        print("\nTop 5 Surplus (least negative bias):")
        for r, v in surplus.items():
            print(f"  N ≡ {r:2d} (mod 30): {v*100:+.2f}%")
        
        print("\nTop 5 Deficit (most negative bias):")
        for r, v in deficit.items():
            print(f"  N ≡ {r:2d} (mod 30): {v*100:+.2f}%")
        
        spread = (stats['mean'].max() - stats['mean'].min()) * 100
        print(f"\nSpectral Spread: {spread:.2f}%")
        
        return stats

def main():
    """Run validation on sample data."""
    print("="*60)
    print("The Second Main Term in Hardy-Littlewood Formula")
    print("Validation Script")
    print("="*60)
    
    # Generate sample data for demonstration
    np.random.seed(42)
    n_samples = 50000
    N = np.random.randint(10000, 10**7, n_samples) * 2
    
    validator = GoldbachValidator()
    
    # Simulate bias with known Dirichlet structure
    chi3 = validator.get_chi(N, 3)
    chi5 = validator.get_chi(N, 5)
    chi7 = validator.get_chi(N, 7)
    
    # True coefficients
    true_bias = -0.092 + 0.0254*chi3 + 0.0109*chi5 + 0.0071*chi7 - 0.0096*chi3*chi5
    noise = np.random.normal(0, 0.025, n_samples)
    
    df = pd.DataFrame({
        'N': N,
        'Bias': true_bias + noise
    })
    
    # Run analysis
    validator.mod30_analysis(df)
    validator.dirichlet_regression(df)
    
    print("\n" + "="*60)
    print("Validation Complete")
    print("="*60)

if __name__ == "__main__":
    main()
