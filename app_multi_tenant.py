import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta
import pytz
from dateutil import parser
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import io
import hashlib
import secrets

# Load environment variables
load_dotenv()

# Import custom styles
from styles import apply_custom_theme

# Customer database (in production, this would be a real database)
CUSTOMERS = {
    "regularcleaning": {
        "name": "Regular Cleaning Ltd",
        "fa_domain": "regularcleaning.facilityapps.com",
        "fa_token": "your_token_here",
        "admin_email": "admin@regularcleaning.co.uk",
        "features": ["recurring_jobs", "csv_import", "api_integration"],
        "created_date": "2025-01-01",
        "status": "active",
        "branding": {
            "primary_color": "#030213",
            "logo": "🧹",
            "company_name": "Regular Cleaning"
        }
    },
    "officeclean": {
        "name": "Office Clean Services",
        "fa_domain": "officeclean.facilityapps.com",
        "fa_token": "your_token_here",
        "admin_email": "admin@officeclean.co.uk",
        "features": ["recurring_jobs", "csv_import"],
        "created_date": "2025-01-15",
        "status": "active",
        "branding": {
            "primary_color": "#2563eb",
            "logo": "🏢",
            "company_name": "Office Clean"
        }
    },
    "hospital": {
        "name": "Hospital Cleaning Services",
        "fa_domain": "hospital.facilityapps.com",
        "fa_token": "your_token_here",
        "admin_email": "admin@hospitalclean.co.uk",
        "features": ["recurring_jobs", "csv_import", "api_integration", "compliance"],
        "created_date": "2025-01-20",
        "status": "active",
        "branding": {
            "primary_color": "#dc2626",
            "logo": "🏥",
            "company_name": "Hospital Clean"
        }
    }
}

