# 🤖 WhatsApp AI Ordering Assistant for Ramadan Juice

## 📌 Overview

A WhatsApp-based AI ordering assistant built with FastAPI, Twilio, LangGraph, SQLAlchemy, and Groq/OpenAI-compatible LLMs.

The assistant allows customers to browse the menu, place orders through WhatsApp, manage their cart, and confirm orders. Confirmed orders are stored in a database and can be viewed through API endpoints.

---

## 🌐 Demo

The application is deployed on Render and integrated with Twilio WhatsApp Sandbox.

Due to API usage costs and sandbox restrictions, the live endpoint is not publicly exposed.
Screenshots demonstrating the workflow will be provided below.

## ✨ Features

### 👤 Customer Features

* 📋 Browse menu categories
* 🍹 View menu items and prices
* 🤖 AI-powered menu recommendations
* 🛒 Create orders through WhatsApp
* ➕ Add multiple items to cart
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
* 🤖 Groq API
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
│   ├── groq_service.py
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
   Twilio
      │
      ▼
 FastAPI Webhook
      │
      ▼
   LangGraph
      │
 ┌────┴──────────────┐
 ▼                   ▼
AI               Database
(Groq/Openai)  (PostgreSQL)
              │
              ▼
           Whatsapp Reply
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

For privacy reasons, the actual business data is not included in this repository.

A sample file (categories.example.json) is provided to demonstrate the expected structure.

You may create your own .json files based on the example data.

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
GROQ_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
DATABASE_URL=sqlite:///./ramadan_juice.db
```

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