// =====================================================
// AURA AI - CUSTOMER SUPPORT
// Frontend JavaScript
// Django Backend Connected
// Hindi + English + Hinglish Voice Support
// =====================================================


// =====================================================
// BACKEND API
// =====================================================

const API_URL = "http://127.0.0.1:8000/api/chat/";


// =====================================================
// MOBILE MENU
// =====================================================

const menuButton = document.getElementById("menuButton");
const mobileMenu = document.getElementById("mobileMenu");
const mobileClose = document.getElementById("mobileClose");

if (menuButton && mobileMenu) {
    menuButton.addEventListener("click", function () {
        mobileMenu.classList.add("open");
    });
}

if (mobileClose && mobileMenu) {
    mobileClose.addEventListener("click", function () {
        mobileMenu.classList.remove("open");
    });
}

document.querySelectorAll(".mobile-links a").forEach(function (link) {
    link.addEventListener("click", function () {
        if (mobileMenu) {
            mobileMenu.classList.remove("open");
        }
    });
});


// =====================================================
// DOM ELEMENTS
// =====================================================

const startCall = document.getElementById("startCall");
const endCall = document.getElementById("endCall");
const voiceState = document.getElementById("voiceState");

const chatBox = document.getElementById("chatBox");
const textInput = document.getElementById("textInput");
const sendButton = document.getElementById("sendButton");
const chatMic = document.getElementById("chatMic");

const typingIndicator = document.getElementById("typingIndicator");

const emptyLog = document.getElementById("emptyLog");
const completedLog = document.getElementById("completedLog");

const finalTranscript = document.getElementById("finalTranscript");
const jsonSummary = document.getElementById("jsonSummary");


// =====================================================
// VARIABLES
// =====================================================

let conversation = [];

let callActive = false;

let recognition = null;

let isRecognizing = false;
let speechSupported = false;

let isSending = false;
let isSpeaking = false;

let selectedRecognitionLanguage = "en-IN";

let lastCustomerLanguage = "en-IN";


// Current order remembered by frontend
let currentOrderId = null;


// Prevent multiple automatic listening timers
let listeningTimer = null;


// =====================================================
// SPEECH RECOGNITION
// =====================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

if (SpeechRecognition) {

    speechSupported = true;

    recognition = new SpeechRecognition();

    recognition.lang = "en-IN";

    recognition.continuous = false;

    recognition.interimResults = false;

    recognition.maxAlternatives = 1;
}


// =====================================================
// CURRENT TIME
// =====================================================

function getCurrentTime() {

    return new Date().toLocaleTimeString("en-IN", {
        hour: "2-digit",
        minute: "2-digit"
    });
}


// =====================================================
// ADD CHAT MESSAGE
// =====================================================

function addChatMessage(speaker, message) {

    if (!chatBox) {
        return;
    }

    const messageDiv = document.createElement("div");

    if (speaker === "Aria") {

        messageDiv.className =
            "chat-message ai-message";

    } else {

        messageDiv.className =
            "chat-message user-message";
    }


    const messageContent =
        document.createElement("div");

    messageContent.className =
        "message-content";


    const strong =
        document.createElement("span");

    strong.className =
        "message-name";

    strong.textContent =
        speaker;


    const paragraph =
        document.createElement("p");

    paragraph.textContent =
        message;


    messageContent.appendChild(strong);

    messageContent.appendChild(paragraph);

    messageDiv.appendChild(messageContent);

    chatBox.appendChild(messageDiv);


    chatBox.scrollTop =
        chatBox.scrollHeight;
}


// =====================================================
// ADD CONVERSATION
// =====================================================

function addConversation(speaker, message) {

    conversation.push({

        speaker: speaker,

        message: message,

        time: getCurrentTime()
    });
}


// =====================================================
// SHOW TYPING
// =====================================================

function showTyping() {

    if (typingIndicator) {

        typingIndicator.classList.add("active");
    }
}


// =====================================================
// HIDE TYPING
// =====================================================

function hideTyping() {

    if (typingIndicator) {

        typingIndicator.classList.remove("active");
    }
}


// =====================================================
// VOICE STATE
// =====================================================

function setVoiceState(state) {

    if (!voiceState) {
        return;
    }


    voiceState.textContent =
        state;


    voiceState.classList.remove(
        "listening",
        "thinking",
        "speaking"
    );


    if (state === "Listening") {

        voiceState.classList.add("listening");
    }


    if (state === "Thinking") {

        voiceState.classList.add("thinking");
    }


    if (state === "Speaking") {

        voiceState.classList.add("speaking");
    }
}


