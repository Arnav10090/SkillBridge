import json
import os
from functools import lru_cache
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

@lru_cache(maxsize=1)
def load_taxonomy() -> dict:
    path = os.path.join(DATA_DIR, "skill_taxonomy.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@lru_cache(maxsize=1)
def load_catalog() -> dict:
    path = os.path.join(DATA_DIR, "course_catalog.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_skills() -> List[dict]:
    return load_taxonomy()["skills"]

def get_skill_by_id(skill_id: str) -> Optional[dict]:
    for s in get_all_skills():
        if s["id"] == skill_id:
            return s
    return None

def get_prerequisites() -> List[dict]:
    return load_taxonomy().get("prerequisites", [])

def get_modules_for_skill(skill_id: str) -> List[dict]:
    """Return all course modules that cover a given skill_id."""
    modules = load_catalog()["modules"]
    return [m for m in modules if skill_id in m.get("skill_tags", [])]

def get_module_by_id(module_id: str) -> Optional[dict]:
    for m in load_catalog()["modules"]:
        if m["id"] == module_id:
            return m
    return None

def get_skill_aliases_map() -> Dict[str, str]:
    """Returns {alias_lowercase: skill_id} for fast lookup during parsing."""
    alias_map = {}
    for skill in get_all_skills():
        alias_map[skill["name"].lower()] = skill["id"]
        for alias in skill.get("aliases", []):
            alias_map[alias.lower()] = skill["id"]
    return alias_map

def build_prerequisite_graph() -> Dict[str, List[str]]:
    """Returns {skill_id: [list of skill_ids that require it as prereq]}"""
    graph: Dict[str, List[str]] = {}
    for prereq in get_prerequisites():
        src = prereq["from"]
        dst = prereq["to"]
        if src not in graph:
            graph[src] = []
        graph[src].append(dst)
    return graph

def get_reverse_prerequisite_graph() -> Dict[str, List[str]]:
    """Returns {skill_id: [list of skill_ids that are prerequisites for it]}"""
    graph: Dict[str, List[str]] = {}
    for prereq in get_prerequisites():
        src = prereq["from"]
        dst = prereq["to"]
        if dst not in graph:
            graph[dst] = []
        graph[dst].append(src)
    return graph