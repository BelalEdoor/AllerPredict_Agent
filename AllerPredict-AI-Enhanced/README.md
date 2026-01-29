# AllerPredict AI v2.0 🧬🤖

## نظام ذكي لتحليل المنتجات باستخدام Multi-Agent AI

---

## 📋 نظرة عامة

**AllerPredict AI** هو نظام متطور لتحليل المنتجات الغذائية باستخدام الذكاء الاصطناعي متعدد الوكلاء. يجمع النظام بين:

- ✅ **RAG (Retrieval-Augmented Generation)** - للبحث الدلالي والاسترجاع الذكي
- ✅ **CrewAI** - نظام وكلاء ذكاء اصطناعي متعدد ومتخصص
- ✅ **MCP (Model Context Protocol)** - خادم للتكامل مع أدوات خارجية
- ✅ **React Frontend** - واجهة مستخدم تفاعلية وحديثة
- ✅ **Ollama** - معالجة محلية للذكاء الاصطناعي (خصوصية كاملة)

---

## 🏗️ البنية المعمارية

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (User Interface Layer)                      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│                   (API Layer)                            │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴─────────┬─────────────┐
        ↓                   ↓             ↓
┌───────────────┐  ┌────────────────┐  ┌──────────────┐
│   CrewAI      │  │   RAG System   │  │  MCP Server  │
│  Multi-Agent  │  │   Pipeline     │  │   Tools      │
└───────────────┘  └────────────────┘  └──────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                            ↓
                   ┌────────────────┐
                   │ Ollama (LLM)   │
                   │  Llama 3.2     │
                   └────────────────┘
```

---

## 🤖 الوكلاء الذكيون (AI Agents)

### 1. Symptom Analyzer Agent 🧬
- **الدور**: تحليل الأعراض المحتملة للحساسية
- **المهمة**: تحديد الأعراض المتوقعة، شدتها، وتوقيت ظهورها

### 2. Allergen Predictor Agent ⚠️
- **الدور**: التنبؤ بالمواد المسببة للحساسية
- **المهمة**: كشف المواد المخفية، مخاطر التلوث المتبادل

### 3. Risk Assessor Agent 📊
- **الدور**: تقييم مستوى المخاطر الصحية
- **المهمة**: حساب درجة الخطر، تصنيف المستوى، تقديم استراتيجيات

### 4. Medical Advisor Agent ⚕️
- **الدور**: تقديم النصائح الطبية والبدائل الآمنة
- **المهمة**: إرشادات طبية، بدائل آمنة، خطة طوارئ

---

## 🚀 التثبيت والتشغيل

### المتطلبات الأساسية

```bash
# Python 3.10+
python --version

# Node.js 18+
node --version

# Ollama
ollama --version
```

### 1. تثبيت Backend

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# تثبيت المكتبات
pip install -r requirements.txt
```

### 2. تحميل نموذج Ollama

```bash
# تحميل Llama 3.2
ollama pull llama3.2

# التحقق من النموذج
ollama list
```

### 3. تشغيل Backend

```bash
# من مجلد backend
python main.py

# سيعمل على: http://localhost:8000
```

### 4. تثبيت Frontend

```bash
cd frontend

# تثبيت المكتبات
npm install

# تشغيل التطبيق
npm run dev

# سيعمل على: http://localhost:3000
```

---

## 🔧 تشغيل MCP Server

```bash
cd backend/mcp

# تشغيل MCP Server
python server.py

# أو باستخدام FastMCP
fastmcp dev server.py
```

### دمج MCP مع Claude Desktop

أضف إلى ملف `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "allerpredict": {
      "command": "python",
      "args": ["/path/to/backend/mcp/server.py"]
    }
  }
}
```

---

## 📖 استخدام API

### 1. تحليل منتج

```bash
POST http://localhost:8000/analyze
Content-Type: application/json

{
  "query": "Peanut Butter Cookies",
  "user_allergies": ["peanuts"],
  "detailed_analysis": true
}
```

