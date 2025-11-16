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

# Global variables (copied from notebook)
MSI_Type = {
    'HBCU': 'Historically Black College or University (HBCU)',
    'AANAPISI': 'Asian American or Native American Pacific Islander-Serving Institution (AANAPISI)',
    'ANNHSI': 'Alaska-Native, Native Hawaiian-Serving Institution (ANNHSI)',
    'HSI': 'Hispanic-serving Institution (HSI)',
    'NANTI': 'Native American Non-Tribal Institution (NANTI)',
    'PBI': 'Predominantly Black Institution (PBI)',
    'TCU': 'Tribal College or University (TCU)'
}

Race_Ethnicity_Keywords = ['American Indian', 'Alaska Native', 'Two or More Races', 'Asian', 'Black', 'African American', 'Latino',
                'Native Hawaiian', 'Other Pacific Islander', 'White', 'Race-Ethnicity Unknown']

percent_and_race = {"American Indian": "Percent of American Indian or Alaska Native Undergraduates",
                    "Alaska Native:": "Percent of American Indian or Alaska Native Undergraduates",
                    "Two or More Races": "Percent of Two or More Races Undergraduates",
                    "Asian": "Percent of Asian Undergraduates",
                    "Black": "Percent of Black or African American Undergraduates",
                    "African American": "Percent of Black or African American Undergraduates",
                    "Latino": "Percent of Latino Undergraduates",
                    "Native Hawaiian": "Percent of Native Hawaiian or Other Pacific Islander Undergraduates",
                    "Other Pacific Islander": "Percent of Native Hawaiian or Other Pacific Islander Undergraduates",
                    "White": "Percent of White Undergraduates",
                    "Race-Ethnicity Unknown": "Percent of Race-Ethnicity Unknown Undergraduates"
}

degree_years = [
    "Bachelor's Degree Graduation Rate Within 4 Years - Total",
    "Bachelor's Degree Graduation Rate Within 5 Years - Total",
    "Bachelor's Degree Graduation Rate Within 6 Years - American Indian or Alaska Native",
    "Bachelor's Degree Graduation Rate Within 6 Years - Asian, Native Hawaiian, Pacific Islander",
    "Bachelor's Degree Graduation Rate Within 6 Years - Asian",
    "Bachelor's Degree Graduation Rate Within 6 Years - Black, Non-Latino",
    "Bachelor's Degree Graduation Rate Within 6 Years - Latino",
    "Bachelor's Degree Graduation Rate Within 6 Years - Men",
    "Bachelor's Degree Graduation Rate Within 6 Years - Native Hawaiian or Other Pacific Islander",
    "Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Total",
    "Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Women",
    "Bachelor's Degree Graduation Rate Within 6 Years - White Non-Latino"
]

percent_bachelors_by_race = [
    "Percent of Bachelor Degrees American Indian or Alaska Native Men",
    "Percent of Bachelor Degrees American Indian or Alaska Native Total",
    "Percent of Bachelor Degrees American Indian or Alaska Native Women",
    "Percent of Bachelor Degrees Asian Men",
    "Percent of Bachelor Degrees Asian Total",
    "Percent of Bachelor Degrees Asian Women",
    "Percent of Bachelor Degrees Black or African American Men",
    "Percent of Bachelor Degrees Black or African American Total",
    "Percent of Bachelor Degrees Black or African American Women",
    "Percent of Bachelor Degrees Latino Men",
    "Percent of Bachelor Degrees Latino Total",
    "Percent of Bachelor Degrees Latina Women",
    "Percent of Bachelor Degrees Native Hawaiian or Other Pacific Islander Men",
    "Percent of Bachelor Degrees Native Hawaiian or Other Pacific Islander Total",
    "Percent of Bachelor Degrees Native Hawaiian or Other Pacific Islander Women",
    "Percent of Bachelor Degrees Women",
    "Percent of Bachelor Degrees Men",
    "Percent of Bachelor Degrees White Total",
    "Percent of Bachelor Degrees White Men",
    "Percent of Bachelor Degrees White Women"
]

