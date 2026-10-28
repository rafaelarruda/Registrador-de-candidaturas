const PAGE_SIZE = 20;
const statusNames = {
  enviado: "Enviada",
  entrevista: "Entrevista",
  oferta: "Oferta",
  recusado: "Encerrada",
};

const elements = {
  total: document.querySelector("#metric-total"),
  counts: Object.fromEntries(
    Object.keys(statusNames).map((status) => [status, document.querySelector(`#metric-${status}`)]),
  ),
  search: document.querySelector("#company-search"),
  status: document.querySelector("#status-filter"),
  body: document.querySelector("#applications-body"),
  empty: document.querySelector("#empty-state"),
  emptyTitle: document.querySelector("#empty-title"),
  emptyCopy: document.querySelector("#empty-copy"),
  resultCount: document.querySelector("#result-count"),
  pageStatus: document.querySelector("#page-status"),
  pageNumber: document.querySelector("#page-number"),
  previous: document.querySelector("#previous-page"),
  next: document.querySelector("#next-page"),
  notice: document.querySelector("#notice"),
  dialog: document.querySelector("#application-dialog"),
  form: document.querySelector("#application-form"),
  formError: document.querySelector("#form-error"),
  id: document.querySelector("#application-id"),
  company: document.querySelector("#company-input"),
  role: document.querySelector("#role-input"),
  link: document.querySelector("#link-input"),
  salary: document.querySelector("#salary-input"),
  requirements: document.querySelector("#requirements-input"),
  statusInput: document.querySelector("#application-status"),
  date: document.querySelector("#application-date"),
  notes: document.querySelector("#notes-input"),
  save: document.querySelector("#save-application"),
  dialogTitle: document.querySelector("#dialog-title"),
};

let page = 0;
let requestSequence = 0;
let searchTimer;

function showNotice(message) {
  elements.notice.textContent = message;
  elements.notice.hidden = false;
}

function clearNotice() {
  elements.notice.hidden = true;
  elements.notice.textContent = "";
}

async function request(path, options = {}) {
  const { includeTotal = false, ...fetchOptions } = options;
  const response = await fetch(path, {
    ...fetchOptions,
    headers: { "Content-Type": "application/json", ...fetchOptions.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = Array.isArray(body?.detail)
      ? body.detail.map((item) => item.msg).join(" ")
      : body?.detail;
    throw new Error(detail || `Falha ao consultar o servidor (${response.status}).`);
  }
  if (response.status === 204) return null;
  const data = await response.json();
  return includeTotal
    ? { data, total: Number(response.headers.get("X-Total-Count") || data.length) }
    : data;
}

function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" })
    .format(new Date(value))
    .replace(" de ", " ");
}

function safeJobUrl(value) {
  if (!value) return null;
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

function renderRow(application) {
  const row = document.createElement("tr");
  const companyCell = document.createElement("td");
  companyCell.dataset.label = "Empresa";
  const company = document.createElement("div");
  company.className = "company-name";
  const initial = document.createElement("span");
  initial.className = "company-initial";
  initial.setAttribute("aria-hidden", "true");
  initial.textContent = application.empresa.trim().slice(0, 1) || "?";
  const copy = document.createElement("div");
  copy.className = "company-copy";
  const name = document.createElement("strong");
  const jobUrl = safeJobUrl(application.link);
  if (jobUrl) {
    const link = document.createElement("a");
    link.href = jobUrl;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = application.empresa;
    name.append(link);
  } else {
    name.textContent = application.empresa;
  }
  const role = document.createElement("span");
  role.textContent = application.cargo;
  copy.append(name, role);
  if (application.salario) {
    const salary = document.createElement("span");
    salary.className = "job-salary";
    salary.textContent = application.salario;
    copy.append(salary);
  }
  if (application.requisitos) {
    const requirements = document.createElement("span");
    requirements.className = "job-requirements";
    requirements.textContent = `Requisitos: ${application.requisitos}`;
    requirements.title = application.requisitos;
    copy.append(requirements);
  }
  company.append(initial, copy);
  companyCell.append(company);

  const dateCell = document.createElement("td");
  dateCell.dataset.label = "Data";
  dateCell.className = "date-value";
  dateCell.textContent = formatDate(application.data_candidatura);

  const statusCell = document.createElement("td");
  statusCell.dataset.label = "Status";
  const pill = document.createElement("span");
  pill.className = `status-pill status-${application.status}`;
  pill.textContent = statusNames[application.status] || application.status;
  statusCell.append(pill);

  const actionsCell = document.createElement("td");
  actionsCell.dataset.label = "Ações";
  const actions = document.createElement("div");
  actions.className = "row-actions";
  const edit = document.createElement("button");
  edit.type = "button";
  edit.className = "text-action";
  edit.dataset.action = "edit";
  edit.dataset.id = application.id;
  edit.textContent = "Editar";
  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "text-action delete";
  remove.dataset.action = "delete";
  remove.dataset.id = application.id;
  remove.textContent = "Excluir";
  actions.append(edit, remove);
  actionsCell.append(actions);
  row.append(companyCell, dateCell, statusCell, actionsCell);
  return row;
}

function renderApplications(applications, total) {
  elements.body.replaceChildren(...applications.map(renderRow));
  const hasFilters = Boolean(elements.search.value.trim() || elements.status.value);
  elements.empty.hidden = applications.length > 0;
  elements.emptyTitle.textContent = hasFilters
    ? "Nenhuma candidatura encontrada."
    : "Seu próximo capítulo começa com uma candidatura.";
  elements.emptyCopy.textContent = hasFilters
    ? "Ajuste os filtros ou tente outra busca."
    : "Adicione uma vaga para acompanhar cada etapa por aqui.";
  document.querySelector("#empty-create").hidden = hasFilters;
  elements.resultCount.textContent = `${total} ${total === 1 ? "registro" : "registros"}`;
  elements.pageNumber.textContent = String(page + 1);
  elements.pageStatus.textContent = total
    ? `Exibindo ${page * PAGE_SIZE + 1}–${page * PAGE_SIZE + applications.length} de ${total}`
    : "Nenhum registro nesta página";
  elements.previous.disabled = page === 0;
  elements.next.disabled = (page + 1) * PAGE_SIZE >= total;
}

async function loadDashboard() {
  const sequence = ++requestSequence;
  clearNotice();
  const parameters = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(page * PAGE_SIZE) });
  if (elements.search.value.trim()) parameters.set("empresa", elements.search.value.trim());
  if (elements.status.value) parameters.set("status", elements.status.value);

  try {
    const [summary, pageResult] = await Promise.all([
      request("/api/resumo"),
      request(`/api/candidaturas?${parameters.toString()}`, { includeTotal: true }),
    ]);
    if (sequence !== requestSequence) return;
    elements.total.textContent = String(summary.total);
    for (const [status, count] of Object.entries(summary.por_status)) {
      if (elements.counts[status]) elements.counts[status].textContent = String(count);
    }
    renderApplications(pageResult.data, pageResult.total);
  } catch (error) {
    if (sequence === requestSequence) showNotice(`Não foi possível carregar as candidaturas. ${error.message}`);
  }
}

