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
import uuid
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import io

# Load environment variables
load_dotenv()

# Import custom styles
from styles import apply_custom_theme

class FacilityAppsClient:
    def __init__(self, domain, token):
        self.domain = domain
        self.token = token
        self.base_url = f"https://{domain}/api/v1"
        self.legacy_base_url = f"https://{domain}/api/1.0"
        self.graphql_url = f"https://{domain}/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_connection(self):
        """Test API connection"""
        try:
            response = requests.get(f"{self.base_url}/planning/sites", headers=self.headers, timeout=10)
            if response.status_code == 200:
                return True, "Connection successful!"
            else:
                return False, f"API returned status {response.status_code}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def get_sites(self):
        """Get sites from API"""
        try:
            response = requests.get(f"{self.base_url}/planning/sites", headers=self.headers, timeout=10)
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
            response = requests.get(f"{self.base_url}/planning/floors", headers=self.headers, timeout=10)
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
            response = requests.get(f"{self.base_url}/planning/spaces", headers=self.headers, timeout=10)
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
            url = f"{self.base_url}/user"
            st.write(f"🔍 DEBUG: Fetching users from: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            st.write(f"🔍 DEBUG: Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                st.write(f"🔍 DEBUG: Response data type: {type(data)}")
                st.write(f"🔍 DEBUG: Response data keys (if dict): {data.keys() if isinstance(data, dict) else 'N/A'}")
                st.write(f"🔍 DEBUG: First 500 chars of response: {str(data)[:500]}")
                
                if isinstance(data, dict) and 'data' in data:
                    st.write(f"🔍 DEBUG: Found 'data' key, returning {len(data['data'])} users")
                    return data['data']
                elif isinstance(data, list):
                    st.write(f"🔍 DEBUG: Data is a list with {len(data)} users")
                    return data
                else:
                    st.warning(f"⚠️ Unexpected user data format. Data type: {type(data)}, Data: {data}")
                    return []
            else:
                st.error(f"❌ Failed to fetch users: API returned status {response.status_code}")
                st.write(f"🔍 DEBUG: Response text: {response.text[:500]}")
                return []
                
        except Exception as e:
            st.error(f"❌ Error fetching users: {str(e)}")
            import traceback
            st.write(f"🔍 DEBUG: Full traceback:\n{traceback.format_exc()}")
            return []
    
    def create_job(self, job_data):
        """Create a job in FacilityApps"""
        try:
            url = f"{self.legacy_base_url}/planning/save/true"
            if hasattr(st, 'session_state') and st.session_state.get('debug_mode', False):
                st.write(f"🔍 DEBUG: Sending job to: {url}")
            response = requests.post(url, headers=self.headers, json=job_data, timeout=30)
            
            if response.status_code in [200, 201]:
                return True, "Success", response.json()
            else:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg += f": {error_data['message']}"
                    elif 'error' in error_data:
                        error_msg += f": {error_data['error']}"
                except:
                    error_msg += f": {response.text[:200]}"
                return False, error_msg, None
                
        except Exception as e:
            return False, f"Exception: {str(e)}", None
    
    def get_forms(self, first=50):
        """Get forms from GraphQL API"""
        try:
            query = {
                "query": f"""
                query {{
                  forms(first: {first}) {{
                    data {{
                      id
                      name
                      type
                      isLogbook
                      version
                      canSubmit
                      createdAt
                      updatedAt
                    }}
                    paginatorInfo {{
                      total
                      count
                      currentPage
                      lastPage
                    }}
                  }}
                }}
                """
            }
            
            response = requests.post(self.graphql_url, headers=self.headers, json=query, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'forms' in data['data']:
                    return data['data']['forms']['data']
                elif 'errors' in data:
                    st.error(f"GraphQL errors: {data['errors']}")
                return []
            return []
        except Exception as e:
            st.error(f"Error fetching forms: {str(e)}")
            return []
    
    def get_form_submission(self, submission_id):
        """Get a specific form submission with question configurations"""
        try:
            query = {
                "query": f"""
                query {{
                  formSubmission(id: {submission_id}) {{
                    id
                    submitterName
                    form {{
                      id
                      name
                      type
                    }}
                    answers {{
                      id
                      answer
                      answerProcessed
                      question {{
                        id
                        name
                        identifier
                        type
                        options
                        settings
                        required
                        explanation
                        order
                        defaultValue
                        maxChoices
                        optionTranslation
                        createdAt
                        updatedAt
                      }}
                    }}
                    createdAt
                    updatedAt
                  }}
                }}
                """
            }
            
            response = requests.post(self.graphql_url, headers=self.headers, json=query, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'formSubmission' in data['data']:
                    return data['data']['formSubmission']
                return None
            return None
        except Exception as e:
            st.error(f"Error fetching form submission: {str(e)}")
            return None

def build_job_payload(job, sites, floors, spaces, users, forms=None):
    """Build a proper API payload from job data"""
    
    # Helper function to get ID from name
    def get_site_id(site_name):
        for site in sites:
            if site.get('name') == site_name or site.get('title') == site_name:
                return str(site.get('id'))
        return None
    
    def get_floor_id(floor_name):
        for floor in floors:
            if floor.get('name') == floor_name or floor.get('title') == floor_name:
                return str(floor.get('id'))
        return None
    
    def get_space_id(space_name):
        for space in spaces:
            if space.get('name') == space_name or space.get('title') == space_name:
                return str(space.get('id'))
        return None
    
    def get_user_id(user_email):
        # Handle empty values and convert to string
        if pd.isna(user_email):
            return None
        user_email = str(user_email).strip()
        if not user_email:
            return None
            
        for user in users:
            if (user.get('user_name', '').lower() == user_email.lower() or 
                user.get('username', '').lower() == user_email.lower() or 
                user.get('email', '').lower() == user_email.lower()):
                return str(user.get('id'))
        return None
    
    def get_form_id(form_name):
        """Get form ID from form name"""
        if not form_name or not forms:
            return None
        form_name = str(form_name).strip()
        for form in forms:
            if form.get('name', '').strip().lower() == form_name.lower():
                return str(form.get('id'))
        return None
    
    # Get IDs from names
    site_id = get_site_id(job.get('site', ''))
    floor_id = get_floor_id(job.get('floor', ''))
    space_id = get_space_id(job.get('space', ''))
    user_id = get_user_id(job.get('assigned_to', ''))
    
    if not site_id:
        return None, f"Site '{job.get('site')}' not found"
    if not user_id:
        return None, f"User '{job.get('assigned_to')}' not found"
    
    # Build floors_spaces structure
    floors_spaces = {}
    if floor_id:
        if space_id:
            floors_spaces[floor_id] = [space_id]
        else:
            floors_spaces[floor_id] = []
    else:
        # Ensure floors_spaces is always an object, not empty
        floors_spaces = {}
    
    # Parse recurrence settings
    recurrence_type = job.get('recurrence_type', 'none')
    # Handle empty or whitespace-only recurrence_type
    if not recurrence_type or str(recurrence_type).strip() == '' or pd.isna(recurrence_type):
        recurrence_type = 'none'
    else:
        recurrence_type = str(recurrence_type).strip()
    
    date_start = job.get('date_start', '')
    date_end = str(job.get('recurrence_end_date', date_start)).strip()
    if date_end == 'nan' or date_end == 'None' or date_end == '':
        date_end = date_start
    
    # Base payload structure
    payload = {
        "id": None,
        "sequence_date": None,
        "editMode": "all",
        "mode": "roster",
        "translations": [],
        "description_translations": [],
        "date_start": date_start,
        "date_end": date_end,
        "hour_start": job.get('hour_start', '9'),
        "minute_start": job.get('minute_start', '0'),
        "hour_end": job.get('hour_end', '17'),
        "minute_end": job.get('minute_end', '0'),
        "locations": site_id,
        "floors_spaces": floors_spaces,
        "contracts": [],
        "rate": None,
        "invoicable": False,
        "clock_hourtype_id": None,
        "duration_seconds": None,
        "owners": [{"id": user_id, "employeeToPosition": {"id": "1"}}],
        "owner_roles": [],
        "approvers": [],
        "approver_roles": [],
        "watchers": [],
        "watcher_roles": [],
        "subtasks": [],
        "contractSubtask": None,
        "syncForms": False,
        "labels": [],
        "instruction-documents": [],
        "remove-instruction-documents": [],
        "repeat_interval_length": 1,
        "use_day_of_week": False,
        "frequency_daily_repeat": [],
        "frequency_weekly_repeat": [],
        "frequency_monthly_repeat": [],
        "frequency_stop_repeat": 0,
        "frequency_stop_repeat_number_value": None,
        "repeat_interval_period": None,  # Will be set based on recurrence_type
        "task_sampling_select": None,
        "subtask_sampling_select": None,
        "exception-mode": 0,
        "excludeExceptions": "1",
        "task_complete_emails": True,
        "task_canceled_emails": True,
        "save_as_concept": False,
        "task_form_submission_id": None,
        "task_form_submission_visible": False
    }
    
    # Add title translations if present
    if job.get('title_en'):
        payload["translations"] = [
            {
                "id": "new-0",
                "regionCode": "en_EN",
                "text": job.get('title_en')
            }
        ]
    
    # Add description translations if present
    if job.get('description_en'):
        payload["description_translations"] = [
            {
                "id": "new-0",
                "regionCode": "en_EN",
                "text": job.get('description_en')
            }
        ]
    
    # Add subtask if form is selected
    if job.get('form_name'):
        form_id = get_form_id(job.get('form_name'))
        if form_id:
            # Generate a unique ID for the subtask
            subtask_id = f"new_{uuid.uuid4().hex}"
            
            # Add the subtask to the payload
            payload["subtasks"] = [
                {
                    "id": subtask_id,
                    "referrer": "forms",
                    "referringId": form_id,
                    "referring_id": form_id,
                    "required": False,
                    "order": 0
                }
            ]
    
    # Configure recurrence based on type
    if recurrence_type == 'none' or recurrence_type == '':
        # One-off job
        payload["sequence_date"] = None
        payload["date_end"] = date_start
        payload["task_complete_emails"] = True
        payload["task_canceled_emails"] = True
        # Don't set repeat_interval_period for one-off jobs - leave it as set in base payload
        
    elif recurrence_type == 'daily':
        # Daily recurrence
        payload["sequence_date"] = date_start
        payload["repeat_interval_period"] = "daily"
        payload["task_complete_emails"] = False
        payload["task_canceled_emails"] = False
        
        # Parse days if specified (e.g., "Mon,Tue,Wed,Thu,Fri" for weekdays)
        days_str = str(job.get('recurrence_days', '')).strip()
        if days_str and days_str != 'nan' and days_str != 'None' and days_str != '':
            day_map = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7}
            days = [day.strip() for day in days_str.split(',')]
            payload["frequency_daily_repeat"] = [day_map.get(d, 0) for d in days if d in day_map]
        
        if date_end and date_end != date_start:
            payload["frequency_stop_repeat"] = 2
            payload["end_after_date"] = date_end
            payload["frequency_stop_repeat_number_value"] = None
        else:
            # Check if there's a recurrence_interval for number of occurrences
            recurrence_interval = str(job.get('recurrence_interval', '')).strip()
            if recurrence_interval and recurrence_interval != 'nan' and recurrence_interval != 'None' and recurrence_interval != '':
                try:
                    num_occurrences = int(recurrence_interval)
                    payload["frequency_stop_repeat"] = 1
                    payload["frequency_stop_repeat_number_value"] = num_occurrences
                    payload["end_after_date"] = None
                except ValueError:
                    pass
        
    elif recurrence_type == 'weekly':
        # Weekly recurrence
        payload["sequence_date"] = date_start
        payload["repeat_interval_period"] = "weekly"
        payload["repeat_interval_length"] = 1
        payload["task_complete_emails"] = False
        payload["task_canceled_emails"] = False
        
        # Get recurrence interval (e.g., 2 for bi-weekly)
        recurrence_interval = str(job.get('recurrence_interval', '1')).strip()
        if recurrence_interval and recurrence_interval != 'nan' and recurrence_interval != 'None' and recurrence_interval != '':
            try:
                payload["repeat_interval_length"] = int(recurrence_interval)
            except ValueError:
                payload["repeat_interval_length"] = 1
        else:
            payload["repeat_interval_length"] = 1
        
        # Add use_day_of_week field
        payload["use_day_of_week"] = False
        
        # Parse specific days (e.g., "Mon,Wed,Fri") - use frequency_daily_repeat for weekly
        days_str = str(job.get('recurrence_days', '')).strip()
        if days_str and days_str != 'nan' and days_str != 'None' and days_str != '':
            day_map = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7}
            days = [day.strip() for day in days_str.split(',')]
            payload["frequency_daily_repeat"] = [day_map.get(d, 0) for d in days if d in day_map]
        else:
            payload["frequency_daily_repeat"] = []
        
        if date_end and date_end != date_start:
            payload["frequency_stop_repeat"] = 2
            payload["end_after_date"] = date_end
            payload["frequency_stop_repeat_number_value"] = None
        else:
            # Check if there's a recurrence_interval for number of occurrences
            recurrence_interval = str(job.get('recurrence_interval', '')).strip()
            if recurrence_interval and recurrence_interval != 'nan' and recurrence_interval != 'None' and recurrence_interval != '':
                try:
                    num_occurrences = int(recurrence_interval)
                    payload["frequency_stop_repeat"] = 1
                    payload["frequency_stop_repeat_number_value"] = num_occurrences
                    payload["end_after_date"] = None
                except ValueError:
                    pass
        
    elif recurrence_type == 'biweekly':
        # Bi-weekly recurrence
        payload["sequence_date"] = date_start
        payload["repeat_interval_period"] = "weekly"
        payload["repeat_interval_length"] = 2
        payload["task_complete_emails"] = False
        payload["task_canceled_emails"] = False
        
        # Parse specific days
        days_str = str(job.get('recurrence_days', '')).strip()
        if days_str and days_str != 'nan' and days_str != 'None' and days_str != '':
            day_map = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7}
            days = [day.strip() for day in days_str.split(',')]
            payload["frequency_daily_repeat"] = [day_map.get(d, 0) for d in days if d in day_map]
        
        if date_end and date_end != date_start:
            payload["frequency_stop_repeat"] = 2
            payload["end_after_date"] = date_end
            payload["frequency_stop_repeat_number_value"] = None
        else:
            # Check if there's a recurrence_interval for number of occurrences
            recurrence_interval = str(job.get('recurrence_interval', '')).strip()
            if recurrence_interval and recurrence_interval != 'nan' and recurrence_interval != 'None' and recurrence_interval != '':
                try:
                    num_occurrences = int(recurrence_interval)
                    payload["frequency_stop_repeat"] = 1
                    payload["frequency_stop_repeat_number_value"] = num_occurrences
                    payload["end_after_date"] = None
                except ValueError:
                    pass
        
    elif recurrence_type == 'monthly':
        # Monthly recurrence
        payload["sequence_date"] = date_start
        payload["repeat_interval_period"] = "monthly"
        payload["repeat_interval_length"] = 1
        payload["use_day_of_week"] = True  # Repeat on same day of week
        payload["task_complete_emails"] = False
        payload["task_canceled_emails"] = False
        
        if date_end and date_end != date_start:
            payload["frequency_stop_repeat"] = 2
            payload["end_after_date"] = date_end
            payload["frequency_stop_repeat_number_value"] = None
        else:
            # Check if there's a recurrence_interval for number of occurrences
            recurrence_interval = str(job.get('recurrence_interval', '')).strip()
            if recurrence_interval and recurrence_interval != 'nan' and recurrence_interval != 'None' and recurrence_interval != '':
                try:
                    num_occurrences = int(recurrence_interval)
                    payload["frequency_stop_repeat"] = 1
                    payload["frequency_stop_repeat_number_value"] = num_occurrences
                    payload["end_after_date"] = None
                except ValueError:
                    pass
    
    return payload, None

