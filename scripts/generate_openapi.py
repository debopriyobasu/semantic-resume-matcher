import json

from src.main import app


def generate_openapi():
    # FastAPI's openapi() function generates the full OpenAPI schema.
    openapi_schema = app.openapi()

    # Write the schema to the target path.
    output_path = "docs/openapi.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Successfully generated OpenAPI schema at {output_path}")


if __name__ == "__main__":
    generate_openapi()
