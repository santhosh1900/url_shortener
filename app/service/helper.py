from datetime import datetime
from typing import Optional
import pytz

class HelperService:

    def __init__(self):
        self.timezone = pytz.timezone("Asia/Kolkata")

    def convertUtcToIst(self, dateTime: Optional[datetime]) -> str:
        if dateTime is None:
            return ''
        if dateTime.tzinfo is None:
            dateTime = pytz.UTC.localize(dateTime)
        result = dateTime.astimezone(self.timezone)
        return result.strftime("%d/%m/%Y : %I:%M:%S %p")
