# FA Job Importer - Design System Rules for Figma MCP

## Project Overview
**Application:** FacilityApps Bulk Job Importer  
**Framework:** Streamlit (Python web framework)  
**Purpose:** Enterprise data import tool for recurring job/roster management  
**Target Users:** Facility management administrators

---

## 1. Design Token Definitions

### Current Token Location
Design tokens are currently defined in `.streamlit/config.toml` (currently backed up as `config.toml.backup`)

### Token Format (TOML)
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Streamlit Theme Structure
Streamlit supports limited theming via these tokens:
- `primaryColor` - Accent color for interactive elements
- `backgroundColor` - Main background
- `secondaryBackgroundColor` - Sidebar and secondary surfaces
- `textColor` - Primary text color
- `font` - Font family ("sans serif", "serif", or "monospace")

### Custom CSS Variables (Not Yet Implemented)
Could be added via `st.markdown()` with embedded `<style>` tags for advanced theming.

---

## 2. Component Library

### Component Architecture
**Framework:** Streamlit (declarative Python components)

### Core UI Components Used

#### Authentication Components
- **Location:** `app.py` lines 23-97
- **Components:**
  - Login form with username/password fields
  - Error messaging
  - Session state management

```python
# Login form structure
st.markdown("## 🔐 Authentication Required")
st.text_input("Username", key="username")
st.text_input("Password", type="password", key="password")
st.button("🔓 Login")
```

#### Sidebar Components
- **Location:** `app.py` lines 1567-1636
- **Components:**
  - Configuration inputs (domain, token)
  - Toggle switches (Enable Import, Debug Mode)
  - Metrics display
  - Logout button

```python
with st.sidebar:
    st.header("⚙️ Configuration")
    st.text_input("FA Domain", value=default_domain)
    st.toggle("🚀 Enable Import", value=False)
    st.metric("Sites", count)
```

#### Data Display Components
- **Data tables:** `st.dataframe()`
- **Expanders:** `st.expander()` for collapsible sections
- **File uploader:** `st.file_uploader()` for CSV import
- **Buttons:** `st.button()` with icons
- **Status messages:** `st.success()`, `st.error()`, `st.warning()`, `st.info()`

#### Recurrence Builder UI
- **Location:** `app.py` lines 929-1199
- **Complex form with:**
  - Frequency dropdowns
  - Day-of-week selectors (checkboxes)
  - Date pickers
  - Number inputs
  - Radio buttons

---

## 3. Frameworks & Libraries

### UI Framework
- **Primary:** Streamlit 1.50.0 (Python web framework)
- **Paradigm:** Declarative, reactive UI
- **Rendering:** Server-side rendering with WebSocket updates

### Styling Libraries
- **Native:** Streamlit's built-in styling system
- **Custom CSS:** Injected via `st.markdown()` with `unsafe_allow_html=True`
- **No CSS preprocessors** (SASS/LESS)

### Build System
- **No build step required** (Streamlit handles bundling)
- **Deployment:** Direct Python execution
- **Dependencies:** `requirements.txt`

### Key Dependencies
```txt
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
python-dateutil>=2.8.2
pytz>=2023.3
python-dotenv>=1.0.0
openpyxl>=3.1.0
```

---

## 4. Asset Management

### Current Asset Structure
- **No image assets** currently used
- **Icons:** Emoji-based (Unicode) - e.g., 🔐, 📋, 🚀, ⚙️, 🔄
- **Future assets:** Would be stored in `/assets` or `/static` directory

### Asset References
Streamlit serves static files from:
```python
# Would reference as:
st.image("assets/logo.png")
# Or via data URIs for inline embedding
```

### No CDN Configuration
Currently self-contained, no external CDN dependencies

---

## 5. Icon System

### Current Approach
**Emoji-based icons** throughout the UI:
- 🔐 Authentication
- 📋 Main app
- 🚀 Import actions
- ⚙️ Configuration
- 🔄 Recurrence
- 📥 Download/Upload
- ✅ Success states
- ❌ Error states
- ⚠️ Warnings
- 🐛 Debug mode

