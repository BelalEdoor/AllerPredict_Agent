"""MCP Server for AllerPredict AI - Simplified Version"""
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from agents.crew_orchestrator import AllerPredictCrew

# Initialize crew (works with or without MCP)
crew = AllerPredictCrew()

def analyze_product_tool(product_query: str, user_allergies: list = None, detailed: bool = False):
    """Standalone function for product analysis"""
    user_profile = {"allergies": user_allergies} if user_allergies else None
    
    if detailed:
        result = crew.analyze_product(product_query, user_profile)
    else:
        result = crew.quick_analyze(product_query)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    response = f"""**AllerPredict AI Analysis**

**Product:** {result['product']['name']} by {result['product'].get('brand', 'Unknown')}
**Category:** {result['product'].get('category', 'Unknown')}
**Known Allergens:** {', '.join(result['product'].get('allergens', [])) or 'None'}
**Ethical Score:** {result['product'].get('ethical_score', 'N/A')}/10

**Analysis:**
{result.get('analysis', 'No detailed analysis available')}

**Safe Alternatives:**
"""
    for alt in result.get('alternatives', [])[:3]:
        response += f"\n- {alt['name']} by {alt['brand']} (Score: {alt['ethical_score']}/10)"
    
    return response

def find_alternatives_tool(allergens: list, category: str = None):
    """Standalone function for finding alternatives"""
    alternatives = crew.rag.find_alternatives(allergens, exclude_id=-1)
    
    if category:
        alternatives = [alt for alt in alternatives if alt.get('category', '').lower() == category.lower()]
    
    response = f"**Safe Alternatives (Avoiding: {', '.join(allergens)})**\n\n"
    for alt in alternatives[:5]:
        response += f"✓ {alt['name']} by {alt['brand']}\n"
        response += f"  Allergens: {', '.join(alt['allergens']) or 'None'}\n"
        response += f"  Score: {alt['ethical_score']}/10\n\n"
    
    return response

def get_product_info_tool(product_name: str):
    """Standalone function for getting product info"""
    results = crew.rag.search(product_name, top_k=1)
    
    if not results:
        return "Product not found"
    
    product = results[0]
    info = f"""**{product['name']}** by {product['brand']}

**Category:** {product['category']}
**Ingredients:** {', '.join(product['ingredients'])}
**Allergens:** {', '.join(product['allergens']) or 'None'}
**Ethical Score:** {product['ethical_score']}/10
**Certifications:** {', '.join(product['certifications']) or 'None'}

**Description:** {product['description']}
**Company:** {product['company_info']}
"""
    return info

# MCP Server setup (only if MCP is available)
if MCP_AVAILABLE:
    server = Server("allerpredict-ai")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List all available MCP tools"""
        return [
            types.Tool(
                name="analyze_product",
                description="Analyze a product for allergens, risks, and get safe alternatives",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "product_query": {
                            "type": "string",
                            "description": "Name or description of the product"
                        },
                        "user_allergies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of user's known allergies"
                        },
                        "detailed": {
                            "type": "boolean",
                            "description": "Use full multi-agent analysis"
                        }
                    },
                    "required": ["product_query"]
                }
            ),
            types.Tool(
                name="find_alternatives",
                description="Find safe alternative products",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "allergens_to_avoid": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of allergens to avoid"
                        },
                        "category": {
                            "type": "string",
                            "description": "Product category"
                        }
                    },
                    "required": ["allergens_to_avoid"]
                }
            ),
            types.Tool(
                name="get_product_info",
                description="Get detailed information about a product",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "Product name"
                        }
                    },
                    "required": ["product_name"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool execution"""
        
        if name == "analyze_product":
            result = analyze_product_tool(
                arguments["product_query"],
                arguments.get("user_allergies", []),
                arguments.get("detailed", False)
            )
            return [types.TextContent(type="text", text=result)]
        
        elif name == "find_alternatives":
            result = find_alternatives_tool(
                arguments["allergens_to_avoid"],
                arguments.get("category")
            )
            return [types.TextContent(type="text", text=result)]
        
        elif name == "get_product_info":
            result = get_product_info_tool(arguments["product_name"])
            return [types.TextContent(type="text", text=result)]
        
        raise ValueError(f"Unknown tool: {name}")

    async def main():
        """Run MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("\n" + "="*60)
        print("MCP Server - Installation Required")
        print("="*60)
        print("\nMCP is not installed. To use the MCP server:")
        print("1. Install MCP: pip install mcp")
        print("2. Run this script again")
        print("\nNote: The main application works without MCP.")
        print("MCP is only needed for Claude Desktop integration.")
        print("\nAlternatively, you can use the standalone functions:")
        print("- analyze_product_tool()")
        print("- find_alternatives_tool()")
        print("- get_product_info_tool()")
        print("="*60 + "\n")
    else:
        import asyncio
        print("Starting MCP Server for AllerPredict AI...")
        asyncio.run(main())
        