---
icon: material/graph-outline
tags:
  - pvgisprototype
  - Python
  - Dependencies
  - Dependency Tree
---

# Dependency flowchart

```bash exec="1" result="mermaid"
pipdeptree -p pvgisprototype --mermaid 2>/dev/null |
    sed 's/flowchart TD/flowchart LR/' |
    sed 's/\.dev.+"\]$/"]/;s/\+d.*"\]$/"]/'
```

## Alternative flowchart

```bash exec="1" result="mermaid"
pipdeptree -p pvgisprototype --mermaid 2>/dev/null
```
