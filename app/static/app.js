const workspace = document.querySelector(".problem-workspace");

if (workspace) {
  const topic = workspace.dataset.topic;
  const problemPanel = document.querySelector("#problem-panel");
  const solutionPanel = document.querySelector("#solution-panel");
  const generateButton = document.querySelector("#generate-problem");
  const solutionButton = document.querySelector("#show-solution");
  let currentProblem = null;

  function renderSubparts(subparts) {
    if (!subparts || !subparts.length) return "";
    return `<ol class="subparts">${subparts.map((part) => `<li><span>${escapeHtml(part.text)}</span></li>`).join("")}</ol>`;
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
    const response = await fetch(`/api/problem?topic=${encodeURIComponent(topic)}`);
    if (!response.ok) {
      problemPanel.innerHTML = `<p class="empty-state">No active problems are available for this topic yet.</p>`;
      generateButton.disabled = false;
      return;
    }
    currentProblem = await response.json();
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
    solutionPanel.innerHTML = `
      <div class="solution-heading">
        <span>Explained solution</span>
        <span>${escapeHtml(data.solution_status)}</span>
      </div>
      <div class="solution-text">${escapeHtml(data.solution)}</div>
    `;
  }

  generateButton.addEventListener("click", generateProblem);
  solutionButton.addEventListener("click", showSolution);
}
