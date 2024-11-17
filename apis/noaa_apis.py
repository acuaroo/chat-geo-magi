from datetime import datetime, date
from dateutil.parser import parse
import requests
import numpy as np 

url = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateIgrfwmm"

def parse_date(start_time):
    if start_time == "now":
        todays_date = date.today()
        startYear = todays_date.year
        startMonth = todays_date.month
        startDay = todays_date.day
    else:
        parsed_date = parse(start_time, fuzzy=True)
        print(parsed_date)

        startYear = parsed_date.year
        startMonth = parsed_date.month
        startDay = parsed_date.day
    
    return startYear, startMonth, startDay

def general_api(location, start_time, end_time=None):
    if not start_time: 
        start_time = "now"

    geocode_url = f"https://geocode.maps.co/search?q={location}&api_key=66d666e816306477290516jgm9a490d"

    geo_response = requests.get(geocode_url)
    data = geo_response.json()

    if data[0]:
        lat = data[0]["lat"]
        lon = data[0]["lon"]
        
        modelType = "WMM"
        startYear, startMonth, startDay = parse_date(start_time)
        endYear, endMonth, endDay = parse_date(end_time) if end_time else startYear, startMonth, startDay

        if startYear < 1590:
            return False, "Please ask the user for a date later than 1590, as IGRF cannot go past it"
        
        if startYear < 2019:
            modelType = "IGRF"
        
        dates = f"&startYear={startYear}&startMonth={startMonth}&startDay={startDay}&endYear={endYear}&endMonth={endMonth}&endDay={endDay}"
        final_url = url + f"?lat1={lat}&lon1={lon}&model={modelType}{dates}&key=EAU2y&resultFormat=json"

        response = requests.get(final_url)
        resp_data = response.json()

        return True, resp_data["result"]
    else:
        return False, "API has failed!"
    
def magnetic_declination(location, start_time):
    if not start_time or start_time == "": 
        start_time = "now"

    success, result = general_api(location, start_time)

    if not success:
        return result + " Could not find declination."
    
    return f"{result[0]['declination']}deg"
    
def magnetic_inclination(location, start_time):
    if not start_time or start_time == "": 
        start_time = "now"

    success, result = general_api(location, start_time)

    if not success:
        return result + " Could not find inclination."
    
    print(result[0])
    
    return f"{result[0]['inclination']}deg"

def total_intensity(location, start_time):
    if not start_time or start_time == "": 
        start_time = "now"

    success, result = general_api(location, start_time)

    if not success:
        return result + " Could not find the total intensity."
    
    print(result[0])
    
    return f"{result[0]['totalintensity']}nT"