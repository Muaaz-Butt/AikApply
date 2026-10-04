# from pydantic import BaseModel, Field
# from typing import List, Optional

# class FieldMapping(BaseModel):
#     selector: str = Field(description="CSS selector, e.g., #first_name")
#     type: str = Field(description="Input type, e.g., text, email, select")
#     value: str = Field(description="The data from the student's profile to insert")
#     confidence: float = Field(description="AI confidence score between 0 and 1")

# class AutomationStep(BaseModel):
#     action: str = Field(description="The action: 'fill', 'click', or 'submit'")
#     selector: Optional[str] = Field(None, description="Selector for button or form")
#     fields: Optional[List[FieldMapping]] = Field(None, description="Fields to fill in this step")

# class AutomationResponse(BaseModel):
#     application_id: int
#     url: str
#     steps: List[AutomationStep]

"""
mapping/schemas.py

Pydantic models that define the exact JSON shape the AI must return.
The LangChain PydanticOutputParser uses these to validate + parse the LLM output.

If you already have a schemas.py, compare it to this one:
  - FormField.wait_ms  is new (for click steps)
  - Step.wait_ms       is new
  - AutomationResponse now has application_id + url at top level
"""

from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator


class FormField(BaseModel):
    """A single form field to fill."""
    selector:   str   = Field(..., description="CSS selector, e.g. #student_name or [name='dob']")
    type:       str   = Field(..., description="text | email | tel | date | number | select | checkbox | radio | textarea | file")
    value:      str   = Field("",  description="Value to fill. Empty string if no match.")
    confidence: float = Field(0.0, description="Match confidence 0.0–1.0")

    # 🔥 THIS IS THE FIX:
    @field_validator('value', mode='before')
    @classmethod
    def ensure_string_value(cls, v: Any) -> str:
        """Converts Booleans or None values to strings to prevent validation errors."""
        if isinstance(v, bool):
            return "true" if v else "false"
        if v is None:
            return ""
        return str(v)


class Step(BaseModel):
    """One step in the automation sequence."""
    action:   Literal["fill", "click", "submit"] = Field(
        ..., description="'fill' to set field values, 'click' to press Next, 'submit' to submit form"
    )
    selector: Optional[str]       = Field(None, description="CSS selector for click/submit actions")
    fields:   Optional[List[FormField]] = Field(None, description="Fields list for fill actions")
    wait_ms:  Optional[int]       = Field(900, description="Milliseconds to wait after a click (for React step transition)")


class AutomationResponse(BaseModel):
    """Top-level mapping response saved to media/mappings/<app_id>_mapping.json"""
    application_id: int         = Field(..., description="Unique numeric application id")
    url:            str         = Field(..., description="Target form URL")
    steps:          List[Step]  = Field(..., description="Ordered list of automation steps")