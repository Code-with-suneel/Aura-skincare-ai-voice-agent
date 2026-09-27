import os
import re
import time

from google import genai
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT / GEMINI SETUP
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY nahi mili. backend/.env check karo.")

client = genai.Client(api_key=api_key)


# =========================================================
# AURA SKINCARE - SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are Aria, the AI customer support assistant for Aura Skincare.

PERSONALITY:
- Friendly
- Professional
- Helpful
- Concise
- Natural Indian customer-support style
- Warm and polite

You help customers with:
- Aura Skincare products
- Orders
- Delivery
- Returns
- Cancellation
- Damaged or defective products
- COD
- Shipping
- General brand-related questions

IMPORTANT RULES:

1. Never invent order information.
2. Never invent tracking information.
3. Never invent customer information.
4. Use order information only when it is provided by the system.
5. Always follow Aura Skincare policies.
6. If required information is missing, politely ask the customer for it.
7. Keep answers short because your responses are spoken by a voice assistant.
8. Do not mention Gemini.
9. Speak as Aria from Aura Skincare.
10. Never make promises outside company policy.
11. Reply in the same language used by the customer whenever possible.
12. If the customer speaks Hindi, respond in Hindi.
13. If the customer speaks Hinglish, respond naturally in Hinglish.
14. If the customer speaks English, respond in English.
15. Do not unnecessarily repeat information already given.
16. For follow-up questions, remember the previous conversation.

AURA SKINCARE POLICIES:

SHIPPING:
- Free shipping above ₹499.
- Orders below ₹499 have a ₹50 shipping fee.
- Standard delivery takes 3–5 business days.

RETURNS:
- Returns are accepted within 7 days of delivery.
- Product must be unopened, unused and in original packaging.

DAMAGED / DEFECTIVE:
- Report within 48 hours of delivery.
- Photos are required.
- Eligible cases may receive a replacement.

CANCELLATION:
- Cancellation is allowed only when the order is Processing.
- Shipped or Out for Delivery orders cannot be cancelled.
- Customers may refuse delivery at the doorstep.

