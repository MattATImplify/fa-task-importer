"""
FacilityApps Bulk Job Importer - MVP
Local-first Streamlit app for validating and importing one-off jobs/rosters
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Authentication with username and password
def check_password():
    """Returns `True` if the user had valid credentials."""
    
    def credentials_entered():
        """Checks whether credentials entered by the user are correct."""
        try:
            if "auth" in st.secrets and "master_username" in st.secrets["auth"] and "master_password" in st.secrets["auth"]:
                username = st.session_state.get("username", "")
                password = st.session_state.get("password", "")
                
                if (username == st.secrets["auth"]["master_username"] and 
                    password == st.secrets["auth"]["master_password"]):
                    st.session_state["password_correct"] = True
                    st.session_state["logged_in_user"] = username
                    # Don't store credentials
                    del st.session_state["username"]
                    del st.session_state["password"]
                else:
                    st.session_state["password_correct"] = False
            else:
                st.session_state["password_correct"] = False
                st.session_state["auth_error"] = "Authentication not configured in secrets.toml"
        except Exception as e:
            st.session_state["password_correct"] = False
            st.session_state["auth_error"] = f"Auth error: {str(e)}"

    # Return True if the user is authenticated.
    if st.session_state.get("password_correct", False):
        return True

    # Show login form
    st.markdown("## 🔐 Authentication Required")
    st.markdown("### FA Job Importer - Admin Login")
    
    # Check if secrets are available
    if "auth_error" in st.session_state:
        st.error(st.session_state["auth_error"])
        return False
    
    try:
        if "auth" not in st.secrets or "master_username" not in st.secrets["auth"] or "master_password" not in st.secrets["auth"]:
            st.error("❌ Authentication not configured. Please add [auth] master_username and master_password to .streamlit/secrets.toml")
            st.code("""
[auth]
master_username = "admin"
master_password = "your_secure_password"
            """)
            return False
    except Exception as e:
        st.error(f"❌ Error reading secrets: {str(e)}")
        return False
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "Username", 
            key="username",
            placeholder="Enter your username"
        )
        st.text_input(
            "Password", 
            type="password", 
            key="password",
            placeholder="Enter your password"
        )
        
        if st.button("🔓 Login", use_container_width=True):
            credentials_entered()
            st.rerun()
    
    if st.session_state.get("password_correct") == False:
        st.error("😕 Invalid username or password")
    
    return False

# Setup logging
def setup_logging():
    """Setup logging for API payloads"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"api_payloads_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file

# Constants
TIMEZONE = pytz.timezone("Europe/London")
MAX_RETRIES = 3
BASE_DELAY = 1.0
FAILURE_THRESHOLD = 0.1  # Abort import if >10% failures


