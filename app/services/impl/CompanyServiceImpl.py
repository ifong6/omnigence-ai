from typing import Optional, List

from sqlalchemy import or_
from sqlmodel import Session, select

from app.models.company_models import Company
from app.services import CompanyService
from app.utils import normalize_string


class CompanyServiceImpl(CompanyService):
    def __init__(self, session: Session):
        """
        Initialize service with database session.

        Args:
            session: Active SQLModel session for database operations
        """
        super().__init__(session)
        self.session = session
        self.model = Company  # ORM table/model class

    # =========================================================================
    # BASIC CRUD
    # =========================================================================

    def get_or_create(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        alias: Optional[str] = None
    ) -> Company:
        """
        Get existing company by name or create new one.

        Args:
            name: Company name (required)
            address: Company address (optional)
            phone: Company phone (optional)
            alias: Company alias (optional)

        Returns:
            Company: Existing or newly created company

        Example:
            >>> with Session(engine) as session:
            ...     service = CompanyServiceImpl(session)
            ...     company = service.get_or_create(
            ...         name="澳門科技大學",
            ...         address="澳門氹仔偉龍馬路"
            ...     )
            ...     session.commit()
        """
        name = name.strip()

        # Try to find existing
        stmt = select(self.model).where(self.model.name == name)
        existing = self.session.exec(stmt).first()
        if existing:
            return existing

        # Create new
        company = self.model(
            name=name,
            address=address,
            phone=phone,
            alias=alias,
        )
        self.session.add(company)
        self.session.flush()
        return company

    def get_by_name(self, name: str) -> Optional[Company]:
        """
        Get company by exact name match.

        Args:
            name: Company name

        Returns:
            Company if found, None otherwise
        """
        stmt = select(self.model).where(self.model.name == name)
        return self.session.exec(stmt).first()

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Get company by ID.

        Args:
            company_id: Company ID

        Returns:
            Company if found, None otherwise
        """
        return self.session.get(self.model, company_id)

    def create(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        alias: Optional[str] = None
    ) -> Company:
        """
        Create a new company.

        Args:
            name: Company name (required)
            address: Company address (optional)
            phone: Company phone (optional)
            alias: Company alias (optional)

        Returns:
            Created company

        Note:
            Remember to call session.commit() after creation
        """
        company = self.model(
            name=name,
            address=address,
            phone=phone,
            alias=alias,
        )
        self.session.add(company)
        self.session.flush()
        return company

    def update(
        self,
        company_id: int,
        *,
        name: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        alias: Optional[str] = None
    ) -> Optional[Company]:
        """
        Update an existing company.

        Args:
            company_id: Company ID to update
            name: New name (optional)
            address: New address (optional)
            phone: New phone (optional)
            alias: New alias (optional)

        Returns:
            Updated company if found, None otherwise

        Note:
            Remember to call session.commit() after update
        """
        company = self.session.get(self.model, company_id)
        if not company:
            return None

        if name is not None:
            company.name = name
        if address is not None:
            company.address = address
        if phone is not None:
            company.phone = phone
        if alias is not None:
            company.alias = alias

        self.session.add(company)
        self.session.flush()
        return company

    def search_by_name(self, search_term: str, limit: int = 10) -> List[Company]:
        """
        Search companies by name or alias.

        Args:
            search_term: Term to search for
            limit: Maximum results to return

        Returns:
            List of matching companies
        """
        search_term = search_term.strip()
        if not search_term:
            return []

        pattern = f"%{search_term}%"
        stmt = (
            select(self.model)
            .where(
                or_(
                    self.model.name.ilike(pattern),  # type: ignore
                    self.model.alias.ilike(pattern),  # type: ignore
                )
            )
            .order_by(self.model.id.desc())  # type: ignore
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    def list_all(self, limit: Optional[int] = None) -> List[Company]:
        """
        Get all companies.

        Args:
            limit: Optional limit on results

        Returns:
            List of all companies
        """
        stmt = select(self.model).order_by(self.model.id.desc())  # type: ignore
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.session.exec(stmt).all())

    # ========================================================================
    # ENHANCED Operations (From tools)
    # ========================================================================

    def create_with_contact_enrichment(
        self,
        *,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        google_search_fn=None
    ) -> dict:
        """
        Create or update company with contact info auto-enrichment.

        This method:
        1. Normalizes inputs
        2. Auto-fills missing address/phone via Google CSE (if provided)
        3. Updates existing company if fields are missing
        4. Creates new record if not found
        """
        if not name or not name.strip():
            raise ValueError("company_name is required and cannot be empty")

        # Normalize inputs
        name = name.strip()
        address = normalize_string(address)
        phone = normalize_string(phone)

        # Try to fetch missing contact info
        if google_search_fn:
            address, phone = self._fetch_missing_contact_info(
                name, address, phone, google_search_fn
            )

        # Check if company exists
        existing = self.get_by_name(name)

        if existing:
            # Update contact info if missing
            current_addr = normalize_string(existing.address)
            current_phone = normalize_string(existing.phone)
            final_addr = current_addr or address
            final_phone = current_phone or phone

            if final_addr != current_addr or final_phone != current_phone:
                updated = self.update(
                    company_id=existing.id,  # type: ignore
                    address=final_addr,
                    phone=final_phone,
                )
                self.session.flush()
                return {
                    "id": updated.id,  # type: ignore
                    "name": updated.name,  # type: ignore
                    "address": updated.address,  # type: ignore
                    "phone": updated.phone,  # type: ignore
                    "status": "existing",
                }
            else:
                return {
                    "id": existing.id,
                    "name": existing.name,
                    "address": existing.address,
                    "phone": existing.phone,
                    "status": "existing",
                }

        # Create new company
        company = self.create(
            name=name,
            address=address,
            phone=phone,
        )
        self.session.flush()

        return {
            "id": company.id,
            "name": company.name,
            "address": company.address,
            "phone": company.phone,
            "status": "created",
        }

    def generate_alias_with_llm(
        self,
        company_id: int,
        llm_fn,
    ) -> dict:
        """
        Generate and assign an intelligent alias using LLM.
        """
        from pydantic import BaseModel

        class CompanyAliasOutput(BaseModel):
            """Output structure for company alias generation."""
            alias: str

        ALIAS_PROMPT = """
            You are an intelligent assistant that generates concise, searchable aliases for company names.

            Company Name: {company_name}

            INSTRUCTIONS:
            1. Generate a short, memorable alias for quick search
            2. Consider common abbreviations, acronyms, or shortened forms
            3. For Chinese companies: simplified versions, common abbreviations
            (e.g., 澳門科技大學 -> 澳科大, 科大)
            4. For English companies: acronyms (IBM), shortened forms (Microsoft)
            5. The alias should be 2-8 characters long when possible

            Examples:
            - 澳門科技大學 → 澳科大
            - 金龍酒店 → 金龍
            - International Business Machines Corporation → IBM
            - 中國建設銀行 → 建行

            Generate ONE clear alias for the company. Output ONLY the alias, nothing else.
            """

        # Get company
        company = self.get_by_id(company_id)
        if not company:
            return {
                "error": "Company not found",
                "status": "not_found",
            }

        current_alias = company.alias

        # Generate alias using LLM
        print(f"[INFO][CompanyService] Generating alias for: {company.name}")
        prompt = ALIAS_PROMPT.format(company_name=company.name)
        alias_output = llm_fn(prompt, config=CompanyAliasOutput)
        generated_alias = alias_output.alias.strip()

        print(f"[INFO][CompanyService] Generated alias: {generated_alias}")

        # Update company
        updated = self.update(
            company_id=company.id,  # type: ignore
            alias=generated_alias,
        )
        self.session.flush()

        if not updated:
            return {
                "error": "Failed to update company with generated alias",
                "status": "error",
            }

        return {
            "id": updated.id,
            "name": updated.name,
            "alias": updated.alias,
            "address": updated.address,
            "phone": updated.phone,
            "status": "alias_created" if not current_alias else "alias_updated",
            "message": f"Successfully generated alias '{generated_alias}' for '{updated.name}'",
        }

    # ============================================================================
    # UTILITY FUNCTIONS
    # ============================================================================

    def _fetch_missing_contact_info(
        self,
        company_name: str,
        address: Optional[str],
        phone: Optional[str],
        google_search_fn,
    ) -> tuple[Optional[str], Optional[str]]:
        """Best-effort enrichment via Google CSE; never blocks DB ops."""
        if address and phone:
            return address, phone
        try:
            found = google_search_fn(company_name) or {}
            address = address or normalize_string(found.get("address"))  # type: ignore
            phone = phone or normalize_string(found.get("phone"))  # type: ignore
        except Exception as e:
            print(f"[WARN][CompanyService] CSE lookup failed: {e}")
        return address, phone
