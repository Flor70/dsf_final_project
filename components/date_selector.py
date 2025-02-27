import streamlit as st
from datetime import datetime, timedelta, date

def render_date_selector(label="Select Date", key="date", min_date=None, max_date=None, default_date=None):
    """
    Render a date selector component.
    
    Args:
        label (str): Label to display
        key (str): Key for the component
        min_date (datetime or date, optional): Minimum allowed date
        max_date (datetime or date, optional): Maximum allowed date
        default_date (datetime or date, optional): Default selected date
        
    Returns:
        date: Selected date
    """
    # Set minimum date (today by default)
    today = date.today()
    
    # Convert datetime to date if needed
    if min_date and isinstance(min_date, datetime):
        min_date = min_date.date()
    else:
        min_date = min_date if min_date else today
    
    if max_date and isinstance(max_date, datetime):
        max_date = max_date.date()
    else:
        max_date = max_date if max_date else (today + timedelta(days=180))
    
    if default_date and isinstance(default_date, datetime):
        default_date = default_date.date()
    else:
        default_date = default_date if default_date else (today + timedelta(days=7))
    
    # Special handling for return date
    if key == "return_date" and "departure_date" in st.session_state:
        departure_date = st.session_state.get("departure_date")
        if departure_date:
            # Ensure min_date is not before departure date
            if min_date < departure_date:
                min_date = departure_date
            
            # Ensure default date is not before min_date
            if default_date < min_date:
                default_date = min_date
    
    # Initialize session state to store the selected date
    if key not in st.session_state:
        st.session_state[key] = default_date
    
    # Ensure the value in session state is valid
    if st.session_state[key] < min_date:
        st.session_state[key] = min_date
    
    # Date selection component with custom format
    try:
        selected_date = st.date_input(
            label,
            value=st.session_state[key],
            min_value=min_date,
            max_value=max_date,
            key=f"{key}_input",
            format="DD/MM/YYYY"
        )
        
        # Validate dates
        if key == "departure_date":
            if selected_date < today:
                st.error("Departure date cannot be in the past.")
                selected_date = today
        
        elif key == "return_date" and "departure_date" in st.session_state:
            departure_date = st.session_state.get("departure_date")
            if departure_date and selected_date < departure_date:
                st.error("Return date cannot be earlier than departure date.")
                selected_date = departure_date
        
        # Update session state with the selected date
        st.session_state[key] = selected_date
    
    except Exception as e:
        st.error(f"Date selection error: {str(e)}")
        # Fallback to a safe value
        if key == "return_date" and "departure_date" in st.session_state:
            selected_date = st.session_state.get("departure_date")
        else:
            selected_date = min_date
        st.session_state[key] = selected_date
    
    return selected_date

