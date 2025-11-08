// === CONFIGURATION ===
const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxyKwHBlKjGKdlniuFm-T4ganKj790LopgE1igc_sX_rXqiIbR4T6k33YrnoBhuoZ7Xtg/exec"; // replace with your Apps Script Web App URL
// =====================

// 1️⃣ Define your trials
const trials = [
  { items: ["apple", "banana", "car"], correct: 2 },
  { items: ["dog", "cat", "table"], correct: 2 },
  { items: ["red", "blue", "chair"], correct: 2 },
  { items: ["pencil", "eraser", "dog"], correct: 2 }
];

// 2️⃣ Convert trials to jsPsych trial objects
const trialTimeline = trials.map(trial => {
  return {
    type: jsPsychHtmlButtonResponse,
    stimulus: "<p>Click the item that doesn't fit:</p>",
    choices: trial.items,
    data: { correct: trial.correct },
    on_finish: function(data) {
      const choiceIndex = data.response;
      data.correct_choice = (choiceIndex === data.correct);
      data.items = trial.items;
    }
  };
});

// 3️⃣ Instructions trial
const instructions = {
  type: jsPsychHtmlButtonResponse,
  stimulus: "<p>Welcome!<br>For each set of three items, click the one that doesn't fit.</p>",
  choices: ["Start"]
};

// 4️⃣ Timeline: instructions + trials
const timeline = [instructions, ...trialTimeline];

// 5️⃣ Run the experiment
jsPsych.run(timeline).then(() => {
  // Prepare data payload for Google Sheets
  const payload = {
    data: jsPsych.data.get().values()
  };

  // Send data to Google Apps Script
  fetch(GOOGLE_SCRIPT_URL, {
    method: "POST",
    mode: "no-cors",
    body: JSON.stringify(payload)
  });

  // Thank you message
  document.body.innerHTML = "<h2>Thank you for participating!</h2>";
});