def check_password():
    """Check username and password authentication"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        # Login form - Figma design style
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            # Card header with logo
            st.markdown("""
            <div style='background: white; border: 1px solid rgba(0,0,0,0.1); border-radius: 10px; padding: 2rem; margin-top: 5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 24px;'>
                    <div style='width: 40px; height: 40px; background: #030213; border-radius: 8px; display: flex; align-items: center; justify-center;'>
                        <span style='color: white; font-size: 18px;'>🔒</span>
                    </div>
                    <div>
                        <div style='font-size: 18px; font-weight: 600; color: #030213;'>FacilityApps</div>
                        <div style='font-size: 11px; color: #717182;'>Job Importer</div>
                    </div>
                </div>
                <h2 style='font-size: 20px; font-weight: 600; margin-bottom: 8px; color: #030213;'>Authentication Required</h2>
                <p style='font-size: 14px; color: #717182; margin-bottom: 24px;'>Sign in to access the bulk job importer</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: -10px;'>", unsafe_allow_html=True)
            st.text_input(
                "Username", 
                key="username",
                placeholder="Enter username",
                label_visibility="visible"
            )
            st.text_input(
                "Password", 
                type="password", 
                key="password",
                placeholder="Enter password",
                label_visibility="visible"
            )
            
            if st.session_state.get("password_correct") == False:
                st.error("Invalid username or password")
            
            if st.button("🔒 Sign In", use_container_width=True, type="primary"):
                credentials_entered()
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        return False
    else:
        return True