// =====================================================
// AVAILABLE VOICES
// =====================================================

function getAvailableVoices() {

    if (!("speechSynthesis" in window)) {

        return [];
    }

    return window.speechSynthesis.getVoices();
}


// =====================================================
// LANGUAGE DETECTION
// =====================================================

function detectCustomerLanguage(message) {

    if (!message) {

        return "en-IN";
    }


    const text =
        String(message).trim();


    if (!text) {

        return "en-IN";
    }


    // -------------------------------------------------
    // Hindi Devanagari
    // -------------------------------------------------

    const hindiPattern =
        /[\u0900-\u097F]/;


    if (hindiPattern.test(text)) {

        return "hi-IN";
    }


    // -------------------------------------------------
    // Hinglish detection
    // -------------------------------------------------

    const lowerText =
        text.toLowerCase();


    const hindiWords = [

        "haan",
        "ha",
        "nahi",
        "nahin",
        "nhi",

        "aap",
        "aapka",
        "aapki",
        "apka",
        "apki",

        "mera",
        "meri",

        "mujhe",
        "mujhko",
        "mujhse",

        "kya",
        "kaise",
        "kaisa",
        "kaisi",

        "kab",
        "kahan",
        "kaha",

        "kyun",
        "kyon",

        "chahiye",
        "hai",
        "hain",

        "karna",
        "karni",
        "karo",
        "kare",

        "batao",
        "bataye",
        "bataiye",

        "kitna",
        "kitne",
        "kitni",

        "milega",
        "aayega",
        "ayega",

        "konsa",
        "kaunsa",
        "kaunsi",

        "wala",
        "wali",
        "wale",

        "order kaha",
        "order kab",
        "order kitna"
    ];


    let hindiWordCount = 0;


    hindiWords.forEach(function (word) {

        const escapedWord =
            word.replace(
                /[.*+?^${}()|[\]\\]/g,
                "\\$&"
            );


        const pattern =
            new RegExp(
                "\\b" +
                escapedWord +
                "\\b",
                "i"
            );


        if (pattern.test(lowerText)) {

            hindiWordCount++;
        }
    });


    if (hindiWordCount >= 1) {

        return "hi-IN";
    }


    return "en-IN";
}


// =====================================================
// SET CUSTOMER LANGUAGE
// =====================================================

function setCustomerLanguage(message) {

    const language =
        detectCustomerLanguage(message);


    lastCustomerLanguage =
        language;


    selectedRecognitionLanguage =
        language;


    console.log(
        "Customer language:",
        language
    );


    return language;
}


// =====================================================
// FIND BEST VOICE
// =====================================================

function getBestVoice(language) {

    const voices =
        getAvailableVoices();


    if (!voices.length) {

        return null;
    }


    const targetLanguage =
        String(language || "en-IN")
            .toLowerCase();


    // -------------------------------------------------
    // Hindi
    // -------------------------------------------------

    if (targetLanguage === "hi-in") {

        let voice =
            voices.find(function (item) {

                return (
                    item.name === "Google हिन्दी" &&
                    item.lang &&
                    item.lang.toLowerCase() === "hi-in"
                );
            });


        if (voice) {

            return voice;
        }


        voice =
            voices.find(function (item) {

                return (
                    item.lang &&
                    item.lang.toLowerCase() === "hi-in"
                );
            });


        if (voice) {

            return voice;
        }


        voice =
            voices.find(function (item) {

                return (
                    item.lang &&
                    item.lang.toLowerCase().startsWith("hi")
                );
            });


        if (voice) {

            return voice;
        }
    }


    // -------------------------------------------------
    // English India
    // -------------------------------------------------

    if (targetLanguage === "en-in") {

        let voice =
            voices.find(function (item) {

                return (
                    item.lang &&
                    item.lang.toLowerCase() === "en-in"
                );
            });


        if (voice) {

            return voice;
        }


        voice =
            voices.find(function (item) {

                return (
                    item.lang &&
                    item.lang.toLowerCase().startsWith("en-in")
                );
            });


        if (voice) {

            return voice;
        }


        voice =
            voices.find(function (item) {

                return (
                    item.lang &&
                    item.lang.toLowerCase().startsWith("en")
                );
            });


        if (voice) {

            return voice;
        }
    }


    return null;
}


// =====================================================
// LOG AVAILABLE VOICES
// =====================================================

