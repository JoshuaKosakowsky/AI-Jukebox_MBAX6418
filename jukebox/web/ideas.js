"use strict";

// Local inspiration only. The existing Generate action owns all provider calls.
(() => {
  const pick = items => items[Math.floor(Math.random() * items.length)];
  const subjects = [
    "a homesick vending machine", "three raccoons in a trench coat", "my jealous refrigerator",
    "a moose on probation", "the last sock in the dryer", "a ghost with a day job",
    "a pigeon with a mortgage", "an exhausted volcano", "a sentient parking ticket",
    "my emergency sandwich", "a snail running for mayor", "a moon with stage fright",
    "a retired thunderstorm", "a goose from human resources", "a lonely traffic cone",
    "a tax-paying werewolf", "a nervous black hole", "a cactus with abandonment issues",
    "the office goldfish", "a dishwasher going on strike", "a disco-loving glacier",
    "a time-traveling lunchbox", "an emotionally unavailable elevator", "a very polite kraken",
    "a jellyfish wedding planner", "an accountant made of bees", "a mermaid stuck in traffic",
    "a sleepwalking scarecrow", "a dragon in community college", "a depressed disco ball",
    "a washing machine with political ambitions", "an opera-singing mushroom", "a robot afraid of charging",
    "a cloud with a parking permit", "the school cafeteria knight", "a melodramatic office chair",
    "a troll doing remote support", "a pirate with a library fine", "a detective made of leftovers", "a goose in witness protection"
  ];
  const objects = [
    "moldy cheese", "a haunted stapler", "a suspicious casserole", "a tiny marching band",
    "my final exam", "a broken umbrella", "expired coupons", "a dramatic houseplant",
    "a singing tax return", "the wrong birthday cake", "a borrowed planet", "a cursed kazoo",
    "a bureaucratic dragon", "a professional apology", "a jar of yesterday", "a bag of fog",
    "an invisible sofa", "a sourdough starter", "a furious snow globe", "an antique password",
    "a pretentious potato", "an overdue library book", "my emotional-support spreadsheet",
    "a bag of melted snowmen", "the world's smallest riot", "a glittering resignation letter",
    "a thunderstorm in a teacup", "a talking dental crown", "a haunted shopping cart",
    "a penguin's business plan", "my unpaid sleep debt", "a legally binding jellybean"
  ];
  const places = [
    "inside the office microwave", "at a wedding on Mars", "in the supermarket after closing",
    "on a midnight bus", "under the staff-room table", "at the bottom of a cereal box",
    "in a courtroom for clouds", "on the last train to the moon", "at a laundromat in space",
    "behind the school cafeteria", "in an underwater bowling alley", "at a funeral for Wi-Fi",
    "in an airport for migrating ghosts", "at the annual meeting of spoons", "in a mountain cable car",
    "at an Antarctic karaoke bar", "on a pirate customer-service line", "in a supermarket freezer",
    "at a volcano's retirement party", "in the lost-luggage afterlife", "on a commuter train for giants",
    "in a submarine talent show", "at the wizard licensing office", "in a cemetery for broken printers",
    "at a cheese tasting for robots", "on a roller coaster for philosophers", "in a library run by sharks", "at a drive-through on Venus"
  ];
  const wants = [
    "wants custody of the moon", "is applying for a human job", "has unionized my kitchen",
    "is suing the weather", "has fallen in love with the fire alarm", "is hiding from the lunch inspector",
    "has declared my lunch a sovereign nation", "is training for competitive napping",
    "has become the landlord", "is negotiating with gravity", "is refusing to haunt on weekends",
    "has eaten the office budget", "is selling insurance to mermaids", "is filing for emotional bankruptcy",
    "has booked the sun for a birthday party", "is opening a detective agency for crumbs",
    "has stolen the opera's lunch money", "is outsourcing its nightmares", "has been promoted to traffic light",
    "is rehearsing an apology to Tuesday", "is staging a musical about my taxes", "is charging rent for my dreams",
    "has misplaced the entire ocean", "has become allergic to applause", "is teaching manners to thunder",
    "is pretending to be a mountain", "has banned Mondays from the kitchen", "is arguing with its future self",
    "has replaced the CEO with soup", "is delivering pizza to the underworld", "has adopted a nervous submarine", "is recruiting a choir of moths"
  ];
  const twists = [
    "the moon wants a refund", "my toaster is the judge", "the mountain calls in sick",
    "the witnesses are all ducks", "gravity has resigned", "the villain is my lunch",
    "the orchestra is on strike", "my sandwich becomes the boss", "the clouds demand overtime",
    "the ghost needs a reference", "all the spoons remember", "my socks start a rebellion",
    "the ending is held up in customs", "the fridge knows my secrets", "a glacier steals the spotlight",
    "the last bus is a whale", "the cheese has hired a lawyer", "the audience is a room of planets"
  ];
  const milestones = [
    "pass this test", "finish my taxes", "find my missing sock", "survive this meeting",
    "pay off my haunted toaster", "learn to parallel park", "answer my last email",
    "win custody of my leftovers", "teach the goose to whisper", "get my sandwich back",
    "convince the moon to stay", "graduate from clown accounting", "defeat the office printer",
    "return this cursed casserole", "finish my night shift", "apologize to the ocean",
    "get through airport security", "win an argument with the fridge", "get the dragon its diploma",
    "find a parking space on Pluto", "finish this group project", "teach my printer empathy",
    "get the ghost off the payroll", "recover my stolen Tuesday", "pass my cloud inspection",
    "find the remote control", "survive the choir audition", "fix the haunted coffee maker",
    "get my sea legs back", "deliver this suspicious pizza", "finish jury duty for ducks", "convince the sun to clock in"
  ];
  const escapes = [
    "go to the mountains", "open a disco for moths", "become the mayor of a cloud",
    "teach whales to yodel", "retire inside a pinball machine", "move in with the northern lights",
    "start a bakery for ghosts", "sail a bathtub to Saturn", "join a band of rebellious spoons",
    "get a cabin on a comet", "dance with an avalanche", "take the sea out for dinner",
    "open a spa for volcanoes", "learn the language of elevators", "start a moonlit snail rodeo",
    "take my houseplant on a world tour", "buy the sunset a sandwich", "become a lighthouse for lost socks",
    "take a nap inside a rainbow", "become a gondolier for clouds", "join the penguin jazz circuit",
    "turn my deadlines into confetti", "open a hotel for thunderstorms", "dance barefoot on the moon",
    "run a marathon with a glacier", "write love letters to gravity", "start a union for imaginary friends",
    "rent a treehouse from a dragon", "spend the summer as a comet", "take my toaster to the opera",
    "give the ocean a performance review", "open a diner at the end of time"
  ];
  const disasters = [
    "missed the bus", "forgot my lunch", "burned the toast", "failed the vibe check",
    "lost my receipt", "wore mismatched shoes", "replied all", "spilled my coffee",
    "ate the office cheese", "forgot my password", "broke the doorbell", "slept through the apocalypse",
    "left my keys in another century", "ordered the wrong soup", "took the wrong umbrella", "sneezed during the spell",
    "put my rent money in the jukebox", "accidentally adopted a volcano", "forgot the robot's birthday",
    "brought a goose to a job interview", "sent my resignation to the wrong planet", "mistook the ghost for my landlord",
    "put glitter in the coffee machine", "tripped over the horizon", "unplugged the moon",
    "lost a staring contest to soup", "fell asleep in the wrong timeline", "dropped the wedding cake into orbit",
    "accidentally hired my reflection", "woke the sleeping supermarket", "got stood up by an elevator", "deleted my own theme song"
  ];
  const hidingPlaces = ["sandwich", "school bag", "spacesuit", "desk drawer", "wedding cake", "boots", "breakfast cereal", "pocket universe"];
  const forms = ["power ballad", "protest anthem", "lullaby", "victory march", "breakup song", "sea shanty", "courtroom confession", "love duet"];
  const genres = [
    "opera", "bluegrass", "death metal", "salsa", "synth-pop", "drum and bass", "gospel",
    "polka", "reggae dub", "tango", "flamenco", "disco", "country waltz", "punk rock",
    "Gregorian chant", "hyperpop", "bossa nova", "Afrobeat", "swing jazz", "industrial rock",
    "Celtic folk", "doom metal", "barbershop", "ska", "orchestral pop", "psychedelic funk",
    "chiptune", "New Orleans brass", "electro-cumbia", "surf rock"
  ];
  const arrangements = [
    "with frantic banjo", "with mournful brass", "with toy-piano melodies", "with thunderous percussion",
    "with accordion and handclaps", "with a kazoo-like lead", "with soaring strings", "with a stomping tuba bass",
    "with icy bells", "with surf-guitar riffs", "with a sudden half-time chorus", "with a gentle music-box opening",
    "with a bass-heavy finale", "with close vocal harmonies", "with distorted cello", "with steel drums"
  ];
  const moods = [
    "Triumphant about a very small victory", "Heartbroken but ridiculously theatrical", "Hopeful against all common sense",
    "Furious about a minor inconvenience", "Tender, strange and sincerely romantic", "Nervous excitement before a bad idea",
    "Majestic and completely overdramatic", "Deadpan humor with genuine sadness", "Joyful chaos with a warm ending",
    "Defiant and oddly dignified", "Dreamy homesickness for somewhere impossible", "Suspicious but ready to dance",
    "A tiny crisis treated like the end of the world", "Relieved, loud and ready to escape", "Melancholy with mischievous energy",
    "Confidently unqualified", "Quietly hopeful after an absurd disaster", "Celebratory and slightly bewildered",
    "Apologetic with unreasonable swagger", "Euphoric over a questionable life decision"
  ];
  let previousFamily = -1;
  const recentTitles = [];
  function nextIdea(seed) {
    const subject = () => pick(subjects), object = () => pick(objects), place = () => pick(places);
    const builders = seed ? [
      () => `${seed}, but ${pick(twists)}`,
      () => `${seed}: ${pick(twists)}`,
      () => `A ${pick(forms)} for ${seed}`,
      () => `${seed} ${place()}, narrated by ${subject()}`,
      () => `Once ${seed} is over, I'll ${pick(escapes)}`,
      () => `Me versus ${seed}, judged by ${subject()}`,
      () => `A love letter to ${seed} from ${subject()}`,
      () => `${seed} has been replaced by ${object()}`
    ] : [
      () => `There's ${object()} in my ${pick(hidingPlaces)}`,
      () => `Once I ${pick(milestones)}, I'll ${pick(escapes)}`,
      () => `${subject()} ${pick(wants)}`,
      () => `I ${pick(disasters)}, and now ${pick(twists)}`,
      () => `A ${pick(forms)} for ${object()} ${place()}`,
      () => `${subject()} ${place()}, but ${pick(twists)}`,
      () => `The breakup of ${object()} and ${subject()}`,
      () => `I trusted ${subject()} with ${object()}`,
      () => `${subject()} needs ${object()} to ${pick(escapes)}`,
      () => `My ${pick(hidingPlaces)} is haunted by ${subject()}`,
      () => `Dear ${subject()}, please return ${object()}`,
      () => `I brought ${object()} to ${place().replace(/^(at|in|inside|on|under|behind) /, "")}`
    ];
    let title;
    for (let attempt = 0; attempt < 20; attempt++) {
      const family = pick(builders.map((_, index) => index).filter(index => index !== previousFamily));
      previousFamily = family;
      title = builders[family]();
      if (Math.random() < 0.55 && !title.includes(", but ") && !title.includes(", and now ")) {
        const extra = `${title}, and ${pick(twists)}`;
        if (extra.length <= 120) title = extra;
      }
      title = title[0].toUpperCase() + title.slice(1);
      if (title.length <= 120 && !recentTitles.includes(title)) break;
    }
    // Bound even adversarial/repetitive random sources without cutting off a story.
    if (title.length > 120) title = `A ${pick(forms)} for ${seed || object()}`;
    recentTitles.push(title);
    if (recentTitles.length > 128) recentTitles.shift();
    const genre = pick(genres);
    const blend = Math.random() < 0.75 ? ` meets ${pick(genres.filter(item => item !== genre))}` : "";
    return {title, style: `${genre}${blend}; ${pick(arrangements)}`, mood: pick(moods)};
  }

  const form = document.querySelector("#cover-form");
  const seed = document.querySelector("#idea-seed");
  const keep = document.querySelector("#idea-keep");
  const status = document.querySelector("#idea-status");
  function surprise() {
    const startingIdea = Array.from(seed.value.trim().replace(/\s+/gu, " ")).slice(0, 42).join("");
    const idea = nextIdea(startingIdea);
    form.elements.namedItem("title").value = idea.title;
    for (const key of ["style", "mood"]) {
      const input = form.elements.namedItem(key);
      if (!keep.checked || !input.value.trim()) input.value = idea[key];
    }
    const vocal = form.querySelector('input[name="mode"][value="vocal"]');
    vocal.checked = true;
    vocal.dispatchEvent(new Event("change", {bubbles: true}));
    status.textContent = `Idea: ${idea.title}`;
  }
  document.querySelector("#surprise-song").addEventListener("click", surprise);
  seed.addEventListener("keydown", event => {
    if (event.key === "Enter") { event.preventDefault(); surprise(); }
  });
  form.addEventListener("reset", () => { status.textContent = ""; });
})();
