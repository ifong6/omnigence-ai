# Python Annotations & Decorators Guide for Pydantic & SQLModel

This document explains all decorators, annotations, and special syntax used in our Pydantic and SQLModel models.

---

## Table of Contents

1. [Python Type Annotations](#python-type-annotations)
2. [Pydantic Specific](#pydantic-specific)
3. [SQLModel Specific](#sqlmodel-specific)
4. [SQLAlchemy Specific](#sqlalchemy-specific)
5. [Python Built-in Decorators](#python-built-in-decorators)
6. [Enum Classes](#enum-classes)

---

## Python Type Annotations

### Basic Type Hints

```python
from typing import Optional, List, Dict, Any
```

#### `Optional[T]`
**What it is:** Type hint indicating a value can be of type `T` or `None`
**When to use:** For fields that may not always have a value
**Example:**
```python
age: Optional[int] = None  # Can be int or None
name: Optional[str] = None  # Can be str or None
```

#### `List[T]`
**What it is:** Type hint for a list containing elements of type `T`
**When to use:** For collections of items of the same type
**Example:**
```python
items: List[QuotationItem] = []  # List of QuotationItem objects
tags: List[str] = []  # List of strings
```

#### `Dict[K, V]`
**What it is:** Type hint for a dictionary with keys of type `K` and values of type `V`
**When to use:** For key-value mappings
**Example:**
```python
metadata: Dict[str, Any] = {}  # Keys are strings, values can be anything
prices: Dict[str, Decimal] = {}  # Keys are strings, values are Decimals
```

#### `Any`
**What it is:** Type hint allowing any type
**When to use:** When you genuinely need to accept any type (use sparingly)
**Example:**
```python
data: Any  # Can be anything
```

---

## Pydantic Specific

### `Field()`
**What it is:** Pydantic function to add metadata and validation to model fields
**When to use:** To add constraints, defaults, descriptions, or database column configuration

**Common Parameters:**

```python
from pydantic import Field

# Default values
name: str = Field(default="Unknown")
age: int = Field(default=0)

# Validation constraints
age: int = Field(gt=0)  # Greater than 0
age: int = Field(ge=18)  # Greater than or equal to 18
age: int = Field(lt=100)  # Less than 100
age: int = Field(le=120)  # Less than or equal to 120

price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

# String constraints
name: str = Field(min_length=1, max_length=200)
email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Descriptions (for API docs)
title: str = Field(..., description="Project title")

# Database-specific
client_id: int = Field(foreign_key="Finance.company.id")
name: str = Field(index=True)  # Create database index

# Required field (no default)
name: str = Field(...)  # The ... means required
```

### `ConfigDict`
**What it is:** Pydantic v2 configuration for model behavior
**When to use:** To configure how the model handles data

```python
from pydantic import BaseModel, ConfigDict

class UserDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model to DTO conversion
        populate_by_name=True,  # Allow field population by alias or name
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_assignment=True,  # Validate on assignment, not just init
        arbitrary_types_allowed=True,  # Allow custom types like Decimal
    )
```

**Common Options:**
- `from_attributes=True` - Enables ORM mode (convert SQLModel objects to Pydantic)
- `populate_by_name=True` - Accept both field name and alias
- `str_strip_whitespace=True` - Auto-strip whitespace
- `validate_assignment=True` - Validate when setting attributes after creation
- `arbitrary_types_allowed=True` - Allow non-standard types

### `@property`
**What it is:** Python built-in decorator to create computed/read-only attributes
**When to use:** For calculated fields that should not be stored in the database

```python
class QuotationWithItemsDTO(BaseModel):
    items: List[QuotationItemDTO] = []

    @property
    def total_amount(self) -> Decimal:
        """Computed field - not stored, calculated on access"""
        return sum(item.amount for item in self.items, Decimal("0"))

# Usage:
quote = QuotationWithItemsDTO(items=[...])
print(quote.total_amount)  # Calls the method, returns calculated value
```

### `@validator` (Pydantic v1) / `@field_validator` (Pydantic v2)
**What it is:** Custom validation logic for fields
**When to use:** When built-in validators aren't enough

```python
from pydantic import field_validator, BaseModel

class User(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

---

## SQLModel Specific

### `table=True`
**What it is:** SQLModel parameter to mark a class as a database table
**When to use:** On models that should be mapped to actual database tables

```python
class Company(CompanyBase, table=True):  #  Creates DB table
    __tablename__ = "company"

class CompanyDTO(CompanyBase):  # L No table, just a DTO
    pass
```

### `Relationship()`
**What it is:** SQLModel function to define relationships between tables
**When to use:** To create foreign key relationships (one-to-many, many-to-one, etc.)

```python
from sqlmodel import Relationship

class Quotation(QuotationBase, table=True):
    # One-to-many: one quotation has many items
    items: List["QuotationItem"] = Relationship(back_populates="quotation")

class QuotationItem(QuotationItemBase, table=True):
    # Many-to-one: many items belong to one quotation
    quotation: Optional[Quotation] = Relationship(back_populates="items")
```

**Parameters:**
- `back_populates` - Name of the reverse relationship on the other model
- `sa_relationship_kwargs` - Pass additional SQLAlchemy relationship options

### `__tablename__: str`
**What it is:** SQLAlchemy special attribute to specify the database table name
**When to use:** Always on models with `table=True`

```python
class Company(CompanyBase, table=True):
    __tablename__: str = "company"  # Table will be named "company"
    __tablename__: str = DBTable.COMPANY_TABLE.table  # Using enum helper
```

### `__table_args__`
**What it is:** SQLAlchemy special attribute for table-level configuration
**When to use:** To set schema, indexes, constraints, etc.

```python
from sqlalchemy import Index

# Simple schema specification
class Flow(FlowBase, table=True):
    __table_args__ = {"schema": "Finance"}

# With indexes (must be tuple)
class Company(CompanyBase, table=True):
    __table_args__ = (
        Index("idx_company_alias", "alias"),
        {"schema": "Finance"},  # Must be last in tuple
    )

# Using enum helpers
class Quotation(QuotationBase, table=True):
    __table_args__ = {"schema": DBTable.QUOTATION_TABLE.schema}
```

---

## SQLAlchemy Specific

### `Column()`
**What it is:** SQLAlchemy function to define advanced column properties
**When to use:** For enums, computed columns, or special database column types

```python
from sqlalchemy import Column, Computed, Numeric
from sqlalchemy import Enum as SAEnum

# Enum column
unit: UnitType = Field(
    default=UnitType.Lot,
    sa_column=Column(
        SAEnum(UnitType, name="unit_type", schema="Finance", create_type=False),
        nullable=False,
        server_default="Lot"
    )
)

# Computed column (GENERATED ALWAYS)
amount: Optional[Decimal] = Field(
    default=None,
    sa_column=Column(
        Numeric(12, 2),
        Computed("quantity * unit_price"),  # Database-computed
        nullable=True
    )
)

# Timestamp with timezone
created_at: datetime = Field(
    sa_column=Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
)
```

**Common Column Arguments:**
- `nullable` - Allow NULL values
- `server_default` - Database-side default value
- `Computed()` - Database-computed column (GENERATED ALWAYS)

### `text()`
**What it is:** SQLAlchemy function to specify raw SQL expressions
**When to use:** For SQL functions like `now()` in server defaults

```python
from sqlalchemy import text

created_at: datetime = Field(
    sa_column=Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),  # SQL function
    )
)
```

### `Index()`
**What it is:** SQLAlchemy function to create database indexes
**When to use:** To improve query performance on frequently searched columns

```python
from sqlalchemy import Index

class Company(CompanyBase, table=True):
    __table_args__ = (
        Index("idx_company_alias", "alias"),  # Single column index
        Index("idx_company_name_alias", "name", "alias"),  # Composite index
        {"schema": "Finance"},
    )
```

### `Enum as SAEnum`
**What it is:** SQLAlchemy enum type mapper
**When to use:** To map Python enums to PostgreSQL enum types

```python
from sqlalchemy import Enum as SAEnum
from app.models.enums import UnitType

unit: UnitType = Field(
    sa_column=Column(
        SAEnum(
            UnitType,
            name="unit_type",  # PostgreSQL enum type name
            schema="Finance",  # Schema where enum is defined
            create_type=False  # Don't create enum type (already exists)
        )
    )
)
```

---

## Python Built-in Decorators

### `@property`
**What it is:** Converts a method into a read-only computed attribute
**When to use:** For calculated/derived values

```python
class DBTable(str, Enum):
    FLOW_TABLE = '"Finance".flow'

    @property
    def schema(self) -> str:
        """Computed property - no parentheses needed when accessing"""
        return self.value.split(".")[0].strip('"')

# Usage:
DBTable.FLOW_TABLE.schema  # Returns "Finance" (no parentheses!)
```

### `@classmethod`
**What it is:** Decorator for methods that receive the class as first argument
**When to use:** For factory methods or validators

```python
class User(BaseModel):
    email: str

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Factory method - cls is the class itself"""
        return cls(**data)

# Usage:
user = User.from_dict({"email": "test@example.com"})
```

### `@staticmethod`
**What it is:** Decorator for methods that don't need class or instance
**When to use:** For utility functions logically grouped with a class

```python
# ❌ Without @staticmethod - requires instance
class MathUtils:
    def add(self, a: int, b: int) -> int:
        """Regular method - needs self parameter"""
        return a + b

# Must create instance first
utils = MathUtils()
result = utils.add(5, 3)  # Works, but wasteful

# Or causes error if called on class
# result = MathUtils.add(5, 3)  # ❌ TypeError: missing 1 required positional argument: 'b'
# (Python thinks 5 is 'self', 3 is 'a', and 'b' is missing)

# ✅ With @staticmethod - no instance needed
class MathUtils:
    @staticmethod
    def add(a: int, b: int) -> int:
        """No self or cls parameter needed"""
        return a + b

# Can call directly on class
result = MathUtils.add(5, 3)  # ✅ Clean and efficient
```

---

## Enum Classes

### `Enum` and `str, Enum`
**What it is:** Python's enumeration type for defining named constants
**When to use:** For fixed sets of values (statuses, types, etc.)

```python
from enum import Enum

# Basic enum
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

# String enum (preferred for database values)
class QuotationStatus(str, Enum):
    DRAFTED = "DRAFTED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"

# With custom properties
class DBTable(str, Enum):
    FLOW_TABLE = '"Finance".flow'

    @property
    def table(self) -> str:
        return self.value.split(".")[1]
```

**Why `str, Enum`?**
- Inheriting from both `str` and `Enum` makes enum values serialize as strings
- Better for JSON APIs and database storage
- Type checkers treat them as strings

**Usage:**
```python
status: QuotationStatus = QuotationStatus.DRAFTED
print(status)  # "DRAFTED"
print(status.value)  # "DRAFTED"

# In models
class Quotation(SQLModel, table=True):
    status: str = Field(default="DRAFTED")  # Can use enum value
```

---

## Common Patterns in Our Codebase

### Pattern 1: Base, Table, Create, Update, Row Models

```python
# 1. Base - shared fields
class JobBase(SQLModel):
    """Shared fields for all operations"""
    title: str
    status: str

# 2. Table - actual database table
class DesignJob(JobBase, table=True):
    """Maps to database table"""
    __tablename__: str = "design_job"
    __table_args__ = {"schema": "Finance"}

    id: Optional[int] = Field(default=None, primary_key=True)
    date_created: Optional[datetime] = Field(...)  # DB-generated

# 3. Create - for INSERT operations
class JobCreate(JobBase):
    """No id, no db-generated fields"""
    pass

# 4. Update - for UPDATE operations
class JobUpdate(SQLModel):
    """All fields optional"""
    title: Optional[str] = None
    status: Optional[str] = None

# 5. Row - for SELECT operations
class JobRow(JobBase):
    """Includes all fields including DB-generated"""
    id: int
    date_created: datetime
```

### Pattern 2: DTOs with Validation

```python
from pydantic import BaseModel, Field

class CreateQuotationDTO(BaseModel):
    """Input validation for API"""
    company_id: int = Field(..., gt=0, description="Must be positive")
    items: List[CreateQuotationItemDTO] = Field(..., min_length=1)
    currency: str = Field(default="MOP", min_length=3, max_length=3)
```

### Pattern 3: Foreign Keys and Relationships

```python
class Quotation(QuotationBase, table=True):
    # Foreign key to company
    client_id: int = Field(foreign_key="Finance.company.id")

    # One-to-many relationship
    items: List["QuotationItem"] = Relationship(back_populates="quotation")

class QuotationItem(QuotationItemBase, table=True):
    # Foreign key to quotation
    quotation_id: int = Field(foreign_key="Finance.quotation.id")

    # Many-to-one relationship
    quotation: Optional[Quotation] = Relationship(back_populates="items")
```

---

## Quick Reference Chart

| Annotation/Decorator | Purpose | Layer |
|---------------------|---------|-------|
| `Optional[T]` | Value can be T or None | All |
| `List[T]` | List of T items | All |
| `Field()` | Add validation/constraints | All |
| `ConfigDict` | Model configuration | Pydantic |
| `@property` | Computed attribute | All |
| `table=True` | Mark as DB table | SQLModel |
| `Relationship()` | Define FK relationship | SQLModel |
| `__tablename__` | DB table name | SQLModel |
| `__table_args__` | Schema, indexes | SQLModel |
| `Column()` | Advanced column config | SQLAlchemy |
| `Computed()` | DB-computed column | SQLAlchemy |
| `Index()` | Database index | SQLAlchemy |
| `Enum` | Named constants | Python |

---

## Best Practices

1. **Type Hints**: Always use type hints for better IDE support and type checking
2. **Field Validation**: Use `Field()` constraints instead of custom validators when possible
3. **Enums**: Use `str, Enum` for database-backed enums
4. **Properties**: Use `@property` for computed fields, not stored fields
5. **Model Separation**: Keep Base/Table/Create/Update/Row models separate
6. **DTOs vs Models**: Use DTOs (Pydantic) for API, Models (SQLModel) for DB
7. **Documentation**: Add `description` to Fields for API documentation
8. **Defaults**: Set sensible defaults or make fields Optional

---

## Common Mistakes to Avoid

L **Don't**: Mix database operations in DTOs
```python
class UserDTO(BaseModel):
    def save_to_db(self):  # L DTOs should be pure data
        ...
```

 **Do**: Keep DTOs pure, use services for DB operations
```python
class UserService:
    def create_user(self, dto: UserDTO) -> User:
        return self.repo.create(dto)
```

L **Don't**: Forget `table=True` on database models
```python
class User(UserBase):  # L Won't create table
    __tablename__ = "users"
```

 **Do**: Always add `table=True`
```python
class User(UserBase, table=True):  # 
    __tablename__ = "users"
```

L **Don't**: Include DB-generated fields in Create models
```python
class JobCreate(SQLModel):
    id: int  # L DB generates this
    date_created: datetime  # L DB generates this
```

 **Do**: Exclude DB-generated fields
```python
class JobCreate(SQLModel):
    title: str  #  Only fields user provides
```

---

## Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Python Enums](https://docs.python.org/3/library/enum.html)
