"""LangGraph wiring for the MemeVid Jokestruc workflow."""
import json

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command, interrupt

from .Nodes.caption_generator import caption_generator
from .Nodes.caption_selector import caption_selector
from .Nodes.dag_composer import dag_composer
from .Nodes.human_review import human_caption_review
from .Nodes.humor_framer import humor_framer
from .Nodes.input_parser import input_parser
from .Nodes.renderer import renderer
from .Nodes.scene_mapper import scene_mapper
from .Nodes.timing_composer import timing_composer
from .Nodes.video_insight.video_insight import video_insight
from .state import JokeState

_builder = StateGraph(JokeState)

# Nodes
_builder.add_node("input_parser", input_parser)
_builder.add_node("video_insight", video_insight)
_builder.add_node("humor_framer", humor_framer)
_builder.add_node("caption_generator", caption_generator)
_builder.add_node("scene_mapper", scene_mapper)
_builder.add_node("timing_composer", timing_composer)
_builder.add_node("dag_composer", dag_composer)
_builder.add_node("renderer", renderer)
_builder.add_node("caption_selector", caption_selector)
_builder.add_node("human_review", human_caption_review)


# Flow
_builder.set_entry_point("input_parser")
_builder.add_edge("input_parser", "video_insight")
_builder.add_edge("video_insight", "humor_framer")
_builder.add_edge("humor_framer", "caption_generator")
_builder.add_edge("caption_generator", "human_review")
_builder.add_edge("human_review", "timing_composer")

_builder.add_edge("timing_composer", "dag_composer")
_builder.add_edge("dag_composer", "renderer")
_builder.add_edge("renderer", END)

_memory = MemorySaver()
app = _builder.compile(checkpointer=_memory)


async def run_graph(initial_state: JokeState, thread_id: str) -> JokeState:
    """Execute the workflow until completion or interrupt."""
    return await app.ainvoke(
        initial_state,
        config={"configurable": {"thread_id": thread_id}},
    )


async def resume_graph(thread_id: str, resume_payload: dict) -> JokeState:
    """Resume a paused workflow thread with human-provided data."""
    return await app.ainvoke(
        Command(resume=resume_payload),
        config={"configurable": {"thread_id": thread_id}},
    )
