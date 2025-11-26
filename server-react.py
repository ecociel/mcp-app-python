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

# import os
#
# from mcp.server.fastmcp import FastMCP
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
#
# mcp = FastMCP(
#     name="my-mcp-app",
#     sse_path="/mcp",
#     message_path="/mcp/messages",
#     stateless_http=True,
# )
#
#
# @mcp.resource("ui://static/widget/greeting-widget.html")
# async def widget_resource(path: str):
#     local_path = os.path.join("static", "widget", path)
#
#     if not os.path.exists(local_path):
#         return None
#
#     # Decide MIME type
#     if local_path.endswith(".html"):
#         mime = "text/html"
#     elif local_path.endswith(".js"):
#         mime = "application/javascript"
#     else:
#         mime = "application/octet-stream"
#
#     with open(local_path, "rb") as f:
#         return {
#             "mimeType": mime,
#             "data": f.read()
#         }
#
#
# print("Hello i am here in the react")
#
#
# @mcp.tool()
# def say_hello(name: str) -> dict:
#     print("Hello i am here")
#     return {
#         "structuredContent": {
#             "greeting": f"Hello, {name}! 👋"
#         },
#         "_meta": {
#             "openai/outputTemplate": "ui://static/widget/greeting-widget.html",
#             "openai/widgetCSP": "default-src 'self' https://esm.sh; script-src 'unsafe-inline' 'self' https://esm.sh;",
#         }
#     }
#
#
# app = FastAPI()
#
# app.mount("/static", StaticFiles(directory="static"), name="static")
#
# app.mount("/mcp", mcp.streamable_http_app())
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
