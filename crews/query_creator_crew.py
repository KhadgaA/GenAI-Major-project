from crewai import Agent, Crew, Task
from textwrap import dedent
from pydantic import BaseModel
from .websearch import WebSearchTool
class RefinedQuery(BaseModel):
    refined_query: str = "The improved research query"

class QueryCreatorCrew:
    def __init__(self):
        self.search_tool = WebSearchTool()

    def query_refinement_agent(self):
        return Agent(
            role="Query Refinement Specialist",
            goal="Refine and improve research queries to maximize search effectiveness",
            backstory="An expert at transforming broad or vague research questions into precise, targeted queries that yield high-quality information.",
            # tools=[self.search_tool],
            verbose=True,
            llm='cohere/command-r-plus-08-2024'
        )

    def query_context_agent(self):
        return Agent(
            role="Research Context Analyzer",
            goal="Add depth and context to research queries",
            backstory="A knowledgeable researcher who understands the nuanced aspects of research topics and can expand queries to capture comprehensive information.",
            # tools=[self.search_tool],
            verbose=True
        )

    def refine_query_task(self, query_refinement_agent, original_query, feedback):
        return Task(
            description=dedent(f"""
            Refine the research query: {original_query}
            Current feedback: {feedback}

            Steps:
            1. Analyze the original query's strengths and weaknesses
            2. Break down the query into specific research dimensions
            3. Expand the query to capture comprehensive insights
            4. Ensure the query is clear, specific, and search-engine friendly
            5. Incorporate any previous feedback to improve query precision
            """),
            agent=query_refinement_agent,
            output_pydantic=RefinedQuery,  # Use the class itself
            expected_output="A refined query that addresses all feedback points and improves clarity. only return query"
        )

    def crew(self, original_query, feedback):
        self.query_task = self.refine_query_task(self.query_refinement_agent(), original_query, feedback)

    def run(self):
        return Crew(
            agents=[self.query_refinement_agent(), self.query_context_agent()],
            tasks=[self.query_task],
            verbose=True,
        ).kickoff()
