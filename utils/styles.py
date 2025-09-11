"""CSS Styles für die Ramsperger Reifen App"""

# Haupt-CSS für die App
MAIN_CSS = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --primary-color: #0ea5e9;
        --primary-dark: #0284c7;
        --secondary-color: #64748b;
        --success-color: #16a34a;
        --warning-color: #f59e0b;
        --error-color: #dc2626;
        --background-light: #f8fafc;
        --background-white: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --border-radius: 8px;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }
    
    /* General App Styling */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Headers */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Feature Boxes */
    .feature-box {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .feature-box:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .feature-box h4 {
        color: var(--text-primary);
        margin-top: 0;
        font-weight: 600;
    }
    
    .feature-box ul {
        margin: 0.5rem 0;
        padding-left: 1.2rem;
    }
    
    .feature-box li {
        margin: 0.3rem 0;
        color: var(--text-secondary);
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--success-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--warning-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .error-box {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--error-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    /* Warenkorb Styles */
    .cart-container {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid var(--primary-color);
        box-shadow: var(--shadow-md);
    }
    
    .cart-item {
        background: var(--background-white);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary-color);
        box-shadow: var(--shadow-sm);
        transition: transform 0.1s ease;
    }
    
    .cart-item:hover {
        transform: translateX(4px);
    }
    
    .total-box {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid var(--success-color);
        box-shadow: var(--shadow-md);
    }
    
    /* Service Option Styles */
    .service-option {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 0.5rem 0;
        border-left: 4px solid var(--warning-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* Reifen Card Styles */
    .tire-card {
        background: var(--background-white);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .tire-card:hover {
        border-color: var(--primary-color);
        box-shadow: var(--shadow-md);
    }
    
    .tire-card-selected {
        border: 2px solid var(--primary-color);
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        box-shadow: var(--shadow-md);
    }
    
    /* Configuration Card */
    .config-card {
        border: 2px solid var(--primary-color);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        box-shadow: var(--shadow-md);
    }
    
    /* Statistics Container */
    .stats-container {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid var(--primary-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* Filter Info */
    .filter-info {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        border-left: 4px solid var(--warning-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* Database Info */
    .database-info {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        border-left: 4px solid var(--success-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* Upload Box */
    .upload-box {
        border: 2px dashed var(--primary-color);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        box-shadow: var(--shadow-md);
        transition: border-color 0.2s ease;
    }
    
    .upload-box:hover {
        border-color: var(--primary-dark);
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    }
    
    /* Workflow Steps */
    .workflow-step {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid var(--primary-dark);
        font-family: 'Inter', sans-serif;
        box-shadow: var(--shadow-sm);
    }
    
    .workflow-step h3 {
        margin-top: 0;
        color: var(--primary-dark);
        font-weight: 600;
    }
    
    /* Buttons Styling */
    .stButton > button {
        border-radius: var(--border-radius);
        border: none;
        font-weight: 500;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Metric Styling */
    [data-testid="metric-container"] {
        background: var(--background-white);
        border: 1px solid var(--border-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Success Message Styling */
    .success-message {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        color: var(--success-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--success-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    /* Error Message Styling */
    .error-message {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        color: var(--error-color);
        padding: 1rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--error-color);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        border-radius: var(--border-radius);
        background: var(--background-light);
    }
    
    /* DataFrame Styling */
    .dataframe {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    /* Text Area Styling */
    .stTextArea > div > div > textarea {
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--border-radius);
        padding: 0.5rem 1rem;
        background: var(--background-light);
        border: 1px solid var(--border-color);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
    }
    
    /* Stock Status Colors */
    .stock-positive {
        color: var(--success-color);
        font-weight: 600;
    }
    
    .stock-zero {
        color: var(--warning-color);
        font-weight: 600;
    }
    
    .stock-negative {
        color: var(--error-color);
        font-weight: 600;
    }
    
    .stock-unknown {
        color: var(--text-secondary);
        font-style: italic;
    }
    
    /* EU Label Colors */
    .eu-label-a { color: #16a34a; font-weight: 600; }
    .eu-label-b { color: #84cc16; font-weight: 600; }
    .eu-label-c { color: #eab308; font-weight: 600; }
    .eu-label-d { color: #f59e0b; font-weight: 600; }
    .eu-label-e { color: #ef4444; font-weight: 600; }
    .eu-label-f { color: #dc2626; font-weight: 600; }
    .eu-label-g { color: #991b1b; font-weight: 600; }
    
    /* Animation Classes */
    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .feature-box, .cart-item, .workflow-step {
            padding: 1rem;
        }
    }
</style>
"""

# Helper Functions für CSS
def get_efficiency_emoji(rating):
    """Gibt Emoji für Effizienz-Rating zurück"""
    if not rating:
        return "⚪"
    rating = str(rating).strip().upper()[:1]
    return {
        "A": "🟢", "B": "🟡", "C": "🟠", 
        "D": "🟠", "E": "🔴", "F": "🔴", "G": "⚫"
    }.get(rating, "⚪")

def get_stock_display(stock_value):
    """Formatiert Bestandsanzeige mit Farben"""
    if pd.isna(stock_value) or stock_value == '':
        return "❓ unbekannt"
    
    try:
        stock_num = float(stock_value)
        if stock_num < 0:
            return f"⚠️ {int(stock_num)}"
        elif stock_num == 0:
            return f"⚪ {int(stock_num)}"
        else:
            return f"✅ {int(stock_num)}"
    except:
        return "❓ unbekannt"

def apply_main_css():
    """Wendet das Haupt-CSS auf die App an"""
    import streamlit as st
    st.markdown(MAIN_CSS, unsafe_allow_html=True)

# Spezielle CSS-Komponenten
def create_metric_card(title, value, delta=None, help_text=None):
    """Erstellt eine ansprechende Metrik-Karte"""
    delta_html = ""
    if delta:
        delta_color = "var(--success-color)" if delta.startswith("↗") else "var(--error-color)" if delta.startswith("↘") else "var(--text-secondary)"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.25rem;">{delta}</div>'
    
    help_html = ""
    if help_text:
        help_html = f'<div style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 0.5rem;">{help_text}</div>'
    
    return f"""
    <div style="
        background: var(--background-white);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        box-shadow: var(--shadow-sm);
        transition: transform 0.2s ease;
    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;">{title}</div>
        <div style="color: var(--text-primary); font-size: 1.8rem; font-weight: 700; margin: 0.25rem 0;">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """

def create_status_badge(text, status="info"):
    """Erstellt Status-Badge"""
    colors = {
        "success": "var(--success-color)",
        "warning": "var(--warning-color)", 
        "error": "var(--error-color)",
        "info": "var(--primary-color)"
    }
    
    bg_colors = {
        "success": "#f0fdf4",
        "warning": "#fef3c7",
        "error": "#fef2f2", 
        "info": "#f0f9ff"
    }
    
    color = colors.get(status, colors["info"])
    bg_color = bg_colors.get(status, bg_colors["info"])
    
    return f"""
    <span style="
        background: {bg_color};
        color: {color};
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid {color};
    ">{text}</span>
    """