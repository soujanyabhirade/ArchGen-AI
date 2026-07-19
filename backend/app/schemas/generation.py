from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    idea: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="A short product idea, e.g. 'Food Delivery App'",
    )


# ----------------------------
# Microservices
# ----------------------------

class Microservice(BaseModel):
    name: str = Field(..., description="Service name")
    responsibility: str = Field(..., description="Purpose of the service")
    language: str = Field(..., description="Programming language")
    framework: str = Field(..., description="Framework used")
    api_gateway: bool = Field(
        default=False,
        description="True if this service acts as the API Gateway"
    )


# ----------------------------
# Databases
# ----------------------------

class DatabaseRecommendation(BaseModel):
    service: str
    database_type: str
    justification: str


# ----------------------------
# Service Communication
# ----------------------------

class CommunicationLink(BaseModel):
    from_service: str
    to_service: str
    pattern: str = Field(..., description="REST or event-driven")
    broker: str | None = Field(
        default=None,
        description="Kafka, RabbitMQ, etc. Only for event-driven communication."
    )
    justification: str


# ----------------------------
# REST APIs
# ----------------------------

class APIEndpoint(BaseModel):
    method: str
    path: str
    description: str


class ServiceAPIs(BaseModel):
    service: str
    endpoints: list[APIEndpoint]


# ----------------------------
# Technology Stack
# ----------------------------

class TechnologyStack(BaseModel):
    frontend: str
    backend: str
    database: str
    message_broker: str | None = None
    api_gateway: str
    deployment: str


# ----------------------------
# Architecture Quality
# ----------------------------

class ArchitectureScore(BaseModel):
    scalability: int = Field(..., ge=1, le=10)
    security: int = Field(..., ge=1, le=10)
    maintainability: int = Field(..., ge=1, le=10)
    cost_efficiency: int = Field(..., ge=1, le=10)


# ----------------------------
# Complete Architecture
# ----------------------------

class ArchitectureData(BaseModel):
    project_name: str
    description: str

    microservices: list[Microservice]

    databases: list[DatabaseRecommendation]

    communication: list[CommunicationLink]

    apis: list[ServiceAPIs]

    technology_stack: TechnologyStack

    deployment_notes: list[str]

    architecture_score: ArchitectureScore


# ----------------------------
# API Response
# ----------------------------

class GenerationResponse(BaseModel):
    idea: str
    status: str
    message: str
    architecture: ArchitectureData | None = None