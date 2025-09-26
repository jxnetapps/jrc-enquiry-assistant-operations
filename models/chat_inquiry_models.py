from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class ParentType(str, Enum):
    NEW_PARENT = "New Parent"
    EXISTING_PARENT = "Existing Parent"
    PROSPECTIVE_PARENT = "Prospective Parent"

class SchoolType(str, Enum):
    DAY_SCHOOL = "Day School"
    BOARDING_SCHOOL = "Boarding School"
    INTERNATIONAL_SCHOOL = "International School"
    MONTESSORI_SCHOOL = "Montessori School"

class InquiryStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    FOLLOW_UP = "follow_up"
    CONVERTED = "converted"
    REJECTED = "rejected"

class ChatInquiryCreate(BaseModel):
    """Model for creating a new chat inquiry"""
    user_id: Optional[str] = Field(None, description="User ID (optional)")
    parentType: ParentType = Field(..., description="Type of parent")
    schoolType: SchoolType = Field(..., description="Type of school")
    firstName: str = Field(..., min_length=1, max_length=100, description="Parent's first name")
    mobile: str = Field(..., min_length=10, max_length=15, description="Mobile number")
    email: EmailStr = Field(..., description="Email address")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    childName: str = Field(..., min_length=1, max_length=100, description="Child's name")
    grade: str = Field(..., min_length=1, max_length=50, description="Grade/Class")
    academicYear: str = Field(..., min_length=1, max_length=20, description="Academic year")
    dateOfBirth: str = Field(..., description="Date of birth (YYYY-MM-DD format)")
    schoolName: str = Field(..., min_length=1, max_length=200, description="School name")
    
    @validator('mobile')
    def validate_mobile(cls, v):
        """Validate mobile number format"""
        # Remove any non-digit characters
        mobile_digits = ''.join(filter(str.isdigit, v))
        
        # Check if it's a valid Indian mobile number (10 digits)
        if len(mobile_digits) == 10:
            return mobile_digits
        elif len(mobile_digits) == 12 and mobile_digits.startswith('91'):
            # Remove country code
            return mobile_digits[2:]
        else:
            raise ValueError('Mobile number must be 10 digits or 12 digits with country code 91')
    
    @validator('dateOfBirth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth format"""
        try:
            # Try to parse the date
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date of birth must be in YYYY-MM-DD format')
    
    @validator('academicYear')
    def validate_academic_year(cls, v):
        """Validate academic year format"""
        # Expected format: YYYY-YYYY or YYYY-YY
        if '-' in v and len(v.split('-')) == 2:
            parts = v.split('-')
            if len(parts[0]) == 4 and len(parts[1]) in [2, 4]:
                return v
        raise ValueError('Academic year must be in YYYY-YYYY or YYYY-YY format')

class ChatInquiryResponse(BaseModel):
    """Model for chat inquiry response"""
    id: str = Field(..., description="Unique identifier")
    user_id: Optional[str] = Field(None, description="User ID")
    parentType: ParentType
    schoolType: SchoolType
    firstName: str
    mobile: str
    email: str
    city: str
    childName: str
    grade: str
    academicYear: str
    dateOfBirth: str
    schoolName: str
    status: InquiryStatus
    source: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatInquiryUpdate(BaseModel):
    """Model for updating chat inquiry"""
    parentType: Optional[ParentType] = None
    schoolType: Optional[SchoolType] = None
    firstName: Optional[str] = Field(None, min_length=1, max_length=100)
    mobile: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    childName: Optional[str] = Field(None, min_length=1, max_length=100)
    grade: Optional[str] = Field(None, min_length=1, max_length=50)
    academicYear: Optional[str] = Field(None, min_length=1, max_length=20)
    dateOfBirth: Optional[str] = None
    schoolName: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[InquiryStatus] = None
    
    @validator('mobile')
    def validate_mobile(cls, v):
        """Validate mobile number format"""
        if v is None:
            return v
        
        # Remove any non-digit characters
        mobile_digits = ''.join(filter(str.isdigit, v))
        
        # Check if it's a valid Indian mobile number (10 digits)
        if len(mobile_digits) == 10:
            return mobile_digits
        elif len(mobile_digits) == 12 and mobile_digits.startswith('91'):
            # Remove country code
            return mobile_digits[2:]
        else:
            raise ValueError('Mobile number must be 10 digits or 12 digits with country code 91')
    
    @validator('dateOfBirth')
    def validate_date_of_birth(cls, v):
        """Validate date of birth format"""
        if v is None:
            return v
        
        try:
            # Try to parse the date
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date of birth must be in YYYY-MM-DD format')
    
    @validator('academicYear')
    def validate_academic_year(cls, v):
        """Validate academic year format"""
        if v is None:
            return v
        
        # Expected format: YYYY-YYYY or YYYY-YY
        if '-' in v and len(v.split('-')) == 2:
            parts = v.split('-')
            if len(parts[0]) == 4 and len(parts[1]) in [2, 4]:
                return v
        raise ValueError('Academic year must be in YYYY-YYYY or YYYY-YY format')

class InquirySearchRequest(BaseModel):
    """Model for searching inquiries"""
    parentType: Optional[ParentType] = None
    schoolType: Optional[SchoolType] = None
    grade: Optional[str] = None
    city: Optional[str] = None
    status: Optional[InquiryStatus] = None
    search_text: Optional[str] = Field(None, description="Search in name fields")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")

class InquiryStatsResponse(BaseModel):
    """Model for inquiry statistics response"""
    total_inquiries: int
    parent_type_distribution: dict
    school_type_distribution: dict
    status_distribution: dict

class ApiResponse(BaseModel, Generic[T]):
    """Generic API response model"""
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[str] = None
