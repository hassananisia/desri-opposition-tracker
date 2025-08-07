import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os
import base64
from dotenv import load_dotenv
from supabase_config import (
    init_supabase, 
    get_user_added_projects, 
    get_removed_projects,
    add_user_project,
    remove_project,
    restore_project,
    restore_all_projects,
    delete_user_project,
    update_project_survey,
    add_survey_to_default_project,
    get_public_hearing_qa, 
    add_public_hearing_qa, 
    update_public_hearing_qa, 
    delete_public_hearing_qa,
    soft_delete_public_hearing_qa,
    restore_public_hearing_qa,
    get_removed_public_hearing_qa,
    get_active_public_hearing_qa
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="DESRI Public Engagement Intelligence Hub",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"  # Start with sidebar expanded
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: white;
    }
    
    /* Apply Verdana font to text elements */
    .stMarkdown, .stText {
        font-family: 'Verdana', sans-serif !important;
    }
    
    /* Control spacing around folium maps and metrics */
    iframe[src*="folium"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Reduce vertical spacing between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    /* Specific spacing control for map containers */
    div:has(> iframe) {
        margin-bottom: 1rem !important;
    }
    
    /* Completely hide ALL sidebar toggle buttons and their text */
    [data-testid="collapsedControl"], 
    [data-testid="baseButton-header"],
    button[kind="header"],
    .css-1rs6os,
    .css-17ziqus,
    button[title="Close sidebar"],
    button[aria-label="Close sidebar"],
    div:has(> button[kind="header"]) {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* Target any element containing the problematic text */
    *:has-text("keyboard_double_arrow_left"),
    *:has-text("keyboard_double_arrow_right"),
    button:has-text("keyboard_double_arrow_left"),
    button:has-text("keyboard_double_arrow_right") {
        display: none !important;
    }
    
    /* Use attribute selector to hide buttons with these texts */
    button[title*="keyboard_double_arrow"],
    [aria-label*="keyboard_double_arrow"] {
        display: none !important;
    }
    
    /* Hide any button in the header area */
    header button {
        display: none !important;
    }
    
    /* Ensure sidebar is always visible and cannot be collapsed */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 21rem !important;
        min-width: 21rem !important;
        position: sticky !important;
        left: 0 !important;
    }
    
    /* Hide the resize handle on the sidebar */
    [data-testid="stSidebarResizeHandle"] {
        display: none !important;
    }
    
    /* Additional targeting for Streamlit's dynamic classes */
    [class*="collapsedControl"] {
        display: none !important;
    }
    
    /* Style Add Project button in Opposition Tracker with light colors and green borders */
    #add-project-form-wrapper .stFormSubmitButton > button {
        background: #f8f9fa !important;
        background-color: #f8f9fa !important;
        color: #2e7d32 !important;
        border: 2px solid #2e7d32 !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(46, 125, 50, 0.15) !important;
    }
    
    #add-project-form-wrapper .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
        background-color: #2e7d32 !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(46, 125, 50, 0.3) !important;
        border: 2px solid #1b5e20 !important;
    }
    
    /* Style other primary buttons and form submit buttons to be green */
    .stButton > button[kind="primary"],
    .stButton > button[type="primary"],
    button.primary,
    div[data-testid="stForm"] button[kind="primary"],
    button[data-testid="baseButton-primary"],
    #add-project-form-wrapper ~ * .stFormSubmitButton > button,
    div.row-widget.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
        background-color: #2e7d32 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[type="primary"]:hover,
    button.primary:hover,
    div[data-testid="stForm"] button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    #add-project-form-wrapper ~ * .stFormSubmitButton > button:hover,
    div.row-widget.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1b5e20 0%, #0d3815 100%) !important;
        background-color: #1b5e20 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    
    /* Override Streamlit's default red primary button color */
    [data-baseweb="button"][kind="primary"] {
        background-color: #2e7d32 !important;
        background-image: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
    }
    
    /* Target form buttons specifically */
    form button[type="submit"],
    form button.primary {
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
        color: white !important;
    }
    
    /* Text styling */
    .main-title {
        font-family: 'Verdana', sans-serif;
        font-size: 2.5rem;
        font-weight: bold;
        color: black;
        margin-top: 2rem;
        line-height: 1.2;
    }
    
    /* Container styling */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 2rem;
        background-color: white;
    }
    
    /* Headers green, regular text black with Verdana font */
    h1, h2, h3, h4, h5, h6 {
        color: #2e7d32 !important;
        font-family: 'Verdana', sans-serif !important;
    }
    .stMarkdown, .stText, p, div, span, label, td, th {
        color: black !important;
        font-family: 'Verdana', sans-serif !important;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: rgba(0, 0, 0, 0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="metric-container"] > div {
        color: black !important;
    }
    
    /* Make metric labels bold */
    [data-testid="metric-container"] label {
        font-weight: bold !important;
        color: #1b5e20 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: bold !important;
        color: #1b5e20 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(46, 125, 50, 0.08);
        color: #1b5e20 !important;
        border-radius: 5px;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    /* Make expander header text larger */
    .streamlit-expanderHeader p {
        font-size: 1.3rem !important;
        margin: 0 !important;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: rgba(46, 125, 50, 0.1);
        color: black;
        border: 1px solid rgba(46, 125, 50, 0.3);
        font-family: 'Verdana', sans-serif !important;
    }
    
    .stButton > button:hover {
        background-color: rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.5);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: black !important;
        background-color: rgba(46, 125, 50, 0.08);
        font-family: 'Verdana', sans-serif !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Make all text black */
    div[data-testid="stMarkdownContainer"] p {
        color: black !important;
        font-family: 'Verdana', sans-serif !important;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background-color: rgba(46, 125, 50, 0.08);
        color: black;
        font-family: 'Verdana', sans-serif !important;
    }
    
    /* Fix selectbox dropdown menu */
    div[data-baseweb="popover"] {
        background-color: #e8f5e9 !important;
    }
    
    div[data-baseweb="popover"] li {
        background-color: #e8f5e9 !important;
        color: black !important;
    }
    
    div[data-baseweb="popover"] li:hover {
        background-color: #e0e0e0 !important;
    }
    
    /* Fix selectbox input field */
    div[data-baseweb="select"] input {
        color: black !important;
        background-color: rgba(46, 125, 50, 0.08) !important;
    }
    
    /* Fix the dropdown options */
    [data-baseweb="menu"] {
        background-color: #e8f5e9 !important;
    }
    
    [data-baseweb="menu"] li {
        color: black !important;
    }
    
    [data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #e0e0e0 !important;
    }
    
    /* Additional Verdana font enforcement */
    .stSelectbox label, .stCheckbox label, .stRadio label {
        font-family: 'Verdana', sans-serif !important;
    }
    
    /* Metric values and labels */
    [data-testid="metric-container"] label {
        font-family: 'Verdana', sans-serif !important;
        font-weight: bold !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Verdana', sans-serif !important;
    }
    
    /* Additional targeting for metric labels */
    [data-testid="metric-container"] > div:first-child {
        font-weight: bold !important;
    }
    
    [data-testid="stMetricLabel"] p {
        font-weight: bold !important;
    }
    
    /* Disable image expansion on hover */
    [data-testid="stImage"] {
        pointer-events: none !important;
        cursor: default !important;
    }
    
    /* Remove the expand button that appears on images */
    [data-testid="StyledFullScreenButton"] {
        display: none !important;
    }
    
    /* Ensure images are not clickable */
    .stImage > img {
        pointer-events: none !important;
        cursor: default !important;
    }
    
    /* Force all metric labels to be bold */
    div[data-testid="metric-container"] div[data-testid="stMetricLabel"],
    div[data-testid="metric-container"] > div > div:first-child,
    div[data-testid="metric-container"] p:first-child {
        font-weight: bold !important;
    }
    
    /* Logo hover effects - applied to image only */
    .logo-container {
        position: relative;
        display: inline-block;
    }
    
    .logo-container img {
        transition: all 0.3s ease;
        cursor: pointer;
        display: block;
    }
    
    .logo-container:hover img {
        transform: translateY(-8px) scale(1.03);
    }
    
    /* Map container hover effect */
    .map-title-container {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .map-title-container:hover {
        transform: translateY(-8px) scale(1.03);
    }
    
    /* Project Management container hover effect */
    .project-management-container {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .project-management-container:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 15px 40px rgba(46, 125, 50, 0.25) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-right: 2px solid rgba(46, 125, 50, 0.2);
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }
    
    /* Sidebar text styling */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #1b5e20 !important;
        font-family: 'Verdana', sans-serif !important;
        text-align: center;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio > label {
        color: #333333 !important;
        font-family: 'Verdana', sans-serif !important;
    }
    
    /* Custom navigation buttons styling */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        gap: 8px;
        display: flex;
        flex-direction: column;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        color: #2c3e50 !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 0;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        font-weight: 500;
        text-align: center;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(46, 125, 50, 0.2);
        border-color: #4caf50;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-selected="true"] {
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
        color: white !important;
        border-color: #1b5e20;
        box-shadow: 0 4px 12px rgba(27, 94, 32, 0.3);
        font-weight: 600;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-selected="true"]:before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: #ffd700;
    }
    
    /* Hide radio button circles */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* Sidebar divider styling */
    section[data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(46, 125, 50, 0.3), transparent);
        margin: 1.5rem 0;
    }
</style>

<script>
    // Continuously remove sidebar toggle buttons with broken text
    setInterval(function() {
        var elements = document.querySelectorAll('*');
        elements.forEach(function(el) {
            if (el.textContent === 'keyboard_double_arrow_left' || 
                el.textContent === 'keyboard_double_arrow_right' ||
                el.textContent.includes('keyboard_double_arrow')) {
                el.style.display = 'none';
            }
        });
    }, 100);