COD:
- COD is available up to ₹2,500.
- Payment can be made using cash or UPI at the doorstep.
"""


# =========================================================
# HINDI / HINGLISH FALLBACK
# =========================================================

def get_fallback_response(user_message):
    """
    Gemini unavailable hone par bhi user ko useful response mile.
    Hindi/Hinglish input ke liye Hindi response.
    English input ke liye English response.
    """

    if not user_message:
        return (
            "I'm sorry, I'm having trouble processing that right now. "
            "Could you please try again?"
        )

    text = str(user_message).lower().strip()

    # -----------------------------------------------------
    # PURE HINDI SCRIPT DETECTION
    # -----------------------------------------------------

    if re.search(r"[\u0900-\u097F]", text):

        # Hindi language request
        if (
            "हिंदी" in text
            or "हिन्दी" in text
            or "हिंदी में" in text
            or "हिन्दी में" in text
        ):
            return (
                "जी हाँ, बिल्कुल। मैं आपसे हिंदी में बात कर सकती हूँ। "
                "आप बताइए, Aura Skincare के बारे में आपको क्या जानकारी चाहिए?"
            )

        # Greeting
        if any(word in text for word in [
            "नमस्ते",
            "नमस्कार",
            "हैलो",
            "हाय"
        ]):
            return (
                "नमस्ते! मैं आरिया हूँ, Aura Skincare की AI customer support assistant। "
                "मैं आपकी कैसे मदद कर सकती हूँ?"
            )

        # Help
        if any(word in text for word in [
            "मदद",
            "जानकारी",
            "बताइए",
            "बताओ"
        ]):
            return (
                "जी बिल्कुल। मैं आपकी मदद करने के लिए यहाँ हूँ। "
                "आप अपना सवाल बताइए।"
            )

        return (
            "जी बिल्कुल। मैं आपकी मदद कर सकती हूँ। "
            "कृपया अपना सवाल या ऑर्डर आईडी बताइए।"
        )

    # -----------------------------------------------------
    # HINGLISH DETECTION
    # -----------------------------------------------------

    hindi_words = [
        "hindi",
        "haan",
        "ha",
        "nahi",
        "nahin",
        "mujhe",
        "aap",
        "aapko",
        "mera",
        "meri",
        "mere",
        "kya",
        "kaise",
        "kab",
        "kahan",
        "batao",
        "bataiye",
        "chahiye",
        "hai",
        "hain",
        "kitna",
        "kitne",
        "konsa",
        "kaunsa",
        "kaunsi",
        "order",
        "milega",
        "milega",
        "cancel",
        "karna",
        "kar",
        "karo",
        "delivery",
        "kabtak",
        "kab",
    ]

    hindi_count = sum(
        1 for word in hindi_words
        if re.search(r"\b" + re.escape(word) + r"\b", text)
    )

    if hindi_count >= 1:

        if "hindi" in text:
            return (
                "Ji haan, bilkul. Main aapse Hindi mein baat kar sakti hoon. "
                "Aap batayiye, Aura Skincare ke baare mein aapko kya information chahiye?"
            )

        return (
            "Ji bilkul. Main aapki help kar sakti hoon. "
            "Aap apna question ya order ID bataiye."
        )

    # -----------------------------------------------------
    # ENGLISH FALLBACK
    # -----------------------------------------------------

    return (
        "I'm sorry, I'm having trouble processing that right now. "
        "Could you please try again?"
    )


# =========================================================
# GEMINI AI FUNCTION
# =========================================================

def ask_gemini(user_message, conversation=None):

    if conversation is None:
        conversation = []

    # Last 12 messages only
    recent_conversation = conversation[-12:]

    conversation_text = ""

    for item in recent_conversation:

        if not isinstance(item, dict):
            continue

        speaker = item.get("speaker", "")
        message = item.get("message", "")

        if not message:
            continue

        if speaker == "Aria":
            conversation_text += f"Aria: {message}\n"
        else:
            conversation_text += f"Customer: {message}\n"

    prompt = f"""
Previous conversation:

{conversation_text}

Use the previous conversation to understand the customer's context.

If the customer asks a follow-up question, use the previous
conversation naturally instead of asking for information again
when it is already available.

Latest customer message:

Customer: {user_message}

Respond naturally as Aria from Aura Skincare.

LANGUAGE RULE:

- If the customer speaks English, answer in English.
- If the customer speaks Hindi, answer in Hindi.
- If the customer speaks Hinglish, answer naturally in Hinglish.
- Do not unnecessarily switch to English.
- Keep the response short and suitable for voice conversation.

IMPORTANT:

- Never invent order information.
- Never invent tracking information.
- Follow Aura Skincare policies.
- Do not mention Gemini.
"""


    # =====================================================
    # GEMINI MODELS
    # =====================================================

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-2.5-flash",
    ]

    last_error = None


    # =====================================================
    # TRY GEMINI
    # =====================================================

    for model_name in models_to_try:

        try:

            print(f"Trying Gemini model: {model_name}")

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    SYSTEM_PROMPT,
                    prompt
                ]
            )

            if response and response.text:

                print(
                    f"Gemini response received from: {model_name}"
                )

                return response.text.strip()

        except Exception as error:

            last_error = error

            print(
                f"Gemini Error with {model_name}: {error}"
            )

            error_text = str(error)

            # Temporary server / availability error
            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                print(
                    f"{model_name} temporarily unavailable. "
                    "Trying next model..."
                )

                time.sleep(1)

                continue

            # Other error
            print(
                "Gemini request failed. "
                "Using local fallback response."
            )

            break


    # =====================================================
    # GEMINI FAILED
    # USE LANGUAGE-AWARE FALLBACK
    # =====================================================

    print(
        "All Gemini models failed."
        f" Last error: {last_error}"
    )

    return get_fallback_response(user_message)