function logAvailableVoices() {

    const voices =
        getAvailableVoices();


    console.log(
        "Total speech voices:",
        voices.length
    );


    voices.forEach(function (voice) {

        console.log(
            voice.name +
            " | " +
            voice.lang
        );
    });
}


if ("speechSynthesis" in window) {

    window.speechSynthesis.onvoiceschanged =
        function () {

            logAvailableVoices();
        };


    setTimeout(function () {

        logAvailableVoices();

    }, 500);
}


// =====================================================
// SPEAK RESPONSE
// =====================================================

function speakResponse(message, languageOverride) {

    if (!message) {
        return;
    }


    if (!("speechSynthesis" in window)) {

        console.warn(
            "Speech synthesis is not supported."
        );

        return;
    }


    const language =
        languageOverride ||
        lastCustomerLanguage ||
        "en-IN";


    console.log(
        "Aria response language:",
        language
    );


    const selectedVoice =
        getBestVoice(language);


    if (selectedVoice) {

        console.log(
            "Selected Aria voice:",
            selectedVoice.name,
            "|",
            selectedVoice.lang
        );
    }


    try {

        window.speechSynthesis.cancel();

    } catch (error) {

        console.log(
            "Speech cancel error:",
            error
        );
    }


    isSpeaking = true;


    const utterance =
        new SpeechSynthesisUtterance(message);


    utterance.lang =
        language;


    if (selectedVoice) {

        utterance.voice =
            selectedVoice;
    }


    // -------------------------------------------------
    // Voice settings
    // -------------------------------------------------

    if (language === "hi-IN") {

        utterance.rate = 0.90;

        utterance.pitch = 1;

        utterance.volume = 1;

    } else {

        utterance.rate = 0.95;

        utterance.pitch = 1;

        utterance.volume = 1;
    }


    // -------------------------------------------------
    // Speech start
    // -------------------------------------------------

    utterance.onstart =
        function () {

            isSpeaking = true;

            setVoiceState("Speaking");

            console.log(
                "Aria started speaking:",
                language
            );
        };


    // -------------------------------------------------
    // Speech end
    // -------------------------------------------------

    utterance.onend =
        function () {

            isSpeaking = false;

            console.log(
                "Aria finished speaking."
            );


            if (callActive) {

                setVoiceState("Listening");


                scheduleListening(700);

            } else {

                setVoiceState("Ready");
            }
        };


    // -------------------------------------------------
    // Speech error
    // -------------------------------------------------

    utterance.onerror =
        function (event) {

            isSpeaking = false;


            console.log(
                "Speech synthesis error:",
                event.error
            );


            // Browser can report "interrupted"
            // when cancel() is called.
            if (event.error === "interrupted") {

                return;
            }


            if (callActive) {

                setVoiceState("Listening");

            } else {

                setVoiceState("Ready");
            }
        };


    // -------------------------------------------------
    // Speak
    // -------------------------------------------------

    setTimeout(function () {

        if (!isSpeaking) {

            return;
        }


        try {

            window.speechSynthesis.speak(
                utterance
            );

        } catch (error) {

            console.error(
                "Speech speak error:",
                error
            );

            isSpeaking = false;
        }

    }, 120);
}


// =====================================================
// SCHEDULE LISTENING
// =====================================================

function scheduleListening(delay = 600) {

    if (listeningTimer) {

        clearTimeout(listeningTimer);
    }


    listeningTimer =
        setTimeout(function () {

            if (
                callActive &&
                !isSending &&
                !isSpeaking &&
                !isRecognizing
            ) {

                startListening();
            }

        }, delay);
}


// =====================================================
// SEND MESSAGE TO DJANGO
// =====================================================

