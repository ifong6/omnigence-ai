from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

# ============================================================================
# OUTPUT DTOs (Response Models)
# ============================================================================

class CompanyDTO(BaseModel):
    """
    Base DTO for company responses.

    This represents the data structure returned by service methods.
    It's decoupled from the database model (Company).
    """
    model_config = ConfigDict(from_attributes=True)  # Allows creation from ORM objects

    id: int = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    alias: Optional[str] = Field(None, description="Company alias (e.g., 澳科大)")
    address: Optional[str] = Field(None, description="Company address")
    phone: Optional[str] = Field(None, description="Company phone number")

    # Note: We can add computed fields, format transformations, etc. here
    # without affecting the database model


class CompanyWithStatsDTO(CompanyDTO):
    """
    DTO for company with additional statistics.

    Extends CompanyDTO with computed fields from aggregate queries.
    """
    job_count: int = Field(0, description="Number of jobs associated with this company")
    quotation_count: int = Field(0, description="Number of quotations for this company")
    last_job_date: Optional[str] = Field(None, description="Date of most recent job")

    # Optional: Add more stats as needed
    # total_revenue: Optional[Decimal] = None


class CompanyListResponseDTO(BaseModel):
    """
    DTO for paginated company list responses.

    This wraps a list of companies with metadata (useful for pagination).
    """
    companies: list[CompanyDTO] = Field(..., description="List of companies")
    total_count: int = Field(..., description="Total number of companies")
    limit: Optional[int] = Field(None, description="Applied limit")
    offset: int = Field(0, description="Applied offset")


class CompanySearchResponseDTO(BaseModel):
    """
    DTO for company search results.

    Simple wrapper for search results with count.
    """
    companies: list[CompanyDTO] = Field(..., description="List of matching companies")
    count: int = Field(..., description="Number of results returned")


# ============================================================================
# INPUT DTOs (Request Models)
# ============================================================================

