import re
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .tools import get_order_details
from .ai_service import ask_gemini


# =========================================================
# CONFIG
# =========================================================

VALID_ORDER_NUMBERS = {"101", "102", "103"}


# =========================================================
# DEVANAGARI DIGITS
# =========================================================

DEVANAGARI_DIGITS = {
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
}


def normalize_devanagari_digits(text):
    if not text:
        return ""

    text = str(text)

    for hindi_digit, english_digit in DEVANAGARI_DIGITS.items():
        text = text.replace(hindi_digit, english_digit)

    return text


# =========================================================
# NUMBER WORDS
# =========================================================

HINDI_NUMBERS = {
    "शून्य": 0,
    "जीरो": 0,
    "एक": 1,
    "दो": 2,
    "तीन": 3,
    "चार": 4,
    "पाँच": 5,
    "पांच": 5,
    "छह": 6,
    "छः": 6,
    "सात": 7,
    "आठ": 8,
    "नौ": 9,
    "दस": 10,
    "ग्यारह": 11,
    "बारह": 12,
    "तेरह": 13,
    "चौदह": 14,
    "पंद्रह": 15,
    "सोलह": 16,
    "सत्रह": 17,
    "अठारह": 18,
    "उन्नीस": 19,
    "बीस": 20,
    "तीस": 30,
    "चालीस": 40,
    "पचास": 50,
    "साठ": 60,
    "सत्तर": 70,
    "अस्सी": 80,
    "नब्बे": 90,
    "सौ": 100,
}


ENGLISH_NUMBERS = {
    "zero": 0,
    "oh": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
}


# =========================================================
# WORDS TO NUMBER
# =========================================================

def words_to_number(text):
    if not text:
        return None

    text = str(text).lower().strip()
    text = normalize_devanagari_digits(text)

    if text.isdigit():
        number = int(text)

        if 1 <= number <= 999:
            return number

        return None

    # Hindi
    hindi_tokens = text.split()

    if any(token in HINDI_NUMBERS for token in hindi_tokens):
        total = 0
        current = 0

        for token in hindi_tokens:
            if token not in HINDI_NUMBERS:
                continue

            value = HINDI_NUMBERS[token]

            if value == 100:
                if current == 0:
                    current = 1

                total += current * 100
                current = 0
            else:
                current += value

        total += current

        if 1 <= total <= 999:
            return total

    # English
    english_tokens = text.split()

    if any(token in ENGLISH_NUMBERS for token in english_tokens):
        total = 0
        current = 0

        for token in english_tokens:
            if token not in ENGLISH_NUMBERS:
                continue

            value = ENGLISH_NUMBERS[token]

            if value == 100:
                if current == 0:
                    current = 1

                total += current * 100
                current = 0
            else:
                current += value

        total += current

        if 1 <= total <= 999:
            return total

    return None


# =========================================================
# FIND ORDER ID
# =========================================================

