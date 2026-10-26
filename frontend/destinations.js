const destinations = {
  varanasi: {
    name: "About Varanasi",
    img: "destinations_1.png",
    img2: "destinations_2.png",
    history: "Varanasi, also known as “The City of Lights,” is one of the oldest cities known to mankind, dating back over 3,000 years, and a spiritual haven for millions of people around the world. Believed to have been founded by Lord Shiva, it is the most well-known Hindu pilgrimage destination in India and is home to the Kashi Vishwanath, one of the 12 Jyotirlingas. Aptly called the cultural capital of India, Varanasi has long provided the right platform for knowledge, philosophy, devotion, and Indian arts and crafts to flourish. Its magnificent temples are not only places of worship but also repositories of art and architecture, preserving the city's cultural and historical heritage, while its iconic Ganges ghats witness daily prayers, ritual baths, and sacred ceremonies. A beacon of religious practices and ancient rituals, Varanasi comes alive during festivals like Dev Deepawali and Maha Shivratri with vibrant decorations, music, and religious processions, epitomizing its heritage through devotion, tradition, and artistic expression. Renowned for its contributions to arts and literature, the city has been a creative hub that has nurtured poets, writers, and artists throughout history, with a rich poetic tradition exploring love, spirituality, and the quest for truth. Classical music and dance are integral to the city's fabric, captivating audiences and showcasing the rich heritage of Indian art forms.",
    places: ["Kashi Vishwanath Temple", "Dashashwamedh Ghat", "Sarnath", "Assi Ghat"],
  }
};

const select = document.getElementById("destSelect");
const info = document.getElementById("destInfo");

select.addEventListener("change", () => {
  const d = destinations[select.value];

  if (!d) {                      // "-- Select --" chosen
    info.classList.add("hidden");
    return;
  }

  document.getElementById("destName").textContent = d.name;

  const img1 = document.getElementById("destImg");
  img1.src = d.img;
  img1.alt = d.name + " - view 1";

  const img2 = document.getElementById("destImg2");
  img2.src = d.img2;
  img2.alt = d.name + " - view 2";

  document.getElementById("destHistory").textContent = d.history;

  info.classList.remove("hidden");
});