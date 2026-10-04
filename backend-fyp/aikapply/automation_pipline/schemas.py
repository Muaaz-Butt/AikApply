"""
apply_pipeline/schemas.py

Pydantic models that define the exact JSON shape the AI must return.
The LangChain PydanticOutputParser uses these to validate + parse the LLM output.
"""

from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator


class FormField(BaseModel):
    """A single form field to fill."""
    selector: str = Field(
        ..., 
        description="CSS selector, e.g. #student_name or [name='dob']"
    )
    type: str = Field(
        ..., 
        description="text | email | tel | date | number | select | checkbox | radio | textarea | file"
    )
    value: str = Field(
        "", 
        description="Value to fill. Empty string if no match."
    )
    confidence: float = Field(
        0.0, 
        description="Match confidence 0.0–1.0"
    )

    # 🔥 CRITICAL FIX: Convert Booleans/None to strings
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
    action: Literal["fill", "click", "submit", "login_click"] = Field(
        ...,
        description="'fill' to set field values, 'click' to press Next, 'submit' to submit form"
    )
    # Kept so the runner can tell login fills from application fills (used for screenshots)
    page_type: Optional[str] = Field(
        None,
        description="'login' or 'application' for fill actions"
    )
    selector: Optional[str] = Field(
        None, 
        description="CSS selector for click/submit actions"
    )
    fields: Optional[List[FormField]] = Field(
        None, 
        description="Fields list for fill actions"
    )
    wait_ms: Optional[int] = Field(
        900, 
        description="Milliseconds to wait after a click (for React step transition)"
    )


class AutomationResponse(BaseModel):
    """Top-level mapping response saved to media/mappings/<app_id>_mapping.json"""
    application_id: int = Field(
        ..., 
        description="Unique numeric application id"
    )
    url: str = Field(
        ..., 
        description="Target form URL"
    )
    steps: List[Step] = Field(
        ..., 
        description="Ordered list of automation steps"
    )