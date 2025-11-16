# app.py (patched - Option B)
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import altair as alt

st.set_page_config(page_title="Affordability Reality Engine",
                   page_icon="🏫", layout="wide")

#data loading (cached)
@st.cache_data
def load_data():
    affordability_df = pd.read_csv("affordability_raw.csv")
    college_selected_raw = pd.read_csv("college_selected_raw.csv")
    return affordability_df, college_selected_raw

affordability_df, college_selected_raw = load_data()

# helper funcs because this data is so messy
def col_get(row, col_name, default=np.nan):
    return row[col_name] if (hasattr(row, "index") and col_name in row.index) else default

def safe_int(x):
    try:
        return int(x)
    except Exception:
        return x

#filter by user preferences, score & rank
def filter_by_state(state, in_out_pref):
    all_states = pd.unique(affordability_df['State Abbreviation']).tolist()
    if in_out_pref == "In-State":
        states = [state]
    elif in_out_pref == "Out-of-State":
        states = [s for s in all_states if s != state]
    else:
        states = all_states
    filtered_df = affordability_df[affordability_df['State Abbreviation'].isin(states)]
    return filtered_df["Unit ID"].tolist()

def filter_by_tuition(tuition_range, in_out_pref, state):
    lower, upper = tuple(tuition_range)
    lower *= 1000
    upper *= 1000
    if in_out_pref == "In-State":



