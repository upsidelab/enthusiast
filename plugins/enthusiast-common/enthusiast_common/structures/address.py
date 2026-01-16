from dataclasses import dataclass
from typing import Optional


@dataclass
class Address:
    first_name: str
    last_name: str
    address_line1: str
    city: str
    postal_code: str
    country_code: str

    address_line2: Optional[str] = None
    state_or_province: Optional[str] = None
    phone_number: Optional[str] = None
    company: Optional[str] = None