def credentials_entered():
    """Check entered credentials"""
    try:
        # Try Azure environment variables first (production)
        master_username = os.getenv("MASTER_USERNAME", "")
        master_password = os.getenv("MASTER_PASSWORD", "")
        
        # Fallback to .env file (local development)
        if not master_username or not master_password:
            from dotenv import load_dotenv
            load_dotenv()
            master_username = os.getenv("MASTER_USERNAME", "")
            master_password = os.getenv("MASTER_PASSWORD", "")
        
        # Final fallback to Streamlit secrets
        if not master_username or not master_password:
            master_username = st.secrets["auth"]["master_username"]
            master_password = st.secrets["auth"]["master_password"]
        
        if (st.session_state["username"] == master_username and 
            st.session_state["password"] == master_password):
            st.session_state.password_correct = True
            st.session_state.logged_in_user = st.session_state["username"]
        else:
            st.session_state.password_correct = False
    except KeyError:
        st.error("Authentication not configured. Please check environment variables or .env file")
        st.session_state.password_correct = False

def load_reference_data(client, debug_mode):
    """Load reference data from API"""
    try:
        st.info("📡 Loading reference data from API...")
        
        # Load actual data from the API
        st.write("⏳ Fetching sites...")
        st.session_state.sites = client.get_sites()
        st.write(f"✅ Loaded {len(st.session_state.sites)} sites")
        
        # Debug: Show sample site data structure
        if debug_mode and st.session_state.sites:
            st.write("🔍 DEBUG: Sample site data structure:")
            st.write(st.session_state.sites[0])
        
        st.write("⏳ Fetching floors...")
        st.session_state.floors = client.get_floors()
        st.write(f"✅ Loaded {len(st.session_state.floors)} floors")
        
        # Debug: Show sample floor data structure
        if debug_mode and st.session_state.floors:
            st.write("🔍 DEBUG: Sample floor data structure:")
            st.write(st.session_state.floors[0])
        
        st.write("⏳ Fetching spaces...")
        st.session_state.spaces = client.get_spaces()
        st.write(f"✅ Loaded {len(st.session_state.spaces)} spaces")
        
        # Debug: Show sample space data structure
        if debug_mode and st.session_state.spaces:
            st.write("🔍 DEBUG: Sample space data structure:")
            st.write(st.session_state.spaces[0])
        
        st.write("⏳ Fetching users...")
        st.session_state.users = client.get_users()
        st.write(f"✅ Loaded {len(st.session_state.users)} users")
        
        st.write("⏳ Fetching forms...")
        st.session_state.forms = client.get_forms()
        st.write(f"✅ Loaded {len(st.session_state.forms)} forms")
        
        if debug_mode and st.session_state.users:
            st.write("🔍 DEBUG: User data analysis:")
            sample_user = st.session_state.users[0]
            st.write(f"  - Sample user: {sample_user}")
            st.write(f"  - email field: '{sample_user.get('email', 'MISSING')}'")
            st.write(f"  - user_name field: '{sample_user.get('user_name', 'MISSING')}'")
            st.write(f"  - username field: '{sample_user.get('username', 'MISSING')}'")
            st.write(f"  - name field: '{sample_user.get('name', 'MISSING')}'")
            st.write(f"  - All fields: {list(sample_user.keys())}")
        
        if debug_mode and st.session_state.forms:
            st.write("🔍 DEBUG: Forms data analysis:")
            sample_form = st.session_state.forms[0]
            st.write(f"  - Sample form: {sample_form}")
            st.write(f"  - Form types: {[f.get('type') for f in st.session_state.forms[:5]]}")
            st.write(f"  - Form names: {[f.get('name') for f in st.session_state.forms[:5]]}")
        
        st.session_state.sites_count = len(st.session_state.sites)
        st.session_state.floors_count = len(st.session_state.floors)
        st.session_state.spaces_count = len(st.session_state.spaces)
        st.session_state.users_count = len(st.session_state.users)
        st.session_state.forms_count = len(st.session_state.forms)
        
        # Debug: Show relationship analysis
        if debug_mode:
            st.write("🔍 DEBUG: Relationship Analysis:")
            
            # Analyze site-floor relationships
            if st.session_state.sites and st.session_state.floors:
                st.write("**Site-Floor Relationships:**")
                for site in st.session_state.sites[:3]:  # Show first 3 sites
                    site_id = site.get('id')
                    site_name = site.get('name', site.get('title', ''))
                    matching_floors = []
                    
                    for floor in st.session_state.floors:
                        # Use siteId as specified
                        floor_site_ref = floor.get('siteId')
                        if str(floor_site_ref) == str(site_id):
                            matching_floors.append(floor.get('name', floor.get('title', '')))
                    
                    st.write(f"  - Site '{site_name}' (ID: {site_id}) → {len(matching_floors)} floors: {matching_floors}")
            
            # Analyze floor-space relationships  
            if st.session_state.floors and st.session_state.spaces:
                st.write("**Floor-Space Relationships:**")
                for floor in st.session_state.floors[:3]:  # Show first 3 floors
                    floor_id = floor.get('id')
                    floor_name = floor.get('name', floor.get('title', ''))
                    matching_spaces = []
                    
                    for space in st.session_state.spaces:
                        # Use floor_Id (capital I) as likely pattern
                        space_floor_ref = space.get('floor_Id')
                        if str(space_floor_ref) == str(floor_id):
                            matching_spaces.append(space.get('name', space.get('title', '')))
                    
                    st.write(f"  - Floor '{floor_name}' (ID: {floor_id}) → {len(matching_spaces)} spaces: {matching_spaces}")
        
        st.session_state.lookups_loaded = True
        
        st.success(f"✅ Reference data loaded successfully! Sites: {len(st.session_state.sites)}, Floors: {len(st.session_state.floors)}, Spaces: {len(st.session_state.spaces)}, Users: {len(st.session_state.users)}, Forms: {len(st.session_state.forms)}")
        
        if debug_mode:
            st.write(f"Debug: Loaded {len(st.session_state.sites)} sites")
            st.write(f"Debug: Loaded {len(st.session_state.floors)} floors")
            st.write(f"Debug: Loaded {len(st.session_state.spaces)} spaces")
            st.write(f"Debug: Loaded {len(st.session_state.users)} users")
            
            # Show sample user data for debugging
            if st.session_state.users:
                st.write("Debug: Sample user data:")
                st.write(st.session_state.users[0])
        
    except Exception as e:
        st.error(f"Error loading reference data: {str(e)}")
        import traceback
        st.write(f"🔍 DEBUG: Full error:\n{traceback.format_exc()}")

def render_step_1(fa_domain, fa_token, debug_mode):
    """Step 1: Load Reference Data"""
    st.markdown("""
    <div style='background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 2rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;'>
            <div style='width: 40px; height: 40px; background: #030213; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;'>1</div>
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
                        load_reference_data(client, debug_mode)
                        st.success("Reference data loaded successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to connect: {message}")
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")

def render_step_2(debug_mode):
    """Step 2: Upload & Validate CSV"""
    st.markdown("""
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

def is_empty(value):
    """Check if a value is empty or None"""
    if value is None:
        return True
    if pd.isna(value):
        return True
    if isinstance(value, str):
        return value.strip() == ''
    return False

def save_import_payload(job_data, payload, status, error_message=None):
    """Save JSON payload for each job import"""
    try:
        # Create payloads directory if it doesn't exist
        payloads_dir = "payloads"
        if not os.path.exists(payloads_dir):
            os.makedirs(payloads_dir)
        
        # Create timestamp for this import session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = str(uuid.uuid4())[:8]  # Short unique ID for this session
        
        # Create filename
        job_title = job_data.get('title_en', job_data.get('job_title', 'Unknown'))
        safe_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:30]  # Limit length
        
        filename = f"payload_{timestamp}_{session_id}_{safe_title}.json"
        filepath = os.path.join(payloads_dir, filename)
        
        # Create payload record
        payload_record = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "job_title": job_title,
                "status": status,
                "error_message": error_message,
                "job_data": job_data
            },
            "api_payload": payload
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload_record, f, indent=2, ensure_ascii=False)
        
        return filepath
        
    except Exception as e:
        st.error(f"Error saving payload: {str(e)}")
        return None