async function sendMessage(messageFromUser) {

    const message =
        String(
            messageFromUser || ""
        ).trim();


    if (!message || isSending) {

        return;
    }


    isSending = true;


    // -------------------------------------------------
    // Detect language
    // -------------------------------------------------

    const customerLanguage =
        setCustomerLanguage(message);


    // -------------------------------------------------
    // Detect order ID
    // -------------------------------------------------

    const detectedOrder =
        findOrderId(message);


    if (detectedOrder) {

        currentOrderId =
            detectedOrder;

        console.log(
            "Current order:",
            currentOrderId
        );
    }


    // -------------------------------------------------
    // Add customer message
    // -------------------------------------------------

    addChatMessage(
        "You",
        message
    );


    addConversation(
        "Customer",
        message
    );


    // -------------------------------------------------
    // Clear text box
    // -------------------------------------------------

    if (textInput) {

        textInput.value = "";
    }


    // -------------------------------------------------
    // Stop recognition
    // -------------------------------------------------

    if (
        recognition &&
        isRecognizing
    ) {

        try {

            recognition.stop();

        } catch (error) {

            console.log(
                "Recognition stop:",
                error
            );
        }
    }


    showTyping();

    setVoiceState("Thinking");


    try {

        console.log(
            "Sending message to:",
            API_URL
        );


        console.log(
            "Customer message:",
            message
        );


        console.log(
            "Customer language:",
            customerLanguage
        );


        console.log(
            "Current order:",
            currentOrderId
        );


        // -------------------------------------------------
        // Django request
        // -------------------------------------------------

        const response =
            await fetch(
                API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        message:
                            message,

                        conversation:
                            conversation,

                        language:
                            customerLanguage
                    })
                }
            );


        const data =
            await response.json();


        console.log(
            "Backend response:",
            data
        );


        hideTyping();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                data.response ||
                "Something went wrong."
            );
        }


        // -------------------------------------------------
        // Support backend response formats
        // -------------------------------------------------

        const aiMessage =
            data.message ||
            data.response ||
            data.reply ||
            "Sorry, I couldn't understand that.";


        // -------------------------------------------------
        // Add Aria response
        // -------------------------------------------------

        addChatMessage(
            "Aria",
            aiMessage
        );


        addConversation(
            "Aria",
            aiMessage
        );


        // -------------------------------------------------
        // Speak
        // -------------------------------------------------

        speakResponse(
            aiMessage,
            customerLanguage
        );


    } catch (error) {

        console.error(
            "Django API Error:",
            error
        );


        hideTyping();


        let errorMessage;


        if (customerLanguage === "hi-IN") {

            errorMessage =
                "माफ़ कीजिए, मेरे सपोर्ट सिस्टम से कनेक्शन में समस्या आ रही है। कृपया थोड़ी देर बाद फिर कोशिश करें।";

        } else {

            errorMessage =
                "I'm sorry, I'm having trouble connecting to my support system right now. Please try again.";
        }


        addChatMessage(
            "Aria",
            errorMessage
        );


        addConversation(
            "Aria",
            errorMessage
        );


        speakResponse(
            errorMessage,
            customerLanguage
        );


    } finally {

        isSending = false;
    }
}


// =====================================================
// SEND BUTTON
// =====================================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        function () {

            if (textInput) {

                sendMessage(
                    textInput.value
                );
            }
        }
    );
}


// =====================================================
// ENTER KEY
// =====================================================

if (textInput) {

    textInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                sendMessage(
                    textInput.value
                );
            }
        }
    );
}


// =====================================================
// QUICK QUESTIONS
// =====================================================

document
    .querySelectorAll(".quick-question")
    .forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const question =
                    button.textContent.trim();


                if (textInput) {

                    textInput.value =
                        question;

                    textInput.focus();
                }
            }
        );
    });


// =====================================================
// START LISTENING
// =====================================================

function startListening() {

    if (!recognition) {

        alert(
            "Voice recognition is not supported in this browser. Please use Google Chrome."
        );

        return;
    }


    if (
        !callActive ||
        isRecognizing ||
        isSending ||
        isSpeaking
    ) {

        return;
    }


    recognition.lang =
        selectedRecognitionLanguage;


    console.log(
        "Starting recognition:",
        recognition.lang
    );


    try {

        recognition.start();

    } catch (error) {

        console.log(
            "Recognition start error:",
            error
        );
    }
}


// =====================================================
// SET RECOGNITION LANGUAGE
// =====================================================

function setRecognitionLanguageFromText(text) {

    if (!text) {

        selectedRecognitionLanguage =
            "en-IN";

        return;
    }


    const language =
        detectCustomerLanguage(text);


    selectedRecognitionLanguage =
        language;


    lastCustomerLanguage =
        language;


    console.log(
        "Next recognition language:",
        selectedRecognitionLanguage
    );
}


// =====================================================
// SPEECH RECOGNITION EVENTS
// =====================================================