</script>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    # Add DESRI logo in sidebar if available
    try:
        if os.path.exists('desri_logo2_cropped.png'):
            with open('desri_logo2_cropped.png', 'rb') as f:
                sidebar_logo_data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <img src="data:image/png;base64,{sidebar_logo_data}" 
                     style="width: 80%; max-width: 200px;" 
                     draggable="false">
            </div>
            """, unsafe_allow_html=True)
    except:
        pass
    
    # Navigation section with improved styling
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.15);
    '>
        <h2 style='
            color: #1b5e20;
            margin: 0;
            font-size: 1.5rem;
            font-weight: bold;
            letter-spacing: 1px;
        '>
            NAVIGATION
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Page selection with styled buttons
    st.markdown("""
    <style>
        /* Custom button styles for navigation */
        .nav-button {
            display: block;
            width: 100%;
            padding: 12px 20px;
            margin: 8px 0;
            background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
            color: white !important;
            text-align: center;
            text-decoration: none;
            font-weight: bold;
            font-size: 1rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .nav-button:hover {
            background: linear-gradient(135deg, #1b5e20 0%, #0d3815 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .nav-button-selected {
            background: linear-gradient(135deg, #1b5e20 0%, #0d3815 100%);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            transform: scale(1.02);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create navigation buttons
    if 'page' not in st.session_state:
        st.session_state.page = "Opposition Tracker"
    
    # Opposition Tracker button
    if st.button("**OPPOSITION TRACKER**", key="nav_tracker", use_container_width=True):
        st.session_state.page = "Opposition Tracker"
        st.rerun()
    
    # 2025 Report button  
    if st.button("**2025 REPORT**", key="nav_2025", use_container_width=True):
        st.session_state.page = "2025 Opposition Report"
        st.rerun()
    
    # Public Hearings Resources button
    if st.button("**PUBLIC HEARINGS RESOURCES**", key="nav_hearings", use_container_width=True):
        st.session_state.page = "Public Hearings Resources"
        st.rerun()
    
    # User Guide button
    if st.button("**📖 USER GUIDE**", key="nav_guide", use_container_width=True):
        st.session_state.page = "User Guide"
        st.rerun()
    
    # Get the current page
    page = st.session_state.page
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # About section with improved styling
    st.markdown("""
    <div style='
        background: rgba(255, 255, 255, 0.8);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #2e7d32;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    '>
        <h3 style='
            color: #1b5e20;
            margin: 0 0 0.8rem 0;
            font-size: 1.2rem;
            font-weight: bold;
        '>
            About This Hub
        </h3>
        <p style='
            color: #424242;
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.5;
        '>
            The DESRI Public Engagement Intelligence Hub monitors and analyzes community 
            opposition to renewable energy projects across the U.S.—with a focused lens 
            on the entire DESRI project portfolio. While only select team members previously 
            had direct access to our contracted Spark AI platform, this hub democratizes 
            critical opposition intelligence for our entire organization.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Spark AI Integration section - separate container
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #e3f2fd 0%, #e1f5fe 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #2196F3;
        box-shadow: 0 2px 6px rgba(33, 150, 243, 0.1);
        margin-top: 1rem;
    '>
        <p style='
            color: #0d47a1;
            margin: 0;
            font-size: 0.85rem;
            line-height: 1.5;
            font-weight: 500;
        '>
            🤖 <strong>Powered by Spark AI Integration:</strong> This platform features live integration 
            with Spark AI technology, automatically enriching project data with real-time sentiment 
            analysis, community feedback insights, and comprehensive opposition tracking when new 
            projects are added to the database.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

# Main content based on page selection
if 'page' not in locals():
    page = "Opposition Tracker"

# Initialize Supabase (needed for all pages)
supabase = init_supabase()

if page == "Opposition Tracker":
    # Header Section - Logo centered
    try:
        # Try to load the image if it exists
        if os.path.exists('desri_hub_logo.png'):
            # Create three columns with logo in the center (slightly wider middle column)
            col1, col2, col3 = st.columns([1, 0.5, 1])
            with col2:
                with open('desri_hub_logo.png', 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode()
                st.markdown(f"""
                <div style="text-align: center;">
                    <div class="logo-container" style="transform: scale(1.3);">
                        <img src="data:image/png;base64,{image_data}" 
                             style="width: 100%; max-width: 100%;" 
                             draggable="false">
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Placeholder for the logo - centered
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.markdown("""
                <div style="background-color: rgba(46,125,50,0.08); padding: 2rem; border-radius: 10px; text-align: center;">
                    <p style="color: #1b5e20; font-size: 1.2rem;">DESRI Logo</p>
                    <p style="color: #2e7d32; font-size: 0.9rem;">Public Engagement<br>Intelligence Hub</p>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Logo error: {e}")

    # Add some spacing after logo
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load data
    @st.cache_data(ttl=1)  # Set TTL to 1 second to ensure fresh data after modifications
    def load_data():
        try:
            # Try to load the processed data
            if os.path.exists('DESRI_PowerBI_Complete.xlsx'):
                df = pd.read_excel('DESRI_PowerBI_Complete.xlsx', sheet_name='Fact_Projects')
            elif os.path.exists('desri_public_opps_major_tracker_with_counties_corrected.xlsx'):
                df = pd.read_excel('desri_public_opps_major_tracker_with_counties_corrected.xlsx')
            elif os.path.exists('desri_public_opps_major_tracker_with_counties.xlsx'):
                df = pd.read_excel('desri_public_opps_major_tracker_with_counties.xlsx')
            else:
                # Create sample data for demonstration
                df = pd.DataFrame({
                    'Project': ['Sample Project 1', 'Sample Project 2'],
                    'State': ['CA', 'TX'],
                    'County': ['Los Angeles County', 'Harris County'],
                    'Sentiment': ['GOOD', 'MIXED'],
                    'Latitude': [34.0522, 29.7604],
                    'Longitude': [-118.2437, -95.3698]
                })
            
            # Merge with user-added projects from Supabase
            if supabase:
                user_projects = get_user_added_projects(supabase)
                if user_projects:
                    # Convert Supabase data to DataFrame
                    user_df = pd.DataFrame(user_projects)
                    # Rename columns to match expected format
                    column_mapping = {
                        'project': 'Project',
                        'state': 'State', 
                        'county': 'County',
                        'type': 'Type',
                        'status': 'Status',
                        'latitude': 'Latitude',
                        'longitude': 'Longitude',
                        'system_size_mw_ac': 'System Size (MW AC)',
                        'system_size_mw_dc': 'System Size (MW DC)',
                        'sentiment': 'Sentiment',
                        'sentiment_detail': 'Sentiment Detail',
                        'mentions_of_moratoria': 'Mentions of Moratoria',
                        'recent_projects': 'Recent Projects'
                    }
                    user_df = user_df.rename(columns=column_mapping)
                    # Add survey columns with proper names
                    # Map survey question columns to their full text
                    survey_questions = {
                        'survey_q1': 'Can you describe any initial public opposition to the project - including when it occurred, its tone, scale, and level of organization, and the permitting stage it emerged in? Who were the most vocal opponents and supporters (if any)? If there was little or no opposition, please describe your community interactions, including any key supporters or positive dynamics that helped ease the permitting process.',
                        'survey_q2': 'What were the most prominent concerns or recurring public fears raised by the community at this project? What type of approval(s) were being sought?',
                        'survey_q3': 'Regarding this project, what forms of community engagement were used, and were they helpful? Do you believe engagement made - or could have made - a positive difference in the project\'s outcome? If so, which approaches were or would have been most effective?',
                        'survey_q4': 'What were some of the most difficult or unexpected questions you\'ve been asked during public hearings, community meetings and/or public interactions regarding this project? How did you respond - or how do you wish you had responded?',
                        'survey_q5': 'If the project succeeded with minimal or manageable opposition, what do you think made the difference?',
                        'survey_q6': 'If opposition caused significant delay or failure, what factors do you believe contributed?',
                        'survey_q7': 'Did public opposition affect project timeline and to what degree?',
                        'survey_q8': '(OPTIONAL) Is there anything else you\'d like to share that didn\'t fit into the questions above?'
                    }
                    
                    for i in range(1, 9):
                        col_name = f'survey_q{i}'
                        if col_name in user_df.columns:
                            user_df[survey_questions[col_name]] = user_df[col_name]
                    # Combine the dataframes
                    df = pd.concat([df, user_df], ignore_index=True)
            
            # Also check for legacy CSV files (for backward compatibility)
            elif os.path.exists('user_added_projects.csv'):
                user_df = pd.read_csv('user_added_projects.csv')
                df = pd.concat([df, user_df], ignore_index=True)
            
            # Remove projects that have been marked for removal
            if supabase:
                removed_projects_data = get_removed_projects(supabase)
                if removed_projects_data:
                    removed_projects = [p['project'] for p in removed_projects_data]
                    df = df[~df['Project'].isin(removed_projects)]
            # Also check for legacy CSV file
            elif os.path.exists('removed_projects.csv'):
                removed_df = pd.read_csv('removed_projects.csv')
                removed_projects = removed_df['Project'].tolist()
                df = df[~df['Project'].isin(removed_projects)]
            
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()

    # Load the data
    df = load_data()

    if not df.empty:
        # Geographic View Section with AI Integration Notice
        st.markdown("""
        <div class='map-title-container' style='
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border: 2px solid #2e7d32;
            border-radius: 20px;
            padding: 2.5rem;
            margin: 2rem auto;
            max-width: 1200px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(46, 125, 50, 0.15);
            position: relative;
            overflow: hidden;
        '>
            <h2 style='
                color: #1b5e20;
                margin: 0;
                font-family: Verdana, sans-serif;
                font-size: 2.8rem;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(27, 94, 32, 0.1);
                letter-spacing: -0.5px;
            '>
                Public Opposition Map: Real-Time Community Sentiment Analysis
            </h2>
            <div style='
                width: 60%;
                height: 2px;
                background: linear-gradient(90deg, transparent, #2e7d32, transparent);
                margin: 1.5rem auto;
            '></div>
            <p style='
                color: black;
                margin: 0;
                font-family: Verdana, sans-serif;
                font-size: 1.2rem;
                font-weight: 500;
            '>
                Comprehensive visualization of community sentiment across renewable energy projects
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Map control options
        col1, col2, col3 = st.columns(3)
        with col1:
            cluster_markers = st.checkbox("Cluster nearby markers", value=False)
        with col2:
            basemap_option = st.selectbox(
                "Select Basemap",
                ["Dark Gray", "Satellite", "Topographic", "Streets", "Oceans"]
            )
    
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            import folium
            from streamlit_folium import st_folium
            from folium.plugins import Fullscreen, MiniMap, MarkerCluster
            
            # Prepare map data
            df_map = df.dropna(subset=['Latitude', 'Longitude'])
            
            # Create base map centered on US
            m = folium.Map(
                    location=[39.8283, -98.5795],  # Center of US
                    zoom_start=4,
                    tiles=None,
                    prefer_canvas=True,
                    zoom_control=True,
                    scrollWheelZoom=True,  # This enables scroll wheel zoom!
                    dragging=True,
                    doubleClickZoom=True,
                    touchZoom=True,
                    keyboard=True
            )
            
            # ArcGIS Basemap URLs
            arcgis_basemaps = {
                    "Dark Gray": {
                        "url": "https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
                        "attr": "Esri, HERE, Garmin, © OpenStreetMap contributors, and the GIS User Community"
                    },
                    "Satellite": {
                        "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                        "attr": "Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN"
                    },
                    "Topographic": {
                        "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
                        "attr": "Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN"
                    },
                    "Streets": {
                        "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
                        "attr": "Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong)"
                    },
                    "Oceans": {
                        "url": "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
                        "attr": "Esri, GEBCO, NOAA, National Geographic, Garmin, HERE, Geonames.org, and other contributors"
                    }
            }
            
            # Add selected basemap
            basemap = arcgis_basemaps[basemap_option]
            folium.TileLayer(
                    tiles=basemap["url"],
                    attr=basemap["attr"],
                    name=basemap_option,
                    overlay=False,
                    control=True
            ).add_to(m)
            
            # Add reference overlay for Dark Gray basemap
            if basemap_option == "Dark Gray":
                    folium.TileLayer(
                        tiles="https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
                        attr="Esri",
                        name="Labels",
                        overlay=True,
                        control=True
                    ).add_to(m)
            
            # Add controls
            Fullscreen(position='topleft').add_to(m)
            
            # Sentiment colors
            sentiment_colors = {
                    'GOOD': '#2ecc71',
                    'MIXED': '#f39c12',
                    'BAD': '#e74c3c',
                    'NO DATA': '#95a5a6'
            }
            
            # Create marker cluster if enabled
            if cluster_markers:
                    marker_cluster = MarkerCluster(
                        name='Projects',
                        overlay=True,
                        control=True,
                        show=True
                    ).add_to(m)
            
            # Add markers
            for idx, row in df_map.iterrows():
                    sentiment = row.get('Sentiment', 'NO DATA')
            
                    # Rich popup content
                    popup_html = f"""
                    <div style="font-family: Arial, sans-serif; width: 280px;">
                        <h3 style="margin: 0 0 10px 0; color: #2c3e50;">{row.get('Project', 'Unknown')}</h3>
                        <hr style="margin: 5px 0;">
                        <table style="width: 100%; font-size: 14px;">
                            <tr><td><b>Location:</b></td><td>{row.get('County', 'Unknown')}, {row.get('State', 'Unknown')}</td></tr>
                            <tr><td><b>Type:</b></td><td>{row.get('Type', 'N/A')}</td></tr>
                            <tr><td><b>Size:</b></td><td>{row.get('System Size (MW AC)', 'N/A')} MW</td></tr>
                            <tr><td><b>Sentiment:</b></td><td><span style="color: {sentiment_colors.get(sentiment)}; font-weight: bold;">{sentiment}</span></td></tr>
                            <tr><td><b>Status:</b></td><td>{row.get('Status', 'N/A')}</td></tr>
                        </table>
                        {f'<hr style="margin: 10px 0;"><p style="margin: 0; font-size: 12px;"><b>Notes:</b> {row.get("Opposition_Notes", "")}</p>' if pd.notna(row.get("Opposition_Notes")) and row.get("Opposition_Notes") else ''}
                    </div>
                    """
            
                    # Create circle marker
                    marker = folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=10,
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{row.get('Project', 'Unknown')} - {sentiment}",
                        color='white',
                        weight=2,
                        fillColor=sentiment_colors.get(sentiment, '#95a5a6'),
                        fillOpacity=0.8
                    )
            
                    # Add to cluster or directly to map
                    if cluster_markers:
                        marker.add_to(marker_cluster)
                    else:
                        marker.add_to(m)
            
            # Add legend
            legend_html = f'''
            <div style="position: fixed; 
                            bottom: 50px; left: 50px; width: 180px; 
                            background-color: rgba(255, 255, 255, 0.95);
                            border: 2px solid black;
                            z-index: 1000; font-size: 14px;
                            border-radius: 5px; padding: 15px;">
                    <p style="margin: 0 0 10px 0; font-weight: bold; color: black;">Sentiment Legend</p>
                    <p style="margin: 5px 0; color: black;"><span style="color: {sentiment_colors['GOOD']};">●</span> Good ({len(df_map[df_map['Sentiment'] == 'GOOD']) if 'Sentiment' in df_map.columns else 0})</p>
                    <p style="margin: 5px 0; color: black;"><span style="color: {sentiment_colors['MIXED']};">●</span> Mixed ({len(df_map[df_map['Sentiment'] == 'MIXED']) if 'Sentiment' in df_map.columns else 0})</p>
                    <p style="margin: 5px 0; color: black;"><span style="color: {sentiment_colors['BAD']};">●</span> Bad ({len(df_map[df_map['Sentiment'] == 'BAD']) if 'Sentiment' in df_map.columns else 0})</p>
                    <p style="margin: 5px 0; color: black;"><span style="color: {sentiment_colors['NO DATA']};">●</span> No Data ({len(df_map[df_map['Sentiment'] == 'NO DATA']) if 'Sentiment' in df_map.columns else 0})</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Add layer control
            folium.LayerControl(position='topright').add_to(m)
            
            # Display the map and capture clicked marker
            map_data = st_folium(
                m, 
                height=600,  # Reduced height slightly to minimize viewport usage
                width=None, 
                returned_objects=["last_object_clicked", "last_object_clicked_tooltip"], 
                key="map",
                use_container_width=True
            )
            
        else:
            st.info("Geographic data not available")
    
        # Summary metrics - moved below map
        # Add custom CSS to reduce spacing
        st.markdown("""
        <style>
            /* Reduce spacing between map and metrics */
            div[data-testid="stMetricValue"] {
                margin-top: 0 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            st.metric("Active Projects", len(df), delta=None, delta_color="off", help="Total number of projects being monitored")
    
        with col2:
            states_count = df['State'].nunique() if 'State' in df.columns else 0
            st.metric("Geographic Coverage", f"{states_count} States", delta=None, delta_color="off", help="Number of states with active projects")
    
        with col3:
            if 'Sentiment' in df.columns:
                good_sentiment = len(df[df['Sentiment'] == 'GOOD'])
                st.metric("Favorable Sentiment", good_sentiment, delta=None, delta_color="off", help="Projects with positive community reception")
            else:
                st.metric("Favorable Sentiment", "N/A", delta=None, delta_color="off")
    
        with col4:
            if 'Sentiment' in df.columns:
                bad_sentiment = len(df[df['Sentiment'] == 'BAD'])
                st.metric("Opposition Cases", bad_sentiment, delta=None, delta_color="off", help="Projects facing significant community resistance")
            else:
                st.metric("Opposition Cases", "N/A", delta=None, delta_color="off")
    
        # Add minimal spacing between sections
        st.markdown("---")
    
        # Project Database Section (moved from tab3)
        st.markdown("### Comprehensive Project Intelligence Database", unsafe_allow_html=True)
        
        # Check if a project was clicked on the map
        clicked_project_name = None
        if 'map_data' in locals() and map_data:
            # Check for tooltip data in the correct location
            if 'last_object_clicked_tooltip' in map_data and map_data['last_object_clicked_tooltip']:
                tooltip_text = map_data['last_object_clicked_tooltip']
                if ' - ' in tooltip_text:
                    clicked_project_name = tooltip_text.split(' - ')[0].strip()
                    # Remove debug output once it's working
                    # st.write("Debug - Extracted project name:", clicked_project_name)
    
        # Add search bar for project name with autocomplete
        # Get all unique project names for the dropdown
        all_project_names = [""] + sorted(df['Project'].dropna().unique().tolist()) if 'Project' in df.columns else [""]
        
        # Pre-select clicked project if available
        default_index = 0
        if clicked_project_name and clicked_project_name in all_project_names:
            default_index = all_project_names.index(clicked_project_name)
        
        # Use selectbox with search functionality
        project_search = st.selectbox(
            "🔍 Project Intelligence Search",
            options=all_project_names,
            index=default_index,
            placeholder="Type to search or select a project...",
            help="Begin typing to filter projects or click a marker on the interactive map for quick selection"
        )
    
        # Add filters
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
        with col1:
            if 'State' in df.columns:
                state_values = [str(x) for x in df['State'].dropna().unique()]
                state_filter = st.selectbox("Geographic Filter", ["All States"] + sorted(state_values))
    
        with col2:
            if 'Sentiment' in df.columns:
                sentiment_values = [str(x) for x in df['Sentiment'].dropna().unique()]
                sentiment_filter = st.selectbox("Community Sentiment", ["All Sentiments"] + sorted(sentiment_values))
    
        with col3:
            if 'Type' in df.columns:
                type_values = [str(x) for x in df['Type'].dropna().unique()]
                type_filter = st.selectbox("Project Category", ["All Types"] + sorted(type_values))
        
        with col4:
            survey_filter = st.selectbox("Assessment Status", ["All Projects", "Assessed ✅", "Pending Assessment ❌"])
        
        with col5:
            # Add a clear filters button
            if st.button("Clear All Filters"):
                st.rerun()
    
        # Apply filters
        filtered_df = df.copy()
        
        # Get list of projects with surveys for filtering
        projects_with_surveys_filter = set()
        
        if supabase:
            user_projects = get_user_added_projects(supabase)
            for proj in user_projects:
                has_survey = any([
                    proj.get('survey_q1'),
                    proj.get('survey_q2'),
                    proj.get('survey_q3'),
                    proj.get('survey_q4'),
                    proj.get('survey_q5'),
                    proj.get('survey_q6'),
                    proj.get('survey_q7'),
                    proj.get('survey_q8')
                ])
                if has_survey:
                    projects_with_surveys_filter.add(proj['project'])
        
        # Also check main dataframe for survey columns
        survey_cols = [col for col in df.columns if 'survey' in col.lower() or 'question' in col.lower()]
        if survey_cols:
            for _, row in df.iterrows():
                if any(pd.notna(row.get(col)) for col in survey_cols):
                    projects_with_surveys_filter.add(row['Project'])
        
        # Apply project name search filter
        if project_search:
            filtered_df = filtered_df[filtered_df['Project'].str.contains(project_search, case=False, na=False)]
        
        if 'state_filter' in locals() and state_filter != "All States":
            filtered_df = filtered_df[filtered_df['State'].astype(str) == state_filter]
        if 'sentiment_filter' in locals() and sentiment_filter != "All Sentiments":
            filtered_df = filtered_df[filtered_df['Sentiment'].astype(str) == sentiment_filter]
        if 'type_filter' in locals() and type_filter != "All Types":
            filtered_df = filtered_df[filtered_df['Type'].astype(str) == type_filter]
        
        # Apply survey filter
        if 'survey_filter' in locals():
            if survey_filter == "Assessed ✅":
                filtered_df = filtered_df[filtered_df['Project'].isin(projects_with_surveys_filter)]
            elif survey_filter == "Pending Assessment ❌":
                filtered_df = filtered_df[~filtered_df['Project'].isin(projects_with_surveys_filter)]
    
        # Display filtered data
        st.markdown(f"Found {len(filtered_df)} projects", unsafe_allow_html=True)
        
        # Check if user has searched, filtered, or clicked a marker
        has_search_or_filter = (
            project_search or 
            clicked_project_name or
            ('state_filter' in locals() and state_filter != "All States") or
            ('sentiment_filter' in locals() and sentiment_filter != "All Sentiments") or
            ('type_filter' in locals() and type_filter != "All Types") or
            ('survey_filter' in locals() and survey_filter != "All Projects")
        )
        
        if not has_search_or_filter:
            st.info("👆 Search for a project by name or use the filters above to view projects. You can also click on a project marker on the map.")
        else:
            # Show message if project was selected from map
            if clicked_project_name:
                st.success(f"📍 Selected from map: {clicked_project_name}")
            
            # Show data in an expandable format
            st.markdown(f"Showing {min(len(filtered_df), 20)} of {len(filtered_df)} projects")
            
            # If there's a clicked project, show it first
            displayed_projects = []
            if clicked_project_name:
                # Find the clicked project and add it first
                clicked_rows = filtered_df[filtered_df['Project'] == clicked_project_name]
                if not clicked_rows.empty:
                    displayed_projects.append(clicked_rows.iloc[0])
                
                # Add other projects (excluding the clicked one to avoid duplication)
                other_projects = filtered_df[filtered_df['Project'] != clicked_project_name].head(19)
                for idx, row in other_projects.iterrows():
                    displayed_projects.append(row)
            else:
                # No clicked project, just show top 20
                for idx, row in filtered_df.head(20).iterrows():
                    displayed_projects.append(row)
            
            # First, get list of projects that have survey data
            projects_with_surveys = set()
            
            if supabase:
                user_projects = get_user_added_projects(supabase)
                for proj in user_projects:
                    # Check if project has any survey responses
                    has_survey = any([
                        proj.get('survey_q1'),
                        proj.get('survey_q2'),
                        proj.get('survey_q3'),
                        proj.get('survey_q4'),
                        proj.get('survey_q5'),
                        proj.get('survey_q6'),
                        proj.get('survey_q7'),
                        proj.get('survey_q8')
                    ])
                    if has_survey:
                        projects_with_surveys.add(proj['project'])
            
            # Also check main dataframe for survey columns
            survey_cols = [col for col in df.columns if 'survey' in col.lower() or 'question' in col.lower()]
            if survey_cols:
                for _, check_row in df.iterrows():
                    if any(pd.notna(check_row.get(col)) for col in survey_cols):
                        projects_with_surveys.add(check_row['Project'])
            
            # Display the projects
            for idx, row in enumerate(displayed_projects):
                project_name = row.get('Project', 'Unknown Project')
                state = row.get('State', 'Unknown State')
                
                # Check if this project has survey data
                has_survey = project_name in projects_with_surveys
                survey_badge = "✅ Has Survey" if has_survey else "📝 Needs Survey"
                survey_color = "#2ecc71" if has_survey else "#e74c3c"
                
                # Create a clear separator between projects
                if idx > 0:
                    st.markdown("""
                    <div style='
                        height: 3px;
                        background: linear-gradient(90deg, transparent, #2e7d32, transparent);
                        margin: 3rem 0;
                    '></div>
                    """, unsafe_allow_html=True)
                
                # Project header with number and survey status
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                    border-left: 5px solid #2e7d32;
                    padding: 1.5rem;
                    border-radius: 10px;
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 6px rgba(46, 125, 50, 0.1);
                    position: relative;
                '>
                    <div style='
                        position: absolute;
                        top: 1rem;
                        right: 1rem;
                        background: {survey_color};
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.9rem;
                        font-weight: bold;
                    '>
                        {survey_badge}
                    </div>
                    <h2 style='
                        color: #1b5e20;
                        margin: 0;
                        font-size: 1.8rem;
                        font-weight: bold;
                        padding-right: 150px;
                    '>
                        📍 Project {idx + 1}: {project_name}
                    </h2>
                    <p style='
                        color: #2e7d32;
                        margin: 0.5rem 0 0 0;
                        font-size: 1.1rem;
                    '>
                        Location: {state}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Get sentiment color
                sentiment_value = row.get('Sentiment', 'N/A')
                sentiment_color_map = {
                    'GOOD': '#2ecc71',
                    'MIXED': '#f39c12', 
                    'BAD': '#e74c3c',
                    'NO DATA': '#95a5a6'
                }
                sentiment_color = sentiment_color_map.get(sentiment_value, '#95a5a6')
                
                # Project Overview Card
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                        <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 1.4rem;">📊 Project Overview</h3>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <span style="color: #7f8c8d; font-size: 0.85rem;">📍 Location</span>
                                <p style="color: #2c3e50; font-weight: bold; margin: 5px 0;">{row.get('County', 'N/A')}</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <span style="color: #7f8c8d; font-size: 0.85rem;">⚡ Type</span>
                                <p style="color: #2c3e50; font-weight: bold; margin: 5px 0;">{row.get('Type', 'N/A')}</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <span style="color: #7f8c8d; font-size: 0.85rem;">📈 Status</span>
                                <p style="color: #2c3e50; font-weight: bold; margin: 5px 0;">{row.get('Status', 'N/A')}</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <span style="color: #7f8c8d; font-size: 0.85rem;">😊 Sentiment</span>
                                <p style="color: {sentiment_color}; font-weight: bold; margin: 5px 0;">{sentiment_value}</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <span style="color: #7f8c8d; font-size: 0.85rem;">⚙️ AC Size</span>
                                <p style="color: #2c3e50; font-weight: bold; margin: 5px 0;">{row.get('System Size (MW AC)', 'N/A')} MW</p>
                            </div>
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <span style="color: #7f8c8d; font-size: 0.85rem;">🔌 DC Size</span>
                                <p style="color: #2c3e50; font-weight: bold; margin: 5px 0;">{row.get('System Size (MW DC)', 'N/A')} MW</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Sentiment Details
                if 'Sentiment Detail' in row and pd.notna(row['Sentiment Detail']):
                    sentiment_text = str(row['Sentiment Detail'])
                    # Process text to handle markdown-style formatting
                    formatted_text = sentiment_text
                    # Replace **text** with HTML bold tags
                    import re
                    formatted_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', formatted_text)
                    # Split by line breaks or bullet points
                    sentiment_items = formatted_text.split('\n\n') if '\n\n' in formatted_text else formatted_text.split(' - ')
                    
                    st.markdown("""
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #2196f3;">
                        <h4 style="color: #1565c0; margin: 0 0 15px 0;">💬 Sentiment Analysis</h4>
                    """, unsafe_allow_html=True)
                    
                    for item in sentiment_items:
                        if item.strip():
                            # Clean up the item and format it properly
                            item_text = item.strip()
                            if item_text.startswith('-'):
                                item_text = item_text[1:].strip()
                            
                            st.markdown(f"""
                            <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 12px; line-height: 1.6;">
                                <p style="color: #2c3e50; margin: 0;">
                                    {item_text}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                # Mentions of Moratoria
                if 'Mentions of Moratoria' in row and pd.notna(row['Mentions of Moratoria']):
                    moratoria_text = str(row['Mentions of Moratoria'])
                    # Process text to handle markdown-style formatting
                    formatted_moratoria = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', moratoria_text)
                    
                    # Check if there are actual moratoria mentions or if it says "No mentions"
                    has_moratoria = not ('no mention' in moratoria_text.lower() or 'none' in moratoria_text.lower())
                    
                    if has_moratoria:
                        # Orange styling for actual moratoria mentions (warning)
                        st.markdown(f"""
                        <div style="background: #fff3e0; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #ff9800;">
                            <h4 style="color: #e65100; margin: 0 0 15px 0;">⚠️ Moratoria Mentions</h4>
                            <div style="background: white; padding: 15px; border-radius: 8px; line-height: 1.6;">
                                <p style="color: #2c3e50; margin: 0;">
                                    {formatted_moratoria}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Blue styling for no moratoria mentions (informational)
                        st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #2196f3;">
                            <h4 style="color: #1565c0; margin: 0 0 15px 0;">✓ Moratoria Status</h4>
                            <div style="background: white; padding: 15px; border-radius: 8px; line-height: 1.6;">
                                <p style="color: #2c3e50; margin: 0;">
                                    {formatted_moratoria}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                # Recent Projects
                if 'Recent Projects' in row and pd.notna(row['Recent Projects']):
                        st.markdown("""
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #2196f3;">
                            <h4 style="color: #1565c0; margin: 0 0 15px 0;">🏗️ Recent Projects</h4>
                        """, unsafe_allow_html=True)
                        projects_text = str(row['Recent Projects'])
                        # Process text to handle markdown-style formatting
                        formatted_projects = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', projects_text)
                        # Split by semicolon or newline
                        project_items = formatted_projects.split(';') if ';' in formatted_projects else formatted_projects.split('\n')
                        
                        for project in project_items:
                            if project.strip():
                                project_text = project.strip()
                                # Check if this looks like a date entry (contains date pattern)
                                if '(' in project_text and ')' in project_text:
                                    # Extract date/source and content
                                    parts = project_text.split(':', 1)
                                    if len(parts) == 2:
                                        header = parts[0].strip()
                                        content = parts[1].strip()
                                        st.markdown(f"""
                                        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 12px;">
                                            <div style="color: #1565c0; font-weight: bold; margin-bottom: 8px;">{header}</div>
                                            <p style="color: #2c3e50; margin: 0; line-height: 1.6;">{content}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 12px;">
                                            <p style="color: #2c3e50; margin: 0; line-height: 1.6;">{project_text}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 12px;">
                                        <p style="color: #2c3e50; margin: 0; line-height: 1.6;">{project_text}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                # Survey Questions and Answers - properly mapped to actual column names
                survey_questions = [
                        ("🎯 Initial Public Opposition", "Can you describe any initial public opposition to the project — including when it occurred, its tone, scale, and level of organization, and the permitting stage it emerged in? Who were the most vocal opponents and supporters (if any)? If there was little or no opposition, please describe your community interactions, including any key supporters or positive dynamics that helped ease the permitting process."),
                        ("⚡ Prominent Concerns", "What were the most prominent concerns or recurring public fears raised by the community at this project? What type of approval(s) were being sought? ("),
                        ("🤝 Community Engagement", "Regarding this project, what forms of community engagement were used, and were they helpful? Do you believe engagement made — or could have made — a positive difference in the project's outcome? If so, which approaches were or would have been most effective?"),
                        ("❓ Difficult Questions", "What were some of the most difficult or unexpected questions you've been asked during public hearings, community meetings and/or public interactions regarding this project? How did you respond — or how do you wish you had responded?"),
                        ("✅ Success Factors", "If the project succeeded with minimal or manageable opposition, what do you think made the difference?"),
                        ("❌ Failure Factors", "If opposition caused significant delay or failure, what factors do you believe contributed?"),
                        ("⏱️ Timeline Impact", "Did public opposition affect project timeline and to what degree?"),
                        ("💭 Additional Comments", "(OPTIONAL) Is there anything else you'd like to share that didn't fit into the questions above?")
                    ]
                    
                # Check if any survey answers exist
                has_survey_data = False
                for _, col_name in survey_questions:
                    if col_name in row and pd.notna(row[col_name]):
                        has_survey_data = True
                        break
                
                if has_survey_data:
                        st.markdown("""
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                            <h3 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 1.4rem;">📋 Community Engagement Survey Responses</h3>
                        """, unsafe_allow_html=True)
                        
                        for title, col_name in survey_questions:
                            if col_name in row and pd.notna(row[col_name]):
                                answer_text = str(row[col_name])
                                st.markdown(f"""
                                <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <h5 style="color: #3498db; margin: 0 0 10px 0; font-size: 1.1rem;">{title}</h5>
                                    <p style="color: #7f8c8d; font-style: italic; margin: 0 0 15px 0; font-size: 0.9rem; line-height: 1.4;">
                                        {col_name}
                                    </p>
                                    <div style="background: #f1f8ff; padding: 15px; border-radius: 8px; border-left: 3px solid #3498db;">
                                        <p style="color: #2c3e50; margin: 0; line-height: 1.6;">
                                            {answer_text}
                                        </p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Opposition Notes (if still exists in data)
                if 'Opposition_Notes' in row and pd.notna(row['Opposition_Notes']):
                    st.markdown(f"""
                    <div style="background: #fce4ec; padding: 20px; border-radius: 12px; margin-top: 20px; border-left: 4px solid #e91e63;">
                        <h4 style="color: #880e4f; margin: 0 0 10px 0;">📝 Opposition Notes</h4>
                        <p style="color: #2c3e50; margin: 0; line-height: 1.6;">
                            {row['Opposition_Notes']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Project Management Section
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='project-management-container' style='
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border: 2px solid #2e7d32;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 1200px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(46, 125, 50, 0.15);
            position: relative;
            overflow: hidden;
        '>
            <h2 style='
                color: #1b5e20;
                margin: 0;
                font-size: 2rem;
                font-weight: bold;
            '>
                🔧 Project Management
            </h2>
            <p style='
                color: black;
                margin: 0.5rem 0 0 0;
                font-size: 1rem;
            '>
                Add or remove projects from the database
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for Add, Remove, and Restore
        tab1, tab2, tab3, tab4 = st.tabs(["➕ Add New Project", "🗑️ Remove Project", "♻️ Restore Projects", "📝 Add/Edit Survey"])
        
        with tab1:
            st.markdown("### Add New Project")
            
            # AI Integration and DESRI Stories Notice
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                border-left: 4px solid #2196F3;
                padding: 1rem 1.2rem;
                margin-bottom: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
            '>
                <p style='
                    color: #0d47a1;
                    margin: 0 0 0.8rem 0;
                    font-family: Verdana, sans-serif;
                    font-size: 0.95rem;
                    line-height: 1.5;
                '>
                    <strong>🤖 Spark AI + DESRI Development Stories:</strong> This platform uniquely combines 
                    AI-powered insights with real human experiences. New projects are automatically enriched with 
                    Spark AI's sentiment analysis and opposition data, while the survey section below allows you 
                    to add DESRI's own development stories and on-the-ground experiences.
                </p>
                <p style='
                    color: #0d47a1;
                    margin: 0;
                    font-family: Verdana, sans-serif;
                    font-size: 0.88rem;
                    line-height: 1.4;
                    font-style: italic;
                '>
                    This dual approach provides a comprehensive view: AI intelligence shows what communities are 
                    saying, while our surveys capture how DESRI teams navigated these challenges—creating a 
                    powerful knowledge base of both data and experience.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add wrapper div for Add Project form styling
            st.markdown('<div id="add-project-form-wrapper">', unsafe_allow_html=True)
            
            with st.form("add_project_form"):
                st.markdown("#### Basic Project Information")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_project_name = st.text_input("Project Name*", placeholder="e.g., Solar Farm X")
                    new_state = st.text_input("State Code*", placeholder="e.g., CA, TX", max_chars=2)
                    new_county = st.text_input("County*", placeholder="e.g., Los Angeles County")
                
                with col2:
                    new_type = st.selectbox("Type*", ["Solar", "Wind", "Storage", "Transmission", "Hybrid"])
                    new_status = st.selectbox("Status*", ["Early Stage Development", "Development", "Construction", "Operating", "On Hold"])
                    new_latitude = st.number_input("Latitude*", min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f")
                
                with col3:
                    new_dc_size = st.number_input("DC Size (MW)", min_value=0.0, step=0.1, format="%.1f")
                    new_ac_size = st.number_input("AC Size (MW)", min_value=0.0, step=0.1, format="%.1f")
                    new_longitude = st.number_input("Longitude*", min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f")
                
                st.markdown("---")
                st.markdown("#### DESRI Development Stories & Community Engagement (Optional)")
                st.markdown("*Share your team's on-the-ground experiences and lessons learned—complementing AI data with human insights:*")
                
                # Survey questions
                survey_q1 = st.text_area(
                    "Initial Public Opposition",
                    placeholder="Describe any initial public opposition, its tone, scale, organization level, and permitting stage. Include vocal opponents/supporters or describe positive community interactions if there was little opposition.",
                    height=100,
                    help="Can you describe any initial public opposition to the project?"
                )
                
                survey_q2 = st.text_area(
                    "Prominent Concerns",
                    placeholder="What were the most prominent concerns or recurring public fears? What type of approval(s) were being sought?",
                    height=80
                )
                
                survey_q3 = st.text_area(
                    "Community Engagement",
                    placeholder="What forms of community engagement were used? Were they helpful? Which approaches were most effective?",
                    height=80
                )
                
                survey_q4 = st.text_area(
                    "Difficult Questions",
                    placeholder="What difficult or unexpected questions were asked during public hearings? How did you respond?",
                    height=80
                )
                
                survey_q5 = st.text_area(
                    "Success Factors",
                    placeholder="If the project succeeded with minimal opposition, what made the difference?",
                    height=80
                )
                
                survey_q6 = st.text_area(
                    "Failure Factors",
                    placeholder="If opposition caused delays or failure, what factors contributed?",
                    height=80
                )
                
                survey_q7 = st.text_area(
                    "Timeline Impact",
                    placeholder="Did public opposition affect the project timeline? To what degree?",
                    height=80
                )
                
                survey_q8 = st.text_area(
                    "Additional Comments",
                    placeholder="Any additional information you'd like to share?",
                    height=80
                )
                
                submitted = st.form_submit_button("Add Project", type="primary")
                
                if submitted:
                    if new_project_name and new_state and new_county and new_latitude != 0 and new_longitude != 0:
                        # Load sentiment data from SparkAI files
                        sentiment_data = None
                        spark_file_pattern = f"us_public_opposition_sparkai/spark_bulk_report_{new_state}_counties_*.csv"
                        
                        import glob
                        spark_files = glob.glob(spark_file_pattern)
                        
                        if spark_files:
                            try:
                                spark_df = pd.read_csv(spark_files[0])
                                # Look for matching county
                                county_match = spark_df[spark_df['County'].str.contains(new_county.replace(' County', ''), case=False, na=False)]
                                if not county_match.empty:
                                    sentiment_row = county_match.iloc[0]
                                    sentiment_data = {
                                        'Sentiment': sentiment_row.get('Sentiment', sentiment_row.get('Overall_Sentiment', 'NO DATA')),
                                        'Sentiment Detail': sentiment_row.get('Sentiment Detail', sentiment_row.get('Summary', '')),
                                        'Mentions of Moratoria': sentiment_row.get('Mentions of Moratoria', sentiment_row.get('Moratoria_Mentions', 'No mentions of moratoria')),
                                        'Recent Projects': sentiment_row.get('Recent Projects', sentiment_row.get('Recent_Projects', ''))
                                    }
                            except:
                                pass
                        
                        # Create new project entry for Supabase
                        new_project = {
                            'project': new_project_name,
                            'state': new_state.upper(),
                            'county': new_county,
                            'type': new_type,
                            'status': new_status,
                            'latitude': new_latitude,
                            'longitude': new_longitude,
                            'system_size_mw_ac': new_ac_size if new_ac_size > 0 else None,
                            'system_size_mw_dc': new_dc_size if new_dc_size > 0 else None,
                            'sentiment': sentiment_data.get('Sentiment', 'NO DATA') if sentiment_data else 'NO DATA',
                            'sentiment_detail': sentiment_data.get('Sentiment Detail', '') if sentiment_data else '',
                            'mentions_of_moratoria': sentiment_data.get('Mentions of Moratoria', '') if sentiment_data else '',
                            'recent_projects': sentiment_data.get('Recent Projects', '') if sentiment_data else '',
                            'survey_q1': survey_q1 if survey_q1 else None,
                            'survey_q2': survey_q2 if survey_q2 else None,
                            'survey_q3': survey_q3 if survey_q3 else None,
                            'survey_q4': survey_q4 if survey_q4 else None,
                            'survey_q5': survey_q5 if survey_q5 else None,
                            'survey_q6': survey_q6 if survey_q6 else None,
                            'survey_q7': survey_q7 if survey_q7 else None,
                            'survey_q8': survey_q8 if survey_q8 else None
                        }
                        
                        # Save to Supabase
                        if supabase:
                            success = add_user_project(supabase, new_project)
                            if success:
                                st.success(f"✅ Project '{new_project_name}' added successfully to cloud database!")
                                st.cache_data.clear()  # Clear cache to ensure fresh data
                                st.rerun()
                            else:
                                st.error("Failed to add project to database. Please try again.")
                        else:
                            # Fallback to CSV if Supabase is not configured
                            st.warning("⚠️ Supabase not configured. Saving to local file (won't work on Streamlit Cloud)")
                            # Legacy CSV code for local testing
                            user_projects_file = 'user_added_projects.csv'
                            new_project_csv = {
                                'Project': new_project_name,
                                'State': new_state.upper(),
                                'County': new_county,
                                'Type': new_type,
                                'Status': new_status,
                                'Latitude': new_latitude,
                                'Longitude': new_longitude,
                                'System Size (MW AC)': new_ac_size if new_ac_size > 0 else None,
                                'System Size (MW DC)': new_dc_size if new_dc_size > 0 else None,
                                'Sentiment': sentiment_data.get('Sentiment', 'NO DATA') if sentiment_data else 'NO DATA',
                                'Sentiment Detail': sentiment_data.get('Sentiment Detail', '') if sentiment_data else '',
                                'Mentions of Moratoria': sentiment_data.get('Mentions of Moratoria', '') if sentiment_data else '',
                                'Recent Projects': sentiment_data.get('Recent Projects', '') if sentiment_data else ''
                            }
                            
                            if os.path.exists(user_projects_file):
                                user_df = pd.read_csv(user_projects_file)
                                user_df = pd.concat([user_df, pd.DataFrame([new_project_csv])], ignore_index=True)
                            else:
                                user_df = pd.DataFrame([new_project_csv])
                            
                            user_df.to_csv(user_projects_file, index=False)
                            st.success(f"✅ Project '{new_project_name}' added locally!")
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.error("Please fill in all required fields (*)")
            
            # Close the Add Project form wrapper div
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### Remove Existing Project")
            
            # Use the already-loaded df which includes user projects and excludes removed ones
            all_projects_list = []
            
            if not df.empty:
                all_projects_list = df['Project'].tolist()
            
            if all_projects_list:
                project_to_remove = st.selectbox(
                    "Select project to remove:",
                    [""] + sorted(all_projects_list),
                    help="Select a project from the dropdown to remove it from the database"
                )
                
                if project_to_remove:
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("🗑️ Remove Project", type="secondary"):
                            if supabase:
                                # Add ANY project (user-added or default) to the removed list
                                # This makes all projects restorable instead of permanently deleting them
                                success, message = remove_project(supabase, project_to_remove)
                                if success:
                                    st.success(f"✅ Project '{project_to_remove}' removed successfully! (Can be restored later)")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.warning(f"⚠️ {message}")
                            else:
                                # Fallback to CSV for local testing
                                st.warning("⚠️ Supabase not configured. Using local file (won't work on Streamlit Cloud)")
                                
                                # Add ANY project to removed list (don't delete user-added projects)
                                removed_projects_file = 'removed_projects.csv'
                                removed = False
                                
                                if os.path.exists(removed_projects_file):
                                    removed_df = pd.read_csv(removed_projects_file)
                                    if project_to_remove not in removed_df['Project'].values:
                                        removed_df = pd.concat([removed_df, pd.DataFrame({'Project': [project_to_remove]})], ignore_index=True)
                                        removed_df.to_csv(removed_projects_file, index=False)
                                        removed = True
                                    else:
                                        st.warning(f"⚠️ Project '{project_to_remove}' has already been removed.")
                                else:
                                    removed_df = pd.DataFrame({'Project': [project_to_remove]})
                                    removed_df.to_csv(removed_projects_file, index=False)
                                    removed = True
                                
                                if removed:
                                    st.success(f"✅ Project '{project_to_remove}' removed! (Can be restored later)")
                                    st.cache_data.clear()
                                    st.rerun()
            else:
                st.info("No projects available to remove.")
        
        with tab3:
            st.markdown("### Restore Removed Projects")
            
            if supabase:
                removed_projects = get_removed_projects(supabase)
                
                if removed_projects:
                    removed_list = [p['project'] for p in removed_projects]
                    st.info(f"📌 {len(removed_list)} project(s) have been removed and can be restored.")
                    
                    project_to_restore = st.selectbox(
                        "Select project to restore:",
                        [""] + sorted(removed_list),
                        help="Select a project from the dropdown to restore it to the database"
                    )
                    
                    if project_to_restore:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if st.button("♻️ Restore Project", type="primary"):
                                success = restore_project(supabase, project_to_restore)
                                if success:
                                    st.success(f"✅ Project '{project_to_restore}' restored successfully!")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("Failed to restore project.")
                    
                    # Option to restore all
                    st.markdown("---")
                    if st.button("♻️ Restore All Projects", type="secondary"):
                        success = restore_all_projects(supabase)
                        if success:
                            st.success(f"✅ All {len(removed_list)} projects restored successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Failed to restore all projects.")
                else:
                    st.info("No removed projects to restore.")
            else:
                # Fallback to CSV for local testing
                if os.path.exists('removed_projects.csv'):
                    removed_df = pd.read_csv('removed_projects.csv')
                    removed_list = removed_df['Project'].tolist()
                    
                    if removed_list:
                        st.info(f"📌 {len(removed_list)} project(s) removed (local mode).")
                        
                        project_to_restore = st.selectbox(
                            "Select project to restore:",
                            [""] + sorted(removed_list),
                            help="Select a project to restore"
                        )
                        
                        if project_to_restore:
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col2:
                                if st.button("♻️ Restore Project", type="primary"):
                                    removed_df = removed_df[removed_df['Project'] != project_to_restore]
                                    if len(removed_df) > 0:
                                        removed_df.to_csv('removed_projects.csv', index=False)
                                    else:
                                        os.remove('removed_projects.csv')
                                    
                                    st.success(f"✅ Project '{project_to_restore}' restored locally!")
                                    st.cache_data.clear()
                                    st.rerun()
                        
                        # Option to restore all
                        st.markdown("---")
                        if st.button("♻️ Restore All Projects", type="secondary"):
                            os.remove('removed_projects.csv')
                            st.success(f"✅ All {len(removed_list)} projects restored locally!")
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.info("No removed projects to restore.")
                else:
                    st.info("No removed projects to restore.")
        
        with tab4:
            st.markdown("### Add or Edit Survey Responses")
            st.info("📋 Add survey responses to any existing project or edit existing responses.")
            
            # Get all projects and check which have surveys
            projects_with_survey_status = []
            
            if not df.empty:
                # Get list of projects that have survey data
                projects_with_surveys = set()
                
                if supabase:
                    user_projects = get_user_added_projects(supabase)
                    for proj in user_projects:
                        # Check if project has any survey responses
                        has_survey = any([
                            proj.get('survey_q1'),
                            proj.get('survey_q2'),
                            proj.get('survey_q3'),
                            proj.get('survey_q4'),
                            proj.get('survey_q5'),
                            proj.get('survey_q6'),
                            proj.get('survey_q7'),
                            proj.get('survey_q8')
                        ])
                        if has_survey:
                            projects_with_surveys.add(proj['project'])
                
                # Also check main dataframe for survey columns
                survey_cols = [col for col in df.columns if 'survey' in col.lower() or 'question' in col.lower()]
                if survey_cols:
                    for _, row in df.iterrows():
                        if any(pd.notna(row.get(col)) for col in survey_cols):
                            projects_with_surveys.add(row['Project'])
                
                # Create list with survey indicators
                for project in df['Project'].tolist():
                    if project in projects_with_surveys:
                        projects_with_survey_status.append(f"✅ {project} (Has survey)")
                    else:
                        projects_with_survey_status.append(f"❌ {project} (No survey)")
            
            if projects_with_survey_status:
                # Add search and filter options
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    search_term = st.text_input(
                        "🔍 Search projects by name:",
                        placeholder="Type to search...",
                        key="survey_search"
                    )
                
                with col2:
                    filter_option = st.selectbox(
                        "Filter by survey status:",
                        ["All Projects", "Has Survey ✅", "No Survey ❌"],
                        key="survey_filter"
                    )
                
                # Filter projects based on search and filter
                filtered_projects = projects_with_survey_status.copy()
                
                if search_term:
                    filtered_projects = [p for p in filtered_projects if search_term.lower() in p.lower()]
                
                if filter_option == "Has Survey ✅":
                    filtered_projects = [p for p in filtered_projects if "✅" in p]
                elif filter_option == "No Survey ❌":
                    filtered_projects = [p for p in filtered_projects if "❌" in p]
                
                # Display count
                total_projects = len(projects_with_survey_status)
                with_survey = len([p for p in projects_with_survey_status if "✅" in p])
                without_survey = total_projects - with_survey
                
                st.markdown(f"""
                <div style='background: #f0f2f6; padding: 10px; border-radius: 8px; margin: 10px 0;'>
                    <b>📊 Survey Status:</b> {with_survey}/{total_projects} projects have surveys 
                    ({without_survey} need surveys)
                </div>
                """, unsafe_allow_html=True)
                
                if filtered_projects:
                    st.markdown(f"**Found {len(filtered_projects)} projects**")
                    
                    selected_project_with_status = st.selectbox(
                        "Select project to add/edit survey:",
                        [""] + sorted(filtered_projects),
                        help="✅ = Has survey data | ❌ = No survey data"
                    )
                    
                    # Extract actual project name (remove status indicators)
                    if selected_project_with_status:
                        selected_project = selected_project_with_status.replace("✅ ", "").replace("❌ ", "").replace(" (Has survey)", "").replace(" (No survey)", "")
                    else:
                        selected_project = ""
                else:
                    st.warning("No projects match your search criteria.")
                    selected_project = ""
                
                if selected_project:
                    # Get existing survey data if available
                    existing_survey_data = {}
                    project_row = df[df['Project'] == selected_project].iloc[0] if len(df[df['Project'] == selected_project]) > 0 else None
                    
                    # First check if project has survey data in the main DataFrame
                    if project_row is not None:
                        # Check for survey columns in the main dataset
                        for i in range(1, 9):
                            col_name = f'survey_q{i}'
                            if col_name in df.columns and pd.notna(project_row.get(col_name)):
                                existing_survey_data[col_name] = str(project_row.get(col_name))
                    
                    if supabase:
                        # Check if this project has survey data in Supabase (this will override DataFrame data if exists)
                        user_projects = get_user_added_projects(supabase)
                        for proj in user_projects:
                            if proj['project'] == selected_project:
                                # Update with Supabase data (more recent)
                                for i in range(1, 9):
                                    key = f'survey_q{i}'
                                    if proj.get(key):
                                        existing_survey_data[key] = proj.get(key)
                                break
                    
                    # Display message if existing survey data was found
                    if any(existing_survey_data.values()):
                        st.info("📝 **Existing survey data found!** The fields below show the current responses. You can edit and save to update them.")
                    
                    st.markdown(f"#### Survey for: **{selected_project}**")
                    
                    with st.form("survey_edit_form"):
                        st.markdown("##### Survey Questions")
                        
                        # Add indicators for which questions have data
                        q1_indicator = " ✓" if existing_survey_data.get('survey_q1') else ""
                        survey_q1 = st.text_area(
                            f"1. Initial Opposition{q1_indicator}",
                            value=existing_survey_data.get('survey_q1', ''),
                            placeholder="Can you describe any initial public opposition to the project?",
                            height=100
                        )
                        
                        q2_indicator = " ✓" if existing_survey_data.get('survey_q2') else ""
                        survey_q2 = st.text_area(
                            f"2. Community Concerns{q2_indicator}",
                            value=existing_survey_data.get('survey_q2', ''),
                            placeholder="What were the most prominent concerns raised by the community?",
                            height=100
                        )
                        
                        q3_indicator = " ✓" if existing_survey_data.get('survey_q3') else ""
                        survey_q3 = st.text_area(
                            f"3. Community Engagement{q3_indicator}",
                            value=existing_survey_data.get('survey_q3', ''),
                            placeholder="What forms of community engagement were used?",
                            height=100
                        )
                        
                        q4_indicator = " ✓" if existing_survey_data.get('survey_q4') else ""
                        survey_q4 = st.text_area(
                            f"4. Difficult Questions{q4_indicator}",
                            value=existing_survey_data.get('survey_q4', ''),
                            placeholder="What difficult or unexpected questions were asked?",
                            height=100
                        )
                        
                        q5_indicator = " ✓" if existing_survey_data.get('survey_q5') else ""
                        survey_q5 = st.text_area(
                            f"5. Success Factors{q5_indicator}",
                            value=existing_survey_data.get('survey_q5', ''),
                            placeholder="If the project succeeded, what made the difference?",
                            height=80
                        )
                        
                        q6_indicator = " ✓" if existing_survey_data.get('survey_q6') else ""
                        survey_q6 = st.text_area(
                            f"6. Failure Factors{q6_indicator}",
                            value=existing_survey_data.get('survey_q6', ''),
                            placeholder="If opposition caused delays, what factors contributed?",
                            height=80
                        )
                        
                        q7_indicator = " ✓" if existing_survey_data.get('survey_q7') else ""
                        survey_q7 = st.text_area(
                            f"7. Timeline Impact{q7_indicator}",
                            value=existing_survey_data.get('survey_q7', ''),
                            placeholder="Did opposition affect the timeline?",
                            height=80
                        )
                        
                        q8_indicator = " ✓" if existing_survey_data.get('survey_q8') else ""
                        survey_q8 = st.text_area(
                            f"8. Additional Comments{q8_indicator}",
                            value=existing_survey_data.get('survey_q8', ''),
                            placeholder="Any additional information?",
                            height=80
                        )
                        
                        submitted = st.form_submit_button("💾 Save Survey Responses", type="primary")
                        
                        if submitted:
                            survey_data = {
                                'survey_q1': survey_q1 if survey_q1 else None,
                                'survey_q2': survey_q2 if survey_q2 else None,
                                'survey_q3': survey_q3 if survey_q3 else None,
                                'survey_q4': survey_q4 if survey_q4 else None,
                                'survey_q5': survey_q5 if survey_q5 else None,
                                'survey_q6': survey_q6 if survey_q6 else None,
                                'survey_q7': survey_q7 if survey_q7 else None,
                                'survey_q8': survey_q8 if survey_q8 else None
                            }
                            
                            if supabase:
                                # Try to update existing user project or add survey to default project
                                success, project_type = update_project_survey(supabase, selected_project, survey_data)
                                
                                if project_type == "default_project" and project_row is not None:
                                    # It's a default project, we need to add it to user_added_projects with all its data
                                    full_project_data = {
                                        'project': selected_project,
                                        'state': project_row.get('State', ''),
                                        'county': project_row.get('County', ''),
                                        'type': project_row.get('Type', ''),
                                        'status': project_row.get('Status', ''),
                                        'latitude': float(project_row.get('Latitude', 0)) if pd.notna(project_row.get('Latitude')) else None,
                                        'longitude': float(project_row.get('Longitude', 0)) if pd.notna(project_row.get('Longitude')) else None,
                                        'system_size_mw_ac': float(project_row.get('System Size (MW AC)', 0)) if pd.notna(project_row.get('System Size (MW AC)')) else None,
                                        'system_size_mw_dc': float(project_row.get('System Size (MW DC)', 0)) if pd.notna(project_row.get('System Size (MW DC)')) else None,
                                        'sentiment': project_row.get('Sentiment', ''),
                                        'sentiment_detail': project_row.get('Sentiment Detail', ''),
                                        'mentions_of_moratoria': project_row.get('Mentions of Moratoria', ''),
                                        'recent_projects': project_row.get('Recent Projects', ''),
                                        **survey_data
                                    }
                                    
                                    success = add_survey_to_default_project(supabase, full_project_data)
                                    
                                if success:
                                    st.success(f"✅ Survey responses saved for '{selected_project}'!")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("Failed to save survey responses.")
                            else:
                                st.warning("⚠️ Supabase not configured. Survey functionality requires cloud database.")
            else:
                st.info("No projects available. Add a project first.")

    else:
        st.error("No data available. Please ensure the data file is in the correct location.")

elif page == "2025 Opposition Report":
    st.markdown("# 2025 Opposition Report (as of June 2025)")
    st.markdown("---")
    
    # Load the data
    @st.cache_data
    def load_opposition_data():
        try:
            # Load restrictions data
            restrictions_df = pd.read_csv('2025-Restrictions.csv', encoding='utf-8-sig')
            # Load contested projects data  
            contested_df = pd.read_csv('2025-Contested-Projects.csv', encoding='utf-8-sig')
            return restrictions_df, contested_df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None, None
    
    restrictions_df, contested_df = load_opposition_data()
    
    if restrictions_df is not None and contested_df is not None:
        # Data preprocessing
        # Count restrictions by state
        state_restrictions = restrictions_df.groupby('State').size().reset_index(name='restriction_count')
        
        # Count contested projects by state and type
        contested_df['State_List'] = contested_df['State'].str.split('|')
        # Expand states for projects that span multiple states
        state_projects = []
        for idx, row in contested_df.iterrows():
            if pd.notna(row['State']):
                states = row['State'].split('|')
                for state in states:
                    state_projects.append({
                        'State': state.strip(),
                        'County': row.get('County', 'Unknown'),
                        'Type': row.get('Type', 'Unknown'),
                        'Title': row.get('Title', 'Unknown'),
                        'Status': row.get('Status', 'Unknown'),
                        'Capacity': row.get('Capacity', ''),
                        'Content': row.get('Content', ''),
                        'Year Cancelled': row.get('Year Cancelled', ''),
                        'Litigation': row.get('Litigation', 'No')
                    })
        
        state_projects_df = pd.DataFrame(state_projects)
        state_project_counts = state_projects_df.groupby('State').size().reset_index(name='project_count')
        
        # Process county-level data for drill-down
        county_restrictions = restrictions_df.groupby(['State', 'County']).size().reset_index(name='restriction_count')
        county_projects = state_projects_df.groupby(['State', 'County']).size().reset_index(name='project_count')
        
        # Create summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total States with Opposition", len(state_restrictions['State'].unique()),
                     help="Number of states with documented restrictions or contested projects")
        with col2:
            st.metric("Total Contested Projects", len(contested_df),
                     help="Projects facing organized opposition as documented by Sabin Center")
        with col3:
            st.metric("Total Restrictions", len(restrictions_df),
                     help="State and local laws impeding renewable energy deployment")
        with col4:
            litigation_count = contested_df[contested_df['Litigation'] == 'Yes'].shape[0]
            st.metric("Projects with Litigation", litigation_count,
                     help="Contested projects involving legal action")
        
        st.markdown("---")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📍 Interactive Map", "📊 Data Tables", "📈 Analytics"])
        
        with tab1:
            st.markdown("### Interactive Opposition Map")
            st.info("🗺️ Click on a state marker to view details. Color intensity shows opposition levels.")
            
            # Create the map
            import folium
            from streamlit_folium import st_folium
            import json
            
            # Create base map centered on US
            m = folium.Map(
                location=[39.8283, -98.5795],
                zoom_start=4,
                tiles='OpenStreetMap',
                prefer_canvas=True
            )
            
            # Prepare data for map
            # Merge state data
            state_map_data = pd.merge(
                state_restrictions,
                state_project_counts,
                on='State',
                how='outer'
            ).fillna(0)
            
            # State coordinates for markers
            state_coords = {
                "AL": [32.806671, -86.791130], "AK": [61.370716, -152.404419],
                "AZ": [33.729759, -111.431221], "AR": [34.969704, -92.373123],
                "CA": [36.116203, -119.681564], "CO": [39.059811, -105.311104],
                "CT": [41.597782, -72.755371], "DE": [39.318523, -75.507141],
                "FL": [27.766279, -81.686783], "GA": [33.040619, -83.643074],
                "HI": [21.094318, -157.498337], "ID": [44.240459, -114.478828],
                "IL": [40.349457, -88.986137], "IN": [39.849426, -86.258278],
                "IA": [42.011539, -93.210526], "KS": [38.526600, -96.726486],
                "KY": [37.668140, -84.670067], "LA": [31.169546, -91.867805],
                "ME": [44.693947, -69.381927], "MD": [39.063946, -76.802101],
                "MA": [42.230171, -71.530106], "MI": [43.326618, -84.536095],
                "MN": [45.694454, -93.900192], "MS": [32.741646, -89.678696],
                "MO": [38.456085, -92.288368], "MT": [46.921925, -110.454353],
                "NE": [41.125370, -98.268082], "NV": [38.313515, -117.055374],
                "NH": [43.452492, -71.563896], "NJ": [40.298904, -74.521011],
                "NM": [34.840515, -106.248482], "NY": [42.165726, -74.948051],
                "NC": [35.630066, -79.806419], "ND": [47.528912, -99.784012],
                "OH": [40.388783, -82.764915], "OK": [35.565342, -96.928917],
                "OR": [44.572021, -122.070938], "PA": [40.590752, -77.209755],
                "RI": [41.680893, -71.511780], "SC": [33.856892, -80.945007],
                "SD": [44.299782, -99.438828], "TN": [35.747845, -86.692345],
                "TX": [31.054487, -97.563461], "UT": [40.150032, -111.862434],
                "VT": [44.045876, -72.710686], "VA": [37.769337, -78.169968],
                "WA": [47.400902, -121.490494], "WV": [38.491226, -80.954456],
                "WI": [44.268543, -89.616508], "WY": [42.755966, -107.302490],
                "DC": [38.907192, -77.036873]
            }
            
            # Find max values for color scaling
            max_restrictions = state_map_data['restriction_count'].max() if not state_map_data.empty else 1
            max_projects = state_map_data['project_count'].max() if not state_map_data.empty else 1
            
            # Add state markers
            for _, row in state_map_data.iterrows():
                state = row['State']
                if state in state_coords:
                    coords = state_coords[state]
                    restrictions = int(row['restriction_count'])
                    projects = int(row['project_count'])
                    
                    # Calculate color intensity based on total opposition
                    total_opposition = restrictions + projects
                    max_opposition = max_restrictions + max_projects
                    intensity = min(total_opposition / max_opposition, 1.0) if max_opposition > 0 else 0
                    
                    # Color from green (low) to red (high)
                    if intensity < 0.33:
                        color = 'green'
                        icon_color = 'white'
                    elif intensity < 0.66:
                        color = 'orange'
                        icon_color = 'white'
                    else:
                        color = 'red'
                        icon_color = 'white'
                    
                    # Create marker with enhanced popup
                    popup_html = f"""
                    <div style='
                        font-family: Verdana, sans-serif;
                        width: 280px;
                        padding: 0;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    '>
                        <div style='
                            background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
                            color: white;
                            padding: 15px;
                            text-align: center;
                        '>
                            <h3 style='
                                margin: 0;
                                font-size: 1.8rem;
                                font-weight: bold;
                                letter-spacing: 2px;
                            '>{state}</h3>
                        </div>
                        <div style='
                            background: white;
                            padding: 20px;
                        '>
                            <div style='
                                display: flex;
                                align-items: center;
                                margin-bottom: 12px;
                                padding: 10px;
                                background: #fff3cd;
                                border-left: 4px solid #ffc107;
                                border-radius: 4px;
                            '>
                                <span style='font-size: 1.5rem; margin-right: 10px;'>📋</span>
                                <div>
                                    <div style='font-size: 0.85rem; color: #856404; font-weight: 600;'>Restrictions</div>
                                    <div style='font-size: 1.3rem; color: #856404; font-weight: bold;'>{restrictions}</div>
                                </div>
                            </div>
                            <div style='
                                display: flex;
                                align-items: center;
                                margin-bottom: 12px;
                                padding: 10px;
                                background: #f8d7da;
                                border-left: 4px solid #dc3545;
                                border-radius: 4px;
                            '>
                                <span style='font-size: 1.5rem; margin-right: 10px;'>⚡</span>
                                <div>
                                    <div style='font-size: 0.85rem; color: #721c24; font-weight: 600;'>Contested Projects</div>
                                    <div style='font-size: 1.3rem; color: #721c24; font-weight: bold;'>{projects}</div>
                                </div>
                            </div>
                            <div style='
                                display: flex;
                                align-items: center;
                                padding: 12px;
                                background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                                border-radius: 8px;
                                border: 2px solid #4caf50;
                                margin-top: 15px;
                            '>
                                <span style='font-size: 1.5rem; margin-right: 10px;'>📊</span>
                                <div>
                                    <div style='font-size: 0.9rem; color: #2e7d32; font-weight: 600;'>Total Opposition Items</div>
                                    <div style='font-size: 1.5rem; color: #1b5e20; font-weight: bold;'>{total_opposition}</div>
                                </div>
                            </div>
                        </div>
                        <div style='
                            background: #f8f9fa;
                            padding: 10px;
                            text-align: center;
                            border-top: 1px solid #dee2e6;
                        '>
                            <small style='color: #6c757d; font-style: italic;'>Click state in dropdown for details</small>
                        </div>
                    </div>
                    """
                    
                    folium.Marker(
                        location=coords,
                        popup=folium.Popup(
                            popup_html,
                            max_width=300
                        ),
                        tooltip=f"<b>{state}</b><br>📍 Click for details<br>Total Opposition: {total_opposition}",
                        icon=folium.Icon(
                            color=color,
                            icon='info-sign',
                            prefix='glyphicon'
                        )
                    ).add_to(m)
            
            # Add legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; right: 50px; width: 200px; height: 120px; 
                        background-color: white; z-index:9999; font-size:14px;
                        border:2px solid grey; border-radius: 5px; padding: 10px">
                <p style="margin: 0 0 10px 0;"><b>Opposition Intensity</b></p>
                <p style="margin: 5px 0;"><span style="color: green;">●</span> Low (< 33%)</p>
                <p style="margin: 5px 0;"><span style="color: orange;">●</span> Medium (33-66%)</p>
                <p style="margin: 5px 0;"><span style="color: red;">●</span> High (> 66%)</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Display map
            map_data = st_folium(
                m,
                height=500,
                width=None,
                returned_objects=["last_object_clicked_popup"],
                key="opposition_map",
                use_container_width=True
            )
            
            # Check if a state was clicked and extract state code
            clicked_state = None
            if map_data and 'last_object_clicked_popup' in map_data and map_data['last_object_clicked_popup']:
                popup_text = str(map_data['last_object_clicked_popup'])
                # Extract state code from the popup HTML - looking for the state code in the h3 tag
                import re
                state_match = re.search(r'<h3[^>]*>([A-Z]{2})</h3>', popup_text)
                if state_match:
                    clicked_state = state_match.group(1)
                    # Store in session state for persistence
                    st.session_state['selected_state_2025'] = clicked_state
            
            # Get state from session or use default
            if 'selected_state_2025' not in st.session_state:
                st.session_state['selected_state_2025'] = "All States"
            elif clicked_state:
                st.session_state['selected_state_2025'] = clicked_state
            
            # State selection (manual or from map click)
            state_options = ["All States"] + sorted(state_restrictions['State'].unique().tolist())
            default_index = 0
            if st.session_state['selected_state_2025'] in state_options:
                default_index = state_options.index(st.session_state['selected_state_2025'])
            
            # Initialize variables
            selected_state = "All States"
            selected_county = "All Counties"
            
            # Add tabs for state/county selection methods
            search_tab1, search_tab2 = st.tabs(["🔍 Browse by State", "🔎 Search by County"])
            
            with search_tab1:
                browse_state = st.selectbox(
                    "Select a state to view county details:",
                    state_options,
                    index=default_index,
                    key="state_selector",
                    on_change=lambda: setattr(st.session_state, 'selected_state_2025', st.session_state.state_selector)
                )
                
                # If a state is selected, show county filter
                if browse_state != "All States":
                    # Get all counties for selected state
                    state_counties_restrict = restrictions_df[restrictions_df['State'] == browse_state]['County'].unique()
                    state_counties_contest = contested_df[contested_df['State'].str.contains(browse_state, na=False)]['County'].unique()
                    all_state_counties = list(set(list(state_counties_restrict) + list(state_counties_contest)))
                    all_state_counties = [c for c in all_state_counties if pd.notna(c)]
                    all_state_counties.sort()
                    
                    if all_state_counties:
                        browse_county = st.selectbox(
                            f"Filter by county in {browse_state}:",
                            ["All Counties"] + all_state_counties,
                            key="county_selector"
                        )
                    else:
                        st.info(f"No county data available for {browse_state}")
                        browse_county = "All Counties"
                    
                    # Set the selected values for display
                    selected_state = browse_state
                    selected_county = browse_county
                else:
                    selected_state = browse_state
                    selected_county = "All Counties"
            
            with search_tab2:
                # Direct county search
                county_search = st.text_input(
                    "🔍 Search for a county (e.g., 'Los Angeles County' or 'Cook'):",
                    placeholder="Type county name...",
                    key="county_search"
                )
                
                if county_search:
                    # Search for county in both datasets
                    search_term = county_search.lower()
                    
                    # Find matching counties
                    restrict_matches = restrictions_df[
                        restrictions_df['County'].str.lower().str.contains(search_term, na=False)
                    ]
                    contest_matches = contested_df[
                        contested_df['County'].str.lower().str.contains(search_term, na=False)
                    ]
                    
                    if not restrict_matches.empty or not contest_matches.empty:
                        # Get unique counties that match
                        matching_counties = set()
                        if not restrict_matches.empty:
                            matching_counties.update(restrict_matches[['State', 'County']].drop_duplicates().apply(
                                lambda x: f"{x['County']}, {x['State']}", axis=1
                            ).tolist())
                        if not contest_matches.empty:
                            matching_counties.update(contest_matches[['State', 'County']].drop_duplicates().apply(
                                lambda x: f"{x['County']}, {x['State']}", axis=1
                            ).tolist())
                        
                        st.success(f"Found {len(matching_counties)} matching counties:")
                        
                        selected_search_county = st.selectbox(
                            "Select a county to view details:",
                            sorted(list(matching_counties)),
                            key="search_county_select"
                        )
                        
                        if selected_search_county:
                            # Parse county and state
                            county_name, state_code = selected_search_county.rsplit(', ', 1)
                            selected_state = state_code
                            selected_county = county_name
                    else:
                        st.warning(f"❌ County '{county_search}' not found in 2025 Opposition Report database")
            
            st.markdown("---")
            
            # Debug: Show what's selected
            if selected_state != "All States" and selected_county != "All Counties":
                st.info(f"📍 Viewing: {selected_county}, {selected_state}")
            elif selected_state != "All States":
                st.info(f"📍 Viewing: All counties in {selected_state}")
            
            if selected_state == "All States":
                # Show state-level map
                st.markdown("#### State-Level Opposition Overview")
                
                # Create state-level summary
                state_summary = pd.merge(
                    state_restrictions,
                    state_project_counts,
                    on='State',
                    how='outer'
                ).fillna(0)
                
                # Display state data in an expandable format
                for _, state_data in state_summary.iterrows():
                    state_code = state_data['State']
                    with st.expander(f"{state_code} - {int(state_data['restriction_count'])} restrictions, {int(state_data['project_count'])} projects"):
                        # Show counties for this state
                        state_counties = county_restrictions[county_restrictions['State'] == state_code]
                        state_county_projects = county_projects[county_projects['State'] == state_code]
                        
                        if not state_counties.empty or not state_county_projects.empty:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Counties with Restrictions:**")
                                for _, county in state_counties.iterrows():
                                    st.write(f"• {county['County']}: {county['restriction_count']} restrictions")
                            
                            with col2:
                                st.markdown("**Counties with Contested Projects:**")
                                for _, county in state_county_projects.iterrows():
                                    st.write(f"• {county['County']}: {county['project_count']} projects")
            else:
                # Show county-level details for selected state
                if selected_county != "All Counties":
                    st.markdown(f"#### Details for {selected_county}, {selected_state}")
                else:
                    st.markdown(f"#### County-Level Details for {selected_state}")
                
                # Get data for selected state
                state_contested = contested_df[contested_df['State'].str.contains(selected_state, na=False)]
                state_restrict = restrictions_df[restrictions_df['State'] == selected_state]
                
                # Filter by county if specific county selected
                if selected_county != "All Counties":
                    state_contested = state_contested[state_contested['County'] == selected_county]
                    state_restrict = state_restrict[state_restrict['County'] == selected_county]
                    
                    # Show county summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"{selected_county} Restrictions", len(state_restrict))
                    with col2:
                        st.metric(f"{selected_county} Contested Projects", len(state_contested))
                    with col3:
                        total_opposition = len(state_restrict) + len(state_contested)
                        st.metric("Total Opposition Items", total_opposition)
                    st.markdown("---")
                    
                    # Check if any data exists for this county
                    if state_contested.empty and state_restrict.empty:
                        st.error(f"❌ No opposition data found for {selected_county}, {selected_state} in 2025 Opposition Report database")
                        st.info("This county may not have any documented restrictions or contested projects as of June 2025.")
                        # Show suggestion to check nearby counties
                        st.markdown(f"##### 💡 Suggestion: Check nearby counties in {selected_state}")
                        nearby_counties_restrict = restrictions_df[restrictions_df['State'] == selected_state]['County'].unique()
                        nearby_counties_contest = contested_df[contested_df['State'].str.contains(selected_state, na=False)]['County'].unique()
                        all_nearby = list(set(list(nearby_counties_restrict) + list(nearby_counties_contest)))
                        all_nearby = [c for c in all_nearby if pd.notna(c) and c != selected_county][:5]  # Show top 5
                        if all_nearby:
                            st.write("Counties with data in this state:")
                            for county in all_nearby:
                                st.write(f"• {county}")
                        # Stop here if no data
                        continue_display = False
                    else:
                        continue_display = True
                else:
                    continue_display = True
                
                # Display county information only if there's data to show
                if continue_display:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("##### Contested Projects")
                        if not state_contested.empty:
                            for _, project in state_contested.iterrows():
                                project_status = "🔴" if project['Status'] == 'Canceled' else "🟡" if project['Status'] == 'Pending' else "🟢"
                                with st.container():
                                    st.markdown(f"""
                                    <div style='background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 3px solid {'#dc3545' if project['Status'] == 'Canceled' else '#ffc107' if project['Status'] == 'Pending' else '#28a745'};'>
                                        <b>{project_status} {project.get('Title', 'Unknown Project')}</b><br>
                                        <small>County: {project.get('County', 'Unknown')} | Type: {project.get('Type', 'Unknown')}</small><br>
                                        <small>Status: {project.get('Status', 'Unknown')} | Capacity: {project.get('Capacity', 'N/A')} MW</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button(f"View Details", key=f"project_{project.name}"):
                                        with st.expander("Project Details", expanded=True):
                                            st.write(f"**Description:** {project.get('Content', 'No description available')}")
                                            st.write(f"**Litigation:** {project.get('Litigation', 'No')}")
                                            if pd.notna(project.get('Year Cancelled')):
                                                st.write(f"**Year Cancelled:** {project.get('Year Cancelled')}")
                                            if pd.notna(project.get('Citations')):
                                                st.write(f"**Citations:** {project.get('Citations')}")
                        else:
                            st.info("No contested projects in this state")
                    
                    with col2:
                        st.markdown("##### Local Restrictions")
                        if not state_restrict.empty:
                            for _, restriction in state_restrict.iterrows():
                                with st.container():
                                    st.markdown(f"""
                                    <div style='background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 3px solid #ffc107;'>
                                        <b>📋 {restriction.get('Title', 'Unknown Restriction')}</b><br>
                                        <small>County: {restriction.get('County', 'Unknown')} | Type: {restriction.get('Type', 'Unknown')}</small><br>
                                        <small>Status: {restriction.get('Status', 'Unknown')} | Year: {restriction.get('Year Adopted', 'N/A')}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button(f"View Details", key=f"restrict_{restriction.name}"):
                                        with st.expander("Restriction Details", expanded=True):
                                            st.write(f"**Content:** {restriction.get('Content', 'No description available')}")
                                            if pd.notna(restriction.get('Citations')):
                                                st.write(f"**Citations:** {restriction.get('Citations')}")
                        else:
                            st.info("No restrictions in this state")
        
        with tab2:
            st.markdown("### Data Tables")
            
            # Create subtabs for different data views
            data_tab1, data_tab2 = st.tabs(["Contested Projects", "Local Restrictions"])
            
            with data_tab1:
                st.markdown("#### All Contested Projects")
                
                # Add filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    type_filter = st.multiselect(
                        "Filter by Type:",
                        options=contested_df['Type'].dropna().unique(),
                        default=[]
                    )
                with col2:
                    status_filter = st.multiselect(
                        "Filter by Status:",
                        options=contested_df['Status'].dropna().unique(),
                        default=[]
                    )
                with col3:
                    litigation_filter = st.selectbox(
                        "Litigation:",
                        options=["All", "Yes", "No"],
                        index=0
                    )
                
                # Apply filters
                filtered_contested = contested_df.copy()
                if type_filter:
                    filtered_contested = filtered_contested[filtered_contested['Type'].isin(type_filter)]
                if status_filter:
                    filtered_contested = filtered_contested[filtered_contested['Status'].isin(status_filter)]
                if litigation_filter != "All":
                    filtered_contested = filtered_contested[filtered_contested['Litigation'] == litigation_filter]
                
                # Display filtered data
                st.dataframe(
                    filtered_contested[['Title', 'State', 'County', 'Type', 'Status', 'Capacity', 'Litigation', 'Year Cancelled']],
                    use_container_width=True,
                    height=400
                )
                
                # Download button
                csv = filtered_contested.to_csv(index=False)
                st.download_button(
                    label="📥 Download Contested Projects CSV",
                    data=csv,
                    file_name="contested_projects.csv",
                    mime="text/csv"
                )
            
            with data_tab2:
                st.markdown("#### All Local Restrictions")
                
                # Add filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    rest_type_filter = st.multiselect(
                        "Filter by Type:",
                        options=restrictions_df['Type'].dropna().unique(),
                        default=[]
                    )
                with col2:
                    rest_status_filter = st.multiselect(
                        "Filter by Status:",
                        options=restrictions_df['Status'].dropna().unique(),
                        default=[]
                    )
                with col3:
                    year_filter = st.slider(
                        "Year Adopted:",
                        min_value=int(restrictions_df['Year Adopted'].min()),
                        max_value=int(restrictions_df['Year Adopted'].max()),
                        value=(int(restrictions_df['Year Adopted'].min()), int(restrictions_df['Year Adopted'].max()))
                    )
                
                # Apply filters
                filtered_restrictions = restrictions_df.copy()
                if rest_type_filter:
                    filtered_restrictions = filtered_restrictions[filtered_restrictions['Type'].isin(rest_type_filter)]
                if rest_status_filter:
                    filtered_restrictions = filtered_restrictions[filtered_restrictions['Status'].isin(rest_status_filter)]
                filtered_restrictions = filtered_restrictions[
                    (filtered_restrictions['Year Adopted'] >= year_filter[0]) &
                    (filtered_restrictions['Year Adopted'] <= year_filter[1])
                ]
                
                # Display filtered data
                st.dataframe(
                    filtered_restrictions[['Title', 'State', 'County', 'Type', 'Status', 'Year Adopted', 'Level']],
                    use_container_width=True,
                    height=400
                )
                
                # Download button
                csv = filtered_restrictions.to_csv(index=False)
                st.download_button(
                    label="📥 Download Restrictions CSV",
                    data=csv,
                    file_name="local_restrictions.csv",
                    mime="text/csv"
                )
        
        with tab3:
            st.markdown("### Analytics Dashboard")
            
            # Row 1: Type distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Project Types Distribution")
                type_counts = contested_df['Type'].value_counts()
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Contested Projects by Type",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Contested Projects by Status")
                status_counts = contested_df['Status'].value_counts()
                fig = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    title="Contested Projects by Status",
                    labels={'x': 'Status', 'y': 'Count'},
                    color=status_counts.index,
                    color_discrete_map={'Canceled': '#dc3545', 'Pending': '#ffc107', 'Operating': '#28a745'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Row 2: Timeline analysis
            st.markdown("#### Timeline Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Process year data for canceled projects
                if 'Year Cancelled' in contested_df.columns:
                    year_data = contested_df[contested_df['Year Cancelled'].notna()].copy()
                    year_data['Year Cancelled'] = pd.to_numeric(year_data['Year Cancelled'], errors='coerce')
                    year_counts = year_data.groupby('Year Cancelled').size().reset_index(name='count')
                    
                    fig = px.line(
                        year_counts,
                        x='Year Cancelled',
                        y='count',
                        title="Canceled Projects Over Time",
                        markers=True,
                        line_shape='linear'
                    )
                    fig.update_layout(
                        xaxis_title="Year", 
                        yaxis_title="Number of Canceled Projects",
                        hovermode='x unified'
                    )
                    fig.update_traces(
                        line_color='#dc3545',
                        marker_color='#dc3545',
                        marker_size=8
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Process year data for restrictions
                if 'Year Adopted' in restrictions_df.columns:
                    restrictions_year_data = restrictions_df.copy()
                    restrictions_year_data['Year Adopted'] = pd.to_numeric(restrictions_year_data['Year Adopted'], errors='coerce')
                    restrictions_year_data = restrictions_year_data[restrictions_year_data['Year Adopted'].notna()]
                    restrictions_year_counts = restrictions_year_data.groupby('Year Adopted').size().reset_index(name='count')
                    
                    fig = px.bar(
                        restrictions_year_counts,
                        x='Year Adopted',
                        y='count',
                        title="Restrictions Adopted by Year",
                        color='count',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(
                        xaxis_title="Year", 
                        yaxis_title="Number of Restrictions Adopted",
                        showlegend=False,
                        hovermode='x unified'
                    )
                    fig.update_traces(
                        hovertemplate='<b>Year %{x}</b><br>Restrictions: %{y}<extra></extra>'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Row 3: Top states analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Top 10 States by Contested Projects")
                top_states = state_project_counts.nlargest(10, 'project_count')
                fig = px.bar(
                    top_states,
                    x='project_count',
                    y='State',
                    orientation='h',
                    title="States with Most Contested Projects",
                    labels={'project_count': 'Number of Projects', 'State': 'State'},
                    color='project_count',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Top 10 States by Restrictions")
                top_restrictions = state_restrictions.nlargest(10, 'restriction_count')
                fig = px.bar(
                    top_restrictions,
                    x='restriction_count',
                    y='State',
                    orientation='h',
                    title="States with Most Restrictions",
                    labels={'restriction_count': 'Number of Restrictions', 'State': 'State'},
                    color='restriction_count',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            st.markdown("---")
            st.markdown("#### Key Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_capacity = contested_df['Capacity'].apply(lambda x: pd.to_numeric(x, errors='coerce')).mean()
                if not pd.isna(avg_capacity):
                    st.metric("Average Project Capacity", f"{avg_capacity:.1f} MW")
                else:
                    st.metric("Average Project Capacity", "N/A")
            
            with col2:
                litigation_pct = (contested_df['Litigation'] == 'Yes').mean() * 100
                st.metric("Projects with Litigation", f"{litigation_pct:.1f}%")
            
            with col3:
                canceled_pct = (contested_df['Status'] == 'Canceled').mean() * 100
                st.metric("Cancellation Rate", f"{canceled_pct:.1f}%")
        
        # Add Key Findings and source citation at the bottom
        st.markdown("---")
        
        # Key Findings box
        st.markdown("""
        <div style='
            background: #f8f9fa;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #28a745;
            box-shadow: 0 2px 8px rgba(40, 167, 69, 0.15);
        '>
            <h4 style='
                color: #155724;
                margin: 0 0 0.5rem 0;
                font-family: Verdana, sans-serif;
                font-size: 1.1rem;
            '>
                📊 2025 Opposition Report Key Findings (as of June 2025)
            </h4>
            <p style='
                color: #495057;
                margin: 0;
                font-size: 0.95rem;
                line-height: 1.6;
            '>
                <strong>459 counties/municipalities</strong> across 44 states have severe restrictions 
                (<strong>16% increase</strong> from 2023).<br>
                <strong>498 contested projects</strong> identified in 49 states 
                (<strong>32% increase</strong> from previous year).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Data Source Attribution box
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 4px solid #1976d2;
            padding: 1.2rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.15);
        '>
            <h4 style='
                color: #0d47a1;
                margin: 0 0 0.8rem 0;
                font-family: Verdana, sans-serif;
                font-size: 1.1rem;
            '>
                📚 Data Source & Attribution
            </h4>
            <p style='
                color: #1565c0;
                margin: 0 0 0.5rem 0;
                font-family: Verdana, sans-serif;
                font-size: 0.95rem;
                line-height: 1.5;
            '>
                <strong>Opposition to Renewable Energy Facilities in the United States: June 2025 Edition</strong><br>
                Data current through December 31, 2024
            </p>
            <p style='
                color: #424242;
                margin: 0.5rem 0;
                font-family: Verdana, sans-serif;
                font-size: 0.88rem;
                line-height: 1.4;
            '>
                By Matthew Eisenson, Jacob Elkin, Ivonne Norman, Rebecca Coombs, Chadol Kim, Rex Koenig, 
                Suzan Michalski, Eric Quiroz, Josepi Scariano, Ava Teasdale, Victor Tong, & Annabel Williams
            </p>
            <p style='
                color: #424242;
                margin: 0.5rem 0;
                font-family: Verdana, sans-serif;
                font-size: 0.88rem;
                line-height: 1.4;
            '>
                <strong>Columbia Law School - Sabin Center for Climate Change Law</strong><br>
                Climate School, Columbia University
            </p>
            <p style='
                color: #1565c0;
                margin: 0.8rem 0 0 0;
                font-family: Verdana, sans-serif;
                font-size: 0.85rem;
            '>
                🔗 <a href="https://climate.law.columbia.edu/content/opposition-renewable-energy-facilities-united-states-june-2025-edition" 
                   target="_blank" style="color: #1976d2;">
                   View Full Report at Columbia Law School
                </a>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("Unable to load the required data files. Please ensure '2025-Restrictions.csv' and '2025-Contested-Projects.csv' are in the correct location.")
    
elif page == "Public Hearings Resources":
    st.markdown("# Public Hearings Q&A Resource Center")
    st.markdown("---")
    
    # Information box
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #1976d2;
        margin-bottom: 2rem;
    '>
        <h3 style='color: #0d47a1; margin: 0 0 0.5rem 0;'>📋 Quick Reference for Public Hearings</h3>
        <p style='color: #1565c0; margin: 0; font-size: 1rem;'>
            Search, add, and manage common questions and DESRI responses for public hearings. 
            This resource helps our teams prepare for community meetings with consistent, well-researched answers.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Search Q&A", "➕ Add New Q&A", "✏️ Edit Q&A", "📊 Browse by Topic", "🗑️ Manage Removed"])
    
    # Load Q&A data
    if supabase:
        qa_data = get_active_public_hearing_qa(supabase)
    else:
        qa_data = []
        st.warning("⚠️ Database not configured. Using demo mode with limited functionality.")
    
    # Define base topics
    base_topics = [
        "Health Concerns",
        "Environmental Impact", 
        "Agricultural and Rural Community Impact",
        "Property Values",
        "Economic Viability",
        "Waste and Recycling",
        "Visual Impact and Noise",
        "Temperature and Heat Island Effects",
        "Decommissioning",
        "Battery Energy Storage Systems (BESS) Safety",
        "Community Engagement and Trust",
        "Energy Independence and Security",
        "Land Use",
        "Other"
    ]
    
    # Get all unique topics from database (including custom ones)
    all_topics_from_db = set()
    if qa_data:
        for qa in qa_data:
            topic = qa.get('topic')
            if topic:
                all_topics_from_db.add(topic)
    
    # Combine base topics with custom topics from database
    topics = base_topics.copy()
    for topic in all_topics_from_db:
        if topic not in topics:
            topics.append(topic)
    
    # Sort topics alphabetically, keeping "Other" at the end
    topics_without_other = [t for t in topics if t != "Other"]
    topics_without_other.sort()
    topics = topics_without_other + ["Other"]
    
    with tab1:
        st.markdown("### Search Questions & Answers")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "🔍 Search for questions or keywords:",
                placeholder="e.g., 'EMF', 'property values', 'solar panels toxic'...",
                key="qa_search"
            )
        with col2:
            search_topic = st.selectbox(
                "Filter by topic:",
                ["All Topics"] + topics,
                key="topic_filter"
            )
        
        if search_query or search_topic != "All Topics":
            # Filter Q&A based on search
            filtered_qa = qa_data
            
            if search_query:
                search_lower = search_query.lower()
                filtered_qa = [
                    qa for qa in filtered_qa 
                    if search_lower in qa.get('question', '').lower() or 
                       search_lower in qa.get('response', '').lower() or
                       search_lower in qa.get('topic', '').lower()
                ]
            
            if search_topic != "All Topics":
                filtered_qa = [qa for qa in filtered_qa if qa.get('topic') == search_topic]
            
            if filtered_qa:
                st.success(f"Found {len(filtered_qa)} matching Q&A items")
                
                for qa in filtered_qa:
                    with st.expander(f"📌 {qa.get('topic', 'General')} - {qa.get('question', '')[:100]}..."):
                        st.markdown(f"**Topic:** {qa.get('topic', 'General')}")
                        st.markdown(f"**Common Concern/Question:** {qa.get('question', '')}")
                        st.markdown("**DESRI Response:**")
                        
                        # Parse and display response with bullet points
                        response = qa.get('response', '')
                        if '•' in response:
                            lines = response.split('•')
                            st.markdown(lines[0])  # First part before bullets
                            for line in lines[1:]:
                                if line.strip():
                                    st.markdown(f"• {line.strip()}")
                        else:
                            st.markdown(response)
                        
                        if qa.get('sources'):
                            st.markdown(f"**Sources:** {qa.get('sources')}")
                        
                        # Quick copy button
                        if st.button(f"📋 Copy Response", key=f"copy_{qa.get('id', 0)}"):
                            st.code(response, language=None)
                            st.info("Response displayed above - select and copy the text")
            else:
                st.warning("No Q&A items found matching your search criteria")
        else:
            st.info("Enter a search term or select a topic to find relevant Q&A items")
    
    with tab2:
        st.markdown("### Add New Question & Answer")
        
        with st.form("add_qa_form"):
            st.markdown("#### Enter Q&A Details")
            
            # Show both options always - let user choose which one to use
            col1, col2 = st.columns(2)
            
            with col1:
                existing_topic = st.selectbox(
                    "Select Existing Topic",
                    ["-- Select --"] + topics,
                    help="Choose from existing topics"
                )
            
            with col2:
                custom_topic = st.text_input(
                    "OR Create New Topic",
                    placeholder="Enter new topic name",
                    help="Type a new topic if not in the list"
                )
            
            # Determine which topic to use
            if custom_topic:
                new_topic = custom_topic
                st.info(f"✨ Will create new topic: **{custom_topic}**")
            elif existing_topic != "-- Select --":
                new_topic = existing_topic
            else:
                new_topic = None
            
            new_question = st.text_area(
                "Common Concern/Question*",
                placeholder='e.g., "Solar farms increase EMF which poses health risks"',
                height=100,
                help="Enter the concern or question as typically asked by the public"
            )
            
            new_response = st.text_area(
                "DESRI Response*",
                placeholder="Enter the complete DESRI response. Use • for bullet points.",
                height=300,
                help="Provide the full response with bullet points where appropriate"
            )
            
            new_sources = st.text_area(
                "Sources (Optional)",
                placeholder="List any sources, studies, or references",
                height=100,
                help="Include citations, studies, or references that support the response"
            )
            
            submitted = st.form_submit_button("➕ Add Q&A", type="primary")
            
            if submitted:
                if new_topic and new_question and new_response:
                    qa_entry = {
                        'topic': new_topic,
                        'question': new_question,
                        'response': new_response,
                        'sources': new_sources if new_sources else None
                    }
                    
                    if supabase:
                        success = add_public_hearing_qa(supabase, qa_entry)
                        if success:
                            st.success("✅ Q&A added successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Failed to add Q&A. Please try again.")
                    else:
                        st.warning("Database not configured. Q&A not saved.")
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab3:
        st.markdown("### Edit or Delete Existing Q&A")
        
        if qa_data:
            # Group by topic for easier navigation
            qa_by_topic = {}
            for qa in qa_data:
                topic = qa.get('topic', 'Other')
                if topic not in qa_by_topic:
                    qa_by_topic[topic] = []
                qa_by_topic[topic].append(qa)
            
            # Select topic first
            edit_topic = st.selectbox(
                "Select topic to edit:",
                list(qa_by_topic.keys()),
                key="edit_topic_select"
            )
            
            if edit_topic:
                # Select specific Q&A within topic
                topic_qas = qa_by_topic[edit_topic]
                qa_options = [
                    f"{qa.get('question', '')[:100]}..." 
                    for qa in topic_qas
                ]
                
                selected_qa_index = st.selectbox(
                    "Select Q&A to edit:",
                    range(len(qa_options)),
                    format_func=lambda x: qa_options[x],
                    key="edit_qa_select"
                )
                
                if selected_qa_index is not None:
                    selected_qa = topic_qas[selected_qa_index]
                    
                    st.markdown("---")
                    st.markdown("#### Edit Q&A")
                    
                    with st.form(f"edit_form_{selected_qa.get('id', 0)}"):
                        # Get current topic
                        current_topic = selected_qa.get('topic', 'Other')
                        
                        # If current topic is not in predefined list, add it
                        edit_topics = topics.copy()
                        if current_topic not in edit_topics:
                            edit_topics.append(current_topic)
                        
                        # Show both options - let user choose which one to use
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_existing_topic = st.selectbox(
                                "Select Existing Topic",
                                edit_topics,
                                index=edit_topics.index(current_topic) if current_topic in edit_topics else 0
                            )
                        
                        with col2:
                            edit_custom_topic = st.text_input(
                                "OR Create New Topic",
                                placeholder="Enter new topic name",
                                help="Type a new topic if not in the list"
                            )
                        
                        # Determine which topic to use
                        if edit_custom_topic:
                            edit_topic = edit_custom_topic
                        else:
                            edit_topic = edit_existing_topic
                        
                        edit_question = st.text_area(
                            "Common Concern/Question",
                            value=selected_qa.get('question', ''),
                            height=100
                        )
                        
                        edit_response = st.text_area(
                            "DESRI Response",
                            value=selected_qa.get('response', ''),
                            height=300
                        )
                        
                        edit_sources = st.text_area(
                            "Sources",
                            value=selected_qa.get('sources', ''),
                            height=100
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            update_btn = st.form_submit_button("💾 Save Changes", type="primary")
                        with col2:
                            delete_btn = st.form_submit_button("🗑️ Remove Q&A", type="secondary")
                        
                        if update_btn:
                            updated_qa = {
                                'topic': edit_topic,
                                'question': edit_question,
                                'response': edit_response,
                                'sources': edit_sources
                            }
                            
                            if supabase:
                                success = update_public_hearing_qa(
                                    supabase, 
                                    selected_qa.get('id'), 
                                    updated_qa
                                )
                                if success:
                                    st.success("✅ Q&A updated successfully!")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("Failed to update Q&A.")
                            else:
                                st.warning("Database not configured.")
                        
                        if delete_btn:
                            if supabase:
                                confirm_key = f"confirm_delete_{selected_qa.get('id', 0)}"
                                if st.checkbox("Confirm removal", key=confirm_key):
                                    success = soft_delete_public_hearing_qa(
                                        supabase,
                                        selected_qa.get('id')
                                    )
                                    if success:
                                        st.success("✅ Q&A removed successfully! You can restore it from the 'Manage Removed' tab.")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error("Failed to remove Q&A.")
                            else:
                                st.warning("Database not configured.")
        else:
            st.info("No Q&A items available to edit. Add some Q&A items first!")
    
    with tab4:
        st.markdown("### Browse Q&A by Topic")
        
        if qa_data:
            # Group by topic
            qa_by_topic = {}
            for qa in qa_data:
                topic = qa.get('topic', 'Other')
                if topic not in qa_by_topic:
                    qa_by_topic[topic] = []
                qa_by_topic[topic].append(qa)
            
            # Display topics with counts
            col1, col2, col3 = st.columns(3)
            topics_list = list(qa_by_topic.keys())
            
            for i, topic in enumerate(topics_list):
                col = [col1, col2, col3][i % 3]
                with col:
                    count = len(qa_by_topic[topic])
                    if st.button(
                        f"📁 {topic}\n({count} items)",
                        key=f"topic_btn_{topic}",
                        use_container_width=True
                    ):
                        st.session_state['selected_browse_topic'] = topic
            
            # Display selected topic's Q&As
            if 'selected_browse_topic' in st.session_state:
                st.markdown("---")
                st.markdown(f"### {st.session_state['selected_browse_topic']}")
                
                topic_items = qa_by_topic.get(st.session_state['selected_browse_topic'], [])
                for qa in topic_items:
                    with st.expander(f"❓ {qa.get('question', '')[:100]}..."):
                        st.markdown(f"**Common Concern:** {qa.get('question', '')}")
                        st.markdown("**DESRI Response:**")
                        
                        response = qa.get('response', '')
                        if '•' in response:
                            lines = response.split('•')
                            st.markdown(lines[0])
                            for line in lines[1:]:
                                if line.strip():
                                    st.markdown(f"• {line.strip()}")
                        else:
                            st.markdown(response)
                        
                        if qa.get('sources'):
                            st.markdown(f"**Sources:** {qa.get('sources')}")
        else:
            st.info("No Q&A items available. Start by adding some Q&A items in the 'Add New Q&A' tab!")
    
    with tab5:
        st.markdown("### Manage Removed Q&As")
        
        if supabase:
            removed_qa = get_removed_public_hearing_qa(supabase)
            
            if removed_qa:
                st.info(f"📋 Found {len(removed_qa)} removed Q&A items")
                
                # Group removed Q&As by topic
                removed_by_topic = {}
                for qa in removed_qa:
                    topic = qa.get('topic', 'Other')
                    if topic not in removed_by_topic:
                        removed_by_topic[topic] = []
                    removed_by_topic[topic].append(qa)
                
                # Display removed Q&As
                for topic in sorted(removed_by_topic.keys()):
                    with st.expander(f"📁 {topic} ({len(removed_by_topic[topic])} items)"):
                        for qa in removed_by_topic[topic]:
                            st.markdown(f"**Question:** {qa.get('question', '')[:100]}...")
                            
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                if st.button(f"👁️ View Full", key=f"view_{qa.get('id')}"):
                                    st.markdown(f"**Full Question:** {qa.get('question', '')}")
                                    st.markdown(f"**Response:** {qa.get('response', '')}")
                                    if qa.get('sources'):
                                        st.markdown(f"**Sources:** {qa.get('sources')}")
                            
                            with col2:
                                if st.button(f"♻️ Restore", key=f"restore_{qa.get('id')}"):
                                    success = restore_public_hearing_qa(supabase, qa.get('id'))
                                    if success:
                                        st.success(f"✅ Q&A restored successfully!")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error("Failed to restore Q&A")
                            
                            with col3:
                                if st.button(f"🗑️ Delete Permanently", key=f"perm_delete_{qa.get('id')}"):
                                    # Add confirmation
                                    confirm_col1, confirm_col2 = st.columns(2)
                                    with confirm_col1:
                                        if st.button(f"✅ Confirm Delete", key=f"confirm_perm_{qa.get('id')}"):
                                            success = delete_public_hearing_qa(supabase, qa.get('id'))
                                            if success:
                                                st.success("Q&A permanently deleted")
                                                st.cache_data.clear()
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete Q&A")
                                    with confirm_col2:
                                        st.warning("⚠️ This cannot be undone!")
                            
                            st.markdown("---")
            else:
                st.success("✨ No removed Q&A items. All Q&As are active!")
                
                # Show statistics
                active_qa = get_active_public_hearing_qa(supabase)
                if active_qa:
                    # Count by topic
                    topic_counts = {}
                    for qa in active_qa:
                        topic = qa.get('topic', 'Other')
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
                    
                    st.markdown("### 📊 Active Q&A Statistics")
                    cols = st.columns(3)
                    for i, (topic, count) in enumerate(sorted(topic_counts.items())):
                        col = cols[i % 3]
                        with col:
                            st.metric(topic[:20] + "..." if len(topic) > 20 else topic, count)
        else:
            st.warning("Database not configured")

elif page == "User Guide":
    st.markdown("# 📖 User Guide")
    st.markdown("---")
    
    # Create tabs for different sections of the guide
    guide_tabs = st.tabs([
        "🏠 Overview", 
        "📍 Opposition Tracker", 
        "📊 2025 Report", 
        "❓ Public Hearings", 
        "💡 Tips & Troubleshooting"
    ])
    
    with guide_tabs[0]:  # Overview
        st.markdown("""
        ## Welcome to the DESRI Public Engagement Intelligence Hub
        
        This comprehensive tool helps track and manage community opposition to renewable energy projects. 
        
        ### 🎯 Main Features
        
        1. **Opposition Tracker** - Interactive map and database of projects
        2. **2025 Opposition Report** - Analytics and insights
        3. **Public Hearings Resources** - Q&A database for community meetings
        
        ### 🚀 Quick Start
        
        - **View Projects**: Click on map markers in Opposition Tracker
        - **Add Data**: Use the "Add New Project" or "Add New Q&A" tabs
        - **Analyze Trends**: Check the 2025 Report for insights
        - **Find Responses**: Search Public Hearings Resources for common questions
        
        Navigate through the tabs above for detailed instructions on each feature.
        """)
    
    with guide_tabs[1]:  # Opposition Tracker
        st.markdown("""
        ## Opposition Tracker Guide
        
        ### 📍 Interactive Map
        
        **Viewing Projects:**
        - **Red markers** indicate projects with opposition
        - **Click any marker** to see full project details
        - **Use mouse wheel** to zoom in/out
        - **Click and drag** to move around the map
        
        ### 🔍 Filtering Projects
        
        #### ⚠️ **IMPORTANT: County Format**
        When searching by county, you MUST include the word "County":
        
        ✅ **Correct Examples:**
        - Los Angeles County
        - Cook County  
        - Harris County
        - Orange County
        - San Diego County
        
        ❌ **Incorrect Examples:**
        - Los Angeles (missing "County")
        - Cook Co. (wrong abbreviation)
        - Harris (missing "County")
        - Orange County, CA (don't add state)
        
        #### Other Filters:
        - **State**: Select from dropdown
        - **Type**: Solar, Wind, Battery Storage, etc.
        - **Survey Status**: Has Survey ✅ or No Survey ❌
        
        ### ➕ Adding New Projects
        
        1. Go to **"Add New Project"** tab
        2. Fill in required fields (marked with *)
        3. **Project Name**: Official name (e.g., "Sunset Solar Farm")
        4. **County**: Must be formatted as "[Name] County"
        5. **Coordinates**: 
           - Get from Google Maps (right-click → "What's here?")
           - Longitude must be negative for US locations
        6. **Status Options**:
           - Opposition - Pending
           - Opposition - Defeated
           - Opposition - Project Withdrawn
           - Under Construction
           - Operational
        
        ### 📝 Survey Responses
        
        **Adding Survey Data:**
        1. Go to **"Add/Edit Survey"** tab
        2. Select project from dropdown
        3. Answer 8 detailed questions about:
           - Initial opposition details
           - Community concerns
           - Engagement strategies
           - Lessons learned
        4. Save responses (can be partial)
        
        **Survey Questions Include:**
        - When/how opposition emerged
        - Main concerns raised
        - Engagement methods used
        - Difficult questions faced
        - Strategic recommendations
        - Contributing factors
        - Organized opposition groups
        """)
    
    with guide_tabs[2]:  # 2025 Report
        st.markdown("""
        ## 2025 Opposition Report Guide
        
        ### 📊 Understanding the Analytics
        
        **Summary Cards** show:
        - Total projects tracked
        - Number of states affected
        - Average project size
        - Data completeness (surveys)
        
        ### 📈 Interactive Charts
        
        **1. Projects by State**
        - Bar chart showing geographic distribution
        - Identifies opposition hotspots
        - Hover for details
        
        **2. Projects by Type**
        - Pie chart of technology distribution
        - Shows which types face most opposition
        - Typically solar has highest count
        
        **3. Opposition Outcomes**
        - **Pending**: Still under review
        - **Defeated**: Project stopped
        - **Withdrawn**: Developer pulled out
        - **Approved**: Overcame opposition
        
        **4. Top Developers**
        - Companies facing most opposition
        - DESRI projects highlighted
        - Competitive intelligence tool
        
        **5. Key Concerns**
        - Most common objections
        - Helps prepare responses
        - Identifies trends
        
        ### 📋 Data Table
        
        - **Sort** by clicking column headers
        - **Search** using the search box
        - **Export** by copying data
        - **Expand** rows for full details
        
        ### 💡 Using Insights
        
        1. **Identify Patterns**: Geographic and thematic trends
        2. **Benchmark Performance**: Compare to competitors
        3. **Inform Strategy**: Focus on common concerns
        """)
    
    with guide_tabs[3]:  # Public Hearings
        st.markdown("""
        ## Public Hearings Resources Guide
        
        ### 🔍 Finding Q&As
        
        **Search Methods:**
        1. **By Topic**: Select from dropdown categories
        2. **By Keyword**: Search for specific terms (e.g., "EMF", "property values")
        3. **Browse All**: View by topic in the Browse tab
        
        ### ➕ Adding New Q&As
        
        **Step-by-Step:**
        1. Go to **"Add New Q&A"** tab
        2. **Topic Selection**:
           - Choose existing topic from dropdown OR
           - Create new topic by typing in text field
        3. **Question**: Write as community typically asks
        4. **Response**: 
           - Use bullet points (start with •)
           - Include data and statistics
           - Keep professional tone
        5. **Sources**: Add studies, reports (optional but recommended)
        
        ### ✏️ Editing Q&As
        
        1. Go to **"Edit Q&A"** tab
        2. Select topic to filter
        3. Choose specific Q&A
        4. Modify any field
        5. Save or Remove
        
        ### 🗑️ Managing Removed Items
        
        **Soft Delete System:**
        - Removed items aren't permanently deleted
        - Can restore from "Manage Removed" tab
        - Option to permanently delete if needed
        
        ### 📝 Response Best Practices
        
        **DO:**
        ✅ Use specific data and statistics
        ✅ Cite credible sources
        ✅ Address underlying concerns
        ✅ Use clear bullet points
        ✅ Keep language accessible
        
        **DON'T:**
        ❌ Dismiss concerns
        ❌ Use excessive jargon
        ❌ Make unsupported claims
        ❌ Be condescending
        """)
    
    with guide_tabs[4]:  # Tips & Troubleshooting
        st.markdown("""
        ## Tips & Troubleshooting
        
        ### 🎯 Data Quality Tips
        
        **Consistency:**
        - Always format counties as "[Name] County"
        - Use official project names
        - Verify coordinates (negative longitude for US)
        
        **Completeness:**
        - Fill all available fields
        - Add survey responses when possible
        - Update project status regularly
        
        ### 🔧 Common Issues & Solutions
        
        **Map not showing projects?**
        - Check filters aren't too restrictive
        - Verify coordinates are correct
        - Refresh page (Ctrl+R or Cmd+R)
        
        **Can't add new Q&A?**
        - Ensure all required fields are filled
        - Check database connection
        - Try refreshing the page
        
        **County filter not working?**
        - Must include "County" in search
        - Check exact spelling
        - Don't include state abbreviation
        
        **Projects not appearing after adding?**
        - Verify latitude/longitude format
        - Longitude should be negative for US
        - Check all required fields were filled
        
        ### 📊 Best Practices
        
        **Monthly Reviews:**
        - Check for new opposition projects
        - Update project statuses
        - Review success/failure patterns
        
        **Before Public Hearings:**
        - Search Q&A database for relevant concerns
        - Review similar projects' surveys
        - Prepare responses for top issues
        
        **Data Management:**
        - Regular backups are automatic
        - Use soft delete to prevent data loss
        - Update information quarterly
        
        ### ⌨️ Keyboard Shortcuts
        
        - **Refresh Page**: Ctrl+R (Windows) or Cmd+R (Mac)
        - **Clear Cache**: Ctrl+Shift+R or Cmd+Shift+R
        - **Search**: Ctrl+F or Cmd+F
        
        ### 📞 Getting Help
        
        1. Check this user guide first
        2. Try refreshing the page
        3. Clear browser cache if needed
        
        ### 🔐 Security Notes
        
        - Don't share login credentials
        - Database is backed up regularly
        - Soft delete prevents accidental data loss
        - Only authorized users should have access
        """)

# Footer
st.markdown("---")

# Add some bottom padding to ensure text is visible
st.markdown("""
<style>
    /* Add minimal padding to the bottom of the app */
    .main .block-container {
        padding-bottom: 2rem !important;
    }
    
    /* Fix excessive spacing around folium map */
    iframe {
        margin-bottom: 0 !important;
    }
    
    /* Reduce spacing after map container */
    .element-container:has(iframe) {
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce spacing before metrics */
    .element-container:has(.metric-container) {
        margin-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Footer with logo - use full width instead of columns
try:
    if os.path.exists('desri_logo2.svg'):
        with open('desri_logo2.svg', 'r') as f:
            svg_content = f.read()
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; margin: 0 auto;">
            <div class="logo-container" style="width: 100%; max-width: 400px;">
                {svg_content}
            </div>
            <div style='display: flex; justify-content: center; width: 100%; margin-top: 1rem;'>
                <p style='margin: 0; padding: 0; font-family: Verdana, sans-serif; font-size: 0.9rem; font-weight: bold; color: black; text-align: center;'>
                    Public Engagement Hub | Tracking Community Opposition to U.S. Renewable Energy Projects
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style='text-align: center; color: black; padding: 1rem;'>
                <p>Public Engagement Hub | Tracking Community Opposition to U.S. Renewable Energy Projects</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
except Exception as e:
    st.markdown(
        """
        <div style='text-align: center; color: rgba(0,0,0,0.6); padding: 1rem;'>
            <p>Public Engagement Hub | Tracking Community Opposition to U.S. Renewable Energy Projects</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Add extra space at the bottom
st.markdown("<br><br><br>", unsafe_allow_html=True)