def validate_job_row(job, sites, floors, spaces, users, debug_mode=False, forms=None):
    """Validate a single job row and return list of errors"""
    errors = []
    
    # Check required fields
    if is_empty(job.get('title_en', job.get('job_title', ''))):
        errors.append("Job title is required")
    
    if is_empty(job.get('assigned_to', '')):
        errors.append("Assigned user is required")
    
    if is_empty(job.get('site', '')):
        errors.append("Site is required")
    
    # Floor and space are optional, but if provided should match reference data
    
    if is_empty(job.get('date_start', '')):
        errors.append("Start date is required")
    
    # Check if site exists in reference data
    if not is_empty(job.get('site', '')):
        site_found = False
        site_name = str(job.get('site', '')).strip()
        for site in sites:
            site_ref_name = site.get('name', site.get('title', ''))
            if site_ref_name and str(site_ref_name).strip().lower() == site_name.lower():
                site_found = True
                break
        if not site_found:
            errors.append(f"Site '{site_name}' not found in reference data")
    
    # Check if floor exists in reference data
    if not is_empty(job.get('floor', '')):
        floor_found = False
        floor_name = str(job.get('floor', '')).strip()
        for floor in floors:
            floor_ref_name = floor.get('name', floor.get('title', ''))
            if floor_ref_name and str(floor_ref_name).strip().lower() == floor_name.lower():
                floor_found = True
                break
        if not floor_found:
            errors.append(f"Floor '{floor_name}' not found in reference data")
    
    # Check if space exists in reference data
    if not is_empty(job.get('space', '')):
        space_found = False
        space_name = str(job.get('space', '')).strip()
        for space in spaces:
            space_ref_name = space.get('name', space.get('title', ''))
            if space_ref_name and str(space_ref_name).strip().lower() == space_name.lower():
                space_found = True
                break
        if not space_found:
            errors.append(f"Space '{space_name}' not found in reference data")
    elif debug_mode:
        st.write(f"🔍 DEBUG: Space is empty/NaN - skipping validation")
    
    # Check if assigned user exists
    if not is_empty(job.get('assigned_to', '')):
        user_found = False
        # Convert to string and handle empty values
        assigned_email_raw = job.get('assigned_to', '')
        if pd.isna(assigned_email_raw):
            assigned_email = ''
        else:
            assigned_email = str(assigned_email_raw).strip()
        
        if debug_mode:
            st.write(f"🔍 DEBUG: Looking for user: '{assigned_email}'")
            st.write(f"🔍 DEBUG: Total users loaded: {len(users)}")
            st.write(f"🔍 DEBUG: First 3 users structure:")
            for i, u in enumerate(users[:3]):
                st.write(f"  User {i+1}: {u}")
            st.write(f"🔍 DEBUG: Available emails: {[u.get('email', 'NO_EMAIL') for u in users[:5]]}")
            st.write(f"🔍 DEBUG: Available user_names: {[u.get('user_name', 'NO_USER_NAME') for u in users[:5]]}")
        
        # Only proceed if we have a non-empty assigned_email
        if assigned_email:
            for user in users:
                user_email = user.get('email', '')
                user_name = user.get('user_name', '')
                username = user.get('username', '')
                
                if (user_email.lower() == assigned_email.lower() or 
                    user_name.lower() == assigned_email.lower() or 
                    username.lower() == assigned_email.lower()):
                    user_found = True
                    if debug_mode:
                        st.write(f"🔍 DEBUG: Found matching user: {user}")
                    break
                    
            if not user_found:
                errors.append(f"User '{assigned_email}' not found in reference data")
    
    # Check if form_name is provided and exists in reference data (optional field)
    form_name = job.get('form_name', '')
    if form_name and not pd.isna(form_name) and str(form_name).strip():
        form_name = str(form_name).strip()
        if form_name and forms:
            form_found = False
            for form in forms:
                form_ref_name = form.get('name', '')
                if form_ref_name and str(form_ref_name).strip().lower() == form_name.lower():
                    form_found = True
                    break
            if not form_found:
                errors.append(f"Form '{form_name}' not found in reference data")
    
    return errors

