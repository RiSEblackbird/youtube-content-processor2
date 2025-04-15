from typing import Dict, List, Any
from langgraph.graph import Graph, StateGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class SummaryState(BaseModel):
    """要約処理の状態を管理するクラス"""
    transcript: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    needs_refinement: bool = True

def create_initial_summarizer() -> StateGraph:
    """初期要約を生成するエージェント"""
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    
    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "あなたは文字起こしテキストを要約する専門家です。"),
        ("user", "以下の文字起こしテキストを300字程度で要約してください:\n\n{text}")
    ])
    
    def summarize(state: SummaryState) -> SummaryState:  # 型をSummaryStateに変更
        text = " ".join([chunk["text"] for chunk in state.transcript])
        response = llm.invoke(summarize_prompt.format(text=text))
        return SummaryState(
            transcript=state.transcript,
            summary=response.content,
            needs_refinement=True
        )
    
    workflow = StateGraph(SummaryState)
    workflow.add_node("summarize", summarize)
    workflow.set_entry_point("summarize")
    workflow.set_finish_point("summarize")
    
    return workflow.compile()

def create_refinement_agent() -> StateGraph:
    """要約を改善するエージェント"""
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    
    refine_prompt = ChatPromptTemplate.from_messages([
        ("system", "要約の品質を改善する専門家として、以下の要約をより簡潔で分かりやすく改善してください。"),
        ("user", "現在の要約:\n{summary}")
    ])
    
    def refine(state: SummaryState) -> SummaryState:  # 型をSummaryStateに変更
        if not state.needs_refinement:
            return state
        
        response = llm.invoke(refine_prompt.format(summary=state.summary))
        return SummaryState(
            transcript=state.transcript,
            summary=response.content,
            needs_refinement=False
        )
    
    workflow = StateGraph(SummaryState)
    workflow.add_node("refine", refine)
    workflow.set_entry_point("refine")
    workflow.set_finish_point("refine")
    
    return workflow.compile()