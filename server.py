"""
ie-mcp: MCP server (stdio) that explains Industrial Ecology Python packages.

Start it with `ie-mcp` or `python server.py`; the assistant tells it which Python
environment to inspect (set_python_environment), or IE_MCP_TARGET_PYTHON fixes one.
"""

from mcp.server.fastmcp import FastMCP

from core.instructions import build_instructions
from core.prompts import register_prompts
from core.registry import PackageRegistry
from core.resources import register_resources
from core.tools import register_tools

# Routing rules and trigger map: see core/instructions.yaml
INSTRUCTIONS = build_instructions()

mcp = FastMCP("ie-mcp", instructions=INSTRUCTIONS)

registry = PackageRegistry()
register_tools(mcp, registry)
register_resources(mcp, registry)
register_prompts(mcp, registry)


def main() -> None:
    """Run the MCP server on stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
