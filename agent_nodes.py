import os
from langchain_openai import ChatOpenAI

from models import Components, RelationshipAnalysisOutput, OrderedComponents
from state import State


def component_segregator(state: State):
    file_context, file_listing = "", ""
    for i, file in enumerate(state["files"]): 
        file_context += f"--- File Index {i}: path: {file['path']} ---\n{file['content']}\n\n"
        file_listing += f"- {i} # {file['path']}\n"

    llm_context = f"""
For the project {state["project_name"]}:

Codebase files context:
{file_context}

Analyse the codebase.
Identify the top 4-{state["max_components"]} core most important abstractions or components to help the new user understand the codebase.

For each component, provide:
- name: concise name for the component
- description: beginner friendly description of the component
- files: list of relevent files indices of the component

List of file indices and paths in the codebase context:
{file_listing}

Return the components in a structured format.
    """

    component_segregation_llm = ChatOpenAI(
            model="gemini-2.5-flash-lite-preview-06-17", 
            temperature=0, 
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    
    component_segregation_llm_with_structured_output = component_segregation_llm.with_structured_output(Components)
    
    components = component_segregation_llm_with_structured_output.invoke(llm_context)

    print(f"created {len(components.components)} components")

    return {"components": components.components}


def component_relationship_analyser(state: State):
    component_context = "Identified Components or Abstractions:\n"
    component_listing = ""
    relevant_file_indices = set()
    for i, component in enumerate(state["components"]):
        component_context += f"- Index {i}: {component.name} (Relevant file indices: [{', '.join(map(str, component.files))}])\n    Description: {component.description}\n"
        component_listing += f"- {i} # {component.name}\n"
        relevant_file_indices.update(component.files)
    component_context += f"Relevant File Snippets referenced by index and path:\n"
    for i in sorted(list(relevant_file_indices)):
        if i < 0 or i >= len(state["files"]): continue
        component_context += f"\n\n- {i} # {state['files'][i]['path']}\n{state['files'][i]['content']}\n"
    
    llm_context = f"""
Based on the following abstractions or components and the relevant file snippets from the project {state["project_name"]}:

List of Component or Abstraction Indices and Names: 
{component_listing}

Context of Components or Abstractions:
{component_context}

Provide:
1. A high-level `overview` of the project's main purpose and functionality in a few beginner-friendly paragraphs. Use markdown formatting with **bold** and *italic* text to highlight important concepts, don't hesitate to use relevant emojis to make it more engaging.
2. A list (`relationships`) describing the key interactions between these abstractions. For each relationship, specify:
- `from_component`: Index of the source component or abstraction (e.g., `0 # ComponentName1`)
- `to_component`: Index of the target component or abstraction (e.g., `1 # ComponentName2`)
- `label`: A brief label for the interaction **in just a few words** (e.g., "Manages", "Inherits", "Uses").
Ideally the relationship should be backed by one component or abstraction calling or passing parameters to another.
Simplify the relationship and exclude those non-important ones.

IMPORTANT: Make sure EVERY component or abstraction is involved in at least ONE relationship (either as source or target). Each component or abstraction index must appear at least once across all relationships.
    """
    component_relationship_analyser_llm = ChatOpenAI(
            model="gemini-2.5-flash-lite-preview-06-17", 
            temperature=0, 
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    component_relationship_analyser_llm_with_structured_output = component_relationship_analyser_llm.with_structured_output(RelationshipAnalysisOutput)

    relationship_analysis = component_relationship_analyser_llm_with_structured_output.invoke(llm_context)

    print(relationship_analysis)

    return {"project_overview": relationship_analysis.overview, "component_relationships": relationship_analysis.relationships}


def component_ordering(state: State):
    components_list = "\n".join([f"- {i} # {component.name}" for i, component in enumerate(state["components"])])
    relationships_list = "\n".join([f"- from {state['components'][relationship.from_component].name} to {state['components'][relationship.to_component].name}: ({relationship.label})" for relationship in state["component_relationships"]])
    
    llm_context = f"""

Given the following project abstractions and their relationships for the project {state["project_name"]}:

Components or Abstractions (Index # Name):

{components_list}

Project Overview: 
{state["project_overview"]}

Relationships between Components:

{relationships_list}

If you are going to make a tutorial for {state["project_name"]}, what is the best order to explain these abstractions, from first to last?
Ideally, first explain those that are the most important or foundational, perhaps user-facing concepts or entry points. Then move to more detailed, lower-level implementation details or supporting concepts.

Output the ordered list of component indices in a list, should include all components and should be a non-repeating valid list of indices.

example output:
[3, 1, 2, 0]

Now provide the ordered list of component indices.

"""

    component_ordering_llm = ChatOpenAI(
            model="gemini-2.5-flash-lite-preview-06-17", 
            temperature=0, 
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    component_ordering_llm_with_structured_output = component_ordering_llm.with_structured_output(OrderedComponents)

    ordered_components = component_ordering_llm_with_structured_output.invoke(llm_context)

    print(ordered_components)

    return {"ordered_components": ordered_components.ordered_components}


def components_pages_planner(state: State):
    docs_metadata = []
    print(state)
    for i, component_index in enumerate(state["ordered_components"]):
        if 0 > component_index >= len(state["components"]):
            continue
        docs_metadata.append({
            "title": state["components"][component_index].name,
            "number": i + 1,
            "component_index": component_index,
            "file_name": f"{i+1:02d}_{''.join(c if c.isalnum() else '_' for c in state['components'][component_index].name).lower()}.md"
        })
    all_docs_names_listing = "\n".join([f"{doc_metadata['number']}. [{doc_metadata['title']}]({doc_metadata['file_name']})" for doc_metadata in docs_metadata])
    pages_to_process = []
    for i, component_index in enumerate(state["ordered_components"]):
        if 0 > component_index >= len(state["components"]):
            continue
        component_details = state["components"][component_index]
        relevant_file_indices = component_details.files
        files_map = [(f"{i} # {state['files'][i]['path']}", state["files"][i]["content"]) for i in relevant_file_indices]
        prev_page = None
        if i > 0: 
            prev_component_index = state["ordered_components"][i - 1]
            prev_page = docs_metadata[prev_component_index]
        
        next_page = None
        if i < len(state["ordered_components"]) - 1:
            next_component_index = state["ordered_components"][i + 1]
            next_page = docs_metadata[next_component_index]
        
        pages_to_process.append({
            "component_num": i + 1,
            "component_index": component_index,
            "all_pages_names_listing": all_docs_names_listing,
            "prev_page": prev_page,
            "next_page": next_page,
            "file_name": docs_metadata[i]["file_name"]
        })

    return {"pages_to_process": pages_to_process, "pages_processed": 0}


def route_based_on_pages_remaining(state: State):
    if state["pages_processed"] < len(state["pages_to_process"]):
        return "pages_to_process"
    else:
        return "no_page_to_process"


def component_page_processor(state: State):
    print(state)
    page = state["pages_to_process"][state["pages_processed"]]
    component_details = state["components"][page["component_index"]]

    files_context = "\n".join([f"# {state['files'][i]['path']}\n\n{state['files'][i]['content']}" for i in component_details.files])
    prev_pages_context = "\n--------\n".join(state["pages"])

    llm_context = f"""
Write a very beginner-friendly tutorial chapter (in Markdown format) for the project {state["project_name"]} about the concept: "{component_details.name}". This is Chapter {page["component_num"]}.

Concept Details:
- Name: {component_details.name}
- Description:
{component_details.description}

Complete Tutorial Structure:
{page["all_pages_names_listing"]}

Context from previous chapters:
{prev_pages_context if prev_pages_context else "This is the first chapter."}

Relevant Code Snippets (Code itself remains unchanged):
{files_context if files_context else "No specific code snippets provided for this abstraction."}

Instructions for the chapter:
- Start with a clear heading (e.g., `# Chapter {page['component_num']}: {component_details.name}`). Use the provided concept name.

- If this is not the first chapter, begin with a brief transition from the previous chapter, referencing it with a proper Markdown link using its name.

- Begin with a high-level motivation explaining what problem this abstraction solves. Start with a central use case as a concrete example. The whole chapter should guide the reader to understand how to solve this use case. Make it very minimal and friendly to beginners.

- If the abstraction is complex, break it down into key concepts. Explain each concept one-by-one in a very beginner-friendly way.

- Explain how to use this abstraction to solve the use case. Give example inputs and outputs for code snippets (if the output isn't values, describe at a high level what will happen).

- Each code block should be BELOW 10 lines! If longer code blocks are needed, break them down into smaller pieces and walk through them one-by-one. Aggresively simplify the code to make it minimal. Use comments to skip non-important implementation details. Each code block should have a beginner friendly explanation right after it.

- Describe the internal implementation to help understand what's under the hood. First provide a non-code or code-light walkthrough on what happens step-by-step when the abstraction is called. It's recommended to use a simple sequenceDiagram with a dummy example - keep it minimal with at most 5 participants to ensure clarity. If participant name has space, use: `participant QP as Query Processing`.

- Then dive deeper into code for the internal implementation with references to files. Provide example code blocks, but make them similarly simple and beginner-friendly. Explain.

- IMPORTANT: When you need to refer to other core abstractions covered in other chapters, ALWAYS use proper Markdown links like this: [Chapter Title](filename.md). Use the Complete Tutorial Structure above to find the correct filename and the chapter title. Translate the surrounding text.

- Use mermaid diagrams to illustrate complex concepts (```mermaid``` format)..

- Heavily use analogies and examples throughout to help beginners understand.

- End the chapter with a brief conclusion that summarizes what was learned and provides a transition to the next chapter. If there is a next chapter, use a proper Markdown link: [Next Chapter Title](next_chapter_filename).

- Ensure the tone is welcoming and easy for a newcomer to understand, feel free to use emojis to make it more engaging.

- Output *only* the Markdown content for this chapter.

Now, directly provide a super beginner-friendly Markdown output (DON'T need ```markdown``` tags):
"""
    
    page_processor_llm = ChatOpenAI(
            model="gemini-2.5-flash-lite-preview-06-17", 
            temperature=0, 
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    
    page_content = page_processor_llm.invoke(llm_context).content
    page_heading = f"# Chapter {page['component_num']}: {component_details.name}"
    if not page_content.strip().startswith(f"# Chapter {page['component_num']}"):
        lines = page_content.strip().split("\n")
        if lines and lines[0].strip().startswith("#"):
            lines[0] = page_heading
            page_content = "\n".join(lines)
        else:
            page_content = f"{page_heading}\n\n{page_content}"

    return {"pages": [page_content], "pages_processed": state["pages_processed"] + 1}


def pages_to_documentation_directory(state: State):
    output_path = os.path.join("docs", state["project_name"])
    mermaid_lines = ["flowchart TD"]
    components = state["components"]
    ordered_components = state["ordered_components"]
    project_overview = state["project_overview"]
    pages = state["pages"]
    for i, component in enumerate(state["components"]):
        node_id = f"A{i}"
        # Use potentially translated name, sanitize for Mermaid ID and label
        sanitized_name = component.name.replace('"', "")
        node_label = sanitized_name  # Using sanitized name only
        mermaid_lines.append(
            f'    {node_id}["{node_label}"]'
        )  # Node label uses potentially translated name
    # Add edges for relationships using potentially translated labels
    for rel in state["component_relationships"]:
        from_node_id = f"A{rel.from_component}"
        to_node_id = f"A{rel.to_component}"
        # Use potentially translated label, sanitize
        edge_label = (
            rel.label.replace('"', "").replace("\n", " ")
        )  # Basic sanitization
        max_label_len = 30
        if len(edge_label) > max_label_len:
            edge_label = edge_label[: max_label_len - 3] + "..."
        mermaid_lines.append(
            f'    {from_node_id} -- "{edge_label}" --> {to_node_id}'
        )  # Edge label uses potentially translated label
    mermaid_diagram = "\n".join(mermaid_lines)

    index_content = f"# Tutorial: {state['project_name']}\n\n"
    index_content += f"{state['project_overview']}\n\n"  # Use the potentially translated summary directly
    # Keep fixed strings in English
    # index_content += f"**Source Repository:** [{repo_url}]({repo_url})\n\n"

    # Add Mermaid diagram for relationships (diagram itself uses potentially translated names/labels)
    index_content += "```mermaid\n"
    index_content += mermaid_diagram + "\n"
    index_content += "```\n\n"

    # Keep fixed strings in English
    index_content += f"## Chapters\n\n"

    chapter_files = []
    # Generate chapter links based on the determined order, using potentially translated names
    for i, component_index in enumerate(ordered_components):
        # Ensure index is valid and we have content for it
        if 0 <= component_index < len(components) and i < len(pages):
            component_name = components[component_index].name 
            # Sanitize potentially translated name for filename
            safe_name = "".join(
                c if c.isalnum() else "_" for c in component_name
            ).lower()
            filename = f"{i+1:02d}_{safe_name}.md"
            index_content += f"{i+1}. [{component_name}]({filename})\n"  # Use potentially translated name in link text

            chapter_content = pages[i]
            if not chapter_content.endswith("\n\n"):
                chapter_content += "\n\n"
            # Keep fixed strings in English
            chapter_content += f"---\n\nGenerated by Kritagya Khandelwal"

            # Store filename and corresponding content
            chapter_files.append({"filename": filename, "content": chapter_content})
        else:
            print(
                f"Warning: Mismatch between chapter order, abstractions, or content at index {i} (abstraction index {component_index}). Skipping file generation for this entry."
            )

    # Add attribution to index content (using English fixed string)
    index_content += f"\n\n---\n\nGenerated by Kritagya Khandelwal"

    os.makedirs(output_path, exist_ok=True)

    # Write index.md
    index_filepath = os.path.join(output_path, "index.md")
    with open(index_filepath, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"  - Wrote {index_filepath}")

    # Write chapter files
    for chapter_info in chapter_files:
        chapter_filepath = os.path.join(output_path, chapter_info["filename"])
        with open(chapter_filepath, "w", encoding="utf-8") as f:
            f.write(chapter_info["content"])
        print(f"  - Wrote {chapter_filepath}")

    return {"output_path": output_path} 