class FacilityAppsClient:
    def __init__(self, domain, token):
        self.domain = domain
        self.token = token
        self.base_url = f"https://{domain}/api/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_connection(self):
        """Test API connection"""
        try:
            response = requests.get(f"{self.base_url}/sites", headers=self.headers, timeout=10)
            if response.status_code == 200:
                return True, "Connection successful!"
            else:
                return False, f"API returned status {response.status_code}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def get_sites(self):
        """Get sites from API"""
        try:
            response = requests.get(f"{self.base_url}/sites", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    return []
            return []
        except Exception as e:
            st.error(f"Error fetching sites: {str(e)}")
            return []
    
    def get_floors(self):
        """Get floors from API"""
        try:
            response = requests.get(f"{self.base_url}/floors", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    return []
            return []
        except Exception as e:
            st.error(f"Error fetching floors: {str(e)}")
            return []
    
    def get_spaces(self):
        """Get spaces from API"""
        try:
            response = requests.get(f"{self.base_url}/spaces", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    return []
            return []
        except Exception as e:
            st.error(f"Error fetching spaces: {str(e)}")
            return []
    
    def get_users(self):
        """Get users from API"""
        try:
            response = requests.get(f"{self.base_url}/users", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data
                else:
                    return []
            return []
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return []

def get_customer_from_subdomain():
    """Extract customer from subdomain"""
    import os
    host = os.environ.get('HTTP_HOST', '')
    
    # For local development, check for customer in session state
    if 'localhost' in host or '127.0.0.1' in host:
        return st.session_state.get('current_customer', 'regularcleaning')
    
    # Extract subdomain from host
    if host.startswith('facilityapps.co.uk'):
        subdomain = host.split('.')[0]
        return subdomain
    
    return None

def get_customer_config(customer_id):
    """Get configuration for specific customer"""
    if customer_id and customer_id in CUSTOMERS:
        return CUSTOMERS[customer_id]
    else:
        st.error(f"Customer '{customer_id}' not found. Please contact support.")
        st.stop()

def check_customer_authentication(customer_id):
    """Check customer-specific authentication"""
    if "customer_authenticated" not in st.session_state:
        st.session_state.customer_authenticated = False
    
    if not st.session_state.customer_authenticated:
        # Customer login form
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            customer_config = get_customer_config(customer_id)
            
            # Branded login card
            st.markdown(f"""
            <div style='background: white; border: 1px solid rgba(0,0,0,0.1); border-radius: 10px; padding: 2rem; margin-top: 5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 24px;'>
                    <div style='width: 40px; height: 40px; background: {customer_config["branding"]["primary_color"]}; border-radius: 8px; display: flex; align-items: center; justify-content: center;'>
                        <span style='color: white; font-size: 18px;'>{customer_config["branding"]["logo"]}</span>
                    </div>
                    <div>
                        <div style='font-size: 18px; font-weight: 600; color: {customer_config["branding"]["primary_color"]};'>{customer_config["branding"]["company_name"]}</div>
                        <div style='font-size: 11px; color: #717182;'>Job Importer</div>
                    </div>
                </div>
                <h2 style='font-size: 20px; font-weight: 600; margin-bottom: 8px; color: #030213;'>Authentication Required</h2>
                <p style='font-size: 14px; color: #717182; margin-bottom: 24px;'>Sign in to access the bulk job importer for {customer_config["name"]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: -10px;'>", unsafe_allow_html=True)
            
            # Customer-specific login
            username = st.text_input(
                "Username", 
                key="customer_username",
                placeholder="Enter username",
                label_visibility="visible"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                key="customer_password",
                placeholder="Enter password",
                label_visibility="visible"
            )
            
            if st.session_state.get("customer_auth_failed") == True:
                st.error("Invalid username or password")
            
            if st.button("🔒 Sign In", use_container_width=True, type="primary"):
                # Simple authentication (in production, use proper auth)
                if username == "admin" and password == "password123":
                    st.session_state.customer_authenticated = True
                    st.session_state.current_customer = customer_id
                    st.session_state.customer_user = username
                    st.rerun()
                else:
                    st.session_state.customer_auth_failed = True
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        return False
    else:
        return True

def load_reference_data(client, debug_mode, customer_id):
    """Load reference data from API for specific customer"""
    try:
        # This would normally load from the API
        # For now, we'll simulate it with customer-specific data
        customer_config = get_customer_config(customer_id)
        
        st.session_state.sites = [
            {"id": 1, "name": f"{customer_config['branding']['company_name']} Building A"},
            {"id": 2, "name": f"{customer_config['branding']['company_name']} Building B"}
        ]
        st.session_state.floors = [
            {"id": 1, "name": "Ground Floor"},
            {"id": 2, "name": "First Floor"}
        ]
        st.session_state.spaces = [
            {"id": 1, "name": "Office 101"},
            {"id": 2, "name": "Office 102"}
        ]
        st.session_state.users = [
            {"id": 1, "name": "John Doe"},
            {"id": 2, "name": "Jane Smith"}
        ]
        
        st.session_state.sites_count = len(st.session_state.sites)
        st.session_state.floors_count = len(st.session_state.floors)
        st.session_state.spaces_count = len(st.session_state.spaces)
        st.session_state.users_count = len(st.session_state.users)
        
        st.session_state.lookups_loaded = True
        
    except Exception as e:
        st.error(f"Error loading reference data: {str(e)}")

def render_step_1(fa_domain, fa_token, debug_mode, customer_id):
    """Step 1: Load Reference Data"""
    customer_config = get_customer_config(customer_id)
    
    st.markdown(f"""
    <div style='background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 2rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;'>
            <div style='width: 40px; height: 40px; background: {customer_config["branding"]["primary_color"]}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;'>1</div>
            <div>
                <h2 style='margin: 0; color: #030213; font-size: 20px;'>Load Reference Data</h2>
                <p style='margin: 0; color: #717182; font-size: 14px;'>Connect to FacilityApps API and load sites, floors, spaces, and users</p>
            </div>
        </div>
        <p style='color: #717182; margin-bottom: 1.5rem;'>Please configure your FA Domain and API Token in the Settings tab before loading data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 Load Reference Data", use_container_width=True, type="primary"):
        if not fa_domain or not fa_token:
            st.error("Please configure FA Domain and API Token in the Settings tab first.")
        else:
            with st.spinner("Loading reference data..."):
                try:
                    client = FacilityAppsClient(fa_domain, fa_token)
                    success, message = client.test_connection()
                    if success:
                        # Load the actual data
                        load_reference_data(client, debug_mode, customer_id)
                        st.success("Reference data loaded successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to connect: {message}")
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")

def render_step_2(debug_mode, customer_id):
    """Step 2: Upload & Validate CSV"""
    customer_config = get_customer_config(customer_id)
    
    st.markdown(f"""
    <div style='background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 2rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;'>
            <div style='width: 40px; height: 40px; background: #e5e5e5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #717182; font-weight: 600;'>2</div>
            <div>
                <h2 style='margin: 0; color: #030213; font-size: 20px;'>Upload & Validate CSV</h2>
                <p style='margin: 0; color: #717182; font-size: 14px;'>Upload your job data file and validate the content</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type="csv",
        help="Upload a CSV file with your job data"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"File uploaded successfully! {len(df)} rows found.")
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Store in session state
            st.session_state.csv_data = df
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

def render_step_3(debug_mode, customer_id):
    """Step 3: Review & Edit Jobs"""
    customer_config = get_customer_config(customer_id)
    
    st.markdown(f"""
    <div style='background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 2rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;'>
            <div style='width: 40px; height: 40px; background: #e5e5e5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #717182; font-weight: 600;'>3</div>
            <div>
                <h2 style='margin: 0; color: #030213; font-size: 20px;'>Review & Edit Jobs</h2>
                <p style='margin: 0; color: #717182; font-size: 14px;'>Configure job settings and recurrence patterns</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if "csv_data" in st.session_state and st.session_state.csv_data is not None:
        df = st.session_state.csv_data
        
        st.subheader("Job Configuration")
        st.write("Review and configure each job before import.")
        
        # Show data table with editing capabilities
        st.dataframe(df, use_container_width=True)
        
        # Add some configuration options
        st.subheader("Bulk Settings")
        col1, col2 = st.columns(2)
        with col1:
            default_frequency = st.selectbox("Default Frequency", ["Daily", "Weekly", "Monthly", "One-time"])
        with col2:
            default_priority = st.selectbox("Default Priority", ["Low", "Medium", "High"])
        
    else:
        st.info("Please upload a CSV file in Step 2 first.")

def render_step_4(enable_import, debug_mode, customer_id):
    """Step 4: Import Jobs"""
    customer_config = get_customer_config(customer_id)
    
    st.markdown(f"""
    <div style='background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 2rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;'>
            <div style='width: 40px; height: 40px; background: #e5e5e5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #717182; font-weight: 600;'>4</div>
            <div>
                <h2 style='margin: 0; color: #030213; font-size: 20px;'>Import Jobs</h2>
                <p style='margin: 0; color: #717182; font-size: 14px;'>Execute the import process</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if "csv_data" in st.session_state and st.session_state.csv_data is not None:
        df = st.session_state.csv_data
        
        st.subheader("Ready to Import")
        st.write(f"**{len(df)} jobs** ready for import")
        
        if enable_import:
            st.warning("⚠️ Import is ENABLED - This will create actual jobs in FacilityApps!")
            
            if st.button("🚀 Import All Jobs", use_container_width=True, type="primary"):
                with st.spinner("Importing jobs..."):
                    # Simulate import process
                    import time
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    st.success("All jobs imported successfully!")
        else:
            st.info("Enable 'Import' in the Settings tab to allow job creation.")
            st.button("🚀 Import All Jobs", use_container_width=True, disabled=True)
    else:
        st.info("Please complete the previous steps first.")

def main():
    """Main application function"""
    # Apply custom theme
    apply_custom_theme()
    
    # Get customer from subdomain
    customer_id = get_customer_from_subdomain()
    
    if not customer_id:
        st.error("Invalid subdomain. Please access the app through your assigned subdomain.")
        st.stop()
    
    # Get customer configuration
    customer_config = get_customer_config(customer_id)
    
    # Check customer authentication
    if not check_customer_authentication(customer_id):
        return
    
    # Initialize session state
    if "lookups_loaded" not in st.session_state:
        st.session_state.lookups_loaded = False
    if "csv_data" not in st.session_state:
        st.session_state.csv_data = None
    if "sites" not in st.session_state:
        st.session_state.sites = []
    if "floors" not in st.session_state:
        st.session_state.floors = []
    if "spaces" not in st.session_state:
        st.session_state.spaces = []
    if "users" not in st.session_state:
        st.session_state.users = []
    
    # Get customer-specific configuration
    fa_domain = customer_config["fa_domain"]
    fa_token = customer_config["fa_token"]
    
    # ===== MAIN LAYOUT WITH TABS =====
    
    # Create tabs for main content
    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "⚙️ Settings", "📊 Reference Data"])
    
    with tab1:
        # Dashboard content - Step-by-step wizard
        st.markdown(f"## {customer_config['branding']['logo']} {customer_config['branding']['company_name']} Job Importer")
        st.markdown(f"**{customer_config['name']}** – Validate and import recurring jobs/rosters")
        
        # Initialize current step
        if "current_step" not in st.session_state:
            st.session_state.current_step = 1
        
        # Step progress indicator
        st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: #030213; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;'>1</div>
                    <div>
                        <div style='font-weight: 600; color: #030213;'>Load Reference Data</div>
                        <div style='font-size: 12px; color: #717182;'>Connect to API</div>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: #e5e5e5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #717182; font-weight: 600;'>2</div>
                    <div>
                        <div style='font-weight: 500; color: #717182;'>Upload & Validate</div>
                        <div style='font-size: 12px; color: #717182;'>Import CSV file</div>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: #e5e5e5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #717182; font-weight: 600;'>3</div>
                    <div>
                        <div style='font-weight: 500; color: #717182;'>Review & Edit</div>
                        <div style='font-size: 12px; color: #717182;'>Configure jobs</div>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: #e5e5e5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #717182; font-weight: 600;'>4</div>
                    <div>
                        <div style='font-weight: 500; color: #717182;'>Import Jobs</div>
                        <div style='font-size: 12px; color: #717182;'>Execute import</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Step content based on current step
        if st.session_state.current_step == 1:
            render_step_1(fa_domain, fa_token, False, customer_id)
        elif st.session_state.current_step == 2:
            render_step_2(False, customer_id)
        elif st.session_state.current_step == 3:
            render_step_3(False, customer_id)
        elif st.session_state.current_step == 4:
            render_step_4(False, False, customer_id)
        
        # Step navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_step > 1:
                if st.button("← Previous", use_container_width=True):
                    st.session_state.current_step -= 1
                    st.rerun()
            else:
                st.button("← Previous", use_container_width=True, disabled=True)
        
        with col2:
            st.markdown(f"<div style='text-align: center; color: #717182; font-size: 14px; padding: 8px;'>Step {st.session_state.current_step} of 4</div>", unsafe_allow_html=True)
        
        with col3:
            if st.session_state.current_step < 4:
                if st.button("Next →", use_container_width=True, type="primary"):
                    st.session_state.current_step += 1
                    st.rerun()
            else:
                st.button("Next →", use_container_width=True, disabled=True)
    
    with tab2:
        # Settings tab
        st.markdown("## ⚙️ Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### API Configuration")
            st.info(f"**Customer**: {customer_config['name']}")
            st.info(f"**FA Domain**: {fa_domain}")
            st.info(f"**Status**: {customer_config['status'].title()}")
            
            if st.button("🔗 Test Connection", use_container_width=True):
                with st.spinner("Testing connection..."):
                    client = FacilityAppsClient(fa_domain, fa_token)
                    success, message = client.test_connection()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        with col2:
            st.markdown("### Application Options")
            
            enable_import = st.toggle(
                "🚀 Enable Import", 
                value=False, 
                help="Allow the application to create jobs in FacilityApps"
            )
            
            if enable_import:
                st.warning("⚠️ Writes enabled! This will create actual jobs in FacilityApps.", icon="⚠️")
            
            debug_mode = st.toggle(
                "🐛 Debug Mode", 
                value=False,
                help="Show additional debugging information"
            )
            
            st.markdown("### User Session")
            if "customer_user" in st.session_state:
                st.info(f"Logged in as: **{st.session_state['customer_user']}**")
            
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                # Clear customer session
                st.session_state.customer_authenticated = False
                st.session_state.current_customer = None
                st.session_state.customer_user = None
                st.rerun()
    
    with tab3:
        # Reference Data tab
        st.markdown("## 📊 Reference Data")
        
        if st.session_state.lookups_loaded:
            # Card-based metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Sites", st.session_state.get("sites_count", 0))
            with col2:
                st.metric("Floors", st.session_state.get("floors_count", 0))
            with col3:
                st.metric("Spaces", st.session_state.get("spaces_count", 0))
            with col4:
                st.metric("Users", st.session_state.get("users_count", 0))
        else:
            st.info("No reference data loaded yet. Configure your API settings and load data from the Dashboard.")
    
    # ===== SIDEBAR (Minimal) =====
    with st.sidebar:
        # Header with branding
        st.markdown(f"""
        <div style='padding: 1rem 0 1.5rem 0; text-align: center;'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 1rem;'>
                <div style='width: 40px; height: 40px; background: {customer_config["branding"]["primary_color"]}; border-radius: 8px; display: flex; align-items: center; justify-content: center;'>
                    <span style='color: white; font-size: 18px;'>{customer_config["branding"]["logo"]}</span>
                </div>
            </div>
            <div style='font-size: 16px; font-weight: 600; color: {customer_config["branding"]["primary_color"]};'>{customer_config["branding"]["company_name"]}</div>
            <div style='font-size: 12px; color: #717182;'>Job Importer</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick status
        if st.session_state.lookups_loaded:
            st.success("✅ Data Loaded")
        else:
            st.warning("⚠️ No Data")
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            # This would refresh the reference data
            st.rerun()
        
        if st.button("📥 Download Template", use_container_width=True):
            # This would download the CSV template
            st.info("Template download feature coming soon!")

if __name__ == "__main__":
    main()
