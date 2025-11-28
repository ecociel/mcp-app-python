from pathlib import Path
from mcp.server.fastmcp import FastMCP
import mcp.types as types
from pydantic import BaseModel, Field

HTML_PATH = Path(__file__).parent / "static" / "widget" / "greeting-widget.html"
HTML_TEXT = HTML_PATH.read_text(encoding="utf8")

MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/greeting.html"

mcp = FastMCP(name="minimal-react-mcp", stateless_http=True)


class WidgetInput(BaseModel):
    name: str = Field(..., description="Name to greet.")


@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="show-greeting-widget",
            title="Show Greeting React Widget",
            description="Render a React JSX widget.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"],
            },
            _meta={
                "openai/outputTemplate": WIDGET_URI,
                "openai/widgetAccessible": True,
                "openai/resultCanProduceWidget": True,
            },
        )
    ]


@mcp._mcp_server.list_resources()
async def list_resources():
    return [
        types.Resource(
            name="greeting-widget",
            title="Greeting React Widget",
            uri=WIDGET_URI,
            description="React JSX widget HTML.",
            mimeType=MIME_TYPE,
        )
    ]


async def handle_resource(req: types.ReadResourceRequest):
    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=WIDGET_URI,
                    mimeType=MIME_TYPE,
                    text=HTML_TEXT,
                )
            ]
        )
    )


mcp._mcp_server.request_handlers[types.ReadResourceRequest] = handle_resource


async def call_tool(req: types.CallToolRequest):
    args = req.params.arguments or {}
    name = args.get("name", "")

    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text="React widget rendered!")],
            structuredContent={"name": name},
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)