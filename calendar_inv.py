from ics import Calendar, Event

def create_ics_file(filename: str, event_name: str, start_dt, end_dt):
    # Create a calendar and an event
    c = Calendar()
    e = Event()
    e.name = event_name
    e.begin = start_dt  # e.g. "2025-03-24 12:00:00"
    e.end = end_dt      # e.g. "2025-03-24 13:00:00"
    
    c.events.add(e)
    
    # Save to .ics file
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(c)

if __name__ == "__main__":
    # Example usage:
    create_ics_file(
        filename="my_event.ics",
        event_name="Cool Jiu-Jitsu Class",
        start_dt="2025-03-24 12:00:00",
        end_dt="2025-03-24 13:30:00"
    )
