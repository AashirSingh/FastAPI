from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pickle
import json
import pandas as pd
import numpy as np

class PatientData(BaseModel):
    start_date: str
    end_date: str
    clinic: str

#class Prediction(BaseModel):
    #no_show:bool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

#with open("rf_model_0730.pkl", "rb") as file:
    #model = pickle.load(file)

@app.post("/prediction")
async def predict_no_show(patient_data: PatientData):
    print(f"Start Date: {patient_data.start_date}")
    print(f"End Date: {patient_data.end_date}")
    print(f"Clinic: {patient_data.clinic}")

    input_data = [
        patient_data.start_date,
        patient_data.end_date,
        patient_data.clinic

    ]

#load value
    start_date = patient_data.start_date
    end_date = patient_data.end_date
    clinic_name = patient_data.clinic

    json_output = noshow_output(start_date, end_date, clinic_name) 
    #Returning the JSON structure
    return({"prediction" : json_output})

def noshow_output(start_date, end_date, clinic_name):
    
  
   #-==================================================================
   #Database queries

    import snowflake.connector
    import numpy as np
    import pandas as pd

    conn = snowflake.connector.connect(
        user = "aasingh",
        password = "CensedWizard19",
        account = "cerner-healtheedw_chla",
        database = "CHLA_DB_LMU",
        schema = "CHLA_LMU_SCHEMA"

    )

    cur = conn.cursor()

    clinic_name = "VALENCIA CARE CENTER"
    start_date = pd.to_datetime("2018-08-13")
    end_date = pd.to_datetime("2019-01-01")

    query = f"""
    SELECT * FROM DS_SCHEDULING
    WHERE CLINIC = '{clinic_name}' AND
    APPT_LOCATION LIKE '%Gastroenterology%' AND APPT_LOCATION <>'Gastroenterology' AND APPT_LOCATION <>'MG - Gastroenterology - Glendale'
    AND APPT_LOCATION <>'Gastroenterology Research'
    AND APPT_DATE BETWEEN '{start_date}' AND '{end_date}'
    """

    cur.execute(query)
    results = cur.fetchall()
    df_future_appointments = pd.DataFrame(results, columns = [col[0] for col in cur.description])

    #Subsetting df_future_appointments for unique MRN
    df_unique_mrn = df_future_appointments.drop_duplicates(subset = "MRN", keep = "first")[["MRN"]].copy()
    df_unique_mrn.reset_index(drop=True, inplace=True)

    unique_mrn = df_unique_mrn["MRN"].tolist()
    print(unique_mrn)
    mrn_str = ', '.join("'" + str(mrn) + "'" for mrn in unique_mrn) 

    #Creating df_past_appointments
    query = f"""
    SELECT * FROM DS_SCHEDULING
    WHERE CLINIC = '{clinic_name}' AND
    APPT_LOCATION LIKE '%Gastroenterology%' AND APPT_LOCATION <>'Gastroenterology' AND APPT_LOCATION <>'MG - Gastroenterology - Glendale'
    AND APPT_LOCATION <>'Gastroenterology Research'
    AND APPT_DATE BETWEEN '{start_date}' AND '{end_date}'
    AND MRN IN ({mrn_str})
    """

    cur.execute(query)
    results = cur.fetchall()

    df_past_appointments = pd.DataFrame(results, columns = [col[0] for col in cur.description])

    #Printing out MRN and APPT_ID
    df_past_appointments[["MRN","APPT_ID"]]

    #Closing the connection
    cur.close()
    conn.close()

    #Patient Level Columns
    df_past_appointments['APPT_STATUS'].unique()

    #Total Number of Sucessful Appointments in the past
    df_past_appointments["TOTAL_NUMBER_OF_SUCCESS_APPOINTMENT"] = df_past_appointments.groupby('MRN', group_keys=False)\
    ['APPT_STATUS'].transform(lambda x: (x == 'CHECKED OUT').sum()).astype(int)

    #Total Number of Cancelled Appointment in the past
    df_past_appointments["TOTAL_NUMBER_OF_CANCELLATIONS"] = df_past_appointments.groupby('MRN', group_keys=False)\
    ['APPT_STATUS'].transform(lambda x: (x == 'CANCELED').sum()).astype(int)

    #Total number of Rescheduled Appointments in the past
    df_past_appointments["TOTAL_NUMBER_OF_RESCHEDULED"] = df_past_appointments.groupby('MRN', group_keys=False)\
    ['APPT_STATUS'].transform(lambda x: (x == 'RESCHEDULED').sum()).astype(int)

    #Creating Age
    #get the year of birth date
    df_past_appointments["BIRTH_DATE"].dt.year

    # get the current year
    current_year = pd.to_datetime('today').year
    current_year

    #calculate age
    df_past_appointments["AGE"] = current_year - df_past_appointments["BIRTH_DATE"].dt.year
    df_past_appointments["AGE"]

    #Creating New Columns
    #Make sure APPT_Date is in datetime format
    df_past_appointments['APPT_DATE']=pd.to_datetime(df_past_appointments['APPT_DATE'])

    #Creating new columns
    df_past_appointments['APPT_DATE_ONLY'] = df_past_appointments['APPT_DATE'].dt.date
    df_past_appointments['APPT_TIME_ONLY'] = df_past_appointments['APPT_DATE'].dt.time

    #Appointment Level Columns

    #Appointment Lead Time
    # Difference between the Appt Date and the Book Date
    df_future_appointments["APPT_DATE"] = pd.to_datetime(df_future_appointments["APPT_DATE"])
    df_future_appointments["BOOK_DATE"] = pd.to_datetime(df_future_appointments["BOOK_DATE"])

    df_future_appointments["APPOINTMENT_LEAD_TIME"] = df_future_appointments["APPT_DATE"] - df_future_appointments["BOOK_DATE"]

    df_future_appointments["APPOINTMENT_LEAD_TIME"] = df_future_appointments["APPOINTMENT_LEAD_TIME"].dt.days

    df_future_appointments[["APPOINTMENT_LEAD_TIME"]]

    # Create 'day_of_week' column
    df_future_appointments["DAY_OF_WEEK"] = df_future_appointments["APPT_DATE"].dt.dayofweek
    df_future_appointments["DAY_OF_WEEK"]

    # Create 'week_of_month' column
    df_future_appointments["WEEK_OF_MONTH"] = df_future_appointments["APPT_DATE"].apply(lambda d: (d.day-1)// 7 + 1)

    # Create 'NUM_OFMONTH' column
    df_future_appointments["NUM_OF_MONTH"] = df_future_appointments["APPT_DATE"].dt.month

    # Create 'hour_of_day' column
    df_future_appointments["HOUR_OF_DAY"] = df_future_appointments["APPT_DATE"].dt.hour

    #Creating copy of df_future_appointments
    df_future_appointments_copy = df_future_appointments.copy()

    #Creating copy of df_past_appointments
    df_past_appointments_copy = df_past_appointments.copy()

    #Slicing df's for desired columns

    # slice calculated columns in df_future
    mrn_appt_lvl_df = df_future_appointments_copy[[
                                                            'MRN',
                                                            'APPT_ID',
                                                            'DAY_OF_WEEK',
                                                            'WEEK_OF_MONTH',
                                                            'NUM_OF_MONTH',
                                                            'HOUR_OF_DAY',
                                                            'APPOINTMENT_LEAD_TIME']]

    #slice calculated columns in df_past
    mrn_lvl_df = df_past_appointments_copy[["MRN",
                                            "TOTAL_NUMBER_OF_SUCCESS_APPOINTMENT",
                                            "TOTAL_NUMBER_OF_CANCELLATIONS",
                                            "TOTAL_NUMBER_OF_RESCHEDULED",
                                            "AGE"]]
    mrn_lvl_df_new = mrn_lvl_df.drop_duplicates()

    #combining two dataframes
    df_prediction_input = mrn_appt_lvl_df.merge(mrn_lvl_df_new, on="MRN")

    #Rearranging dataframe
    df_prediction_input = df_prediction_input[['MRN','APPT_ID','APPOINTMENT_LEAD_TIME','TOTAL_NUMBER_OF_CANCELLATIONS','TOTAL_NUMBER_OF_RESCHEDULED','TOTAL_NUMBER_OF_SUCCESS_APPOINTMENT','DAY_OF_WEEK','WEEK_OF_MONTH','NUM_OF_MONTH','HOUR_OF_DAY','AGE']]

    #Creating output df
    df_prediction_output = pd.DataFrame(columns = ["mrn", "appt_id", "appt_date", "appt_time", "predicted_no_show"])

    #Filling in no-show columns
    model_filename = "rf_model_0730.pkl"

    df_input = df_prediction_input.drop(["MRN","APPT_ID"], axis=1)

    with open(model_filename, "rb") as file:
        model = pickle.load(file)

    for i, row in df_input.iterrows():
        prediction = model.predict(df_input.iloc[[i]])

        df_prediction_output.at[i, 'predicted_no_show'] = prediction[0]

    #Filling in other columns
    for idx in range(0, len(df_prediction_output)):
        parameters = df_prediction_input.drop(["MRN","APPT_ID"], axis=1).iloc[[idx]]
        prediction =  model.predict(parameters)
        
        for i in df_prediction_output.index:
            df_prediction_output.loc[i,'mrn'] = df_prediction_input.loc[i,'MRN']
            df_prediction_output.loc[i,'appt_id'] = df_prediction_input.loc[i,'APPT_ID']

            mrn_output = df_prediction_output.loc[i,'mrn']

            if mrn_output in df_past_appointments['MRN'].values:
                past_appointment_row = df_past_appointments[df_past_appointments['MRN'] == mrn_output]

                df_prediction_output.loc[i,'appt_date'] = past_appointment_row['APPT_DATE_ONLY'].values[0]
        
            if mrn_output in df_past_appointments['MRN'].values:
                past_appointment_row = df_past_appointments[df_past_appointments['MRN'] == mrn_output]

                df_prediction_output.loc[i,'appt_time'] = past_appointment_row['APPT_TIME_ONLY'].values[0]
        
    #Calculating total number of appointments
    total_number_of_appointments = len(df_prediction_output)
    print("Total Number of Appointments: ", total_number_of_appointments)

    #Calculating total number of now shows
    def count_noshow(df_prediction_output, predicted_no_show):
        return (df_prediction_output[predicted_no_show] == 0).sum()

    Total_number_of_predicted_no_show = count_noshow(df_prediction_output, "predicted_no_show")
    print("Total Number of predicted no show: ", Total_number_of_predicted_no_show )

    #Changing date and time to string
    df_prediction_output['appt_date'] = df_prediction_output['appt_date'].astype(str)
    df_prediction_output['appt_time'] = df_prediction_output['appt_time'].astype(str)
        

    #Converting the dataframe to a list of dictionaries
    data_list = df_prediction_output.to_dict('records')

    #Calculating summary information
    total_num_appt = len(df_prediction_output)
    total_num_noshow = len(df_prediction_output[df_prediction_output['predicted_no_show'] == 1])

    #Constructing JSON object
    json_structure = {
            "noshow_table":data_list,
            "noshow_summary":[
            {
                "total_num_appt":total_num_appt,
                "total_num_noshow":total_num_noshow
            }
        ]
    }
    #Convert object to JSON string
    json_string = json.dumps(json_structure)

    return(json_string)
  






