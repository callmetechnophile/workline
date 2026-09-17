"""Command line interface for ProjectExecutionAgent."""
import argparse
from research_agents.project_execution_agent.agent import ProjectExecutionAgent
from research_agents.project_execution_agent.schemas import ProjectExecutionAgentInput

def main():
    parser = argparse.ArgumentParser(description="WorkflowGuide AI ProjectExecutionAgent (Agent #10) CLI")
    parser.add_argument("--project-id", default="proj_cli_001", help="Project identifier")
    parser.add_argument("--title", default="Autonomous Engineering System", help="Project title")
    parser.add_argument("--domain", default="Robotics / Edge AI", help="Engineering domain")
    parser.add_argument("--output-dir", default=None, help="Output directory for generated plan")
    args = parser.parse_args()

    agent = ProjectExecutionAgent()
    inp = ProjectExecutionAgentInput(
        project_id=args.project_id,
        title=args.title,
        engineering_domain=args.domain,
        output_dir=args.output_dir,
    )
    result = agent.run_sync(inp)
    print(result.structured_markdown_report)

if __name__ == "__main__":
    main()
