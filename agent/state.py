from typing import TypeDict, List, Any, Optional
from operator import add

class MainAgentState(TypeDict):
    user_query: str
    session_id: str

    agent_response: Optional[str]
    reference_metadata: Optional[List[Any]]

    mcp_response: Optional[str]
    response_from_google_sheet: Optional[str]