# Figma Design Brief - FA Job Importer

## 🎯 Project Overview
**Application:** FacilityApps Bulk Job Importer  
**Purpose:** Enterprise admin tool for importing recurring cleaning/maintenance jobs  
**Tech Stack:** Python + Streamlit  
**Current Stage:** Functional MVP, ready for professional styling

---

## 📋 What We Need from Figma

### Design Deliverables
1. **Complete design system** with tokens (colors, typography, spacing)
2. **UI component library** (buttons, inputs, tables, alerts, etc.)
3. **Key screens:**
   - Login screen
   - Main dashboard with sidebar
   - Data validation table view
   - Recurrence settings form
   - Success/error states

### Design Requirements
- **Professional enterprise aesthetic** (not consumer-facing)
- **Data-dense layouts** (tables, forms, metrics)
- **Clear visual hierarchy** for multi-step workflow
- **Accessible color contrast** (WCAG AA minimum)
- **Responsive design** (desktop-first, mobile-friendly sidebar)

---

## 🎨 Current State

### Existing Theme
```toml
primaryColor = "#FF4B4B"        # Red accent
backgroundColor = "#FFFFFF"      # White
secondaryBackgroundColor = "#F0F2F6"  # Light gray
textColor = "#262730"           # Dark gray
font = "sans serif"
```

### Component Inventory
- ✅ Login form (username/password)
- ✅ Sidebar (configuration, metrics, logout)
- ✅ Multi-step workflow (4 main sections)
- ✅ Data tables (CSV preview, validation results)
- ✅ Complex forms (recurrence builder with 7+ inputs)
- ✅ Status alerts (success, error, warning, info)
- ✅ Collapsible sections (expanders)
- ✅ File upload/download
- ✅ Buttons (primary, secondary, toggle)
- ✅ Metrics display

### Current Icons
Using emoji-based icons throughout:
- 🔐 Authentication
- 📋 Documents/Lists
- 🚀 Actions
- ⚙️ Settings
- ✅❌⚠️ Status indicators

**Decision needed:** Keep emoji or use custom icon set?

---

## 🏗️ Application Structure

### Main Workflow (4 Steps)
1. **Load Reference Data** - Connect to API, load sites/floors/spaces/users
2. **Upload & Validate CSV** - Upload job list, see validation results
3. **Review & Edit** - Preview data, configure recurrence settings per job
4. **Import Jobs** - Batch create jobs with progress tracking

### Key UI Patterns

#### Login Screen
```
┌─────────────────────────────┐
│                             │
│   🔐 Authentication         │
│   FA Job Importer Login     │
│                             │
│   ┌─────────────────────┐   │
│   │ Username            │   │
│   └─────────────────────┘   │
│   ┌─────────────────────┐   │
│   │ •••••••             │   │
│   └─────────────────────┘   │
│   ┌─────────────────────┐   │
│   │    🔓 Login         │   │
│   └─────────────────────┘   │
│                             │
└─────────────────────────────┘
```

#### Main Layout
```
┌──────────┬────────────────────────────────────┐
│ Sidebar  │ Main Content Area                  │
│          │                                    │
│ ⚙️ Config │ 📋 FacilityApps Bulk Job Importer │
│          │                                    │
│ Logged:  │ 1️⃣ Load Reference Data            │
│ admin    │ [📥 Load Sites/Floors/...]         │
│          │                                    │
│ [Logout] │ 2️⃣ Upload & Validate CSV          │
│          │ [Choose CSV file]                  │
│ ───────  │                                    │
│          │ 3️⃣ Review & Edit Jobs             │
│ Domain:  │ ┌─────────────────────────────┐   │
│ [____]   │ │ Job Data Table              │   │
│          │ │ [Expandable row settings]   │   │
│ Token:   │ └─────────────────────────────┘   │
│ [****]   │                                    │
│          │ 4️⃣ Import Jobs                    │
│ ───────  │ [🚀 Import All]                   │
│          │                                    │
│ 🚀 Import│                                    │
│ ☐ Enable │                                    │
│          │                                    │
│ 🐛 Debug │                                    │
│ ☐ Enable │                                    │
│          │                                    │
│ ───────  │                                    │
│          │                                    │
│ Sites: 5 │                                    │
│ Floors:10│                                    │
│ Spaces:25│                                    │
│ Users: 8 │                                    │
└──────────┴────────────────────────────────────┘
```

#### Data Table View
```
┌──────────────────────────────────────────────────────────┐
│ Title          │ Site    │ Start Date │ Frequency │ ... │
├────────────────┼─────────┼────────────┼───────────┼─────┤
│ Daily Cleaning │ Bldg A  │ 2025-01-01 │ Daily     │ ... │
│ [🔄 Recurrence Settings ▼]                               │
│   ☑ Repeat this job                                      │
│   Frequency: Daily  Interval: 1                          │
│   Days: Mon Tue Wed Thu Fri Sat Sun                      │
│   Ends: After 30 occurrences                             │
│ ─────────────────────────────────────────────────────────│
│ Weekly Report  │ Bldg B  │ 2025-01-01 │ Weekly    │ ... │
└──────────────────────────────────────────────────────────┘
```