percent_bachelors_by_field = [
    "Percent of Bachelor Degrees Awarded in Science, Technology, Engineering, and Math",
    "Percent of Bachelor Degrees Awarded in Arts and Humanities",
    "Percent of Bachelor Degrees Awarded in Education",
    "Percent of Bachelor Degrees Awarded in Social Sciences",
    "Percent of Bachelor Degrees Awarded in Health Sciences",
    "Percent of Bachelor Degrees Awarded in Business"
]

dependent_independent = ["Median Debt for Dependent Students", "Median Debt for Independent Students"]

instate_outstate = ["Average In-State Tuition for First-Time, Full-Time Undergraduates",
                    "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"]

# Function definitions (copied from notebook)

def search_msi(name):
  if name not in MSI_Type:
    print(f"Invalid MSI type: {name}. Available types are: {', '.join(MSI_Type.keys())}")
    return pd.DataFrame() # Return an empty DataFrame for invalid input
  column_name = MSI_Type[name]
  filtered_colleges = college_results_cleaned[college_results_cleaned[column_name] == 1]
  return filtered_colleges['Institution Name']

def is_msi(institution):
    matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = college_results_cleaned[matches].copy()
    else:
        print(f"Invalid Institution: {institution}.")
        return pd.DataFrame()
    msi_columns = list(MSI_Type.values())
    sub['Minority Serving Institution'] = (sub[msi_columns] == 1).any(axis=1)
    df = pd.DataFrame({
      "Institution Name": sub["Institution Name"],
      "Minority Serving Institution": sub['Minority Serving Institution']
    })
    return df

def search_percent_by_race_ethnicity(institution, string):
  if string not in percent_and_race:
        print(f"Invalid Race or Ethnicity: {string}. Available Race and Ethnicity options are: {', '.join(percent_and_race.keys())}")
        return pd.DataFrame()
  else:
    column_name = percent_and_race[string]
  if len(college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)) > 0:
    sub = college_results_cleaned[
        college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
    ]
  else:
    print(f"Invalid Institution: {institution}.")
    return pd.DataFrame()
  # Find the graduation rate column specific to the race, if it exists
  grad_column_name = next(
      (col for col in degree_years
        if string.lower() in col.lower() and '6 years - total' not in col.lower()), # Exclude general 6-year total
      None
  )
  # If no specific grad column for race, default to total 6-year graduation rate
  if grad_column_name is None:
      grad_column_name = "Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Total"
      
  df = pd.DataFrame({
      "Institution Name": sub["Institution Name"],
      percent_and_race[string]: sub[column_name],
      "Bachelor's Degree Graduation Rate Within 4 Years - Total": sub["Bachelor's Degree Graduation Rate Within 4 Years - Total"],
      "Bachelor's Degree Graduation Rate Within 5 Years - Total": sub["Bachelor's Degree Graduation Rate Within 5 Years - Total"],
      "Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Total": sub["Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Total"],
      f"Graduation Rate ({string} Specific)": sub[grad_column_name]
  })
  return df

def grad_rate_years(institution, num):
    column_name = next(
        (col for col in degree_years if str(num) in col and "Total" in col), # Ensuring we pick the 'Total' for general years
        None
    )
    if column_name is None:
        print(f"No general graduation rate column contains {num} years.")
        return pd.DataFrame()
    matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
      sub = college_results_cleaned[matches]
    else:
      print(f"Invalid Institution: {institution}.")
      return pd.DataFrame()
    df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        column_name: sub[column_name]
    })
    return df

def percent_nonresident(institution):
  matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
  if matches.sum() >= 1:
    sub = college_results_cleaned[matches]
  else:
    print(f"Invalid Institution: {institution}.")
    return pd.DataFrame()
  df = pd.DataFrame({
      "Institution Name": sub["Institution Name"],
      "Percent of Nonresident Undergraduates": sub["Percent of Nonresident Undergraduates"]
  })
  return df