if (recognition) {


    // -------------------------------------------------
    // Recognition started
    // -------------------------------------------------

    recognition.onstart =
        function () {

            isRecognizing =
                true;


            console.log(
                "Speech recognition started:",
                recognition.lang
            );


            if (callActive) {

                setVoiceState(
                    "Listening"
                );
            }
        };


    // -------------------------------------------------
    // Recognition result
    // -------------------------------------------------

    recognition.onresult =
        function (event) {

            const transcript =
                event.results[0][0]
                    .transcript
                    .trim();


            if (!transcript) {

                return;
            }


            console.log(
                "Customer said:",
                transcript
            );


            const detectedLanguage =
                setCustomerLanguage(
                    transcript
                );


            console.log(
                "Detected customer language:",
                detectedLanguage
            );


            if (callActive) {

                sendMessage(
                    transcript
                );

            } else {

                if (textInput) {

                    textInput.value =
                        transcript;
                }

                sendMessage(
                    transcript
                );
            }
        };


    // -------------------------------------------------
    // Recognition error
    // -------------------------------------------------

    recognition.onerror =
        function (event) {

            console.log(
                "Speech recognition error:",
                event.error
            );


            isRecognizing = false;


            if (!callActive) {

                return;
            }


            if (event.error === "no-speech") {

                setVoiceState(
                    "Listening"
                );


                scheduleListening(800);


                return;
            }


            if (event.error === "not-allowed") {

                setVoiceState(
                    "Microphone blocked"
                );


                return;
            }


            if (
                event.error ===
                "audio-capture"
            ) {

                setVoiceState(
                    "Microphone unavailable"
                );


                return;
            }


            if (
                event.error ===
                "language-not-supported"
            ) {

                console.warn(
                    "Selected language is not supported."
                );


                selectedRecognitionLanguage =
                    "en-IN";


                setVoiceState(
                    "Listening"
                );


                scheduleListening(800);


                return;
            }


            setVoiceState(
                "Listening"
            );


            scheduleListening(800);
        };


    // -------------------------------------------------
    // Recognition ended
    // -------------------------------------------------

    recognition.onend =
        function () {

            isRecognizing =
                false;


            console.log(
                "Speech recognition ended."
            );


            if (
                callActive &&
                !isSending &&
                !isSpeaking
            ) {

                setVoiceState(
                    "Listening"
                );


                scheduleListening(600);
            }
        };
}


// =====================================================
// START CALL
// =====================================================

if (startCall) {

    startCall.addEventListener(
        "click",
        async function () {


            // -------------------------------------------------
            // Browser microphone support
            // -------------------------------------------------

            if (
                !navigator.mediaDevices ||
                !navigator.mediaDevices.getUserMedia
            ) {

                alert(
                    "Microphone access is not supported in this browser."
                );

                return;
            }


            try {

                // -------------------------------------------------
                // Request microphone permission
                // -------------------------------------------------

                const stream =
                    await navigator
                        .mediaDevices
                        .getUserMedia({
                            audio: true
                        });


                stream
                    .getTracks()
                    .forEach(
                        function (track) {

                            track.stop();
                        }
                    );


                // -------------------------------------------------
                // Reset call
                // -------------------------------------------------

                callActive = true;

                conversation = [];

                currentOrderId = null;

                isSending = false;

                isSpeaking = false;

                isRecognizing = false;

                lastCustomerLanguage =
                    "en-IN";

                selectedRecognitionLanguage =
                    "en-IN";


                // -------------------------------------------------
                // Reset speech
                // -------------------------------------------------

                if ("speechSynthesis" in window) {

                    window.speechSynthesis.cancel();
                }


                // -------------------------------------------------
                // Reset recognition
                // -------------------------------------------------

                if (recognition) {

                    recognition.lang =
                        "en-IN";
                }


                // -------------------------------------------------
                // Buttons
                // -------------------------------------------------

                startCall.style.display =
                    "none";


                if (endCall) {

                    endCall.style.display =
                        "inline-flex";
                }


                // -------------------------------------------------
                // Clear old chat
                // -------------------------------------------------

                if (chatBox) {

                    chatBox.innerHTML =
                        "";
                }


                // -------------------------------------------------
                // Reset call log
                // -------------------------------------------------

                if (completedLog) {

                    completedLog.style.display =
                        "none";
                }


                if (emptyLog) {

                    emptyLog.style.display =
                        "block";
                }


                if (finalTranscript) {

                    finalTranscript.innerHTML =
                        "";
                }


                if (jsonSummary) {

                    jsonSummary.textContent =
                        "";
                }


                // -------------------------------------------------
                // Aria greeting
                // -------------------------------------------------

                const greeting =
                    "Hi, I'm Aria from Aura Skincare. How can I help you today?";


                addChatMessage(
                    "Aria",
                    greeting
                );


                addConversation(
                    "Aria",
                    greeting
                );


                speakResponse(
                    greeting,
                    "en-IN"
                );


            } catch (error) {

                console.error(
                    "Microphone error:",
                    error
                );


                alert(
                    "Please allow microphone permission to start the AI voice call."
                );
            }
        }
    );
}