st.set_page_config(
    page_title="College Finder",
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
  filtered_colleges = affordability_df[affordability_df[column_name] == 1]
  return filtered_colleges['Unit ID']

def is_msi(institution):
    matches = affordability_df["Unit ID"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = affordability_df[matches].copy()
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
  if len(affordability_df["Institution Name"].str.contains(institution, case=False, na=False)) > 0:
    sub = affordability_df[
        affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
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
    matches = affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
      sub = affordability_df[matches]
    else:
      print(f"Invalid Institution: {institution}.")
      return pd.DataFrame()
    df = pd.DataFrame({
        "Institution Name": sub["Institution Name"],
        column_name: sub[column_name]
    })
    return df

def percent_nonresident(institution):
  matches = affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
  if matches.sum() >= 1:
    sub = affordability_df[matches]
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
    matches = affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = affordability_df[matches]
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
    matches = affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = affordability_df[matches]
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
    matches = affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = affordability_df[matches]
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
    matches = affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
    if matches.sum() >= 1:
        sub = affordability_df[matches]
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
  matches = affordability_df["Institution Name"].str.contains(institution, case=False, na=False)
  if matches.sum() >= 1:
    sub = affordability_df[matches].copy()
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

def priv_or_pub():
    filtered_df = affordability_df[affordability_df['Sector']]
    filtered_ids = filtered_df["Unit ID"].tolist()
    return filtered_ids 

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
            (college_selected_raw["Average In-State Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
            (college_selected_raw["Average In-State Tuition for First-Time, Full-Time Undergraduates"] <= upper)
        ]
    elif in_out_pref == "Out-of-State":
        within_range = college_selected_raw[
            (college_selected_raw["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
            (college_selected_raw["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] <= upper)
        ]
    else:
        in_state_ids = affordability_df[affordability_df['State Abbreviation'] == state]["Unit ID"]
        out_of_state_ids = affordability_df[affordability_df['State Abbreviation'] != state]["Unit ID"]
        in_state = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(in_state_ids)]
        out_of_state = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(out_of_state_ids)]
        within_range_in_state = in_state[
            (in_state["Average In-State Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
            (in_state["Average In-State Tuition for First-Time, Full-Time Undergraduates"] <= upper)
        ]
        within_range_out_state = out_of_state[
            (out_of_state["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] >= lower) &
            (out_of_state["Out-of-State Average Tuition for First-Time, Full-Time Undergraduates"] <= upper)
        ]
        within_range = pd.concat([within_range_in_state, within_range_out_state], axis=0)
    return within_range["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()

def filter_by_debt(debt_range):
    lower, upper = tuple(debt_range)
    lower *= 1000
    upper *= 1000
    within_range = college_selected_raw[
        (college_selected_raw["Median Debt for Dependent Students"] >= lower) &
        (college_selected_raw["Median Debt for Dependent Students"] <= upper)
    ]
    return within_range["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()

def filter_by_minority_serving(require_msi):
    if not require_msi:
        return college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()
    msi_units = affordability_df[affordability_df['MSI Status'] == 1]["Unit ID"].tolist()
    filtered = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(msi_units)]
    return filtered["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()

def filter_by_size(size_choice):
    if size_choice == "Small":
        filtered_df = college_selected_raw[college_selected_raw["Number of Undergraduates Enrolled"] <= 5000]
    elif size_choice == "Medium":
        filtered_df = college_selected_raw[(college_selected_raw["Number of Undergraduates Enrolled"] > 5000) &
                                            (college_selected_raw["Number of Undergraduates Enrolled"] <= 15000)]
    else:
        filtered_df = college_selected_raw[college_selected_raw["Number of Undergraduates Enrolled"] > 15000]
    return filtered_df["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].tolist()
        within_range_ids = within_range["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"]
        # names_df = affordability_df[affordability_df["Unit ID"].isin(within_range_ids)]
        # names_list = names_df["Institution Name"].tolist()
        return within_range_ids.tolist()
    
    def filter_by_minority_serving():
        filtered_df = affordability_df[affordability_df['MSI Status']== 0]
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

def merge_and_normalize(ids):
    if not ids:
        return pd.DataFrame()
    filtered_college = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(ids)]
    filtered_afford = affordability_df[affordability_df["Unit ID"].isin(ids)][["Unit ID","Institution Name","MSI Status","Average Work Study Award","Affordability Gap (net price minus income earned working 10 hrs at min wage)","State Abbreviation"]]
    merged = filtered_college.merge(filtered_afford, left_on="UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION", right_on="Unit ID", how="inner")
    if merged.empty:
        return merged
    numeric_cols = [
        "Median Earnings of Students Working and Not Enrolled 10 Years After Entry",
        "Median Debt for Dependent Students",
        "Median Debt for Independent Students",
        "Average In-State Tuition for First-Time, Full-Time Undergraduates",
        "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates",
        "Average Amount of Loans Awarded to First-Time, Full-Time Undergraduates",
        "Average Amount of Federal Grant Aid Awarded to First-Time, Full-Time Undergraduates",
        "Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates",
        "Average Work Study Award",
        "Affordability Gap (net price minus income earned working 10 hrs at min wage)"
    
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

    st.title("College Finder")

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
    numeric_cols = [c for c in numeric_cols if c in merged.columns]
    scaler = MinMaxScaler()
    if numeric_cols:
        merged[numeric_cols] = scaler.fit_transform(merged[numeric_cols].fillna(0))
    return merged

def score_and_rank_schools(merged_df, user_weights, column_directions):
    if merged_df.empty:
        return merged_df
    df = merged_df.copy()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != "UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"]
    df["score"] = 0.0
    for col in numeric_cols:
        weight = user_weights.get(col, 0)
        if weight == 0:
            continue
        vals = df[col].fillna(0)
        if column_directions.get(col) == "lower":
            vals = 1 - vals
        df["score"] += vals * weight
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    return df.drop_duplicates(subset="Institution Name", keep="first")

#session state defaults
def init_session_state_defaults():
    defaults = {
        "selected_college_id": None,
        "selected_college_name": None,
        "ranked_df": None,
        "merged_df": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state_defaults()

#Input panel!
st.title("🏫 College Finder")

with st.sidebar:
    st.markdown("### Profile & Preferences")
    state = st.selectbox("What state do you live in?", sorted(pd.unique(affordability_df['State Abbreviation'])), key="state")
    in_out_pref = st.radio("I'd like to be...", ["In-State", "Out-of-State", "I don't care"], index=2, key="in_out_pref")
    st.markdown("---")

    with st.expander("Cost Preferences", expanded=True):
        col1, col2 = st.columns([3,1])
        with col1:
            tuition_range = st.slider("Select yearly tuition range (thousands $):", 0, 100, (20, 75), step=1, key="tuition_range")
        with col2:
            tuition_importance = st.slider("Importance", 0, 5, 3, key="tuition_importance", help="How important is tuition when ranking colleges?")
        col1, col2 = st.columns([3,1])
        with col1:
            debt_range = st.slider("Maximum debt you're willing to take (thousands $):", 0, 100, (10, 40), step=1, key="debt_range")
        with col2:
            debt_importance = st.slider("Importance", 0, 5, 3, key="debt_importance", help="How important is minimizing debt for you?")
    st.markdown("---")
    with st.expander("Campus Preferences", expanded=False):
        student_body_size = st.selectbox("Preferred student body size", ["Small", "Medium", "Large"], index=1, key="student_body_size")
        size_importance = st.slider("Importance", 0, 5, 3, key="size_importance")
        msi_required = st.checkbox("Require Minority-Serving Institution (MSI)?", key="msi_required")
        msi_importance = st.slider("MSI importance in ranking", 0, 5, 1, key="msi_importance")
    st.markdown("---")

    st.markdown("#### Weights preview (you can tweak importance sliders)")
    user_weights = {
        "Median Debt for Dependent Students": st.session_state.get("debt_importance", 3),
        "Median Debt for Independent Students": st.session_state.get("debt_importance", 3),
        "Average In-State Tuition for First-Time, Full-Time Undergraduates": st.session_state.get("tuition_importance", 3),
        "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates": st.session_state.get("tuition_importance", 3),
        "Average Amount of Loans Awarded to First-Time, Full-Time Undergraduates": st.session_state.get("tuition_importance", 3),
        "Average Amount of Federal Grant Aid Awarded to First-Time, Full-Time Undergraduates": st.session_state.get("tuition_importance", 3),
        "Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates": st.session_state.get("tuition_importance", 3),
        "Average Work Study Award": st.session_state.get("tuition_importance", 3),
        "Affordability Gap (net price minus income earned working 10 hrs at min wage)": st.session_state.get("tuition_importance", 3),
        "MSI Status": st.session_state.get("msi_importance", 1),
        "Median Earnings of Students Working and Not Enrolled 10 Years After Entry": 3
    }
    st.markdown("**Tip:** importance sliders range 0 (ignored) to 5 (crucial).")
    st.markdown("---")

    
    def compute_recommendations_callback():
        # read values from session_state
        state_val = st.session_state["state"]
        in_out_val = st.session_state["in_out_pref"]
        tuition_val = st.session_state["tuition_range"]
        debt_val = st.session_state["debt_range"]
        msi_val = st.session_state["msi_required"]
        size_val = st.session_state["student_body_size"]

        # filters
        state_ids = filter_by_state(state_val, in_out_val)
        tuition_ids = filter_by_tuition(tuition_val, in_out_val, state_val)
        debt_ids = filter_by_debt(debt_val)
        msi_ids = filter_by_minority_serving(msi_val)
        size_ids = filter_by_size(size_val)

        #find intersection of all prefs
        found_ids = list(set(state_ids) & set(tuition_ids) & set(debt_ids) & set(msi_ids) & set(size_ids))
        if not found_ids:
            st.session_state.ranked_df = pd.DataFrame()
            st.session_state.merged_df = pd.DataFrame()

            # show warning after rerun
            st.session_state._last_warning = "No colleges match your filters."
            return

        merged = merge_and_normalize(found_ids)
        if merged.empty:
            st.session_state.ranked_df = pd.DataFrame()
            st.session_state.merged_df = merged
            st.session_state._last_warning = "After merging datasets, no colleges had the required fields."
            return

        # dynamic column directions: default to higher unless known lower
        column_directions = {}
        lower_is_better = {
            "Median Debt for Dependent Students",
            "Median Debt for Independent Students",
            "Average In-State Tuition for First-Time, Full-Time Undergraduates",
            "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates",
            "Affordability Gap (net price minus income earned working 10 hrs at min wage)"
        }
        for c in merged.columns:
            column_directions[c] = "lower" if c in lower_is_better else "higher"

        ranked = score_and_rank_schools(merged, user_weights, column_directions)
        st.session_state.ranked_df = ranked
        st.session_state.merged_df = merged
        st.session_state._last_warning = None

    st.button("GO! Show Recommendations", type="primary", on_click=compute_recommendations_callback, key="go_button")


# output: show warnings or ranked results if they exist in session_state

if st.session_state.get("_last_warning"):
    st.warning(st.session_state._last_warning)

ranked_df = st.session_state.get("ranked_df", None)
merged_df = st.session_state.get("merged_df", None)

if ranked_df is None or ranked_df.empty:
    st.info("No recommendations yet — set filters on the left and click GO!")
else:
    top_n = 9
    top = ranked_df.head(top_n).copy()
    st.subheader(f"Top {min(top_n, len(top))} Recommendations")
    st.markdown("Click a college card's View details button to open its full detail view on the right.")

    cols = st.columns(3)
    # callback to set selected college (safe, no inline mutation during rerun)
    def select_college_callback(unit_id, name):
        st.session_state.selected_college_id = unit_id
        st.session_state.selected_college_name = name

    for i, row in top.reset_index().iterrows():
        c_idx = i % 3
        with cols[c_idx]:
            name = col_get(row, "Institution Name", "Unknown")
            score = round(col_get(row, "score", 0) * 100, 1)
            st.markdown(f"### {name}")
            st.caption(f"Recommendation score: **{score}**")
            sn1, sn2 = st.columns(2)
            earnings = col_get(row, "Median Earnings of Students Working and Not Enrolled 10 Years After Entry", np.nan)
            dep_debt = col_get(row, "Median Debt for Dependent Students", np.nan)
            sn1.metric("Median Earnings (10y)", f"${safe_int(earnings):,}" if not pd.isna(earnings) else "N/A")
            sn2.metric("Median Debt (dependent)", f"${safe_int(dep_debt):,}" if not pd.isna(dep_debt) else "N/A")
            # tuition mini-chart
            tuition_vals = []
            tuition_labels = []
            if "Average In-State Tuition for First-Time, Full-Time Undergraduates" in merged_df.columns:
                tuition_vals.append(col_get(row, "Average In-State Tuition for First-Time, Full-Time Undergraduates", 0))
                tuition_labels.append("In-State")
            if "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates" in merged_df.columns:
                tuition_vals.append(col_get(row, "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates", 0))
                tuition_labels.append("Out-of-State")
            if tuition_vals:
                tdf = pd.DataFrame({"Type": tuition_labels, "Cost": tuition_vals})
                chart = alt.Chart(tdf).mark_bar(size=12).encode(
                    x=alt.X('Cost:Q', title='Cost ($)'),
                    y=alt.Y('Type:N', sort='-x', title=None),
                ).properties(height=80)
                st.altair_chart(chart, use_container_width=True)

            # Use on_click callback with args instead of inline st.button in if-statement
            unit_id = int(col_get(row, "UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION", -1))
            btn_key = f"view_{unit_id}"
            st.button("View details", key=btn_key,
                      on_click=select_college_callback,
                      args=(unit_id, name))

    st.markdown("---")
    st.header("Selected College — Details")
    selected_name = st.session_state.get("selected_college_name", None)
    selected_id = st.session_state.get("selected_college_id", None)
    if selected_name and selected_id:
        aff_row = affordability_df[affordability_df["Unit ID"] == selected_id]
        sel_row = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"] == selected_id]
        if not aff_row.empty and not sel_row.empty:
            aff_row = aff_row.iloc[0]
            sel_row = sel_row.iloc[0]

            st.subheader(selected_name)
            st.metric("State", aff_row.get("State Abbreviation", "N/A"))
            st.metric("Undergraduate Enrollment", f"{safe_int(col_get(sel_row, 'Number of Undergraduates Enrolled', 0)):,}")
            st.metric("MSI Status", "Yes" if col_get(aff_row, "MSI Status", 0) == 1 else "No")

            tabs = st.tabs(["Tuition & Cost", "Debt & Earnings", "Demographics"])
            with tabs[0]:
                st.write("#### Tuition breakdown")
                tuition_df = pd.DataFrame({
                    "Category": ["In-State", "Out-of-State"],
                    "Cost": [
                        col_get(sel_row, "Average In-State Tuition for First-Time, Full-Time Undergraduates", np.nan),
                        col_get(sel_row, "Out-of-State Average Tuition for First-Time, Full-Time Undergraduates", np.nan)
                    ]
                }).dropna()
                if not tuition_df.empty:
                    c = alt.Chart(tuition_df).mark_bar().encode(
                        x=alt.X("Cost:Q", title="Annual Cost ($)"),
                        y=alt.Y("Category:N", sort='-x', title=None)
                    )
                    st.altair_chart(c, use_container_width=True)
                grant = col_get(sel_row, 'Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates', np.nan)
                st.write("**Average Institutional Grant Aid**: ",
                         f"${safe_int(grant):,}" if not pd.isna(grant) else "N/A")

            with tabs[1]:
                st.write("#### Debt & Earnings")
                earnings = col_get(sel_row, "Median Earnings of Students Working and Not Enrolled 10 Years After Entry", np.nan)
                dependent_debt = col_get(sel_row, "Median Debt for Dependent Students", np.nan)
                independent_debt = col_get(sel_row, "Median Debt for Independent Students", np.nan)
                st.metric("Median Earnings (10y)", f"${safe_int(earnings):,}" if not pd.isna(earnings) else "N/A")
                st.metric("Median Debt (Dependent)", f"${safe_int(dependent_debt):,}" if not pd.isna(dependent_debt) else "N/A")
                st.metric("Median Debt (Independent)", f"${safe_int(independent_debt):,}" if not pd.isna(independent_debt) else "N/A")

                if not pd.isna(earnings) and earnings > 0 and not pd.isna(dependent_debt):
                    d_to_e = dependent_debt / earnings
                    st.write(f"**Debt-to-Earnings ratio (dependent debt / earnings)**: {d_to_e:.2f}")
                    gauge_df = pd.DataFrame({"metric": ["Ratio"], "value": [d_to_e]})
                    g = alt.Chart(gauge_df).mark_bar().encode(
                        x=alt.X('value:Q', scale=alt.Scale(domain=[0, max(5, d_to_e + 1)]), title="Debt-to-earnings"),
                        y=alt.Y('metric:N', title=None)
                    ).properties(height=50)
                    st.altair_chart(g, use_container_width=True)

            with tabs[2]:
                st.write("#### Student Race/Ethnicity (percent)")
                race_map = {
                    "American Indian or Alaska Native": "Percent of American Indian or Alaska Native Undergraduates",
                    "Two or More Races": "Percent of Two or More Races Undergraduates",
                    "Asian": "Percent of Asian Undergraduates",
                    "Black": "Percent of Black or African American Undergraduates",
                    "Latino": "Percent of Latino Undergraduates",
                    "Native Hawaiian or Other Pacific Islander": "Percent of Native Hawaiian or Other Pacific Islander Undergraduates",
                    "White": "Percent of White Undergraduates",
                    "Unknown": "Percent of Undergraduates Race-Ethnicity Unknown"
                }
                rows = []
                for label, col in race_map.items():
                    if col in sel_row.index:
                        val = col_get(sel_row, col, np.nan)
                        if not pd.isna(val):
                            rows.append({"race": label, "pct": val})
                rdf = pd.DataFrame(rows)
                if not rdf.empty:
                    pie = alt.Chart(rdf).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="pct", type="quantitative"),
                        color=alt.Color(field="race", type="nominal"),
                        tooltip=["race", "pct"]
                    )
                    st.altair_chart(pie, use_container_width=True)
                else:
                    st.info("No race/ethnicity percentage data available for this institution.")
        else:
            st.error("No detailed statistics found for this institution.")
    else:
        st.info("Select a college card to see details here.")
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
    col3.metric("MSI Status", "Yes" if aff_row["MSI Status"] == 0 else "No")

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
    st.subheader("Percent Undergraduates Enrolled by Race or Ethnicity")
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

st.markdown("---")
with st.container():
    st.caption("Tip: inputs have been made persistent. Use GO to refresh recommendations; click View details to pin a college without losing your filters.")
