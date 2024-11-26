# #!/usr/bin/env python
# from typing import Optional
# from pydantic import BaseModel
# from crewai.flow.flow import Flow, listen, router, start, or_
# # import sys
# # sys.path.append("/home/manish/crew_ai/research_agents")
# # import crews.query_creator_crew
# from crews.query_creator_crew import QueryCreatorCrew
# from crews.search_agents_crew import SearchAgentsCrew
# from crews.research_synthesis_crew import ResearchSynthesisCrew
# from crews.critique_crew import CritiqueCrew

# from dotenv import load_dotenv
# load_dotenv()

# class ResearchFlowState(BaseModel):
#     original_query: str = ""
#     search_results: list = []
#     research_synthesis: str = ""
#     critique_feedback: Optional[str] = None
#     human_feedback: Optional[str] = None
#     retry_count: int = 0
#     is_research_satisfactory: bool = False

# class ResearchFlow(Flow[ResearchFlowState]):

#     @start()
#     def initialize_research(self):
#         """Initialize the research flow with the original query"""
#         print("Initializing research flow")
#         # self.state.original_query = initial_query

#     @router(initialize_research)
#     def generate_query(self):
#         """Create refined research query"""
#         print("Generating refined research query")
#         query_crew = QueryCreatorCrew()
#         query_crew.crew(self.state.original_query,self.state.human_feedback)
#         result = query_crew.run()
#         self.state.original_query = result.raw
#         return "search_research"

#     @router(generate_query)
#     def search_research(self):
#         """Parallel search by multiple search agents"""
#         print("Conducting parallel research")
#         search_crew = SearchAgentsCrew()
#         result = search_crew.crew().kickoff(
#             inputs={"query": self.state.original_query}
#         )
#         self.state.search_results = result.raw
#         return "synthesize_research"

#     @listen(or_(search_research,'synthesize_research'))
#     def synthesize_research(self):
#         """Synthesize research from multiple sources"""
#         print("Synthesizing research")
#         synthesis_crew = ResearchSynthesisCrew()
#         result = synthesis_crew.crew().kickoff(
#             inputs={
#                 "search_results": self.state.search_results,
#                 "original_query": self.state.original_query,
#                 "critique_feedback": self.state.critique_feedback
#             }
#         )
#         self.state.research_synthesis = result.raw
#         return "critique_research"

#     @router(synthesize_research)
#     def critique_research(self):
#         """Critique the research synthesis"""
#         print("Critiquing research")
#         if self.state.retry_count > 3:
#             return "max_retry_exceeded"

#         critique_crew = CritiqueCrew()
#         result = critique_crew.crew().kickoff(
#             inputs={
#                 "research_synthesis": self.state.research_synthesis,
#                 "original_query": self.state.original_query
#             }
#         )
        
#         self.state.critique_feedback = result.get('feedback', '')
#         self.state.is_research_satisfactory = result.get('is_satisfactory', False)
#         self.state.retry_count += 1

#         if self.state.is_research_satisfactory:
#             return "save_research"
#         else:
#             return "synthesize_research"

#     @listen("save_research")
#     def save_research(self):
#         """Save the final research output"""
#         print("Saving research output")
#         with open("research_output.txt", "w") as f:
#             f.write(self.state.research_synthesis)
#         print("Research completed successfully!")

#     @listen("max_retry_exceeded")
#     def max_retry_exceeded(self):
#         """Handle max retry scenario"""
#         print("Maximum research attempts exceeded")
#         print("Final research synthesis:")
#         print(self.state.research_synthesis)
#         print("Final critique feedback:")
#         print(self.state.critique_feedback)

# def kickoff(initial_query: str):
#     """Kickoff the research flow"""
#     research_flow = ResearchFlow()
#     research_flow.kickoff(inputs={"original_query":initial_query})

# def plot():
#     """Generate flow plot"""
#     research_flow = ResearchFlow()
#     research_flow.plot()

# if __name__ == "__main__":
#     kickoff("Your research topic here")



#!/usr/bin/env python
import json_repair
from typing import Optional
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, router, start, or_
from crews.query_creator_crew import QueryCreatorCrew
from crews.search_agents_crew import SearchAgentsCrew
from crews.human_feedback_agents_crew import HumanFeedbackCrew
from crews.research_synthesis_crew import ResearchSynthesisCrew
from crews.critique_crew import CritiqueCrew
from dotenv import load_dotenv
import os
import litellm
litellm.set_verbose=True

load_dotenv()

class ResearchFlowState(BaseModel):
    original_query: str = ""
    search_results: list = []
    research_synthesis: str = ""
    critique_feedback: Optional[str] = None
    human_feedback: Optional[str] = None
    retry_count: int = 0
    is_research_satisfactory: bool = False

