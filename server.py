from pathlib import Path
import mcp.types as types
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent

DIST_DIR = ROOT / "dist" / "widgets" / "greeting-widget"
DEV_HTML = ROOT / "widgets" / "greeting-widget" / "index.html"
WIDGET_URI = "ui://widget/greeting-widget.html"
MIME_TYPE = "text/html+skybridge"

mcp = FastMCP(name="minimal-react-widget", stateless_http=True)


@mcp._mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="show-greeting-widget",
            title="Show Greeting React Widget",
            description="Displays the greeting widget",
            inputSchema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
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
            uri=WIDGET_URI,
            mimeType=MIME_TYPE,
            description="Greeting widget HTML",
        )
    ]


def load_html():
    # Load built Vite HTML first
    if DIST_DIR.exists():
        html_files = list(DIST_DIR.glob("*.html"))
        if html_files:
            html_path = html_files[0]
            html = html_path.read_text(encoding="utf8")

            # Inline JS and CSS assets into <script> and <style>
            for asset in DIST_DIR.rglob("*"):
                if asset.suffix == ".js":
                    js_text = asset.read_text(encoding="utf8")
                    html = html.replace(
                        f'./assets/{asset.name}',
                        ""
                    )
                    html = html.replace(
                        f'<script type="module" crossorigin src="">',
                        f"<script>{js_text}</script>"
                    )

                if asset.suffix == ".css":
                    css_text = asset.read_text(encoding="utf8")
                    html = html.replace(
                        f'<link rel="stylesheet" href="./assets/{asset.name}">',
                        f"<style>{css_text}</style>"
                    )

            return html

    # Fallback: return raw dev HTML
    if DEV_HTML.exists():
        return DEV_HTML.read_text(encoding="utf8")

    return "<html><body>Widget not found</body></html>"


async def read_resource(req: types.ReadResourceRequest):
    if str(req.params.uri) != WIDGET_URI:
        return types.ServerResult(types.ReadResourceResult(contents=[]))

    html = load_html()

    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=WIDGET_URI,
                    mimeType=MIME_TYPE,
                    text=html,
                )
            ]
        )
    )


mcp._mcp_server.request_handlers[types.ReadResourceRequest] = read_resource

async def call_tool(req: types.CallToolRequest):
    args = req.params.arguments or {}
    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text="Widget Loaded!")],
            structuredContent=args,
        )
    )


mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool


app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# from pathlib import Path
# import re
# import mcp.types as types
# from mcp.server.fastmcp import FastMCP
#
# ROOT = Path(__file__).resolve().parent
#
# DIST_WIDGET_DIR = ROOT / "dist" / "widgets" / "greeting-widget"
# DEV_WIDGET_HTML = ROOT / "widgets" / "greeting-widget" / "index.html"
#
# WIDGET_URI = "ui://widget/greeting-widget.html"
# MIME_TYPE = "text/html+skybridge"
#
# mcp = FastMCP(name="react-widget-mcp", stateless_http=True)
#
#
# @mcp._mcp_server.list_tools()
# async def list_tools():
#     return [
#         types.Tool(
#             name="show-greeting-widget",
#             title="Show Greeting React Widget",
#             description="Render the widget",
#             inputSchema={
#                 "type": "object",
#                 "properties": {"name": {"type": "string"}},
#                 "required": ["name"]
#             },
#             _meta={
#                 "openai/outputTemplate": WIDGET_URI,
#                 "openai/widgetAccessible": True,
#                 "openai/resultCanProduceWidget": True
#             }
#         )
#     ]
#
#
# @mcp._mcp_server.list_resources()
# async def list_resources():
#     return [
#         types.Resource(
#             name="greeting-widget",
#             title="Greeting Widget",
#             uri=WIDGET_URI,
#             mimeType=MIME_TYPE,
#         )
#     ]
#
#
# def find_html():
#     """Find built widget HTML or fallback to dev version."""
#     if DIST_WIDGET_DIR.exists():
#         html_files = list(DIST_WIDGET_DIR.glob("*.html"))
#         if html_files:
#             return html_files[0]
#     if DEV_WIDGET_HTML.exists():
#         return DEV_WIDGET_HTML
#     return None
#
#
# def inline_assets(html: str) -> str:
#     """
#     Convert Vite output:
#       <script type="module" src="./assets/xxx.js">
#       <link rel="stylesheet" href="./assets/xxx.css">
#     Into inline <script> and <style>.
#     """
#
#     # --- Inline JS files ---
#     script_tags = re.findall(r'<script[^>]+src="([^"]+\.js)"[^>]*></script>', html)
#     for src in script_tags:
#         js_path = DIST_WIDGET_DIR / src.replace("./", "")
#         if js_path.exists():
#             js_code = js_path.read_text(encoding="utf8")
#             html = html.replace(
#                 f'<script type="module" crossorigin src="{src}"></script>',
#                 f"<script>\n{js_code}\n</script>"
#             )
#
#     # --- Inline CSS files ---
#     link_tags = re.findall(r'<link[^>]+href="([^"]+\.css)"[^>]*>', html)
#     for href in link_tags:
#         css_path = DIST_WIDGET_DIR / href.replace("./", "")
#         if css_path.exists():
#             css_code = css_path.read_text(encoding="utf8")
#             html = html.replace(
#                 f'<link rel="stylesheet" href="{href}">',
#                 f"<style>\n{css_code}\n</style>"
#             )
#
#     return html
#
#
# async def read_resource(req: types.ReadResourceRequest):
#     uri = str(req.params.uri)
#
#     # Serve widget HTML
#     if uri == WIDGET_URI:
#         html_file = find_html()
#         if not html_file:
#             return types.ServerResult(types.ReadResourceResult(contents=[]))
#
#         html = html_file.read_text(encoding="utf8")
#
#         # Inline JS + CSS so ChatGPT does NOT need ui:// asset fetching
#         html = inline_assets(html)
#
#         return types.ServerResult(
#             types.ReadResourceResult(
#                 contents=[
#                     types.TextResourceContents(
#                         uri=WIDGET_URI,
#                         mimeType=MIME_TYPE,
#                         text=html
#                     )
#                 ]
#             )
#         )
#
#     # Anything else returns empty
#     return types.ServerResult(types.ReadResourceResult(contents=[]))
#
#
# mcp._mcp_server.request_handlers[types.ReadResourceRequest] = read_resource
#
#
# async def call_tool(req: types.CallToolRequest):
#     args = req.params.arguments or {}
#     name = args.get("name", "")
#     return types.ServerResult(
#         types.CallToolResult(
#             content=[types.TextContent(type="text", text="Widget Loaded!")],
#             structuredContent={"name": name},
#         )
#     )
#
#
# mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool
#
# app = mcp.streamable_http_app()
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



