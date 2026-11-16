const activityViewer = document.getElementById("activityViewer");
const activityImage = document.getElementById("activityFullImage");
const activityTitle = document.getElementById("activityTitle");

document.querySelectorAll(".activity-card").forEach(card => {
  card.addEventListener("click", () => {
    const photo = card.querySelector("img");
    activityImage.src = photo.src;
    activityImage.alt = photo.alt;
    activityTitle.textContent = photo.alt;
    activityViewer.showModal();
  });
});
document.getElementById("activityClose").addEventListener("click", () => activityViewer.close());
activityViewer.addEventListener("click", event => {
  const bounds = activityViewer.getBoundingClientRect();
  if (event.target === activityViewer && (event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom)) activityViewer.close();
});
