from crewai import Agent, Crew, Task
from textwrap import dedent
from pydantic import BaseModel
from typing import Literal

class RouteDecider(BaseModel):
    route: Literal['save_research','rewrite','restart'] = 'save_research'

class HumanFeedbackCrew:

    def route_decider_agent(self):
        return Agent(
            role="Feedback Route Decider expert",
            goal="Route the agents based on human feedback",
            backstory="Taking human feedback into account you choose the most appropriate route",
            # tools=[self.search_tool],
            verbose=True,
            llm='cohere/command-r-plus-08-2024'
        )



    def route_choose_task(self, agent, feedback):
        return Task(
            description=dedent(f"""
            Human feedback: {feedback}

            steps:
            check whether human is satisfied with the result and chose the most appropriate route.
            """),
            agent=agent,
            output_pydantic=RouteDecider,  # Use the class itself
            expected_output="""json of {"route": Literal['save_research','rewrite','restart']}"""
        )

    def crew(self, feedback):
        self.query_task = self.route_choose_task(self.route_decider_agent(), feedback)

    def run(self):
        return Crew(
            agents=[self.route_decider_agent()],
            tasks=[self.query_task],
            verbose=True,
        ).kickoff()
