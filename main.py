#!/usr/bin/env python3
"""
Squad Tools Manager - Unified CLI for all OpenSeneca squad tools
Provides easy access to run, monitor, and manage squad tools
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


TOOLS_DIR = Path.home() / ".openclaw" / "workspace" / "tools"
OUTPUTS_DIR = Path.home() / ".openclaw" / "workspace" / "outputs"
LOGS_DIR = Path.home() / ".openclaw" / "workspace" / "logs"


class SquadToolsManager:
    def __init__(self):
        self.tools = self._discover_tools()
        self.cron_jobs = self._parse_cron_jobs()

    def _discover_tools(self) -> Dict[str, Dict]:
        """Discover all tools in the tools directory"""
        tools = {}

        for tool_dir in TOOLS_DIR.iterdir():
            if tool_dir.name.startswith("_") or not tool_dir.is_dir():
                continue

            readme = tool_dir / "README.md"
            if readme.exists():
                # Extract description from README
                desc = ""
                try:
                    with open(readme, "r") as f:
                        lines = f.readlines()
                        skipped_title = False
                        for line in lines[:20]:  # Check first 20 lines
                            stripped = line.strip()
                            if not stripped:
                                continue
                            if stripped.startswith("# ") and not skipped_title:
                                # Skip first title line
                                skipped_title = True
                                continue
                            if not stripped.startswith("#"):
                                desc = stripped
                                break
                except Exception:
                    pass

                # Find main executable
                main_file = None
                for ext in [".py", ".sh", ".js"]:
                    for filename in ["main" + ext, tool_dir.name + ext]:
                        if (tool_dir / filename).exists():
                            main_file = filename
                            break
                    if main_file:
                        break

                tools[tool_dir.name] = {
                    "path": str(tool_dir),
                    "description": desc or "No description available",
                    "main_file": main_file,
                    "type": self._get_tool_type(main_file),
                }

        return tools

    def _get_tool_type(self, main_file: Optional[str]) -> str:
        """Determine tool type from main file extension"""
        if not main_file:
            return "unknown"
        if main_file.endswith(".py"):
            return "python"
        elif main_file.endswith(".sh"):
            return "bash"
        elif main_file.endswith(".js"):
            return "node"
        return "unknown"

    def _parse_cron_jobs(self) -> List[Dict]:
        """Parse cron jobs related to squad tools"""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                check=True
            )
            jobs = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "openclaw" in line or "squad" in line.lower():
                    jobs.append({
                        "schedule": " ".join(line.split()[:5]),
                        "command": " ".join(line.split()[5:])
                    })
            return jobs
        except Exception:
            return []

    def list_tools(self, show_all: bool = False) -> None:
        """List all discovered tools"""
        print(f"\n{'='*60}")
        print(f"Squad Tools ({len(self.tools)} total)")
        print(f"{'='*60}\n")

        for name, info in sorted(self.tools.items()):
            status = self._get_tool_status(name)
            status_symbol = "✓" if status == "active" else "·"

            print(f"{status_symbol} {name:40} [{info['type']}]")

            if show_all:
                print(f"   {info['description']}")
                print(f"   Path: {info['path']}")
                print(f"   Main: {info['main_file'] or 'N/A'}")
                print()

    def show_tool_info(self, tool_name: str) -> None:
        """Show detailed information about a specific tool"""
        if tool_name not in self.tools:
            print(f"Error: Tool '{tool_name}' not found")
            print(f"Available tools: {', '.join(self.tools.keys())}")
            return

        tool = self.tools[tool_name]
        print(f"\n{'='*60}")
        print(f"Tool: {tool_name}")
        print(f"{'='*60}\n")
        print(f"Description: {tool['description']}")
        print(f"Type: {tool['type']}")
        print(f"Path: {tool['path']}")
        print(f"Main file: {tool['main_file'] or 'N/A'}")

        # Show status
        status = self._get_tool_status(tool_name)
        print(f"Status: {status.upper()}")

        # Show recent outputs
        outputs = self._get_tool_outputs(tool_name)
        if outputs:
            print(f"\nRecent outputs:")
            for output in outputs[:3]:
                mtime = datetime.fromtimestamp(output.stat().st_mtime)
                print(f"  - {output.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")

        # Show logs
        logs = self._get_tool_logs(tool_name)
        if logs:
            print(f"\nLogs:")
            for log in logs[:3]:
                mtime = datetime.fromtimestamp(log.stat().st_mtime)
                print(f"  - {log.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")

        print()

    def run_tool(self, tool_name: str, args: List[str] = None) -> int:
        """Run a tool by name"""
        if tool_name not in self.tools:
            print(f"Error: Tool '{tool_name}' not found")
            return 1

        tool = self.tools[tool_name]
        tool_path = Path(tool["path"])

        if not tool["main_file"]:
            print(f"Error: No main file found for '{tool_name}'")
            return 1

        main_file = tool_path / tool["main_file"]

        if not main_file.exists():
            print(f"Error: Main file not found: {main_file}")
            return 1

        # Prepare command based on file type
        if tool["type"] == "python":
            cmd = [sys.executable, str(main_file)]
        elif tool["type"] == "bash":
            cmd = ["bash", str(main_file)]
        elif tool["type"] == "node":
            cmd = ["node", str(main_file)]
        else:
            print(f"Error: Unknown tool type: {tool['type']}")
            return 1

        # Add user arguments
        if args:
            cmd.extend(args)

        print(f"Running: {' '.join(cmd)}\n")

        try:
            result = subprocess.run(cmd, cwd=str(tool_path))
            return result.returncode
        except Exception as e:
            print(f"Error running tool: {e}")
            return 1

    def show_cron_jobs(self) -> None:
        """Show cron jobs related to squad tools"""
        print(f"\n{'='*60}")
        print(f"Squad Cron Jobs ({len(self.cron_jobs)} total)")
        print(f"{'='*60}\n")

        if not self.cron_jobs:
            print("No squad-related cron jobs found")
            return

        for i, job in enumerate(self.cron_jobs, 1):
            print(f"{i}. {job['schedule']}")
            print(f"   {job['command']}")
            print()

    def show_recent_outputs(self, limit: int = 10) -> None:
        """Show recent outputs from all tools"""
        print(f"\n{'='*60}")
        print(f"Recent Outputs (last {limit})")
        print(f"{'='*60}\n")

        if not OUTPUTS_DIR.exists():
            print("No outputs directory found")
            return

        outputs = sorted(
            OUTPUTS_DIR.glob("*.*"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:limit]

        for output in outputs:
            mtime = datetime.fromtimestamp(output.stat().st_mtime)
            size = output.stat().st_size
            print(f"{output.name:50} {mtime.strftime('%Y-%m-%d %H:%M')} ({size} bytes)")

    def show_logs(self, tool_name: Optional[str] = None, lines: int = 20) -> None:
        """Show logs for a tool or all recent logs"""
        if tool_name:
            if tool_name not in self.tools:
                print(f"Error: Tool '{tool_name}' not found")
                return
            logs = self._get_tool_logs(tool_name)
        else:
            logs = list(LOGS_DIR.glob("*.log")) if LOGS_DIR.exists() else []

        if not logs:
            print("No logs found")
            return

        for log_file in logs:
            print(f"\n{'='*60}")
            print(f"Log: {log_file.name}")
            print(f"{'='*60}\n")

            try:
                result = subprocess.run(
                    ["tail", "-n", str(lines), str(log_file)],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
            except Exception as e:
                print(f"Error reading log: {e}")

    def _get_tool_status(self, tool_name: str) -> str:
        """Get tool status (active, inactive, unknown)"""
        # Check for cron jobs
        for job in self.cron_jobs:
            if tool_name in job["command"]:
                return "active"

        # Check for recent output
        outputs = self._get_tool_outputs(tool_name)
        if outputs:
            latest = max(outputs, key=lambda f: f.stat().st_mtime)
            age_hours = (datetime.now().timestamp() - latest.stat().st_mtime) / 3600
            if age_hours < 24:
                return "active"

        return "inactive"

    def _get_tool_outputs(self, tool_name: str) -> List[Path]:
        """Get output files for a tool"""
        if not OUTPUTS_DIR.exists():
            return []

        outputs = []
        for pattern in [f"{tool_name}*", f"{tool_name.replace('-', '_')}-*"]:
            outputs.extend(OUTPUTS_DIR.glob(pattern))
        return outputs

    def _get_tool_logs(self, tool_name: str) -> List[Path]:
        """Get log files for a tool"""
        if not LOGS_DIR.exists():
            return []

        logs = []
        for pattern in [f"{tool_name}*.log", f"{tool_name.replace('-', '_')}*.log"]:
            logs.extend(LOGS_DIR.glob(pattern))
        return logs

    def generate_status_report(self) -> str:
        """Generate a comprehensive status report"""
        report = []
        report.append(f"\n{'='*60}")
        report.append(f"Squad Tools Status Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"{'='*60}\n")

        # Summary
        active_count = sum(1 for t in self.tools if self._get_tool_status(t) == "active")
        report.append(f"Total tools: {len(self.tools)}")
        report.append(f"Active tools: {active_count}")
        report.append(f"Cron jobs: {len(self.cron_jobs)}")
        report.append("")

        # Tool status
        report.append("\nTool Status:")
        report.append("-" * 40)
        for name in sorted(self.tools.keys()):
            status = self._get_tool_status(name)
            status_symbol = "✓" if status == "active" else "·"
            report.append(f"{status_symbol} {name:40} {status.upper()}")

        # Recent outputs
        report.append("\n\nRecent Outputs:")
        report.append("-" * 40)
        recent = self._get_recent_files(OUTPUTS_DIR, 5)
        for f in recent:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            report.append(f"{f.name:50} {mtime.strftime('%Y-%m-%d %H:%M')}")

        # Cron jobs
        report.append("\n\nCron Jobs:")
        report.append("-" * 40)
        for i, job in enumerate(self.cron_jobs, 1):
            report.append(f"{i}. {job['schedule']}")
            report.append(f"   {job['command']}")

        return "\n".join(report)

    def _get_recent_files(self, directory: Path, limit: int = 10) -> List[Path]:
        """Get recently modified files from directory"""
        if not directory.exists():
            return []

        return sorted(
            directory.glob("*.*"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:limit]


def main():
    parser = argparse.ArgumentParser(
        description="Squad Tools Manager - Unified CLI for OpenSeneca squad tools"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List all tools")
    list_parser.add_argument("-a", "--all", action="store_true", help="Show detailed info")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show tool information")
    info_parser.add_argument("tool", help="Tool name")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a tool")
    run_parser.add_argument("tool", help="Tool name")
    run_parser.add_argument("args", nargs="*", help="Arguments to pass to the tool")

    # Cron command
    subparsers.add_parser("cron", help="Show cron jobs")

    # Outputs command
    outputs_parser = subparsers.add_parser("outputs", help="Show recent outputs")
    outputs_parser.add_argument("-n", "--number", type=int, default=10, help="Number of outputs to show")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show logs")
    logs_parser.add_argument("tool", nargs="?", help="Tool name (optional)")
    logs_parser.add_argument("-n", "--lines", type=int, default=20, help="Number of lines to show")

    # Status command
    subparsers.add_parser("status", help="Generate status report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    manager = SquadToolsManager()

    if args.command == "list":
        manager.list_tools(show_all=args.all)
    elif args.command == "info":
        manager.show_tool_info(args.tool)
    elif args.command == "run":
        return manager.run_tool(args.tool, args.args)
    elif args.command == "cron":
        manager.show_cron_jobs()
    elif args.command == "outputs":
        manager.show_recent_outputs(limit=args.number)
    elif args.command == "logs":
        manager.show_logs(args.tool, lines=args.lines)
    elif args.command == "status":
        print(manager.generate_status_report())

    return 0


if __name__ == "__main__":
    sys.exit(main())