---

## 🎨 Design System Requirements

### Color Palette Needs

#### Semantic Colors
- **Primary/Brand** - Main CTA buttons, links, highlights
- **Success** - ✅ Jobs created, validations passed
- **Error** - ❌ Validation failures, API errors
- **Warning** - ⚠️ Potential issues, confirmations needed
- **Info** - ℹ️ Helpful tips, informational messages

#### Neutral Scale
- **Background** - Main canvas
- **Surface** - Cards, panels, sidebar
- **Border** - Subtle dividers, input borders
- **Text Primary** - Headings, body text
- **Text Secondary** - Labels, helper text
- **Text Disabled** - Inactive elements

### Typography System

#### Font Recommendations
Professional sans-serif options:
- Inter (modern, clean)
- IBM Plex Sans (enterprise feel)
- System UI (native, fast)
- Roboto (familiar, readable)

#### Type Scale
```
H1 (Page Title):     32px / Bold
H2 (Section):        24px / Semibold  
H3 (Subsection):     18px / Semibold
Body:                16px / Regular
Small:               14px / Regular
Caption:             12px / Regular
Button:              16px / Medium
```

### Spacing System
Base unit: **4px**

```
xs:  4px   - Tight spacing (icon padding)
sm:  8px   - Input padding
md:  16px  - Component spacing
lg:  24px  - Section spacing
xl:  32px  - Major sections
2xl: 48px  - Page-level spacing
```

### Component Specifications

#### Buttons
- **Height:** 40px (default), 48px (large), 32px (small)
- **Padding:** 16px horizontal
- **Border radius:** 8px (rounded) or 4px (sharp)
- **States:** Default, Hover, Active, Disabled, Loading

Types:
1. Primary (filled, brand color)
2. Secondary (outlined)
3. Tertiary (text only)
4. Danger (red, for destructive actions)

#### Input Fields
- **Height:** 40px
- **Padding:** 12px horizontal
- **Border:** 1px solid, subtle gray
- **Border radius:** 4px
- **States:** Default, Focus (brand color border), Error (red), Disabled

Types:
- Text input
- Password (with show/hide toggle)
- Number input
- Date picker
- Dropdown select
- Multi-select checkboxes

#### Tables
- **Row height:** 48px (comfortable) or 40px (compact)
- **Header:** Bold text, subtle background
- **Row:** Alternating background (zebra striping optional)
- **Border:** 1px solid between rows
- **Hover:** Subtle highlight on row hover

#### Alerts/Messages
- **Padding:** 12px
- **Border radius:** 8px
- **Icon:** Left-aligned, 20px
- **Border-left:** 4px solid (semantic color)

Types:
- Success (green)
- Error (red)
- Warning (orange)
- Info (blue)

---

## 🔧 Technical Constraints

### Streamlit Styling Limitations
1. **Limited CSS control** - Not all properties work in shadow DOM
2. **Global theme only** - 5 theme properties via config
3. **Component customization** - Via injected CSS (not all selectors work)
4. **No custom components** - Must use Streamlit's built-in components

### What Works Well
✅ Global color scheme (via config.toml)  
✅ Custom CSS for specific selectors  
✅ Typography (font family, sizes, weights)  
✅ Spacing and layout  
✅ Borders and shadows  
✅ Hover states  

### What's Challenging
⚠️ Deep component styling (shadow DOM)  
⚠️ Custom animations  
⚠️ Complex interactions  
⚠️ Custom form controls  

---

## 📦 Deliverable Format

### Preferred Structure in Figma

1. **📄 Cover Page**
   - Project overview
   - Version history
   - Contact info

2. **🎨 Design Tokens**
   - Color palette (with hex codes)
   - Typography scale
   - Spacing scale
   - Border radius values
   - Shadow definitions

3. **🧩 Component Library**
   - Buttons (all variants + states)
   - Inputs (all types + states)
   - Tables (headers, rows, cells)
   - Alerts (all types)
   - Cards/Panels
   - Navigation (sidebar)
   - Modals/Expanders

4. **📱 Key Screens**
   - Login (desktop + mobile)
   - Main dashboard (desktop + mobile)
   - Table view (with data)
   - Form view (recurrence builder)

5. **📐 Layout Grids**
   - Desktop breakpoints
   - Tablet adaptations
   - Mobile layouts

### Export Requirements
- **Design tokens** as JSON or CSS variables
- **Components** with clear naming
- **Screens** with specs (spacing, sizing)
- **Assets** as SVG (if custom icons)

---

## 🚀 Next Steps

1. **Review this brief** and the detailed `design_system_rules.md`
2. **Create initial concepts** (2-3 style directions)
3. **Review with stakeholder** (choose direction)
4. **Build component library** in Figma
5. **Design key screens**
6. **Extract design tokens** (via Figma MCP)
7. **Implement in code** (update config, CSS)
8. **Iterate & refine**

---

## 📞 Contact

**Project Owner:** Matt  
**Email:** matt@implifysolutions.com  
**Figma:** @matt

**Detailed Technical Spec:** See `.cursor/rules/design_system_rules.md`

