from typing import List, Dict
from pydantic import BaseModel
from crewai import Agent, Crew, Task
from .websearch import WebSearchTool  # Import your WebSearchTool


# Define BaseModel classes for output
class AcademicSearchOutput(BaseModel):
    academic_results: List[Dict[str, str]]  # A list of dictionaries with search results


class WebSearchOutput(BaseModel):
    web_results: List[Dict[str, str]]  # A list of dictionaries with search results


class NewsSearchOutput(BaseModel):
    news_results: List[Dict[str, str]]  # A list of dictionaries with search results


class SearchAgentsCrew:
    def __init__(self):
        self.search_tools = [WebSearchTool() for _ in range(3)]  # Instantiate multiple WebSearchTool instances

    def academic_search_agent(self):
        return Agent(
            role="Academic Research Specialist",
            goal="Conduct deep academic and scholarly research using specialized search tools.",
            backstory="A meticulous researcher with expertise in finding high-quality academic and scientific sources.",
            tools=[self.search_tools[0]],  # Assign one instance of WebSearchTool
            verbose=True,
            llm="cohere/command-r-plus-08-2024"
        )

    def general_web_search_agent(self):
        return Agent(
            role="Web Research Generalist",
            goal="Perform comprehensive web searches to gather diverse information sources.",
            backstory="A skilled internet researcher capable of finding relevant information across various websites and sources.",
            tools=[self.search_tools[1]],  # Assign another instance of WebSearchTool
            verbose=True,
            llm="cohere/command-r-plus-08-2024"
        )

    def news_and_current_events_agent(self):
        return Agent(
            role="Current Events and News Researcher",
            goal="Find the most recent and relevant news and current event information.",
            backstory="An expert at tracking down the latest news and contextual information related to research topics.",
            tools=[self.search_tools[2]],  # Assign another instance of WebSearchTool
            verbose=True,
            llm="cohere/command-r-plus-08-2024"
        )

    def search_task(self, search_agent, search_type, query):
        # Select the correct BaseModel for expected output based on the search_type
        if search_type == "academic":
            output_model = AcademicSearchOutput
        elif search_type == "web":
            output_model = WebSearchOutput
        elif search_type == "news":
            output_model = NewsSearchOutput
        else:
            raise ValueError(f"Unsupported search type: {search_type}")

        return Task(
            description=f"""
            Perform {search_type} research on the query: {query}
            
            Objectives:
            1. Conduct a thorough search using specialized tools.
            2. Collect diverse and credible sources.
            3. Summarize key findings.
            4. Identify unique perspectives or insights.
            """,
            agent=search_agent,
            output_pydantic=output_model,  # Use the appropriate BaseModel for output
            expected_output=f"A structured list of {search_type} search results."
        )

    def crew(self, query):
        # Create agents
        self.academic_agent = self.academic_search_agent()
        self.web_search_agent = self.general_web_search_agent()
        self.news_agent = self.news_and_current_events_agent()

        # Create tasks
        self.academic_search_task = self.search_task(self.academic_agent, "academic", query)
        self.web_search_task = self.search_task(self.web_search_agent, "web", query)
        self.news_search_task = self.search_task(self.news_agent, "news", query)

        # Create and return the crew
    

    def run(self):

        return Crew(
            agents=[ self.web_search_agent],
            tasks=[self.web_search_task],
            verbose=True,
        ).kickoff()