def percent_bachelors_by_race_ethnicity(institution, race, gender="Total"):
    column_name = next(
        (col for col in percent_bachelors_by_race
         if race.lower() in col.lower() and gender.lower() in col.lower()),
        None
    )
    if column_name is None:
        print(f"Invalid Race or Gender combination: {race} {gender}")
        return pd.DataFrame()
    matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = college_results_cleaned[matches]
    else:
        print(f"Invalid Institution: {institution}.")
        return pd.DataFrame()
    df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        column_name: sub[column_name]
    })
    return df

def percent_of_bachelors_by_field(institution, field):
    column_name = next(
        (col for col in percent_bachelors_by_field
         if field.lower() in col.lower()),
        None
    )
    if column_name is None:
        print(f"Invalid Field: {field}")
        return pd.DataFrame()
    matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = college_results_cleaned[matches]
    else:
        print(f"Invalid Institution: {institution}.")
        return pd.DataFrame()
    df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        column_name: sub[column_name]
    })
    return df

def median_debt(institution, dependence):
    column_name = next(
        (col for col in dependent_independent
         if dependence.lower() in col.lower()),
        None
    )
    if column_name is None:
        print(f"Invalid Field: {dependence}")
        return pd.DataFrame()
    matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = college_results_cleaned[matches]
    else:
        print(f"Invalid Institution: {institution}.")
        return pd.DataFrame()
    df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        column_name: sub[column_name]
    })
    return df

def tuition_by_state_status(institution, status="Out"):
    column_name = next(
        (col for col in instate_outstate
         if status.lower() in col.lower()),
        None
    )
    if column_name is None:
        print(f"Invalid Field: {status}")
        return pd.DataFrame()
    matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = college_results_cleaned[matches]
    else:
        print(f"Invalid Institution: {institution}.")
        return pd.DataFrame()
    df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        column_name: sub[column_name]
    })
    return df

def affordability_gap_df(institution):
  matches = affordability_gap["Institution Name"].str.contains(institution, case=False, na=False)
  if matches.sum() >= 1:
    sub = affordability_gap[matches]
  else:
    print(f"Invalid Institution: {institution}.")
    return pd.DataFrame()
  df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        "Affordability Gap (net price minus income earned working 10 hrs at min wage)": sub["Affordability Gap (net price minus income earned working 10 hrs at min wage)"],
        "Weekly Hours to Close Gap": sub["Weekly Hours to Close Gap"],
        "Income Earned from Working 10 Hours a Week at State's Minimum Wage": sub["Income Earned from Working 10 Hours a Week at State's Minimum Wage"],
    })
  return df

def school_size(institution):
  matches = college_results_cleaned["Institution Name"].str.contains(institution, case=False, na=False)
  if matches.sum() >= 1:
    sub = college_results_cleaned[matches].copy()
  else:
    print(f"Invalid Institution: {institution}.")
    return pd.DataFrame()

  def classify_size(num_undergrads):
    if pd.isna(num_undergrads):
        return np.nan
    if num_undergrads <= 5000:
      return 'Small'
    elif num_undergrads <= 15000:
      return 'Medium'
    else:
      return "Large"

  sub["Size"] = sub["Number of Undergraduates Enrolled"].apply(classify_size)

  df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        "Size": sub["Size"]
    })
  return df