class ResearchFlow(Flow[ResearchFlowState]):

    @start()
    def initialize_research(self):
        """Initialize the research flow with the original query"""
        print("Initializing research flow")
        # self.state.original_query = self.state.original_query")
        if not self.state.original_query:
            raise ValueError("Original query must be provided.")
        return "generate_query"


    @listen('initialize_research')
    def generate_query(self):
        """Create refined research query"""
        print("Generating refined research query")
        query_crew = QueryCreatorCrew()
        query_crew.crew(self.state.original_query, self.state.human_feedback)
        result = query_crew.run()
        if not result or not hasattr(result, 'raw'):
            raise RuntimeError("QueryCreatorCrew did not return a valid result.")
        self.state.original_query = result.raw
        # return search_research

    @listen('generate_query')
    def search_research(self):
        """Parallel search by multiple search agents"""
        print("Conducting parallel research")
        search_crew = SearchAgentsCrew()
        search_crew.crew(self.state.original_query)
        result = search_crew.run()
        if not result or not hasattr(result, 'raw'):
            raise RuntimeError("SearchAgentsCrew did not return valid results.")
        self.state.search_results = result.raw
        # return "search_research"

    @listen(or_(search_research,'synthesize_research'))
    def synthesize_research(self):
        """Synthesize research from multiple sources"""
        print("Synthesizing research")
        synthesis_crew = ResearchSynthesisCrew()
        synthesis_crew.crew(self.state.original_query,self.state.critique_feedback,self.state.search_results)
        result = synthesis_crew.run()
        # print(result)
        # import pdb
        # pdb.set_trace()
        if not result or not hasattr(result, 'raw'):
            raise RuntimeError("ResearchSynthesisCrew did not return a valid synthesis.")
        self.state.research_synthesis = result.raw
        # return "critique_research"

    @router(synthesize_research)
    def critique_research(self):
        """Critique the research synthesis"""
        print("Critiquing research")
        if self.state.retry_count > 3:
            return "max_retry_exceeded"

        critique_crew = CritiqueCrew()
        critique_crew.crew(self.state.original_query,self.state.research_synthesis)
        result = critique_crew.run() 
        
        if not result:
            raise RuntimeError("CritiqueCrew did not return valid feedback.")
        # import pdb
        # pdb.set_trace()
        result = json_repair.loads(result.raw.strip().replace("```json",'',).replace('```',''))
        self.state.critique_feedback = result.get('feedback', '')
        self.state.is_research_satisfactory = result.get('is_satisfactory', False)
        self.state.retry_count += 1

        if self.state.is_research_satisfactory:
            return "human_feedback"
        else:
            return "synthesize_research"
        
    @listen('human_feedback')
    def human_feedback_method(self):
        print("-"*20)
        print('Current answer: ')
        print(self.state.research_synthesis)
        print("-"*20)
        feedback = input('feedback about the result: ')
        self.state.human_feedback = feedback
        return 1
    @router(human_feedback_method)
    def feedback_router(self):
        feedback_crew = HumanFeedbackCrew()
        feedback_crew.crew(self.state.human_feedback)
        result = feedback_crew.run()
        feedback_route = {'save_research':'save_research',
                          'rewrite':'synthesize_research',
                          'restart':'initialize_research'}
        # import pdb
        # pdb.set_trace()
        result = result.raw.strip().replace("```json",'',).replace('```','')
        result = json_repair.loads(result)
        return feedback_route[result['route']]




    @listen("save_research")
    def save_research_method(self):
        """Save the final research output"""
        print("Saving research output")
        # import pdb 
        # pdb.set_trace()
        try:
            with open("research_output.json", "w") as f:
                f.write(self.state.research_synthesis.strip().replace("```json",'',).replace('```',''))
            print("Research completed successfully!")
        except IOError as e:
            print(f"Failed to save research output: {e}")
        return 0

    # @listen("synthesize_research")
    # def route_synthesize_research(self):

    @listen("max_retry_exceeded")
    def max_retry_exceeded_method(self):
        """Handle max retry scenario"""
        print("Maximum research attempts exceeded")
        print("Final research synthesis:")
        print(self.state.research_synthesis)
        print("Final critique feedback:")
        print(self.state.critique_feedback)

def kickoff(initial_query: str):
    """Kickoff the research flow"""
    if not initial_query:
        raise ValueError("Initial query is required to kickoff the flow.")
    research_flow = ResearchFlow()
    research_flow.kickoff(inputs={"original_query": initial_query})

def plot():
    """Generate flow plot"""
    research_flow = ResearchFlow()
    research_flow.plot()


if __name__ == "__main__":
    kickoff("Generative Image Watermarking")
    # plot()
