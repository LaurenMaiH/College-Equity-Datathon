import pandas as pd

affordability_df =  pd.read_csv("affordability_raw.csv")
college_selected_raw = pd.read_csv("college_selected_raw.csv")
ids =  [209542, 186380, 100751, 176017, 216339, 199193, 217882, 157085, 218663, 155317, 139959, 123961, 153658, 240444, 167358, 221759, 243780, 238032, 163286, 234076, 178396, 171100, 134237, 170976, 166629, 145637, 139755, 193900, 204024, 100858, 164988, 215293, 130943]
filtered_college = college_selected_raw[college_selected_raw["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION"].isin(ids)][["UNIQUE_IDENTIFICATION_NUMBER_OF_THE_INSTITUTION","Median Earnings of Students Working and Not Enrolled 10 Years After Entry", "Median Debt for Dependent Students","Median Debt for Independent Students","Average In-State Tuition for First-Time, Full-Time Undergraduates","Out-of-State Average Tuition for First-Time, Full-Time Undergraduates","Average Amount of Loans Awarded to First-Time, Full-Time Undergraduates","Average Amount of Federal Grant Aid Awarded to First-Time, Full-Time Undergraduates","Average Amount of Institutional Grant Aid Awarded to First-Time, Full-Time Undergraduates"]]
filtered_college.head(5)

