# Hello World with OpenCode

A minimal demo project for trying out **OpenCode** ([sst/opencode](https://github.com/sst/opencode)) — the open-source, terminal-based AI coding agent. It's model-agnostic (Anthropic, OpenAI, Google, local models, etc.) and works as a TUI, in VS Code, or non-interactively from scripts.

This folder contains:
- `hello.js` — a one-function "hello world" app for OpenCode to read, explain, and modify
- `opencode.json` — an optional project config file OpenCode auto-loads
- This README, which doubles as the demo script

## 1. Install OpenCode

Pick one:

```bash
# Quick install script
curl -fsSL https://opencode.ai/install | bash

# Or via a package manager
npm i -g opencode-ai@latest      # npm/bun/pnpm/yarn
brew install sst/tap/opencode    # macOS
```

## 2. Authenticate with a provider

```bash
opencode auth login
```

This shows an interactive picker (Anthropic, OpenAI, Google, Bedrock, Azure, etc.) and stores the credential locally at `~/.local/share/opencode/auth.json`. If you already have an env var like `OPENAI_API_KEY` set, OpenCode will often auto-detect it.

## 3. Run it against this project (interactive TUI)

```bash
cd hello-opencode
opencode
```

This opens the terminal UI, scoped to this folder. Try prompts like:

- `explain what hello.js does`
- `add a second greet function that shouts the greeting in all caps, with a test`
- `refactor hello.js to use ES module syntax`

OpenCode will show you a diff and ask for permission before it edits or runs anything — press `Tab` to switch between the `build` agent (full access) and `plan` agent (read-only, good for exploring first).

## 4. Run it non-interactively (scriptable / CI-friendly)

OpenCode also supports one-shot prompts that print a result and exit:

```bash
opencode -p "Explain the use of the greet function in hello.js"
```

You can restrict which tools it's allowed to touch:

```bash
opencode -p "Add JSDoc comments to hello.js" --allowedTools=read,edit
opencode -p "Just tell me what this file does" --excludedTools=bash,edit
```

## 5. Project config (optional)

`opencode.json` in the project root is auto-loaded. It's where you'd add things like MCP servers:

```json
{
  "$schema": "http://opencode.ai/config.json",
  "mcp": {
    "localmcp": {
      "type": "local",
      "command": ["bun", "x", "my-mcp-command"]
    }
  }
}
```

## 6. Sanity-check the app itself

None of this needs OpenCode at all — it's just plain Node:

```bash
node hello.js
# -> Hello, world!
```

That's the whole loop: a trivial app to point OpenCode at, and the commands to install, authenticate, and drive it either interactively or as a one-shot CLI call.