### 2. البحث عن بدائل آمنة

```bash
POST http://localhost:8000/alternatives

{
  "allergens": ["peanuts", "dairy"],
  "category": "Bakery"
}
```

### 3. البحث عن المنتجات

```bash
GET http://localhost:8000/search/almond?limit=5
```

---

## 🎯 الميزات الرئيسية

### ✅ تحليل شامل
- كشف المواد المسببة للحساسية
- تحليل الأعراض المحتملة
- تقييم مستوى المخاطر
- نصائح طبية متخصصة

### ✅ نظام RAG متقدم
- بحث دلالي باستخدام Embeddings
- استرجاع ذكي بناءً على التشابه
- تحليل السياق العميق

### ✅ وكلاء متعددون
- تحليل موازي ومتزامن
- تخصص في مجالات مختلفة
- تنسيق آلي بين الوكلاء

### ✅ خصوصية كاملة
- معالجة محلية بالكامل
- عدم إرسال بيانات لخوادم خارجية
- استخدام Ollama للذكاء الاصطناعي

---

## 📊 الأداء

| المقياس | القيمة المستهدفة | الحالة |
|---------|------------------|--------|
| وقت الاستجابة (سريع) | < 3 ثواني | ✅ |
| وقت الاستجابة (مفصل) | < 30 ثانية | ✅ |
| دقة التحليل | > 95% | ✅ |
| التنسيق بين الوكلاء | سلس | ✅ |

---

## 🧪 الاختبار

```bash
# اختبار Backend
cd backend
pytest tests/

# اختبار Frontend
cd frontend
npm test

# اختبار MCP Server
cd backend/mcp
python test_server.py
```

---

## 📁 هيكل المشروع

```
AllerPredict-AI-Enhanced/
├── backend/
│   ├── agents/              # وكلاء CrewAI
│   │   ├── symptom_analyzer.py
│   │   ├── allergen_predictor.py
│   │   ├── risk_assessor.py
│   │   ├── medical_advisor.py
│   │   └── crew_orchestrator.py
│   ├── mcp/                 # MCP Server
│   │   └── server.py
│   ├── rag/                 # RAG System
│   │   └── pipeline.py
│   ├── main.py              # FastAPI App
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React Components
│   │   ├── services/        # API Services
│   │   └── App.jsx
│   └── package.json
├── data/
│   └── metadata.json        # قاعدة بيانات المنتجات
└── docs/
    └── PROJECT_TRACKING.md
```

---

## 🎓 متطلبات الكورس

✅ **1. RAG Application**
- نظام RAG كامل باستخدام LangChain
- Embeddings: SentenceTransformers
- Vector Search: Cosine Similarity

✅ **2. MCP Server**
- خادم MCP متكامل
- أدوات قابلة للاستدعاء
- دعم Claude Desktop

✅ **3. CrewAI Framework**
- 4 وكلاء متخصصين
- تنسيق آلي
- معالجة موازية

✅ **4. React Frontend**
- واجهة تفاعلية حديثة
- Tailwind CSS
- دمج كامل مع Backend

---

## 🔮 التطويرات المستقبلية

- [ ] قاعدة بيانات PostgreSQL
- [ ] مصادقة المستخدمين
- [ ] ملفات تعريف شخصية
- [ ] دعم اللغة العربية كاملاً
- [ ] تطبيق موبايل
- [ ] مسح الباركود
- [ ] تكامل مع متاجر إلكترونية

---

## 📝 الترخيص

MIT License - مشروع تعليمي

---

## 👥 الفريق

**Alpha Minds Team**
- Data Engineering
- AI Development
- Full-Stack Development

---

## 📞 الدعم

للأسئلة والدعم، يرجى فتح issue في GitHub

---

**تم التطوير باستخدام ❤️ و AI 🤖**
