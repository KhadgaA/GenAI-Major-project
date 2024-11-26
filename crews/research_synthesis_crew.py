from crewai import Agent, Crew, Task
from pydantic import BaseModel, Field

class OutputCritique(BaseModel):
    is_synthesis_valid: bool = Field(description="Boolean indicating synthesis quality")
    improvement_notes: str = Field(description="Suggestions for synthesis improvement")

class OutputSynthesis(BaseModel):
    research_synthesis: str = Field(description="Comprehensive research summary")
    key_insights: str = Field(description="List of key research insights")

class ResearchSynthesisCrew:
    def synthesis_lead_agent(self):
        return Agent(
            role="Research Synthesis Lead",
            goal="Integrate and synthesize research findings from multiple sources",
            backstory="An expert researcher who can connect complex ideas, identify patterns, and create comprehensive research summaries.",
            verbose=True,
            llm='cohere/command-r-plus-08-2024'
        )

    def critical_analysis_agent(self):
        return Agent(
            role="Critical Analysis Specialist",
            goal="Evaluate research findings for coherence, relevance, and depth",
            backstory="A critical thinker who ensures research synthesis is rigorous, balanced, and scientifically sound.",
            verbose=True,
            llm='cohere/command-r-plus-08-2024'
        )

    def synthesis_task(self, synthesis_lead, original_query, critique_feedback, search_results):
        return Task(
            description=f"""
            Synthesize research findings for query: {original_query}

            Previous critique feedback: {critique_feedback}

            Research Sources:
            {search_results}

            Synthesis Requirements:
            1. Integrate findings from multiple sources
            2. Identify key themes and insights
            3. Resolve conflicting information
            4. Create a coherent and comprehensive research summary
            5. Incorporate previous critique feedback
            """,
            agent=synthesis_lead,
            output_pydantic=OutputSynthesis,
            expected_output="""json of{"research_synthesis": A comprehensive research summary, "key_insights": Key insights derived from the research}"""
        )

    def critique_task(self, critical_analysis):
        return Task(
            description="""
            Review and validate the research synthesis for:
            1. Factual accuracy
            2. Comprehensiveness
            3. Logical coherence
            4. Addressing the original research query
            """,
            agent=critical_analysis,
            output_pydantic=OutputCritique,
            expected_output="""json of {"is_synthesis_valid": Boolean indicating synthesis quality,"improvement_notes": Suggestions for synthesis improvement.}"""
        )

    def crew(self, original_query, critique_feedback, search_results):
        self.synthesis_lead = self.synthesis_lead_agent()
        self.synthesis_task = self.synthesis_task(
            self.synthesis_lead, original_query, critique_feedback, search_results
        )

    def run(self):
        return Crew(
            agents=[self.synthesis_lead],
            tasks=[self.synthesis_task],
            verbose=True
        ).kickoff()
