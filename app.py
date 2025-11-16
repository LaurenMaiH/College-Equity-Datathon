import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Affordability Reality Engine",
    page_icon="🏫",
    layout="wide"
)

affordability_df =  pd.read_csv("affordability_raw.csv")
college_selected_raw = pd.read_csv("college_selected_raw.csv")



def main():
    def filter_by_state():
        all_states = pd.unique(affordability_df['State Abbreviation']).tolist()
        if in_out_state_selection == "In-State":
            states = [state]
        elif in_out_state_selection == "Out-of-State":
            states = [s for s in all_states if s != state]
        else:
            states = all_states
        
        
        filtered_df = affordability_df[affordability_df['State Abbreviation'].isin(states)]
        filtered_ids = filtered_df["Unit ID"].tolist()
        return filtered_ids

    def filter_by_tuition(tuition_range):
        lower, upper = tuition_range
        # convert slider to dollars
        lower *= 1000
        upper *= 1000
        if in_out_state_selection == "In-State":
            within_range = college_selected_raw[
                (college_selected_raw["Average In-State Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
                (college_selected_raw["Average In-State Tuition for First-Time, Full-Time Undergraduates"] <= upper)
            ]
            within_range_ids = within_range["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()

        elif in_out_state_selection == "Out-of-State":
            within_range = college_selected_raw[
                (college_selected_raw["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
                (college_selected_raw["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] <= upper)
            ]
            within_range_ids = within_range["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()
        else:
            in_state_ids = affordability_df[affordability_df['State Abbreviation'] == state]["Unit ID"]
            out_of_state_ids = affordability_df[affordability_df['State Abbreviation'] != state]["Unit ID"]

            in_state = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(in_state_ids)]
            out_of_state = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(out_of_state_ids)]
            within_range_in_state = in_state[
                (in_state["Average In-State Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
                (in_state["Average In-State Tuition for First-Time, Full-Time Undergraduates"] <= upper)
            ]
            within_range_out_of_state = out_of_state[
                (out_of_state["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
                (out_of_state["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] <= upper)
            ]

            within_range_ids = within_range_in_state["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist() + within_range_out_of_state["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()
        # names_df = affordability_df[affordability_df["Unit ID"].isin(within_range_ids)]
        # names_list = names_df["Institution Name"].tolist()
        return within_range_ids
    
    def filter_by_max_debt(debt):
        lower, upper = debt
        # convert slider to dollars
        lower *= 1000
        upper *= 1000
        within_range = college_selected_raw[
            (college_selected_raw["Median Debt for Dependent Students"] >= lower) &
            (college_selected_raw["Median Debt for Dependent Students"] <= upper)
        ]
        within_range_ids = within_range["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"]
        # names_df = affordability_df[affordability_df["Unit ID"].isin(within_range_ids)]
        # names_list = names_df["Institution Name"].tolist()
        return within_range_ids.tolist()
    
    def filter_by_minority_serving():
        filtered_df = affordability_df[affordability_df['MSI Status']== 1]
        filtered_ids = filtered_df["Unit ID"].tolist()
        return filtered_ids    

    def filter_by_size(size):
        
        if size == "Small":
            filtered_df = college_selected_raw[college_selected_raw["Number of Undergraduates Enrolled"] <= 5000]
        elif size == "Medium":
            filtered_df = college_selected_raw[college_selected_raw["Number of Undergraduates Enrolled"] > 5000 and college_selected_raw["Number of Undergraduates Enrolled"] <=15000]
        else:
            filtered_df = college_selected_raw[college_selected_raw["Number of Undergraduates Enrolled"] > 15000]
        college_ids = filtered_df["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()
        return college_ids
        
    #     if num_undergrads <= 5000:
    #   return 'Small'
    # elif num_undergrads <= 15000:
    #   return 'Medium'
    # else:
    #   return "Large"

    def process_inputs():
        state_colleges = filter_by_state()
        tuition_colleges = filter_by_tuition(tuition_range)
        debt_colleges = filter_by_max_debt(debt)
        minority_serving_colleges = filter_by_minority_serving()
        size_colleges = filter_by_size(student_body_size_selection)



        college_ids = set(state_colleges) & set(tuition_colleges) & set(debt_colleges) & set(minority_serving_colleges) & set(size_colleges)
        college_names_df = affordability_df[affordability_df["Unit ID"].isin(college_ids)]
        college_names = list(set(college_names_df["Institution Name"].tolist()))


        return college_names


    sentiment_mapping = [1,2,3,4,5]
    
    # load in data

    st.title("Affordability Reality Engine")

    # -------------------------
    # State of Residence
    # -------------------------
    state = st.selectbox(
        "What state do you live in?",
        sorted(pd.unique(affordability_df['State Abbreviation']))
    )

    # -------------------------
    # In-state / Out-of-state
    # -------------------------
    in_out_state = ["In-State", "Out-of-State", "I don't care"]
    in_out_state_selection = st.pills(
        "I'd like to be...'",
        in_out_state,
        key="in_out_pref"
    )
    in_out_state_importance = st.feedback("stars", key="in_out_state_importance")

    # -------------------------
    # Student Body Size
    # -------------------------
    student_body_sizes = ["Large Student Body", "Medium Student Body", "Small Student Body"]
    student_body_size_selection = st.pills(
        "I prefer a...",
        student_body_sizes,
        selection_mode="multi",
        key="student_body"
    )
    student_body_size_importance = st.feedback("stars", key="student_body_importance")

    # # -------------------------
    # # Full-Time or Part-Time Student
    # # -------------------------
    # full_or_part_student = ["Full-Time Student", "Part-Time Student"]
    # full_or_part_student_selection = st.pills(
    #     "Are you a...",
    #     full_or_part_student,
    #     selection_mode="multi",
    #     key="student_status"
    # )
    # full_or_part_importance = st.feedback("stars", key="full_or_part_importance")



    # -------------------------
    # Minority Serving Institutions
    # -------------------------
    minority_serving = [
        "Yes",
        "No"
        
    ]
    minority_serving_selection = st.pills(
        "It's important for me to attend an institution that is a minority-serving institution.",
        minority_serving,
        selection_mode="multi",
        key="minority_serving"
    )
    minority_serving_importance = st.feedback("stars", key="minority_serving_importance")

    # -------------------------
    # Maximum Debt
    # -------------------------
    debt = st.slider(
        "Maximum debt I'm willing to take on (in thousands):",
        0,
        50,
        (15, 35),
        key="debt_slider"
    )
    debt_importance = st.feedback("stars", key="debt_importance")




    # -------------------------
    # Tuition Range
    # -------------------------
    tuition_range = st.slider(
        "Select yearly tuition range (in thousands of dollars):",
        0,
        100,
        (25, 75),
        key="tuition_slider"
    )
    tuition_importance = st.feedback("stars", key="tuition_importance")


    if st.button("GO!"):
        # pass data to function
        colleges = process_inputs()
        st.markdown(", ".join(map(str, colleges)))

# given if the student wants in-state or out-of-state, return College IDs


    










if __name__ == "__main__":
    main()

