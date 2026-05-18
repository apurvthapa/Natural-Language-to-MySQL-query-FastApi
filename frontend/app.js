const form = document.querySelector("#queryForm");
const queryInput = document.querySelector("#queryInput");
const inputLabel = document.querySelector("#inputLabel");
const sqlOutput = document.querySelector("#sqlOutput");
const resultTable = document.querySelector("#resultTable");
const rowCount = document.querySelector("#rowCount");
const timeMetric = document.querySelector("#timeMetric");
const messageBanner = document.querySelector("#messageBanner");
const connectionStatus = document.querySelector("#connectionStatus");
const submitButton = document.querySelector(".submit-button");
const downloadCsvButton = document.querySelector("#downloadCsv");
const pageSummary = document.querySelector("#pageSummary");
const paginationControls = document.querySelector("#paginationControls");
const modeTabs = document.querySelectorAll(".mode-tab");
const sampleQueries = document.querySelectorAll(".sample-query");

let mode = "natural";
let resultRows = [];
let resultColumns = [];
let currentPage = 1;

const ROWS_PER_PAGE = 100;
const API_BASE_URL = (window.HARBOR_SQL_API_BASE_URL || "").replace(/\/$/, "");

const modeConfig = {
    natural: {
        endpoint: "/query_to_sql",
        label: "Voyage question",
        placeholder: "Top delayed routes by average delay",
        samples: [
            "Top delayed routes by average delay",
            "Average delay by vessel type",
            "Which destination ports receive the most shipments?"
        ]
    },
    sql: {
        endpoint: "/sql",
        label: "Read-only SQL",
        placeholder: "SELECT shipment_status, COUNT(*) AS shipments FROM shipments GROUP BY shipment_status",
        samples: [
            "SELECT * FROM shipments LIMIT 250",
            "SELECT vessel_type, AVG(capacity_teu) AS average_capacity FROM ships GROUP BY vessel_type",
            "SELECT region, COUNT(*) AS ports FROM ports GROUP BY region"
        ]
    }
};

function setStatus(text, state = "ready") {
    connectionStatus.textContent = text;
    connectionStatus.classList.toggle("loading", state === "loading");
    connectionStatus.classList.toggle("error", state === "error");
}

function setBanner(message, isError = false) {
    if (!message) {
        messageBanner.className = "message-banner hidden";
        messageBanner.textContent = "";
        return;
    }

    messageBanner.className = isError ? "message-banner error" : "message-banner";
    messageBanner.textContent = message;
}

function formatSeconds(value) {
    const seconds = Number(value || 0);
    return `${seconds.toFixed(3)}s`;
}

