from pydantic import BaseModel, Field, validator, ValidationError, root_validator, Optional
from typing import Any, Optional, TypedDict

class Event(BaseModel):
    event_start: str
    event_stop: str
    complex_naming: bool
    video_title: str
    complex_name_format_helper: Optional[str] = None
    title_end_with_date: bool
    
    
    @validator('complex_name_format_helper', always=True, pre=True)
    def check_simple_name_value_based_on_complex_naming(cls, v: Any, values: dict[str, Any]):
        if 'complex_naming' in values and values['complex_naming']:
            if not v:
                raise ValueError('complex_name_format_helper is mandatory when complex_naming is True')
        return v
    
class Inputs(BaseModel):
    day: str
    complex_title_end: Optional[str] = None
    event: Event
    
    # complex_title_end can't be empty if event.complex_naming = true
    @root_validator(pre=True)
    def check_complex_title_end_based_on_event_complex_naming(cls, values: dict[str, Any]):
        event = values.get('event')
        complex_title_end = values.get('complex_title_end')
        if event and event.complex_naming and not complex_title_end:
            raise ValueError('complex_title_end is required when complex_naming is True in the event')
        return values