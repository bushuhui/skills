#!/usr/bin/env python3
"""
pi-github: GitHub MCP Server Python Client

A CLI wrapper for the GitHub MCP Server HTTP endpoint.
Communicates via JSON-RPC over HTTP Streamable (SSE) to call any GitHub MCP tool.

Usage:
    python3 github_mcp.py <tool_name> --json '<params>'
    python3 github_mcp.py --list-tools
    python3 github_mcp.py get_me
    python3 github_mcp.py get_file_contents --json '{"owner":"octocat","repo":"hello-world","path":"README.md"}'
"""

import argparse
import json
import os
import re
import sys
import requests


# Configuration
MCP_URL = os.environ.get("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY", os.environ.get("HTTP_PROXY", ""))
# Default proxy only if no proxy env is set
if not HTTPS_PROXY:
    HTTPS_PROXY = "http://192.169.1.2:7890"


class GitHubMCPClient:
    """Client for the GitHub MCP Server using HTTP Streamable transport."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
        })

        # Configure proxy if reachable
        self._setup_proxy()
        self._initialized = False
        self._id_counter = 1

    def _setup_proxy(self):
        """Test and configure proxy, fall back to direct if unreachable."""
        if not HTTPS_PROXY:
            return
        try:
            requests.get(
                "https://api.githubcopilot.com/mcp/",
                proxies={"http": HTTPS_PROXY, "https": HTTPS_PROXY},
                timeout=3,
            )
        except Exception:
            return  # Proxy unreachable, use direct

        self.session.proxies = {
            "http": HTTPS_PROXY,
            "https": HTTPS_PROXY,
        }

    def _next_id(self):
        self._id_counter += 1
        return self._id_counter

    def _parse_sse(self, text):
        """Parse SSE response, extract JSON from 'data:' lines."""
        text = text.strip()
        if text.startswith("{"):
            return json.loads(text)
        results = []
        for line in text.split("\n"):
            if line.startswith("data: "):
                data = line[6:]
                try:
                    results.append(json.loads(data))
                except json.JSONDecodeError:
                    continue
        return results[0] if len(results) == 1 else results

    def _send(self, method, params=None):
        """Send a JSON-RPC request and return parsed response."""
        body = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            body["params"] = params

        resp = self.session.post(MCP_URL, json=body, timeout=60)
        resp.raise_for_status()

        # Save session ID for subsequent requests
        if "mcp-session-id" in resp.headers:
            self.session.headers["Mcp-Session-Id"] = resp.headers["mcp-session-id"]

        return self._parse_sse(resp.text)

    def _notify(self, method, params=None):
        """Send a JSON-RPC notification (no response expected)."""
        body = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params is not None:
            body["params"] = params
        try:
            self.session.post(MCP_URL, json=body, timeout=10)
        except Exception:
            pass  # Notifications are fire-and-forget

    def initialize(self):
        """Initialize MCP session."""
        if self._initialized:
            return
        result = self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "pi-github", "version": "1.0.0"},
        })
        self._notify("notifications/initialized")
        self._initialized = True

    def list_tools(self):
        """List all available MCP tools."""
        self.initialize()
        return self._send("tools/list")

    def list_resources(self):
        """List all available MCP resources."""
        self.initialize()
        return self._send("resources/list")

    def list_prompts(self):
        """List all available MCP prompts."""
        self.initialize()
        return self._send("prompts/list")

    def call_tool(self, tool_name, arguments=None):
        """Call a specific MCP tool."""
        self.initialize()
        return self._send("tools/call", {
            "name": tool_name,
            "arguments": arguments or {},
        })


def main():
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable is not set", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="GitHub MCP Server CLI Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 github_mcp.py --list-tools
    python3 github_mcp.py get_me
    python3 github_mcp.py get_file_contents --json '{"owner":"octocat","repo":"hello-world","path":"README.md"}'
    python3 github_mcp.py issue_read --json '{"owner":"octocat","repo":"hello-world","issue_number":1}'
    python3 github_mcp.py search_repositories --json '{"query":"machine learning","sort":"stars"}'
        """,
    )
    parser.add_argument("tool", nargs="?", help="MCP tool/method name to call")
    parser.add_argument("--json", dest="params", help="JSON string of parameters for the tool")
    parser.add_argument("--list-tools", action="store_true", help="List all available tools")
    parser.add_argument("--list-resources", action="store_true", help="List all available resources")
    parser.add_argument("--list-prompts", action="store_true", help="List all available prompts")
    parser.add_argument("--raw", action="store_true", help="Raw JSON output (no pretty print)")

    args = parser.parse_args()
    client = GitHubMCPClient()
    pretty = not args.raw

    if args.list_tools:
        result = client.list_tools()
        print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))
        sys.exit(0)

    if args.list_resources:
        result = client.list_resources()
        print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))
        sys.exit(0)

    if args.list_prompts:
        result = client.list_prompts()
        print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))
        sys.exit(0)

    if not args.tool:
        parser.print_help()
        sys.exit(1)

    params = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    result = client.call_tool(args.tool, params)
    print(json.dumps(result, indent=2 if pretty else None, ensure_ascii=False))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