function openDialog(application = null) {
  elements.form.reset();
  elements.formError.hidden = true;
  elements.id.value = application?.id ?? "";
  elements.company.value = application?.empresa ?? "";
  elements.role.value = application?.cargo ?? "";
  elements.link.value = application?.link ?? "";
  elements.salary.value = application?.salario ?? "";
  elements.requirements.value = application?.requisitos ?? "";
  elements.statusInput.value = application?.status ?? "enviado";
  elements.date.value = application?.data_candidatura?.slice(0, 10) ?? "";
  elements.notes.value = application?.anotacoes ?? "";
  elements.dialogTitle.textContent = application ? "Editar candidatura" : "Nova candidatura";
  elements.save.textContent = application ? "Salvar alterações" : "Salvar candidatura";
  elements.dialog.showModal();
  elements.company.focus();
}

function closeDialog() {
  elements.dialog.close();
}

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.save.disabled = true;
  elements.save.textContent = "Salvando...";
  elements.formError.hidden = true;

  const payload = {
    empresa: elements.company.value.trim(),
    cargo: elements.role.value.trim(),
    link: elements.link.value.trim() || null,
    salario: elements.salary.value.trim() || null,
    requisitos: elements.requirements.value.trim() || null,
    status: elements.statusInput.value,
    anotacoes: elements.notes.value.trim() || null,
  };
  if (elements.date.value) payload.data_candidatura = `${elements.date.value}T12:00:00`;
  const id = elements.id.value;

  try {
    await request(id ? `/api/candidaturas/${id}` : "/api/candidaturas", {
      method: id ? "PATCH" : "POST",
      body: JSON.stringify(payload),
    });
    closeDialog();
    page = 0;
    await loadDashboard();
    showNotice(id ? "Candidatura atualizada." : "Candidatura adicionada.");
  } catch (error) {
    elements.formError.textContent = error.message;
    elements.formError.hidden = false;
  } finally {
    elements.save.disabled = false;
    elements.save.textContent = id ? "Salvar alterações" : "Salvar candidatura";
  }
});

elements.body.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = Number(button.dataset.id);
  if (button.dataset.action === "edit") {
    try {
      openDialog(await request(`/api/candidaturas/${id}`));
    } catch (error) {
      showNotice(`Não foi possível abrir a candidatura. ${error.message}`);
    }
  } else if (button.dataset.action === "delete") {
    const company = button.closest("tr").querySelector(".company-copy strong").textContent;
    if (!window.confirm(`Excluir a candidatura para ${company}?`)) return;
    try {
      await request(`/api/candidaturas/${id}`, { method: "DELETE" });
      if (page > 0 && elements.body.children.length === 1) page -= 1;
      await loadDashboard();
      showNotice("Candidatura excluída.");
    } catch (error) {
      showNotice(`Não foi possível excluir a candidatura. ${error.message}`);
    }
  }
});

document.querySelector("#new-application").addEventListener("click", () => openDialog());
document.querySelector("#empty-create").addEventListener("click", () => openDialog());
document.querySelector("#close-dialog").addEventListener("click", closeDialog);
document.querySelector("#cancel-dialog").addEventListener("click", closeDialog);
elements.dialog.addEventListener("click", (event) => {
  if (event.target === elements.dialog) closeDialog();
});
elements.search.addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => {
    page = 0;
    loadDashboard();
  }, 250);
});
elements.status.addEventListener("change", () => {
  page = 0;
  loadDashboard();
});
elements.previous.addEventListener("click", () => {
  if (page > 0) {
    page -= 1;
    loadDashboard();
  }
});
elements.next.addEventListener("click", () => {
  page += 1;
  loadDashboard();
});

loadDashboard();