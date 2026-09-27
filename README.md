# Aura Skincare AI Voice Agent

An AI-powered voice customer support assistant for Aura Skincare. The assistant, named **Aria**, helps customers with order tracking, shipping, returns, cancellations, and other customer support queries through voice and text.

## Project Overview

Aura Skincare AI Voice Agent is a browser-based customer support application designed to provide a natural and user-friendly customer service experience.

Customers can start a voice call with Aria, ask questions using their microphone or text input, and receive spoken or written responses. The application supports English, Hindi, and Hinglish.

## Features

* **AI Voice Assistant:** Talk to Aria using your microphone.
* **Text Chat:** Type questions and receive responses.
* **Multilingual Support:** English, Hindi, and Hinglish.
* **Order Tracking:** Retrieve order details using an order ID.
* **Customer Support:** Get information about shipping, returns, cancellations, and damaged products.
* **Voice Status:** See whether Aria is listening, thinking, or speaking.
* **Conversation Transcript:** Review the conversation after the call.
* **Call Summary:** View a structured JSON summary of the call.
* **Responsive Design:** Use the application on desktop and mobile devices.
* **Graceful Error Handling:** Handles unclear speech and invalid order IDs.

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Web Speech API (Speech Recognition and Speech Synthesis)

### Backend

* Python
* Django
* Django REST Framework
* Google Gemini API

## Project Structure

```text
Aura-skincare-ai-voice-agent/
│
├── aura_backend/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── support/
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── ai_service.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── tools.py
│   ├── urls.py
│   └── views.py
│
├── .env.example
├── .gitignore
├── index.html
├── manage.py
├── requirements.txt
├── script.js
└── style.css
```

## Sample Orders

The application includes three sample orders for testing.

| Order ID | Customer     | Product                     | Amount | Status           |
| -------- | ------------ | --------------------------- | -----: | ---------------- |
| ORD-101  | Priya Sharma | Vitamin C Serum (30ml)      |   ₹699 | Out for Delivery |
| ORD-102  | Rahul Verma  | Hydrating Sunscreen SPF 50  |   ₹499 | Delivered        |
| ORD-103  | Ananya Patel | Green Tea Face Wash + Toner |   ₹850 | Processing       |

## Customer Support Policies

The assistant follows these sample business policies:

* **Shipping:** Free shipping on orders above ₹499. Orders below ₹499 have a ₹50 shipping fee.
* **Delivery:** Standard delivery takes 3–5 business days.
* **Returns:** Customers can request a return within 7 days of delivery if the product is unopened, unused, and in its original packaging.
* **Damaged Products:** Customers must report damaged or defective products within 48 hours and provide photos to request a replacement.
* **Cancellation:** Orders can be cancelled only while they are in Processing status. Shipped or Out for Delivery orders cannot be cancelled. Customers may refuse delivery at the doorstep.
* **Cash on Delivery:** COD is available for orders up to ₹2,500. Customers can pay by cash or UPI at the doorstep.

## Local Setup

### Prerequisites

* Python 3.10 or later
* pip
* A modern browser with microphone access
* A Google Gemini API key for AI-powered fallback responses

### 1. Clone the Repository

```bash
git clone https://github.com/Code-with-suneel/Aura-skincare-ai-voice-agent.git
cd Aura-skincare-ai-voice-agent
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own API key. Never commit your real API key to GitHub.

### 4. Start the Django Backend

From the project root, run:

```bash
python manage.py runserver
```

The backend will be available at:

```text
http://127.0.0.1:8000/
```

The chat API endpoint is:

```text
http://127.0.0.1:8000/api/chat/
```

### 5. Start the Frontend

Open a second terminal in the project root and run:

```bash
python -m http.server 5500
```

Open the application in your browser:

```text
http://127.0.0.1:5500/
```

Allow microphone access when prompted to use voice features.

## Testing

Try the following example questions:

| Customer Question              | Expected Behavior                                                      |
| ------------------------------ | ---------------------------------------------------------------------- |
| Where is my order ORD-101?     | Provides the order status and tracking details.                        |
| What is the status of ORD-102? | Provides the delivered status.                                         |
| Can I cancel ORD-103?          | Explains that the order is eligible for cancellation while processing. |
| What is your return policy?    | Explains the 7-day return policy.                                      |
| Do you offer cash on delivery? | Explains COD availability and payment methods.                         |
| I want to check my order.      | Asks the customer for an order ID.                                     |

## How to Use

1. Open the application in a supported browser.
2. Click **Start Call**.
3. Allow microphone access.
4. Speak naturally to Aria or use the text chat.
5. Ask about orders, shipping, returns, or other support topics.
6. Click **End Call** to finish the conversation.
7. Review the conversation transcript and JSON summary.

## API

### Chat Endpoint

**POST** `/api/chat/`

The API accepts a customer message, conversation history, and language preference.

Example request:

```json
{
  "message": "Where is my order ORD-101?",
  "conversation": [],
  "language": "en-IN"
}
```

The API returns a response from the support assistant, along with relevant conversation information.

## Notes and Limitations

* Voice recognition and speech synthesis depend on browser support and available system voices.
* Microphone permission is required for voice conversations.
* The included orders are sample data for demonstration purposes.
* Gemini is used for general questions that are not handled by the built-in order and policy responses.
* The Gemini API key must be configured separately.

## Author

**Suneel Kumar**

GitHub: [Code-with-suneel](https://github.com/Code-with-suneel)
