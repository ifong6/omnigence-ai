from langchain_core.prompts import PromptTemplate
from langchain_core.tools.render import render_text_description_and_args
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic.agents.output_parsers.react_single_input import ReActSingleInputOutputParser
from app.llm.invoke_claude_llm import get_claude_llm
from app.prompt.legacy.job_crud_prompt import REACT_PROMPT
from typing import List, Any, Optional


def invoke_react_agent(
    tools: List[Any],
    user_input: str,
    verbose: bool = True,
    handle_parsing_errors: bool = True,
    max_iterations: int = 5,
    return_intermediate_steps: bool = True,
    prompt_template: Optional[str] = None
) -> Any:
    template = prompt_template if prompt_template is not None else REACT_PROMPT

    prompt = PromptTemplate(
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
        template=template
    )

    llm = get_claude_llm()

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
