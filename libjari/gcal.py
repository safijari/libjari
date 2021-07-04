from libjari.jpath import JPath
import traceback
import maya
from dataclasses import dataclass
import requests
import webbrowser

CREDS_CACHE_LOC = JPath.from_home("gcal_creds_cache")
CREDS_CACHE_LOC2 = JPath.from_home("gcal_creds_cache").with_suffix(".json")

auth_url = "https://accounts.google.com/o/oauth2/auth"
scope = "https://www.googleapis.com/auth/calendar"
token_url = "https://www.googleapis.com/oauth2/v3/token"


class Gcal(object):
    def __init__(self, client_id, client_secret):
        super(Gcal, self).__init__()
        self.client_id = client_id
        self.client_secret = client_secret

        if not CREDS_CACHE_LOC.exists() or not CREDS_CACHE_LOC2.exists():
            self.initialize()
        else:
            self.tokens = CREDS_CACHE_LOC2.read_json()

    def initialize(self):
        url = f"{auth_url}?client_id={self.client_id}&response_type=code&scope={scope}&access_type=offline&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        webbrowser.open(url)
        self.auth_code = input("Enter auth code here: ")
        CREDS_CACHE_LOC.write_text(self.auth_code)
        res = requests.post(
            token_url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": self.auth_code,
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "grant_type": "authorization_code",
            },
        )
        assert res.ok, "Unable to get token, unsure what to do now"
        CREDS_CACHE_LOC2.write_json(res.json())
        self.tokens = res.json()

    def refresh(self):
        ref_out = requests.post(
            token_url,
            data={
                "refresh_token": self.tokens["refresh_token"],
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        assert ref_out.ok, "Could not refresh, " + ref_out.text
        self.tokens.update(ref_out.json())
        CREDS_CACHE_LOC2.write_json(self.tokens)

    def get_cal_url(self, calendar_name):
        return (
            f"https://www.googleapis.com/calendar/v3/calendars/{calendar_name}/events"
        )

    def get_recnt_events_for_calendar(self, calendar_name):
        url = self.get_cal_url(calendar_name)
        auth_header = {"Authorization": "Bearer " + self.tokens["access_token"]}
        now = maya.now()
        yesterday = now - maya.timedelta(1)
        tomorrow = now + maya.timedelta(1)
        res = requests.get(
            url,
            headers=auth_header,
            params={"timeMin": yesterday.iso8601(), "timeMax": tomorrow.iso8601()},
        )
        if not res.ok:
            self.refresh()
        return res.json()["items"]


# {'access_token': '', 'expires_in': 3599, 'refresh_token': '', 'scope': 'https://www.googleapis.com/auth/calendar', 'token_type': 'Bearer'}

if __name__ == "__main__":
    from pprint import pprint

    d = JPath.from_home("Dropbox/dots/gcal_creds.json").read_json()
    c = Gcal(d["client_id"], d["secret"])
    for item in c.get_recnt_events_for_calendar("jari@simberobotics.com"):
        # print(item.keys())
        if "start" in item:
            print(item["summary"])
            print(item["start"])
            print(item["end"])
            print(item)
            # print("start" in item)
            # print("end" in item)
        #     try:
        #         m1 = maya.parse(item["start"]["dateTime"]).epoch
        #         m2 = maya.parse(item["end"]["dateTime"]).epoch
        #         print(m1, m2)
        #     except Exception:
        #         pass
