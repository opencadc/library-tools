"""Generate Markdown documentation from the JSON Schema."""

from pathlib import Path
from library.schema import Schema
from jsonschema_markdown import generate  # type: ignore


def generate_schema_markdown(path: Path = Path("docs/schema.md")):
    """Generate Markdown documentation from the JSON Schema."""
    schema = Schema.model_json_schema()
    output = generate(schema, footer=False, hide_empty_columns=True)
    header = """---\nhide: \n    - toc\n---\n\n"""
    output = header + output
    with path.open("w", encoding="utf-8") as archive:
        archive.write(output)


if __name__ == "__main__":
    generate_schema_markdown()
