# 🤖 WhatsApp AI Ordering Assistant for Ramadan Juice

## 📌 Overview

A WhatsApp-based AI ordering assistant built with FastAPI, Twilio, LangGraph, SQLAlchemy, and OpenAI-compatible LLMs.

The assistant allows customers to browse the menu, place orders through WhatsApp, manage their cart, and confirm orders. Confirmed orders are stored in a database and can be viewed through API endpoints.

---

## 🌐 Demo

The application is deployed on Render and integrated with Twilio WhatsApp Sandbox.

Due to API usage costs and sandbox restrictions, the live endpoint is not publicly exposed.
Screenshots demonstrating the workflow will be provided below.

## ✨ Features

### 👤 Customer Features

* 📋 Access the full menu through the menu link
* 🍹 View menu items and prices
* 🤖 AI-powered menu recommendations
* 🛒 Create orders through WhatsApp
* ➕ Add multiple items to cart
* 📝 Add order notes and customizations
* 📦 View cart contents
* ✅ Confirm orders
* ❌ Cancel orders

### 🏪 Business Features

* 👥 Store customer information
* 💾 Persist confirmed orders
* 📊 Retrieve orders through API endpoints
* 🌱 Seed menu data automatically

---

## 🛠️ Technologies Used

### Backend

* ⚡ FastAPI
* 🐍 Python
* 🗄️ SQLAlchemy

### AI & Agent Framework

* 🧠 LangGraph
* ✨ OpenAI GPT-4o Mini Support
* 🧩 AI Intent Classification
* 🌍 Multilingual Support (English, Arabic, Arabizi)

### Messaging

* 💬 Twilio WhatsApp Sandbox

### Database

* 🗃️ SQLite (Development)
* 🐘 PostgreSQL (Production)

### Deployment

* ☁️ Render Web Service
* 🐘 Render PostgreSQL
* 🌐 ngrok (Local Development)

---

## 📂 Project Structure

```text
app/
│
├── graph/
│   ├── order_graph.py
│   └── chat_router_graph.py
│
├── services/
│   ├── ai_assistant_service.py
│   ├── order_extraction_service.py
│   ├── openai_service.py
│   ├── intent_service.py
│   ├── menu_service.py
│   └── search_service.py
│
├── database.py
├── main.py
├── models.py
└── seed.py
```

---

## 🏗️ Architecture

```text
WhatsApp User
      │
      ▼
Twilio WhatsApp
      │
      ▼
FastAPI Webhook
      │
      ▼
LangGraph Order Flow
      │
 ┌────┴──────────────┐
 ▼                   ▼
OpenAI GPT-4o Mini   PostgreSQL
AI Assistant         Database
      │                   │
      └───────▼───────────┘
        WhatsApp Reply
```

---

## 🔄 LangGraph Workflow

```text
START
  │
  ▼
🛒 Start Order
  │
  ▼
🍹 Choose Item
  │
  ▼
📏 Choose Size
  │
  ▼
🔢 Choose Quantity
  │
  ▼
➕ Add To Cart
  │
  ▼
END
```

---

## 🚀 API Endpoints

### 💬 WhatsApp Webhook

```http
POST /whatsapp
```

### 📦 Orders

```http
GET /orders
```

---
📁 Sample Data

The project expects menu/category/prices data files inside the data/ directory.

---

## ⚙️ Installation

### 📥 Clone Repository

```bash
git clone <repository-url>
cd whatsapp_ai_agent
```

### 🐍 Create Virtual Environment

```bash
python -m venv .venv
```

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔐 Configure Environment Variables

```env
OPENAI_API_KEY=your_key
DATABASE_URL=external_Database_URL
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token

```
**Note:**
- For local development, you may use SQLite or the Render External Database URL.
- In Render Web Services, use the Render Internal Database URL.
- Use the Render External Database URL when connecting from your laptop or running Alembic migrations locally.

### 🌱 Seed Database

```bash
python -m app.seed
```

### ▶️ Run Application

```bash
uvicorn app.main:app --reload
```

---

## 📱 Example Conversation

```text
Customer: ORDER

Bot: What would you like to order?

Customer: أفوكا

Bot: What size would you like?

Customer: وسط

Bot: How many would you like?

Customer: 2

Bot: Added to cart ✅

Customer: CART

Bot: Displays cart contents

Customer: CONFIRM

Bot: Order confirmed ✅
```

---

## 🔮 Future Improvements

* 🎤 Voice-to-Text using Whisper/OpenAI
* 🔊 Voice-to-Voice WhatsApp Assistant
* 📈 Analytics Dashboard
* 🐘 PostgreSQL-backed LangGraph Memory
* 📊 Admin Dashboard
* 🚚 Order Status Tracking
* 🧾 Menu Management Interface
* 📱 Official WhatsApp Business Number Integration

---

## 👩‍💻 Author

Zahraa Alkerdy

Computer and Communication Engineer

Passionate about Artificial Intelligence, Machine Learning, LLM Applications, and AI Automation Systems.