### Icon Usage Pattern
```python
st.button("🚀 Enable Import")
st.header("⚙️ Configuration")
st.success("✅ Success message")
```

### Future Icon System
If migrating to custom icons:
- Store in `/assets/icons/`
- SVG format preferred
- Named convention: `icon-{name}.svg`
- Load via `st.image()` or embedded SVG in markdown

---

## 6. Styling Approach

### Current Methodology
**Native Streamlit styling** with limited customization

### Theme Configuration
- **File:** `.streamlit/config.toml`
- **Scope:** Global application theme
- **Limitations:** Only 5 theme properties available

### Custom CSS Injection (Available but not used)
```python
st.markdown("""
<style>
    /* Custom CSS here */
    .stButton > button {
        background-color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)
```

### Responsive Design
- **Handled by Streamlit automatically**
- Uses columns for layout: `st.columns([1, 2, 1])`
- Sidebar collapses on mobile
- No custom breakpoints needed

### Layout Patterns
```python
# Two-column layout
col1, col2 = st.columns(2)
with col1:
    st.text_input("Field 1")
with col2:
    st.text_input("Field 2")

# Sidebar for navigation/config
with st.sidebar:
    st.header("Settings")
```

---

## 7. Project Structure

### File Organization
```
FA Task Importer/
├── app.py                          # Main application (2904 lines)
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── secrets.toml               # Credentials & config
│   └── config.toml.backup         # Theme config (currently disabled)
├── .gitignore                     # Git exclusions
├── venv/                          # Python virtual environment
├── logs/                          # API payload logs
├── DEPLOYMENT.md                  # Deployment instructions
├── ADMIN_CREDENTIALS.md           # Auth documentation
└── LOGIN_INFO.txt                 # Quick reference

Key files for styling:
- app.py: Main UI components (lines 1535-2904)
- .streamlit/config.toml: Theme configuration
```

### Component Organization in app.py

#### Authentication (lines 23-97)
```python
def check_password() -> bool:
    # Username/password login form
```

#### API Client (lines 101-328)
```python
class FacilityAppsClient:
    # API interaction logic
```

#### Validation (lines 328-927)
```python
class JobValidator:
    # Business logic for data validation
```

#### UI Builders (lines 929-1532)
```python
def build_recurrence_ui(row_idx, row) -> Dict:
    # Complex form UI for recurrence settings

def build_recurrence_preview(settings) -> str:
    # Natural language preview of settings

def create_recurring_jobs_template() -> bytes:
    # Excel template generator
```

#### Main Application (lines 1535-2904)
```python
def main():
    # Main Streamlit app entry point
    # - Page config
    # - Authentication
    # - Sidebar
    # - Multi-step workflow:
    #   1. Load reference data
    #   2. Upload & validate CSV
    #   3. Review & edit
    #   4. Import jobs
```

---

## 8. Design Considerations for Figma

### Enterprise Application Requirements

#### Visual Hierarchy
1. **Primary actions** - Import, Load, Submit (prominent buttons)
2. **Secondary actions** - Download templates, Export
3. **Tertiary actions** - Debug toggle, Logout

#### Color System Needs
- **Success states:** Green (job created successfully)
- **Error states:** Red (validation failures)
- **Warning states:** Orange/Yellow (potential issues)
- **Info states:** Blue (informational messages)
- **Neutral states:** Gray (disabled, inactive)

#### Typography Requirements
- **Headings:** Clear hierarchy (H1: Page title, H2: Sections, H3: Subsections)
- **Body text:** Readable for data-heavy tables
- **Monospace:** For technical details (IDs, API tokens, JSON)
- **Labels:** Form field labels, metric labels

#### Spacing System
- **Compact mode:** For data tables and forms (many fields)
- **Comfortable mode:** For headers and primary actions
- **Wide mode:** Full-width layout for admin tools

#### Component Priorities
1. **Data tables** - Core feature (CSV display, validation results)
2. **Forms** - Configuration inputs, recurrence builder
3. **Buttons** - Various states and importance levels
4. **Status indicators** - Success/error/warning messages
5. **Modals/Expanders** - For detailed settings and row editing
6. **Sidebar** - Persistent navigation and configuration

