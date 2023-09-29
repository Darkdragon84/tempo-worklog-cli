from datetime import date

from tempo_worklog_creator.util.io_util import converter

TODAY = "today"

def process_date_input(date_str: str) -> date:
    if date_str == TODAY:
        return date.today()
    return converter.structure(date_str, date)