def render_step_3(debug_mode):
    """Step 3: Review & Edit Jobs"""
    # Make the content area wider for better job review experience
    st.markdown("""
    <style>
    /* Target the specific Streamlit main container that controls width */
    .stMainBlockContainer.block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Target the emotion cache class specifically */
    .st-emotion-cache-1w723zb {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Ensure the main element uses full width */
    .main {
        max-width: 100% !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: white; border: 1px solid #e5e5e5; border-radius: 10px; padding: 2rem; margin-bottom: 1rem;'>
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;'>
            <div style='width: 40px; height: 40px; background: #e5e5e5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #717182; font-weight: 600;'>3</div>
            <div>
                <h2 style='margin: 0; color: #030213; font-size: 20px;'>Review & Edit Jobs</h2>
                <p style='margin: 0; color: #717182; font-size: 14px;'>Validate and configure job settings and recurrence patterns</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if "csv_data" not in st.session_state or st.session_state.csv_data is None:
        st.info("Please upload a CSV file in Step 2 first.")
        return
    
    if not st.session_state.get('lookups_loaded', False):
        st.warning("Please load reference data in Step 1 first.")
        return
    
    df = st.session_state.csv_data
    
    # Convert dataframe to list of dictionaries for easier editing
    if 'edited_jobs' not in st.session_state:
        # Clear any existing validation cache when loading new CSV
        st.session_state.jobs_validated = {}
        # Preprocess the CSV data to map field names correctly
        jobs = []
        for _, row in df.iterrows():
            job = {
                'title_en': row.get('title_en', ''),
                'description_en': row.get('description_en', ''),
                'date_start': row.get('date_start', ''),
                'recurrence_end_date': row.get('recurrence_end_date', ''),
                'hour_start': str(int(row.get('hour_start', 9))) if pd.notna(row.get('hour_start')) else '9',
                'minute_start': str(int(row.get('minute_start', 0))) if pd.notna(row.get('minute_start')) else '0',
                'hour_end': str(int(row.get('hour_end', 17))) if pd.notna(row.get('hour_end')) else '17',
                'minute_end': str(int(row.get('minute_end', 0))) if pd.notna(row.get('minute_end')) else '0',
                'site': row.get('site_name', ''),
                'floor': row.get('floor_name', ''),
                'space': row.get('space_name', ''),
                'assigned_to': row.get('owner_email', ''),  # Map owner_email to assigned_to
                'labels': row.get('label_list', '').split(',') if pd.notna(row.get('label_list')) and str(row.get('label_list', '')).strip() else [],
                'recurrence_type': row.get('recurrence_type', 'none'),
                'recurrence_days': row.get('recurrence_days', ''),
                'recurrence_months': row.get('recurrence_months', ''),
                'recurrence_interval': row.get('recurrence_interval', ''),
                'form_name': str(row.get('form_name', '')).strip() if pd.notna(row.get('form_name', '')) else ''  # Add form_name from CSV, handle NaN
            }
            # Clean up labels (remove empty strings and whitespace)
            if isinstance(job.get('labels'), list):
                job['labels'] = [label.strip() for label in job['labels'] if label.strip()]
            else:
                job['labels'] = []
            jobs.append(job)
        
        if debug_mode:
            st.write(f"🔍 DEBUG: Processed {len(jobs)} jobs from CSV")
            if jobs:
                st.write(f"🔍 DEBUG: Sample job: {jobs[0]}")
        
        st.session_state.edited_jobs = jobs
    
    # Get reference data
    sites = st.session_state.get('sites', [])
    floors = st.session_state.get('floors', [])
    spaces = st.session_state.get('spaces', [])
    users = st.session_state.get('users', [])
    forms = st.session_state.get('forms', [])
    
    # Debug: Show user data structure
    if debug_mode and users:
        st.write(f"🔍 DEBUG: Found {len(users)} users in session state")
        st.write(f"🔍 DEBUG: First user structure: {users[0]}")
        st.write(f"🔍 DEBUG: User keys: {users[0].keys() if isinstance(users[0], dict) else 'Not a dict'}")
    
    # Validate all jobs (only if not already validated or if this is a fresh load)
    if 'jobs_validated' not in st.session_state:
        st.session_state.jobs_validated = {}
    
    valid_count = 0
    invalid_count = 0
    
    for idx, job in enumerate(st.session_state.edited_jobs):
        # Only re-validate if this job hasn't been validated before or if we're forcing validation
        if idx not in st.session_state.jobs_validated or st.session_state.get('force_validate', False):
            errors = validate_job_row(job, sites, floors, spaces, users, debug_mode, forms)
            st.session_state.edited_jobs[idx]['_validation_errors'] = errors
            st.session_state.jobs_validated[idx] = True
        else:
            errors = st.session_state.edited_jobs[idx].get('_validation_errors', [])
        
        if errors:
            invalid_count += 1
        else:
            valid_count += 1
    
    # Reset force validation flag
    if 'force_validate' in st.session_state:
        st.session_state.force_validate = False
    
    # Show summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", len(st.session_state.edited_jobs))
    with col2:
        st.metric("✅ Valid", valid_count)
    with col3:
        st.metric("❌ Invalid", invalid_count)
    
    st.markdown("---")
    
    # Render each job as a collapsible card
    for idx, job in enumerate(st.session_state.edited_jobs):
        errors = job.get('_validation_errors', [])
        is_valid = len(errors) == 0
        
        # Job summary for collapsed view
        job_title = job.get('title_en', job.get('job_title', f'Job {idx+1}'))
        site = job.get('site', 'N/A')
        assigned_to = job.get('assigned_to', 'N/A')
        date_start = job.get('date_start', 'N/A')
        
        status_icon = "✅" if is_valid else "❌"
        
        # Expander - only expand invalid jobs by default
        with st.expander(
            f"{status_icon} {job_title} • {site} • {assigned_to} • {date_start}",
            expanded=not is_valid
        ):
            if not is_valid:
                st.error("**Validation Errors:**")
                for error in errors:
                    st.write(f"• {error}")
                st.markdown("---")
            
            # Editing form
            col1, col2 = st.columns(2)
            
            with col1:
                # Job Title
                job_title_edit = st.text_input(
                    "Job Title",
                    value=job_title,
                    key=f"job_title_{idx}"
                )
                st.session_state.edited_jobs[idx]['title_en'] = job_title_edit
                
                # Site dropdown
                # Filter out empty values and convert to string
                site_options = []
                for s in sites:
                    site_name = s.get('name', s.get('title', ''))
                    if site_name and not pd.isna(site_name) and str(site_name).strip():
                        site_options.append(str(site_name).strip())
                
                if not site_options:
                    st.warning("No sites loaded. Please load reference data first.")
                    selected_site = job.get('site', '')
                else:
                    # Add "(Not assigned)" option at the start
                    site_options_with_blank = ["(Not assigned)"] + site_options
                    
                    current_site = job.get('site', '')
                    # Handle empty values in current_site
                    if pd.isna(current_site) or not current_site or str(current_site).strip() == '':
                        current_site = ''
                    
                    # Determine the index based on current_site
                    if not current_site or current_site == '':
                        default_index = 0  # "(Not assigned)"
                    elif current_site in site_options:
                        default_index = site_options_with_blank.index(current_site)
                    else:
                        # Keep original site if it exists, add it to options
                        site_options_with_blank = [current_site] + site_options_with_blank
                        default_index = 0
                    
                    selected_site = st.selectbox(
                        "Site",
                        options=site_options_with_blank,
                        index=default_index,
                        key=f"site_{idx}"
                    )
                    
                    # Convert "(Not assigned)" back to empty string
                    if selected_site == "(Not assigned)":
                        selected_site = ''
                
                # Only update if the value actually changed
                if st.session_state.edited_jobs[idx].get('site') != selected_site:
                    st.session_state.edited_jobs[idx]['site'] = selected_site
                    # Clear floor and space when site changes
                    st.session_state.edited_jobs[idx]['floor'] = ''
                    st.session_state.edited_jobs[idx]['space'] = ''
                
                # Floor dropdown - filter by selected site
                # Get the current site to filter floors
                current_site_for_floor = selected_site if 'selected_site' in locals() else job.get('site', '')
                if pd.isna(current_site_for_floor) or not current_site_for_floor or str(current_site_for_floor).strip() == '':
                    current_site_for_floor = ''
                
                # Filter floors by site
                floor_options = []
                if current_site_for_floor:
                    # Find the site ID for the selected site
                    site_id = None
                    if debug_mode:
                        st.write(f"🔍 DEBUG: Looking for site: '{current_site_for_floor}'")
                        st.write(f"🔍 DEBUG: Available sites: {[s.get('name', s.get('title', '')) for s in sites]}")
                    
                    for s in sites:
                        site_name = s.get('name', s.get('title', ''))
                        if debug_mode:
                            st.write(f"🔍 DEBUG: Checking site '{site_name}' (ID: {s.get('id')}) against '{current_site_for_floor}'")
                        if site_name and str(site_name).strip().lower() == current_site_for_floor.lower():
                            site_id = str(s.get('id'))
                            if debug_mode:
                                st.write(f"🔍 DEBUG: ✅ Found matching site! ID: {site_id}")
                            break
                    
                    if debug_mode and not site_id:
                        st.write(f"🔍 DEBUG: ❌ No matching site found for '{current_site_for_floor}'")
                    
                    # Filter floors for this site
                    if site_id:
                        if debug_mode:
                            st.write(f"🔍 DEBUG: Looking for floors with site_id = '{site_id}'")
                            st.write(f"🔍 DEBUG: Sample floor data: {floors[0] if floors else 'No floors'}")
                            st.write(f"🔍 DEBUG: All floor data keys: {list(floors[0].keys()) if floors else 'No floors'}")
                        
                        for f in floors:
                            # Use siteId as specified
                            floor_site_id = str(f.get('siteId', ''))
                            
                            if debug_mode and len(floor_options) < 5:  # Show more for debugging
                                st.write(f"🔍 DEBUG: Floor '{f.get('name', '')}' - siteId: '{floor_site_id}'")
                                st.write(f"  - Match: '{floor_site_id}' == '{site_id}' ? {floor_site_id == site_id}")
                            
                            if floor_site_id == site_id:
                                floor_name = f.get('name', f.get('title', ''))
                                if floor_name and not pd.isna(floor_name) and str(floor_name).strip():
                                    floor_options.append(str(floor_name).strip())
                        if debug_mode:
                            if floor_options:
                                st.write(f"🔍 DEBUG: Found {len(floor_options)} floors for site '{current_site_for_floor}' (ID: {site_id})")
                            else:
                                st.write(f"🔍 DEBUG: No floors found for site '{current_site_for_floor}' (ID: {site_id}) - checking all floors...")
                                for f in floors[:3]:  # Show first 3 floors
                                    st.write(f"  - Floor '{f.get('name', '')}' has site ref: {f.get('site_Id') or f.get('site_id') or f.get('site') or f.get('siteId') or f.get('site_ref')}")
                else:
                    # No site selected, show all floors
                    for f in floors:
                        floor_name = f.get('name', f.get('title', ''))
                        if floor_name and not pd.isna(floor_name) and str(floor_name).strip():
                            floor_options.append(str(floor_name).strip())
                
                if not floor_options:
                    if current_site_for_floor:
                        st.info(f"No floors available for site '{current_site_for_floor}' - this is normal if the site doesn't have floors.")
                        # Still show dropdown with "(Not assigned)" option
                        floor_options_with_blank = ["(Not assigned)"]
                        # Auto-clear any existing floor value when no floors exist
                        selected_floor = ''
                    else:
                        st.info("No floors loaded. Please load reference data first.")
                        floor_options_with_blank = ["(Not assigned)"]
                        selected_floor = job.get('floor', '')
                    
                    # Show dropdown even when no floors exist
                    selected_floor = st.selectbox(
                        "Floor",
                        options=floor_options_with_blank,
                        index=0,  # Default to "(Not assigned)"
                        key=f"floor_{idx}"
                    )
                    
                    # Convert "(Not assigned)" back to empty string
                    if selected_floor == "(Not assigned)":
                        selected_floor = ''
                else:
                    # Add "(Not assigned)" option at the start
                    floor_options_with_blank = ["(Not assigned)"] + floor_options
                    
                    current_floor = job.get('floor', '')
                    # Handle empty values in current_floor
                    if pd.isna(current_floor) or not current_floor or str(current_floor).strip() == '':
                        current_floor = ''
                    
                    # Determine the index based on current_floor
                    if not current_floor or current_floor == '':
                        default_index = 0  # "(Not assigned)"
                    elif current_floor in floor_options:
                        default_index = floor_options_with_blank.index(current_floor)
                    else:
                        # Keep original floor if it exists, add it to options
                        floor_options_with_blank = [current_floor] + floor_options_with_blank
                        default_index = 0
                    
                    selected_floor = st.selectbox(
                        "Floor",
                        options=floor_options_with_blank,
                        index=default_index,
                        key=f"floor_{idx}"
                    )
                    
                    # Convert "(Not assigned)" back to empty string
                    if selected_floor == "(Not assigned)":
                        selected_floor = ''
                
                # Only update if the value actually changed
                if st.session_state.edited_jobs[idx].get('floor') != selected_floor:
                    st.session_state.edited_jobs[idx]['floor'] = selected_floor
                    # Clear space when floor changes
                    st.session_state.edited_jobs[idx]['space'] = ''
                
                # Space dropdown - filter by selected floor
                # Get the current floor to filter spaces
                current_floor_for_space = selected_floor if 'selected_floor' in locals() else job.get('floor', '')
                if pd.isna(current_floor_for_space) or not current_floor_for_space or str(current_floor_for_space).strip() == '':
                    current_floor_for_space = ''
                
                # Filter spaces by floor
                space_options = []
                if current_floor_for_space:
                    # Find the floor ID for the selected floor
                    floor_id = None
                    for f in floors:
                        floor_name = f.get('name', f.get('title', ''))
                        if floor_name and str(floor_name).strip().lower() == current_floor_for_space.lower():
                            floor_id = str(f.get('id'))
                            break
                    
                    # Filter spaces for this floor
                    if floor_id:
                        if debug_mode:
                            st.write(f"🔍 DEBUG: Looking for spaces with floor_id = '{floor_id}'")
                            st.write(f"🔍 DEBUG: Sample space data: {spaces[0] if spaces else 'No spaces'}")
                        
                        for s in spaces:
                            # Use floor_Id (capital I) as likely pattern
                            space_floor_id = str(s.get('floor_Id', ''))
                            if debug_mode and len(space_options) < 3:  # Only show first few for debugging
                                st.write(f"🔍 DEBUG: Space '{s.get('name', '')}' has floor_Id: '{space_floor_id}'")
                            
                            if space_floor_id == floor_id:
                                space_name = s.get('name', s.get('title', ''))
                                if space_name and not pd.isna(space_name) and str(space_name).strip():
                                    space_options.append(str(space_name).strip())
                        if debug_mode:
                            if space_options:
                                st.write(f"🔍 DEBUG: Found {len(space_options)} spaces for floor '{current_floor_for_space}' (ID: {floor_id})")
                            else:
                                st.write(f"🔍 DEBUG: No spaces found for floor '{current_floor_for_space}' (ID: {floor_id}) - this is normal")
                else:
                    # No floor selected, show all spaces
                    for s in spaces:
                        space_name = s.get('name', s.get('title', ''))
                        if space_name and not pd.isna(space_name) and str(space_name).strip():
                            space_options.append(str(space_name).strip())
                
                if not space_options:
                    if current_floor_for_space:
                        st.info(f"No spaces available for floor '{current_floor_for_space}' - this is normal if the floor doesn't have spaces.")
                        # Still show dropdown with "(Not assigned)" option
                        space_options_with_blank = ["(Not assigned)"]
                        # Auto-clear any existing space value when no spaces exist
                        selected_space = ''
                    else:
                        st.info("No spaces loaded. Please load reference data first.")
                        space_options_with_blank = ["(Not assigned)"]
                        selected_space = job.get('space', '')
                    
                    # Show dropdown even when no spaces exist
                    selected_space = st.selectbox(
                        "Space",
                        options=space_options_with_blank,
                        index=0,  # Default to "(Not assigned)"
                        key=f"space_{idx}"
                    )
                    
                    # Convert "(Not assigned)" back to empty string
                    if selected_space == "(Not assigned)":
                        selected_space = ''
                else:
                    # Add "(Not assigned)" option at the start
                    space_options_with_blank = ["(Not assigned)"] + space_options
                    
                    current_space = job.get('space', '')
                    # Handle empty values in current_space
                    if pd.isna(current_space) or not current_space or str(current_space).strip() == '':
                        current_space = ''
                    
                    # Determine the index based on current_space
                    if not current_space or current_space == '':
                        default_index = 0  # "(Not assigned)"
                    elif current_space in space_options:
                        default_index = space_options_with_blank.index(current_space)
                    else:
                        # Keep original space if it exists, add it to options
                        space_options_with_blank = [current_space] + space_options_with_blank
                        default_index = 0
                    
                    selected_space = st.selectbox(
                        "Space",
                        options=space_options_with_blank,
                        index=default_index,
                        key=f"space_{idx}"
                    )
                    
                    # Convert "(Not assigned)" back to empty string
                    if selected_space == "(Not assigned)":
                        selected_space = ''
                
                # Only update if the value actually changed
                if st.session_state.edited_jobs[idx].get('space') != selected_space:
                    st.session_state.edited_jobs[idx]['space'] = selected_space
            
            with col2:
                # User dropdown
                user_options = [u.get('user_name', u.get('username', u.get('name', u.get('email', '')))) for u in users if u.get('user_name') or u.get('username') or u.get('name') or u.get('email')]
                
                if not user_options:
                    st.warning("No users loaded. Please load reference data first.")
                    selected_user = job.get('assigned_to', '')
                else:
                    # Add blank option at the start
                    user_options_with_blank = ["(Not assigned)"] + user_options
                    
                    current_user = job.get('assigned_to', '')
                    # Determine the index based on current_user
                    if not current_user or current_user == '':
                        default_index = 0  # "(Not assigned)"
                    elif current_user in user_options:
                        default_index = user_options_with_blank.index(current_user)
                    else:
                        # Current user not in list, add it
                        user_options_with_blank.insert(1, current_user)
                        default_index = 1
                    
                    selected_user = st.selectbox(
                        "Assigned To",
                        options=user_options_with_blank,
                        index=default_index,
                        key=f"user_{idx}"
                    )
                    
                    # Convert "(Not assigned)" back to empty string
                    if selected_user == "(Not assigned)":
                        selected_user = ''
                
                # Store the selected user in a temporary variable, don't auto-update
                temp_user_key = f"temp_user_{idx}"
                if temp_user_key not in st.session_state:
                    st.session_state[temp_user_key] = selected_user
                elif st.session_state[temp_user_key] != selected_user:
                    st.session_state[temp_user_key] = selected_user
                
                # Date - handle NaT values properly
                try:
                    current_date = pd.to_datetime(job.get('date_start'))
                    if pd.isna(current_date):
                        current_date = pd.Timestamp.now()
                except:
                    current_date = pd.Timestamp.now()
                
                selected_date = st.date_input(
                    "Start Date",
                    value=current_date.date(),
                    key=f"date_{idx}"
                )
                st.session_state.edited_jobs[idx]['date_start'] = selected_date.strftime('%Y-%m-%d')
                
                # Recurrence type
                recurrence_options = ["none", "daily", "weekly", "biweekly", "monthly"]
                current_recurrence = job.get('recurrence_type', 'none')
                
                # Handle unexpected recurrence types by defaulting to 'none'
                if current_recurrence not in recurrence_options:
                    current_recurrence = 'none'
                
                recurrence_type = st.selectbox(
                    "Recurrence Type",
                    options=recurrence_options,
                    index=recurrence_options.index(current_recurrence),
                    key=f"recurrence_{idx}"
                )
                st.session_state.edited_jobs[idx]['recurrence_type'] = recurrence_type
                
                # Recurrence end date
                try:
                    rec_end_date = pd.to_datetime(job.get('recurrence_end_date'))
                    if pd.isna(rec_end_date):
                        rec_end_date = current_date + pd.Timedelta(days=30)
                except:
                    rec_end_date = current_date + pd.Timedelta(days=30)
                
                if recurrence_type != "none":
                    selected_end_date = st.date_input(
                        "Recurrence End Date",
                        value=rec_end_date.date(),
                        key=f"rec_end_{idx}"
                    )
                    st.session_state.edited_jobs[idx]['recurrence_end_date'] = selected_end_date.strftime('%Y-%m-%d')
                
                # Form selection dropdown
                form_names = [form.get('name', '') for form in st.session_state.get('forms', []) if form.get('name')]
                
                if form_names:
                    current_form = job.get('form_name', '')
                    form_options = ["(Not assigned)"] + form_names
                    
                    # Determine default index
                    if not current_form or current_form == '':
                        default_form_index = 0  # "(Not assigned)"
                    elif current_form in form_names:
                        default_form_index = form_options.index(current_form)
                    else:
                        # Current form not in list, add it
                        form_options.insert(1, current_form)
                        default_form_index = 1
                    
                    selected_form = st.selectbox(
                        "Form (Optional)",
                        options=form_options,
                        index=default_form_index,
                        key=f"form_{idx}"
                    )
                    
                    # Convert "(Not assigned)" back to empty string
                    if selected_form == "(Not assigned)":
                        selected_form = ''
                    
                    st.session_state.edited_jobs[idx]['form_name'] = selected_form
                else:
                    st.info("No forms available")
            
            # Validate & Save button and Delete job button
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button(f"✅ Validate & Save", key=f"validate_{idx}", type="primary", use_container_width=True):
                    # Update the job with all the form values
                    st.session_state.edited_jobs[idx]['assigned_to'] = st.session_state.get(f"temp_user_{idx}", '')
                    
                    # Re-validate this specific job
                    job_errors = validate_job_row(st.session_state.edited_jobs[idx], sites, floors, spaces, users, debug_mode, forms)
                    st.session_state.edited_jobs[idx]['_validation_errors'] = job_errors
                    
                    # Just show success/error and force a minimal rerun to update counts
                    if not job_errors:
                        st.success(f"✅ Job {idx+1} validated successfully!", key=f"success_{idx}")
                    else:
                        st.error(f"❌ Job {idx+1} has errors:", key=f"error_{idx}")
                        for error in job_errors:
                            st.write(f"• {error}")
                    
                    # Force re-calculation of counts
                    st.session_state.force_validate = True
                    st.rerun()
            
            with col_btn2:
                if st.button(f"🗑️ Delete Job", key=f"delete_{idx}", type="secondary", use_container_width=True):
                    st.session_state.edited_jobs.pop(idx)
                    st.rerun()
    
    st.markdown("---")
    
    # Proceed to import button
    if st.button("➡️ Proceed to Import", use_container_width=True, type="primary"):
        if invalid_count > 0:
            st.warning(f"⚠️ Please fix {invalid_count} invalid jobs before importing.")
        else:
            st.session_state.current_step = 4
            st.rerun()

def render_step_4(enable_import, debug_mode):
    """Step 4: Import Jobs"""
    st.markdown("""
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
    
    if "edited_jobs" not in st.session_state or not st.session_state.edited_jobs:
        st.info("Please complete the previous steps first.")
        return
    
    jobs = st.session_state.edited_jobs
    
    st.subheader("Ready to Import")
    st.write(f"**{len(jobs)} jobs** ready for import")
    
    # Debug information
    if debug_mode:
        st.write(f"🔍 DEBUG: enable_import = {enable_import}")
        st.write(f"🔍 DEBUG: enable_import type = {type(enable_import)}")
        st.write(f"🔍 DEBUG: session_state enable_import = {st.session_state.get('enable_import', 'NOT_SET')}")
    
    if enable_import:
        st.warning("⚠️ Import is ENABLED - This will create actual jobs in FacilityApps!")
        
        if st.button("🚀 Import All Jobs", use_container_width=True, type="primary"):
            # Initialize the client
            fa_domain = st.session_state.get('config_fa_domain', 'demouk.facilityapps.com')
            fa_token = st.session_state.get('config_fa_token', '')
            client = FacilityAppsClient(fa_domain, fa_token)
            
            # Get reference data for ID lookups
            sites = st.session_state.get('sites', [])
            floors = st.session_state.get('floors', [])
            spaces = st.session_state.get('spaces', [])
            users = st.session_state.get('users', [])
            forms = st.session_state.get('forms', [])
            
            import_results = []
            success_count = 0
            failure_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, job in enumerate(jobs):
                status_text.text(f"Importing job {idx+1} of {len(jobs)}: {job.get('title_en', 'Untitled')}...")
                
                # Build proper API payload
                job_payload, build_error = build_job_payload(job, sites, floors, spaces, users, forms)
                
                # Save payload regardless of success/failure
                if job_payload:
                    payload_file = save_import_payload(job, job_payload, "attempted", build_error)
                    if payload_file and debug_mode:
                        st.write(f"🔍 DEBUG: Payload saved to {payload_file}")
                
                if build_error:
                    # Payload build failed
                    success = False
                    message = f"Payload build error: {build_error}"
                    response = None
                else:
                    # Send to API
                    success, message, response = client.create_job(job_payload)
                    
                    # Update payload with final status
                    if job_payload:
                        final_status = "success" if success else "failed"
                        final_error = message if not success else None
                        save_import_payload(job, job_payload, final_status, final_error)
                
                import_results.append({
                    "job_number": idx + 1,
                    "title": job.get('title_en', 'Untitled'),
                    "status": "✅ Success" if success else "❌ Failed",
                    "message": message,
                    "response": response,
                    "payload": job_payload if debug_mode else None
                })
                
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                
                progress_bar.progress((idx + 1) / len(jobs))
            
            status_text.empty()
            progress_bar.empty()
            
            # Display results
            st.markdown("---")
            st.subheader("Import Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Jobs", len(jobs))
            with col2:
                st.metric("✅ Successful", success_count)
            with col3:
                st.metric("❌ Failed", failure_count)
            
            # Show detailed results
            st.markdown("### Detailed Results")
            for result in import_results:
                with st.expander(f"{result['status']} Job {result['job_number']}: {result['title']}", expanded=(result['status'] == "❌ Failed")):
                    st.write(f"**Status:** {result['status']}")
                    st.write(f"**Message:** {result['message']}")
                    if debug_mode and result.get('payload'):
                        st.write(f"**Payload Sent:**")
                        st.json(result['payload'])
                    if debug_mode and result['response']:
                        st.write(f"**API Response:**")
                        st.json(result['response'])
            
            # Create downloadable CSV log
            import pandas as pd
            from datetime import datetime
            
            results_df = pd.DataFrame([{
                "Job Number": r['job_number'],
                "Title": r['title'],
                "Status": r['status'],
                "Message": r['message']
            } for r in import_results])
            
            csv = results_df.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.download_button(
                label="📥 Download Import Log",
                data=csv,
                file_name=f"import_log_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Show payload files
            st.markdown("---")
            st.subheader("💾 Saved Payloads")
            payloads_dir = "payloads"
            if os.path.exists(payloads_dir):
                payload_files = [f for f in os.listdir(payloads_dir) if f.endswith('.json')]
                if payload_files:
                    st.write(f"📁 {len(payload_files)} payload files saved to `{payloads_dir}/` directory")
                    
                    # Show recent payloads
                    recent_files = sorted(payload_files, reverse=True)[:5]  # Show last 5
                    st.write("**Recent payload files:**")
                    for file in recent_files:
                        file_path = os.path.join(payloads_dir, file)
                        file_size = os.path.getsize(file_path)
                        st.write(f"  - `{file}` ({file_size} bytes)")
                    
                    # Download all payloads as zip
                    if st.button("📦 Download All Payloads as ZIP"):
                        import zipfile
                        import io
                        
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for file in payload_files:
                                file_path = os.path.join(payloads_dir, file)
                                zip_file.write(file_path, file)
                        
                        zip_buffer.seek(0)
                        st.download_button(
                            label="⬇️ Download Payloads ZIP",
                            data=zip_buffer.getvalue(),
                            file_name=f"import_payloads_{timestamp}.zip",
                            mime="application/zip"
                        )
                else:
                    st.info("No payload files found.")
            else:
                st.info("Payloads directory not created yet.")
            
            if failure_count == 0:
                st.success(f"🎉 All {success_count} jobs imported successfully!")
            else:
                st.warning(f"⚠️ Import completed with {failure_count} failures. Please review the detailed results above.")
    else:
        st.info("🔒 Import is DISABLED - Enable 'Import' in the Settings tab to allow job creation.")
        st.button("🚀 Import All Jobs", use_container_width=True, disabled=True, help="Enable Import in Settings tab first")

def main():
    """Main application function"""
    # Set page config
    st.set_page_config(
        page_title="FacilityApps",
        page_icon=None,  # Remove favicon
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom theme
    apply_custom_theme()
    
    # Check authentication first
    if not check_password():
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
    
    # Load configuration from environment variables (Azure App Service)
    default_domain = os.getenv("FA_DOMAIN", "")
    default_token = os.getenv("FA_TOKEN", "")
    
    # Try to get from Streamlit secrets as fallback (for local development)
    try:
        if not default_domain:
            default_domain = st.secrets.get("production", {}).get("FA_DOMAIN", "")
        if not default_token:
            default_token = st.secrets.get("production", {}).get("FA_TOKEN", "")
    except:
        pass
    
    # ===== MAIN LAYOUT WITH TABS =====
    
    # Create tabs for main content
    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "⚙️ Settings", "📊 Reference Data"])
    
    with tab1:
        # Dashboard content - Step-by-step wizard
        st.markdown("## 📋 FacilityApps Bulk Job Importer")
        st.markdown("**Production Version** – Validate and import recurring jobs/rosters")
        
        # Initialize current step
        if "current_step" not in st.session_state:
            st.session_state.current_step = 1
        
        # Step progress indicator with dynamic highlighting
        current = st.session_state.current_step
        
        step1_bg = "#030213" if current == 1 else "#e5e5e5"
        step1_color = "white" if current == 1 else "#717182"
        step1_title_color = "#030213" if current == 1 else "#717182"
        step1_font_weight = "600" if current == 1 else "500"
        
        step2_bg = "#030213" if current == 2 else "#e5e5e5"
        step2_color = "white" if current == 2 else "#717182"
        step2_title_color = "#030213" if current == 2 else "#717182"
        step2_font_weight = "600" if current == 2 else "500"
        
        step3_bg = "#030213" if current == 3 else "#e5e5e5"
        step3_color = "white" if current == 3 else "#717182"
        step3_title_color = "#030213" if current == 3 else "#717182"
        step3_font_weight = "600" if current == 3 else "500"
        
        step4_bg = "#030213" if current == 4 else "#e5e5e5"
        step4_color = "white" if current == 4 else "#717182"
        step4_title_color = "#030213" if current == 4 else "#717182"
        step4_font_weight = "600" if current == 4 else "500"
        
        st.markdown(f"""
        <div style='margin-bottom: 2rem;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: {step1_bg}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: {step1_color}; font-weight: 600;'>1</div>
                    <div>
                        <div style='font-weight: {step1_font_weight}; color: {step1_title_color};'>Load Reference Data</div>
                        <div style='font-size: 12px; color: #717182;'>Connect to API</div>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: {step2_bg}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: {step2_color}; font-weight: 600;'>2</div>
                    <div>
                        <div style='font-weight: {step2_font_weight}; color: {step2_title_color};'>Upload & Validate</div>
                        <div style='font-size: 12px; color: #717182;'>Import CSV file</div>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: {step3_bg}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: {step3_color}; font-weight: 600;'>3</div>
                    <div>
                        <div style='font-weight: {step3_font_weight}; color: {step3_title_color};'>Review & Edit</div>
                        <div style='font-size: 12px; color: #717182;'>Configure jobs</div>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 40px; height: 40px; background: {step4_bg}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: {step4_color}; font-weight: 600;'>4</div>
                    <div>
                        <div style='font-weight: {step4_font_weight}; color: {step4_title_color};'>Import Jobs</div>
                        <div style='font-size: 12px; color: #717182;'>Execute import</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Step content based on current step
        if st.session_state.current_step == 1:
            # Use stored credentials from Settings tab, fallback to defaults
            fa_domain = st.session_state.get('config_fa_domain', default_domain)
            fa_token = st.session_state.get('config_fa_token', default_token)
            render_step_1(fa_domain, fa_token, False)
        elif st.session_state.current_step == 2:
            render_step_2(st.session_state.get('debug_mode', False))
        elif st.session_state.current_step == 3:
            render_step_3(st.session_state.get('debug_mode', False))
        elif st.session_state.current_step == 4:
            render_step_4(st.session_state.get('enable_import', False), st.session_state.get('debug_mode', False))
        
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
            
            # Initialize session state for API credentials
            if 'config_fa_domain' not in st.session_state:
                st.session_state.config_fa_domain = default_domain
            if 'config_fa_token' not in st.session_state:
                st.session_state.config_fa_token = default_token
            
            # Display configuration from environment variables (read-only)
            st.info("🔒 Configuration is managed via environment variables and cannot be changed here.")
            
            fa_domain = st.text_input(
                "FA Domain",
                value=default_domain,
                placeholder="example.facilityapps.com",
                help="Configured via environment variable FA_DOMAIN",
                key="settings_domain",
                disabled=True
            )
            
            fa_token = st.text_input(
                "API Token",
                value="••••••••••••••••" if default_token else "",
                placeholder="Configured via environment variable FA_TOKEN",
                help="Configured via environment variable FA_TOKEN (hidden for security)",
                key="settings_token",
                disabled=True
            )
            
            # Show customer ID if available
            customer_id = os.getenv("CUSTOMER_ID", "Not configured")
            st.info(f"**Customer ID:** {customer_id}")
            
            # Use environment variables for the actual connection
            st.session_state.config_fa_domain = default_domain
            st.session_state.config_fa_token = default_token
            
            if st.button("🔗 Test Connection", use_container_width=True):
                if not default_domain or not default_token:
                    st.error("FA_DOMAIN and FA_TOKEN environment variables not configured")
                else:
                    with st.spinner("Testing connection..."):
                        client = FacilityAppsClient(default_domain, default_token)
                        success, message = client.test_connection()
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        with col2:
            st.markdown("### Application Options")
            
            enable_import = st.toggle(
                "🚀 Enable Import", 
                value=st.session_state.get('enable_import', False), 
                help="Allow the application to create jobs in FacilityApps"
            )
            
            # Update session state and rerun if changed
            if enable_import != st.session_state.get('enable_import', False):
                st.session_state.enable_import = enable_import
                st.success(f"✅ Import {'enabled' if enable_import else 'disabled'} - Page will refresh...")
                st.rerun()
            else:
                st.session_state.enable_import = enable_import
            
            if enable_import:
                st.warning("⚠️ Writes enabled! This will create actual jobs in FacilityApps.", icon="⚠️")
            
            debug_mode = st.toggle(
                "🐛 Debug Mode", 
                value=st.session_state.get('debug_mode', False),
                help="Show additional debugging information"
            )
            
            # Update session state and rerun if changed
            if debug_mode != st.session_state.get('debug_mode', False):
                st.session_state.debug_mode = debug_mode
                st.rerun()
            else:
                st.session_state.debug_mode = debug_mode
            
            st.markdown("### User Session")
            if "logged_in_user" in st.session_state:
                st.info(f"Logged in as: **{st.session_state['logged_in_user']}**")
            
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    with tab3:
        # Reference Data tab
        st.markdown("## 📊 Reference Data")
        
        if st.session_state.lookups_loaded:
            # Card-based metrics including forms
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Sites", st.session_state.get("sites_count", 0))
            with col2:
                st.metric("Floors", st.session_state.get("floors_count", 0))
            with col3:
                st.metric("Spaces", st.session_state.get("spaces_count", 0))
            with col4:
                st.metric("Users", st.session_state.get("users_count", 0))
            with col5:
                st.metric("Forms", len(st.session_state.get("forms", [])))
            
            st.markdown("---")
            
            # Sites, Floors, and Spaces in one section
            st.markdown("### Sites, Floors & Spaces")
            
            if st.session_state.get('sites'):
                # Create a combined dataframe for sites, floors, and spaces
                sites_df = pd.DataFrame(st.session_state.sites)
                floors_df = pd.DataFrame(st.session_state.floors)
                spaces_df = pd.DataFrame(st.session_state.spaces)
                
                # Combine all into one dataframe
                combined_data = []
                
                # Add sites
                for site in st.session_state.sites:
                    combined_data.append({
                        'ID': site.get('id', ''),
                        'Name': site.get('name', ''),
                        'Type': 'Site'
                    })
                
                # Add floors
                for floor in st.session_state.floors:
                    combined_data.append({
                        'ID': floor.get('id', ''),
                        'Name': floor.get('name', ''),
                        'Type': 'Floor'
                    })
                
                # Add spaces
                for space in st.session_state.spaces:
                    combined_data.append({
                        'ID': space.get('id', ''),
                        'Name': space.get('name', ''),
                        'Type': 'Space'
                    })
                
                combined_df = pd.DataFrame(combined_data)
                
                if not combined_df.empty:
                    st.dataframe(combined_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No sites, floors, or spaces found")
            
            st.markdown("---")
            
            # Users in separate section
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### Users")
            with col2:
                st.markdown("### &nbsp;")  # Spacing
                if st.session_state.get('users'):
                    csv = pd.DataFrame(st.session_state.users).to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="users.csv",
                        mime="text/csv",
                        key="download_users"
                    )
            
            if st.session_state.get('users'):
                users_df = pd.DataFrame(st.session_state.users)
                if not users_df.empty:
                    # Show user name and email if available
                    display_cols = []
                    if 'user_name' in users_df.columns:
                        display_cols.append('user_name')
                    if 'email' in users_df.columns:
                        display_cols.append('email')
                    if 'name' in users_df.columns and 'name' not in display_cols:
                        display_cols.append('name')
                    if display_cols:
                        st.dataframe(users_df[display_cols], use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(users_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No users found")
            
            st.markdown("---")
            
            # Forms in separate section
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### Forms")
            with col2:
                st.markdown("### &nbsp;")  # Spacing
                if st.session_state.get('forms'):
                    csv = pd.DataFrame(st.session_state.forms).to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="forms.csv",
                        mime="text/csv",
                        key="download_forms"
                    )
            
            if st.session_state.get('forms'):
                forms_df = pd.DataFrame(st.session_state.forms)
                if not forms_df.empty:
                    # Show form name and type if available
                    display_cols = []
                    if 'name' in forms_df.columns:
                        display_cols.append('name')
                    if 'type' in forms_df.columns:
                        display_cols.append('type')
                    if display_cols:
                        st.dataframe(forms_df[display_cols], use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(forms_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No forms found")
        else:
            st.info("No reference data loaded yet. Configure your API settings and load data from the Dashboard.")
    

    
    # ===== SIDEBAR (Minimal) =====
    with st.sidebar:
        # Header with branding
        st.image("FA logo.jpg", use_container_width=True)
        st.markdown("""
        <div style='padding: 0 0 1.5rem 0; text-align: center;'>
            <div style='font-size: 14px; color: #717182; margin-top: 0.5rem;'>Bulk Job Importer</div>
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
            # Clear cached data and reload
            if 'sites' in st.session_state:
                del st.session_state['sites']
            if 'floors' in st.session_state:
                del st.session_state['floors']
            if 'spaces' in st.session_state:
                del st.session_state['spaces']
            if 'users' in st.session_state:
                del st.session_state['users']
            st.success("Data refreshed! Reloading...")
            st.rerun()
        
        if st.button("📥 Download Template", use_container_width=True):
            # This would download the CSV template
            st.info("Template download feature coming soon!")

if __name__ == "__main__":
    main()