def find_order_id(text):
    if not text:
        return None

    original_text = str(text).strip()

    text = normalize_devanagari_digits(
        original_text.lower()
    )

    # ORD-101
    # ORD 101
    # ORD101
    # ORDER-101
    # ORDER 101

    patterns = [
        r"\bord[-\s]?(\d{3})\b",
        r"\border[-\s]?(\d{3})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            number = match.group(1)

            if number in VALID_ORDER_NUMBERS:
                return f"ORD-{number}"

    # Hindi ORD
    hindi_ord_patterns = [
        r"ओ\s*आर\s*डी",
        r"ओआरडी",
        r"ओ\.?\s*आर\.?\s*डी",
        r"ओ\s*आरडी",
        r"ओआर\s*डी",
    ]

    has_hindi_ord = any(
        re.search(
            pattern,
            original_text,
            re.IGNORECASE
        )
        for pattern in hindi_ord_patterns
    )

    if has_hindi_ord:
        match = re.search(
            r"\b(101|102|103)\b",
            text
        )

        if match:
            return f"ORD-{match.group(1)}"

    # Direct number
    match = re.search(
        r"\b(101|102|103)\b",
        text
    )

    if match:
        return f"ORD-{match.group(1)}"

    # Spoken Hindi order numbers
    hindi_order_patterns = {
        101: [
            "एक सौ एक",
            "सौ एक",
            "एक शून्य एक",
            "एक जीरो एक",
        ],
        102: [
            "एक सौ दो",
            "सौ दो",
            "एक शून्य दो",
            "एक जीरो दो",
        ],
        103: [
            "एक सौ तीन",
            "सौ तीन",
            "एक शून्य तीन",
            "एक जीरो तीन",
        ],
    }

    for number, patterns_list in hindi_order_patterns.items():
        for pattern in patterns_list:
            if pattern in original_text:
                return f"ORD-{number}"

    # Spoken English order numbers
    english_order_patterns = {
        101: [
            "one hundred one",
            "one hundred and one",
            "hundred one",
            "one zero one",
            "one oh one",
        ],
        102: [
            "one hundred two",
            "one hundred and two",
            "hundred two",
            "one zero two",
            "one oh two",
        ],
        103: [
            "one hundred three",
            "one hundred and three",
            "hundred three",
            "one zero three",
            "one oh three",
        ],
    }

    for number, patterns_list in english_order_patterns.items():
        for pattern in patterns_list:
            if pattern in text:
                return f"ORD-{number}"

    return None


# =========================================================
# ONLY ORDER ID?
# =========================================================

def is_only_order_id(user_message, order_id):
    if not user_message or not order_id:
        return False

    text = str(user_message).strip().lower()

    text = normalize_devanagari_digits(text)

    text = re.sub(
        r"[.,!?।]+$",
        "",
        text
    ).strip()

    number = order_id.split("-")[1]

    # Polite words remove
    text = re.sub(
        r"\b(please|pls|ji|haan|han|ha)\b",
        "",
        text
    ).strip()

    # Direct number
    if text == number:
        return True

    # ORD-101
    if re.fullmatch(
        rf"ord[-\s]?{number}",
        text
    ):
        return True

    # ORDER 101
    if re.fullmatch(
        rf"order[-\s]?{number}",
        text
    ):
        return True

    extra_patterns = [
        rf"order\s+number\s+{number}",
        rf"order\s+no\.?\s+{number}",
        rf"order\s+id\s+{number}",
        rf"order\s*#\s*{number}",
    ]

    for pattern in extra_patterns:
        if re.fullmatch(pattern, text):
            return True

    # Spoken English
    spoken_orders = {
        "101": [
            "one zero one",
            "one oh one",
            "one hundred one",
            "one hundred and one",
            "hundred one",
        ],
        "102": [
            "one zero two",
            "one oh two",
            "one hundred two",
            "one hundred and two",
            "hundred two",
        ],
        "103": [
            "one zero three",
            "one oh three",
            "one hundred three",
            "one hundred and three",
            "hundred three",
        ],
    }

    if text in spoken_orders.get(number, []):
        return True

    # Spoken Hindi
    hindi_orders = {
        "101": [
            "एक शून्य एक",
            "एक जीरो एक",
            "एक सौ एक",
            "सौ एक",
        ],
        "102": [
            "एक शून्य दो",
            "एक जीरो दो",
            "एक सौ दो",
            "सौ दो",
        ],
        "103": [
            "एक शून्य तीन",
            "एक जीरो तीन",
            "एक सौ तीन",
            "सौ तीन",
        ],
    }

    if text in hindi_orders.get(number, []):
        return True

    return False


# =========================================================
# FIND LAST ORDER FROM CONVERSATION
# =========================================================

def find_last_order_id(conversation):
    if not conversation:
        return None

    for item in reversed(conversation):

        if not isinstance(item, dict):
            continue

        speaker = str(
            item.get("speaker", "")
        ).lower().strip()

        allowed_speakers = [
            "",
            "user",
            "customer",
            "human",
            "you",
        ]

        if speaker not in allowed_speakers:
            continue

        message = item.get(
            "message",
            ""
        )

        order_id = find_order_id(message)

        if order_id:
            return order_id

    return None


# =========================================================
# LANGUAGE DETECTION
# =========================================================

def detect_language(text):

    if not text:
        return "english"

    text = str(text).strip()

    # Hindi script
    if re.search(
        r"[\u0900-\u097F]",
        text
    ):
        return "hindi"

    lower_text = text.lower()

    hinglish_words = [
        "mera",
        "meri",
        "mere",
        "mujhe",
        "aap",
        "aapka",
        "aapki",
        "aapke",
        "kya",
        "kaise",
        "kab",
        "kahan",
        "kaha",
        "batao",
        "bataiye",
        "karna",
        "kar sakte",
        "milega",
        "chahiye",
        "naam",
        "kis",
        "kiske",
        "mein",
        "me",
        "pe",
        "par",
        "kitna",
        "kitne",
        "kaunsa",
        "konsa",
        "maine",
        "kiya",
        "hai",
        "hain",
        "ho",
        "raha",
        "rahi",
        "sakta",
        "sakti",
        "cancel kar",
        "order ka",
        "order ki",
        "order me",
        "order mein",
    ]

    for word in hinglish_words:

        if re.search(
            rf"\b{re.escape(word)}\b",
            lower_text
        ):
            return "hinglish"

    return "english"


# =========================================================
# EXPLICIT LANGUAGE COMMAND
# =========================================================

def detect_language_preference(text):

    if not text:
        return None

    original = str(text).strip()

    text = original.lower()

    hindi_commands = [
        "speak in hindi",
        "speak hindi",
        "talk in hindi",
        "talk hindi",
        "respond in hindi",
        "reply in hindi",
        "answer in hindi",
        "hindi language",
        "hindi mein",
        "hindi me",
        "hindi mein baat",
        "hindi me baat",
        "hindi mein bolo",
        "hindi me bolo",
        "हिंदी में",
        "हिंदी भाषा में",
        "हिंदी में बात",
        "हिंदी में बोल",
        "हिंदी में बताओ",
    ]

    english_commands = [
        "speak in english",
        "speak english",
        "talk in english",
        "talk english",
        "respond in english",
        "reply in english",
        "answer in english",
        "english language",
        "english mein",
        "english me",
        "english mein baat",
        "english me baat",
        "अंग्रेजी में",
        "अंग्रेज़ी में",
    ]

    hinglish_commands = [
        "speak in hinglish",
        "talk in hinglish",
        "respond in hinglish",
        "reply in hinglish",
        "answer in hinglish",
        "hinglish mein",
        "hinglish me",
    ]

    if any(
        command in text
        for command in hinglish_commands
    ):
        return "hinglish"

    if any(
        command in text
        for command in hindi_commands
    ):
        return "hindi"

    if any(
        command in text
        for command in english_commands
    ):
        return "english"

    return None


# =========================================================
# FIND PREVIOUS LANGUAGE PREFERENCE
# =========================================================

def find_language_preference(conversation):

    if not conversation:
        return None

    for item in reversed(conversation):

        if not isinstance(item, dict):
            continue

        speaker = str(
            item.get("speaker", "")
        ).lower().strip()

        if speaker in [
            "aria",
            "assistant",
            "ai",
        ]:
            continue

        message = item.get(
            "message",
            ""
        )

        preference = detect_language_preference(
            message
        )

        if preference:
            return preference

    return None


# =========================================================
# RESOLVE LANGUAGE - FIXED
# =========================================================

def resolve_language(
    user_message,
    requested_language=None,
    conversation=None,
):

    # -----------------------------------------------------
    # 1. Explicit language command in CURRENT message
    # -----------------------------------------------------

    current_preference = detect_language_preference(
        user_message
    )

    if current_preference:
        return current_preference

    # -----------------------------------------------------
    # 2. Detect CURRENT user message
    #
    # English -> English
    # Hindi -> Hindi
    # Hinglish -> Hinglish
    # -----------------------------------------------------

    detected_language = detect_language(
        user_message
    )

    if detected_language in [
        "hindi",
        "hinglish",
    ]:
        return detected_language

    # -----------------------------------------------------
    # 3. Previous explicit language preference
    #
    # Only use this when current message itself is
    # neutral English/order ID.
    # -----------------------------------------------------

    previous_preference = find_language_preference(
        conversation
    )

    if previous_preference:
        return previous_preference

    # -----------------------------------------------------
    # 4. Frontend language
    #
    # Use only when current message is neutral.
    # -----------------------------------------------------

    if requested_language:

        language = str(
            requested_language
        ).lower().strip()

        if language in [
            "hindi",
            "hi",
            "hi-in",
        ]:
            return "hindi"

        if language in [
            "english",
            "en",
            "en-in",
        ]:
            return "english"

        if language in [
            "hinglish",
            "hi-en",
            "en-hi",
        ]:
            return "hinglish"

    # -----------------------------------------------------
    # 5. Final fallback
    # -----------------------------------------------------

    return detected_language


# =========================================================
# PRODUCT QUESTION
# =========================================================

def is_product_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "product",
        "item",
        "what did i order",
        "what is my order",
        "what's my order",
        "order contains",
        "which product",
        "what product",
        "what's in order",
        "what is in order",
        "what is the product",
        "product name",
        "item name",
        "konsa product",
        "kaunsa product",
        "kya product",
        "product kya",
        "order me kya",
        "order mein kya",
        "order me kya hai",
        "order mein kya hai",
        "maine kya order",
        "kya order kiya",
        "kya mangaya",
        "kya mangwaya",
        "प्रोडक्ट",
        "उत्पाद",
        "ऑर्डर में क्या",
        "कौन सा प्रोडक्ट",
        "कौनसा प्रोडक्ट",
        "क्या प्रोडक्ट",
        "क्या मंगाया",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# OWNER / CUSTOMER NAME QUESTION
# =========================================================

def is_owner_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "owner name",
        "owner ka naam",
        "order owner",
        "whose order",
        "whose name",
        "registered name",
        "customer name",
        "customer ka naam",
        "customer",
        "name of customer",
        "kis naam par",
        "kis naam pe",
        "kiske naam",
        "kiske naam par",
        "kiske naam pe",
        "who is the owner",
        "who owns the order",
        "order kis ke naam",
        "order kis naam",
        "नाम किसका",
        "किस नाम पर",
        "किस नाम पे",
        "किसके नाम",
        "किसके नाम पर",
        "ग्राहक का नाम",
        "कस्टमर का नाम",
        "ओनर का नाम",
        "नाम क्या है",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# PRICE QUESTION
# =========================================================

def is_price_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "price",
        "cost",
        "amount",
        "how much",
        "how much is",
        "what is the price",
        "what's the price",
        "order price",
        "product price",
        "kitne ka",
        "kitna ka",
        "kitni price",
        "kitna paisa",
        "price kya",
        "price kitna",
        "paisa kitna",
        "paisa kitne",
        "कीमत",
        "कितने का",
        "कितने की",
        "कितना का",
        "कितना पैसा",
        "कितनी कीमत",
        "कीमत क्या",
        "दाम",
        "पैसे कितने",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# DELIVERY / STATUS QUESTION
# =========================================================

def is_delivery_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "where is my order",
        "where's my order",
        "order status",
        "what is the status",
        "what's the status",
        "status of my order",
        "delivery status",
        "delivery",
        "when will it arrive",
        "when will my order arrive",
        "when will order arrive",
        "when is my order arriving",
        "is my order delivered",
        "is my order out",
        "kab milega",
        "kab tak",
        "kahan hai",
        "kaha hai",
        "status kya",
        "order ka status",
        "order ki status",
        "order kaha",
        "order kahan",
        "delivery kab",
        "kab deliver",
        "kab deliver hoga",
        "डिलीवरी",
        "कब मिलेगा",
        "कब तक",
        "कहाँ है",
        "कहा है",
        "स्टेटस",
        "स्थिति",
        "ऑर्डर कहाँ",
        "ऑर्डर कहां",
        "कब डिलीवर",
        "डिलीवर हुआ",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# TRACKING QUESTION
# =========================================================

def is_tracking_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "tracking id",
        "tracking number",
        "track id",
        "courier",
        "tracking",
        "waybill",
        "shipment number",
        "awb",
        "tracking code",
        "courier name",
        "courier ka naam",
        "tracking id kya hai",
        "tracking number kya hai",
        "ट्रैकिंग आईडी",
        "ट्रैकिंग नंबर",
        "ट्रैकिंग",
        "कूरियर",
        "कूरियर का नाम",
        "ट्रैकिंग कोड",
        "शिपमेंट नंबर",
        "एडब्ल्यूबी",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# CANCELLATION QUESTION
# =========================================================

def is_cancellation_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "cancel",
        "cancellation",
        "can i cancel",
        "cancel my order",
        "cancel the order",
        "can this be cancelled",
        "cancel kar",
        "cancel karna",
        "cancel kar sakte",
        "cancel ho sakta",
        "order cancel",
        "कैंसल",
        "कैंसिल",
        "रद्द",
        "रद्द कर",
        "रद्द करना",
        "ऑर्डर कैंसल",
        "ऑर्डर रद्द",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# RETURN QUESTION
# =========================================================

def is_return_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "return",
        "returns",
        "return policy",
        "can i return",
        "return my order",
        "return product",
        "वापस",
        "रिटर्न",
        "रिटर्न कर",
        "वापस कर",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# DAMAGED / DEFECTIVE QUESTION
# =========================================================

def is_damage_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "damaged",
        "damage",
        "defective",
        "broken",
        "damaged product",
        "defective product",
        "received damaged",
        "खराब",
        "डैमेज",
        "डैमेज्ड",
        "टूटा",
        "खराब प्रोडक्ट",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# COD QUESTION
# =========================================================

def is_cod_question(text):

    if not text:
        return False

    text = str(text).lower()

    keywords = [
        "cod",
        "cash on delivery",
        "cash delivery",
        "pay cash",
        "pay by cash",
        "upi at doorstep",
        "cash at doorstep",
        "कैश ऑन डिलीवरी",
        "कैश",
        "डिलीवरी पर कैश",
        "upi",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# CREATE ORDER RESPONSE
# =========================================================

def create_order_specific_response(
    order_id,
    user_message,
    language,
):

    result = get_order_details(order_id)

    if not result.get("success"):

        if language == "hindi":
            return (
                "माफ़ कीजिए, मुझे यह ऑर्डर आईडी नहीं मिली। "
                "कृपया सही ऑर्डर आईडी बताइए।"
            )

        if language == "hinglish":
            return (
                "Sorry, mujhe ye order ID nahi mili. "
                "Please correct order ID batayiye."
            )

        return (
            "I couldn't find that order ID. "
            "Please check the order ID and try again."
        )

    order = result["order"]

    customer_name = order.get(
        "customer_name",
        ""
    )

    product = order.get(
        "product",
        ""
    )

    amount = order.get(
        "amount",
        ""
    )

    status = order.get(
        "status",
        ""
    )

    expected = order.get(
        "expected",
        ""
    )

    courier = order.get(
        "courier",
        ""
    )

    tracking_id = order.get(
        "tracking_id",
        ""
    )

    # =====================================================
    # ONLY ORDER ID
    # =====================================================

    if is_only_order_id(
        user_message,
        order_id
    ):

        if language == "hindi":
            return (
                f"जी, आपका ऑर्डर {order_id} मिल गया है। "
                f"आप इसके बारे में क्या जानना चाहते हैं?"
            )

        if language == "hinglish":
            return (
                f"Ji, aapka order {order_id} mil gaya hai. "
                f"Aap iske baare mein kya jaanna chahte hain?"
            )

        return (
            f"Sure, I found your order {order_id}. "
            f"What would you like to know about this order?"
        )

    # =====================================================
    # CUSTOMER NAME
    # =====================================================

    if is_owner_question(user_message):

        if language == "hindi":
            return (
                f"यह ऑर्डर {customer_name} के नाम पर रजिस्टर्ड है।"
            )

        if language == "hinglish":
            return (
                f"Ye order {customer_name} ke naam par registered hai."
            )

        return (
            f"The order is registered under {customer_name}."
        )

    # =====================================================
    # PRODUCT
    # =====================================================

    if is_product_question(user_message):

        if language == "hindi":
            return (
                f"इस ऑर्डर में {product} है।"
            )

        if language == "hinglish":
            return (
                f"Is order mein {product} hai."
            )

        return (
            f"This order contains {product}."
        )

    # =====================================================
    # PRICE
    # =====================================================

    if is_price_question(user_message):

        if language == "hindi":
            return (
                f"आपके ऑर्डर की कीमत {amount} है।"
            )

        if language == "hinglish":
            return (
                f"Aapke order ki price {amount} hai."
            )

        return (
            f"Your order amount is {amount}."
        )

    # =====================================================
    # TRACKING
    # =====================================================

    if is_tracking_question(user_message):

        if not courier and not tracking_id:

            if language == "hindi":
                return (
                    "इस ऑर्डर के लिए अभी courier या tracking ID "
                    "उपलब्ध नहीं है।"
                )

            if language == "hinglish":
                return (
                    "Is order ke liye abhi courier ya tracking ID "
                    "available nahi hai."
                )

            return (
                "Courier and tracking details are not available "
                "for this order yet."
            )

        if language == "hindi":

            if courier and tracking_id:
                return (
                    f"आपका courier {courier} है और आपकी "
                    f"tracking ID {tracking_id} है।"
                )

            if tracking_id:
                return (
                    f"आपकी tracking ID {tracking_id} है।"
                )

            return (
                f"आपका courier {courier} है।"
            )

        if language == "hinglish":

            if courier and tracking_id:
                return (
                    f"Aapka courier {courier} hai aur aapki "
                    f"tracking ID {tracking_id} hai."
                )

            if tracking_id:
                return (
                    f"Aapki tracking ID {tracking_id} hai."
                )

            return (
                f"Aapka courier {courier} hai."
            )

        if courier and tracking_id:
            return (
                f"Your courier is {courier} and your tracking ID "
                f"is {tracking_id}."
            )

        if tracking_id:
            return (
                f"Your tracking ID is {tracking_id}."
            )

        return (
            f"Your courier is {courier}."
        )

    # =====================================================
    # CANCELLATION
    # =====================================================

    if is_cancellation_question(user_message):

        normalized_status = status.lower().strip()

        # Processing
        if normalized_status == "processing":

            if language == "hindi":
                return (
                    "जी हाँ, आपका ऑर्डर अभी Processing में है, "
                    "इसलिए इसे कैंसल किया जा सकता है।"
                )

            if language == "hinglish":
                return (
                    "Ji haan, aapka order abhi Processing mein hai, "
                    "isliye ise cancel kiya ja sakta hai."
                )

            return (
                "Yes, your order is currently Processing, "
                "so it is eligible for cancellation."
            )

        # Out for Delivery
        if normalized_status == "out for delivery":

            if language == "hindi":
                return (
                    "माफ़ कीजिए, आपका ऑर्डर Out for Delivery में है, "
                    "इसलिए इसे अब कैंसल नहीं किया जा सकता। "
                    "आप डिलीवरी के समय पैकेज लेने से मना कर सकते हैं।"
                )

            if language == "hinglish":
                return (
                    "Sorry, aapka order Out for Delivery mein hai, "
                    "isliye ise ab cancel nahi kiya ja sakta. "
                    "Aap delivery ke time package lene se mana kar sakte hain."
                )

            return (
                "Sorry, your order is already Out for Delivery, "
                "so it cannot be cancelled now. "
                "You may refuse the package at the doorstep."
            )

        # Delivered
        if normalized_status == "delivered":

            if language == "hindi":
                return (
                    "यह ऑर्डर पहले ही Delivered हो चुका है, "
                    "इसलिए इसे कैंसल नहीं किया जा सकता। "
                    "अगर आप return करना चाहते हैं, तो Aura Skincare की "
                    "7-day return policy लागू होती है।"
                )

            if language == "hinglish":
                return (
                    "Ye order already Delivered ho chuka hai, "
                    "isliye ise cancel nahi kiya ja sakta. "
                    "Agar aap return karna chahte hain, to Aura Skincare ki "
                    "7-day return policy apply hoti hai."
                )

            return (
                "This order has already been delivered, so it cannot "
                "be cancelled. If you want to return it, Aura Skincare's "
                "7-day return policy applies."
            )

        # Other
        if language == "hindi":
            return (
                f"माफ़ कीजिए, यह ऑर्डर अभी {status} स्थिति में है, "
                "इसलिए इसे कैंसल नहीं किया जा सकता।"
            )

        if language == "hinglish":
            return (
                f"Sorry, ye order abhi {status} status mein hai, "
                "isliye ise cancel nahi kiya ja sakta."
            )

        return (
            f"Sorry, this order is currently {status}, "
            "so it cannot be cancelled."
        )

    # =====================================================
    # DELIVERY / STATUS
    # =====================================================

    if is_delivery_question(user_message):

        if language == "hindi":

            response = (
                f"आपका ऑर्डर अभी {status} है। "
                f"{expected}।"
            )

            if courier:
                response += (
                    f" Courier {courier} है।"
                )

            if tracking_id:
                response += (
                    f" Tracking ID {tracking_id} है।"
                )

            return response

        if language == "hinglish":

            response = (
                f"Aapka order abhi {status} hai. "
                f"{expected}."
            )

            if courier:
                response += (
                    f" Courier {courier} hai."
                )

            if tracking_id:
                response += (
                    f" Tracking ID {tracking_id} hai."
                )

            return response

        response = (
            f"Your order is currently {status}. "
            f"{expected}."
        )

        if courier:
            response += (
                f" The courier is {courier}."
            )

        if tracking_id:
            response += (
                f" The tracking ID is {tracking_id}."
            )

        return response

    # =====================================================
    # DEFAULT ORDER RESPONSE
    # =====================================================

    if language == "hindi":

        response = (
            f"ऑर्डर {order_id} {customer_name} के नाम पर रजिस्टर्ड है। "
            f"इसमें {product} है। "
            f"कीमत {amount} है। "
            f"स्टेटस {status} है। "
            f"{expected}।"
        )

        if courier:
            response += (
                f" Courier {courier} है।"
            )

        if tracking_id:
            response += (
                f" Tracking ID {tracking_id} है।"
            )

        return response

    if language == "hinglish":

        response = (
            f"Order {order_id} {customer_name} ke naam par registered hai. "
            f"Ismein {product} hai. "
            f"Price {amount} hai. "
            f"Status {status} hai. "
            f"{expected}."
        )

        if courier:
            response += (
                f" Courier {courier} hai."
            )

        if tracking_id:
            response += (
                f" Tracking ID {tracking_id} hai."
            )

        return response

    response = (
        f"Order {order_id} is registered under {customer_name}. "
        f"It contains {product} for {amount}. "
        f"The current status is {status}. "
        f"{expected}."
    )

    if courier:
        response += (
            f" The courier is {courier}."
        )

    if tracking_id:
        response += (
            f" The tracking ID is {tracking_id}."
        )

    return response


# =========================================================
# POLICY RESPONSE
# =========================================================

def get_policy_response(text, language):

    if not text:
        return None

    original_text = str(text)

    lower_text = original_text.lower()

    # Shipping
    if any(
        keyword in lower_text
        for keyword in [
            "shipping",
            "delivery charge",
            "shipping charge",
            "shipping fee",
            "shipping cost",
            "shipping price",
            "delivery fee",
            "delivery charge",
            "shipping policy",
            "delivery policy",
            "शिपिंग",
            "डिलीवरी चार्ज",
            "डिलीवरी फीस",
        ]
    ):

        if language == "hindi":
            return (
                "Aura Skincare में ₹499 से ऊपर के orders पर "
                "free shipping है। ₹499 से कम के orders पर "
                "₹50 shipping fee है। Standard delivery "
                "3 से 5 business days लेती है।"
            )

        if language == "hinglish":
            return (
                "Aura Skincare mein ₹499 se upar orders par "
                "free shipping hai. ₹499 se kam orders par "
                "₹50 shipping fee hai. Standard delivery "
                "3 se 5 business days leti hai."
            )

        return (
            "Aura Skincare offers free shipping above ₹499. "
            "Orders below ₹499 have a ₹50 shipping fee. "
            "Standard delivery takes 3 to 5 business days."
        )

    # Returns
    if is_return_question(text):

        if language == "hindi":
            return (
                "Returns delivery के 7 दिनों के अंदर किए जा सकते हैं। "
                "Product unopened, unused और original packaging में होना चाहिए।"
            )

        if language == "hinglish":
            return (
                "Return delivery ke 7 din ke andar kiya ja sakta hai. "
                "Product unopened, unused aur original packaging mein hona chahiye."
            )

        return (
            "Returns are accepted within 7 days of delivery. "
            "The product must be unopened, unused and in original packaging."
        )

    # Damaged
    if is_damage_question(text):

        if language == "hindi":
            return (
                "Damaged या defective product की report delivery के "
                "48 घंटे के अंदर photos के साथ करनी होती है। "
                "Eligible cases में replacement मिल सकता है।"
            )

        if language == "hinglish":
            return (
                "Damaged ya defective product ko delivery ke "
                "48 hours ke andar photos ke saath report karna hota hai. "
                "Eligible cases mein replacement mil sakta hai."
            )

        return (
            "Damaged or defective products must be reported within "
            "48 hours of delivery with photos. Eligible cases may "
            "receive a replacement."
        )

    # COD
    if is_cod_question(text):

        if language == "hindi":
            return (
                "COD ₹2,500 तक available है। "
                "आप doorstep पर cash या UPI से payment कर सकते हैं।"
            )

        if language == "hinglish":
            return (
                "COD ₹2,500 tak available hai. "
                "Aap doorstep par cash ya UPI se payment kar sakte hain."
            )

        return (
            "COD is available up to ₹2,500. "
            "You can pay by cash or UPI at the doorstep."
        )

    return None


# =========================================================
# BASIC RESPONSE
# =========================================================

def get_basic_response(text, language):

    if not text:
        return None

    original_text = str(text).strip()

    lower_text = original_text.lower()

    # Explicit language command
    preference = detect_language_preference(
        original_text
    )

    if preference:

        if preference == "hindi":
            return (
                "जी हाँ, बिल्कुल। मैं आपसे हिंदी में बात करूँगी। "
                "आप बताइए, मैं आपकी कैसे मदद कर सकती हूँ?"
            )

        if preference == "hinglish":
            return (
                "Ji haan, bilkul. Main aapse Hinglish mein baat karungi. "
                "Aap bataiye, main aapki kaise help kar sakti hoon?"
            )

        return (
            "Sure. I will speak with you in English. "
            "How can I help you?"
        )

    # Greeting
    greeting_pattern = (
        r"^(hello|hi|hey|good morning|good afternoon|"
        r"good evening|नमस्ते|नमस्कार|हैलो|हाय)"
    )

    if re.search(
        greeting_pattern,
        lower_text
    ):

        if language == "hindi":
            return (
                "नमस्ते! मैं आरिया हूँ, Aura Skincare की "
                "AI customer support assistant। "
                "मैं आपकी कैसे मदद कर सकती हूँ?"
            )

        if language == "hinglish":
            return (
                "Hello! Main Aria hoon, Aura Skincare ki "
                "AI customer support assistant. "
                "Main aapki kaise help kar sakti hoon?"
            )

        return (
            "Hello! I'm Aria from Aura Skincare. "
            "How can I help you today?"
        )

    # Thank you
    if any(
        phrase in lower_text
        for phrase in [
            "thank you",
            "thanks",
            "thankyou",
            "धन्यवाद",
            "शुक्रिया",
        ]
    ):

        if language == "hindi":
            return (
                "आपका स्वागत है! क्या मैं आपकी किसी और चीज़ में मदद करूँ?"
            )

        if language == "hinglish":
            return (
                "You're welcome! Kya main aapki aur kisi cheez mein help karun?"
            )

        return (
            "You're welcome! Is there anything else I can help you with?"
        )

    return None


# =========================================================
# GENERAL ORDER CHECK REQUEST
# =========================================================

def is_order_check_request(text):

    if not text:
        return False

    lower_text = str(text).lower()

    keywords = [
        "check my order",
        "check the order",
        "check order",
        "track my order",
        "track the order",
        "track order",
        "want to check my order",
        "want to track my order",
        "i want to check my order",
        "i want to track my order",
        "order check",
        "order track",
        "check my order status",
        "check order status",
        "mujhe order check",
        "mera order check",
        "order check karna",
        "order track karna",
        "मेरा ऑर्डर चेक",
        "ऑर्डर चेक",
        "ऑर्डर ट्रैक",
    ]

    return any(
        keyword in lower_text
        for keyword in keywords
    )


# =========================================================
# MAIN RESPONSE GENERATOR
# =========================================================

def generate_response(
    user_message,
    conversation=None,
    requested_language=None,
):

    if conversation is None:
        conversation = []

    # =====================================================
    # LANGUAGE
    # =====================================================

    language = resolve_language(
        user_message,
        requested_language,
        conversation,
    )

    # =====================================================
    # EXPLICIT LANGUAGE COMMAND FIRST
    #
    # Important:
    # If user says "Hindi mein baat karo", don't let
    # previous order context override it.
    # =====================================================

    if detect_language_preference(user_message):

        return get_basic_response(
            user_message,
            language,
        )

    # =====================================================
    # CURRENT ORDER
    # =====================================================

    current_order_id = find_order_id(
        user_message
    )

    # =====================================================
    # PREVIOUS ORDER
    # =====================================================

    order_id = current_order_id

    if not order_id:
        order_id = find_last_order_id(
            conversation
        )

    # =====================================================
    # GENERAL ORDER CHECK
    #
    # If user says:
    # "I want to check my order"
    #
    # Don't send to Gemini.
    # Ask for order ID.
    # =====================================================

    if is_order_check_request(user_message):

        if language == "hindi":
            return (
                "बिल्कुल। मैं आपके ऑर्डर को चेक करने में आपकी मदद कर सकती हूँ। "
                "कृपया अपना ऑर्डर आईडी बताइए।"
            )

        if language == "hinglish":
            return (
                "Bilkul. Main aapke order ko check karne mein help kar sakti hoon. "
                "Please apna order ID bataiye."
            )

        return (
            "Sure. I can help you check your order. "
            "Please provide your order ID."
        )

    # =====================================================
    # POLICY BEFORE ORDER CONTEXT
    #
    # Explicit policy questions should not accidentally
    # return old order details.
    # =====================================================

    policy_response = get_policy_response(
        user_message,
        language,
    )

    if policy_response:
        return policy_response

    # =====================================================
    # ORDER
    # =====================================================

    if order_id:

        return create_order_specific_response(
            order_id,
            user_message,
            language,
        )

    # =====================================================
    # BASIC
    # =====================================================

    basic_response = get_basic_response(
        user_message,
        language,
    )

    if basic_response:
        return basic_response

    # =====================================================
    # GEMINI FALLBACK
    # =====================================================

    try:

        response = ask_gemini(
            user_message,
            conversation,
        )

        if response:
            return response

    except Exception as error:

        print(
            "GEMINI ERROR:",
            error
        )

    # =====================================================
    # SAFE FALLBACK
    # =====================================================

    if language == "hindi":
        return (
            "माफ़ कीजिए, मैं आपकी बात पूरी तरह समझ नहीं पाई। "
            "कृपया थोड़ा और स्पष्ट बताइए।"
        )

    if language == "hinglish":
        return (
            "Sorry, main aapki baat clearly samajh nahi paayi. "
            "Please thoda aur clearly bataiye."
        )

    return (
        "Sorry, I didn't fully understand that. "
        "Could you please explain a little more?"
    )


# =========================================================
# CHAT API
# =========================================================

@csrf_exempt
def chat(request):

    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return JsonResponse({
            "success": True,
            "message": (
                "Aura Skincare AI support API is running."
            ),
            "agent": "Aria",
            "brand": "Aura Skincare",
        })

    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "Only POST requests are allowed.",
            },
            status=405,
        )

    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        body = request.body.decode(
            "utf-8"
        )

        data = json.loads(
            body
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON request.",
            },
            status=400,
        )

    except Exception as error:

        print(
            "JSON ERROR:",
            error
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Unable to read request.",
            },
            status=400,
        )

    # =====================================================
    # MESSAGE
    # =====================================================

    user_message = data.get(
        "message",
        ""
    )

    if user_message is None:
        user_message = ""

    if not isinstance(
        user_message,
        str,
    ):
        user_message = str(
            user_message
        )

    user_message = user_message.strip()

    # =====================================================
    # EMPTY MESSAGE
    # =====================================================

    if not user_message:

        return JsonResponse(
            {
                "success": False,
                "message": "Please provide a message.",
            },
            status=400,
        )

    # =====================================================
    # CONVERSATION
    # =====================================================

    conversation = data.get(
        "conversation",
        [],
    )

    if not isinstance(
        conversation,
        list,
    ):
        conversation = []

    # =====================================================
    # REQUESTED LANGUAGE
    # =====================================================

    requested_language = data.get(
        "language",
        None,
    )

    if requested_language is not None:

        requested_language = str(
            requested_language
        ).strip()

    # =====================================================
    # GENERATE RESPONSE
    # =====================================================

    try:

        response_text = generate_response(
            user_message=user_message,
            conversation=conversation,
            requested_language=requested_language,
        )

        final_language = resolve_language(
            user_message=user_message,
            requested_language=requested_language,
            conversation=conversation,
        )

        # =================================================
        # DETECT ORDER
        # =================================================

        detected_order_id = find_order_id(
            user_message
        )

        if not detected_order_id:

            detected_order_id = find_last_order_id(
                conversation
            )

        # =================================================
        # RESPONSE
        # =================================================

        return JsonResponse({

            "success": True,

            "message": response_text,

            "response": response_text,

            "agent": "Aria",

            "brand": "Aura Skincare",

            "language": final_language,

            "order_id": detected_order_id,

        })

    except Exception as error:

        print(
            "CHAT ERROR:",
            repr(error)
        )

        return JsonResponse({

            "success": False,

            "message": (
                "Sorry, something went wrong. "
                "Please try again."
            ),

            "response": (
                "Sorry, something went wrong. "
                "Please try again."
            ),

            "agent": "Aria",

            "brand": "Aura Skincare",

            "error": str(error),

        }, status=500)