function formatCell(value) {
    if (value === null || value === undefined) {
        return "";
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return String(value);
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function resetTable(message = "No cargo loaded yet") {
    resultRows = [];
    resultColumns = [];
    currentPage = 1;
    resultTable.querySelector("thead").innerHTML = "";
    resultTable.querySelector("tbody").innerHTML = `<tr><td class="empty-state">${escapeHtml(message)}</td></tr>`;
    renderPagination();
    updateDownloadState();
}

function collectColumns(rows) {
    return [...rows.reduce((set, row) => {
        Object.keys(row).forEach((key) => set.add(key));
        return set;
    }, new Set())];
}

function renderTablePage() {
    const thead = resultTable.querySelector("thead");
    const tbody = resultTable.querySelector("tbody");

    if (resultRows.length === 0) {
        resetTable("No rows returned");
        return;
    }

    const totalPages = Math.max(1, Math.ceil(resultRows.length / ROWS_PER_PAGE));
    currentPage = Math.min(Math.max(1, currentPage), totalPages);

    const startIndex = (currentPage - 1) * ROWS_PER_PAGE;
    const visibleRows = resultRows.slice(startIndex, startIndex + ROWS_PER_PAGE);

    thead.innerHTML = `<tr>${resultColumns.map((column) => `<th scope="col">${escapeHtml(column)}</th>`).join("")}</tr>`;
    tbody.innerHTML = visibleRows.map((row) => {
        const cells = resultColumns
            .map((column) => `<td>${escapeHtml(formatCell(row[column]))}</td>`)
            .join("");
        return `<tr>${cells}</tr>`;
    }).join("");

    renderPagination();
    updateDownloadState();
}

function setResultRows(rows) {
    resultRows = Array.isArray(rows) ? rows : [];
    resultColumns = collectColumns(resultRows);
    currentPage = 1;
    renderTablePage();
}

function getPageNumbers(totalPages) {
    if (totalPages <= 7) {
        return Array.from({ length: totalPages }, (_, index) => index + 1);
    }

    const pages = new Set([1, totalPages, currentPage - 1, currentPage, currentPage + 1]);
    return [...pages]
        .filter((page) => page >= 1 && page <= totalPages)
        .sort((a, b) => a - b);
}

function renderPagination() {
    const totalRows = resultRows.length;
    const totalPages = Math.ceil(totalRows / ROWS_PER_PAGE);

    if (totalRows === 0) {
        pageSummary.textContent = "Showing 0 rows";
        paginationControls.innerHTML = "";
        return;
    }

    const startRow = (currentPage - 1) * ROWS_PER_PAGE + 1;
    const endRow = Math.min(currentPage * ROWS_PER_PAGE, totalRows);
    pageSummary.textContent = `Showing ${startRow}-${endRow} of ${totalRows} rows`;

    if (totalPages <= 1) {
        paginationControls.innerHTML = "";
        return;
    }

    const pageButtons = [];
    const pageNumbers = getPageNumbers(totalPages);

    pageButtons.push(renderPageButton("Prev", currentPage - 1, currentPage === 1));

    pageNumbers.forEach((page, index) => {
        if (index > 0 && page - pageNumbers[index - 1] > 1) {
            pageButtons.push(`<span class="page-gap">...</span>`);
        }

        pageButtons.push(renderPageButton(String(page), page, false, page === currentPage));
    });

    pageButtons.push(renderPageButton("Next", currentPage + 1, currentPage === totalPages));
    paginationControls.innerHTML = pageButtons.join("");
}

function renderPageButton(label, page, disabled, active = false) {
    return `
        <button
            class="page-button${active ? " active" : ""}"
            type="button"
            data-page="${page}"
            ${disabled ? "disabled" : ""}
            ${active ? 'aria-current="page"' : ""}
        >${escapeHtml(label)}</button>
    `;
}

function updateDownloadState() {
    downloadCsvButton.disabled = resultRows.length === 0;
}

function csvEscape(value) {
    const text = formatCell(value);
    if (/[",\n\r]/.test(text)) {
        return `"${text.replaceAll('"', '""')}"`;
    }

    return text;
}

function downloadCsv() {
    if (resultRows.length === 0) {
        return;
    }

    const csvRows = [
        resultColumns.map(csvEscape).join(","),
        ...resultRows.map((row) => resultColumns.map((column) => csvEscape(row[column])).join(","))
    ];
    const blob = new Blob([csvRows.join("\n")], {
        type: "text/csv;charset=utf-8"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const timestamp = new Date().toISOString().slice(0, 19).replaceAll(":", "-");

    link.href = url;
    link.download = `harbor-sql-results-${timestamp}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

function updateMode(nextMode) {
    mode = nextMode;
    const config = modeConfig[mode];

    modeTabs.forEach((tab) => {
        const isActive = tab.dataset.mode === mode;
        tab.classList.toggle("active", isActive);
        tab.setAttribute("aria-selected", String(isActive));
    });

    inputLabel.textContent = config.label;
    queryInput.placeholder = config.placeholder;

    sampleQueries.forEach((button, index) => {
        button.textContent = [
            ["Delayed routes", "Vessel delays", "Port volume"],
            ["Shipments", "Capacity avg", "Region ports"]
        ][mode === "natural" ? 0 : 1][index];
        button.dataset.query = config.samples[index];
    });

    queryInput.value = "";
    setBanner("");
    sqlOutput.textContent = "Awaiting query";
    rowCount.textContent = "0 rows";
    timeMetric.textContent = "0.000s";
    resetTable();
}

async function runQuery(query) {
    const config = modeConfig[mode];

    setStatus("Crossing channel", "loading");
    setBanner("");
    submitButton.disabled = true;

    const response = await fetch(`${API_BASE_URL}${config.endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_query: query
        })
    });

    const responseText = await response.text();
    let payload;

    try {
        payload = responseText ? JSON.parse(responseText) : {};
    } catch {
        payload = {
            error: responseText || "Request failed"
        };
    }

    if (!response.ok) {
        throw new Error(payload.detail || payload.error || "Request failed");
    }

    return payload;
}

function renderResponse(payload) {
    const rows = Array.isArray(payload.result) ? payload.result : [];
    const rowTotal = payload.row_count ?? rows.length;
    const sqlText = payload.sql_query || (mode === "sql" ? queryInput.value.trim() : "No SQL generated");
    const errorMessage = payload.error || (payload.success === false ? payload.error : "");
    const infoMessage = payload.message || (typeof payload.result === "string" ? payload.result : "");

    sqlOutput.textContent = sqlText;
    rowCount.textContent = `${rowTotal} ${rowTotal === 1 ? "row" : "rows"}`;
    timeMetric.textContent = formatSeconds(payload.execution_time);
    setResultRows(rows);

    if (errorMessage) {
        setBanner(errorMessage, true);
        setStatus("Needs attention", "error");
        return;
    }

    setBanner(infoMessage, false);
    setStatus("Docked");
}

modeTabs.forEach((tab) => {
    tab.addEventListener("click", () => updateMode(tab.dataset.mode));
});

sampleQueries.forEach((button) => {
    button.addEventListener("click", () => {
        queryInput.value = button.dataset.query;
        queryInput.focus();
    });
});

paginationControls.addEventListener("click", (event) => {
    const button = event.target.closest(".page-button");

    if (!button || button.disabled) {
        return;
    }

    currentPage = Number(button.dataset.page);
    renderTablePage();
});

downloadCsvButton.addEventListener("click", downloadCsv);

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = queryInput.value.trim();

    if (!query) {
        setBanner("Empty query is not allowed", true);
        return;
    }

    try {
        const payload = await runQuery(query);
        renderResponse(payload);
    } catch (error) {
        setBanner(error.message, true);
        setStatus("Offline", "error");
        sqlOutput.textContent = "Request failed";
        resetTable("No rows returned");
    } finally {
        submitButton.disabled = false;
    }
});
