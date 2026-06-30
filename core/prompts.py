"""
MCP prompts registration.

Prompts are reusable, parameterised message templates that guide the LLM
through a structured workflow for common tasks. Registered onto the FastMCP
instance via register_prompts().
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .registry import PackageRegistry


def register_prompts(mcp: FastMCP, registry: PackageRegistry) -> None:

    @mcp.prompt()
    def get_started(package: str) -> str:
        """Guide the user through getting started with a package.

        Fetches installation instructions and the introduction section, then
        summarises what the package does, how to install it, and a minimal
        first example.

        Args:
            package: Package name (call list_packages() to see available options).
        """
        available = registry.list_packages()
        if package not in available:
            return (
                f"Unknown package '{package}'. "
                f"Available packages: {available}. "
                f"Please retry with a valid package name."
            )
        sections = registry.get_sections(package)
        intro_section = "introduction" if "introduction" in sections else (sections[0] if sections else None)
        steps = [
            f"1. Call get_package_info('{package}') to get metadata and installation instructions.",
        ]
        if intro_section:
            steps.append(
                f"2. Call get_doc_section('{package}', '{intro_section}') to read the introduction."
            )
        steps.append(
            f"{len(steps) + 1}. Summarise: what the package does, how to install it, "
            f"and provide a minimal first working example."
        )
        return (
            f"Help me get started with the '{package}' Python package.\n\n"
            + "\n".join(steps)
        )

    @mcp.prompt()
    def explain_function(package: str, function_name: str) -> str:
        """Explain what a specific function does, including its source and documentation.

        Fetches the function source from GitHub and searches the docs for
        relevant context, then explains parameters, return value, and usage.

        Args:
            package: Package name (call list_packages() to see available options).
            function_name: Exact name of the function or method to explain.
        """
        available = registry.list_packages()
        if package not in available:
            return (
                f"Unknown package '{package}'. "
                f"Available packages: {available}. "
                f"Please retry with a valid package name."
            )
        return (
            f"Explain the '{function_name}' function from the '{package}' package.\n\n"
            f"Please:\n"
            f"1. Call get_function_source('{package}', '{function_name}') to read the source code.\n"
            f"2. Call search_docs('{package}', '{function_name}') to find relevant documentation.\n"
            f"3. Provide a clear explanation covering: what the function does, its parameters, "
            f"return value, any exceptions it raises, and a short usage example."
        )

    @mcp.prompt()
    def how_to(package: str, task: str) -> str:
        """Get step-by-step instructions for accomplishing a specific task with a package.

        Searches the documentation and, if relevant functions are found, fetches
        their source to produce an accurate, code-level guide.

        Args:
            package: Package name (call list_packages() to see available options).
            task: What you want to accomplish, e.g. 'export a database to SimaPro'.
        """
        available = registry.list_packages()
        if package not in available:
            return (
                f"Unknown package '{package}'. "
                f"Available packages: {available}. "
                f"Please retry with a valid package name."
            )
        return (
            f"How do I {task} using the '{package}' package?\n\n"
            f"Please:\n"
            f"1. Call search_docs('{package}', '{task}') to find relevant documentation snippets.\n"
            f"2. For any key functions mentioned, call get_function_source('{package}', <function_name>) "
            f"to confirm the exact API.\n"
            f"3. Provide a clear, step-by-step guide with runnable code examples."
        )

    @mcp.prompt()
    def compare_function_versions(
        package: str,
        function_name: str,
        version_a: str,
        version_b: str,
    ) -> str:
        """Compare how a function changed between two versions of a package.

        Fetches the function source at both version tags and produces a
        side-by-side diff with a plain-language explanation of what changed
        (signature, parameters, logic, docstring, removal).

        Args:
            package: Package name (call list_packages() to see available options).
            function_name: Exact name of the function or method to compare.
            version_a: First version tag (e.g. 'v1.0.0' or '1.0.0').
            version_b: Second version tag to compare against (e.g. 'v2.0.0').
        """
        available = registry.list_packages()
        if package not in available:
            return (
                f"Unknown package '{package}'. "
                f"Available packages: {available}. "
                f"Please retry with a valid package name."
            )
        return (
            f"Compare the '{function_name}' function between version {version_a} "
            f"and version {version_b} of the '{package}' package.\n\n"
            f"Please:\n"
            f"1. Call list_source_versions('{package}') to confirm both tags exist "
            f"and find the exact tag spelling if needed.\n"
            f"2. Call get_function_source('{package}', '{function_name}', '{version_a}') "
            f"to fetch the function at version {version_a}.\n"
            f"3. Call get_function_source('{package}', '{function_name}', '{version_b}') "
            f"to fetch the function at version {version_b}.\n"
            f"4. If either call returns an error saying the function was not found, "
            f"report that the function did not exist in that version.\n"
            f"5. Present a clear comparison covering:\n"
            f"   - Signature changes (parameters added, removed, renamed, or retyped)\n"
            f"   - Behavioural / logic changes\n"
            f"   - Docstring changes\n"
            f"   - Any deprecation or breaking-change notes\n"
            f"   - A plain-language summary of what the change means for users."
        )

    @mcp.prompt()
    def compare_packages() -> str:
        """Compare all available packages: what each does and when to choose one over another.

        Lists all packages, fetches their metadata, and produces a side-by-side
        summary of purpose, key features, and typical use cases.
        """
        available = registry.list_packages()
        if not available:
            return "No packages are currently registered in this MCP server."
        pkg_calls = "\n".join(
            f"{i + 2}. Call get_package_info('{pkg}') to get its metadata."
            for i, pkg in enumerate(available)
        )
        return (
            f"Compare the Python packages available in this MCP server: {available}.\n\n"
            f"Please:\n"
            f"1. Call list_packages() to confirm the full list.\n"
            f"{pkg_calls}\n"
            f"{len(available) + 2}. Summarise each package: purpose, key features, typical use cases, "
            f"and guidance on when to choose one over another."
        )