# from pathlib import Path
# import mcp.types as types
# from mcp.server.fastmcp import FastMCP
#
# ROOT = Path(__file__).resolve().parent
#
# DIST_WIDGET_DIR = ROOT / "dist" / "widgets" / "greeting-widget"
# DEV_WIDGET_HTML = ROOT / "widgets" / "greeting-widget" / "index.html"
#
# WIDGET_URI = "ui://widget/greeting-widget.html"
# ASSETS_URI = "ui://widget/greeting-widget-assets/"
# MIME_TYPE = "text/html+skybridge"
#
# mcp = FastMCP(name="react-widget-mcp", stateless_http=True)
#
#
# @mcp._mcp_server.list_tools()
# async def list_tools():
#     return [
#         types.Tool(
#             name="show-greeting-widget",
#             title="Show Greeting React Widget",
#             description="Render the widget",
#             inputSchema={
#                 "type": "object",
#                 "properties": {"name": {"type": "string"}},
#                 "required": ["name"]
#             },
#             _meta={
#                 "openai/outputTemplate": WIDGET_URI,
#                 "openai/widgetAccessible": True,
#                 "openai/resultCanProduceWidget": True
#             }
#         )
#     ]
#
#
# @mcp._mcp_server.list_resources()
# async def list_resources():
#     resources = [
#         types.Resource(
#             name="greeting-widget",
#             title="Greeting Widget",
#             uri=WIDGET_URI,
#             mimeType=MIME_TYPE,
#         )
#     ]
#
#     if DIST_WIDGET_DIR.exists():
#         for f in DIST_WIDGET_DIR.rglob("*"):
#             if f.is_file() and f.name != "index.html":
#                 rel = str(f.relative_to(DIST_WIDGET_DIR)).replace("\\", "/")
#                 uri = ASSETS_URI + rel
#                 resources.append(
#                     types.Resource(
#                         name=f"asset-{f.name}",
#                         uri=uri,
#                         mimeType="application/javascript" if f.suffix == ".js" else "text/css",
#                         description="Widget asset"
#                     )
#                 )
#     return resources
#
#
# def find_html():
#     if DIST_WIDGET_DIR.exists():
#         html_files = list(DIST_WIDGET_DIR.glob("*.html"))
#         if html_files:
#             return html_files[0]
#     if DEV_WIDGET_HTML.exists():
#         return DEV_WIDGET_HTML
#     return None
#
#
# async def read_resource(req: types.ReadResourceRequest):
#     uri = str(req.params.uri)
#
#     if uri == WIDGET_URI:
#         html_file = find_html()
#         if not html_file:
#             return types.ServerResult(types.ReadResourceResult(contents=[]))
#
#         html = html_file.read_text(encoding="utf8")
#
#         html = html.replace(
#             './assets/',
#             ASSETS_URI + 'assets/'
#         )
#
#         return types.ServerResult(
#             types.ReadResourceResult(
#                 contents=[
#                     types.TextResourceContents(
#                         uri=WIDGET_URI,
#                         mimeType=MIME_TYPE,
#                         text=html
#                     )
#                 ]
#             )
#         )
#
#     if uri.startswith(ASSETS_URI):
#         rel = uri[len(ASSETS_URI):]
#         file_path = DIST_WIDGET_DIR / rel
#
#         if not file_path.exists():
#             return types.ServerResult(types.ReadResourceResult(contents=[]))
#
#         mime = (
#             "application/javascript"
#             if file_path.suffix == ".js"
#             else "text/css"
#         )
#
#         return types.ServerResult(
#             types.ReadResourceResult(
#                 contents=[
#                     types.TextResourceContents(
#                         uri=uri,
#                         mimeType=mime,
#                         text=file_path.read_text(encoding="utf8")
#                     )
#                 ]
#             )
#         )
#
#     return types.ServerResult(types.ReadResourceResult(contents=[]))
#
#
# mcp._mcp_server.request_handlers[types.ReadResourceRequest] = read_resource
#
#
# async def call_tool(req: types.CallToolRequest):
#     args = req.params.arguments or {}
#     name = args.get("name", "")
#     return types.ServerResult(
#         types.CallToolResult(
#             content=[types.TextContent(type="text", text="Widget Loaded!")],
#             structuredContent={"name": name},
#         )
#     )
#
#
# mcp._mcp_server.request_handlers[types.CallToolRequest] = call_tool
#
# app = mcp.streamable_http_app()
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)