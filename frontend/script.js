(function () {
  const menu = document.getElementById("menu");
  if (!menu) return; // page lo <nav id="menu"> lekapote skip

  const steps = [
    { name: "Destinations", file: "destinations.html" },
    { name: "Regions",      file: "regions.html" },
    { name: "Places",       file: "places.html" },
    { name: "Preferences",  file: "preferences.html" },
    { name: "Customize",    file: "customize.html" },
    { name: "Plan",         file: "plan.html" },
    { name: "Suggestions",  file: "suggestions.html" },
  ];

  const current = location.pathname.split("/").pop() || "destinations.html";

  let visited = [];
  try {
    visited = JSON.parse(localStorage.getItem("visited") || "[]");
  } catch (e) {}
  if (!visited.includes(current)) visited.push(current);
  try {
    localStorage.setItem("visited", JSON.stringify(visited));
  } catch (e) {}

  menu.innerHTML = steps
    .map(s => {
      let cls = "";
      if (s.file === current) cls = "active";
      else if (visited.includes(s.file)) cls = "visited";
      return `<a href="${s.file}" class="${cls}">${s.name}</a>`;
    })
    .join("");
})();