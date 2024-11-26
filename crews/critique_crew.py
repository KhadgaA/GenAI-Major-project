from crewai import Agent, Crew, Task
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

class OutputCritique(BaseModel):
    is_satisfactory: bool = Field(description="Boolean indicating synthesis quality")
    feedback: str = Field(description="Suggestions for synthesis improvement")
class OutputImprovement(BaseModel):
    improvement_strategy: str = Field(description="Detailed improvement recommendations")

class CritiqueCrew:
    def quality_assessment_agent(self):
        return Agent(
            role="Research Quality Assessor",
            goal="Critically evaluate research synthesis for depth, accuracy, and relevance",
            backstory="A meticulous expert in assessing research quality, identifying gaps, and providing constructive feedback.",
            verbose=True,
            llm='cohere/command-r-plus-08-2024'
        )

    def improvement_suggestions_agent(self):
        return Agent(
            role="Research Improvement Strategist",
            goal="Provide actionable recommendations to enhance research synthesis",
            backstory="A strategic thinker who can identify specific areas of improvement and suggest concrete enhancements.",
            verbose=True,
            llm='cohere/command-r-plus-08-2024'
        )

    def critique_task(self, quality_assessment, original_query, research_synthesis):
        return Task(
            description=f"""
            Critique Research Synthesis for query: {original_query}
            
            Research Synthesis:
            {research_synthesis}
            
            Critique Objectives:
            1. Assess overall research quality
            2. Identify potential gaps or weaknesses
            3. Evaluate relevance to the original query
            4. Provide specific, actionable improvement suggestions
            5. Determine if research meets high-quality standards
            """,
            agent=quality_assessment,
            output_pydantic=OutputCritique,
            expected_output= """A Json of {
                "is_satisfactory": "Boolean indicating research quality",
                "feedback": "Detailed critique and improvement suggestions"
                }
            """
        )

    def improvement_task(self, improvement_agent, quality_assessment):
        return Task(
            description="""
            Generate specific improvement strategies for research synthesis
            
            Use the quality assessment feedback to:
            1. Develop targeted improvement recommendations
            2. Suggest additional research directions
            3. Highlight potential blind spots
            """,
            agent=improvement_agent,
            output_pydantic=OutputImprovement,
            expected_output="""Json of {"improvement_strategy": "Detailed improvement recommendations"}"""
        )

    def crew(self,original_query, research_synthesis):
        self.quality_assessment = self.quality_assessment_agent()
        # self.improvement_agent = self.improvement_suggestions_agent()

        self.critique_task = self.critique_task(self.quality_assessment, original_query, research_synthesis)
        # self.improvement_task = self.improvement_task(self.improvement_agent, self.quality_assessment)

    
    def run(self):
        return Crew(
            agents=[self.quality_assessment],
            tasks=[self.critique_task],
            verbose=True
        ).kickoff()