class CreateCompanyDTO(BaseModel):
    """
    DTO for company creation requests.

    This validates input data before it reaches the service layer.
    """
    name: str = Field(
        ...,
        description="Company name (required)",
        min_length=1,
        max_length=200
    )
    alias: Optional[str] = Field(
        None,
        description="Company alias (optional)",
        max_length=64
    )
    address: Optional[str] = Field(
        None,
        description="Company address (optional)",
        max_length=300
    )
    phone: Optional[str] = Field(
        None,
        description="Company phone (optional)",
        max_length=32
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty after stripping whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("Company name cannot be empty or whitespace only")
        return v

    @field_validator('alias', 'address', 'phone')
    @classmethod
    def normalize_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional string fields (strip and return None if empty)."""
        if v is None:
            return None
        v = v.strip()
        return v if v else None


class UpdateCompanyDTO(BaseModel):
    """
    DTO for company update requests.

    All fields are optional (only provided fields will be updated).
    """
    name: Optional[str] = Field(
        None,
        description="New company name",
        min_length=1,
        max_length=200
    )
    alias: Optional[str] = Field(
        None,
        description="New alias",
        max_length=64
    )
    address: Optional[str] = Field(
        None,
        description="New address",
        max_length=300
    )
    phone: Optional[str] = Field(
        None,
        description="New phone",
        max_length=32
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Ensure name is not empty after stripping whitespace."""
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Company name cannot be empty or whitespace only")
        return v

    @field_validator('alias', 'address', 'phone')
    @classmethod
    def normalize_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional string fields (strip and return None if empty)."""
        if v is None:
            return None
        v = v.strip()
        return v if v else None


class GetOrCreateCompanyDTO(BaseModel):
    """
    DTO for get-or-create company requests.

    This is used when you want to ensure a company exists, creating it if needed.
    """
    name: str = Field(
        ...,
        description="Company name (required)",
        min_length=1,
        max_length=200
    )
    address: Optional[str] = Field(
        None,
        description="Company address (optional, used if creating)",
        max_length=300
    )
    phone: Optional[str] = Field(
        None,
        description="Company phone (optional, used if creating)",
        max_length=32
    )
    alias: Optional[str] = Field(
        None,
        description="Company alias (optional, used if creating)",
        max_length=64
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty after stripping whitespace."""
        v = v.strip()
        if not v:
            raise ValueError("Company name cannot be empty or whitespace only")
        return v


class SearchCompanyDTO(BaseModel):
    """
    DTO for company search requests.

    Validates search parameters for company queries.
    """
    query: str = Field(
        ...,
        description="Search term (searches name and alias)",
        min_length=1,
        max_length=200
    )
    limit: int = Field(
        10,
        description="Maximum results to return",
        ge=1,
        le=100
    )
    offset: int = Field(
        0,
        description="Number of results to skip",
        ge=0
    )


# ============================================================================
# OPERATION RESULT DTOs
# ============================================================================

class CompanyCreatedResponseDTO(BaseModel):
    """
    DTO for company creation response.

    Returns the created company with additional metadata.
    """
    company: CompanyDTO = Field(..., description="Created company details")
    message: str = Field(
        default="Company created successfully",
        description="Success message"
    )
    created: bool = Field(True, description="Whether company was newly created")


class CompanyUpdatedResponseDTO(BaseModel):
    """
    DTO for company update response.
    """
    company: CompanyDTO = Field(..., description="Updated company details")
    message: str = Field(
        default="Company updated successfully",
        description="Success message"
    )
    fields_updated: list[str] = Field(
        default_factory=list,
        description="List of updated fields"
    )


class CompanyNotFoundDTO(BaseModel):
    """
    DTO for company not found error.
    """
    error: str = Field(default="Company not found", description="Error message")
    company_id: Optional[int] = Field(None, description="Company ID that was not found")
    company_name: Optional[str] = Field(None, description="Company name that was not found")


class CompanyGetOrCreateResponseDTO(BaseModel):
    """
    DTO for get-or-create company response.

    Indicates whether company was found or created.
    """
    company: CompanyDTO = Field(..., description="Company details")
    created: bool = Field(..., description="True if created, False if found existing")
    message: str = Field(..., description="Operation message")


class CompanyEnrichedResponseDTO(BaseModel):
    """
    DTO for company creation with contact enrichment response.

    Used when company contact info is auto-filled via external search.
    """
    id: int = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    address: Optional[str] = Field(None, description="Company address (may be enriched)")
    phone: Optional[str] = Field(None, description="Company phone (may be enriched)")
    status: str = Field(
        ...,
        description="Status: 'created' or 'existing'"
    )
    enriched: bool = Field(
        False,
        description="True if contact info was auto-enriched"
    )


class CompanyAliasGeneratedResponseDTO(BaseModel):
    """
    DTO for AI-generated alias response.

    Used when company alias is generated via LLM.
    """
    id: int = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    alias: str = Field(..., description="Generated alias")
    address: Optional[str] = Field(None, description="Company address")
    phone: Optional[str] = Field(None, description="Company phone")
    status: str = Field(
        ...,
        description="Status: 'alias_created' or 'alias_updated'"
    )
    message: str = Field(..., description="Success message")


# ============================================================================
# EXAMPLE USAGE IN DOCSTRINGS
# ============================================================================

"""
BEFORE (Without DTOs):
---------------------
# Service returns raw ORM object
company = service.create(name="澳門科技大學", address="澳門氹仔偉龍馬路")
# Problem: Exposes database model directly, no validation

# Service returns plain dict
companies = service.search_by_name("科大")
# Problem: No type safety, unclear structure


AFTER (With DTOs):
------------------
# Input is validated
create_dto = CreateCompanyDTO(
    name="澳門科技大學",
    address="澳門氹仔偉龍馬路",
    phone="+853 8897 1111"
)
# If name is empty, Pydantic raises ValidationError

# Service returns typed DTO
response: CompanyCreatedResponseDTO = service.create_company(create_dto)
company_dto: CompanyDTO = response.company
# IDE knows all fields: company_dto.id, company_dto.name, etc.

# Search returns typed DTO
search_dto = SearchCompanyDTO(query="科大", limit=10)
response: CompanyListResponseDTO = service.search_companies(search_dto)
for company in response.companies:
    print(f"{company.name} ({company.alias})")
# Clear structure, autocomplete works, type-safe


Benefits:
---------
1. Type Safety: IDEs provide autocomplete and catch errors
2. Validation: Pydantic validates input before it reaches business logic
3. Decoupling: Changes to database model don't affect API contracts
4. Documentation: DTOs serve as clear API documentation
5. Flexibility: Can add computed fields, transformations without touching DB models
"""