// =====================================================
// END CALL
// =====================================================

if (endCall) {

    endCall.addEventListener(
        "click",
        function () {


            callActive =
                false;


            // -------------------------------------------------
            // Clear listening timer
            // -------------------------------------------------

            if (listeningTimer) {

                clearTimeout(
                    listeningTimer
                );

                listeningTimer =
                    null;
            }


            // -------------------------------------------------
            // Stop recognition
            // -------------------------------------------------

            if (recognition) {

                try {

                    recognition.stop();

                } catch (error) {

                    console.log(
                        "Recognition stop:",
                        error
                    );
                }
            }


            isRecognizing =
                false;


            isSpeaking =
                false;


            // -------------------------------------------------
            // Stop speech
            // -------------------------------------------------

            if ("speechSynthesis" in window) {

                try {

                    window.speechSynthesis.cancel();

                } catch (error) {

                    console.log(
                        "Speech cancel:",
                        error
                    );
                }
            }


            // -------------------------------------------------
            // UI
            // -------------------------------------------------

            setVoiceState(
                "Call Ended"
            );


            if (startCall) {

                startCall.style.display =
                    "inline-flex";
            }


            endCall.style.display =
                "none";


            // -------------------------------------------------
            // Generate final call summary
            // -------------------------------------------------

            updateCallLog();
        }
    );
}


// =====================================================
// CHAT MICROPHONE
// =====================================================

if (chatMic) {

    chatMic.addEventListener(
        "click",
        async function () {


            if (!recognition) {

                alert(
                    "Voice recognition is not supported. Please use Google Chrome."
                );

                return;
            }


            if (
                callActive ||
                isRecognizing ||
                isSending ||
                isSpeaking
            ) {

                return;
            }


            try {

                const stream =
                    await navigator
                        .mediaDevices
                        .getUserMedia({
                            audio: true
                        });


                stream
                    .getTracks()
                    .forEach(
                        function (track) {

                            track.stop();
                        }
                    );


                recognition.lang =
                    selectedRecognitionLanguage;


                console.log(
                    "Chat microphone language:",
                    recognition.lang
                );


                recognition.start();


            } catch (error) {

                console.error(
                    "Chat microphone error:",
                    error
                );


                alert(
                    "Please allow microphone permission."
                );
            }
        }
    );
}


// =====================================================
// FIND ORDER ID
// =====================================================

function findOrderId(text) {

    if (!text) {

        return null;
    }


    const originalText =
        String(text);


    const value =
        originalText.toUpperCase();


    // -------------------------------------------------
    // ORD-101 / ORD 101 / ORD101
    // -------------------------------------------------

    const match =
        value.match(
            /\bORD[- ]?(\d{3})\b/
        );


    if (match) {

        const number =
            match[1];


        if (
            number === "101" ||
            number === "102" ||
            number === "103"
        ) {

            return "ORD-" + number;
        }
    }


    // -------------------------------------------------
    // Direct order numbers
    // -------------------------------------------------

    const direct =
        value.match(
            /\b(101|102|103)\b/
        );


    if (direct) {

        return "ORD-" + direct[1];
    }


    // -------------------------------------------------
    // Hindi digits
    // -------------------------------------------------

    const hindiDigits =
        originalText
            .replace(/१/g, "1")
            .replace(/२/g, "2")
            .replace(/३/g, "3")
            .replace(/४/g, "4")
            .replace(/५/g, "5")
            .replace(/६/g, "6")
            .replace(/७/g, "7")
            .replace(/८/g, "8")
            .replace(/९/g, "9")
            .replace(/०/g, "0");


    const hindiOrder =
        hindiDigits.match(
            /\b(101|102|103)\b/
        );


    if (hindiOrder) {

        return "ORD-" +
            hindiOrder[1];
    }


    // -------------------------------------------------
    // Spoken English numbers
    // -------------------------------------------------

    const spokenEnglish = {

        "one zero one": "ORD-101",
        "one oh one": "ORD-101",
        "one hundred one": "ORD-101",
        "hundred one": "ORD-101",

        "one zero two": "ORD-102",
        "one oh two": "ORD-102",
        "one hundred two": "ORD-102",
        "hundred two": "ORD-102",

        "one zero three": "ORD-103",
        "one oh three": "ORD-103",
        "one hundred three": "ORD-103",
        "hundred three": "ORD-103"
    };


    const lower =
        originalText.toLowerCase();


    for (const phrase in spokenEnglish) {

        if (lower.includes(phrase)) {

            return spokenEnglish[phrase];
        }
    }


    // -------------------------------------------------
    // Spoken Hindi numbers
    // -------------------------------------------------

    const spokenHindi = {

        "एक शून्य एक": "ORD-101",
        "एक जीरो एक": "ORD-101",
        "एक सौ एक": "ORD-101",
        "सौ एक": "ORD-101",

        "एक शून्य दो": "ORD-102",
        "एक जीरो दो": "ORD-102",
        "एक सौ दो": "ORD-102",
        "सौ दो": "ORD-102",

        "एक शून्य तीन": "ORD-103",
        "एक जीरो तीन": "ORD-103",
        "एक सौ तीन": "ORD-103",
        "सौ तीन": "ORD-103"
    };


    for (const phrase in spokenHindi) {

        if (originalText.includes(phrase)) {

            return spokenHindi[phrase];
        }
    }


    return null;
}