def priv_or_pub(institution):
  matches = affordability_gap["Institution Name"].str.contains(institution, case=False, na=False)
  if matches.sum() >= 1:
      sub = affordability_gap[matches]
  else:
      print(f"Invalid Institution: {institution}.")
      return pd.DataFrame()
  df = pd.DataFrame({
      "Institution Name": sub["Institution Name"],
      'Sector': sub['Sector Name']
  })
  return df

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
        if not ids:
            st.warning("No colleges found after filtering")
            return pd.DataFrame()
        filtered_college = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(ids)][["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION","Median Earnings of Students Working and Not Enrolled 10 Years After Entry", "Median Debt for Dependent Students","Median Debt for Independent Students","Average In-State Tuition for First-Time, Full-Time Undergraduates","Out-of-State Average Tuition for First-Time, Full-Time Undergraduates","Average Amount of Loans Awarded to First-Time, Full-Time Undergraduates","Average Amount of Federal Grant Aid Awarded to First-Time, Full-Time Undergraduates","Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates"]]
        filtered_affordability = affordability_df[affordability_df["Unit ID"].isin(ids)][["Unit ID","Institution Name","MSI Status","Average Work Study Award","Affordability Gap (net price minus income earned working 10 hrs at min wage)","State Abbreviation"]]
        merged = filtered_college.merge(filtered_affordability, left_on="UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION", right_on="Unit ID", how="inner")
        #normalize cols
        if merged.empty:
            st.warning("No colleges matched after merging datasets.")
            return pd.DataFrame()
        numerical_cols = merged.select_dtypes(include=['number']).columns
        numerical_cols = numerical_cols.drop("UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION", errors="ignore")
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
        st.session_state.ranked_colleges = sorted_df["Institution Name"].tolist()[:5]
        scores = sorted_df["score"].tolist()[:5]
        st.markdown(", ".join(map(str, st.session_state.ranked_colleges)))
        st.markdown(", ".join(map(str, scores)))
        if st.session_state.ranked_colleges:
            st.session_state.selected = st.selectbox(
                "Choose a college:",st.session_state.ranked_colleges
            )
            if st.session_state.selected:
                display_college_stats(st.session_state.selected)
    else:
        if not all_weights_filled:
            st.info("Please fill out all the star ratings to enable the button.")
        
 



    # -------------------------
    # Display Metrics
    # -------------------------  

def display_college_stats(institution):
    # Find rows in both datasets
    aff_row = affordability_df[affordability_df["Institution Name"] == institution].iloc[0]
    # Some datasets use different IDs—match using Unit ID
    college_id = aff_row["Unit ID"]
    sel_row = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"] == college_id]
    if sel_row.empty:
        st.error("No detailed statistics found for this institution.")
        return
    sel_row = sel_row.iloc[0]
    st.markdown(f"## 📊 {institution} — Stats Overview")

    # ============ BASIC INFO ===============
    col1, col2, col3 = st.columns(3)
    col1.metric("State", aff_row["State Abbreviation"])
    col2.metric("Undergrad Enrollment", f"{sel_row['Number of Undergraduates Enrolled']:,}")
    col3.metric("MSI Status", "Yes" if aff_row["MSI Status"] == 1 else "No")

    st.divider()
    # ============ TUITION CHART ===============
    st.subheader("Tuition Comparison")
    tuition_data = pd.DataFrame({
        "State Status": ["In-State Tuition", "Out-of-State Tuition"],
        "Cost": [
            sel_row["Average In-State Tuition for First-Time, Full-Time Undergraduates"],
            sel_row["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"]
        ]
    })
    st.bar_chart(tuition_data, x="State Status", y="Cost")
    # ============ DEBT ===============
    st.subheader("Median Student Debt")
    st.metric("Debt", f"${sel_row['Median Debt for Dependent Students']:,}")
    # ============ DEMOGRAPHICS ===============
    race_labels = [
    "American Indian / Alaska Native",       
    "2+ Races",
    "Asian",
    "Black",
    "Latino",
    "Native Hawaiian / Pacific Islander",       
    "White",
    "Unknown"
    ]
    race_label_to_column = {
    "American Indian / Alaska Native": "Percent of American Indian or Alaska Native Undergraduates",
    "2+ Races": "Percent of Two or More Races Undergraduates",
    "Asian": "Percent of Asian Undergraduates",
    "Black": "Percent of Black or African American Undergraduates",
    "Latino": "Percent of Latino Undergraduates",
    "Native Hawaiian / Pacific Islander": "Percent of Native Hawaiian or Other Pacific Islander Undergraduates",
    "White": "Percent of White Undergraduates",
    "Unknown": "Percent of Undergraduates Race-Ethnicity Unknown"
    }
    race_ethnicity_percent_data = pd.DataFrame({
    "Race / Ethnicity": race_labels,
    "Percentage": [sel_row[race_label_to_column[label]] for label in race_labels]
    })
    st.bar_chart(race_ethnicity_percent_data, x="Race / Ethnicity", y="Percentage")
    # ============ BACHELOR DEGREES BY RACE GENDER ===============






if __name__ == "__main__":
    main()

