from pydantic import BaseModel, constr, field_validator, Field, model_validator
from typing import List, Optional, Any


class CustomersModel(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?1?\d{9,15}$')

    @field_validator('phone_number')
    def phone_number_format(cls, v):
        if not v:
            raise ValueError('Phone number must be provided')
        return v


def convert_arabic_to_western_numbers(value: str) -> str:
    arabic_to_western = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    return ''.join(arabic_to_western.get(char, char) for char in value)


class Accounts(BaseModel):
    bank_name: Optional[str] = None
    account_fullname: Optional[str] = None
    account_number: Optional[str] = None
    account_iban: Optional[str] = None


class Conditions(BaseModel):
    condition_type: str = None
    condition_value: List[str] = []


class Documents(BaseModel):
    name: Optional[str] = None
    path: Optional[str] = None


class Company(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    permit_number: Optional[str] = None
    tax_number: Optional[str] = None
    logo: Optional[str] = None
    accounts: List[Accounts] = []
    documents: List[Documents] = []


class Data(BaseModel):
    company_info: Optional[Company] = None
    conditions: List[Conditions] = []


class InventoryModel(BaseModel):
    product: str
    quantity: int
    price: float
    desc: Optional[str] = None
    barcode: Optional[str] = None

    @field_validator('quantity')
    def quantity_validation(cls, v: Any, values: dict[str, Any], **kwargs):
        if isinstance(v, str):
            # Filter out non-numeric characters
            v = ''.join(filter(str.isdigit, v))
            if not v:
                raise ValueError('يرجى ادخال رقما صالحا')
            convert_arabic_to_western_numbers(v)
            v = int(v)
        if v <= 0:
            raise ValueError('يرجى ادخال رقما صالحا')
        return v

    @field_validator('price')
    def price_validation(cls, v: Any, values: dict[str, Any], **kwargs):
        if isinstance(v, str):
            # Filter out non-numeric characters
            v = ''.join(filter(lambda x: x.isdigit() or x == '.', v))
            if not v:
                raise ValueError('يرجى ادخال سعرا صالحا')
            convert_arabic_to_western_numbers(v)
            v = float(v)
        if v <= 0:
            raise ValueError('يرجى ادخال سعرا صالحا')
        return v

    @field_validator('barcode', mode='before')
    def barcode_validation(cls, v: Optional[str], values: dict[str, Any], **kwargs):
        if v:
            v = convert_arabic_to_western_numbers(v)
            if not v.isdigit() or len(v) != 13:
                raise ValueError('يرجى ادخال باركود صالح')
        return v


class CustomersModel(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def check_phone_number(cls, v: str):
        if len(v) != 10 or not v.startswith('05'):
            raise ValueError('يجب أن يتكون الرقم من عشرة أرقام وأن يبدأ بـ 05')
        return v


class MaintenenceModel(BaseModel):
    cost: float

    @field_validator('cost')
    def check_cost(cls, v: Any):
        if isinstance(v, str):
            # Filter out non-numeric characters
            v = ''.join(filter(lambda x: x.isdigit() or x == '.', v))
            if not v:
                raise ValueError('يرجى ادخال سعرا صالحا')
            convert_arabic_to_western_numbers(v)
            v = float(v)
        if v <= 0:
            raise ValueError('يرجى ادخال سعرا صالحا')
        return v


class ContractModel(BaseModel):
    completion_period: int = Field(description='يجب أن يكون رقما صالحا')
    delay_fine: float = Field(description='يجب أن يكون رقما صالحا')
    total_payment: float = Field(description='يجب أن يكون رقما صالحا')

    @model_validator(mode='before')
    def preprocess_arabic_numbers(cls, values: dict[str, Any]) -> dict[str, Any]:
        for field in ['completion_period', 'delay_fine', 'total_payment']:
            if isinstance(values.get(field), str):
                values[field] = convert_arabic_to_western_numbers(
                    values[field])
        return values

    @field_validator('completion_period')
    def check_completion_period(cls, v: Any) -> int:
        if v <= 0:
            raise ValueError('يرجى ادخال سعرا صالحا')
        return v

    @field_validator('delay_fine')
    def check_delay_fine(cls, v: Any) -> float:
        if v <= 0:
            raise ValueError('يرجى ادخال سعرا صالحا')
        return v

    @field_validator('total_payment')
    def check_total_payment(cls, v: Any) -> float:
        if v <= 0:
            raise ValueError('يرجى ادخال رقما صالحا')
        return v
