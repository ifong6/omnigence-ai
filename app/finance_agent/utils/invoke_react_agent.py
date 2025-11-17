from langchain_core.prompts import PromptTemplate
from langchain_core.tools.render import render_text_description_and_args
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.agents.output_parsers.react_single_input import ReActSingleInputOutputParser
from app.llm.invoke_openai_llm import get_openai_llm
from app.prompt.job_crud_prompt import REACT_PROMPT
from typing import List, Any


def invoke_react_agent(
    tools: List[Any],
    user_input: str,
    verbose: bool = True,
    handle_parsing_errors: bool = True,
    max_iterations: int = 5,
    return_intermediate_steps: bool = True
) -> Any:
    """
    Create and invoke a ReAct agent with the given tools and user input.

    Args:
        tools: List of tools to be used by the agent
        user_input: The user input to process
        verbose: Whether to print verbose output (default: True)
        handle_parsing_errors: Whether to handle parsing errors (default: True)
        max_iterations: Maximum number of iterations (default: 5)
        return_intermediate_steps: Whether to return intermediate steps (default: True)

    Returns:
        dict: Response from the agent executor

    Example:
        response = invoke_react_agent(tools=job_crud_tools, user_input=state.user_input)
    """
    prompt = PromptTemplate(
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
        template=REACT_PROMPT
    )

    llm = get_openai_llm()

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
        tools_renderer=render_text_description_and_args,
        output_parser=ReActSingleInputOutputParser(),
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=handle_parsing_errors,
        max_iterations=max_iterations,
        return_intermediate_steps=return_intermediate_steps
    )

    return executor.invoke({"input": user_input})
