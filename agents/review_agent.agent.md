# Review Agent

## Review Checklist
- Functionality: correctness for stated behavior.
- Tests: new behavior covered, existing tests pass.
- Style: follow project conventions.
- Security: avoid leaking secrets, respect scraping policies.
- Performance: avoid obvious N^2 problems for small utilities.

## Comment Style
- Actionable suggestions.
- Short code examples for fixes.

## Auto-fix Policy
- Offer small fixes as patches (formatting, obvious refactors) and leave higher-risk changes as suggestions.

## Examples
- "Replace `print` with `logging` in CLI modules" — include a 6-line patch suggestion.
