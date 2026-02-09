"""
Explainability Utilities
Functions for generating SHAP plots or other explainability visualizations.
"""
import shap
import matplotlib.pyplot as plt

def generate_shap_summary_plot(model, X_train, file_path='static/images/shap_summary.png'):
    """
    Generates and saves a SHAP summary plot.
    Note: This is a utility function and might require a trained model and data.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_train)
    
    plt.figure()
    shap.summary_plot(shap_values, X_train, show=False)
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
    print(f"SHAP summary plot saved to {file_path}")
