from abc import ABC, abstractmethod
from app.dto.pre_routing_dto import PreRoutingLoggerRequestDTO, PreRoutingLoggerResponseDTO


class PreRoutingLoggerService(ABC):
    """
    Abstract base class for pre-routing logger service.

    Service encapsulates LLM summarization + DB logging.
    Controller / Node only interacts with DTOs, not directly with Session / Repo.
    """

    @abstractmethod
    def handle(self, req: PreRoutingLoggerRequestDTO) -> PreRoutingLoggerResponseDTO:
        """
        Handle pre-routing logging request.

        Args:
            req: Request DTO containing flow information

        Returns:
            Response DTO with flow UUID
        """
        pass
