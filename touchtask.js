const jsPsych = initJsPsych();

// Timeline array
const timeline = [];

// Welcome
const welcome_trial = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: "<h2>Welcome to the Triple Odd-One-Out Experiment</h2>" +
            "<p>In this experiment, you will see sets of three images.</p>" +
            "<p>Your task is to choose the image that does not fit with the other two.</p>" +
            "<p>Press any key to continue.</p>"
};
timeline.push(welcome_trial);

// Instructions
const instructions_trial = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: "<p>Here is an example:</p>" +
            "<div style='display:flex; justify-content:space-around;'>" +
            "<img src='img/img1.png' width='150'>" +
            "<img src='img/img2.png' width='150'>" +
            "<img src='img/img3.png' width='150'>" +
            "</div>" +
            "<p>Click the image that is different from the other two.</p>" +
            "<p>Press any key to start the experiment.</p>"
};
timeline.push(instructions_trial);

// Define your triple stimuli (replace with your 13 images)
const triple_trials = [
  { items: ['img/img1.png','img/img2.png','img/img3.png'] },
  { items: ['img/img4.png','img/img5.png','img/img6.png'] },
  { items: ['img/img7.png','img/img8.png','img/img9.png'] },
  { items: ['img/img10.png','img/img11.png','img/img12.png'] },
  { items: ['img/img1.png','img/img12.png','img/img13.png'] }
];

// Add triple trials to timeline
triple_trials.forEach(triple => {
  timeline.push({
    type: jsPsychImageButtonResponse,
    stimulus: "<div style='margin-bottom:10px;'>Click the image that does not fit with the other two:</div>",
    choices: triple.items,
    button_html: function(choice) {
      return '<button class="jspsych-btn" style="border:none;background:none;padding:0;margin:0;"><img src="' + choice + '" width="150"></button>';
    },
    data: { items: triple.items },
    on_finish: function(data) {
      const items = data.items;
      data.item1 = items[0];
      data.item2 = items[1];
      data.item3 = items[2];
      data.response_img = items[data.response];
      console.log("Trial data:", data);
    }
  });
});

const end_trial = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: "<p>Thank you for participating!</p><p>Press any key to download your data.</p>",
  on_finish: function() {
    // Filter only the main image trials
    const filtered = jsPsych.data.get().filter({ trial_type: 'image-button-response' }).values();

    // Extract needed fields and map response index to actual image
    const cleanData = filtered.map(trial => ({
      item1: trial.item1,
      item2: trial.item2,
      item3: trial.item3,
      response: [trial.item1, trial.item2, trial.item3][trial.response], // map index to image
      rt: trial.rt
    }));

    // Convert to CSV manually
    let csv = "item1,item2,item3,response,rt\n";
    cleanData.forEach(row => {
      csv += `${row.item1},${row.item2},${row.item3},${row.response},${row.rt}\n`;
    });

    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'experiment_data.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
};

timeline.push(end_trial);

// Run everything
jsPsych.run(timeline);
