import requests
import json
import os

class TimeTree():
    p_token = os.environ['TIMETREE_TOKEN']
    url = 'https://timetreeapis.com'
    headers = {'Authorization': f'Bearer {p_token}',
                "Accept": "application/vnd.timetree.v1+json",
                "Content-Type": "application/json"}
    calendar_id = os.environ['TIMETREE_CALENDAR_ID']

    def add_schedule(self, title, description, date):
        timetree_dict = {
            "data": {
                "attributes": {
                    "title": title,
                    "category": "schedule",
                    "all_day": True,
                    "start_at": date.isoformat(),
                    "end_at": date.isoformat(),
                    "description": description,
                },
                "relationships": {
                    "label": {
                        "data": {
                            "id": f"{self.calendar_id},1",
                            "type": "label"
                        }
                    }
                }
            }
        }
        json_data = json.dumps(timetree_dict)
        response = requests.post(self.url + f"/calendars/{self.calendar_id}/events",
                    headers=self.headers, data=json_data)
        print(response.text)