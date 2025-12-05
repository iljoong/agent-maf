# Microsoft Agent Framework Samples

This repository contains sample implementations demonstrating the Microsoft Agent Framework capabilities.

## Setup

Set up a Python environment using `conda` or `venv` and install the required packages:

```bash
conda create -n maf python=3.11
conda activate maf
pip install -r requirements.txt
```

Copy and update the value of environment variables in `.env`.

```bash
cp env.sample .env
```

## DevUI Samples

This repository includes the following sample agents and workflows:

### Agents
- **devui/agent**: Default agent sample
- **devui/agent_finance**: Agent using multiple tools (finance tool, code interpreter)
- **devui/agent_weather**: Agent using weather tool
- **devui/agent_search**: Agent using web search tool

### Workflows
- **devui/workflow**: Default workflow sample
- **devui/workflow_research**: Multi-agent workflow sample

## Running the Samples

To run devui and select any sample from the pulldown menu:

```bash
cd devui

devui
```

> **Note**: You may add `--port 8090` option if port 8080 is not available.