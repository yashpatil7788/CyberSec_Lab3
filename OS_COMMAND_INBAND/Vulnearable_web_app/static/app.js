"use strict";
for (const button of document.querySelectorAll("[data-target]")) {
  button.addEventListener("click", () => {
    const input = document.getElementById("target");
    input.value = button.dataset.target;
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
  });
}
