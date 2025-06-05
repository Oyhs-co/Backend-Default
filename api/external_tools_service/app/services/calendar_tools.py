import os
from typing import Any, Dict, Optional
from caldav import DAVClient, Calendar
from datetime import datetime

RADICALE_URL = os.getenv("RADICALE_URL", "http://radicale:5232/")
RADICALE_USERNAME = os.getenv("RADICALE_USERNAME", None)
RADICALE_PASSWORD = os.getenv("RADICALE_PASSWORD", None)


def get_caldav_client() -> DAVClient:
    if RADICALE_USERNAME and RADICALE_PASSWORD:
        return DAVClient(RADICALE_URL, username=RADICALE_USERNAME, password=RADICALE_PASSWORD)
    return DAVClient(RADICALE_URL)


def list_calendar_events(calendar_path: str = None) -> Optional[Dict[str, Any]]:
    """
    Lista eventos de un calendario CalDAV (Radicale).
    Si calendar_path es None, usa el primer calendario encontrado.
    """
    client = get_caldav_client()
    principal = client.principal()
    calendars = principal.calendars()
    if not calendars:
        return {"events": []}
    calendar: Calendar = None
    if calendar_path:
        for cal in calendars:
            if cal.url.endswith(calendar_path):
                calendar = cal
                break
    if not calendar:
        calendar = calendars[0]
    events = calendar.events()
    return {"events": [e.vobject_instance.vevent.summary.value for e in events if hasattr(e.vobject_instance, 'vevent')]}


def create_calendar_event(summary: str, dtstart: datetime, dtend: datetime, calendar_path: str = None) -> Dict[str, Any]:
    """
    Crea un evento en un calendario CalDAV (Radicale).
    """
    from icalendar import Event, Calendar as ICalendar
    import uuid
    client = get_caldav_client()
    principal = client.principal()
    calendars = principal.calendars()
    if not calendars:
        raise Exception("No calendars found")
    calendar: Calendar = None
    if calendar_path:
        for cal in calendars:
            if cal.url.endswith(calendar_path):
                calendar = cal
                break
    if not calendar:
        calendar = calendars[0]
    ical = ICalendar()
    event = Event()
    event.add('uid', str(uuid.uuid4()))
    event.add('summary', summary)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    ical.add_component(event)
    calendar.add_event(ical.to_ical().decode())
    return {"status": "created", "summary": summary} 