"""
Supabase configuration for DESRI Opposition Tracker
"""
import os
import streamlit as st
from supabase import create_client, Client

def init_supabase() -> Client:
    """Initialize Supabase client with credentials from Streamlit secrets or environment variables"""
    
    # Try to get credentials from Streamlit secrets first (for deployment)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except:
        # Fall back to environment variables (for local development)
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
    
    if not url or not key:
        st.error("""
        ⚠️ Supabase credentials not found!
        
        **For local development:**
        1. Create a `.env` file with:
           ```
           SUPABASE_URL=your_url_here
           SUPABASE_KEY=your_key_here
           ```
        
        **For Streamlit Cloud:**
        1. Go to your app settings
        2. Add secrets:
           ```
           SUPABASE_URL = "your_url_here"
           SUPABASE_KEY = "your_key_here"
           ```
        """)
        return None
    
    return create_client(url, key)

def get_user_added_projects(supabase: Client):
    """Fetch all user-added projects from Supabase"""
    try:
        response = supabase.table('user_added_projects').select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching user projects: {e}")
        return []

def get_removed_projects(supabase: Client):
    """Fetch all removed projects from Supabase"""
    try:
        response = supabase.table('removed_projects').select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching removed projects: {e}")
        return []

def add_user_project(supabase: Client, project_data: dict):
    """Add a new user project to Supabase"""
    try:
        response = supabase.table('user_added_projects').insert(project_data).execute()
        return True
    except Exception as e:
        st.error(f"Error adding project: {e}")
        return False

def remove_project(supabase: Client, project_name: str):
    """Add a project to the removed list"""
    try:
        # Check if already removed
        existing = supabase.table('removed_projects').select("*").eq('project', project_name).execute()
        if existing.data:
            return False, "Project already removed"
        
        # Add to removed list
        response = supabase.table('removed_projects').insert({'project': project_name}).execute()
        return True, "Project removed successfully"
    except Exception as e:
        return False, f"Error: {e}"

def restore_project(supabase: Client, project_name: str):
    """Remove a project from the removed list"""
    try:
        response = supabase.table('removed_projects').delete().eq('project', project_name).execute()
        return True
    except Exception as e:
        st.error(f"Error restoring project: {e}")
        return False

def restore_all_projects(supabase: Client):
    """Clear all removed projects"""
    try:
        # Delete all records from removed_projects table
        response = supabase.table('removed_projects').delete().neq('id', 0).execute()  # neq('id', 0) matches all records
        return True
    except Exception as e:
        st.error(f"Error restoring all projects: {e}")
        return False

def delete_user_project(supabase: Client, project_name: str):
    """Delete a user-added project from Supabase"""
    try:
        response = supabase.table('user_added_projects').delete().eq('project', project_name).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting user project: {e}")
        return False

def update_project_survey(supabase: Client, project_name: str, survey_data: dict):
    """Update survey answers for an existing project"""
    try:
        # Check if it's a user-added project
        existing = supabase.table('user_added_projects').select("*").eq('project', project_name).execute()
        
        if existing.data:
            # Update the existing project with survey data
            response = supabase.table('user_added_projects').update(survey_data).eq('project', project_name).execute()
            return True, "user_project"
        else:
            # It's a default project - we need to add it to user_added_projects with survey data
            # First get the project details from the main dataset
            return False, "default_project"
    except Exception as e:
        st.error(f"Error updating survey: {e}")
        return False, "error"

def add_survey_to_default_project(supabase: Client, project_data: dict):
    """Add a default project to user_added_projects table with survey answers"""
    try:
        # Check if already exists
        existing = supabase.table('user_added_projects').select("*").eq('project', project_data['project']).execute()
        
        if existing.data:
            # Update existing
            response = supabase.table('user_added_projects').update(project_data).eq('project', project_data['project']).execute()
        else:
            # Insert new
            response = supabase.table('user_added_projects').insert(project_data).execute()
        return True
    except Exception as e:
        st.error(f"Error adding survey to project: {e}")
        return False

# Public Hearings Q&A Functions
def get_public_hearing_qa(supabase: Client):
    """Fetch all public hearing Q&A items from Supabase"""
    try:
        response = supabase.table('public_hearing_qa').select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching Q&A items: {e}")
        return []

def add_public_hearing_qa(supabase: Client, qa_data: dict):
    """Add a new Q&A item to Supabase"""
    try:
        response = supabase.table('public_hearing_qa').insert(qa_data).execute()
        return True
    except Exception as e:
        st.error(f"Error adding Q&A item: {e}")
        return False

def update_public_hearing_qa(supabase: Client, qa_id: int, qa_data: dict):
    """Update an existing Q&A item in Supabase"""
    try:
        response = supabase.table('public_hearing_qa').update(qa_data).eq('id', qa_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating Q&A item: {e}")
        return False

def delete_public_hearing_qa(supabase: Client, qa_id: int):
    """Delete a Q&A item from Supabase"""
    try:
        response = supabase.table('public_hearing_qa').delete().eq('id', qa_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting Q&A item: {e}")
        return False

def soft_delete_public_hearing_qa(supabase: Client, qa_id: int):
    """Soft delete a Q&A item by marking it as removed"""
    try:
        response = supabase.table('public_hearing_qa').update({'is_removed': True}).eq('id', qa_id).execute()
        return True
    except Exception as e:
        # If is_removed column doesn't exist, fall back to permanent delete with warning
        if "column public_hearing_qa.is_removed does not exist" in str(e):
            st.warning("⚠️ The 'is_removed' column doesn't exist in the database. Please add it to enable soft delete. Using permanent delete instead.")
            return delete_public_hearing_qa(supabase, qa_id)
        else:
            st.error(f"Error removing Q&A item: {e}")
            return False

def restore_public_hearing_qa(supabase: Client, qa_id: int):
    """Restore a soft-deleted Q&A item"""
    try:
        response = supabase.table('public_hearing_qa').update({'is_removed': False}).eq('id', qa_id).execute()
        return True
    except Exception as e:
        st.error(f"Error restoring Q&A item: {e}")
        return False

def get_removed_public_hearing_qa(supabase: Client):
    """Fetch all removed Q&A items from Supabase"""
    try:
        response = supabase.table('public_hearing_qa').select("*").eq('is_removed', True).execute()
        return response.data
    except Exception as e:
        # If is_removed column doesn't exist, return empty list
        if "column public_hearing_qa.is_removed does not exist" in str(e):
            return []
        else:
            st.error(f"Error fetching removed Q&A items: {e}")
            return []

def get_active_public_hearing_qa(supabase: Client):
    """Fetch only active (non-removed) Q&A items from Supabase"""
    try:
        response = supabase.table('public_hearing_qa').select("*").or_('is_removed.is.null,is_removed.eq.false').execute()
        return response.data
    except Exception as e:
        # If is_removed column doesn't exist, fall back to getting all Q&As
        if "column public_hearing_qa.is_removed does not exist" in str(e):
            try:
                response = supabase.table('public_hearing_qa').select("*").execute()
                return response.data
            except Exception as e2:
                st.error(f"Error fetching Q&A items: {e2}")
                return []
        else:
            st.error(f"Error fetching active Q&A items: {e}")
            return []