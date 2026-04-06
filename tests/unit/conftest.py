import sys
from unittest.mock import MagicMock
from types import ModuleType

def mock_package(name):
    m = ModuleType(name)
    m.__path__ = []
    sys.modules[name] = m
    return m

# Create the hierarchy
google = mock_package("google")
adk = mock_package("google.adk")
google.adk = adk

agents = mock_package("google.adk.agents")
adk.agents = agents

models = mock_package("google.adk.models")
adk.models = models

tools = mock_package("google.adk.tools")
adk.tools = tools

mcp_tool = mock_package("google.adk.tools.mcp_tool")
tools.mcp_tool = mcp_tool

mcp_session_manager = mock_package("google.adk.tools.mcp_tool.mcp_session_manager")
mcp_tool.mcp_session_manager = mcp_session_manager

tool_context = mock_package("google.adk.tools.tool_context")
tools.tool_context = tool_context

callback_context = mock_package("google.adk.agents.callback_context")
agents.callback_context = callback_context

llm_request = mock_package("google.adk.models.llm_request")
models.llm_request = llm_request

genai = mock_package("google.genai")
google.genai = genai

genai_types = mock_package("google.genai.types")
genai.types = genai_types

# Now add MagicMocks for the actual classes/functions needed
agents.LlmAgent = MagicMock()
tools.BaseTool = MagicMock()
mcp_tool.MCPToolset = MagicMock()
mcp_session_manager.StreamableHTTPConnectionParams = MagicMock()
tool_context.ToolContext = MagicMock()
genai_types.GenerateContentConfig = MagicMock()
genai_types.HarmCategory = MagicMock()
genai_types.HarmBlockThreshold = MagicMock()
genai_types.SafetySetting = MagicMock()
genai_types.HttpOptions = MagicMock()
genai_types.HttpRetryOptions = MagicMock()
genai_types.Content = MagicMock()
genai_types.Part = MagicMock()

callback_context.CallbackContext = MagicMock()
llm_request.LlmRequest = MagicMock()
