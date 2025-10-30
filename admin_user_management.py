"""
Admin Panel for User Management
Allows configuration of users and their API tokens
"""

import streamlit as st
import json
import os
from datetime import datetime

# Load user management data
def load_user_management():
    """Load user management configuration"""
    if os.path.exists('user_management.json'):
        with open('user_management.json', 'r') as f:
            return json.load(f)
    return {}

def save_user_management(data):
    """Save user management configuration"""
    with open('user_management.json', 'w') as f:
        json.dump(data, f, indent=2)

def manage_users():
    """User Management Interface"""
    st.markdown("## 👥 User Management")
    
    data = load_user_management()
    
    # Customer selection
    customers = list(data.keys())
    if not customers:
        st.warning("No customers configured. Please add a customer first.")
        return
    
    selected_customer = st.selectbox("Select Customer", customers)
    
    if selected_customer not in data:
        data[selected_customer] = {"users": []}
    
    st.markdown("---")
    
    # Add new user
    st.markdown("### ➕ Add New User")
    
    col1, col2 = st.columns(2)
    with col1:
        new_username = st.text_input("Username", key="new_username")
        new_email = st.text_input("Email", key="new_email")
    
    with col2:
        new_role = st.selectbox("Role", ["admin", "user"], key="new_role")
    
    if st.button("Add User", key="add_user"):
        if new_username and new_email:
            new_user = {
                "id": str(len(data[selected_customer]["users"]) + 1),
                "username": new_username,
                "email": new_email,
                "role": new_role,
                "api_tokens": []
            }
            data[selected_customer]["users"].append(new_user)
            save_user_management(data)
            st.success("User added successfully!")
            st.rerun()
        else:
            st.error("Please fill in all required fields")
    
    st.markdown("---")
    
    # List existing users
    st.markdown("### 📋 Existing Users")
    
    if not data[selected_customer]["users"]:
        st.info("No users configured yet.")
    else:
        for user in data[selected_customer]["users"]:
            with st.expander(f"{user['username']} ({user['email']}) - {user['role']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Role:** {user['role']}")
                    
                    # Manage API tokens
                    st.markdown("#### 🔑 API Tokens")
                    for token in user['api_tokens']:
                        st.write(f"- **{token['name']}:** {token['token']}")
                    
                    # Add new token
                    if st.button("Add API Token", key=f"add_token_{user['id']}"):
                        new_token_name = st.text_input("Token Name", key=f"token_name_{user['id']}")
                        new_token = st.text_input("Token Value", key=f"token_value_{user['id']}")
                        
                        if new_token_name and new_token:
                            token_obj = {
                                "id": str(len(user['api_tokens']) + 1),
                                "name": new_token_name,
                                "token": new_token,
                                "created_date": datetime.now().strftime("%Y-%m-%d"),
                                "expires_date": None,
                                "active": True
                            }
                            user['api_tokens'].append(token_obj)
                            save_user_management(data)
                            st.success("Token added successfully!")
                            st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete User", key=f"delete_user_{user['id']}"):
                        data[selected_customer]["users"].remove(user)
                        save_user_management(data)
                        st.success("User deleted successfully!")
                        st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="User Management", page_icon="👥")
    manage_users()

