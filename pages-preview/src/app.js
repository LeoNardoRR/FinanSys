import {createClient} from "@supabase/supabase-js";

const SUPABASE_URL = "https://jrbemrqahgnabqrrvhqb.supabase.co";
const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_NTKml0Ke4rNl4tq3i1bN0w_CWljRZZ4";
const APP_URL = "https://leonardorr.github.io/FinanSys/";
const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
  auth: {persistSession: true, autoRefreshToken: true, detectSessionInUrl: true},
});

const state = {user: null, transactions: [], categories: [], cards: [], goals: [], subscriptions: [], kind: "expense", datePreset: "all"};
const AUTH_TIMEOUT_MS = 15000;
let authAttempt = 0;
const money = new Intl.NumberFormat("pt-BR", {style: "currency", currency: "BRL"});
const titles = {home: "Visão geral", transactions: "Movimentações", cards: "Cartões", planning: "Planejamento"};
const authCopy = {
  login: ["Entre na sua conta", "Acesse seu panorama financeiro com segurança."],
  signup: ["Crie sua conta", "Comece gratuitamente e sincronize seus dados entre dispositivos."],
  recovery: ["Recupere seu acesso", "Enviaremos um link seguro para o e-mail cadastrado."],
  "new-password": ["Defina uma nova senha", "Use pelo menos 8 caracteres para proteger sua conta."],
};
const defaults = [
  ["Salário", "income", "#16a34a"], ["Investimentos", "income", "#0d9488"],
  ["Moradia", "expense", "#2563eb"], ["Alimentação", "expense", "#dc2626"],
  ["Transporte", "expense", "#d97706"], ["Saúde", "expense", "#7c3aed"],
  ["Lazer", "expense", "#db2777"], ["Educação", "expense", "#0891b2"],
  ["Assinaturas", "expense", "#4f46e5"], ["Outros", "expense", "#64748b"],
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const escapeHtml = (value = "") => { const node = document.createElement("span"); node.textContent = String(value); return node.innerHTML; };
const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const valueOf = (selector) => $(selector).value.trim();
const optionalInt = (selector) => valueOf(selector) ? Number(valueOf(selector)) : null;

function isoDate(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function offsetDate(days) { const date = new Date(); date.setDate(date.getDate() + days); return isoDate(date); }
function monthBoundary(position = "end") { const now = new Date(); return isoDate(position === "start" ? new Date(now.getFullYear(), now.getMonth(), 1) : new Date(now.getFullYear(), now.getMonth() + 1, 0)); }
function signedAmount(item) { return (item.kind === "income" ? 1 : -1) * Number(item.amount); }

function parseMoney(value) {
  const normalized = String(value).trim().replace(/\s/g, "");
  const parsed = Number(normalized.includes(",") ? normalized.replace(/\./g, "").replace(",", ".") : normalized);
  return Number.isFinite(parsed) ? Math.round(parsed * 100) / 100 : NaN;
}

function friendlyError(error) {
  const message = error?.message || String(error || "Erro inesperado.");
  if (error?.code === "invalid_credentials" || /invalid login credentials/i.test(message)) return "E-mail ou senha incorretos. Confira os dados ou recupere sua senha.";
  if (error?.code === "email_not_confirmed" || /email not confirmed/i.test(message)) return "Seu e-mail ainda não foi confirmado. Abra o link enviado no cadastro.";
  if (error?.code === "user_already_exists" || /user already registered/i.test(message)) return "Este e-mail já possui uma conta. Entre ou recupere sua senha.";
  if (/password/i.test(message) && /least/i.test(message)) return "A senha precisa ter pelo menos 8 caracteres.";
  if (/only request this after/i.test(message)) {
    const seconds = message.match(/after (\d+) seconds?/i)?.[1] || "alguns";
    return `O e-mail já foi solicitado. Aguarde ${seconds} segundos antes de tentar novamente.`;
  }
  if (/rate limit|too many/i.test(message)) return "Muitas tentativas. Aguarde alguns minutos.";
  if (error?.code === "auth_timeout" || /tempo limite/i.test(message)) return "A conexão demorou demais. Confira sua internet e tente novamente.";
  if (/failed to fetch|network/i.test(message)) return "Sem conexão com o servidor. Verifique sua internet.";
  return "Não foi possível concluir agora. Tente novamente em instantes.";
}

function toast(message) {
  const element = $("#toast"); element.textContent = message; element.hidden = false;
  clearTimeout(toast.timer); toast.timer = setTimeout(() => { element.hidden = true; }, 3500);
}

function setAuthMessage(message = "", success = false, pending = false) {
  const element = $("#auth-message"); element.textContent = message; element.classList.toggle("success", success); element.classList.toggle("pending", pending); element.classList.toggle("visible", Boolean(message));
  if (message) element.scrollIntoView({block: "nearest", behavior: "smooth"});
}

function setBusy(form, busy) {
  form.querySelectorAll("button,input,select,textarea").forEach((control) => { control.disabled = busy; });
  form.toggleAttribute("aria-busy", busy);
}

function validateAuthForm(form) {
  const empty = [...form.querySelectorAll("[required]")].find((input) => !input.value.trim());
  if (empty) { setAuthMessage("Preencha todos os campos para continuar."); empty.focus(); return false; }
  const invalidEmail = [...form.querySelectorAll('input[type="email"]')].find((input) => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim()));
  if (invalidEmail) { setAuthMessage("Informe um e-mail válido."); invalidEmail.focus(); return false; }
  const shortPassword = [...form.querySelectorAll('input[autocomplete="current-password"],input[autocomplete="new-password"]')].find((input) => input.value.length < 8);
  if (shortPassword) { setAuthMessage("A senha precisa ter pelo menos 8 caracteres."); shortPassword.focus(); return false; }
  const invalid = [...form.elements].find((control) => control.willValidate && !control.checkValidity());
  if (!invalid) return true;
  const message = invalid.validity.valueMissing ? "Preencha todos os campos para continuar." : invalid.validity.typeMismatch ? "Informe um e-mail válido." : invalid.validity.tooShort ? "A senha precisa ter pelo menos 8 caracteres." : "Revise os dados informados.";
  setAuthMessage(message); invalid.focus(); return false;
}

function withTimeout(promise) {
  let timer;
  const timeout = new Promise((_, reject) => { timer = setTimeout(() => reject(Object.assign(new Error("Tempo limite de autenticação."), {code: "auth_timeout"})), AUTH_TIMEOUT_MS); });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

async function runAuth(form, busyLabel, action) {
  if (!validateAuthForm(form)) return null;
  const attempt = ++authAttempt;
  const submit = form.querySelector("button[type='submit']"); const label = submit.querySelector("span"); const original = label.textContent;
  document.activeElement?.blur(); setBusy(form, true); submit.classList.add("loading"); label.textContent = busyLabel; setAuthMessage("Conectando com segurança…", false, true);
  try {
    const result = await withTimeout(action());
    if (result.error) throw result.error;
    if (attempt !== authAttempt) return null;
    return result.data;
  } catch (error) {
    if (attempt !== authAttempt) return null;
    console.error("Falha de autenticação", {code: error?.code, status: error?.status});
    setAuthMessage(friendlyError(error)); return null;
  } finally {
    setBusy(form, false); submit.classList.remove("loading"); label.textContent = original;
  }
}

function showAuth(mode = "login") {
  authAttempt += 1;
  $("#auth-screen").hidden = false; $("#app-shell").hidden = true; $("#tab-bar").hidden = true; $("#loading-screen").hidden = true;
  $$(".auth-form").forEach((form) => { form.hidden = form.id !== `${mode}-form`; });
  $$("[data-auth-tab]").forEach((button) => button.classList.toggle("active", button.dataset.authTab === mode));
  $("#auth-tabs").hidden = !["login", "signup"].includes(mode); [$("#auth-title").textContent, $("#auth-description").textContent] = authCopy[mode] || authCopy.login;
  setAuthMessage();
}

async function showApp(user) {
  state.user = user; $("#auth-screen").hidden = true; $("#loading-screen").hidden = false;
  $("#account-email").textContent = user.email || "Conta FinanSys";
  $("#account-button").textContent = (user.email || "F").charAt(0).toUpperCase();
  $("#welcome-copy").textContent = `Olá, ${(user.email || "você").split("@")[0]}`;
  try {
    await seedCategories();
    await loadData();
    $("#app-shell").hidden = false; $("#tab-bar").hidden = false; $("#loading-screen").hidden = true;
  } catch (error) {
    $("#loading-screen").hidden = true; showAuth("login"); setAuthMessage(friendlyError(error));
  }
}

async function seedCategories() {
  const {error} = await supabase.from("categories").upsert(
    defaults.map(([name, kind, color]) => ({user_id: state.user.id, name, kind, color})),
    {onConflict: "user_id,name", ignoreDuplicates: true},
  );
  if (error) throw error;
}

async function loadData() {
  const [transactions, categories, cards, goals, subscriptions] = await Promise.all([
    supabase.from("transactions").select("*").order("occurred_on", {ascending: false}).order("created_at", {ascending: false}).limit(1000),
    supabase.from("categories").select("*").eq("active", true).order("name"),
    supabase.from("cards").select("*").eq("active", true).order("name"),
    supabase.from("goals").select("*").eq("active", true).order("created_at", {ascending: false}),
    supabase.from("subscriptions").select("*").eq("active", true).order("billing_day"),
  ]);
  for (const result of [transactions, categories, cards, goals, subscriptions]) if (result.error) throw result.error;
  state.transactions = transactions.data; state.categories = categories.data; state.cards = cards.data; state.goals = goals.data; state.subscriptions = subscriptions.data;
  render();
}

function render() {
  renderDashboard(); renderForecast(); renderTransactions(); renderCards(); renderGoals(); renderSubscriptions(); updateSelects();
}

function renderDashboard() {
  const now = new Date(); const prefix = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const month = state.transactions.filter((item) => item.occurred_on.startsWith(prefix));
  const income = month.filter((item) => item.kind === "income").reduce((sum, item) => sum + Number(item.amount), 0);
  const expenses = month.filter((item) => item.kind === "expense").reduce((sum, item) => sum + Number(item.amount), 0);
  $("#balance").textContent = money.format(income - expenses); $("#income").textContent = money.format(income); $("#expenses").textContent = money.format(expenses);
  renderTransactionList($("#recent-list"), state.transactions.slice(0, 5), false);
}

function renderForecast() {
  const target = valueOf("#forecast-date") || isoDate();
  const throughDate = state.transactions.filter((item) => item.occurred_on <= target);
  const onDate = state.transactions.filter((item) => item.occurred_on === target);
  const balance = throughDate.reduce((sum, item) => sum + signedAmount(item), 0);
  const dayIncome = onDate.filter((item) => item.kind === "income").reduce((sum, item) => sum + Number(item.amount), 0);
  const dayExpenses = onDate.filter((item) => item.kind === "expense").reduce((sum, item) => sum + Number(item.amount), 0);
  const balanceElement = $("#forecast-balance");
  balanceElement.textContent = money.format(balance); balanceElement.classList.toggle("negative", balance < 0);
  $("#forecast-day-income").textContent = money.format(dayIncome); $("#forecast-day-expense").textContent = money.format(dayExpenses);
  const futureCount = throughDate.filter((item) => item.occurred_on > isoDate()).length;
  $("#forecast-caption").textContent = target >= isoDate() ? `${futureCount} lançamento${futureCount === 1 ? " futuro" : "s futuros"} considerado${futureCount === 1 ? "" : "s"} até ${formatDate(target)}.` : `Resultado acumulado até ${formatDate(target)}.`;
  const result = $(".forecast-result"); result.classList.remove("pulse"); requestAnimationFrame(() => result.classList.add("pulse"));
}

function renderTransactions() {
  const query = valueOf("#transaction-search").toLocaleLowerCase("pt-BR");
  const start = valueOf("#filter-date-start"); const end = valueOf("#filter-date-end");
  const validRange = !start || !end || start <= end;
  const items = validRange ? state.transactions.filter((item) => (!query || item.description.toLocaleLowerCase("pt-BR").includes(query)) && (!start || item.occurred_on >= start) && (!end || item.occurred_on <= end)) : [];
  const income = items.filter((item) => item.kind === "income").reduce((sum, item) => sum + Number(item.amount), 0);
  const expenses = items.filter((item) => item.kind === "expense").reduce((sum, item) => sum + Number(item.amount), 0);
  $("#period-count").textContent = validRange ? `${items.length} LANÇAMENTO${items.length === 1 ? "" : "S"}` : "AJUSTE AS DATAS";
  $("#period-balance").textContent = money.format(income - expenses); $("#period-income").textContent = money.format(income); $("#period-expenses").textContent = money.format(expenses);
  renderTransactionList($("#transaction-list"), items, true);
}

function renderTransactionList(target, items, allowDelete) {
  const categoryNames = Object.fromEntries(state.categories.map((item) => [item.id, item.name]));
  target.innerHTML = items.length ? items.map((item) => {
    const suffix = item.installments_total ? ` · ${item.installment_number}/${item.installments_total}` : "";
    return `<article class="transaction ${item.kind}"><span class="transaction-icon">${icon(item.kind)}</span><span><strong>${escapeHtml(item.description)}</strong><small>${formatDate(item.occurred_on)} · ${escapeHtml(categoryNames[item.category_id] || "Sem categoria")}${suffix}</small></span><span><strong class="amount">${item.kind === "income" ? "+" : "−"}${money.format(Number(item.amount))}</strong>${allowDelete ? `<button class="delete" type="button" data-delete-transaction="${item.id}">Excluir</button>` : ""}</span></article>`;
  }).join("") : '<p class="empty"><strong>Nenhum lançamento</strong>Use o botão + para começar.</p>';
}

function renderCards() {
  $("#cards-list").innerHTML = state.cards.length ? state.cards.map((card) => {
    const used = state.transactions.filter((item) => item.card_id === card.id && item.kind === "expense").reduce((sum, item) => sum + Number(item.amount), 0);
    const limit = Number(card.credit_limit); const percent = limit ? Math.min(used / limit * 100, 100) : 0;
    return `<article class="data-card credit-visual"><div class="data-card-head"><div><h3>${escapeHtml(card.name)}</h3><p>${escapeHtml(card.brand || "Cartão de crédito")}</p></div><button class="delete-card" type="button" data-delete-record="cards:${card.id}" aria-label="Excluir ${escapeHtml(card.name)}">×</button></div><strong>${money.format(used)} utilizados</strong><div class="progress"><i style="width:${percent}%"></i></div><div class="card-meta"><span>Limite ${money.format(limit)}</span><span>Fecha dia ${card.closing_day || "—"} · vence ${card.due_day || "—"}</span></div></article>`;
  }).join("") : '<p class="empty panel"><strong>Nenhum cartão</strong>Cadastre um cartão para acompanhar o limite.</p>';
}

function renderGoals() {
  $("#goals-list").innerHTML = state.goals.length ? state.goals.map((goal) => {
    const target = Number(goal.target_amount); const current = Number(goal.current_amount); const percent = target ? Math.min(current / target * 100, 100) : 0;
    return `<article class="data-card"><div class="data-card-head"><div><h3>${escapeHtml(goal.name)}</h3><p>${goal.target_date ? `Até ${formatDate(goal.target_date)}` : "Sem data limite"}</p></div><button class="delete-card" type="button" data-delete-record="goals:${goal.id}" aria-label="Excluir ${escapeHtml(goal.name)}">×</button></div><strong>${money.format(current)} de ${money.format(target)}</strong><div class="progress"><i style="width:${percent}%"></i></div><p>${percent.toFixed(0)}% concluído · aporte de ${money.format(Number(goal.monthly_contribution))}/mês</p><div class="goal-update"><input type="text" inputmode="decimal" value="${current.toFixed(2).replace(".", ",")}" aria-label="Valor atual de ${escapeHtml(goal.name)}" data-goal-value="${goal.id}"><button type="button" data-update-goal="${goal.id}">Atualizar</button></div></article>`;
  }).join("") : '<p class="empty panel"><strong>Nenhuma meta</strong>Crie seu primeiro objetivo financeiro.</p>';
}

function renderSubscriptions() {
  $("#subscriptions-list").innerHTML = state.subscriptions.length ? state.subscriptions.map((item) => `<article class="data-card"><div class="data-card-head"><div><h3>${escapeHtml(item.name)}</h3><p>Cobrança todo dia ${item.billing_day}</p></div><button class="delete-card" type="button" data-delete-record="subscriptions:${item.id}" aria-label="Excluir ${escapeHtml(item.name)}">×</button></div><strong>${money.format(Number(item.amount))}/mês</strong></article>`).join("") : '<p class="empty panel"><strong>Nenhuma assinatura</strong>Adicione custos recorrentes para acompanhar o total mensal.</p>';
}

function updateSelects() {
  const category = $("#transaction-category"); const previousCategory = category.value;
  category.innerHTML = '<option value="">Sem categoria</option>' + state.categories.filter((item) => item.kind === state.kind).map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  if ([...category.options].some((option) => option.value === previousCategory)) category.value = previousCategory;
  const cards = '<option value="">Não se aplica</option>' + state.cards.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  $("#transaction-card").innerHTML = cards; $("#subscription-card").innerHTML = cards;
}

function formatDate(value) { return new Date(`${value}T12:00:00`).toLocaleDateString("pt-BR"); }
function addMonths(dateString, months) { const [year, month, day] = dateString.split("-").map(Number); const date = new Date(Date.UTC(year, month - 1 + months, 1)); const last = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + 1, 0)).getUTCDate(); return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}-${String(Math.min(day, last)).padStart(2, "0")}`; }

function selectTab(tab) {
  $$(".view").forEach((view) => view.classList.toggle("active", view.dataset.view === tab));
  $$(".tab-bar [data-tab]").forEach((button) => { const active = button.dataset.tab === tab; button.classList.toggle("active", active); if (active) button.setAttribute("aria-current", "page"); else button.removeAttribute("aria-current"); });
  $("#page-title").textContent = titles[tab]; window.scrollTo({top: 0, behavior: "smooth"});
}

function setDatePreset(preset) {
  const start = $("#filter-date-start"); const end = $("#filter-date-end"); const today = isoDate();
  if (preset === "today") { start.value = today; end.value = today; }
  if (preset === "7") { start.value = today; end.value = offsetDate(6); }
  if (preset === "month") { start.value = monthBoundary("start"); end.value = monthBoundary("end"); }
  if (preset === "all") { start.value = ""; end.value = ""; }
  state.datePreset = preset; $$("[data-date-preset]").forEach((button) => button.classList.toggle("active", button.dataset.datePreset === preset)); renderTransactions();
}

function setForecastPreset(preset) {
  $("#forecast-date").value = preset === "month" ? monthBoundary("end") : offsetDate(Number(preset)); renderForecast();
}

function openTransaction(kind) {
  state.kind = kind; const form = $("#transaction-form"); form.reset(); $("#transaction-date").value = new Date().toISOString().slice(0, 10); $("#transaction-installments").value = "1"; $("#transaction-error").textContent = "";
  $$("[data-kind]").forEach((button) => button.classList.toggle("active", button.dataset.kind === kind)); updateSelects(); $("#transaction-dialog").showModal();
}

async function saveTransaction(event) {
  event.preventDefault(); const form = event.currentTarget; const description = valueOf("#transaction-description"); const total = parseMoney(valueOf("#transaction-amount")); const installments = Number(valueOf("#transaction-installments"));
  if (!description || !Number.isFinite(total) || total <= 0 || !Number.isInteger(installments) || installments < 1 || installments > 120) return $("#transaction-error").textContent = "Revise a descrição, o valor e as parcelas.";
  setBusy(form, true); $("#transaction-error").textContent = "";
  const totalCents = Math.round(total * 100); const base = Math.floor(totalCents / installments); const remainder = totalCents - base * installments; const group = installments > 1 ? crypto.randomUUID() : null;
  const rows = Array.from({length: installments}, (_, index) => ({
    user_id: state.user.id, description: installments > 1 ? `${description} (${index + 1}/${installments})` : description,
    amount: (base + (index === installments - 1 ? remainder : 0)) / 100, occurred_on: addMonths(valueOf("#transaction-date"), index), kind: state.kind,
    category_id: valueOf("#transaction-category") || null, card_id: valueOf("#transaction-card") || null, notes: valueOf("#transaction-notes") || null,
    installment_group: group, installment_number: group ? index + 1 : null, installments_total: group ? installments : null,
  }));
  const {error} = await supabase.from("transactions").insert(rows); setBusy(form, false);
  if (error) return $("#transaction-error").textContent = friendlyError(error);
  $("#transaction-dialog").close(); await loadData(); toast("Lançamento salvo e sincronizado.");
}

async function saveCard(event) {
  event.preventDefault(); const form = event.currentTarget; const limit = parseMoney(valueOf("#card-limit"));
  if (!valueOf("#card-name") || !Number.isFinite(limit) || limit < 0) return $("#card-error").textContent = "Revise o nome e o limite.";
  setBusy(form, true); const {error} = await supabase.from("cards").insert({user_id: state.user.id, name: valueOf("#card-name"), brand: valueOf("#card-brand") || null, credit_limit: limit, closing_day: optionalInt("#card-closing"), due_day: optionalInt("#card-due")}); setBusy(form, false);
  if (error) return $("#card-error").textContent = friendlyError(error); $("#card-dialog").close(); form.reset(); await loadData(); toast("Cartão salvo.");
}

async function saveGoal(event) {
  event.preventDefault(); const form = event.currentTarget; const target = parseMoney(valueOf("#goal-target")); const current = parseMoney(valueOf("#goal-current")); const monthly = parseMoney(valueOf("#goal-monthly"));
  if (!valueOf("#goal-name") || !Number.isFinite(target) || target <= 0 || current < 0 || monthly < 0) return $("#goal-error").textContent = "Revise o nome e os valores.";
  setBusy(form, true); const {error} = await supabase.from("goals").insert({user_id: state.user.id, name: valueOf("#goal-name"), target_amount: target, current_amount: current, monthly_contribution: monthly, target_date: valueOf("#goal-date") || null}); setBusy(form, false);
  if (error) return $("#goal-error").textContent = friendlyError(error); $("#goal-dialog").close(); form.reset(); await loadData(); toast("Meta salva.");
}

async function saveSubscription(event) {
  event.preventDefault(); const form = event.currentTarget; const amount = parseMoney(valueOf("#subscription-amount")); const day = Number(valueOf("#subscription-day"));
  if (!valueOf("#subscription-name") || !Number.isFinite(amount) || amount <= 0 || !Number.isInteger(day) || day < 1 || day > 31) return $("#subscription-error").textContent = "Revise o nome, o valor e o dia.";
  setBusy(form, true); const {error} = await supabase.from("subscriptions").insert({user_id: state.user.id, name: valueOf("#subscription-name"), amount, billing_day: day, card_id: valueOf("#subscription-card") || null}); setBusy(form, false);
  if (error) return $("#subscription-error").textContent = friendlyError(error); $("#subscription-dialog").close(); form.reset(); await loadData(); toast("Assinatura salva.");
}

async function updateGoal(id) {
  const input = $(`[data-goal-value="${id}"]`); const current = parseMoney(input.value);
  if (!Number.isFinite(current) || current < 0) return toast("Informe um valor válido.");
  const {error} = await supabase.from("goals").update({current_amount: current}).eq("id", id); if (error) return toast(friendlyError(error)); await loadData(); toast("Progresso atualizado.");
}

async function deleteTransaction(id) {
  if (!confirm("Excluir este lançamento? Esta ação não pode ser desfeita.")) return;
  const {error} = await supabase.from("transactions").delete().eq("id", id); if (error) return toast(friendlyError(error)); await loadData(); toast("Lançamento excluído.");
}

async function deleteRecord(table, id) {
  const labels = {cards: "cartão", goals: "meta", subscriptions: "assinatura"};
  if (!confirm(`Excluir ${labels[table]}? Esta ação não pode ser desfeita.`)) return;
  const {error} = await supabase.from(table).delete().eq("id", id); if (error) return toast(error.code === "23503" ? "Este registro está sendo usado por outro lançamento." : friendlyError(error)); await loadData(); toast("Registro excluído.");
}

function registerEvents() {
  $$("[data-auth-tab]").forEach((button) => button.addEventListener("click", () => showAuth(button.dataset.authTab)));
  $("#forgot-password").addEventListener("click", () => { $("#recovery-email").value = valueOf("#login-email"); showAuth("recovery"); });
  $$("[data-password-toggle]").forEach((button) => button.addEventListener("click", () => {
    const input = $(`#${button.dataset.passwordToggle}`); const visible = input.type === "text"; input.type = visible ? "password" : "text";
    button.setAttribute("aria-label", visible ? "Mostrar senha" : "Ocultar senha"); button.querySelector("use").setAttribute("href", visible ? "#i-eye" : "#i-eye-off"); input.focus();
  }));
  $("#login-form").addEventListener("submit", async (event) => {
    event.preventDefault(); const data = await runAuth(event.currentTarget, "Entrando…", () => supabase.auth.signInWithPassword({email: valueOf("#login-email"), password: valueOf("#login-password")}));
    if (data?.session) setAuthMessage("Login confirmado. Carregando seus dados…", true, true);
  });
  $("#signup-form").addEventListener("submit", async (event) => {
    event.preventDefault(); if (!validateAuthForm(event.currentTarget)) return;
    const password = valueOf("#signup-password");
    if (password !== valueOf("#signup-password-confirm")) return setAuthMessage("As senhas não coincidem.");
    const data = await runAuth(event.currentTarget, "Criando conta…", () => supabase.auth.signUp({email: valueOf("#signup-email"), password, options: {emailRedirectTo: APP_URL}}));
    if (!data) return;
    if (!data.session) {
      const message = "Cadastro recebido. Abra o e-mail de confirmação para liberar sua conta.";
      setAuthMessage(message, true); toast(message);
    }
  });
  $("#recovery-form").addEventListener("submit", async (event) => {
    event.preventDefault(); const data = await runAuth(event.currentTarget, "Enviando…", () => supabase.auth.resetPasswordForEmail(valueOf("#recovery-email"), {redirectTo: APP_URL}));
    if (data !== null) setAuthMessage("Se o e-mail estiver cadastrado, você receberá um link de recuperação.", true);
  });
  $("#new-password-form").addEventListener("submit", async (event) => {
    event.preventDefault(); const data = await runAuth(event.currentTarget, "Atualizando…", () => supabase.auth.updateUser({password: valueOf("#new-password")}));
    if (data) { setAuthMessage("Senha atualizada. Você já pode continuar.", true); toast("Senha atualizada."); }
  });
  $("#logout-button").addEventListener("click", async () => { await supabase.auth.signOut(); });
  $("#account-button").addEventListener("click", () => { $("#account-menu").hidden = !$("#account-menu").hidden; });
  $$("[data-tab]").forEach((button) => button.addEventListener("click", () => selectTab(button.dataset.tab)));
  $$("[data-action]").forEach((button) => button.addEventListener("click", () => openTransaction(button.dataset.action)));
  $$("[data-open-dialog]").forEach((button) => button.addEventListener("click", () => { const dialog = $(`#${button.dataset.openDialog}`); dialog.querySelector("form").reset(); dialog.querySelector(".form-error").textContent = ""; updateSelects(); dialog.showModal(); }));
  $$(".close-dialog").forEach((button) => button.addEventListener("click", () => button.closest("dialog").close()));
  $$("[data-kind]").forEach((button) => button.addEventListener("click", () => { state.kind = button.dataset.kind; $$("[data-kind]").forEach((item) => item.classList.toggle("active", item === button)); updateSelects(); }));
  $("#transaction-form").addEventListener("submit", saveTransaction); $("#card-form").addEventListener("submit", saveCard); $("#goal-form").addEventListener("submit", saveGoal); $("#subscription-form").addEventListener("submit", saveSubscription);
  $("#transaction-search").addEventListener("input", renderTransactions);
  $("#forecast-date").addEventListener("change", renderForecast);
  $$("[data-forecast-preset]").forEach((button) => button.addEventListener("click", () => setForecastPreset(button.dataset.forecastPreset)));
  $$("[data-date-preset]").forEach((button) => button.addEventListener("click", () => setDatePreset(button.dataset.datePreset)));
  [$("#filter-date-start"), $("#filter-date-end")].forEach((input) => input.addEventListener("change", () => { state.datePreset = "custom"; $$("[data-date-preset]").forEach((button) => button.classList.remove("active")); $("#filter-date-start").max = valueOf("#filter-date-end") || "9999-12-31"; $("#filter-date-end").min = valueOf("#filter-date-start"); renderTransactions(); }));
  document.addEventListener("click", (event) => { const transaction = event.target.closest("[data-delete-transaction]"); if (transaction) deleteTransaction(transaction.dataset.deleteTransaction); const record = event.target.closest("[data-delete-record]"); if (record) { const [table, id] = record.dataset.deleteRecord.split(":"); deleteRecord(table, id); } const goal = event.target.closest("[data-update-goal]"); if (goal) updateGoal(goal.dataset.updateGoal); });
  document.addEventListener("click", (event) => { if (!event.target.closest("#account-button") && !event.target.closest("#account-menu")) $("#account-menu").hidden = true; });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") $("#account-menu").hidden = true; });
  window.addEventListener("offline", updateNetwork); window.addEventListener("online", () => { updateNetwork(); if (state.user) loadData(); }); updateNetwork();
}

function updateNetwork() { $("#network-banner").hidden = navigator.onLine; }

let installPrompt = null;
window.addEventListener("beforeinstallprompt", (event) => { event.preventDefault(); installPrompt = event; $("#install-app").hidden = false; });
$("#install-app").addEventListener("click", async () => { if (!installPrompt) return; await installPrompt.prompt(); installPrompt = null; $("#install-app").hidden = true; });
if ("serviceWorker" in navigator) window.addEventListener("load", () => navigator.serviceWorker.register("service-worker.js"));

$("#forecast-date").value = monthBoundary("end");
registerEvents();
supabase.auth.onAuthStateChange((event, session) => {
  queueMicrotask(() => {
    if (event === "PASSWORD_RECOVERY") return showAuth("new-password");
    if (session?.user) showApp(session.user); else showAuth("login");
  });
});
