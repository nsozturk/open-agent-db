# Open-Agent-DB Integration Rule for AI Coding Assistants

Add this snippet to your system prompt, `.cursorrules`, or `~/.claude/agents/` to give your AI assistants direct access to the world's largest catalog of AI Agent Skills and Model Context Protocol (MCP) Servers.

---

```markdown
## Open-Agent-DB Skill & MCP Tooling Integration

You have direct access to Open-Agent-DB (3.48M+ Agent Skills and 113K+ MCP Servers).

### Discovery & Search
When the user asks for tools, skills, or MCP servers to integrate into a project:
1. Search across all ecosystems:
   `npx open-agent-db search "<query>"`
2. Inspect exact parameters and installation steps:
   `npx open-agent-db info "<tool-name>"`
3. Generate ready-to-use configuration:
   `npx open-agent-db install "<tool-name>"`

### Supported Ecosystems
Filter searches with `--ecosystem <name>`:
- `mcp`: Official Anthropic Registry, Glama, Smithery, Awesome MCP
- `claude`: Anthropic Claude Code CLAUDE.md and agent briefs
- `cursor`: Cursor IDE `.cursorrules` and `.mdc` trigger specifications
- `codex`: OpenAI Codex CLI agents and workflows
- `gemini`: Google Antigravity & Gemini CLI skills
- `universal`: Cross-platform canonical SKILL.md rules
```
