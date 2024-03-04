from datetime import datetime, timedelta
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = '다운로드_받은_파일경로.json'


creds = None

if os.path.exists('token.pickle'):
   with open('token.pickle', 'rb') as token:
       creds = pickle.load(token)

if not creds or not creds.valid:
   if creds and creds.expired and creds.refresh_token:
       creds.refresh(Request())
   else:
       flow = InstalledAppFlow.from_client_secrets_file(
           CREDENTIALS_FILE, SCOPES)
       creds = flow.run_local_server(port=5090)

   with open('token.pickle', 'wb') as token:
       pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

d = datetime.now().date()
tomorrow = datetime(d.year, d.month, d.day, 10)+timedelta(days=1)
start = tomorrow.isoformat()
end = (tomorrow + timedelta(hours=1)).isoformat()

event_result = service.events().insert(calendarId='primary',
   body={
       'summary': 'Automating calendar',
       'start': {'dateTime': start, 'timeZone': 'Asia/Seoul'},
       'end': {'dateTime': end, 'timeZone': 'Asia/Seoul'},
   }
).execute()

print("created event")
print("id: ", event_result['id'])
print("summary: ", event_result['summary'])
print("starts at: ", event_result['start']['dateTime'])
print("ends at: ", event_result['end']['dateTime'])
