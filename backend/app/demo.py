"""Independently authored UI examples, unrelated to patient records."""

from backend.app.contracts import DemoCase, DemoCases


def synthetic_cases() -> DemoCases:
    return DemoCases(
        cases=[
            DemoCase(
                id="synthetic-example-a",
                name="Example A · Workflow preview",
                description="An invented encounter placeholder for exploring the review interface.",
            ),
            DemoCase(
                id="synthetic-example-b",
                name="Example B · Missing information",
                description="An invented placeholder illustrating unavailable information.",
            ),
        ]
    )
