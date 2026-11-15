// Run before page scripts restore any saved planning selections.
(function () {
  const keys = ["selectedDestination", "selectedRegions", "selected_places",
    "compulsory_places", "ayan_selected_places", "ayan_preferences",
    "trip_preferences", "trip_result", "visited"];
  if (performance.getEntriesByType("navigation")[0]?.type === "reload") {
    for (const key of keys) {
      try { localStorage.removeItem(key); } catch (error) {}
      try { sessionStorage.removeItem(key); } catch (error) {}
    }
    sessionStorage.setItem("planningReset", String(Date.now()));
  }
  const resetVersion = sessionStorage.getItem("planningReset");
  window.addEventListener("pageshow", event => {
    // Do not revive an old, cached page after the trip has been reset.
    if (event.persisted && resetVersion !== sessionStorage.getItem("planningReset")) {
      location.replace(location.href);
    }
  });
})();
