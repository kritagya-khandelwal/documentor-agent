import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

from models import Component, Relationship


class State(TypedDict):
    files: list[dict]
    project_name: str
    max_components: int
    components: list[Component]
    project_overview: str
    component_relationships: list[Relationship]
    use_cache: bool
    ordered_components: list[int]
    pages_to_process: list[dict]
    pages_processed: int
    pages: Annotated[list[str], operator.add]
    output_directory: str 