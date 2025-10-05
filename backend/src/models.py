from typing import List, Optional
from pydantic import BaseModel, Field


class EntityContact(BaseModel):
    name: str
    address: Optional[str] = Field(None, description="The physical address of the entity")
    phone: Optional[str] = Field(None, description="The contact phone number of the entity")
    email: Optional[str] = Field(None, description="The contact email of the entity")
    website: Optional[str] = Field(None, description="The website URL of the entity")
    type: Optional[str] = Field(None, description="The type of entity, e.g., agency, hotel, restaurant, attraction")
    
class ResearchResponse(BaseModel):
    topic: str =Field(..., description="The main topic of the user's query")
    summary: str = Field(..., description="A concise summary of the answer to the user's query") 
    sources: list[str] = Field(..., description="List of sources or documents referenced to generate the summary")
    tools_used  : list[str] = Field(..., description="List of tools used to generate the response, if any")
    entities: List[EntityContact] = Field([], description="List of entities with their contact information extracted from the documents")
    
