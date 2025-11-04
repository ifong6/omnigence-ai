from app.finance_agent.agent_config.FinanceAgentState import FinanceAgentState
from app.llm.invoke_openai_llm import invoke_openai_llm
from app.prompt.planning_prompt_template import PLANNING_PROMPT_TEMPLATE, PlannerOutput

def planner_node(state: FinanceAgentState):
    print("- [INVOKE] [planner_node]")
    print(f"  [DEBUG] Current state.intents: {state.intents}")
    print(f"  [DEBUG] Current state.index: {state.index}")

    # Plan handlers based on intents
    system_prompt = PLANNING_PROMPT_TEMPLATE.format(intents=state.intents)
    parsed_response = invoke_openai_llm(system_prompt, PlannerOutput)

    # Access as Pydantic model attributes
    print(f"  [DEBUG] Planner returned next_handlers: {parsed_response.next_handlers}")
    print(f"  [DEBUG] Type: {type(parsed_response.next_handlers)}")

    return {
        "next_handlers": parsed_response.next_handlers
    }