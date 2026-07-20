"""
Studex Knowledge Graph — Auto-Entity Extractor
Runs after every conversation. Pulls entities from the day's conversation
and updates the graph, ready for Obsidian + Obsidian Mind Map plugin.
"""
import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict

MEMORY_DIR = Path(os.getenv("OBSIDIAN_VAULT", "/root/robusca/robusca-brain")) / "memory" / "conversations"
GRAPH_FILE = MEMORY_DIR / "entities.json"
GRAPH_MD = MEMORY_DIR.parent / "graph.md"


# Patterns for Studex-specific entities
ENTITY_PATTERNS = {
    "COMPANY": [
        r'\b(Studex|NtechLab|Pharmasyntez|ART Engineering|Project Phoenix|GRM|AfricaBiz|PROWTC|Blotato|FeedHive|Shopify|Polsia)\b',
    ],
    "PERSON": [
        r'\b(Tumelo|Natalia|Svetlana|Anton|Robusca|Charlie|Naledi|Hermes)\b',
    ],
    "DEAL": [
        r'\b(PROWTC|Dubai|Rwanda A1|rubies|caviar|coffee)\b',
    ],
    "MONEY": [
        r'(?:USD |R |\$)([\d,]+(?:\.\d{2})?)',
    ],
    "DATE": [
        r'\b(20\d{2}-\d{2}-\d{2})\b',
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}',
    ],
    "URL": [
        r'https?://[^\s<>"{}|\\^`\[\]]+',
    ],
    "AGENT": [
        r'\b(robusca|charlie|naledi|hermes|ceo)\b',
    ],
}


def load_today_conversation() -> str:
    """Load today's conversation log."""
    today = datetime.now().strftime("%Y-%m-%d")
    path = MEMORY_DIR / f"{today}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract entities from conversation text."""
    entities = {k: [] for k in ENTITY_PATTERNS}
    
    for entity_type, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities[entity_type].extend([m.strip() if isinstance(m, str) else m[0] for m in matches])
    
    # Deduplicate
    for k in entities:
        entities[k] = list(set(entities[k]))
    
    return entities


def load_graph() -> Dict:
    """Load existing entity graph."""
    if GRAPH_FILE.exists():
        try:
            return json.loads(GRAPH_FILE.read_text())
        except:
            pass
    return {"entities": {}, "relations": [], "last_updated": ""}


def save_graph(graph: Dict):
    """Save entity graph."""
    graph["last_updated"] = datetime.now().isoformat()
    GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_FILE.write_text(json.dumps(graph, indent=2), encoding="utf-8")


def update_graph(entities: Dict[str, List[str]]):
    """Add new entities to the graph."""
    graph = load_graph()
    today = datetime.now().strftime("%Y-%m-%d")
    
    for etype, values in entities.items():
        if etype not in graph["entities"]:
            graph["entities"][etype] = {}
        
        for v in values:
            v_lower = v.lower()
            if v_lower not in graph["entities"][etype]:
                graph["entities"][etype][v_lower] = {
                    "name": v,
                    "first_seen": today,
                    "mentions": 1,
                    "sources": [today]
                }
            else:
                graph["entities"][etype][v_lower]["mentions"] += 1
                if today not in graph["entities"][etype][v_lower]["sources"]:
                    graph["entities"][etype][v_lower]["sources"].append(today)
    
    save_graph(graph)
    print(f"✅ Graph updated — {sum(len(v) for v in entities.values())} new entities")


def generate_graph_md() -> str:
    """Generate Obsidian-compatible graph view markdown."""
    graph = load_graph()
    
    lines = [
        "# 🕸️ Studex Knowledge Graph",
        f"_Last updated: {graph['last_updated']}_",
        "",
        "## Entities",
        ""
    ]
    
    for etype, data in graph.get("entities", {}).items():
        if not data:
            continue
        lines.append(f"### {etype}")
        for key, info in data.items():
            lines.append(f"- **{info['name']}** — seen {info['mentions']}× (first: {info['first_seen']})")
        lines.append("")
    
    return "\n".join(lines)


def run():
    """Main entry point — run after each conversation."""
    print("🕸️ Studex Knowledge Graph — building...")
    
    text = load_today_conversation()
    if not text:
        print("No conversation log found for today.")
        return
    
    entities = extract_entities(text)
    total = sum(len(v) for v in entities.values())
    print(f"Found {total} entities: { {k: len(v) for k, v in entities.items()} }")
    
    update_graph(entities)
    
    graph_md = generate_graph_md()
    GRAPH_MD.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_MD.write_text(graph_md, encoding="utf-8")
    print(f"✅ Graph written to {GRAPH_MD}")


if __name__ == "__main__":
    run()