# AllerPredict AI - API Documentation

## Base URL
```
http://localhost:8000
```

---

## Endpoints

### 1. Health Check

**GET** `/`

الاستجابة:
```json
{
  "status": "active",
  "service": "AllerPredict AI",
  "version": "2.0.0",
  "features": ["RAG", "MCP", "CrewAI", "Multi-Agent Analysis"]
}
```

---

### 2. Detailed Health Check

**GET** `/health`

الاستجابة:
```json
{
  "status": "healthy",
  "rag_loaded": true,
  "agents_initialized": true,
  "models": {
    "embeddings": "all-MiniLM-L6-v2",
    "llm": "llama3.2 (Ollama)"
  }
}
```

---

### 3. Get All Products

**GET** `/products`

الاستجابة:
```json
{
  "products": [
    {
      "id": 1,
      "name": "Peanut Butter Cookies",
      "brand": "Sweet Treats Co.",
      "category": "Bakery",
      "ingredients": ["flour", "sugar", "peanut butter", ...],
      "allergens": ["peanuts", "eggs", "gluten", "dairy"],
      "description": "...",
      "ethical_score": 7.5,
      "company_info": "...",
      "certifications": ["Non-GMO", "Fair Trade"]
    }
  ]
}
```

---

### 4. Analyze Product

**POST** `/analyze`

الطلب:
```json
{
  "query": "Peanut Butter Cookies",
  "user_allergies": ["peanuts"],
  "detailed_analysis": false
}
```

المعاملات:
- `query` (string, required): اسم أو وصف المنتج
- `user_allergies` (array, optional): قائمة الحساسيات
- `detailed_analysis` (boolean, optional): استخدام التحليل المفصل (افتراضي: false)

الاستجابة (تحليل سريع):
```json
{
  "product": {
    "id": 1,
    "name": "Peanut Butter Cookies",
    "brand": "Sweet Treats Co.",
    "category": "Bakery",
    "allergens": ["peanuts", "eggs", "gluten", "dairy"],
    "ethical_score": 7.5,
    "similarity_score": 0.95
  },
  "analysis": "Detailed text analysis from Ollama...",
  "alternatives": [...]
}
```

الاستجابة (تحليل مفصل):
```json
{
  "product": {...},
  "analysis": {
    "symptom_analysis": "...",
    "allergen_prediction": "...",
    "risk_assessment": "...",
    "medical_advice": "..."
  },
  "alternatives": [...],
  "similarity_score": 0.95
}
```

---

### 5. Find Alternatives

**POST** `/alternatives`

الطلب:
```json
{
  "allergens": ["peanuts", "dairy"],
  "category": "Bakery"
}
```

المعاملات:
- `allergens` (array, required): المواد المراد تجنبها
- `category` (string, optional): فئة المنتج

الاستجابة:
```json
{
  "allergens_avoided": ["peanuts", "dairy"],
  "alternatives": [
    {
      "id": 3,
      "name": "Whole Wheat Bread",
      "brand": "Harvest Bakery",
      "category": "Bakery",
      "allergens": ["gluten"],
      "ethical_score": 7.0,
      "description": "..."
    }
  ]
}
```

---

### 6. Search Products

**GET** `/search/{query}`

المعاملات:
- `query` (path, required): نص البحث
- `limit` (query, optional): عدد النتائج (افتراضي: 5)

مثال:
```
GET /search/cookies?limit=3
```

الاستجابة:
```json
{
  "query": "cookies",
  "results": [
    {
      "id": 1,
      "name": "Peanut Butter Cookies",
      "similarity_score": 0.87,
      ...
    }
  ]
}
```

---

### 7. Get Product by ID

**GET** `/product/{product_id}`

المعاملات:
- `product_id` (path, required): معرف المنتج

مثال:
```
GET /product/1
```

الاستجابة:
```json
{
  "id": 1,
  "name": "Peanut Butter Cookies",
  "brand": "Sweet Treats Co.",
  "category": "Bakery",
  "ingredients": [...],
  "allergens": [...],
  "description": "...",
  "ethical_score": 7.5,
  "company_info": "...",
  "certifications": [...]
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Product not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message here"
}
```

---

## Rate Limits

لا توجد حدود حالياً (نظام محلي)

---

## Authentication

غير مطلوب حالياً

---

## CORS

مسموح من:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

---

## Response Times

| Endpoint | متوسط الوقت |
|----------|-------------|
| GET /products | < 100ms |
| POST /analyze (سريع) | 2-5 ثواني |
| POST /analyze (مفصل) | 15-30 ثانية |
| POST /alternatives | < 500ms |
| GET /search | < 300ms |

---

## Example Usage (JavaScript)

```javascript
// Analyze product
const analyzeProduct = async () => {
  const response = await fetch('http://localhost:8000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: 'Almond Milk',
      user_allergies: ['tree nuts'],
      detailed_analysis: true
    })
  });
  
  const data = await response.json();
  console.log(data);
};
```

## Example Usage (Python)

```python
import requests

# Analyze product
response = requests.post('http://localhost:8000/analyze', json={
    'query': 'Greek Yogurt',
    'user_allergies': ['dairy'],
    'detailed_analysis': False
})

data = response.json()
print(data)
```

---

## Interactive Documentation

زر الوثائق التفاعلية (Swagger):
```
http://localhost:8000/docs
```

الوثائق البديلة (ReDoc):
```
http://localhost:8000/redoc
```
