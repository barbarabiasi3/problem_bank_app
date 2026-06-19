const workspace = document.querySelector(".problem-workspace");

if (workspace) {
  const topic = workspace.dataset.topic;
  const problemPanel = document.querySelector("#problem-panel");
  const solutionPanel = document.querySelector("#solution-panel");
  const generateButton = document.querySelector("#generate-problem");
  const solutionButton = document.querySelector("#show-solution");
  let currentProblem = null;
  const historyStoreKey = `mgt404-seen:${topic}`;

  function renderSubparts(subparts) {
    if (!subparts || !subparts.length) return "";
    return `<ol class="subparts">${subparts.map((part) => `
      <li data-label="${escapeHtml(part.label)}">
        <span class="subpart-label">(${escapeHtml(part.label)})</span>
        <span>${escapeHtml(part.text)}</span>
        <div class="inline-solution" hidden></div>
      </li>`).join("")}</ol>`;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function generateProblem() {
    generateButton.disabled = true;
    solutionButton.disabled = true;
    solutionPanel.hidden = true;
    solutionPanel.innerHTML = "";
    problemPanel.innerHTML = `<p class="empty-state">Loading...</p>`;
    const seen = JSON.parse(localStorage.getItem(historyStoreKey) || "[]");
    const last = seen.length ? seen[seen.length - 1] : "";
    const params = new URLSearchParams({
      topic,
      exclude: seen.join(","),
      last,
    });
    const response = await fetch(`/api/problem?${params.toString()}`);
    if (!response.ok) {
      problemPanel.innerHTML = `<p class="empty-state">No active problems are available for this topic yet.</p>`;
      generateButton.disabled = false;
      return;
    }
    currentProblem = await response.json();
    const nextSeen = currentProblem.history_reset ? [] : seen;
    nextSeen.push(currentProblem.history_key);
    localStorage.setItem(historyStoreKey, JSON.stringify([...new Set(nextSeen)]));
    problemPanel.innerHTML = `
      <div class="problem-meta">
        <span>${escapeHtml(currentProblem.difficulty)}</span>
        <span>${escapeHtml(currentProblem.subtopic || currentProblem.item_type)}</span>
      </div>
      <h2>${escapeHtml(currentProblem.problem_title || currentProblem.topic)}</h2>
      <div class="problem-text">${escapeHtml(currentProblem.problem_text)}</div>
      ${renderSubparts(currentProblem.subparts)}
    `;
    solutionButton.disabled = false;
    generateButton.disabled = false;
  }

  async function showSolution() {
    if (!currentProblem) return;
    solutionButton.disabled = true;
    solutionPanel.hidden = false;
    solutionPanel.innerHTML = `<p class="empty-state">Loading solution...</p>`;
    const response = await fetch(currentProblem.solution_url);
    if (!response.ok) {
      solutionPanel.innerHTML = `<p class="empty-state">The solution could not be loaded.</p>`;
      solutionButton.disabled = false;
      return;
    }
    const data = await response.json();
    const solutionParts = data.solution_subparts || [];
    if (solutionParts.length) {
      solutionParts.forEach((part) => {
        const label = window.CSS && CSS.escape ? CSS.escape(part.label) : part.label;
        const target = problemPanel.querySelector(`li[data-label="${label}"] .inline-solution`);
        if (target) {
          target.innerHTML = `<strong>Solution (${escapeHtml(part.label)}):</strong> ${escapeHtml(part.text)}`;
          target.hidden = false;
        }
      });
      solutionPanel.hidden = true;
      solutionPanel.innerHTML = "";
      return;
    }
    solutionPanel.innerHTML = `<div class="solution-text">${escapeHtml(data.solution)}</div>`;
  }

  generateButton.addEventListener("click", generateProblem);
  solutionButton.addEventListener("click", showSolution);
}
