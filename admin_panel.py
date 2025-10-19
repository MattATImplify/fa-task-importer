import streamlit as st
import pandas as pd
import json
from datetime import datetime
import hashlib
import secrets

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

def check_admin_authentication():
    """Check admin authentication"""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        # Admin login form
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            st.markdown("""
            <div style='background: white; border: 1px solid rgba(0,0,0,0.1); border-radius: 10px; padding: 2rem; margin-top: 5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 24px;'>
                    <div style='width: 40px; height: 40px; background: #030213; border-radius: 8px; display: flex; align-items: center; justify-content: center;'>
                        <span style='color: white; font-size: 18px;'>⚙️</span>
                    </div>
                    <div>
                        <div style='font-size: 18px; font-weight: 600; color: #030213;'>FacilityApps</div>
                        <div style='font-size: 11px; color: #717182;'>Admin Panel</div>
                    </div>
                </div>
                <h2 style='font-size: 20px; font-weight: 600; margin-bottom: 8px; color: #030213;'>Admin Authentication</h2>
                <p style='font-size: 14px; color: #717182; margin-bottom: 24px;'>Sign in to manage customers and system settings</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: -10px;'>", unsafe_allow_html=True)
            
            username = st.text_input(
                "Admin Username", 
                key="admin_username",
                placeholder="Enter admin username",
                label_visibility="visible"
            )
            password = st.text_input(
                "Admin Password", 
                type="password", 
                key="admin_password",
                placeholder="Enter admin password",
                label_visibility="visible"
            )
            
            if st.session_state.get("admin_auth_failed") == True:
                st.error("Invalid admin credentials")
            
            if st.button("🔒 Sign In", use_container_width=True, type="primary"):
                # Simple admin authentication (in production, use proper auth)
                if username == "admin" and password == "admin123":
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_user = username
                    st.rerun()
                else:
                    st.session_state.admin_auth_failed = True
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        return False
    else:
        return True

def main():
    """Admin panel main function"""
    if not check_admin_authentication():
        return
    
    st.title("⚙️ FacilityApps Admin Panel")
    st.markdown("**Multi-Tenant Customer Management System**")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Customers", "📊 Analytics", "⚙️ System", "🔧 Tools"])
    
    with tab1:
        st.header("Customer Management")
        
        # Customer overview
        col1, col2, col3, col4 = st.columns(4)
        
        total_customers = len(CUSTOMERS)
        active_customers = len([c for c in CUSTOMERS.values() if c["status"] == "active"])
        trial_customers = len([c for c in CUSTOMERS.values() if c["status"] == "trial"])
        suspended_customers = len([c for c in CUSTOMERS.values() if c["status"] == "suspended"])
        
        with col1:
            st.metric("Total Customers", total_customers)
        with col2:
            st.metric("Active", active_customers, delta="+2 this month")
        with col3:
            st.metric("Trial", trial_customers)
        with col4:
            st.metric("Suspended", suspended_customers)
        
        st.divider()
        
        # Customer list
        st.subheader("Customer List")
        
        # Create DataFrame for display
        customer_data = []
        for customer_id, config in CUSTOMERS.items():
            customer_data.append({
                "ID": customer_id,
                "Company Name": config["name"],
                "Subdomain": f"{customer_id}.facilityapps.co.uk",
                "Admin Email": config["admin_email"],
                "Status": config["status"].title(),
                "Created": config["created_date"],
                "Features": ", ".join(config["features"])
            })
        
        df = pd.DataFrame(customer_data)
        st.dataframe(df, use_container_width=True)
        
        # Customer actions
        st.subheader("Customer Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➕ Add New Customer", use_container_width=True):
                st.info("Add customer form would open here")
        
        with col2:
            if st.button("✏️ Edit Customer", use_container_width=True):
                st.info("Edit customer form would open here")
        
        with col3:
            if st.button("🗑️ Delete Customer", use_container_width=True):
                st.warning("Delete customer confirmation would appear here")
    
    with tab2:
        st.header("Analytics & Usage")
        
        # Usage metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Usage")
            # Mock data
            import random
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            usage = [random.randint(100, 500) for _ in months]
            
            chart_data = pd.DataFrame({
                "Month": months,
                "Jobs Imported": usage
            })
            st.bar_chart(chart_data.set_index("Month"))
        
        with col2:
            st.subheader("Customer Activity")
            # Mock data
            activity_data = pd.DataFrame({
                "Customer": ["Regular Cleaning", "Office Clean", "Hospital Clean"],
                "Last Login": ["2 hours ago", "1 day ago", "3 days ago"],
                "Jobs This Month": [45, 23, 67]
            })
            st.dataframe(activity_data, use_container_width=True)
        
        # Revenue tracking
        st.subheader("Revenue Tracking")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monthly Recurring Revenue", "£2,450", "+12%")
        with col2:
            st.metric("Average Revenue Per Customer", "£817", "+8%")
        with col3:
            st.metric("Churn Rate", "2.1%", "-0.5%")
    
    with tab3:
        st.header("System Configuration")
        
        # System settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("General Settings")
            
            system_name = st.text_input("System Name", value="FacilityApps Job Importer")
            system_url = st.text_input("System URL", value="facilityapps.co.uk")
            maintenance_mode = st.toggle("Maintenance Mode", value=False)
            
            if st.button("💾 Save Settings", use_container_width=True):
                st.success("Settings saved successfully!")
        
        with col2:
            st.subheader("Email Configuration")
            
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587)
            smtp_username = st.text_input("SMTP Username", type="password")
            smtp_password = st.text_input("SMTP Password", type="password")
            
            if st.button("📧 Test Email", use_container_width=True):
                st.info("Test email would be sent here")
    
    with tab4:
        st.header("System Tools")
        
        # Backup and restore
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Backup & Restore")
            
            if st.button("💾 Create Backup", use_container_width=True):
                st.success("Backup created successfully!")
            
            uploaded_backup = st.file_uploader("Upload Backup File", type="json")
            if uploaded_backup:
                st.info("Backup file uploaded. Click restore to apply.")
                if st.button("🔄 Restore Backup", use_container_width=True):
                    st.success("Backup restored successfully!")
        
        with col2:
            st.subheader("System Health")
            
            # Mock health checks
            health_checks = [
                ("Database", "✅ Healthy", "green"),
                ("API Services", "✅ Healthy", "green"),
                ("Email Service", "⚠️ Warning", "orange"),
                ("File Storage", "✅ Healthy", "green"),
                ("SSL Certificates", "✅ Healthy", "green")
            ]
            
            for check, status, color in health_checks:
                st.markdown(f"**{check}**: <span style='color: {color}'>{status}</span>", unsafe_allow_html=True)
            
            if st.button("🔍 Run Health Check", use_container_width=True):
                st.success("Health check completed!")
        
        # Logs
        st.subheader("System Logs")
        log_level = st.selectbox("Log Level", ["All", "Error", "Warning", "Info"])
        
        # Mock logs
        logs = [
            "2025-01-19 10:30:15 - INFO - Customer 'regularcleaning' logged in",
            "2025-01-19 10:25:42 - INFO - Customer 'officeclean' imported 15 jobs",
            "2025-01-19 10:20:18 - WARNING - API rate limit approaching for 'hospital'",
            "2025-01-19 10:15:33 - ERROR - Failed to connect to FacilityApps API for 'regularcleaning'",
            "2025-01-19 10:10:07 - INFO - System backup completed successfully"
        ]
        
        for log in logs:
            st.text(log)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Admin Panel")
        st.info(f"Logged in as: **{st.session_state.get('admin_user', 'admin')}**")
        
        st.divider()
        
        st.markdown("### Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation started...")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.session_state.admin_user = None
            st.rerun()

if __name__ == "__main__":
    main()
