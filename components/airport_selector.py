import streamlit as st
import pandas as pd
import os

def load_airports_data(file_path=None):
    """
    Load airport data from CSV file.
    
    Args:
        file_path (str, optional): Path to the airports CSV file.
        
    Returns:
        pandas.DataFrame: DataFrame containing airport data
    """
    if file_path is None:
        # Default path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(os.path.dirname(current_dir), "docs", "airports.csv")
    
    try:
        airports_df = pd.read_csv(file_path)
        
        # Create a display name column combining code and name
        airports_df['display_name'] = airports_df['code'] + " - " + airports_df['name']
        
        return airports_df
    except Exception as e:
        print(f"Error loading airports data: {str(e)}")
        # Return empty DataFrame if file not found
        return pd.DataFrame(columns=['code', 'name', 'city', 'country', 'display_name'])

def render_airport_selector(key="airport", label="Select Airport"):
    """
    Render an airport selector component.
    
    Args:
        key (str): Key for the component
        label (str): Label to display
        
    Returns:
        str: Selected airport code or None
    """
    # Load airport data if not already in session state
    if 'airports_df' not in st.session_state:
        st.session_state.airports_df = load_airports_data()
    
    airports_df = st.session_state.airports_df
    
    # Create list of options for the selectbox
    options = [""] + airports_df['display_name'].tolist()
    
    # Get the index of the currently selected option
    selected_index = 0
    if key in st.session_state and st.session_state[key]:
        selected_code = st.session_state[key]
        selected_airport = airports_df[airports_df['code'] == selected_code]
        if not selected_airport.empty:
            selected_display = selected_airport['display_name'].iloc[0]
            if selected_display in options:
                selected_index = options.index(selected_display)
    
    # Callback function for when a selection is made
    def on_select():
        selected_option = st.session_state[f"{key}_select"]
        
        # Update selected airport code if a valid option is selected
        if selected_option:
            # Find the matching airport code
            selected_airport = airports_df[airports_df['display_name'] == selected_option]
            
            if not selected_airport.empty:
                # Store the selected airport code
                st.session_state[key] = selected_airport['code'].iloc[0]
            else:
                st.session_state[key] = None
        else:
            st.session_state[key] = None
    
    # Airport selection dropdown with search functionality
    st.selectbox(
        label,
        options=options,
        index=selected_index,
        key=f"{key}_select",
        on_change=on_select,
        placeholder="Search and select airport"
    )
    
    # Return the selected airport code
    return st.session_state.get(key)