// =====================================================
// GET LATEST ORDER FROM CONVERSATION
// =====================================================

function getLatestOrderId() {

    // First use current remembered order

    if (currentOrderId) {

        return currentOrderId;
    }


    // Otherwise search conversation
    // from newest to oldest

    for (
        let i = conversation.length - 1;
        i >= 0;
        i--
    ) {

        const found =
            findOrderId(
                conversation[i].message
            );


        if (found) {

            currentOrderId =
                found;

            return found;
        }
    }


    return null;
}


// =====================================================
// DETECT INTENT
// =====================================================

function detectIntent() {

    const customerText =
        conversation
            .filter(function (item) {

                return (
                    item.speaker === "Customer" ||
                    item.speaker === "You"
                );
            })
            .map(function (item) {

                return item.message.toLowerCase();
            })
            .join(" ");


    // -------------------------------------------------
    // Order tracking
    // -------------------------------------------------

    if (
        customerText.includes("track") ||
        customerText.includes("tracking") ||
        customerText.includes("where is my order") ||
        customerText.includes("where is the order") ||
        customerText.includes("where is order") ||
        customerText.includes("delivery") ||
        customerText.includes("deliver") ||
        customerText.includes("status") ||
        customerText.includes("कहाँ है") ||
        customerText.includes("कब तक") ||
        customerText.includes("डिलीवरी") ||
        customerText.includes("स्टेटस") ||
        customerText.includes("ट्रैकिंग")
    ) {

        return "ORDER_TRACKING";
    }


    // -------------------------------------------------
    // Cancellation
    // -------------------------------------------------

    if (
        customerText.includes("cancel") ||
        customerText.includes("cancellation") ||
        customerText.includes("कैंसल") ||
        customerText.includes("रद्द")
    ) {

        return "ORDER_CANCELLATION";
    }


    // -------------------------------------------------
    // Return
    // -------------------------------------------------

    if (
        customerText.includes("return") ||
        customerText.includes("refund") ||
        customerText.includes("रिटर्न") ||
        customerText.includes("रिफंड")
    ) {

        return "RETURN_POLICY";
    }


    // -------------------------------------------------
    // Damaged / defective
    // -------------------------------------------------

    if (
        customerText.includes("damage") ||
        customerText.includes("damaged") ||
        customerText.includes("defective") ||
        customerText.includes("damaged product") ||
        customerText.includes("डैमेज") ||
        customerText.includes("खराब")
    ) {

        return "DAMAGED_PRODUCT";
    }


    // -------------------------------------------------
    // COD
    // -------------------------------------------------

    if (
        customerText.includes("cod") ||
        customerText.includes("cash on delivery") ||
        customerText.includes("cash delivery") ||
        customerText.includes("कैश ऑन डिलीवरी")
    ) {

        return "COD";
    }


    // -------------------------------------------------
    // Shipping
    // -------------------------------------------------

    if (
        customerText.includes("shipping") ||
        customerText.includes("shipping charge") ||
        customerText.includes("delivery charge") ||
        customerText.includes("delivery fee") ||
        customerText.includes("shipping fee") ||
        customerText.includes("शिपिंग")
    ) {

        return "SHIPPING_POLICY";
    }


    return "GENERAL_SUPPORT";
}


// =====================================================
// CREATE SUMMARY
// =====================================================

