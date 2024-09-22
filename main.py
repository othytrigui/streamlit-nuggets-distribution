import streamlit as st
import pandas as pd
from io import BytesIO

# Function to calculate the total nuggets for a person
def calculate_total_nuggets(nuggets_list):
    total_nuggets = 0
    for nuggets, percentage in nuggets_list:
        total_nuggets += sum(nuggets) * (percentage / 100)
    return total_nuggets

# Function to generate Excel file
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Recycling nuggets distribution')
    processed_data = output.getvalue()
    return processed_data

# Streamlit app
st.title("Blood recycling nuggets distribution")

# Dictionary to store the people and their respective nugget data
if 'people_nuggets_data' not in st.session_state:
    st.session_state.people_nuggets_data = {}

# Sidebar for adding new person using a form
with st.sidebar:
    st.header("Add a person")
    # Use st.form to allow "Enter" to trigger submission
    with st.form("add_person_form"):
        new_person_name = st.text_input("Person's name")
        submit_button = st.form_submit_button("Add person")
        if submit_button:
            if new_person_name and new_person_name not in st.session_state.people_nuggets_data:
                # Initialize with one nugget input group (with empty numbers and a percentage)
                st.session_state.people_nuggets_data[new_person_name] = [{"nuggets": "", "percentage": 80}]
            else:
                st.warning("Please provide a unique name.")

# Create a tab for each person
if st.session_state.people_nuggets_data:
    tabs = st.tabs(list(st.session_state.people_nuggets_data.keys()))

    for idx, person_name in enumerate(st.session_state.people_nuggets_data):
        with tabs[idx]:
            st.subheader(f"{person_name}'s nuggets calculation")
            
            # Dynamic input for nuggets and percentage
            for nugget_idx, nugget_data in enumerate(st.session_state.people_nuggets_data[person_name]):
                st.write(f"Input group {nugget_idx + 1}")
                
                # Accept comma-separated list of numbers
                numbers_input = st.text_input(f"Enter nuggets (comma separated) for {person_name}", key=f"nuggets_{person_name}_{nugget_idx}", value=nugget_data["nuggets"])
                
                # Update the data in the session state
                st.session_state.people_nuggets_data[person_name][nugget_idx]["nuggets"] = numbers_input
                
                # Select percentage (75%, 80% or 90%)
                percentage = st.selectbox(f"Percentage for this group {person_name}", options=[75, 80, 90], key=f"percentage_{person_name}_{nugget_idx}", index=(0 if nugget_data["percentage"] == 75 else 1 if nugget_data["percentage"] == 80 else 2))

                st.session_state.people_nuggets_data[person_name][nugget_idx]["percentage"] = percentage
            
            # Button to add another input group
            if len(st.session_state.people_nuggets_data[person_name]) < 2:  # Limit to two input groups
                if st.button(f"Add another group for {person_name}", key=f"add_nuggets_{person_name}"):
                    st.session_state.people_nuggets_data[person_name].append({"nuggets": "", "percentage": 80})
                    st.rerun()  # Force rerun to update UI immediately

# Sidebar button to calculate total nuggets for all people
with st.sidebar:
    if st.button("Calculate total for all"):
        # Data for Excel file
        nuggets_data = []

        # Loop through all people to calculate their total nuggets
        for person_name, groups in st.session_state.people_nuggets_data.items():
            total_nuggets = 0
            for group in groups:
                try:
                    numbers_list = list(map(int, group["nuggets"].split(",")))
                    total_nuggets += sum(numbers_list) * (group["percentage"] / 100)
                except ValueError:
                    st.error(f"Please enter valid numbers for {person_name}.")
                    continue
            nuggets_data.append({"Name": person_name, "Total nuggets": total_nuggets})
        
        # Convert to DataFrame
        df = pd.DataFrame(nuggets_data)
        
        # Generate Excel file
        excel_file = to_excel(df)

        # Download Excel file
        st.download_button(
            label="Download excel",
            data=excel_file,
            file_name='recycling_nuggets_distribution.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )