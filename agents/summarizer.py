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
    """
    初期要約を生成するエージェント (GPT-4.1最適化版)
    memo: 改良案はreference_docs\gpt41-prompt-manual-concise.mdを入力したClaude3.7sonnetに提案させたものをベースにしている
    """
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    
    # GPT-4.1向けに最適化された要約プロンプト
    # 明確な構造と出力フォーマット指定を活用
    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", """あなたはYouTube動画の文字起こしテキストを要約する専門家です。
        
        【目的】
        視聴者が動画内容を素早く理解し、重要な学びを得られるような要約を作成します。
        
        【出力形式】
        以下の厳密な構造に従って要約を作成してください：
        
        ## 【タイトル】
        [似た内容の動画のタイトルとも明確に区別できる最小限の文字数のタイトル]
        
        ## 【概要】(300字以内)
        [全体を簡潔に要約した1段落]
        
        ## 【主要トピック】
        - [トピック1]
        - [トピック2]
        - [トピック3]
        (3-5項目)
        
        ## 【重要ポイント】
        1. **[ポイント1のタイトル]**: [説明]
        2. **[ポイント2のタイトル]**: [説明]
        3. **[ポイント3のタイトル]**: [説明]
        (各説明は50字以内、合計3-5項目)
        
        ## 【キーワード】
        `[キーワード1]`, `[キーワード2]`, `[キーワード3]`, `[キーワード4]`, `[キーワード5]`
        (5-8個)
        
        ## 【実践アクション】
        1. [具体的な行動や応用方法1]
        2. [具体的な行動や応用方法2]
        (2-3項目)
        
        【重要ルール】
        - 常に客観的かつ正確に原文の内容を反映すること
        - 要約全体で1000字以内に収めること
        - 内容の網羅性を優先し、重要情報の漏れがないようにすること
        - 専門用語は必ず説明を加えること
        - 情報の優先順位を明確にすること
        """),
        ("user", "以下の文字起こしテキストを要約してください:\n\n{text}")
    ])
    
    # Chain-of-Thoughtアプローチを活用した要約関数
    def summarize(state: SummaryState) -> SummaryState:
        text = " ".join([chunk["text"] for chunk in state.transcript])
        
        # GPT-4.1の内部モノローグ/Chain-of-Thoughtの特性を活用
        cot_prompt = ChatPromptTemplate.from_messages([
            ("system", """文字起こしテキストを要約する前に、以下のステップで分析してください:
            
            [内部思考]
            1. このテキストの主題は何か
            2. 話者が伝えようとしている主要なメッセージは何か
            3. 重要な事実や数字はあるか
            4. 専門用語とその意味は何か
            5. 視聴者が実践できる具体的なアクションは何か
            
            [要約作成]
            上記の分析に基づいて、指定された形式で要約を作成してください。
            """),
            ("user", f"以下の文字起こしテキストを分析してください:\n\n{text}")
        ])
        
        # 分析ステップ
        formatted_cot_prompt = cot_prompt.format_messages()
        analysis = llm.invoke(formatted_cot_prompt)
        
        # 要約ステップ
        formatted_summarize_prompt = summarize_prompt.format_messages(text=text)
        response = llm.invoke(formatted_summarize_prompt)
        
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