---

## 9. Current UI Patterns

### Status Messaging Pattern
```python
# Success
st.success("✅ 150 sites loaded successfully")

# Error
st.error("❌ Invalid credentials")

# Warning
st.warning("⚠️ Import is ENABLED – writes will occur!")

# Info
st.info("ℹ️ Validation found 3 issues")
```

### Collapsible Sections
```python
with st.expander("🔄 Recurrence Settings (Row 1)", expanded=False):
    # Detailed settings here
```

### Tabular Data Display
```python
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
```

### Metrics Display
```python
col1, col2, col3 = st.columns(3)
col1.metric("Total Rows", 150)
col2.metric("Valid", 145)
col3.metric("Errors", 5)
```

---

## 10. Figma Design Recommendations

### Create These Component Sets

1. **Button System**
   - Primary button (CTA)
   - Secondary button
   - Tertiary button
   - Icon button
   - Toggle switch
   - States: default, hover, active, disabled

2. **Input System**
   - Text input
   - Password input
   - Number input
   - Date picker
   - Dropdown select
   - Multi-select checkboxes
   - Radio buttons
   - States: default, focus, error, disabled

3. **Feedback System**
   - Success alert
   - Error alert
   - Warning alert
   - Info alert
   - Toast notifications
   - Loading spinners
   - Progress indicators

4. **Data Display**
   - Table headers
   - Table rows (even/odd)
   - Table cells (text, number, date)
   - Empty states
   - Pagination (if needed)

5. **Layout Components**
   - Sidebar
   - Header bar
   - Section headers
   - Dividers
   - Cards/Panels
   - Expander/Accordion

6. **Login Screen**
   - Full-page layout
   - Centered card
   - Logo placement
   - Form structure

### Design Token Needs

#### Colors
- Primary brand color (currently `#FF4B4B`)
- Success: Green
- Error: Red
- Warning: Orange
- Info: Blue
- Background: White
- Surface: Light gray (`#F0F2F6`)
- Text: Dark gray (`#262730`)
- Border: Subtle gray
- Disabled: Muted gray

#### Typography
- Font family: Professional sans-serif (e.g., Inter, Roboto, System UI)
- Sizes: 12px, 14px, 16px, 18px, 24px, 32px
- Weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- Line heights: 1.5 for body, 1.2 for headings

#### Spacing
- Base unit: 4px
- Scale: 4, 8, 12, 16, 24, 32, 48, 64px
- Component padding: 12-16px
- Section spacing: 24-32px

#### Borders & Shadows
- Border radius: 4px (buttons, inputs), 8px (cards)
- Border width: 1px
- Shadow: Subtle elevation for cards and modals

---

## Integration Workflow

When Figma designs are ready:

1. **Extract design tokens** from Figma
2. **Update `.streamlit/config.toml`** with theme colors
3. **Generate custom CSS** for advanced styling
4. **Inject CSS** via `st.markdown()` in `app.py`
5. **Test responsiveness** at different screen sizes
6. **Document** component usage patterns

### Code Pattern for Applying Figma Tokens
```python
# In app.py, early in main()
def apply_custom_theme():
    st.markdown("""
    <style>
        /* Figma-generated CSS variables */
        :root {
            --primary-color: #FF4B4B;
            --success-color: #00C853;
            --error-color: #FF5252;
            /* ... more tokens */
        }
        
        /* Component styling */
        .stButton > button {
            background-color: var(--primary-color);
            border-radius: 8px;
            /* ... */
        }
    </style>
    """, unsafe_allow_html=True)

# Call early in main()
apply_custom_theme()
```

---

## Notes for Designers

- **Streamlit has styling limitations** - not all CSS properties work
- **Focus on Streamlit's native components** - custom components are complex
- **Emoji icons work universally** - but custom SVGs can be added
- **Tables are auto-styled** - limited customization available
- **Mobile responsiveness** is automatic - test on various devices
- **Dark mode** can be supported via theme configuration

**Contact:** matt@implifysolutions.com (Figma: @matt)

