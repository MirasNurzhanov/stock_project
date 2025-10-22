document.addEventListener("DOMContentLoaded", () => {
  const balanceEl = document.querySelector(".balance");

  document.querySelectorAll(".buy-form").forEach(form => {
    form.addEventListener("submit", (e) => {
      e.preventDefault(); // stop immediate navigation

      const btn = form.querySelector("button[type='submit']");
      const price = parseFloat(btn.dataset.price);

      // Visual update
      const current = parseFloat(balanceEl.innerText);
      balanceEl.innerText = (current - price).toFixed(2);

      // Then proceed to server (tiny delay so user sees it)
      setTimeout(() => form.submit(), 300);
    });
  });
});


