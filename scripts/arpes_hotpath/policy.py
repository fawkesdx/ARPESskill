"""Refusals for steps the skill forbids. Exit code 2 at the CLI."""


class PolicyRefusal(Exception):
    """The requested step would invent axes, physics, or a package feature."""
