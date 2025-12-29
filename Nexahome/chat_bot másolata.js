// n8n Code node (JavaScript)
// Discord input: item.json.content
// Random replies for ALL categories (like jokes/greetings)
// + adds item.json.action that tells which function/category ran

const jokes = [
  "Why did the scarecrow win an award? Because he was outstanding in his field!",
  "I would tell you a construction joke, but I'm still working on it.",
  "Why don't scientists trust atoms? Because they make up everything!",
  "Why did the bicycle fall over? Because it was two-tired!",
  "What do you call fake spaghetti? An impasta!",
  "Why did the math book look sad? Because it had too many problems!",
  "Why can't your nose be 12 inches long? Because then it would be a foot!",
  "What do you call cheese that isn't yours? Nacho cheese!"
];

const greetingMessages = [
  "Hello! How can I help you?",
  "Hi there! What can I do for you?",
  "Hey! Need any assistance?",
  "Greetings! How may I assist you?",
  "Hello! What would you like to do today?",
  "Hi! I'm here to help you with anything you need.",
  "Hey there! How can I make your day better?",
  "Greetings! What can I do for you today?"
];

// Multiple variants for every type
const emptyReplies = [
  "You didn't type anything.",
  "I didn't receive any text.",
  "Looks like your message was empty."
];

const goodbyeReplies = [
  "Goodbye!",
  "See you later!",
  "Bye! Take care."
];

const howAreYouReplies = [
  "I'm just a program, but thanks for asking!",
  "Doing fine—I'm code, but I appreciate it!",
  "I'm online and ready. 😄"
];

const nameReplies = [
  "I'm Nexa, your server and home assistant.",
  "Nexa here — your server/home assistant.",
  "I'm Nexa. What do you need?"
];

const timeReplies = [
  (t) => `The current time is ${t}.`,
  (t) => `Right now it's ${t}.`,
  (t) => `Time check: ${t}.`
];

const rebootReplies = [
  "Rebooting . . .",
  "Rebooting now!",
  "System reboot initiated."
];

const dateReplies = [
  (d) => `Today's date is ${d}.`,
  (d) => `It's ${d} today.`,
  (d) => `Date: ${d}.`
];

const unknownReplies = [
  "Sorry, I don't understand that.",
  "I didn't get that. Try a different command.",
  "Hmm… I don't recognize that command."
];

// Helpers
function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function getCurrentTime() {
  const now = new Date();
  return now.toTimeString().slice(0, 8);
}

function getCurrentDate() {
  const now = new Date();
  return now.toISOString().slice(0, 10);
}

function startOfDay(d) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

function daysBetween(a, b) {
  const msPerDay = 24 * 60 * 60 * 1000;
  const A = startOfDay(a).getTime();
  const B = startOfDay(b).getTime();
  return Math.round((B - A) / msPerDay);
}

function formatDateYYYYMMDD(d) {
  return d.toISOString().slice(0, 10);
}

// Christmas variants
const christmasTodayReplies = [
  "Merry Christmas! 🎄✨",
  "Happy Holidays! ❄️🎅",
  "Merry Christmas — enjoy the holidays! 🎁"
];

const christmasNotTodayReplies = [
  (next, inDays) =>
    `It's not Christmas today. The next Christmas period starts on ${next} (in ${inDays} day${inDays === 1 ? "" : "s"}).`,
  (next, inDays) =>
    `Not today — Christmas starts on ${next}. That's in ${inDays} day${inDays === 1 ? "" : "s"}.`,
  (next, inDays) =>
    `Nope, not Christmas today. Next one begins: ${next} (in ${inDays} day${inDays === 1 ? "" : "s"}).`
];

function getChristmasReply(now = new Date()) {
  const y = now.getFullYear();

  const christmasEve = new Date(y, 11, 24); // Dec 24
  const christmasDay = new Date(y, 11, 25); // Dec 25
  const boxingDay = new Date(y, 11, 26); // Dec 26

  const today = startOfDay(now).getTime();
  const t24 = startOfDay(christmasEve).getTime();
  const t25 = startOfDay(christmasDay).getTime();
  const t26 = startOfDay(boxingDay).getTime();

  const isChristmasWindow = (today === t24 || today === t25 || today === t26);

  if (isChristmasWindow) {
    return pickRandom(christmasTodayReplies);
  }

  // Next Christmas period start (Dec 24)
  let next = christmasEve;
  if (today > t26) {
    next = new Date(y + 1, 11, 24);
  }

  const nextStr = formatDateYYYYMMDD(next);
  const inDays = daysBetween(new Date(today), next);

  const tmpl = pickRandom(christmasNotTodayReplies);
  return tmpl(nextStr, inDays);
}

// Main: returns BOTH reply + action (state)
function getNexaReply(inputText) {
  const text = (inputText ?? "").toString().trim();
  const lower = text.toLowerCase();

  let action = "unknown";
  let reply = "";

  if (text === "") {
    action = "empty";
    reply = pickRandom(emptyReplies);
    return { reply, action };
  }

  if (["exit", "quit", "bye"].includes(lower)) {
    action = "exit";
    reply = pickRandom(goodbyeReplies);
    return { reply, action };
  }

  if ([
    "hi", "hello", "hey", "hi!", "hello!", "hey!",
    "hi there", "hello there", "hey there",
    "greetings", "greetings!", "ey", "eyo"
  ].includes(lower)) {
    action = "greeting";
    reply = pickRandom(greetingMessages);
    return { reply, action };
  }

  if ([
    "how are you?", "how are you", "how's it going?",
    "how are you doing?"
  ].includes(lower)) {
    action = "status";
    reply = pickRandom(howAreYouReplies);
    return { reply, action };
  }

  if ([
    "what is your name?", "what's your name?", "who are you?"
  ].includes(lower)) {
    action = "name";
    reply = pickRandom(nameReplies);
    return { reply, action };
  }

  if ([
    "tell me a joke", "joke", "make me laugh", "joke please"
  ].includes(lower)) {
    action = "joke";
    reply = pickRandom(jokes);
    return { reply, action };
  }

  if ([
    "what time is it?", "time", "current time"
  ].includes(lower)) {
    action = "time";
    const t = getCurrentTime();
    const tmpl = pickRandom(timeReplies);
    reply = tmpl(t);
    return { reply, action };
  }

  if ([
    "reboot", "restart"
  ].includes(lower)) {
    action = "reboot";
    reply = pickRandom(rebootReplies);
    return { reply, action };
  }

  if ([
    "xmas", "christmas", "crismas",
    "merry christmas", "marry christmas",
    "merry xmas", "happy christmas"
  ].includes(lower)) {
    action = "christmas";
    reply = getChristmasReply(new Date());
    return { reply, action };
  }

  if ([
    "what is the date today?", "date", "current date"
  ].includes(lower)) {
    action = "date";
    const d = getCurrentDate();
    const tmpl = pickRandom(dateReplies);
    reply = tmpl(d);
    return { reply, action };
  }

  action = "unknown";
  reply = pickRandom(unknownReplies);
  return { reply, action };
}

// --- n8n Code node ---
const items = $input.all();

for (const item of items) {
  const content = item.json.content ?? "";
  const result = getNexaReply(content);

  item.json.reply = result.reply;
  item.json.action = result.action; // ✅ state variable: tells what ran
}

return items;
