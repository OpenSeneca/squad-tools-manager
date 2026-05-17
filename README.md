# Squad Tools Manager

Unified CLI wrapper for all OpenSeneca squad tools. Provides easy access to run, monitor, and manage all squad tools from one interface.

## Features

- **Tool Discovery**: Automatically discovers all tools in the workspace
- **Quick Run**: Execute any tool by name without remembering paths
- **Status Monitoring**: Check which tools are active (running via cron or recently used)
- **Log Viewing**: View logs for any tool from one place
- **Output Tracking**: See recent outputs from all tools
- **Cron Job Management**: View all squad-related cron jobs
- **Status Reports**: Generate comprehensive status reports

## Installation

```bash
cd ~/.openclaw/workspace/tools/squad-tools-manager
chmod +x main.py
```

Make sure Python 3.8+ is available.

## Usage

### List all tools

```bash
./main.py list
```

With detailed information:
```bash
./main.py list --all
```

### Show tool information

```bash
./main.py info <tool-name>
```

Example:
```bash
./main.py info content-pipeline
```

### Run a tool

```bash
./main.py run <tool-name> [args...]
```

Examples:
```bash
# Run content pipeline
./main.py run content-pipeline

# Run squad tools tester with quick mode
./main.py run squad-tools-tester --quick

# Run squad cron manager
./main.py run squad-cron-manager check
```

### Show cron jobs

```bash
./main.py cron
```

### Show recent outputs

```bash
# Show last 10 outputs (default)
./main.py outputs

# Show last 5 outputs
./main.py outputs -n 5
```

### Show logs

```bash
# Show logs for a specific tool
./main.py logs <tool-name>

# Show recent logs from all tools
./main.py logs

# Show last 50 lines
./main.py logs <tool-name> -n 50
```

### Generate status report

```bash
./main.py status
```

## Tool Status

Tools are considered **active** if:
- They have a cron job installed
- They have produced output in the last 24 hours

Tools are considered **inactive** otherwise.

## Tool Types

The manager supports multiple tool types:
- **Python**: Tools with `.py` main files
- **Bash**: Tools with `.sh` main files
- **Node**: Tools with `.js` main files

## Tool Discovery

The manager scans `~/.openclaw/workspace/tools/` for:
- Directories that don't start with `_` (not archived)
- README.md files (for descriptions)
- Main executable files: `main.py`, `main.sh`, `main.js`, `<tool-name>.py`, `<tool-name>.sh`, `<tool-name>.js`

## Output Locations

- **Tool outputs**: `~/.openclaw/workspace/outputs/`
- **Tool logs**: `~/.openclaw/workspace/logs/`

## Examples

### Quick daily workflow

```bash
# 1. Check all tools
./main.py list

# 2. See what's been happening today
./main.py outputs -n 5

# 3. Run the content pipeline if needed
./main.py run content-pipeline

# 4. Check logs if something failed
./main.py logs content-pipeline

# 5. Generate a status report
./main.py status
```

### Monitor a specific tool

```bash
# Show tool info
./main.py info squad-dashboard-v2

# Check its logs
./main.py logs squad-dashboard-v2

# Run it manually if needed
./main.py run squad-dashboard-v2
```

### Check automation status

```bash
# View all cron jobs
./main.py cron

# Generate status report
./main.py status
```

## Integration

### Create a shell alias (optional)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias stm='python3 ~/.openclaw/workspace/tools/squad-tools-manager/main.py'
```

Then use:
```bash
stm list
stm run content-pipeline
stm status
```

### Add to cron for daily status check

```cron
# Generate status report daily at 8 AM
0 8 * * * python3 ~/.openclaw/workspace/tools/squad-tools-manager/main.py status > ~/.openclaw/workspace/outputs/squad-status-$(date +\%Y-\%m-\%d).md 2>&1
```

## Troubleshooting

### "Tool not found"

Check if the tool directory exists:
```bash
ls ~/.openclaw/workspace/tools/
```

Use `./main.py list` to see all discovered tools.

### "No main file found"

The tool doesn't have a recognized main file. Main files must be named:
- `main.py`, `main.sh`, `main.js`
- `<tool-name>.py`, `<tool-name>.sh`, `<tool-name>.js`

### "No outputs directory found"

Create the directory:
```bash
mkdir -p ~/.openclaw/workspace/outputs
```

### "No logs directory found"

Create the directory:
```bash
mkdir -p ~/.openclaw/workspace/logs
```

## Current Tools

As of 2026-05-17, the manager discovers:

**Core Automation:**
- content-pipeline (v1.4.0)
- squad-output-digest-v2 (v2.0.0)
- squad-output-digest-emailer-v2 (v1.0.0)
- auto-ingester-axon (v1.0.0)

**Monitoring & Management:**
- squad-dashboard-v2 (v2.1.0)
- squad-cron-manager (v1.0.0)
- squad-tools-tester (v1.0.0)
- squad-tools-health-check (v1.0.0)
- squad-config-validator (v1.0.0)
- squad-output-stats (v1.0.0)
- forge-watchdog (v1.0.0)

**Utilities:**
- blog-assistant
- blog-angle-tracker
- blog-publisher (v1.0.0)
- paper-summarizer (v1.0.0)
- competitor-tracker (v1.0.0)
- github-publisher (v1.1.0)
- deployment-config-fixer (v1.0.0)
- squad-tools-audit (v1.0.0)

## Version

**v1.0.0** - 2026-05-17
- Initial release
- Tool discovery and listing
- Tool execution wrapper
- Status monitoring
- Log viewing
- Output tracking
- Cron job display
- Status reports

## License

MIT

## Author

OpenSeneca Squad - Archimedes (Engineering)
