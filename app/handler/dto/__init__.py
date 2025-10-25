import re
from typing import Optional
from pydantic import BaseModel, field_validator, HttpUrl, Field

class URLPayload(BaseModel):
    url: HttpUrl = Field(..., example="https://example.com/page/")
    customName: Optional[str] = Field(None, example="myBrand")

    @field_validator('url', mode='before')
    def normalizeAndValidateUrl(cls, value: str):
        if isinstance(value, str):
            normalizedValue = value.rstrip('/')
            return normalizedValue
        return value
    
    @field_validator('customName')
    def validate_custom_name(cls, value: str):
        if value is None:
            return value
        if not re.fullmatch(r'[A-Za-z0-9]+', value):
            raise ValueError("customName must contain only letters and numbers (no special characters).")
        return value.strip()
    
class GetCodesPayload(BaseModel):
    limit: int = Field(default=50, ge=1, description="Number of records per page")
    page: int = Field(..., ge=1, description="Page number to retrieve")

class LoginPayload(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
