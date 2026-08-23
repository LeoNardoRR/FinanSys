const STORAGE_KEY = "finansys-pages-preview-v1";
const seed = [
  {id: 1, description: "Salário", amount: 6800, kind: "income", date: "2026-08-05"},
  {id: 2, description: "Supermercado", amount: 438.72, kind: "expense", date: "2026-08-21"},
  {id: 3, description: "Academia", amount: 129.9, kind: "expense", date: "2026-08-19"},
  {id: 4, description: "Internet", amount: 119.9, kind: "expense", date: "2026-08-16"}
];
let entries = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null") || seed;
let kind = "expense";
const money = new Intl.NumberFormat("pt-BR", {style: "currency", currency: "BRL"});
const titles = {home: "Visão geral", transactions: "Movimentações", cards: "Cartões", goals: "Metas"};
const dialog = document.querySelector("#entry-dialog");
const form = document.querySelector("#entry-form");

function renderList(target, items) {
  target.innerHTML = items.length ? items.map((entry) => `<article class="transaction ${entry.kind}"><span class="transaction-icon">${entry.kind === "income" ? "↑" : "↓"}</span><span><strong>${escapeHtml(entry.description)}</strong><small>${new Date(`${entry.date}T12:00:00`).toLocaleDateString("pt-BR")}</small></span><strong class="amount">${entry.kind === "income" ? "+" : "−"}${money.format(entry.amount)}</strong></article>`).join("") : '<p class="empty">Ainda não há lançamentos.</p>';
}
function render() {
  const income = entries.filter((x) => x.kind === "income").reduce((sum, x) => sum + x.amount, 0);
  const expenses = entries.filter((x) => x.kind === "expense").reduce((sum, x) => sum + x.amount, 0);
  document.querySelector("#balance").textContent = money.format(income - expenses);
  document.querySelector("#income").textContent = `↑ ${money.format(income)}`;
  document.querySelector("#expenses").textContent = `↓ ${money.format(expenses)}`;
  const ordered = [...entries].sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id);
  renderList(document.querySelector("#recent-list"), ordered.slice(0, 4));
  renderList(document.querySelector("#transaction-list"), ordered);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}
function openEntry(nextKind) {
  kind = nextKind;
  form.reset();
  document.querySelector("#date").value = new Date().toISOString().slice(0, 10);
  document.querySelectorAll("[data-kind]").forEach((button) => button.classList.toggle("active", button.dataset.kind === kind));
  dialog.showModal();
}
function selectTab(tab) {
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active", view.dataset.view === tab));
  document.querySelectorAll(".tab-bar [data-tab]").forEach((button) => button.classList.toggle("active", button.dataset.tab === tab));
  document.querySelector("#page-title").textContent = titles[tab];
  window.scrollTo({top: 0, behavior: "smooth"});
}
document.querySelectorAll("[data-tab]").forEach((button) => button.addEventListener("click", () => selectTab(button.dataset.tab)));
document.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => openEntry(button.dataset.action)));
document.querySelectorAll("[data-kind]").forEach((button) => button.addEventListener("click", () => { kind = button.dataset.kind; document.querySelectorAll("[data-kind]").forEach((item) => item.classList.toggle("active", item === button)); }));
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const description = document.querySelector("#description").value.trim();
  const amount = Number(document.querySelector("#amount").value.replace(".", "").replace(",", "."));
  const date = document.querySelector("#date").value;
  if (!description || !Number.isFinite(amount) || amount <= 0 || !date) return document.querySelector("#form-error").textContent = "Revise a descrição, o valor e a data.";
  entries.push({id: Date.now(), description, amount, date, kind});
  render(); dialog.close(); selectTab("home");
});
function escapeHtml(value) { const node = document.createElement("span"); node.textContent = value; return node.innerHTML; }
if ("serviceWorker" in navigator) window.addEventListener("load", () => navigator.serviceWorker.register("service-worker.js"));
render();
