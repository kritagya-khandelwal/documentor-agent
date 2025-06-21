from pydantic import BaseModel, Field


class Component(BaseModel):
    name: str = Field(description="concise name for the component")
    description: str = Field(description="beginner friendly description of the component")
    files: list[int] = Field(description="list of relevent files indices of the component")


class Components(BaseModel):
    components: list[Component] = Field(description="list of components")


class Relationship(BaseModel):
    from_component: int = Field(description="index of the source component or abstraction")
    to_component: int = Field(description="index of the target component or abstraction")
    label: str = Field(description="brief label for the interaction in just a few words")


class RelationshipAnalysisOutput(BaseModel):
    overview: str = Field(description="A high-level `overview` of the project's main purpose and functionality in a few beginner-friendly paragraphs Use markdown formatting with **bold** and *italic* text to highlight important concepts, don't hesitate to use relevant emojis to make it more engaging")
    relationships: list[Relationship] = Field(description="list of `relationships` between the components")


class OrderedComponents(BaseModel):
    ordered_components: list[int] = Field(description="ordered list of component indices in a list, should include all components and should be a non-repeating valid list of indices") 