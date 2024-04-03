---
icon: material/graph-outline
tags:
  - pvgisprototype
  - Python
  - Dependencies
  - Dependency Tree
---

# Tree

```bash exec="1" result="mermaid"
pipdeptree -p pvgisprototype --mermaid 2>/dev/null |
    sed 's/flowchart TD/flowchart LR/' |
    sed 's/\.dev.+"\]$/"]/;s/\+d.*"\]$/"]/'
```

# Wide format

```bash exec="1" result="mermaid"
pipdeptree -p pvgisprototype --mermaid 2>/dev/null
```
