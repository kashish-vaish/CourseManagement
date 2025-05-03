import pandas as pd
import requests
import config 
import time
import io
import zipfile
from datetime import datetime



def get_attendance_status(date_filter):
    API_TOKEN = config.qualtricskey
    BASE_URL = config.qualtricsurl
    headers = {
        "x-api-token": API_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.get(f"{BASE_URL}/surveys", headers=headers)

    data= response.json()
    survey_id=""
    for survey in data["result"]["elements"]:
        if survey["name"] == "S25-Data101-Attendance":
            survey_id= survey["id"]

    
    start = f"{date_filter}T00:00:00Z"
    end = f"{date_filter}T23:59:59Z"
    export_payload = {"format":"csv",
                    "startDate": start,
                        "endDate": end
        }
    start_resp = requests.post(f"{BASE_URL}/surveys/{survey_id}/export-responses", json=export_payload, headers=headers)
    print(start_resp.json())
    progress_id = start_resp.json()["result"]["progressId"]

    while True:
        check_resp = requests.get(f"{BASE_URL}/surveys/{survey_id}/export-responses/{progress_id}",headers=headers)
        status = check_resp.json()["result"]["status"]
        if status == "complete":
            file_id = check_resp.json()["result"]["fileId"]
            break
        elif status == "failed":
            raise Exception("Export failed")
        time.sleep(1)

    file_resp = requests.get(f"{BASE_URL}/surveys/{survey_id}/export-responses/{file_id}/file", headers=headers)
    # print(file_resp.headers.get("Content-Type"))

    with zipfile.ZipFile(io.BytesIO(file_resp.content)) as z:
        print(z.namelist());
        with z.open(z.namelist()[0]) as f:
            df = pd.read_csv(f, encoding ="ISO-8859-1")


    df = df.drop(index=[0,1]).reset_index(drop=True)
    data = df[["uid", "StartDate", "EndDate", "Longt", "Lati"]]

    studentlist = pd.read_csv("C:\\Workspace\\Rutgers\\Sem3\\CS142_Data101_Sem3\\Spring 2025\\Logistics\\Attendance\\studentlist.csv")



    data = data[['uid','Longt','Lati']]
    uids_na_coord = data[data['Longt'].isna()]
    data = data.dropna(subset=['Longt'])
    uids_na_coord = uids_na_coord[~uids_na_coord['uid'].isin(data['uid'])]

    studentlist['Attendance'] = studentlist['uid'].isin(data['uid']).map({True: "Present", False: "Absent"})

    return studentlist