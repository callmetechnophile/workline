"""
Prompt templates and rubric definitions for query construction and scoring.
"""

QUERY_GENERATION_RUBRIC = """
Given an engineering project context, construct targeted search queries for academic paper discovery:
- Extract technical nouns, core methodologies, and hardware constraints.
- Avoid general stop words or single run-on sentence queries.
- Generate queries covering:
  1. Primary system goal and core domain topology
  2. Component-specific technical implementations
  3. Technology / algorithm benchmark investigations
  4. Operational constraint solutions (e.g. real-time edge, thermal mitigation)
"""

RELEVANCE_CRITERIA_EXPLANATIONS = {
    "title_match": "Title directly addresses project concept or core methodology",
    "objective_match": "Investigates target research objective: {objective}",
    "component_match": "Evaluates matching component: {component}",
    "technology_match": "Implements matching technology/algorithm: {technology}",
    "domain_match": "Directly targets engineering domain: {domain}",
    "constraint_match": "Addresses operational constraint: {constraint}",
    "recency_boost": "Recent publication with modern benchmarks ({year})",
}