function createSummary(intent, orderId) {

    if (
        intent === "ORDER_TRACKING" &&
        orderId
    ) {

        return (
            "Customer asked about the delivery or tracking status of " +
            orderId +
            "."
        );
    }


    if (
        intent === "ORDER_CANCELLATION"
    ) {

        if (orderId) {

            return (
                "Customer asked about cancelling order " +
                orderId +
                "."
            );
        }


        return (
            "Customer asked about the order cancellation policy."
        );
    }


    if (
        intent === "RETURN_POLICY"
    ) {

        return (
            "Customer asked about Aura Skincare's return and refund policy."
        );
    }


    if (
        intent === "DAMAGED_PRODUCT"
    ) {

        return (
            "Customer asked about a damaged or defective product."
        );
    }


    if (intent === "COD") {

        return (
            "Customer asked about Cash on Delivery."
        );
    }


    if (
        intent === "SHIPPING_POLICY"
    ) {

        return (
            "Customer asked about Aura Skincare shipping policy."
        );
    }


    return (
        "Customer contacted Aria for Aura Skincare customer support."
    );
}


// =====================================================
// UPDATE CALL LOG
// =====================================================

function updateCallLog() {

    if (conversation.length === 0) {

        return;
    }


    // -------------------------------------------------
    // Show completed call
    // -------------------------------------------------

    if (emptyLog) {

        emptyLog.style.display =
            "none";
    }


    if (completedLog) {

        completedLog.style.display =
            "grid";
    }


    if (finalTranscript) {

        finalTranscript.innerHTML =
            "";
    }


    // -------------------------------------------------
    // Render transcript
    // -------------------------------------------------

    conversation.forEach(
        function (item) {

            const div =
                document.createElement(
                    "div"
                );


            div.className =
                "final-message";


            const strong =
                document.createElement(
                    "strong"
                );


            strong.textContent =
                item.speaker;


            const span =
                document.createElement(
                    "span"
                );


            span.textContent =
                " — " +
                item.message;


            const small =
                document.createElement(
                    "small"
                );


            small.style.marginLeft =
                "6px";


            small.textContent =
                item.time;


            div.appendChild(
                strong
            );


            div.appendChild(
                span
            );


            div.appendChild(
                small
            );


            if (finalTranscript) {

                finalTranscript.appendChild(
                    div
                );
            }
        }
    );


    // -------------------------------------------------
    // Intent
    // -------------------------------------------------

    const intent =
        detectIntent();


    // -------------------------------------------------
    // Latest order
    // -------------------------------------------------

    const orderId =
        getLatestOrderId();


    // -------------------------------------------------
    // Resolution status
    // -------------------------------------------------

    let resolutionStatus =
        "INFORMATION_PROVIDED";


    if (orderId) {

        resolutionStatus =
            "RESOLVED";

    } else if (
        intent !==
        "GENERAL_SUPPORT"
    ) {

        resolutionStatus =
            "RESOLVED";
    }


    // -------------------------------------------------
    // Structured summary
    // -------------------------------------------------

    const summary = {

        customer_intent:
            intent,

        order_id:
            orderId,

        resolution_status:
            resolutionStatus,

        call_summary:
            createSummary(
                intent,
                orderId
            ),

        conversation_turns:
            conversation.length
    };


    // -------------------------------------------------
    // Show JSON
    // -------------------------------------------------

    if (jsonSummary) {

        jsonSummary.textContent =
            JSON.stringify(
                summary,
                null,
                2
            );
    }
}


// =====================================================
// INITIAL ARIA MESSAGE
// =====================================================

if (
    chatBox &&
    chatBox.children.length === 0
) {

    const welcome =
        "Hi! I'm Aria from Aura Skincare. How can I help you today?";


    addChatMessage(
        "Aria",
        welcome
    );
}


// =====================================================
// INITIAL BUTTON STATE
// =====================================================

if (endCall) {

    endCall.style.display =
        "none";
}


if (voiceState) {

    setVoiceState(
        "Ready"
    );
}


// =====================================================
// DEBUG INFORMATION
// =====================================================

console.log(
    "===================================="
);

console.log(
    "Aura AI frontend loaded successfully."
);

console.log(
    "Backend API:",
    API_URL
);

console.log(
    "Speech Recognition supported:",
    speechSupported
);

console.log(
    "Speech Synthesis supported:",
    "speechSynthesis" in window
);

console.log(
    "Initial customer language:",
    lastCustomerLanguage
);

console.log(
    "===================================="
);