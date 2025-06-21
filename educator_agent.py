from langgraph.graph import StateGraph, START, END

from state import State
from agent_nodes import (
    component_segregator,
    component_relationship_analyser,
    component_ordering,
    components_pages_planner,
    component_page_processor,
    pages_to_documentation_directory,
    route_based_on_pages_remaining
)


def build_educator_agent():
    """Build and return the compiled educator agent workflow."""
    
    educator_agent_builder = StateGraph(State)

    educator_agent_builder.add_node("component_segregator", component_segregator)
    educator_agent_builder.add_node("component_relationship_analyser", component_relationship_analyser)
    educator_agent_builder.add_node("component_ordering", component_ordering)
    educator_agent_builder.add_node("components_pages_planner", components_pages_planner)
    educator_agent_builder.add_node("component_page_processor", component_page_processor)
    educator_agent_builder.add_node("pages_to_documentation_directory", pages_to_documentation_directory)

    educator_agent_builder.add_edge(START, "component_segregator")
    educator_agent_builder.add_edge("component_segregator", "component_relationship_analyser")
    educator_agent_builder.add_edge("component_relationship_analyser", "component_ordering")
    educator_agent_builder.add_edge("component_ordering", "components_pages_planner")
    educator_agent_builder.add_conditional_edges(
        "components_pages_planner",
        route_based_on_pages_remaining,
        {
            "pages_to_process": "component_page_processor",
            "no_page_to_process": "pages_to_documentation_directory"
        }
    )
    educator_agent_builder.add_conditional_edges(
        "component_page_processor", 
        route_based_on_pages_remaining,
        {
            "pages_to_process": "component_page_processor",
            "no_page_to_process": "pages_to_documentation_directory"
        }
    )
    educator_agent_builder.add_edge("pages_to_documentation_directory", END)

    return educator_agent_builder.compile()


# Create the compiled agent
educator_agent = build_educator_agent() 