"""
CLI for Agent #27 — Technical Documentation & Engineering Publication Agent.
"""

import argparse
from research_agents.documentation_agent.agent import TechDocAgent


def main():
    parser = argparse.ArgumentParser(description="Agent #27 — Technical Documentation Agent")
    parser.add_argument("--project-id",    default="DEMO-DOC",  help="Project ID")
    parser.add_argument("--operation",     default="create_document", help="Operation")
    parser.add_argument("--user-id",       default="eng.demo",  help="User ID")
    parser.add_argument("--doc-type",      default="DESIGN_DESCRIPTION", help="Document type")
    parser.add_argument("--title",         default="System Design Description", help="Title")
    parser.add_argument("--doc-id",        default=None,        help="Document ID")
    parser.add_argument("--eval",          action="store_true", help="Run harness evaluation")
    args = parser.parse_args()

    if args.eval:
        import json
        from research_agents.documentation_agent.evals.harness_eval import run_eval
        print(json.dumps(run_eval(), indent=2, default=str))
        return

    agent  = TechDocAgent()
    result = agent.run({
        "project_id":    args.project_id,
        "operation":     args.operation,
        "user_id":       args.user_id,
        "document_type": args.doc_type,
        "title":         args.title,
        "doc_id":        args.doc_id,
    })

    doc = result.get("document") or {}
    print(f"Agent #27 Status:      {result.get('status')}")
    print(f"Operation:             {result.get('operation')}")
    print(f"Project:               {result.get('project_id')}")
    if doc:
        print(f"Document ID:           {doc.get('doc_id')}")
        print(f"Title:                 {doc.get('title')}")
        print(f"Type:                  {doc.get('document_type')}")
        print(f"Status:                {doc.get('status')}")
        print(f"Authority:             {doc.get('authority')}")
        print(f"Revision:              {doc.get('revision')}")
        print(f"Sections:              {len(doc.get('content_sections', {}))}")
    if result.get("quality_score") is not None:
        print(f"Quality Score:         {result.get('quality_score'):.3f}")
    print(f"Summary:               {result.get('summary')}")
    if result.get("errors"):
        print(f"Errors:                {result.get('errors')}")


if __name__ == "__main__":
    main()
