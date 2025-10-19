"""
Custom styling for FA Job Importer based on Figma design system
Design source: https://www.figma.com/make/nI65iKCEyzqO5dfqb3fXsL/FA-Job-Importer-Design-System
"""

import streamlit as st


def apply_custom_theme():
    """
    Apply custom CSS theme extracted from Figma design system.
    This function should be called early in the Streamlit app.
    """
    
    custom_css = """
    <style>
    /* === Figma Design System CSS Variables === */
    :root {
        /* Colors */
        --background: #ffffff;
        --foreground: #030213;
        --primary: #030213;
        --primary-foreground: #ffffff;
        --secondary: #f3f3f5;
        --secondary-foreground: #030213;
        --muted: #ececf0;
        --muted-foreground: #717182;
        --accent: #e9ebef;
        --accent-foreground: #030213;
        
        /* Semantic Colors */
        --success: #00c853;
        --success-foreground: #ffffff;
        --error: #d4183d;
        --error-foreground: #ffffff;
        --warning: #ff9800;
        --warning-foreground: #ffffff;
        --info: #2196f3;
        --info-foreground: #ffffff;
        
        /* UI Elements */
        --border: rgba(0, 0, 0, 0.1);
        --input-background: #f3f3f5;
        --radius: 0.625rem;
        
        /* Sidebar */
        --sidebar: #f9f9fb;
        --sidebar-foreground: #030213;
        --sidebar-border: #ebebeb;
    }
    
    /* === Global Overrides === */
    
    /* Main container */
    .main {
        background-color: #fafafa !important;
    }
    
    /* Sidebar styling - Match Figma exactly */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e5e5e5 !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #ffffff !important;
    }
    
    /* Sidebar content padding */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 1rem !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--foreground) !important;
        font-weight: 500 !important;
    }
    
    h1 {
        font-size: 2rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* === Buttons === */
    
    /* Primary buttons */
    .stButton > button[kind="primary"],
    .stButton > button[kind="primaryFormSubmit"] {
        background-color: var(--primary) !important;
        color: var(--primary-foreground) !important;
        border: none !important;
        border-radius: var(--radius) !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[kind="primaryFormSubmit"]:hover {
        background-color: #1a1a2e !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background-color: var(--secondary) !important;
        color: var(--secondary-foreground) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: var(--accent) !important;
    }
    
    /* === Input Fields === */
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background-color: var(--input-background) !important;
        border: 1px solid var(--border) !important;
        border-radius: calc(var(--radius) - 2px) !important;
        padding: 0.5rem 0.75rem !important;
        color: var(--foreground) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(3, 2, 19, 0.1) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: var(--input-background) !important;
        border: 1px solid var(--border) !important;
        border-radius: calc(var(--radius) - 2px) !important;
    }
    
    /* === Alerts/Messages === */
    
    /* Success */
    .stSuccess {
        background-color: var(--success) !important;
        color: var(--success-foreground) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
        border-left: 4px solid #00a043 !important;
    }
    
    /* Error */
    .stError, .stException {
        background-color: var(--error) !important;
        color: var(--error-foreground) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
        border-left: 4px solid #b01030 !important;
    }
    
    /* Warning */
    .stWarning {
        background-color: var(--warning) !important;
        color: var(--warning-foreground) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
        border-left: 4px solid #e68900 !important;
    }
    
    /* Info */
    .stInfo {
        background-color: var(--info) !important;
        color: var(--info-foreground) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
        border-left: 4px solid #1976d2 !important;
    }
    
    /* === Data Tables === */
    
    /* DataFrame styling */
    .stDataFrame {
        border-radius: var(--radius) !important;
        overflow: hidden !important;
    }
    
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }
    
    /* Table headers */
    [data-testid="stDataFrame"] thead tr th {
        background-color: var(--muted) !important;
        color: var(--foreground) !important;
        font-weight: 500 !important;
        padding: 0.75rem !important;
        border-bottom: 2px solid var(--border) !important;
    }
    
    /* Table cells */
    [data-testid="stDataFrame"] tbody tr td {
        padding: 0.75rem !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    /* Alternating row colors */
    [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background-color: rgba(249, 249, 251, 0.5) !important;
    }
    
    /* === Expanders === */
    
    .streamlit-expanderHeader {
        background-color: var(--secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--accent) !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius) var(--radius) !important;
        padding: 1rem !important;
        background-color: var(--background) !important;
    }
    
    /* === Metrics === */
    
    [data-testid="stMetric"] {
        background-color: var(--secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--muted-foreground) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--foreground) !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
    }
    
    /* === Checkboxes === */
    
    .stCheckbox {
        padding: 0.25rem 0 !important;
    }
    
    .stCheckbox > label {
        font-weight: 400 !important;
        color: var(--foreground) !important;
    }
    
    /* === Toggle Switches === */
    
    .stCheckbox > label > div[data-testid="stWidgetLabel"] {
        font-weight: 500 !important;
    }
    
    /* === File Uploader === */
    
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius) !important;
        background-color: var(--secondary) !important;
        padding: 2rem !important;
    }
    
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: var(--primary) !important;
        background-color: var(--accent) !important;
    }
    
    /* === Dividers === */
    
    hr {
        border-color: var(--border) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* === Tabs === */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem !important;
        border-radius: var(--radius) var(--radius) 0 0 !important;
        font-weight: 500 !important;
        color: var(--muted-foreground) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--accent) !important;
        color: var(--foreground) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--background) !important;
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }
    
    /* === Spacing & Layout === */
    
    /* Reduce excessive padding */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
    
    /* === Scrollbars === */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--muted-foreground);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--foreground);
    }
    
    /* === Login Screen Styling === */
    
    /* Center login form */
    .login-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
    }
    
    /* === Responsive Design === */
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
    }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)


def apply_login_screen_style():
    """Apply centered styling for login screen"""
    st.markdown("""
    <style>
    /* Center the login form */
    .main > div {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 70vh;
    }
    
    /* Login card styling */
    .login-card {
        background-color: var(--background);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        max-width: 400px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

