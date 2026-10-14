// Selecting a language tab selects it in every synced tab set on the page, and
// those change height, so keep the clicked tab where it was on the screen.
let anchor = null;

document.addEventListener(
  "click",
  (event) => {
    const label = event.target.closest(".sd-tab-label");
    if (label) anchor = { label, top: label.getBoundingClientRect().top };
  },
  true,
);

// The input of the clicked tab changes after all synced tab sets are switched.
document.addEventListener("change", (event) => {
  if (!anchor || event.target !== anchor.label.previousElementSibling) return;
  const { label, top } = anchor;
  anchor = null;
  // Furo enables smooth scrolling, which would animate the correction.
  window.scrollBy({ top: label.getBoundingClientRect().top - top, behavior: "instant" });
});
