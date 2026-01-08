# Agent Behavior Guidelines

## Before Starting Work

1. **Read parent context first**: `~/Programs/CLAUDE.md` has cross-project principles
2. **Read project CLAUDE.md**: Project-specific technical guidelines
3. **Read progress_actual.md**: Current state, decisions, constraints
4. **Check other projects**: Look at sibling projects in ~/Programs for patterns

## Documentation Discipline

### progress_actual.md (REQUIRED)
- Create if it doesn't exist
- Add to .gitignore (private, not committed)
- Update with:
  - Current state of play
  - Key decisions made
  - Explicit constraints and "DO NOTs"
  - Watch-outs discovered
  - Next steps

### When user says "NO" or "DON'T"
- **Immediately** add to progress_actual.md under a "Constraints" section
- This is a HARD constraint, not a preference
- Persists across sessions - future agents will read it

## Tool Usage

### Package Management
- **Use `uv`** for Python (per ~/Programs/CLAUDE.md)
- NOT pip, NOT venv - always `uv pip install`, `uv venv`

### Logging
- Create session logs
- Keep events in structured format (JSONL)
- Don't rely on conversation context for critical decisions

## Error Handling

### If something fails twice
1. Stop and note the failure
2. Don't repeat the same approach
3. Document in progress_actual.md
4. Try alternative approach OR ask user

### If instructions conflict with problem-solving instinct
- **Instructions win**
- User's explicit "NO" overrides your "but this would work" reasoning

## Anti-Patterns (DO NOT)

- Don't put project-specific decisions in CLAUDE.md (that's for principles)
- Don't assume context survives session compaction
- Don't fall back to forbidden methods when preferred method fails
- Don't treat user constraints as suggestions
