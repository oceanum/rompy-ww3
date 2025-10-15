#!/usr/bin/env python
"""Script to generate minimal OpenAPI schema for the rompy-ww3 Config and Data objects that works with Redoc."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rompy_ww3.config import Config
from rompy_ww3.data import Data
import json


def create_minimal_schema(schema_obj, schema_name):
    """
    Create a minimal representation of a schema focusing only on top-level properties.
    This avoids complex nested structures that cause Redoc issues.
    """
    if isinstance(schema_obj, dict):
        # Keep only the essential properties for documentation
        minimal_schema = {"type": "object", "title": schema_name}

        # Copy basic metadata
        if "title" in schema_obj:
            minimal_schema["title"] = schema_obj["title"]
        if "description" in schema_obj:
            minimal_schema["description"] = schema_obj["description"]

        # Copy only top-level properties, simplifying complex ones
        if "properties" in schema_obj:
            minimal_schema["properties"] = {}
            for prop_name, prop_value in schema_obj["properties"].items():
                # Simplify property definitions
                if isinstance(prop_value, dict):
                    simplified_prop = {}
                    # Copy basic property info
                    if "type" in prop_value:
                        simplified_prop["type"] = prop_value["type"]
                    if "description" in prop_value:
                        simplified_prop["description"] = prop_value["description"]
                    if "default" in prop_value:
                        simplified_prop["default"] = prop_value["default"]
                    # For complex types, just indicate they exist
                    if "properties" in prop_value or "$ref" in prop_value:
                        if "description" not in simplified_prop:
                            simplified_prop["description"] = (
                                f"{prop_name} object (see detailed documentation for full structure)"
                            )
                        if "type" not in simplified_prop:
                            simplified_prop["type"] = "object"
                    minimal_schema["properties"][prop_name] = simplified_prop
                else:
                    minimal_schema["properties"][prop_name] = prop_value

        # Copy required fields if they exist
        if "required" in schema_obj and isinstance(schema_obj["required"], list):
            minimal_schema["required"] = schema_obj["required"]

        return minimal_schema
    else:
        return schema_obj


# Get the original JSON schemas for both Config and Data models
config_schema = Config.model_json_schema()
data_schema = Data.model_json_schema()

# Create minimal schemas for better Redoc compatibility
minimal_config = create_minimal_schema(config_schema, "Config")
minimal_data = create_minimal_schema(data_schema, "Data")

# Create a very simple OpenAPI specification
openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "WW3 Schema Documentation",
        "version": "1.0.0",
        "description": "Schema documentation for WW3 Config and Data objects",
    },
    "paths": {
        "/config": {
            "get": {
                "summary": "Get WW3 Configuration Structure",
                "description": "Defines the structure and properties of the WW3 configuration object",
                "responses": {
                    "200": {
                        "description": "WW3 Configuration Schema",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Config"}
                            }
                        },
                    }
                },
            }
        },
        "/data": {
            "get": {
                "summary": "Get WW3 Data Structure",
                "description": "Defines the structure and properties of the WW3 data object",
                "responses": {
                    "200": {
                        "description": "WW3 Data Schema",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Data"}
                            }
                        },
                    }
                },
            }
        },
    },
    "components": {"schemas": {"Config": minimal_config, "Data": minimal_data}},
}

# Write the schema to a file in the docs directory
with open("docs/config_schema.json", "w") as f:
    json.dump(openapi_spec, f, indent=2)

print(
    "Minimal OpenAPI specification for Config and Data objects generated at docs/config_schema.json"
)
print("Schemas simplified for Redoc compatibility")
