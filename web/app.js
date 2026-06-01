const conversation = document.querySelector("#conversation");
const composer = document.querySelector("#composer");
const input = document.querySelector("#messageInput");
const voiceButton = document.querySelector("#voiceButton");
const modeLabel = document.querySelector("#modeLabel");
const micStatusLabel = document.querySelector("#micStatusLabel");
const ttsStatusLabel = document.querySelector("#ttsStatusLabel");
const scoreLabel = document.querySelector("#scoreLabel");
const totalLabel = document.querySelector("#totalLabel");
const meterFill = document.querySelector("#meterFill");
const voiceOutputButton = document.querySelector("#voiceOutputButton");
const sessionId = crypto.randomUUID();

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;
const mediaDevices = navigator.mediaDevices;
const canSpeak = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
let voiceOutputEnabled = canSpeak;
let selectedVoice = null;
let listening = false;

if (recognition) {
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.continuous = false;
  micStatusLabel.textContent = "Ready";
} else {
  voiceButton.disabled = true;
  voiceButton.title = "Speech recognition is not available in this browser";
  micStatusLabel.textContent = "Unavailable";
}

if (!window.isSecureContext && location.hostname !== "127.0.0.1" && location.hostname !== "localhost") {
  voiceButton.disabled = true;
  voiceButton.title = "Microphone access needs localhost or HTTPS";
  micStatusLabel.textContent = "Blocked";
}

if (!canSpeak) {
  voiceOutputEnabled = false;
  voiceOutputButton.disabled = true;
  voiceOutputButton.textContent = "Voice output unavailable";
  ttsStatusLabel.textContent = "Unavailable";
}

function chooseVoice() {
  if (!canSpeak) return null;
  const voices = window.speechSynthesis.getVoices();
  const englishVoices = voices.filter((voice) => voice.lang && voice.lang.toLowerCase().startsWith("en"));
  selectedVoice =
    englishVoices.find((voice) => voice.lang === "en-US" && /natural|online|aria|guy|jenny|zira|david/i.test(voice.name)) ||
    englishVoices.find((voice) => voice.lang === "en-US") ||
    englishVoices.find((voice) => voice.lang === "en-GB") ||
    englishVoices[0] ||
    null;
  if (voiceOutputEnabled) {
    ttsStatusLabel.textContent = selectedVoice ? `On (${selectedVoice.lang})` : "No English";
  }
  return selectedVoice;
}

if (canSpeak) {
  chooseVoice();
  window.speechSynthesis.addEventListener("voiceschanged", chooseVoice);
}

function addBubble(role, text) {
  const article = document.createElement("article");
  article.className = `bubble ${role}`;
  const name = document.createElement("span");
  name.textContent = role === "bot" ? "Raza" : "You";
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.append(name, paragraph);
  conversation.append(article);
  conversation.scrollTop = conversation.scrollHeight;
}

function speak(text) {
  if (!canSpeak || !voiceOutputEnabled) return;
  const voice = selectedVoice || chooseVoice();
  if (!voice) {
    ttsStatusLabel.textContent = "No English";
    addBubble("bot", "I cannot find an English text-to-speech voice on this browser. Install or enable an English voice in the system speech settings.");
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = voice.lang || "en-US";
  utterance.voice = voice;
  utterance.rate = 0.96;
  utterance.pitch = 1;
  utterance.volume = 1;
  utterance.addEventListener("start", () => {
    ttsStatusLabel.textContent = "Speaking";
  });
  utterance.addEventListener("end", () => {
    ttsStatusLabel.textContent = `On (${voice.lang})`;
  });
  utterance.addEventListener("error", () => {
    ttsStatusLabel.textContent = "Error";
  });
  window.speechSynthesis.speak(utterance);
}

function updateStatus(data) {
  const modeNames = {
    home: "Choose",
    qa: "Q&A",
    quiz: "Quiz",
  };
  modeLabel.textContent = modeNames[data.mode] || "Ready";
  scoreLabel.textContent = data.score ?? 0;
  totalLabel.textContent = data.quizTotal ?? 7;
  const total = data.quizTotal || 7;
  const width = Math.max(0, Math.min(100, ((data.score || 0) / total) * 100));
  meterFill.style.width = `${width}%`;
}

async function sendMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) return;

  if (canSpeak) {
    chooseVoice();
  }
  addBubble("user", trimmed);
  input.value = "";

  const response = await fetch("/api/message", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ sessionId, message: trimmed }),
  });

  if (!response.ok) {
    addBubble("bot", "Something went wrong in the demo server.");
    return;
  }

  const data = await response.json();
  addBubble("bot", data.reply);
  updateStatus(data);
  speak(data.reply);
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(input.value);
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});

async function checkMicrophoneAccess() {
  if (!mediaDevices?.getUserMedia) {
    micStatusLabel.textContent = "Unavailable";
    addBubble("bot", "This browser does not expose microphone access. Try Chrome or Edge on localhost.");
    return false;
  }

  try {
    const stream = await mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((track) => track.stop());
    return true;
  } catch (error) {
    const labels = {
      NotAllowedError: "Permission",
      SecurityError: "Permission",
      NotFoundError: "No mic",
      DevicesNotFoundError: "No mic",
      NotReadableError: "Busy",
      TrackStartError: "Busy",
      OverconstrainedError: "Settings",
    };
    micStatusLabel.textContent = labels[error.name] || "Error";
    addBubble("bot", `Microphone access failed: ${labels[error.name] || error.name}. You can still type your message.`);
    return false;
  }
}

voiceButton.addEventListener("click", async () => {
  if (!recognition || listening) return;
  const hasMic = await checkMicrophoneAccess();
  if (!hasMic) return;
  try {
    listening = true;
    micStatusLabel.textContent = "Listening";
    voiceButton.classList.add("listening");
    recognition.start();
  } catch {
    listening = false;
    micStatusLabel.textContent = "Retry";
    voiceButton.classList.remove("listening");
  }
});

if (recognition) {
  recognition.addEventListener("start", () => {
    listening = true;
    micStatusLabel.textContent = "Listening";
  });

  recognition.addEventListener("result", (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    sendMessage(transcript);
  });

  recognition.addEventListener("error", (event) => {
    const labels = {
      "not-allowed": "Permission",
      "service-not-allowed": "Permission",
      "no-speech": "No speech",
      "audio-capture": "No mic",
      network: "Network",
    };
    micStatusLabel.textContent = labels[event.error] || "Error";
    addBubble("bot", `Microphone problem: ${labels[event.error] || event.error}. You can still type your message.`);
  });

  recognition.addEventListener("end", () => {
    listening = false;
    if (!["Permission", "No mic", "Blocked"].includes(micStatusLabel.textContent)) {
      micStatusLabel.textContent = "Ready";
    }
    voiceButton.classList.remove("listening");
  });
}

voiceOutputButton.addEventListener("click", () => {
  if (!canSpeak) return;
  voiceOutputEnabled = !voiceOutputEnabled;
  window.speechSynthesis.cancel();
  voiceOutputButton.textContent = voiceOutputEnabled ? "Voice output on" : "Voice output off";
  ttsStatusLabel.textContent = voiceOutputEnabled && selectedVoice ? `On (${selectedVoice.lang})` : "Off";
  if (voiceOutputEnabled) {
    speak("Voice output is on.");
  }
});
