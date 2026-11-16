const destinations = {
  varanasi: {
    name: "About Varanasi",
    img: "destinations_1.png",
    img2: "destinations_2.png",
    history: [
      "Varanasi, also known as “The City of Lights,” is one of the oldest cities known to mankind, dating back over 3,000 years, and a spiritual haven for millions of people around the world. Believed to have been founded by Lord Shiva, it is the most well-known Hindu pilgrimage destination in India and is home to the Kashi Vishwanath, one of the 12 Jyotirlingas. Aptly called the cultural capital of India, Varanasi has long provided the right platform for knowledge, philosophy, devotion, and Indian arts and crafts to flourish. Its magnificent temples are not only places of worship but also repositories of art and architecture, preserving the city's cultural and historical heritage, while its iconic Ganges ghats witness daily prayers, ritual baths, and sacred ceremonies.",
 
      "A beacon of religious practices and ancient rituals, Varanasi comes alive during festivals like Dev Deepawali and Maha Shivratri with vibrant decorations, music, and religious processions, epitomizing its heritage through devotion, tradition, and artistic expression. Renowned for its contributions to arts and literature, the city has been a creative hub that has nurtured poets, writers, and artists throughout history, with a rich poetic tradition exploring love, spirituality, and the quest for truth. Classical music and dance are integral to the city's fabric, captivating audiences and showcasing the rich heritage of Indian art forms."
    ],
    places: ["Kashi Vishwanath Temple", "Dashashwamedh Ghat", "Sarnath", "Assi Ghat"],
  }
};
 
const select = document.getElementById("destSelect");
const info = document.getElementById("destInfo");
const heading = document.getElementById("destName");

select.addEventListener("change", () => {
  const destination = destinations[select.value];
  info.classList.toggle("hidden", !destination);
  document.getElementById("destinationWelcome").hidden = Boolean(destination);
  document.body.classList.toggle("choosing-destination", !destination);
  heading.textContent = destination ? destination.name : "Choose a destination";
  try {
    if (destination) localStorage.setItem("selectedDestination", select.value);
    else localStorage.removeItem("selectedDestination");
  } catch (error) {
    // Selection remains usable when browser storage is disabled.
  }
  if (!destination) return;
  document.getElementById("destImg").src = destination.img;
  document.getElementById("destImg2").src = destination.img2;
  const cultureStart = destination.history[0].indexOf("Aptly called");
  document.getElementById("cityText").textContent = destination.history[0].slice(0, cultureStart).trim();
  document.getElementById("cultureText").textContent = destination.history[0].slice(cultureStart);
  document.getElementById("artsText").textContent = destination.history[1];
});