class FacilityAppsClient:
    """Client for interacting with FacilityApps API"""
    
    def __init__(self, domain: str, token: str):
        self.domain = domain
        self.token = token
        self.base_url = f"https://{domain}"
        self.headers = {
            "Authorization": f"Bearer {self._redact_token(token, reveal=True)}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def _redact_token(token: str, reveal: bool = False) -> str:
        """Redact token for logging (show first/last 4 chars only)"""
        if reveal:
            return token
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connectivity"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/planning/sites",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def get_sites(self) -> List[Dict]:
        """Fetch all sites"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/planning/sites",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try common patterns: {"data": [...]} or {"sites": [...]}
                if "data" in data:
                    return data["data"]
                elif "sites" in data:
                    return data["sites"]
                else:
                    st.warning(f"Unexpected sites response format with keys: {list(data.keys())}")
                    return []
            return []
        except Exception as e:
            st.error(f"Failed to fetch sites: {e}")
            return []
    
    def get_floors(self) -> List[Dict]:
        """Fetch all floors"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/planning/floors",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try common patterns: {"data": [...]} or {"floors": [...]}
                if "data" in data:
                    return data["data"]
                elif "floors" in data:
                    return data["floors"]
                else:
                    st.warning(f"Unexpected floors response format with keys: {list(data.keys())}")
                    return []
            return []
        except Exception as e:
            st.error(f"Failed to fetch floors: {e}")
            return []
    
    def get_spaces(self) -> List[Dict]:
        """Fetch all spaces"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/planning/spaces",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try common patterns: {"data": [...]} or {"spaces": [...]}
                if "data" in data:
                    return data["data"]
                elif "spaces" in data:
                    return data["spaces"]
                else:
                    st.warning(f"Unexpected spaces response format with keys: {list(data.keys())}")
                    return []
            return []
        except Exception as e:
            st.error(f"Failed to fetch spaces: {e}")
            return []
    
    def get_users(self) -> List[Dict]:
        """Fetch all users with pagination"""
        all_users = []
        page = 1
        limit = 200
        
        try:
            while True:
                response = requests.get(
                    f"{self.base_url}/api/v1/user",
                    headers=self.headers,
                    params={"limit": limit, "page": page},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                users = data.get("data", [])
                all_users.extend(users)
                
                meta = data.get("meta", {})
                pagination = meta.get("pagination", {})
                total_pages = pagination.get("total_pages", 1)
                
                if page >= total_pages:
                    break
                page += 1
                
            return all_users
        except Exception as e:
            st.error(f"Failed to fetch users: {e}")
            return []
    
    def create_job(self, payload: Dict) -> Tuple[bool, Any]:
        """
        Create a one-off job/roster
        Returns: (success, response_data_or_error)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/1.0/planning/save/true",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Respect rate limiting
            if "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
                if remaining < 5:
                    time.sleep(2)  # Back off if close to limit
            
            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                return False, {
                    "status": response.status_code,
                    "body": response.text[:500]
                }
        except Exception as e:
            return False, {"error": str(e)}
    
    def create_job_with_retry(self, payload: Dict) -> Tuple[bool, Any]:
        """Create job with exponential backoff retry on 5xx errors"""
        for attempt in range(MAX_RETRIES):
            success, result = self.create_job(payload)
            
            if success:
                return True, result
            
            # Check if it's a 5xx error
            if isinstance(result, dict) and result.get("status", 0) >= 500:
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
            
            return False, result
        
        return False, {"error": "Max retries exceeded"}


class JobValidator:
    """Validates CSV rows against FacilityApps requirements"""
    
    def __init__(self, sites: List[Dict], floors: List[Dict], 
                 spaces: List[Dict], users: List[Dict]):
        # Ensure inputs are lists (handle None)
        sites = sites or []
        floors = floors or []
        spaces = spaces or []
        users = users or []
        
        # Build lookup dictionaries by ID (filter out None items, non-dicts, and items without IDs)
        self.sites = {
            str(s.get("id")): s 
            for s in sites 
            if isinstance(s, dict) and s.get("id") is not None
        }
        self.floors = {
            str(f.get("id")): f 
            for f in floors 
            if isinstance(f, dict) and f.get("id") is not None
        }
        self.spaces = {
            str(s.get("id")): s 
            for s in spaces 
            if isinstance(s, dict) and s.get("id") is not None
        }
        self.users = {
            str(u.get("id")): u 
            for u in users 
            if isinstance(u, dict) and u.get("id") is not None
        }
        
        # Build name-to-ID lookups (case-insensitive)
        self.site_name_to_id = {}
        for s in sites:
            if isinstance(s, dict) and s.get("id") is not None:
                # Try common name fields
                name = s.get("name") or s.get("site_name") or s.get("title")
                if name:
                    self.site_name_to_id[str(name).strip().lower()] = str(s.get("id"))
        
        self.floor_name_to_id = {}
        for f in floors:
            if isinstance(f, dict) and f.get("id") is not None:
                name = f.get("name") or f.get("floor_name") or f.get("title")
                if name:
                    # Include site context in key for disambiguation
                    site_id = str(f.get("site_id", f.get("location_id", "")))
                    key = f"{site_id}|{str(name).strip().lower()}"
                    self.floor_name_to_id[key] = str(f.get("id"))
                    # Also store without site context (less safe but more flexible)
                    self.floor_name_to_id[str(name).strip().lower()] = str(f.get("id"))
        
        self.space_name_to_id = {}
        for s in spaces:
            if isinstance(s, dict) and s.get("id") is not None:
                name = s.get("name") or s.get("space_name") or s.get("title")
                if name:
                    # Include floor context for disambiguation
                    floor_id = str(s.get("floor_id", ""))
                    key = f"{floor_id}|{str(name).strip().lower()}"
                    self.space_name_to_id[key] = str(s.get("id"))
                    # Also store without floor context
                    self.space_name_to_id[str(name).strip().lower()] = str(s.get("id"))
        
        self.user_name_to_id = {}
        for u in users:
            if isinstance(u, dict) and u.get("id") is not None:
                # Try various user name fields
                username = u.get("user_name") or u.get("username") or u.get("name")
                if username:
                    self.user_name_to_id[str(username).strip().lower()] = str(u.get("id"))
                # Also try email
                email = u.get("email")
                if email:
                    self.user_name_to_id[str(email).strip().lower()] = str(u.get("id"))
        
        # Build relationships
        self.floor_to_site = {
            str(f.get("id")): str(f.get("siteId") or f.get("site_id") or f.get("location_id"))
            for f in floors
            if isinstance(f, dict) and f.get("id") is not None and (f.get("siteId") is not None or f.get("site_id") is not None or f.get("location_id") is not None)
        }
        self.space_to_floor = {
            str(s.get("id")): str(s.get("floorId") or s.get("floor_id"))
            for s in spaces
            if isinstance(s, dict) and s.get("id") is not None and (s.get("floorId") is not None or s.get("floor_id") is not None)
        }
    
    def resolve_site(self, row: pd.Series) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve site ID from either site_id or site_name column
        Returns: (resolved_id, error_message)
        """
        site_id = row.get("site_id")
        site_name = row.get("site_name")
        
        # Prefer ID if provided
        if pd.notna(site_id) and str(site_id).strip() != "":
            return str(site_id).strip(), None
        
        # Try name lookup
        if pd.notna(site_name) and str(site_name).strip() != "":
            name_key = str(site_name).strip().lower()
            resolved_id = self.site_name_to_id.get(name_key)
            if resolved_id:
                return resolved_id, None
            else:
                # Try to suggest close matches
                available = list(self.site_name_to_id.keys())[:5]
                return None, f"Site name '{site_name}' not found. Available: {', '.join(available)}"
        
        return None, "Neither site_id nor site_name provided"
    
    def resolve_floor(self, row: pd.Series, site_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve floor ID from either floor_id or floor_name column
        Returns: (resolved_id, error_message)
        """
        floor_id = row.get("floor_id")
        floor_name = row.get("floor_name")
        
        # If neither provided, that's OK (floor is optional)
        if (pd.isna(floor_id) or str(floor_id).strip() == "") and \
           (pd.isna(floor_name) or str(floor_name).strip() == ""):
            return None, None
        
        # Prefer ID if provided
        if pd.notna(floor_id) and str(floor_id).strip() != "":
            return str(floor_id).strip(), None
        
        # Try name lookup with site context
        if pd.notna(floor_name) and str(floor_name).strip() != "":
            name = str(floor_name).strip().lower()
            # Try with site context first
            context_key = f"{site_id}|{name}"
            resolved_id = self.floor_name_to_id.get(context_key)
            if resolved_id:
                return resolved_id, None
            # Try without context
            resolved_id = self.floor_name_to_id.get(name)
            if resolved_id:
                return resolved_id, None
            else:
                return None, f"Floor name '{floor_name}' not found in site {site_id}"
        
        return None, None
    
    def resolve_space(self, row: pd.Series, floor_id: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve space ID from either space_id or space_name column
        Returns: (resolved_id, error_message)
        """
        space_id = row.get("space_id")
        space_name = row.get("space_name")
        
        # If neither provided, that's OK (space is optional)
        if (pd.isna(space_id) or str(space_id).strip() == "") and \
           (pd.isna(space_name) or str(space_name).strip() == ""):
            return None, None
        
        # Prefer ID if provided
        if pd.notna(space_id) and str(space_id).strip() != "":
            return str(space_id).strip(), None
        
        # Try name lookup with floor context
        if pd.notna(space_name) and str(space_name).strip() != "":
            name = str(space_name).strip().lower()
            if floor_id:
                # Try with floor context first
                context_key = f"{floor_id}|{name}"
                resolved_id = self.space_name_to_id.get(context_key)
                if resolved_id:
                    return resolved_id, None
            # Try without context
            resolved_id = self.space_name_to_id.get(name)
            if resolved_id:
                return resolved_id, None
            else:
                return None, f"Space name '{space_name}' not found"
        
        return None, None
    
    def resolve_owner(self, row: pd.Series) -> Tuple[Optional[str], Optional[str]]:
        """
        Resolve owner ID from either owner_employee_id or owner_name/owner_email
        Returns: (resolved_id, error_message)
        """
        owner_id = row.get("owner_employee_id")
        owner_name = row.get("owner_name")
        owner_email = row.get("owner_email")
        
        # Prefer ID if provided
        if pd.notna(owner_id) and str(owner_id).strip() != "":
            return str(owner_id).strip(), None
        
        # Try name lookup
        if pd.notna(owner_name) and str(owner_name).strip() != "":
            name_key = str(owner_name).strip().lower()
            resolved_id = self.user_name_to_id.get(name_key)
            if resolved_id:
                return resolved_id, None
        
        # Try email lookup
        if pd.notna(owner_email) and str(owner_email).strip() != "":
            email_key = str(owner_email).strip().lower()
            resolved_id = self.user_name_to_id.get(email_key)
            if resolved_id:
                return resolved_id, None
        
        return None, "Owner not found by ID, name, or email"
    
    def validate_row(self, row: pd.Series, row_num: int, 
                     seen_keys: set) -> List[Dict]:
        """
        Validate a single row and return list of issues
        Each issue: {row_number, status, issue_code, issue_detail, suggestion}
        """
        issues = []
        today = datetime.now(TIMEZONE).date()
        
        # Resolve site (required - either ID or name must be provided)
        site_id, site_error = self.resolve_site(row)
        if site_error:
            issues.append({
                "row_number": row_num,
                "status": "ERROR",
                "issue_code": "MISSING_SITE",
                "issue_detail": site_error,
                "suggestion": "Provide site_id or site_name"
            })
        else:
            # Store resolved ID back in row for later use
            row["_resolved_site_id"] = site_id
        
        # Resolve owner (required - either ID, name, or email)
        owner_id, owner_error = self.resolve_owner(row)
        if owner_error:
            issues.append({
                "row_number": row_num,
                "status": "ERROR",
                "issue_code": "MISSING_OWNER",
                "issue_detail": owner_error,
                "suggestion": "Provide owner_employee_id, owner_name, or owner_email"
            })
        else:
            # Store resolved ID back in row
            row["_resolved_owner_id"] = owner_id
        
        # Resolve floor (optional)
        floor_id = None
        if site_id:
            floor_id, floor_error = self.resolve_floor(row, site_id)
            if floor_error:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_FLOOR",
                    "issue_detail": floor_error,
                    "suggestion": "Check floor_id or floor_name"
                })
            elif floor_id:
                row["_resolved_floor_id"] = floor_id
        
        # Resolve space (optional)
        if floor_id:
            space_id, space_error = self.resolve_space(row, floor_id)
            if space_error:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_SPACE",
                    "issue_detail": space_error,
                    "suggestion": "Check space_id or space_name"
                })
            elif space_id:
                row["_resolved_space_id"] = space_id
        
        # Required field checks (non-location fields)
        required = ["title_en", "date_start", "date_end", "hour_start", 
                   "minute_start", "hour_end", "minute_end"]
        
        for field in required:
            if pd.isna(row.get(field)) or str(row.get(field, "")).strip() == "":
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "MISSING_REQUIRED",
                    "issue_detail": f"Missing required field: {field}",
                    "suggestion": f"Provide a value for {field}"
                })
        
        # If missing required fields, skip further validation
        if any(i["issue_code"] in ["MISSING_SITE", "MISSING_OWNER", "MISSING_REQUIRED"] for i in issues):
            return issues
        
        # Date validation
        try:
            date_start = pd.to_datetime(row["date_start"]).date()
            date_end = pd.to_datetime(row["date_end"]).date()
            
            if date_start < today:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "PAST_DATE",
                    "issue_detail": f"date_start {date_start} is in the past",
                    "suggestion": f"Use date >= {today}"
                })
            
            if date_end < date_start:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_DATE_RANGE",
                    "issue_detail": f"date_end {date_end} before date_start {date_start}",
                    "suggestion": "Set date_end >= date_start"
                })
        except Exception as e:
            issues.append({
                "row_number": row_num,
                "status": "ERROR",
                "issue_code": "INVALID_DATE",
                "issue_detail": f"Date parsing error: {e}",
                "suggestion": "Use YYYY-MM-DD format"
            })
        
        # Time validation
        try:
            hour_start = int(row["hour_start"])
            minute_start = int(row["minute_start"])
            hour_end = int(row["hour_end"])
            minute_end = int(row["minute_end"])
            
            if not (0 <= hour_start <= 23):
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_HOUR",
                    "issue_detail": f"hour_start {hour_start} out of range",
                    "suggestion": "Use 0-23"
                })
            
            if not (0 <= hour_end <= 23):
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_HOUR",
                    "issue_detail": f"hour_end {hour_end} out of range",
                    "suggestion": "Use 0-23"
                })
            
            if not (0 <= minute_start <= 59):
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_MINUTE",
                    "issue_detail": f"minute_start {minute_start} out of range",
                    "suggestion": "Use 0-59"
                })
            
            if not (0 <= minute_end <= 59):
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_MINUTE",
                    "issue_detail": f"minute_end {minute_end} out of range",
                    "suggestion": "Use 0-59"
                })
            
            # Check end time > start time
            start_minutes = hour_start * 60 + minute_start
            end_minutes = hour_end * 60 + minute_end
            
            if end_minutes <= start_minutes:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_TIME_RANGE",
                    "issue_detail": f"End time ({hour_end:02d}:{minute_end:02d}) must be after start ({hour_start:02d}:{minute_start:02d})",
                    "suggestion": "Set end_time > start_time"
                })
        except Exception as e:
            issues.append({
                "row_number": row_num,
                "status": "ERROR",
                "issue_code": "INVALID_TIME",
                "issue_detail": f"Time parsing error: {e}",
                "suggestion": "Use integer values for hours/minutes"
            })
        
        # Validate resolved site ID exists
        resolved_site_id = row.get("_resolved_site_id")
        if resolved_site_id and resolved_site_id not in self.sites:
            issues.append({
                "row_number": row_num,
                "status": "ERROR",
                "issue_code": "INVALID_SITE",
                "issue_detail": f"Resolved site_id {resolved_site_id} not found in system",
                "suggestion": "Check site reference"
            })
        
        # Validate resolved floor belongs to site (if both present)
        resolved_floor_id = row.get("_resolved_floor_id")
        if resolved_floor_id and resolved_site_id:
            if resolved_floor_id not in self.floors:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_FLOOR",
                    "issue_detail": f"Resolved floor_id {resolved_floor_id} not found",
                    "suggestion": "Check floor reference"
                })
            else:
                # Check floor belongs to site
                expected_site = self.floor_to_site.get(resolved_floor_id)
                if expected_site != resolved_site_id:
                    issues.append({
                        "row_number": row_num,
                        "status": "ERROR",
                        "issue_code": "FLOOR_SITE_MISMATCH",
                        "issue_detail": f"Floor does not belong to specified site",
                        "suggestion": f"Floor belongs to site {expected_site}"
                    })
        
        # Validate resolved space belongs to floor (if both present)
        resolved_space_id = row.get("_resolved_space_id")
        if resolved_space_id:
            if not resolved_floor_id:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "SPACE_WITHOUT_FLOOR",
                    "issue_detail": "Space provided without floor",
                    "suggestion": "Provide floor when specifying space"
                })
            elif resolved_space_id not in self.spaces:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_SPACE",
                    "issue_detail": f"Resolved space_id {resolved_space_id} not found",
                    "suggestion": "Check space reference"
                })
            else:
                # Check space belongs to floor
                expected_floor = self.space_to_floor.get(resolved_space_id)
                if expected_floor != resolved_floor_id:
                    issues.append({
                        "row_number": row_num,
                        "status": "ERROR",
                        "issue_code": "SPACE_FLOOR_MISMATCH",
                        "issue_detail": f"Space does not belong to specified floor",
                        "suggestion": f"Space belongs to floor {expected_floor}"
                    })
        
        # Validate resolved owner ID exists
        resolved_owner_id = row.get("_resolved_owner_id")
        if resolved_owner_id and resolved_owner_id not in self.users:
            issues.append({
                "row_number": row_num,
                "status": "ERROR",
                "issue_code": "INVALID_OWNER",
                "issue_detail": f"Resolved owner_id {resolved_owner_id} not found in system",
                "suggestion": "Check owner reference"
            })
        
        # Label validation - disabled for now
        # label_list = row.get("label_list", "")
        # if pd.notna(label_list) and str(label_list).strip() != "":
        #     labels = [l.strip() for l in str(label_list).split(",")]
        #     labels = [l for l in labels if l]  # Remove empty
        #     if len(labels) != len(set(labels)):
        #         issues.append({
        #             "row_number": row_num,
        #             "status": "WARN",
        #             "issue_code": "DUPLICATE_LABELS",
        #             "issue_detail": "Duplicate labels found",
        #             "suggestion": "Remove duplicate labels"
        #         })
        
        # Duplicate check (use resolved IDs)
        dup_key = (
            row.get("_resolved_site_id", ""),
            row.get("_resolved_floor_id", ""),
            row.get("_resolved_space_id", ""),
            str(row.get("title_en", "")).strip(),
            str(row.get("date_start", "")).strip(),
            str(row.get("hour_start", "")).strip(),
            str(row.get("minute_start", "")).strip()
        )
        
        if dup_key in seen_keys:
            issues.append({
                "row_number": row_num,
                "status": "WARN",
                "issue_code": "DUPLICATE_ROW",
                "issue_detail": "Duplicate job found in file (same site/floor/space/title/date/time)",
                "suggestion": "Review if intentional"
            })
        else:
            seen_keys.add(dup_key)
        
        # Recurrence validation
        recurrence_type = str(row.get("recurrence_type", "none")).strip().lower()
        if recurrence_type and recurrence_type not in ["", "none"]:
            # Validate recurrence type
            valid_types = ["daily", "weekdays", "weekly", "biweekly", "monthly"]
            if recurrence_type not in valid_types:
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "INVALID_RECURRENCE_TYPE",
                    "issue_detail": f"recurrence_type '{recurrence_type}' is invalid",
                    "suggestion": f"Use one of: {', '.join(valid_types)}, or leave empty for one-off"
                })
            
            # Validate recurrence end date is provided
            recurrence_end_date = row.get("recurrence_end_date")
            if pd.isna(recurrence_end_date) or str(recurrence_end_date).strip() == "":
                issues.append({
                    "row_number": row_num,
                    "status": "ERROR",
                    "issue_code": "MISSING_RECURRENCE_END",
                    "issue_detail": "recurrence_end_date required for recurring jobs",
                    "suggestion": "Provide end date (YYYY-MM-DD) or set recurrence_type to 'none'"
                })
            else:
                # Validate end date is after start date
                try:
                    rec_end = pd.to_datetime(recurrence_end_date).date()
                    start = pd.to_datetime(row["date_start"]).date()
                    if rec_end <= start:
                        issues.append({
                            "row_number": row_num,
                            "status": "ERROR",
                            "issue_code": "INVALID_RECURRENCE_END",
                            "issue_detail": f"recurrence_end_date {rec_end} must be after date_start {start}",
                            "suggestion": "Set end date > start date"
                        })
                except Exception as e:
                    issues.append({
                        "row_number": row_num,
                        "status": "ERROR",
                        "issue_code": "INVALID_RECURRENCE_END_FORMAT",
                        "issue_detail": f"Invalid recurrence_end_date format: {e}",
                        "suggestion": "Use YYYY-MM-DD format"
                    })
            
            # Validate days for weekly/biweekly patterns
            if recurrence_type in ["weekly", "biweekly"]:
                recurrence_days = row.get("recurrence_days", "")
                if pd.notna(recurrence_days) and str(recurrence_days).strip() != "":
                    days = [d.strip().lower()[:3] for d in str(recurrence_days).split(",")]
                    valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                    invalid_days = [d for d in days if d not in valid_days]
                    if invalid_days:
                        issues.append({
                            "row_number": row_num,
                            "status": "ERROR",
                            "issue_code": "INVALID_RECURRENCE_DAYS",
                            "issue_detail": f"Invalid day(s): {', '.join(invalid_days)}",
                            "suggestion": "Use: Mon, Tue, Wed, Thu, Fri, Sat, Sun (comma-separated)"
                        })
            
            # Validate interval for custom intervals
            recurrence_interval = row.get("recurrence_interval")
            if pd.notna(recurrence_interval) and recurrence_interval != "":
                try:
                    interval = int(recurrence_interval)
                    if interval < 1:
                        issues.append({
                            "row_number": row_num,
                            "status": "ERROR",
                            "issue_code": "INVALID_RECURRENCE_INTERVAL",
                            "issue_detail": f"recurrence_interval {interval} must be >= 1",
                            "suggestion": "Use positive integer (1, 2, 3, etc.)"
                        })
                except ValueError:
                    issues.append({
                        "row_number": row_num,
                        "status": "ERROR",
                        "issue_code": "INVALID_RECURRENCE_INTERVAL_FORMAT",
                        "issue_detail": "recurrence_interval must be an integer",
                        "suggestion": "Use whole numbers (1, 2, 3, etc.)"
                    })
        
        # If no issues, mark as OK
        if not issues:
            issues.append({
                "row_number": row_num,
                "status": "OK",
                "issue_code": "VALID",
                "issue_detail": "Row is valid",
                "suggestion": ""
            })
        
        return issues


def build_recurrence_ui(row_idx: int, row: pd.Series) -> Dict:
    """Build recurrence UI and return recurrence settings"""
    
    # Initialize recurrence settings
    recurrence_settings = {
        "is_recurring": False,
        "repeat_interval_period": None,
        "repeat_interval_length": 1,
        "use_day_of_week": False,
        "frequency_daily_repeat": [],
        "frequency_weekly_repeat": [],
        "frequency_monthly_repeat": [],
        "frequency_stop_repeat": None,
        "frequency_stop_repeat_number_value": None,
        "end_after_date": None
    }
    
    st.write("**🔄 Recurrence Settings:**")
    
    # Step 1: Toggle recurrence
    is_recurring = st.checkbox(
        "Repeat this job",
        value=bool(row.get("is_recurring", False)),
        key=f"recurring_{row_idx}"
    )
    
    if not is_recurring:
        return recurrence_settings
    
    recurrence_settings["is_recurring"] = True
    
    # Step 2: Frequency and interval
    col1, col2 = st.columns([2, 1])
    
    with col1:
        frequency = st.selectbox(
            "Repeat every",
            options=["Daily", "Weekly", "Monthly", "Yearly"],
            index=0,
            key=f"frequency_{row_idx}"
        )
    
    with col2:
        interval = st.number_input(
            "Interval",
            min_value=1,
            max_value=999,
            value=int(row.get("recurrence_interval", 1)) if pd.notna(row.get("recurrence_interval", 1)) else 1,
            key=f"interval_{row_idx}"
        )
    
    # Map frequency to period
    period_map = {
        "Daily": "daily",
        "Weekly": "weekly", 
        "Monthly": "monthly",
        "Yearly": "yearly"
    }
    
    recurrence_settings["repeat_interval_period"] = period_map[frequency]
    recurrence_settings["repeat_interval_length"] = interval
    
    # Step 3: Pattern details
    if frequency == "Daily":
        st.write("**Repeat on:**")
        days = st.multiselect(
            "Days of week",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            key=f"daily_days_{row_idx}"
        )
        
        # Convert to numbers (1=Monday, 7=Sunday)
        day_map = {
            "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
            "Friday": 5, "Saturday": 6, "Sunday": 7
        }
        recurrence_settings["frequency_daily_repeat"] = [day_map[d] for d in days]
        
    elif frequency == "Weekly":
        st.write("**Repeat on:**")
        days = st.multiselect(
            "Days of week",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            default=["Monday"],
            key=f"weekly_days_{row_idx}"
        )
        
        day_map = {
            "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
            "Friday": 5, "Saturday": 6, "Sunday": 7
        }
        recurrence_settings["frequency_daily_repeat"] = [day_map[d] for d in days]
        # For weekly on specific days, use daily period
        recurrence_settings["repeat_interval_period"] = "daily"
        
    elif frequency == "Monthly":
        monthly_type = st.radio(
            "Monthly pattern",
            options=["On this date", "On this weekday"],
            key=f"monthly_type_{row_idx}"
        )
        
        if monthly_type == "On this weekday":
            recurrence_settings["use_day_of_week"] = True
            # For monthly weekday, we still use frequency_daily_repeat for the day
            day = st.selectbox(
                "Day of week",
                options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                key=f"monthly_weekday_{row_idx}"
            )
            day_map = {
                "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
                "Friday": 5, "Saturday": 6, "Sunday": 7
            }
            recurrence_settings["frequency_daily_repeat"] = [day_map[day]]
    
    # Step 4: End condition
    st.write("**Ends:**")
    end_type = st.radio(
        "End condition",
        options=["Never", "After N occurrences", "On date"],
        key=f"end_type_{row_idx}"
    )
    
    if end_type == "After N occurrences":
        recurrence_settings["frequency_stop_repeat"] = 1
        recurrence_settings["frequency_stop_repeat_number_value"] = st.number_input(
            "Number of occurrences",
            min_value=1,
            max_value=999,
            value=10,
            key=f"stop_count_{row_idx}"
        )
    elif end_type == "On date":
        recurrence_settings["frequency_stop_repeat"] = 2
        end_date_value = row.get("recurrence_end_date", "2025-12-31")
        if pd.notna(end_date_value) and str(end_date_value).strip():
            try:
                end_date_value = pd.to_datetime(end_date_value).date()
            except:
                end_date_value = pd.to_datetime("2025-12-31").date()
        else:
            end_date_value = pd.to_datetime("2025-12-31").date()
            
        recurrence_settings["end_after_date"] = st.date_input(
            "End date",
            value=end_date_value,
            key=f"stop_date_{row_idx}"
        )
    else:  # Never
        recurrence_settings["frequency_stop_repeat"] = 0
    
    # Natural language preview
    preview = build_recurrence_preview(recurrence_settings)
    st.info(f"📅 **Preview:** {preview}")
    
    return recurrence_settings


def create_recurring_jobs_template() -> bytes:
    """Create Excel template with recurring job examples"""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Recurring Jobs Template"
    
    # Define styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    example_fill = PatternFill(start_color="E7F3FF", end_color="E7F3FF", fill_type="solid")
    instruction_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Headers
    headers = [
        "title_en", "description_en", "site_name", "floor_name", "space_name", 
        "owner_email", "date_start", "date_end", "hour_start", "minute_start", 
        "hour_end", "minute_end",
        "is_recurring", "repeat_interval_period", "repeat_interval_length",
        "use_day_of_week", "frequency_daily_repeat", "frequency_weekly_repeat",
        "frequency_monthly_repeat", "frequency_stop_repeat", 
        "frequency_stop_repeat_number_value", "end_after_date"
    ]
    
    # Write headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
        cell.border = border
    
    # Example data
    examples = [
        # One-time job
        [
            "Office Clean - One-off", "Single occurrence cleaning", "Main Office", "Ground Floor", "Reception",
            "cleaner@company.com", "2025-01-15", "2025-01-15", "9", "0", "17", "0",
            "FALSE", "", "", "", "", "", "", "", "", "", ""
        ],
        # Daily job (weekdays only)
        [
            "Daily Office Clean", "Regular office cleaning", "Main Office", "Ground Floor", "Reception",
            "cleaner@company.com", "2025-01-15", "2025-12-31", "9", "0", "17", "0",
            "TRUE", "daily", "1", "FALSE", "1,2,3,4,5", "", "", "2", "", "2025-12-31"
        ],
        # Weekly job (Tuesdays and Thursdays)
        [
            "Weekly Deep Clean", "Thorough cleaning twice a week", "Main Office", "Ground Floor", "Reception",
            "cleaner@company.com", "2025-01-15", "2025-12-31", "9", "0", "17", "0",
            "TRUE", "daily", "1", "FALSE", "2,4", "", "", "2", "", "2025-12-31"
        ],
        # Bi-weekly job (every 2 weeks on Monday)
        [
            "Bi-weekly Maintenance", "Maintenance every 2 weeks", "Main Office", "Ground Floor", "Reception",
            "maintenance@company.com", "2025-01-15", "2025-12-31", "8", "0", "16", "0",
            "TRUE", "daily", "2", "FALSE", "1", "", "", "2", "", "2025-12-31"
        ],
        # Monthly job (same date each month)
        [
            "Monthly Equipment Check", "Monthly equipment inspection", "Main Office", "Ground Floor", "Reception",
            "maintenance@company.com", "2025-01-15", "2025-12-31", "10", "0", "15", "0",
            "TRUE", "monthly", "1", "FALSE", "", "", "", "2", "", "2025-12-31"
        ],
        # Monthly job (specific weekday - 2nd Tuesday)
        [
            "Monthly Team Meeting", "Monthly team meeting", "Main Office", "Ground Floor", "Conference Room",
            "manager@company.com", "2025-01-15", "2025-12-31", "14", "0", "15", "0",
            "TRUE", "monthly", "1", "TRUE", "2", "", "", "2", "", "2025-12-31"
        ],
        # Job with occurrence limit
        [
            "Training Session Series", "10-week training program", "Main Office", "Ground Floor", "Training Room",
            "trainer@company.com", "2025-01-15", "2025-12-31", "10", "0", "12", "0",
            "TRUE", "weekly", "1", "FALSE", "3", "", "", "1", "10", ""
        ]
    ]
    
    # Write examples
    for row_idx, example in enumerate(examples, 2):
        for col_idx, value in enumerate(example, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = border
            if row_idx == 2:  # First example row
                cell.fill = example_fill
    
    # Add instructions sheet
    ws2 = wb.create_sheet("Instructions")
    
    instructions = [
        ["RECURRING JOBS EXCEL TEMPLATE - INSTRUCTIONS"],
        [""],
        ["BASIC JOB FIELDS:"],
        ["• title_en: Job title in English"],
        ["• description_en: Job description in English"],
        ["• site_name: Name of the site (must match your FA system)"],
        ["• floor_name: Name of the floor (optional)"],
        ["• space_name: Name of the space/room (optional)"],
        ["• owner_email: Email of the person responsible"],
        ["• date_start: Start date (YYYY-MM-DD)"],
        ["• date_end: End date (YYYY-MM-DD)"],
        ["• hour_start/minute_start: Start time"],
        ["• hour_end/minute_end: End time"],
        [""],
        ["RECURRENCE FIELDS:"],
        ["• is_recurring: TRUE for recurring jobs, FALSE for one-time"],
        ["• repeat_interval_period: daily, weekly, monthly, yearly"],
        ["• repeat_interval_length: How often (1 = every, 2 = every 2nd, etc.)"],
        ["• use_day_of_week: TRUE for monthly weekday patterns"],
        ["• frequency_daily_repeat: Days of week (1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat, 7=Sun)"],
        ["• frequency_weekly_repeat: Week numbers (usually leave empty)"],
        ["• frequency_monthly_repeat: Month numbers (usually leave empty)"],
        ["• frequency_stop_repeat: 0=never, 1=after N times, 2=on date"],
        ["• frequency_stop_repeat_number_value: Number of occurrences (if stop_repeat=1)"],
        ["• end_after_date: End date (if stop_repeat=2)"],
        [""],
        ["EXAMPLES:"],
        ["• Daily weekdays: period='daily', daily_repeat='1,2,3,4,5'"],
        ["• Weekly Tues/Thu: period='daily', daily_repeat='2,4'"],
        ["• Bi-weekly Monday: period='daily', length=2, daily_repeat='1'"],
        ["• Monthly same date: period='monthly', use_day_of_week=FALSE"],
        ["• Monthly 2nd Tuesday: period='monthly', use_day_of_week=TRUE, daily_repeat='2'"],
        ["• Stop after 10 times: stop_repeat=1, stop_count=10"],
        ["• Stop on date: stop_repeat=2, end_after_date='2025-12-31'"],
        [""],
        ["TIPS:"],
        ["• Copy the examples and modify for your needs"],
        ["• Use the UI in the app for easier configuration"],
        ["• All dates should be in YYYY-MM-DD format"],
        ["• Times should be 24-hour format (9 for 9 AM, 17 for 5 PM)"],
        ["• Leave optional fields empty if not needed"]
    ]
    
    for row_idx, instruction in enumerate(instructions, 1):
        cell = ws2.cell(row=row_idx, column=1, value=instruction[0])
        if instruction[0].startswith("RECURRING JOBS") or instruction[0].startswith("BASIC") or instruction[0].startswith("RECURRENCE") or instruction[0].startswith("EXAMPLES") or instruction[0].startswith("TIPS"):
            cell.font = Font(bold=True)
            cell.fill = instruction_fill
        elif instruction[0].startswith("•"):
            cell.font = Font(size=10)
    
    # Auto-adjust column widths
    for ws in [wb.active, ws2]:
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def build_recurrence_preview(settings: Dict) -> str:
    """Build natural language preview of recurrence settings"""
    if not settings.get("is_recurring"):
        return "One-time job"
    
    period = settings.get("repeat_interval_period", "daily")
    interval = settings.get("repeat_interval_length", 1)
    
    # Build frequency description
    if period == "daily":
        days = settings.get("frequency_daily_repeat", [])
        if not days:
            freq_desc = f"every {interval} day{'s' if interval > 1 else ''}"
        else:
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_list = [day_names[d-1] for d in days if 1 <= d <= 7]
            # Check if this is a weekly pattern (specific days selected)
            if len(days) < 7:  # Not all days selected, so it's a weekly pattern
                if interval == 1:
                    freq_desc = f"weekly on {', '.join(day_list)}"
                else:
                    freq_desc = f"every {interval} weeks on {', '.join(day_list)}"
            else:  # All days selected, so it's truly daily
                freq_desc = f"every {interval} day{'s' if interval > 1 else ''} on {', '.join(day_list)}"
    elif period == "monthly":
        if settings.get("use_day_of_week"):
            days = settings.get("frequency_daily_repeat", [])
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_list = [day_names[d-1] for d in days if 1 <= d <= 7]
            freq_desc = f"every {interval} month{'s' if interval > 1 else ''} on {', '.join(day_list)}"
        else:
            freq_desc = f"every {interval} month{'s' if interval > 1 else ''} on the same date"
    else:  # yearly
        freq_desc = f"every {interval} year{'s' if interval > 1 else ''}"
    
    # Build end condition description
    stop_repeat = settings.get("frequency_stop_repeat", 0)
    if stop_repeat == 1:
        count = settings.get("frequency_stop_repeat_number_value", 0)
        end_desc = f", ending after {count} times"
    elif stop_repeat == 2:
        end_date = settings.get("end_after_date")
        if end_date:
            end_desc = f", ending on {end_date}"
        else:
            end_desc = ""
    else:
        end_desc = ""
    
    return f"Repeats {freq_desc}{end_desc}"


def build_job_payload(row: pd.Series) -> Dict:
    """Build JSON payload for FacilityApps job/roster API using resolved IDs"""
    
    # Parse labels - disabled for now as they're causing issues
    # label_list = row.get("label_list", "")
    labels = []
    # if pd.notna(label_list) and str(label_list).strip() != "":
    #     labels = [l.strip() for l in str(label_list).split(",")]
    #     labels = [l for l in labels if l]
    #     labels = list(dict.fromkeys(labels))  # Dedupe, preserve order
    
    # Create a fresh validator to resolve IDs from current data
    validator = JobValidator(
        st.session_state.sites,
        st.session_state.floors,
        st.session_state.spaces,
        st.session_state.users
    )
    
    # Resolve IDs using current row data
    site_id, _ = validator.resolve_site(row)
    floor_id, _ = validator.resolve_floor(row, site_id)
    space_id, _ = validator.resolve_space(row, floor_id)
    owner_id, _ = validator.resolve_owner(row)
    
    # Fallback to original columns if resolution failed
    if not site_id:
        site_id = str(row.get("site_id", "")).strip()
        if not site_id:  # Still empty after fallback
            site_id = None
    if not floor_id:
        floor_id = str(row.get("floor_id", "")).strip() or None
    if not space_id:
        space_id = str(row.get("space_id", "")).strip() or None
    if not owner_id:
        owner_id = str(row.get("owner_employee_id", "")).strip()
        if not owner_id:  # Still empty after fallback
            owner_id = None
    
    # Build floors_spaces - empty array by default, object with data only if floor/space exist
    floors_spaces = []
    if floor_id and space_id:
        # Only create the object structure if we have both floor and space
        floors_spaces = {floor_id: [space_id]}
    
    # Build description
    description = row.get("description_en", "")
    if pd.isna(description):
        description = ""
    
    # Get recurrence settings from UI (stored in dataframe)
    is_recurring = bool(row.get("is_recurring", False))
    repeat_interval_period = row.get("repeat_interval_period")
    repeat_interval_length = int(row.get("repeat_interval_length", 1))
    use_day_of_week = bool(row.get("use_day_of_week", False))
    frequency_daily_repeat = row.get("frequency_daily_repeat", [])
    frequency_weekly_repeat = row.get("frequency_weekly_repeat", [])
    frequency_monthly_repeat = row.get("frequency_monthly_repeat", [])
    frequency_stop_repeat = row.get("frequency_stop_repeat")
    frequency_stop_repeat_number_value = row.get("frequency_stop_repeat_number_value")
    end_after_date = row.get("end_after_date")
    
    # Convert end_after_date to string if it's a date object
    if end_after_date and hasattr(end_after_date, 'strftime'):
        end_after_date = end_after_date.strftime('%Y-%m-%d')
    
    # Use recurrence end date or same as start for one-off
    if is_recurring and end_after_date:
        date_end = str(end_after_date)
    else:
        date_end = str(row["date_end"])
    
    # Build owners array - just the user ID (no employeeToPosition unless we have a valid position ID)
    owners = []
    if owner_id and str(owner_id).strip():
        owners = [{"id": str(owner_id)}]
    
    # Build base payload
    payload = {
        "id": None,
        "sequence_date": str(row["date_start"]) if is_recurring else None,
        "editMode": "all",
        "mode": "roster",
        "translations": [
            {
                "id": "new-0",
                "regionCode": "en_EN",
                "text": str(row["title_en"])
            },
            {
                "id": "new-1",
                "regionCode": "nl_NL",
                "text": "Mijn titel"
            }
        ],
        "description_translations": [
            {
                "id": "new-0",
                "regionCode": "en_EN",
                "text": str(description)
            },
            {
                "id": "new-1",
                "regionCode": "nl_NL",
                "text": "Mijn omschrijving"
            }
        ],
        "date_start": str(row["date_start"]),
        "date_end": date_end,
        "hour_start": str(int(row["hour_start"])),
        "minute_start": str(int(row["minute_start"])),
        "hour_end": str(int(row["hour_end"])),
        "minute_end": str(int(row["minute_end"])),
        "locations": str(site_id) if site_id else "",
        "floors_spaces": floors_spaces,
        "contracts": [],
        "rate": None,
        "invoicable": False,
        "clock_hourtype_id": None,
        "duration_seconds": None,
        "owners": owners,
        "owner_roles": [],
        "approvers": [],
        "approver_roles": [],
        "watchers": [],
        "watcher_roles": [],
        "subtasks": [],
        "contractSubtask": None,
        "syncForms": False,
        "labels": labels,
        "instruction-documents": [],
        "remove-instruction-documents": [],
        "task_sampling_select": None,
        "subtask_sampling_select": None,
        "exception-mode": 0,
        "excludeExceptions": "1",
        "task_complete_emails": False if is_recurring else True,
        "task_canceled_emails": False if is_recurring else True,
        "save_as_concept": False,
        "task_form_submission_id": None,
        "task_form_submission_visible": False
    }
    
    # Add recurrence fields only if this is a recurring job
    if is_recurring:
        payload["repeat_interval_length"] = repeat_interval_length
        payload["use_day_of_week"] = use_day_of_week
        payload["frequency_daily_repeat"] = frequency_daily_repeat
        payload["frequency_weekly_repeat"] = frequency_weekly_repeat
        payload["frequency_monthly_repeat"] = frequency_monthly_repeat
        payload["frequency_stop_repeat"] = frequency_stop_repeat
        payload["repeat_interval_period"] = repeat_interval_period
        
        # Critical: only include the appropriate stop field
        if frequency_stop_repeat == 0:
            # Never ends - no additional fields needed
            pass
        elif frequency_stop_repeat == 1:
            # Stop after N times - include number_value, NOT end_after_date
            payload["frequency_stop_repeat_number_value"] = frequency_stop_repeat_number_value
        elif frequency_stop_repeat == 2:
            # Stop at date - include end_after_date, NOT number_value
            if end_after_date:
                payload["end_after_date"] = end_after_date
    else:
        # One-off job - set recurrence fields to null/empty arrays
        payload["repeat_interval_length"] = 1
        payload["use_day_of_week"] = False
        payload["frequency_daily_repeat"] = []
        payload["frequency_weekly_repeat"] = []
        payload["frequency_monthly_repeat"] = []
        payload["frequency_stop_repeat"] = None
        payload["frequency_stop_repeat_number_value"] = None
        payload["repeat_interval_period"] = None
    
    # Recurrence fields are already included in the main payload
    
    return payload


def export_run_outputs(df: pd.DataFrame, audit_df: pd.DataFrame, 
                      lookups: Dict, domain: str) -> Path:
    """
    Export audit report, validated CSV, and metadata to timestamped run folder
    Returns: Path to run directory
    """
    timestamp = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")
    run_dir = Path("./runs") / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Export audit report
    audit_df.to_csv(run_dir / "audit_report.csv", index=False)
    
    # Export validated ready rows (only rows with no errors)
    error_row_numbers = audit_df[audit_df["status"] == "ERROR"]["row_number"].unique()
    # Convert row_numbers (2,3,4...) back to DataFrame positions (0,1,2...)
    error_positions = [rn - 2 for rn in error_row_numbers]
    # Use iloc to filter by position
    all_positions = set(range(len(df)))
    ready_positions = list(all_positions - set(error_positions))
    ready_df = df.iloc[ready_positions]
    ready_df.to_csv(run_dir / "validated_ready.csv", index=False)
    
    # Export lookup cache
    with open(run_dir / "lookup_cache.json", "w") as f:
        json.dump(lookups, f, indent=2, default=str)
    
    # Export run summary
    summary = {
        "timestamp": timestamp,
        "domain": domain,
        "total_rows": len(df),
        "ready_rows": len(ready_df),
        "error_rows": len(error_row_numbers),
        "timezone": "Europe/London"
    }
    with open(run_dir / "run_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    return run_dir


def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="FA Job Importer",
        page_icon="📋",
        layout="wide"
    )
    
    # Check authentication
    if not check_password():
        st.stop()
    
    st.title("📋 FacilityApps Bulk Job Importer")
    st.markdown("**Production Version** – Validate and import recurring jobs/rosters")
    
    # Initialize session state
    if "lookups_loaded" not in st.session_state:
        st.session_state.lookups_loaded = False
    if "csv_data" not in st.session_state:
        st.session_state.csv_data = None
    if "audit_issues" not in st.session_state:
        st.session_state.audit_issues = None
    if "sites" not in st.session_state:
        st.session_state.sites = []
    if "floors" not in st.session_state:
        st.session_state.floors = []
    if "spaces" not in st.session_state:
        st.session_state.spaces = []
    if "users" not in st.session_state:
        st.session_state.users = []
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Show logged in user
        if "logged_in_user" in st.session_state:
            st.success(f"👤 Logged in as: **{st.session_state['logged_in_user']}**")
            if st.button("🚪 Logout"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.divider()
        
        # Load from env or allow override
        default_domain = os.getenv("FA_DOMAIN", "")
        default_token = os.getenv("FA_TOKEN", "")
        
        fa_domain = st.text_input(
            "FA Domain",
            value=default_domain,
            help="e.g., demouk.facilityapps.com"
        )
        
        fa_token = st.text_input(
            "Bearer Token",
            value=default_token,
            type="password",
            help="Your FacilityApps API token"
        )
        
        if st.button("🔍 Test Connectivity"):
            if not fa_domain or not fa_token:
                st.error("Please provide both domain and token")
            else:
                with st.spinner("Testing connection..."):
                    client = FacilityAppsClient(fa_domain, fa_token)
                    success, message = client.test_connection()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        st.divider()
        
        enable_import = st.toggle(
            "🚀 Enable Import",
            value=False,
            help="Enable actual write operations to FA"
        )
        
        if enable_import:
            st.warning("⚠️ Import is ENABLED – writes will occur!")
        
        debug_mode = st.toggle(
            "🐛 Debug Mode",
            value=False,
            help="Show detailed debugging information (payloads, lookups, validation details)"
        )
        
        st.divider()
        
        # Show lookup metrics
        if st.session_state.lookups_loaded:
            st.metric("Sites", st.session_state.get("sites_count", 0))
            st.metric("Floors", st.session_state.get("floors_count", 0))
            st.metric("Spaces", st.session_state.get("spaces_count", 0))
            st.metric("Users", st.session_state.get("users_count", 0))
    
    # ===== MAIN CONTENT =====
    
    # Section 1: Load Lookups
    st.header("1️⃣ Load Reference Data")
    
    if st.button("📥 Load Sites/Floors/Spaces/Users", type="primary"):
        if not fa_domain or not fa_token:
            st.error("Please configure domain and token in sidebar")
        else:
            with st.spinner("Fetching data from FacilityApps..."):
                client = FacilityAppsClient(fa_domain, fa_token)
                
                sites = client.get_sites()
                floors = client.get_floors()
                spaces = client.get_spaces()
                users = client.get_users()
                
                # Debug: Check data types
                if sites:
                    if isinstance(sites, dict):
                        st.warning(f"⚠️ Sites returned as dict with keys: {list(sites.keys())}")
                    elif isinstance(sites, list) and len(sites) > 0 and not isinstance(sites[0], dict):
                        st.warning(f"⚠️ Sites items are {type(sites[0])}, not dicts")
                
                if floors:
                    if isinstance(floors, dict):
                        st.warning(f"⚠️ Floors returned as dict with keys: {list(floors.keys())}")
                    elif isinstance(floors, list) and len(floors) > 0 and not isinstance(floors[0], dict):
                        st.warning(f"⚠️ Floors items are {type(floors[0])}, not dicts")
                
                if spaces:
                    if isinstance(spaces, dict):
                        st.warning(f"⚠️ Spaces returned as dict with keys: {list(spaces.keys())}")
                    elif isinstance(spaces, list) and len(spaces) > 0 and not isinstance(spaces[0], dict):
                        st.warning(f"⚠️ Spaces items are {type(spaces[0])}, not dicts")
                
                if users:
                    if isinstance(users, dict):
                        st.warning(f"⚠️ Users returned as dict with keys: {list(users.keys())}")
                    elif isinstance(users, list) and len(users) > 0 and not isinstance(users[0], dict):
                        st.warning(f"⚠️ Users items are {type(users[0])}, not dicts")
                
                st.session_state.client = client
                st.session_state.sites = sites
                st.session_state.floors = floors
                st.session_state.spaces = spaces
                st.session_state.users = users
                st.session_state.lookups_loaded = True
                st.session_state.sites_count = len(sites) if sites else 0
                st.session_state.floors_count = len(floors) if floors else 0
                st.session_state.spaces_count = len(spaces) if spaces else 0
                st.session_state.users_count = len(users) if users else 0
                
                st.success(f"✅ Loaded: {len(sites)} sites, {len(floors)} floors, {len(spaces)} spaces, {len(users)} users")
                
                # Show sample data for debugging (only in debug mode)
                if debug_mode:
                    with st.expander("🔍 Debug: View Sample Data"):
                        st.write("**Sites Response:**")
                        if isinstance(sites, list) and len(sites) > 0:
                            st.json(sites[0])
                        elif isinstance(sites, dict):
                            st.json(sites)
                        else:
                            st.write(f"Type: {type(sites)}, Value: {str(sites)[:200]}")
                        
                        st.write("**Floors Response:**")
                        if isinstance(floors, list) and len(floors) > 0:
                            st.json(floors[0])
                            st.write(f"**Available fields in floor object:** {list(floors[0].keys()) if isinstance(floors[0], dict) else 'Not a dict'}")
                        elif isinstance(floors, dict):
                            st.json(floors)
                        else:
                            st.write(f"Type: {type(floors)}, Value: {str(floors)[:200]}")
                        
                        st.write("**Spaces Response:**")
                        if isinstance(spaces, list) and len(spaces) > 0:
                            st.json(spaces[0])
                        elif isinstance(spaces, dict):
                            st.json(spaces)
                        else:
                            st.write(f"Type: {type(spaces)}, Value: {str(spaces)[:200]}")
                        
                        st.write("**Users Response:**")
                        if isinstance(users, list) and len(users) > 0:
                            st.json(users[0])
                        elif isinstance(users, dict):
                            st.json(users)
                        else:
                            st.write(f"Type: {type(users)}, Value: {str(users)[:200]}")
                
                st.rerun()
    
    if not st.session_state.lookups_loaded:
        st.info("👆 Click above to load reference data before uploading CSV")
        return
    
    # Section 1.5: Lookup Tables Reference
    st.header("📚 Available Sites, Floors & Spaces")
    st.info("Use these names in your CSV - no need for IDs!")
    
    # Build lookup tables with better field detection
    sites_list = []
    for site in st.session_state.sites:
        if isinstance(site, dict):
            # Try multiple possible field names for site ID and name
            site_id = site.get("id") or site.get("site_id") or site.get("location_id")
            site_name = site.get("name") or site.get("site_name") or site.get("title") or site.get("location_name")
            
            sites_list.append({
                "site_name": site_name if site_name else "N/A",
                "site_id": site_id if site_id else "N/A"
            })
    
    floors_list = []
    for floor in st.session_state.floors:
        if isinstance(floor, dict):
            # Try multiple field names
            floor_id = floor.get("id") or floor.get("floor_id")
            floor_name = floor.get("name") or floor.get("floor_name") or floor.get("title")
            site_id = (floor.get("siteId") or floor.get("site_id") or floor.get("location_id") or 
                      floor.get("parent_id") or floor.get("site") or floor.get("location") or 
                      floor.get("building_id") or floor.get("building") or floor.get("facility_id") or 
                      floor.get("facility"))
            
            # Debug: Show what fields are available and what we found (only in debug mode)
            if debug_mode and len(floors_list) == 0:  # Only show for first floor
                st.write(f"**Debug - Floor fields available:** {list(floor.keys())}")
                st.write(f"**Debug - Site ID found:** {site_id}")
                st.write(f"**Debug - Trying these site fields:** siteId={floor.get('siteId')}, site_id={floor.get('site_id')}, location_id={floor.get('location_id')}, parent_id={floor.get('parent_id')}, site={floor.get('site')}, location={floor.get('location')}, building_id={floor.get('building_id')}, building={floor.get('building')}, facility_id={floor.get('facility_id')}, facility={floor.get('facility')}")
            
            # Find site name
            site_name = "N/A"
            if site_id:
                for s in st.session_state.sites:
                    if isinstance(s, dict):
                        s_id = s.get("id") or s.get("site_id") or s.get("location_id")
                        if str(s_id) == str(site_id):
                            site_name = s.get("name") or s.get("site_name") or s.get("title") or s.get("location_name") or "N/A"
                            break
            
            floors_list.append({
                "site_name": site_name if site_name else "N/A",
                "floor_name": floor_name if floor_name else "N/A",
                "site_id": site_id if site_id else "N/A",
                "floor_id": floor_id if floor_id else "N/A"
            })
    
    spaces_list = []
    for space in st.session_state.spaces:
        if isinstance(space, dict):
            # Try multiple field names
            space_id = space.get("id") or space.get("space_id") or space.get("room_id")
            space_name = space.get("name") or space.get("space_name") or space.get("title") or space.get("room_name")
            floor_id = space.get("floorId") or space.get("floor_id") or space.get("parent_id")
            site_id = space.get("siteId") or space.get("site_id") or space.get("location_id")
            
            # Debug: Show what fields are available and what we found (only in debug mode)
            if debug_mode and len(spaces_list) == 0:  # Only show for first space
                st.write(f"**Debug - Space fields available:** {list(space.keys())}")
                st.write(f"**Debug - Floor ID found:** {floor_id}")
                st.write(f"**Debug - Site ID found:** {site_id}")
                st.write(f"**Debug - Trying these floor fields:** floorId={space.get('floorId')}, floor_id={space.get('floor_id')}, parent_id={space.get('parent_id')}")
                st.write(f"**Debug - Trying these site fields:** siteId={space.get('siteId')}, site_id={space.get('site_id')}, location_id={space.get('location_id')}")
            
            # Find floor and site names
            floor_name = "N/A"
            site_name = "N/A"
            
            # Find floor name
            if floor_id:
                for f in st.session_state.floors:
                    if isinstance(f, dict):
                        f_id = f.get("id") or f.get("floor_id")
                        if str(f_id) == str(floor_id):
                            floor_name = f.get("name") or f.get("floor_name") or f.get("title") or "N/A"
                            break
            
            # Find site name (use direct siteId from space)
            if site_id:
                for s in st.session_state.sites:
                    if isinstance(s, dict):
                        s_id = s.get("id") or s.get("site_id") or s.get("siteId") or s.get("location_id")
                        if str(s_id) == str(site_id):
                            site_name = s.get("name") or s.get("site_name") or s.get("title") or s.get("location_name") or "N/A"
                            break
            
            spaces_list.append({
                "site_name": site_name if site_name else "N/A",
                "floor_name": floor_name if floor_name else "N/A",
                "space_name": space_name if space_name else "N/A",
                "site_id": site_id if site_id else "N/A",
                "floor_id": floor_id if floor_id else "N/A",
                "space_id": space_id if space_id else "N/A"
            })
    
    # Display as tabs with cascading filters
    tab1, tab2, tab3 = st.tabs(["📍 Sites", "🏢 Floors", "🚪 Spaces"])
    
    with tab1:
        if sites_list:
            sites_df = pd.DataFrame(sites_list)
            st.write(f"**Total Sites:** {len(sites_df)}")
            st.dataframe(sites_df, width='stretch', hide_index=True)
            
            # Download button
            csv_sites = sites_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Sites Lookup",
                data=csv_sites,
                file_name="sites_lookup.csv",
                mime="text/csv"
            )
        else:
            st.warning("No sites found")
    
    with tab2:
        if floors_list:
            floors_df = pd.DataFrame(floors_list)
            
            # Cascading filter: Select site to filter floors
            unique_sites = sorted(floors_df["site_name"].unique())
            selected_site = st.selectbox(
                "🔍 Filter by Site:",
                options=["All Sites"] + list(unique_sites),
                key="floor_site_filter"
            )
            
            # Apply filter
            if selected_site != "All Sites":
                filtered_floors = floors_df[floors_df["site_name"] == selected_site]
            else:
                filtered_floors = floors_df
            
            st.write(f"**Showing:** {len(filtered_floors)} of {len(floors_df)} floors")
            st.dataframe(filtered_floors, width='stretch', hide_index=True)
            
            # Download button (downloads filtered data)
            csv_floors = filtered_floors.to_csv(index=False)
            st.download_button(
                label=f"📥 Download {'Filtered' if selected_site != 'All Sites' else 'All'} Floors",
                data=csv_floors,
                file_name=f"floors_lookup{'_' + selected_site.replace(' ', '_') if selected_site != 'All Sites' else ''}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No floors found")
    
    with tab3:
        if spaces_list:
            spaces_df = pd.DataFrame(spaces_list)
            
            # Cascading filters: Site -> Floor -> Spaces
            col1, col2 = st.columns(2)
            
            with col1:
                unique_sites_spaces = sorted(spaces_df["site_name"].unique())
                selected_site_space = st.selectbox(
                    "🔍 Filter by Site:",
                    options=["All Sites"] + list(unique_sites_spaces),
                    key="space_site_filter"
                )
            
            # Filter floors based on selected site
            if selected_site_space != "All Sites":
                available_floors = sorted(spaces_df[spaces_df["site_name"] == selected_site_space]["floor_name"].unique())
            else:
                available_floors = sorted(spaces_df["floor_name"].unique())
            
            with col2:
                selected_floor = st.selectbox(
                    "🔍 Filter by Floor:",
                    options=["All Floors"] + list(available_floors),
                    key="space_floor_filter"
                )
            
            # Apply filters
            filtered_spaces = spaces_df.copy()
            if selected_site_space != "All Sites":
                filtered_spaces = filtered_spaces[filtered_spaces["site_name"] == selected_site_space]
            if selected_floor != "All Floors":
                filtered_spaces = filtered_spaces[filtered_spaces["floor_name"] == selected_floor]
            
            st.write(f"**Showing:** {len(filtered_spaces)} of {len(spaces_df)} spaces")
            st.dataframe(filtered_spaces, width='stretch', hide_index=True)
            
            # Download button (downloads filtered data)
            csv_spaces = filtered_spaces.to_csv(index=False)
            filename_parts = ["spaces_lookup"]
            if selected_site_space != "All Sites":
                filename_parts.append(selected_site_space.replace(" ", "_"))
            if selected_floor != "All Floors":
                filename_parts.append(selected_floor.replace(" ", "_"))
            
            st.download_button(
                label=f"📥 Download {'Filtered' if len(filename_parts) > 1 else 'All'} Spaces",
                data=csv_spaces,
                file_name="_".join(filename_parts) + ".csv",
                mime="text/csv"
            )
        else:
            st.warning("No spaces found")
    
    st.divider()
    
    # Section 2: Upload CSV
    st.header("2️⃣ Upload CSV")
    
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"],
        help="Upload your jobs CSV file"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.csv_data = df
            st.success(f"✅ Loaded {len(df)} rows")
            
            with st.expander("📄 Preview Data", expanded=True):
                st.dataframe(df, width='stretch')
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")
            return
    
    if st.session_state.csv_data is None:
        st.info("👆 Upload a CSV file to continue")
        return
    
    df = st.session_state.csv_data
    
    # Section 3: Audit & Fix
    st.header("3️⃣ Audit & Fix")
    
    if not st.session_state.lookups_loaded:
        st.warning("⚠️ Please load reference data (step 1) before auditing")
        return
    
    # Inline editable data grid with cascading dropdowns
    with st.expander("✏️ Edit CSV Data", expanded=True):
        st.info("💡 Edit cells below, then click 'Audit & Validate' or 'Re-audit' to see updated validation")
        
        # Create a copy for editing
        edited_df = df.copy()
        
        # Create columns for the main editing interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**Edit Data:**")
        
        with col2:
            if st.button("🔄 Reset to Original", help="Reset all changes back to original CSV"):
                edited_df = df.copy()
                st.session_state.csv_data = edited_df
                st.rerun()
        
        # Create the editable table with cascading dropdowns
        for idx, row in df.iterrows():
            st.write(f"**Row {idx + 1}:**")
            
            # Create columns for inline editing
            cols = st.columns([2, 1, 1, 1, 1, 2])  # title, site, floor, space, owner, other fields
            
            with cols[0]:
                # Title and description (always editable)
                title = st.text_input("Title", value=str(row.get("title_en", "")), key=f"title_{idx}")
                description = st.text_input("Description", value=str(row.get("description_en", "")), key=f"desc_{idx}")
                edited_df.at[idx, "title_en"] = title
                edited_df.at[idx, "description_en"] = description
            
            with cols[1]:
                # Site dropdown
                site_options = ["Select Site..."] + sorted([s.get("name", s.get("site_name", "")) for s in st.session_state.sites if s.get("name") or s.get("site_name")])
                current_site = row.get("site_name", "")
                if current_site not in site_options:
                    current_site = "Select Site..."
                
                selected_site = st.selectbox(
                    "Site",
                    options=site_options,
                    index=site_options.index(current_site) if current_site in site_options else 0,
                    key=f"site_{idx}"
                )
                
                if selected_site != "Select Site...":
                    edited_df.at[idx, "site_name"] = selected_site
                else:
                    edited_df.at[idx, "site_name"] = ""
            
            with cols[2]:
                # Floor dropdown (filtered by selected site)
                if selected_site != "Select Site...":
                    # Find floors for this site
                    site_id = None
                    for site in st.session_state.sites:
                        if site.get("name") == selected_site or site.get("site_name") == selected_site:
                            site_id = site.get("id") or site.get("site_id") or site.get("siteId")
                            break
                    
                    if site_id:
                        floor_options = ["Select Floor..."] + sorted([f.get("name", f.get("floor_name", "")) for f in st.session_state.floors if (f.get("siteId") == site_id or f.get("siteId") == str(site_id) or f.get("site_id") == site_id or f.get("site_id") == str(site_id)) and (f.get("name") or f.get("floor_name"))])
                    else:
                        floor_options = ["Select Floor..."]
                else:
                    floor_options = ["Select Floor..."]
                
                current_floor = row.get("floor_name", "")
                if current_floor not in floor_options:
                    current_floor = "Select Floor..."
                
                selected_floor = st.selectbox(
                    "Floor",
                    options=floor_options,
                    index=floor_options.index(current_floor) if current_floor in floor_options else 0,
                    key=f"floor_{idx}"
                )
                
                if selected_floor != "Select Floor...":
                    edited_df.at[idx, "floor_name"] = selected_floor
                else:
                    edited_df.at[idx, "floor_name"] = ""
            
            with cols[3]:
                # Space dropdown (filtered by selected site and floor)
                if selected_site != "Select Site..." and selected_floor != "Select Floor...":
                    # Find space for this site and floor
                    site_id = None
                    floor_id = None
                    
                    for site in st.session_state.sites:
                        if site.get("name") == selected_site or site.get("site_name") == selected_site:
                            site_id = site.get("id") or site.get("site_id") or site.get("siteId")
                            break
                    
                    for floor in st.session_state.floors:
                        if (((floor.get("siteId") == site_id or floor.get("siteId") == str(site_id)) or 
                             (floor.get("site_id") == site_id or floor.get("site_id") == str(site_id))) and 
                            (floor.get("name") == selected_floor or floor.get("floor_name") == selected_floor)):
                            floor_id = floor.get("id") or floor.get("floor_id")
                            break
                    
                    if site_id and floor_id:
                        space_options = ["Select Space..."] + sorted([s.get("name", s.get("space_name", "")) for s in st.session_state.spaces if (s.get("floorId") == floor_id or s.get("floorId") == str(floor_id) or s.get("floor_id") == floor_id or s.get("floor_id") == str(floor_id)) and (s.get("name") or s.get("space_name"))])
                    else:
                        space_options = ["Select Space..."]
                else:
                    space_options = ["Select Space..."]
                
                current_space = row.get("space_name", "")
                if current_space not in space_options:
                    current_space = "Select Space..."
                
                selected_space = st.selectbox(
                    "Space",
                    options=space_options,
                    index=space_options.index(current_space) if current_space in space_options else 0,
                    key=f"space_{idx}"
                )
                
                if selected_space != "Select Space...":
                    edited_df.at[idx, "space_name"] = selected_space
                else:
                    edited_df.at[idx, "space_name"] = ""
            
            with cols[4]:
                # Owner dropdown
                owner_options = ["Select Owner..."] + sorted([u.get("email", u.get("owner_email", "")) for u in st.session_state.users if u.get("email") or u.get("owner_email")])
                current_owner = row.get("owner_email", "")
                if current_owner not in owner_options:
                    current_owner = "Select Owner..."
                
                selected_owner = st.selectbox(
                    "Owner",
                    options=owner_options,
                    index=owner_options.index(current_owner) if current_owner in owner_options else 0,
                    key=f"owner_{idx}"
                )
                
                if selected_owner != "Select Owner...":
                    edited_df.at[idx, "owner_email"] = selected_owner
                else:
                    edited_df.at[idx, "owner_email"] = ""
            
            with cols[5]:
                # Other important fields
                date_start = st.text_input("Start Date", value=str(row.get("date_start", "")), key=f"date_start_{idx}")
                date_end = st.text_input("End Date", value=str(row.get("date_end", "")), key=f"date_end_{idx}")
                edited_df.at[idx, "date_start"] = date_start
                edited_df.at[idx, "date_end"] = date_end
            
            # Recurrence settings
            with st.expander(f"🔄 Recurrence Settings (Row {idx + 1})", expanded=False):
                recurrence_settings = build_recurrence_ui(idx, row)
                
                # Ensure recurrence columns exist in the dataframe
                for key in recurrence_settings.keys():
                    if key not in edited_df.columns:
                        edited_df[key] = None
                
                # Store recurrence settings in the dataframe
                for key, value in recurrence_settings.items():
                    edited_df.at[idx, key] = value
            
            st.divider()
        
        # Show the updated dataframe
        st.write("**Updated Data Preview:**")
        st.dataframe(edited_df, width='stretch')
        
        # Update session state with edited data
        if not edited_df.equals(df):
            st.session_state.csv_data = edited_df
            df = edited_df  # Update local df too
            st.info("⚡ Changes detected - click 'Audit & Validate' or 'Re-audit' to validate")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Audit & Validate", type="primary"):
            with st.spinner("Validating rows..."):
                # Use the current df which includes any edits
                current_df = st.session_state.csv_data
                
                validator = JobValidator(
                    st.session_state.sites,
                    st.session_state.floors,
                    st.session_state.spaces,
                    st.session_state.users
                )
                
                all_issues = []
                seen_keys = set()
                
                for enum_idx, (idx, row) in enumerate(current_df.iterrows()):
                    row_num = enum_idx + 2  # Account for header (row 1 is header, data starts at row 2)
                    issues = validator.validate_row(row, row_num, seen_keys)
                    all_issues.extend(issues)
                
                audit_df = pd.DataFrame(all_issues)
                st.session_state.audit_issues = audit_df
                
                st.success("✅ Validation complete")
    
    with col2:
        if st.button("🔄 Re-audit"):
            if not st.session_state.lookups_loaded:
                st.error("Please load reference data first")
            else:
                with st.spinner("Re-validating..."):
                    # Use the current df which includes any edits
                    current_df = st.session_state.csv_data
                    
                    validator = JobValidator(
                        st.session_state.sites,
                        st.session_state.floors,
                        st.session_state.spaces,
                        st.session_state.users
                    )
                    
                    all_issues = []
                    seen_keys = set()
                    
                    for enum_idx, (idx, row) in enumerate(current_df.iterrows()):
                        row_num = enum_idx + 2  # Account for header (row 1 is header, data starts at row 2)
                        issues = validator.validate_row(row, row_num, seen_keys)
                        all_issues.extend(issues)
                    
                    audit_df = pd.DataFrame(all_issues)
                    st.session_state.audit_issues = audit_df
                    
                    st.success("✅ Re-validation complete")
    
    # Show audit results
    if st.session_state.audit_issues is not None:
        audit_df = st.session_state.audit_issues
        current_df = st.session_state.csv_data
        
        # Enrich audit data with location information from CSV
        audit_with_location = audit_df.copy()
        
        # Add site, floor, space columns to audit results
        sites_col = []
        floors_col = []
        spaces_col = []
        
        for idx, row in audit_with_location.iterrows():
            row_num = row["row_number"]
            csv_idx = row_num - 2  # Convert back to dataframe index
            
            if csv_idx >= 0 and csv_idx < len(current_df):
                csv_row = current_df.iloc[csv_idx]
                # Get location names from CSV
                site = csv_row.get("site_name", csv_row.get("_resolved_site_id", ""))
                floor = csv_row.get("floor_name", csv_row.get("_resolved_floor_id", ""))
                space = csv_row.get("space_name", csv_row.get("_resolved_space_id", ""))
                
                sites_col.append(str(site) if pd.notna(site) and str(site).strip() != "" else "N/A")
                floors_col.append(str(floor) if pd.notna(floor) and str(floor).strip() != "" else "N/A")
                spaces_col.append(str(space) if pd.notna(space) and str(space).strip() != "" else "N/A")
            else:
                sites_col.append("N/A")
                floors_col.append("N/A")
                spaces_col.append("N/A")
        
        audit_with_location.insert(1, "site", sites_col)
        audit_with_location.insert(2, "floor", floors_col)
        audit_with_location.insert(3, "space", spaces_col)
        
        # Summary metrics
        error_count = len(audit_with_location[audit_with_location["status"] == "ERROR"])
        warn_count = len(audit_with_location[audit_with_location["status"] == "WARN"])
        ok_count = len(audit_with_location[audit_with_location["status"] == "OK"])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("✅ OK", ok_count)
        col2.metric("⚠️ Warnings", warn_count)
        col3.metric("❌ Errors", error_count)
        
        # Calculate ready rows
        error_rows = audit_with_location[audit_with_location["status"] == "ERROR"]["row_number"].unique()
        ready_count = len(current_df) - len(error_rows)
        col4.metric("📋 Ready for Import", f"{ready_count} / {len(current_df)}")
        
        # Group issues by row number
        row_issues = {}
        for idx, issue in audit_with_location.iterrows():
            row_num = issue["row_number"]
            if row_num not in row_issues:
                row_issues[row_num] = []
            row_issues[row_num].append(issue)
        
        # Show collapsed rows with visual indicators
        st.write("**Row-by-Row Issues:**")
        
        # Filter options
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            filter_status = st.multiselect(
                "Show Status",
                options=["ERROR", "WARN", "OK"],
                default=["ERROR", "WARN"],
                key="audit_status_filter"
            )
        
        with filter_col2:
            unique_sites = sorted([s for s in audit_with_location["site"].unique() if s != "N/A"])
            selected_site_audit = st.selectbox(
                "Filter by Site",
                options=["All Sites"] + unique_sites,
                key="audit_site_filter"
            )
        
        with filter_col3:
            if selected_site_audit != "All Sites":
                available_floors_audit = sorted([f for f in audit_with_location[audit_with_location["site"] == selected_site_audit]["floor"].unique() if f != "N/A"])
            else:
                available_floors_audit = sorted([f for f in audit_with_location["floor"].unique() if f != "N/A"])
            
            selected_floor_audit = st.selectbox(
                "Filter by Floor",
                options=["All Floors"] + available_floors_audit,
                key="audit_floor_filter"
            )
        
        with filter_col4:
            if selected_site_audit != "All Sites" and selected_floor_audit != "All Floors":
                available_spaces_audit = sorted([s for s in audit_with_location[(audit_with_location["site"] == selected_site_audit) & (audit_with_location["floor"] == selected_floor_audit)]["space"].unique() if s != "N/A"])
            elif selected_site_audit != "All Sites":
                available_spaces_audit = sorted([s for s in audit_with_location[audit_with_location["site"] == selected_site_audit]["space"].unique() if s != "N/A"])
            elif selected_floor_audit != "All Floors":
                available_spaces_audit = sorted([s for s in audit_with_location[audit_with_location["floor"] == selected_floor_audit]["space"].unique() if s != "N/A"])
            else:
                available_spaces_audit = sorted([s for s in audit_with_location["space"].unique() if s != "N/A"])
            
            selected_space_audit = st.selectbox(
                "Filter by Space",
                options=["All Spaces"] + available_spaces_audit,
                key="audit_space_filter"
            )
        
        # Display rows
        for row_num in sorted(row_issues.keys()):
            issues = row_issues[row_num]
            csv_idx = row_num - 2
            
            if csv_idx >= 0 and csv_idx < len(current_df):
                csv_row = current_df.iloc[csv_idx]
                
                # Check if this row should be shown based on filters
                show_row = True
                
                # Filter by status
                if filter_status:
                    row_statuses = [issue["status"] for issue in issues]
                    if not any(status in filter_status for status in row_statuses):
                        show_row = False
                
                # Filter by location
                if show_row and selected_site_audit != "All Sites":
                    site = csv_row.get("site_name", "")
                    if str(site) != selected_site_audit:
                        show_row = False
                
                if show_row and selected_floor_audit != "All Floors":
                    floor = csv_row.get("floor_name", "")
                    if str(floor) != selected_floor_audit:
                        show_row = False
                
                if show_row and selected_space_audit != "All Spaces":
                    space = csv_row.get("space_name", "")
                    if str(space) != selected_space_audit:
                        show_row = False
                
                if not show_row:
                    continue
                
                # Determine row status and color
                has_errors = any(issue["status"] == "ERROR" for issue in issues)
                has_warnings = any(issue["status"] == "WARN" for issue in issues)
                is_ok = all(issue["status"] == "OK" for issue in issues)
                
                if has_errors:
                    status_icon = "❌"
                    status_color = "red"
                    status_text = "ERRORS"
                elif has_warnings:
                    status_icon = "⚠️"
                    status_color = "orange"
                    status_text = "WARNINGS"
                else:
                    status_icon = "✅"
                    status_color = "green"
                    status_text = "OK"
                
                # Get current values from CSV
                site_name = str(csv_row.get('site_name', 'N/A')).strip()
                floor_name = str(csv_row.get('floor_name', 'N/A')).strip()
                space_name = str(csv_row.get('space_name', 'N/A')).strip()
                
                # Clean up N/A values
                if site_name in ['N/A', 'nan', '']:
                    site_name = 'Not Set'
                if floor_name in ['N/A', 'nan', '']:
                    floor_name = 'Not Set'
                if space_name in ['N/A', 'nan', '']:
                    space_name = 'Not Set'
                
                # Create location hierarchy display
                location_parts = [site_name]
                if floor_name != 'Not Set':
                    location_parts.append(floor_name)
                if space_name != 'Not Set':
                    location_parts.append(space_name)
                
                location_info = " → ".join(location_parts)
                
                # Create the expander with summary in the title
                expander_title = f"{status_icon} Row {row_num}: {csv_row.get('title_en', 'Untitled')} | 📍 {location_info} | {status_text}"
                
                with st.expander(expander_title, expanded=False):
                    # Show issues summary
                    error_count = len([i for i in issues if i["status"] == "ERROR"])
                    warn_count = len([i for i in issues if i["status"] == "WARN"])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Errors", error_count)
                    with col2:
                        st.metric("Warnings", warn_count)
                    with col3:
                        st.metric("Total Issues", len(issues))
                    
                    # Show detailed issues with field highlighting
                    st.write("**Issues:**")
                    for issue in issues:
                        if issue["status"] == "ERROR":
                            # Add field-specific highlighting
                            if "SITE" in issue['issue_code']:
                                st.error(f"❌ {issue['issue_code']}: {issue['issue_detail']} 🔍 *Check Site field below*")
                            elif "FLOOR" in issue['issue_code']:
                                st.error(f"❌ {issue['issue_code']}: {issue['issue_detail']} 🔍 *Check Floor field below*")
                            elif "SPACE" in issue['issue_code']:
                                st.error(f"❌ {issue['issue_code']}: {issue['issue_detail']} 🔍 *Check Space field below*")
                            elif "OWNER" in issue['issue_code']:
                                st.error(f"❌ {issue['issue_code']}: {issue['issue_detail']} 🔍 *Check Owner field below*")
                            else:
                                st.error(f"❌ {issue['issue_code']}: {issue['issue_detail']}")
                            
                            if issue.get('suggestion'):
                                st.info(f"💡 Suggestion: {issue['suggestion']}")
                        elif issue["status"] == "WARN":
                            st.warning(f"⚠️ {issue['issue_code']}: {issue['issue_detail']}")
                            if issue.get('suggestion'):
                                st.info(f"💡 Suggestion: {issue['suggestion']}")
                        else:
                            st.success(f"✅ {issue['issue_code']}: {issue['issue_detail']}")
                    
                    # Inline editing section
                    st.write("**Edit This Row:**")
                    
                    # Create columns for editing
                    edit_cols = st.columns([2, 1, 1, 1, 1, 2])
                    
                    with edit_cols[0]:
                        # Title and description
                        title = st.text_input("Title", value=str(csv_row.get("title_en", "")), key=f"edit_title_{row_num}")
                        description = st.text_input("Description", value=str(csv_row.get("description_en", "")), key=f"edit_desc_{row_num}")
                        
                        # Update session state immediately when values change
                        if title != str(csv_row.get("title_en", "")):
                            st.session_state.csv_data.at[csv_idx, "title_en"] = title
                            st.success(f"✅ Title updated: '{title}'")
                        if description != str(csv_row.get("description_en", "")):
                            st.session_state.csv_data.at[csv_idx, "description_en"] = description
                            st.success(f"✅ Description updated: '{description}'")
                    
                    with edit_cols[1]:
                        # Site dropdown
                        site_options = ["Select Site..."] + sorted([s.get("name", s.get("site_name", "")) for s in st.session_state.sites if s.get("name") or s.get("site_name")])
                        current_site = csv_row.get("site_name", "")
                        if current_site not in site_options:
                            current_site = "Select Site..."
                        
                        # Check if site has issues
                        site_has_issues = any("SITE" in issue['issue_code'] for issue in issues)
                        site_label = "🔴 Site" if site_has_issues else "Site"
                        
                        selected_site = st.selectbox(
                            site_label,
                            options=site_options,
                            index=site_options.index(current_site) if current_site in site_options else 0,
                            key=f"edit_site_{row_num}"
                        )
                        
                        # Update session state immediately when site changes
                        if selected_site != "Select Site...":
                            if selected_site != str(csv_row.get("site_name", "")):
                                st.session_state.csv_data.at[csv_idx, "site_name"] = selected_site
                                st.success(f"✅ Site updated: '{selected_site}'")
                        else:
                            if str(csv_row.get("site_name", "")) != "":
                                st.session_state.csv_data.at[csv_idx, "site_name"] = ""
                                st.success("✅ Site cleared")
                    
                    with edit_cols[2]:
                        # Floor dropdown (filtered by selected site)
                        if selected_site != "Select Site...":
                            site_id = None
                            for site in st.session_state.sites:
                                if site.get("name") == selected_site or site.get("site_name") == selected_site:
                                    site_id = site.get("id") or site.get("site_id") or site.get("siteId")
                                    break
                            
                            if site_id:
                                floor_options = ["Select Floor..."] + sorted([f.get("name", f.get("floor_name", "")) for f in st.session_state.floors if (f.get("siteId") == site_id or f.get("siteId") == str(site_id) or f.get("site_id") == site_id or f.get("site_id") == str(site_id)) and (f.get("name") or f.get("floor_name"))])
                            else:
                                floor_options = ["Select Floor..."]
                        else:
                            floor_options = ["Select Floor..."]
                        
                        current_floor = csv_row.get("floor_name", "")
                        if current_floor not in floor_options:
                            current_floor = "Select Floor..."
                        
                        # Check if floor has issues
                        floor_has_issues = any("FLOOR" in issue['issue_code'] for issue in issues)
                        floor_label = "🔴 Floor" if floor_has_issues else "Floor"
                        
                        selected_floor = st.selectbox(
                            floor_label,
                            options=floor_options,
                            index=floor_options.index(current_floor) if current_floor in floor_options else 0,
                            key=f"edit_floor_{row_num}"
                        )
                        
                        # Update session state immediately when floor changes
                        if selected_floor != "Select Floor...":
                            if selected_floor != str(csv_row.get("floor_name", "")):
                                st.session_state.csv_data.at[csv_idx, "floor_name"] = selected_floor
                                st.success(f"✅ Floor updated: '{selected_floor}'")
                        else:
                            if str(csv_row.get("floor_name", "")) != "":
                                st.session_state.csv_data.at[csv_idx, "floor_name"] = ""
                                st.success("✅ Floor cleared")
                    
                    with edit_cols[3]:
                        # Space dropdown (filtered by selected site and floor)
                        if selected_site != "Select Site..." and selected_floor != "Select Floor...":
                            site_id = None
                            floor_id = None
                            
                            for site in st.session_state.sites:
                                if site.get("name") == selected_site or site.get("site_name") == selected_site:
                                    site_id = site.get("id") or site.get("site_id") or site.get("siteId")
                                    break
                            
                            for floor in st.session_state.floors:
                                if (((floor.get("siteId") == site_id or floor.get("siteId") == str(site_id)) or 
                                     (floor.get("site_id") == site_id or floor.get("site_id") == str(site_id))) and 
                                    (floor.get("name") == selected_floor or floor.get("floor_name") == selected_floor)):
                                    floor_id = floor.get("id") or floor.get("floor_id")
                                    break
                            
                            if site_id and floor_id:
                                space_options = ["Select Space..."] + sorted([s.get("name", s.get("space_name", "")) for s in st.session_state.spaces if (s.get("floorId") == floor_id or s.get("floorId") == str(floor_id) or s.get("floor_id") == floor_id or s.get("floor_id") == str(floor_id)) and (s.get("name") or s.get("space_name"))])
                            else:
                                space_options = ["Select Space..."]
                        else:
                            space_options = ["Select Space..."]
                        
                        current_space = csv_row.get("space_name", "")
                        if current_space not in space_options:
                            current_space = "Select Space..."
                        
                        # Check if space has issues
                        space_has_issues = any("SPACE" in issue['issue_code'] for issue in issues)
                        space_label = "🔴 Space" if space_has_issues else "Space"
                        
                        selected_space = st.selectbox(
                            space_label,
                            options=space_options,
                            index=space_options.index(current_space) if current_space in space_options else 0,
                            key=f"edit_space_{row_num}"
                        )
                        
                        # Update session state immediately when space changes
                        if selected_space != "Select Space...":
                            if selected_space != str(csv_row.get("space_name", "")):
                                st.session_state.csv_data.at[csv_idx, "space_name"] = selected_space
                                st.success(f"✅ Space updated: '{selected_space}'")
                        else:
                            if str(csv_row.get("space_name", "")) != "":
                                st.session_state.csv_data.at[csv_idx, "space_name"] = ""
                                st.success("✅ Space cleared")
                    
                    with edit_cols[4]:
                        # Owner dropdown
                        owner_options = ["Select Owner..."] + sorted([u.get("email", u.get("owner_email", "")) for u in st.session_state.users if u.get("email") or u.get("owner_email")])
                        current_owner = csv_row.get("owner_email", "")
                        if current_owner not in owner_options:
                            current_owner = "Select Owner..."
                        
                        # Check if owner has issues
                        owner_has_issues = any("OWNER" in issue['issue_code'] for issue in issues)
                        owner_label = "🔴 Owner" if owner_has_issues else "Owner"
                        
                        selected_owner = st.selectbox(
                            owner_label,
                            options=owner_options,
                            index=owner_options.index(current_owner) if current_owner in owner_options else 0,
                            key=f"edit_owner_{row_num}"
                        )
                        
                        # Update session state immediately when owner changes
                        if selected_owner != "Select Owner...":
                            if selected_owner != str(csv_row.get("owner_email", "")):
                                st.session_state.csv_data.at[csv_idx, "owner_email"] = selected_owner
                                st.success(f"✅ Owner updated: '{selected_owner}'")
                        else:
                            if str(csv_row.get("owner_email", "")) != "":
                                st.session_state.csv_data.at[csv_idx, "owner_email"] = ""
                                st.success("✅ Owner cleared")
                    
                    with edit_cols[5]:
                        # Other important fields
                        date_start = st.text_input("Start Date", value=str(csv_row.get("date_start", "")), key=f"edit_date_start_{row_num}")
                        date_end = st.text_input("End Date", value=str(csv_row.get("date_end", "")), key=f"edit_date_end_{row_num}")
                        
                        # Update session state immediately when dates change
                        if date_start != str(csv_row.get("date_start", "")):
                            st.session_state.csv_data.at[csv_idx, "date_start"] = date_start
                            st.success(f"✅ Start Date updated: '{date_start}'")
                        if date_end != str(csv_row.get("date_end", "")):
                            st.session_state.csv_data.at[csv_idx, "date_end"] = date_end
                            st.success(f"✅ End Date updated: '{date_end}'")
                    
                    # Check if any changes were made
                    original_row = st.session_state.csv_data.iloc[csv_idx]
                    has_changes = (
                        str(original_row.get("title_en", "")) != str(title) or
                        str(original_row.get("description_en", "")) != str(description) or
                        str(original_row.get("site_name", "")) != str(selected_site if selected_site != "Select Site..." else "") or
                        str(original_row.get("floor_name", "")) != str(selected_floor if selected_floor != "Select Floor..." else "") or
                        str(original_row.get("space_name", "")) != str(selected_space if selected_space != "Select Space..." else "") or
                        str(original_row.get("owner_email", "")) != str(selected_owner if selected_owner != "Select Owner..." else "") or
                        str(original_row.get("date_start", "")) != str(date_start) or
                        str(original_row.get("date_end", "")) != str(date_end)
                    )
                    
                    if has_changes:
                        st.info("💡 Changes detected and saved! Click Re-validate to test fixes")
                        # Force a rerun to update the UI with new values
                        st.rerun()
                    
                    # Update button for this row
                    if st.button(f"🔄 Re-validate Row {row_num}", key=f"revalidate_{row_num}"):
                        # Ensure session state is updated with all changes
                        st.session_state.csv_data = current_df.copy()
                        
                        # Re-run validation for this specific row
                        validator = JobValidator(
                            st.session_state.sites,
                            st.session_state.floors,
                            st.session_state.spaces,
                            st.session_state.users
                        )
                        
                        # Get the updated row from session state
                        updated_row = st.session_state.csv_data.iloc[csv_idx]
                        seen_keys = set()
                        
                        # Validate the updated row
                        new_issues = validator.validate_row(updated_row, row_num, seen_keys)
                        
                        # Update the audit issues for this row
                        if st.session_state.audit_issues is not None:
                            # Remove old issues for this row
                            st.session_state.audit_issues = st.session_state.audit_issues[
                                st.session_state.audit_issues["row_number"] != row_num
                            ]
                            # Add new issues
                            if new_issues:
                                new_issues_df = pd.DataFrame(new_issues)
                                st.session_state.audit_issues = pd.concat([
                                    st.session_state.audit_issues, 
                                    new_issues_df
                                ], ignore_index=True)
                        
                        # Add debugging info for floor-site validation
                        if any("FLOOR_SITE_MISMATCH" in issue['issue_code'] for issue in issues):
                            st.write("**🔍 Debug Info:**")
                            st.write(f"- Resolved Site ID: {updated_row.get('_resolved_site_id', 'None')}")
                            st.write(f"- Resolved Floor ID: {updated_row.get('_resolved_floor_id', 'None')}")
                            # Create a fresh validator for debug info
                            debug_validator = JobValidator(
                                st.session_state.sites,
                                st.session_state.floors,
                                st.session_state.spaces,
                                st.session_state.users
                            )
                            st.write(f"- Floor-to-Site mapping: {dict(list(debug_validator.floor_to_site.items())[:3])}...")
                            if updated_row.get('_resolved_floor_id'):
                                expected_site = debug_validator.floor_to_site.get(updated_row.get('_resolved_floor_id'))
                                st.write(f"- Expected site for this floor: {expected_site}")
                        
                        st.success(f"✅ Row {row_num} updated! Re-running validation...")
                        st.rerun()
                
                # Add some spacing between rows
                st.divider()
        
        # Update session state with any changes
        st.session_state.csv_data = current_df
        
        # Export section
        st.subheader("📦 Export Results")
        
        if st.button("💾 Export Audit & Ready CSVs"):
            with st.spinner("Exporting..."):
                lookups = {
                    "sites": st.session_state.sites,
                    "floors": st.session_state.floors,
                    "spaces": st.session_state.spaces,
                    "users_count": len(st.session_state.users)  # Don't export full user list
                }
                
                # Use the current edited data from session state
                current_df = st.session_state.csv_data
                
                run_dir = export_run_outputs(
                    current_df,
                    audit_df,
                    lookups,
                    fa_domain
                )
                
                st.success(f"✅ Exported to: `{run_dir}`")
                st.info(f"""
                **Files created:**
                - `audit_report.csv` – All validation issues
                - `validated_ready.csv` – Rows ready for import
                - `lookup_cache.json` – Reference data snapshot
                - `run_summary.json` – Run metadata
                """)
        
        # Excel template download
        st.subheader("📋 Recurring Jobs Excel Template")
        
        if st.button("📥 Download Excel Template for Recurring Jobs"):
            # Create Excel template with examples
            excel_data = create_recurring_jobs_template()
            
            st.download_button(
                label="💾 Download Excel Template",
                data=excel_data,
                file_name="recurring_jobs_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download this template to see examples of how to set up recurring jobs"
            )
            
            st.info("""
            **📋 Excel Template includes:**
            - **Basic job fields**: title_en, description_en, site_name, etc.
            - **Recurrence examples**: Daily, Weekly, Monthly patterns
            - **Sample data**: Ready-to-use examples
            - **Instructions**: How to configure each recurrence type
            """)
    
    # Section 4: Import (Optional)
    st.header("4️⃣ Import to FacilityApps")
    
    if not enable_import:
        st.info("🔒 Import is disabled. Enable in sidebar to proceed.")
    elif st.session_state.audit_issues is None:
        st.info("Run audit first before importing")
    else:
        # Use the current edited data from session state
        current_df = st.session_state.csv_data.copy()
        
        # Show current data status with validation (only in debug mode)
        if debug_mode:
            st.info(f"📊 Using {len(current_df)} rows from session state for import")
            
            # Show sample of current data to prove it's updated
            st.write("**📋 Current Session State Data Sample:**")
            sample_data = current_df[['title_en', 'site_name', 'floor_name', 'space_name', 'owner_email']].head(3)
            st.dataframe(sample_data, width='stretch')
            
            # Show what will be sent to API
            st.write("**🔍 What Will Be Sent to API:**")
            if len(current_df) > 0:
                sample_row = current_df.iloc[0]
                sample_payload = build_job_payload(sample_row)
                st.write(f"- **Sample Row 1:** {sample_row['title_en']}")
                st.write(f"- **Site:** {sample_row.get('site_name', 'N/A')} → {sample_payload.get('locations', 'MISSING')}")
                st.write(f"- **Floor/Spaces:** {sample_payload.get('floors_spaces', 'MISSING')}")
                st.write(f"- **Owners:** {sample_payload.get('owners', 'MISSING')}")
            
            # Show lookup data status
            st.write("**📊 Lookup Data Status:**")
            st.write(f"- **Sites loaded:** {len(st.session_state.sites)}")
            st.write(f"- **Floors loaded:** {len(st.session_state.floors)}")
            st.write(f"- **Spaces loaded:** {len(st.session_state.spaces)}")
            st.write(f"- **Users loaded:** {len(st.session_state.users)}")
            
            if st.session_state.sites:
                st.write(f"- **Sample Site:** {st.session_state.sites[0]}")
            if st.session_state.users:
                st.write(f"- **Sample User:** {st.session_state.users[0]}")
        
        audit_df = st.session_state.audit_issues
        error_row_numbers = audit_df[audit_df["status"] == "ERROR"]["row_number"].unique()
        
        if len(error_row_numbers) > 0:
            st.warning(f"⚠️ {len(error_row_numbers)} rows have errors. Fix them before importing.")
        
        # Convert row_numbers to DataFrame positions and filter
        error_positions = [rn - 2 for rn in error_row_numbers]
        all_positions = set(range(len(current_df)))
        ready_positions = list(all_positions - set(error_positions))
        ready_df = current_df.iloc[ready_positions].copy()
        
        # Add original CSV row numbers for tracking
        ready_df['_original_csv_row'] = [pos + 2 for pos in ready_positions]
        
        st.info(f"**{len(ready_df)}** rows ready for import")
        
        if st.button("🚀 Run Import", disabled=(len(ready_df) == 0)):
            with st.spinner("Importing jobs..."):
                # Setup logging for this import session
                log_file = setup_logging()
                if debug_mode:
                    st.info(f"📝 Logging API payloads to: `{log_file}`")
                
                client = st.session_state.client
                
                results = []
                failures = []
                failure_count = 0
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, (df_idx, row) in enumerate(ready_df.iterrows()):
                    # Check failure threshold
                    if len(results) > 0:
                        failure_rate = failure_count / len(results)
                        if failure_rate > FAILURE_THRESHOLD:
                            st.error(f"🛑 Aborting: Failure rate {failure_rate:.1%} exceeds {FAILURE_THRESHOLD:.1%}")
                            break
                    
                    status_text.text(f"Importing row {idx + 1}/{len(ready_df)}...")
                    
                    payload = build_job_payload(row)
                    
                    # Log the payload being sent with detailed validation
                    logging.info(f"=== ROW {row.get('_original_csv_row', idx + 2)}: {row['title_en']} ===")
                    logging.info(f"Raw Row Data: {dict(row)}")
                    
                    # Debug ID resolution
                    validator = JobValidator(
                        st.session_state.sites,
                        st.session_state.floors,
                        st.session_state.spaces,
                        st.session_state.users
                    )
                    site_id, site_error = validator.resolve_site(row)
                    floor_id, floor_error = validator.resolve_floor(row, site_id)
                    space_id, space_error = validator.resolve_space(row, floor_id)
                    owner_id, owner_error = validator.resolve_owner(row)
                    
                    logging.info(f"ID Resolution Debug:")
                    logging.info(f"  Site: '{row.get('site_name', '')}' -> {site_id} (error: {site_error})")
                    logging.info(f"  Floor: '{row.get('floor_name', '')}' -> {floor_id} (error: {floor_error})")
                    logging.info(f"  Space: '{row.get('space_name', '')}' -> {space_id} (error: {space_error})")
                    logging.info(f"  Owner: '{row.get('owner_email', '')}' -> {owner_id} (error: {owner_error})")
                    
                    logging.info(f"Payload: {json.dumps(payload, indent=2)}")
                    logging.info(f"API Endpoint: {client.base_url}/api/1.0/planning/save/true")
                    logging.info(f"Headers: {json.dumps(dict(client.headers), indent=2)}")
                    
                    # Show validation in UI (only in debug mode)
                    if debug_mode:
                        st.write(f"**🔍 Payload Validation for Row {row.get('_original_csv_row', idx + 2)}:**")
                        st.write(f"- **Title:** {row['title_en']}")
                        st.write(f"- **Site Name:** {row.get('site_name', 'N/A')} → **Site ID:** {payload.get('locations', 'MISSING')}")
                        st.write(f"- **Floor Name:** {row.get('floor_name', 'N/A')} → **Floor/Spaces:** {payload.get('floors_spaces', 'MISSING')}")
                        st.write(f"- **Space Name:** {row.get('space_name', 'N/A')}")
                        st.write(f"- **Owner Email:** {row.get('owner_email', 'N/A')} → **Owner ID:** {payload.get('owners', 'MISSING')}")
                        st.write(f"- **Raw Payload Keys:** {list(payload.keys())}")
                    
                    # Validate payload before sending
                    validation_errors = []
                    if not payload.get("locations"):
                        validation_errors.append("Missing site ID (locations)")
                    if not payload.get("owners") or len(payload.get("owners", [])) == 0:
                        validation_errors.append("Missing owner ID")
                    
                    # Additional validation for required fields
                    if not row.get("site_name") and not row.get("site_id"):
                        validation_errors.append("Row missing site_name or site_id")
                    if not row.get("owner_email") and not row.get("owner_employee_id"):
                        validation_errors.append("Row missing owner_email or owner_employee_id")
                    
                    if validation_errors:
                        logging.error(f"Payload validation failed: {validation_errors}")
                        st.error(f"❌ Row {row.get('_original_csv_row', idx + 2)} validation failed: {', '.join(validation_errors)}")
                        failures.append({
                            "csv_row": row.get('_original_csv_row', idx + 2),
                            "status": "failed",
                            "error": f"Validation failed: {', '.join(validation_errors)}",
                            "title": row["title_en"]
                        })
                        continue
                    
                    success, result = client.create_job_with_retry(payload)
                    
                    # Log the response
                    if success:
                        logging.info(f"SUCCESS - Response: {json.dumps(result, indent=2)}")
                    else:
                        logging.error(f"FAILED - Error: {json.dumps(result, indent=2)}")
                    
                    if success:
                        job_id = result.get("id", "unknown")
                        results.append({
                            "csv_row": row.get('_original_csv_row', idx + 2),
                            "status": "success",
                            "job_id": job_id,
                            "title": row["title_en"]
                        })
                    else:
                        failure_count += 1
                        failures.append({
                            "csv_row": row.get('_original_csv_row', idx + 2),
                            "status": "failed",
                            "error": json.dumps(result),
                            "title": row["title_en"]
                        })
                    
                    # Rate limiting: ~1 req/sec
                    time.sleep(1)
                    
                    progress_bar.progress((idx + 1) / len(ready_df))
                
                progress_bar.empty()
                status_text.empty()
                
                # Export results
                timestamp = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")
                run_dir = Path("./runs") / timestamp
                run_dir.mkdir(parents=True, exist_ok=True)
                
                if results:
                    results_df = pd.DataFrame(results)
                    results_df.to_csv(run_dir / "created_ids.csv", index=False)
                
                if failures:
                    failures_df = pd.DataFrame(failures)
                    failures_df.to_csv(run_dir / "failures.csv", index=False)
                
                # Show summary
                col1, col2 = st.columns(2)
                col1.metric("✅ Successful", len(results))
                col2.metric("❌ Failed", len(failures))
                
                st.success(f"✅ Import complete! Results saved to `{run_dir}`")
                
                # Add log file download
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        log_content = f.read()
                    st.download_button(
                        label="📥 Download API Payload Log",
                        data=log_content,
                        file_name=f"api_payloads_{timestamp}.log",
                        mime="text/plain"
                    )
                
                if failures:
                    with st.expander("❌ View Failures"):
                        st.dataframe(pd.DataFrame(failures), width='stretch')


if __name__ == "__main__":
    main()

