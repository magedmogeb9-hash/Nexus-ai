# ⚡ AIForge — منصة صياغة وتدريب الذكاء الاصطناعي

منصة متكاملة لتدريب وتطوير نماذج الذكاء الاصطناعي مع دفع إلكتروني ورفع تلقائي لـ GitHub.

## الميزات

- ✅ تدريب جميع نماذج الذكاء الاصطناعي (LLMs، رؤية، صوت، تضمين)
- ✅ طرق تدريب متقدمة: SFT، LoRA، QLoRA، DPO، RL
- ✅ واجهة مستخدم احترافية ومتجاوبة مع الهاتف
- ✅ دفع إلكتروني: Stripe, PayPal, Paddle
- ✅ رفع تلقائي للمشاريع إلى GitHub
- ✅ دعم Hugging Face, Unsloth, Oumi

## التثبيت السريع

```bash
git clone https://github.com/YOUR_USERNAME/AIForge.git
cd AIForge
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# عدّل .env بمفاتيحك
python app.py
```

افتح: `http://localhost:5000`  
Admin: `admin@example.com` / `admin123`

## Docker

```bash
docker-compose up -d
```

## هيكل المشروع

```
AIForge/
├── app.py              # نقطة الدخول الرئيسية
├── models.py           # نماذج قاعدة البيانات
├── auth.py             # المصادقة والتسجيل
├── payments.py         # بوابات الدفع
├── github_integration.py  # رفع إلى GitHub
├── training_engine.py  # محرك التدريب
├── admin.py            # لوحة الإدارة
├── api.py              # REST API
├── utils/              # أدوات مساعدة
├── templates/          # واجهات HTML
└── static/             # CSS & JS
```

## المتطلبات

- Python 3.10+
- المفاتيح في `.env` (Stripe, PayPal, GitHub, HuggingFace)

## الترخيص

MIT License
