import requests, json
from datetime import datetime, timedelta, time

def handle(req):
    """Boolean value if a time is between 2 other times"""
    def time_inbetween(startTime, endTime, currentTime):
        startTime = datetime.fromisoformat(startTime)
        endTime = datetime.fromisoformat(endTime)
        currentTime = datetime.fromisoformat(currentTime)
        if startTime <= endTime:
            return startTime <= currentTime < endTime

    """Returns a code is a room is free or not at the current time"""
    def free_room_getter(room_code):
        hourNow = datetime.now().strftime("%Y-%m-%d"+"T"+"%H:00:00"+"+00:00")
        semStart = datetime(2019,9,23)
        today = datetime.today()
        monday1 = (semStart - timedelta(days=semStart.weekday()))
        monday2 = (today - timedelta(days=today.weekday()))
        week = int((monday2-monday1).days/7) + 1 # +1 to correct week number to send in data payload
        weekstr = str(week) # string to send in data payload
        eachMondayDate = semStart + timedelta(days=(week-1)*7) # -1 to get correct monday date
        mondayDates = eachMondayDate.strftime("%Y-%m-%d" + "T00:00:00.00Z") # format to correct style for data payload
        url = "https://opentimetable.dcu.ie/broker/api/categoryTypes/1e042cb1-547d-41d4-ae93-a1f2c3d34538/categories/events/filter"
        # Below data and headers varibales are required by POST request to above url so must not be changed
        data = {
                "ViewOptions":{
                "Days":[
                {
                    "Name":"Monday",
                    "DayOfWeek":1,
                    "IsDefault":"true"
                },
                {
                    "Name":"Tuesday",
                    "DayOfWeek":2,
                    "IsDefault":"true"
                },
                {
                    "Name":"Wednesday",
                    "DayOfWeek":3,
                    "IsDefault":"true"
                },
                {
                    "Name":"Thursday",
                    "DayOfWeek":4,
                    "IsDefault":"true"
                },
                {
                    "Name":"Friday",
                    "DayOfWeek":5,
                    "IsDefault":"true"
                }
            ],
            "Weeks":[
                {
                    "WeekNumber":weekstr,
                    "WeekLabel":"Week " + weekstr,
                    "FirstDayInWeek":mondayDates
                }
            ],
            "TimePeriods":[
                {
                    "Description":"All Day",
                    "StartTime":"08:00",
                    "EndTime":"22:00",
                    "IsDefault":"true"
                }
            ],
            "DatePeriods":[
                {
                    "Description":"This Week",
                    "StartDateTime":"2019-09-23T00:00:00.000Z",
                    "EndDateTime":"2020-11-06T00:00:00.000Z",
                    "IsDefault":"true",
                    "IsThisWeek":"true",
                    "IsNextWeek":"false",
                    "Type":"ThisWeek"
                }
            ],
            "LegendItems":[],
            "InstitutionConfig":{},
            "DateConfig":{
                "FirstDayInWeek":1,
                "StartDate":"2019-09-23T00:00:00+00:00",
                "EndDate":"2020-09-29T00:00:00+00:00"
            },
            "AllDays":[
                {
                    "Name":"Monday",
                    "DayOfWeek":1,
                    "IsDefault":"true"
                },
                {
                    "Name":"Tuesday",
                    "DayOfWeek":2,
                    "IsDefault":"true"
                },
                {
                    "Name":"Wednesday",
                    "DayOfWeek":3,
                    "IsDefault":"true"
                },
                {
                    "Name":"Thursday",
                    "DayOfWeek":4,
                    "IsDefault":"true"
                },
                {
                    "Name":"Friday",
                    "DayOfWeek":5,
                    "IsDefault":"true"
                },
                {
                    "Name":"Saturday",
                    "DayOfWeek":6,
                    "IsDefault":"false"
                },
                {
                    "Name":"Sunday",
                    "DayOfWeek":0,
                    "IsDefault":"false"
                }
            ]
            },
            "CategoryIdentities": [
                room_code
            ]
        }

        headers = {
                "Host": "opentimetable.dcu.ie",
                "Connection": "keep-alive",
                "Content-Length": "2077",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://opentimetable.dcu.ie",
                "Authorization": "basic T64Mdy7m[",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.50 Safari/537.36",
                "Content-Type": "application/json",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Referer": "https://opentimetable.dcu.ie/",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cookie": "ARRAffinity=9f44d4a4ced6305a4e654ecb314979befa3e227ad97e82701e115f4276041bc3"
                }
        response = requests.post(url, data=json.dumps(data), headers=headers).json()
        res = json.dumps(response)
        startTimeList = []
        endTimeList = []
        # Uses OpenFaas function to extract all module data from timetable
        room_mod_data = requests.get("http://209.97.128.134:8080/function/module-data", data=res).json()
        # Creates 2 sorted lists containing start and end times of every module in a specific room
        for k, v in room_mod_data.items():
            start_time = startTimeList.append(v[0])
        for k, v in room_mod_data.items():
            end_time = endTimeList.append(v[1])
        startTimeList = sorted(startTimeList)
        endTimeList = sorted(endTimeList)
        # Returns a code if the room is free currently or not
        # by seeing if the current time is between a modules start and end time
        i = 0
        while i < len(startTimeList):
            occupied = time_inbetween(startTimeList[i], endTimeList[i], hourNow)
            if occupied == True:
                break
            i+=1
        if occupied:
            return 601 # Room is not free
        else:
            return 600 # Room in free
    # Main part of handle function
    room = req
    room_code = requests.get("http://209.97.128.134:8080/function/roomdictionary", data=room).json() # Queries a dictionay of unique room identifiers to pass to POST request
    free = free_room_getter(room_code)
    return free