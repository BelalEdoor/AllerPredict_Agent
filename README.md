# AllerPredict AI - Agentic Product Analysis System

## 🎯 Project Overview

**AllerPredict AI** is an advanced agentic AI application that analyzes food products for allergens, safety risks, and ethical concerns. The system uses a multi-agent architecture powered by CrewAI, integrated with a RAG (Retrieval-Augmented Generation) pipeline and exposed through an MCP (Model Context Protocol) server.

### Key Features

- 🤖 **Multi-Agent System**: Two specialized AI agents working together
  - **Product Safety Analyst**: Analyzes allergens and safety risks
  - **Recommendation Specialist**: Suggests safer and more ethical alternatives

- 🔍 **RAG Pipeline**: Semantic search over product database using SentenceTransformers
- 🌐 **MCP Server**: Standardized tool exposure using FastMCP
- ⚡ **FastAPI Backend**: High-performance REST API
- 💻 **React Frontend**: Modern, responsive chat interface
- 🔄 **Dual Mode**: Support for both agentic and legacy analysis

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  - Chat Interface                                           │
│  - Product Browser                                          │
│  - Mode Toggle (Agentic vs Legacy)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                  BACKEND (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MCP Server (FastMCP)                                  │ │
│  │  - analyze_product tool                                │ │
│  │  - get_products tool                                   │ │
│  │  - health_check tool                                   │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │  MCP Tool Wrapper                                      │ │
│  │  - ProductAnalysisTool                                 │ │
│  │  - Input/Output schemas                                │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │  CrewAI Multi-Agent System                            │ │
│  │  ┌──────────────────┐  ┌──────────────────────────┐   │ │
│  │  │ Analysis Agent   │→ │ Recommendation Agent     │   │ │
│  │  │ - RAG Tool       │  │ - Generates alternatives │   │ │
│  │  │ - Risk assess    │  │ - Final report           │   │ │
│  │  └──────────────────┘  └──────────────────────────┘   │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │  RAG Engine                                            │ │
│  │  - SentenceTransformers (all-MiniLM-L6-v2)            │ │
│  │  - Vector similarity search                            │ │
│  │  - Product metadata (20+ products)                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm 9+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python main.py
```

Backend will start at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend/react-app

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will start at `http://localhost:3000` or `http://localhost:5173`

---

## 📡 API Endpoints

### V2 (Agentic) Endpoints

- **POST** `/api/v2/analyze` - Full agentic analysis
  ```json
  {
    "product_name": "Oreo Cookies",
    "user_context": "I have a soy allergy"
  }
  ```

- **GET** `/api/v2/products` - Get all products
- **GET** `/api/v2/health` - System health check

### Legacy Endpoints

- **POST** `/analyze_product` - Direct RAG analysis
- **GET** `/products` - Get products list

### Documentation

- OpenAPI Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🤖 Agent Workflow

1. **User Query** → Product name or question
2. **Analysis Agent** → Calls RAG tool to retrieve product data
   - Detects allergens
   - Assesses risk level (low/medium/high)
   - Calculates ethical score (0-100)
3. **Recommendation Agent** → Uses analysis results
   - Suggests safer alternatives
   - Provides actionable advice
   - Generates final report
4. **Response** → Structured output with both agents' work

---

## 📊 Data Structure

Products are stored in `data/metadata.json` with the following fields:

```json
{
  "id": "0",
  "name": "Product Name",
  "category": "Category",
  "brand": "Brand Name",
  "description": "Product description",
  "ingredients": "ingredient1, ingredient2",
  "allergen_warnings": "allergen1, allergen2",
  "ethical_notes": "Ethical concerns or positives",
  "recommendations": "alternative1, alternative2"
}
```

---

## 🎨 Frontend Features

- **Product Browser**: Searchable sidebar with all products
- **Mode Toggle**: Switch between Agentic AI and Basic RAG
- **Chat Interface**: Natural conversation flow
- **Agent Indicators**: Shows which agents processed the request
- **Detailed Reports**: Expandable full analysis reports

---

## 🔧 Configuration

### Environment Variables (Optional)

Create `.env` file in backend directory:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Model Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 📈 Performance

- **RAG Search**: ~50-100ms per query
- **Agent Workflow**: 2-5 seconds (depends on complexity)
- **Embedding Generation**: One-time on startup
- **Product Database**: 20 products (easily scalable)

---

## 🧪 Testing

### Test Backend

```bash
# Health check
curl http://localhost:8000/api/v2/health

# Test analysis
curl -X POST http://localhost:8000/api/v2/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Oreo Cookies"}'
```

### Test MCP Server

```bash
cd backend/mcp
python server.py
```

---

## 📝 Project Structure

```
agentic-allerpredict/
├── backend/
│   ├── agents/
│   │   ├── analysis_agent.py      # Product Safety Analyst
│   │   ├── recommendation_agent.py # Recommendation Specialist
│   │   └── crew.py                # CrewAI workflow orchestration
│   ├── mcp/
│   │   ├── tool.py                # MCP tool wrapper
│   │   └── server.py              # FastMCP server
│   ├── rag/
│   │   └── rag_engine.py          # RAG implementation
│   ├── main.py                    # FastAPI application
│   └── requirements.txt           # Python dependencies
├── frontend/
│   └── react-app/
│       ├── src/
│       │   ├── App.jsx            # Main React component
│       │   └── styles.css         # Styling
│       └── package.json           # Node dependencies
├── data/
│   └── metadata.json              # Product database
├── docs/
│   ├── architecture.md            # Architecture details
│   └── limitations.md             # Known limitations
├── diagrams/
│   └── architecture.txt           # System diagrams
└── README.md                      # This file
```

---

## 👥 Contributors

Developed as an academic project demonstrating:
- Agentic AI systems
- RAG architectures
- MCP server implementation
- Multi-agent coordination

---

## 📄 License

This is an academic project. All rights reserved.

---

## 🆘 Support

For issues or questions:
1. Check the documentation in `/docs`
2. Review the architecture diagram
3. Check API docs at `/docs` endpoint
4. See limitations in `docs/limitations.md`

---

**Version**: 2.0.0  
**Last Updated**: January 2026