"""
SkillGraph: wraps the skill taxonomy in a NetworkX DAG.

This is the single source of truth for prerequisite structure. Path
generation, explainability, and adaptation all query this object rather
than re-deriving relationships — keep it that way so the "explanation"
your Stage 3 module gives is always grounded in the same graph the path
was actually generated from.
"""

import networkx as nx
from app.models.schemas import SkillNode
from app.data.seed_skills import SEED_SKILLS


class SkillGraph:
    def __init__(self, nodes: list[SkillNode] | None = None):
        self.graph = nx.DiGraph()
        self.nodes_by_id: dict[str, SkillNode] = {}
        self._build(nodes or SEED_SKILLS)

    def _build(self, nodes: list[SkillNode]) -> None:
        # First pass: register all nodes so prerequisite edges can reference
        # any node regardless of definition order.
        for node in nodes:
            self.nodes_by_id[node.id] = node
            self.graph.add_node(node.id)

        # Second pass: add prerequisite edges (prereq -> node)
        for node in nodes:
            for prereq_id in node.prerequisites:
                if prereq_id not in self.nodes_by_id:
                    raise ValueError(
                        f"Skill '{node.id}' references unknown prerequisite '{prereq_id}'"
                    )
                self.graph.add_edge(prereq_id, node.id)

        if not nx.is_directed_acyclic_graph(self.graph):
            cycle = nx.find_cycle(self.graph)
            raise ValueError(f"Skill graph contains a cycle: {cycle}")

    def get_node(self, skill_id: str) -> SkillNode:
        return self.nodes_by_id[skill_id]

    def prerequisites_of(self, skill_id: str) -> list[str]:
        """Direct prerequisites only."""
        return list(self.graph.predecessors(skill_id))

    def all_ancestors(self, skill_id: str) -> set[str]:
        """Every skill (direct or indirect) that must come before this one."""
        return nx.ancestors(self.graph, skill_id)

    def subgraph_for_targets(self, target_skill_ids: list[str]) -> nx.DiGraph:
        """
        The minimal set of nodes needed to reach the target skills:
        each target plus all of its ancestors.
        """
        needed: set[str] = set()
        for target_id in target_skill_ids:
            if target_id not in self.nodes_by_id:
                raise ValueError(f"Unknown target skill: {target_id}")
            needed.add(target_id)
            needed |= self.all_ancestors(target_id)
        return self.graph.subgraph(needed).copy()

    def topological_order(self, subgraph: nx.DiGraph) -> list[str]:
        """
        A valid learning order: every prerequisite appears before the
        skills that depend on it. NetworkX's topo sort is deterministic
        given a stable node insertion order, but ties are broken by
        difficulty_tier in the path generator for a more sensible ramp.
        """
        return list(nx.topological_sort(subgraph))


# Module-level singleton — fine for a hackathon build; swap for dependency
# injection if you need per-request graph variants later.
skill_graph = SkillGraph()
