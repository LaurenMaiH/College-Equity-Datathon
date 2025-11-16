import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler



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
        

    def process_inputs():
        state_colleges = filter_by_state()
        tuition_colleges = filter_by_tuition(tuition_range)
        debt_colleges = filter_by_max_debt(debt)
        minority_serving_colleges = filter_by_minority_serving()
        size_colleges = filter_by_size(student_body_size_selection)



        college_ids = list(set(set(state_colleges) & set(tuition_colleges) & set(debt_colleges) & set(minority_serving_colleges) & set(size_colleges)))
        college_names_df = affordability_df[affordability_df["Unit ID"].isin(college_ids)]
        college_names = list(set(college_names_df["Institution Name"].tolist()))


        return college_ids

    def filter_to_found_colleges(ids):
        filtered_college = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(ids)][["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION","Median Earnings of Students Working and Not Enrolled 10 Years After Entry", "Median Debt for Dependent Students","Median Debt for Independent Students","Average In-State Tuition for First-Time, Full-Time Undergraduates","Out-of-State Average Tuition for First-Time, Full-Time Undergraduates","Average Amount of Loans Awarded to First-Time, Full-Time Undergraduates","Average Amount of Federal Grant Aid Awarded to First-Time, Full-Time Undergraduates","Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates"]]
        filtered_affordability = affordability_df[affordability_df["Unit ID"].isin(ids)][["Unit ID","Institution Name","MSI Status","Average Work Study Award","Affordability Gap (net price minus income earned working 10 hrs at min wage)","State Abbreviation"]]
        merged = filtered_college.merge(filtered_affordability, left_on="UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION", right_on="Unit ID", how="inner")
        #normalize cols
        numerical_cols = merged.select_dtypes(include=['number']).columns
        numerical_cols = numerical_cols.drop("UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION")
        scaler = MinMaxScaler()
        merged[numerical_cols] = scaler.fit_transform(merged[numerical_cols])
        
        return merged
    
    def score_and_rank_schools(merged_df, user_weights, column_directions):

        df = merged_df.copy()
        
        # Identify numeric columns to normalize (skip ignored columns)
        numeric_cols = df.select_dtypes(include=["number"]).columns
        numerical_cols = numeric_cols.drop("UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION")

        df["score"] = 0.0
        
        # Compute weighted score
        for col in numerical_cols:
            weight = user_weights.get(col, 0)
            if weight == 0:
                continue  # skip columns the user hasn't weighted
            
            values = df[col]
            
            if column_directions.get(col) == "lower":
                values = 1 - values  # flip for lower_is_better
            
            df["score"] += values * weight
        
        # Sort by score descending
        df = df.sort_values("score", ascending=False).reset_index(drop=True)
        df = df.drop_duplicates(subset="Institution Name", keep="first")

        
        return df
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

    user_weights = {
        "Median Debt for Dependent Students": debt_importance,
        "Median Debt for Independent Students": debt_importance,
        "Average In-State Tuition for First-Time, Full-Time Undergraduates": tuition_importance,
        "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates": tuition_importance,
        "Average Amount of Loans Awarded to First-Time, Full-Time Undergraduates": tuition_importance,
        "Average Amount of Federal Grant Aid Awarded to First-Time, Full-Time Undergraduates": tuition_importance,
        "Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates": tuition_importance,
        "MSI Status": minority_serving_importance,        # will be ignored
        "Average Work Study Award": tuition_importance,
        "Affordability Gap (net price minus income earned working 10 hrs at min wage)": tuition_importance,
    }

    # Column directions (whether higher or lower is better)
    column_directions = {
        "Median Earnings of Students Working and Not Enrolled 10 Years After Entry": "higher",
        "Median Debt for Dependent Students": "lower",
        "Median Debt for Independent Students": "lower",
        "Average In-State Tuition for First-Time, Full-Time Undergraduates": "lower",
        "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates": "lower",
        "Average Amount of Loans Awarded to First-Time, Full-Time Undergraduates": "higher",
        "Average Amount of Federal Grant Aid Awarded to First-Time, Full-Time Undergraduates": "higher",
        "Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates": "higher",
        "Institution Name": "ignore",
        "MSI Status": "higher",
        "Average Work Study Award": "higher",
        "Affordability Gap (net price minus income earned working 10 hrs at min wage)": "lower",
        "State Abbreviation": "ignore"
    }

    all_weights_filled = all(v is not None for v in user_weights.values())

    # Disable button if any weight is None
    if st.button("GO!", disabled=not all_weights_filled):
        colleges = process_inputs()
        merged = filter_to_found_colleges(colleges)
        sorted_df = score_and_rank_schools(merged, user_weights, column_directions)
        print(sorted_df.head(5))
        ranked_colleges = sorted_df["Institution Name"].tolist()[:5]
        scores = sorted_df["score"].tolist()[:5]
        st.markdown(", ".join(map(str, ranked_colleges)))
        st.markdown(", ".join(map(str, scores)))
    else:
        if not all_weights_filled:
            st.info("Please fill out all the star ratings to enable the button.")
        
 




    










if __name__ == "__main__":
    main()

