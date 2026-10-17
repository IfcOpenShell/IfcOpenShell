// Every code block switches language on its own. The last picked language, or
// ?lang= in the address, is only the initial tab of the blocks when a page
// loads, so picking a tab never changes the other blocks on the page.
(() => {
  const storageKey = "ifcopenshell-docs-language";
  const languages = ["cpp", "python", "js"];

  const languageOf = (label) =>
    languages.find((language) => label.classList.contains(`ios-lang-${language}`));

  function preferredLanguage() {
    const requested = new URLSearchParams(window.location.search).get("lang");
    if (languages.includes(requested)) {
      localStorage.setItem(storageKey, requested);
      return requested;
    }
    return localStorage.getItem(storageKey);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const language = preferredLanguage();
    if (language) {
      const selector = `.ios-snippet > label.ios-lang-${language}:not(.ios-lang-missing)`;
      for (const label of document.querySelectorAll(selector)) {
        label.previousElementSibling.checked = true;
      }
    }
  });

  document.addEventListener("click", (event) => {
    const label = event.target.closest(".ios-snippet > label.ios-lang");
    if (label && !label.classList.contains("ios-lang-missing")) {
      localStorage.setItem(storageKey, languageOf(label));
    }
  });
})();
