# دليل البدء السريع - AllerPredict AI

## 🚀 خطوات التشغيل السريع

### الطريقة 1: استخدام سكريبت التشغيل الآلي

```bash
# من المجلد الرئيسي للمشروع
./start.sh
```

هذا السكريبت سيقوم بـ:
- ✅ التحقق من تثبيت Ollama
- ✅ تحميل نموذج Llama 3.2 إن لم يكن موجوداً
- ✅ تثبيت مكتبات Backend
- ✅ تشغيل Backend على المنفذ 8000
- ✅ تثبيت مكتبات Frontend
- ✅ تشغيل Frontend على المنفذ 3000

---

### الطريقة 2: التشغيل اليدوي

#### خطوة 1: تشغيل Backend

```bash
cd backend

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو venv\Scripts\activate  # Windows

# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل الخادم
python main.py
```

#### خطوة 2: تشغيل Frontend (في نافذة طرفية جديدة)

```bash
cd frontend

# تثبيت المكتبات
npm install

# تشغيل التطبيق
npm run dev
```

---

## 📋 اختبار النظام

### 1. اختبار Backend API

افتح المتصفح وانتقل إلى:
```
http://localhost:8000/docs
```

ستجد واجهة Swagger التفاعلية لاختبار جميع الـ APIs.

### 2. اختبار Frontend

افتح المتصفح وانتقل إلى:
```
http://localhost:3000
```

---

## 🎯 كيفية الاستخدام

### تحليل منتج

1. **البحث عن المنتج**:
   - اكتب اسم المنتج في شريط البحث
   - اختر المنتج من القائمة

2. **إضافة الحساسية (اختياري)**:
   - أضف المواد التي تعاني من حساسية تجاهها
   - مثال: peanuts, dairy, gluten

3. **اختيار نوع التحليل**:
   - ✅ تحليل سريع (3-5 ثواني)
   - ✅ تحليل مفصل (15-30 ثانية) - يستخدم جميع الوكلاء الأربعة

4. **اضغط "Analyze with AI"**

5. **استعرض النتائج**:
   - تحليل الأعراض
   - توقع المواد المسببة للحساسية
   - تقييم المخاطر
   - نصائح طبية
   - بدائل آمنة

---

## 🔧 استخدام MCP Server

### تشغيل MCP Server

```bash
cd backend/mcp
python server.py
```

### الأدوات المتاحة

1. **analyze_product**: تحليل منتج كامل
2. **find_alternatives**: البحث عن بدائل آمنة
3. **get_product_info**: الحصول على معلومات منتج

### استخدام مع Claude Desktop

أضف إلى ملف الإعدادات:

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

## 📊 مثال عملي

### السيناريو: شخص لديه حساسية من الفول السوداني

```javascript
// طلب API
POST /analyze
{
  "query": "Peanut Butter Cookies",
  "user_allergies": ["peanuts"],
  "detailed_analysis": true
}

// النتيجة المتوقعة
{
  "product": {
    "name": "Peanut Butter Cookies",
    "allergens": ["peanuts", "eggs", "gluten", "dairy"]
  },
  "analysis": {
    "symptom_analysis": "...",
    "allergen_prediction": "...",
    "risk_assessment": "HIGH RISK - Contains peanuts",
    "medical_advice": "AVOID - Severe allergic reaction possible"
  },
  "alternatives": [
    {
      "name": "Rice Cakes",
      "allergens": [],
      "ethical_score": 8.0
    }
  ]
}
```

---

## 🐛 استكشاف الأخطاء

### مشكلة: Backend لا يعمل

**الحل**:
```bash
# تحقق من تثبيت Python
python --version

# تحقق من المكتبات
pip list | grep fastapi

# أعد تثبيت المكتبات
pip install -r requirements.txt --force-reinstall
```

### مشكلة: Frontend لا يعمل

**الحل**:
```bash
# احذف node_modules وأعد التثبيت
rm -rf node_modules package-lock.json
npm install

# جرب منفذ مختلف
npm run dev -- --port 3001
```

### مشكلة: Ollama لا يستجيب

**الحل**:
```bash
# تحقق من تشغيل Ollama
ollama list

# أعد تشغيل Ollama
ollama serve

# تحقق من تحميل النموذج
ollama pull llama3.2
```

---

## 📝 ملاحظات مهمة

1. **الأداء**:
   - التحليل السريع: مناسب للاستخدام العادي
   - التحليل المفصل: مناسب للحالات الحرجة

2. **الخصوصية**:
   - جميع البيانات تتم معالجتها محلياً
   - لا يتم إرسال بيانات لخوادم خارجية

3. **الدقة**:
   - النظام تعليمي وليس بديلاً عن الاستشارة الطبية
   - استشر طبيباً متخصصاً للحالات الخطيرة

---

## 🎓 للمزيد من المعلومات

راجع الملفات التالية:
- `README.md` - توثيق شامل
- `PROJECT_TRACKING.md` - متابعة المتطلبات
- `backend/agents/` - شرح الوكلاء
- `docs/` - مستندات إضافية

---

**استمتع باستخدام AllerPredict AI! 🚀**
