# Chapter 4: Pydantic Models

Welcome back! We've explored how our documentation agent works, the logic behind its steps, and how it finds the right files. Now, let's talk about how we keep all the information organized and validated. This is where **Pydantic Models** come into play!

## What are Pydantic Models? 🤔

Think of Pydantic Models as **blueprints** or **templates** for the data our agent uses. In any software project, especially one that deals with a lot of information, it's crucial to have a clear structure for that data. Pydantic Models help us define exactly what kind of data we expect, what its fields are, and what type of data each field should hold (like text, numbers, or lists).

Why is this important?

1.  **Data Validation:** Pydantic automatically checks if the data we receive matches our defined structure. If you expect a number but get text, Pydantic will raise an error, preventing bugs and ensuring data integrity.
2.  **Data Serialization/Deserialization:** Pydantic makes it easy to convert data between different formats, like Python dictionaries and JSON. This is super useful when communicating with APIs or saving data.
3.  **Readability and Maintainability:** By defining our data structures clearly, our code becomes much easier to understand and manage. Anyone looking at the Pydantic models can immediately grasp what kind of data is being handled.

In our Agent Documentor project, we use Pydantic Models to define the structure for:

*   **Components:** What information we need about each code component (its name, description, and related files).
*   **Relationships:** How different components interact with each other.
*   **Analysis Outputs:** The structured results from our LLM analysis, like project overviews and ordered component lists.

## Our Pydantic Models 🏗️

Let's look at the Pydantic Models we've defined in `models.py`:

```python
# models.py

from pydantic import BaseModel, Field


class Component(BaseModel):
    name: str = Field(description="concise name for the component")
    description: str = Field(description="beginner friendly description of the component")
    files: list[int] = Field(description="list of relevent files indices of the component")
```

This `Component` model is a blueprint for a single component identified in our code. It tells us that each component must have:

*   `name`: A string representing the component's name.
*   `description`: A string describing the component.
*   `files`: A list of integers, where each integer is an index pointing to a file identified by our File Extractor.

The `Field` function is used here to add descriptions to each attribute, which helps document the model itself and can be used by tools.

---

```python
class Components(BaseModel):
    components: list[Component] = Field(description="list of components")
```

The `Components` model is a container for multiple `Component` models. When our `component_segregator` node asks the LLM to identify components, it expects the output to be structured like this `Components` model, containing a list of individual `Component` objects.

---

```python
class Relationship(BaseModel):
    from_component: int = Field(description="index of the source component or abstraction")
    to_component: int = Field(description="index of the target component or abstraction")
    label: str = Field(description="brief label for the interaction in just a few words")
```

This `Relationship` model defines how one component connects to another. It includes:

*   `from_component`: The index of the component that initiates the relationship.
*   `to_component`: The index of the component that is the target of the relationship.
*   `label`: A short description of the relationship (e.g., "uses", "manages").

---

```python
class RelationshipAnalysisOutput(BaseModel):
    overview: str = Field(description="A high-level `overview` of the project's main purpose and functionality in a few beginner-friendly paragraphs Use markdown formatting with **bold** and *italic* text to highlight important concepts, don't hesitate to use relevant emojis to make it more engaging")
    relationships: list[Relationship] = Field(description="list of `relationships` between the components")
```

This model is used for the output of the `component_relationship_analyser` node. It bundles together the overall project `overview` (a string) and a list of `relationships` (using our `Relationship` model).

---

```python
class OrderedComponents(BaseModel):
    ordered_components: list[int] = Field(description="ordered list of component indices in a list, should include all components and should be a non-repeating valid list of indices")
```

Finally, the `OrderedComponents` model is used to structure the output from the `component_ordering` node. It simply expects a list of integers, representing the indices of the components in the desired order for documentation.

## How Pydantic is Used in the Agent 🤖

In the **[Agent Nodes Logic](02_agent_nodes_logic.md)** chapter, you saw how we used these models. For example, in `component_segregator`:

```python
    component_segregation_llm_with_structured_output = component_segregation_llm.with_structured_output(Components)
    components = component_segregation_llm_with_structured_output.invoke(llm_context)
```

Here, we tell the LLM to output its response in the structure defined by our `Components` Pydantic model. Pydantic then takes the LLM's raw text output, parses it, validates it against the `Components` model, and if everything matches, it returns a Python object of type `Components`. If there's a mismatch (e.g., the LLM didn't provide a list of files for a component), Pydantic would raise an error, letting us know something went wrong.

This structured approach makes our agent much more reliable and easier to debug.

## What's Next? ➡️

We've now covered the essential building blocks of our Agent Documentor: the overall workflow, the logic within each node, how it finds files, and how it structures its data using Pydantic Models.

In our next chapter, we'll look at the **[File Extractor](03_file_extractor.md)** again, but this time we'll focus on how it's integrated into the agent's workflow to actually fetch the files needed for documentation. Get ready to see how the pieces fit together! ✨

---

Generated by Kritagya Khandelwal