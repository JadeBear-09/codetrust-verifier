LIGHT_DASHBOARD_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>CodeTrust · Product intent map</title>
  <style>
    :root {
      --paper:#f7f7f5;
      --card:#ffffff;
      --ink:#242424;
      --muted:#6f6f6b;
      --faint:#989892;
      --line:#deded9;
      --soft:#eeeeea;
      --green:#2f6f55;
      --green-bg:#edf6f0;
      --amber:#8c5b19;
      --amber-bg:#fff5e5;
      --red:#9b3d35;
      --red-bg:#fff0ee;
      --blue:#45648a;
      --blue-bg:#edf3fa;
      --shadow:0 1px 2px rgba(30,30,25,.05),0 8px 30px rgba(30,30,25,.04);
    }
    * { box-sizing:border-box; }
    body {
      margin:0;
      min-height:100vh;
      background:var(--paper);
      color:var(--ink);
      font:14px/1.45 ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    }
    button,input { font:inherit; }
    button { color:inherit; }
    .app { min-height:100vh; display:grid; grid-template-columns:228px minmax(560px,1fr) 350px; }
    .rail,.detail { background:rgba(255,255,255,.82); backdrop-filter:blur(12px); }
    .rail { border-right:1px solid var(--line); padding:20px 16px; display:flex; flex-direction:column; }
    .brand { display:flex; align-items:center; gap:10px; padding:2px 8px 22px; font-weight:680; letter-spacing:-.02em; }
    .mark { width:28px; height:28px; border:1px solid #c7c7c1; border-radius:9px; display:grid; place-items:center; background:#fff; font-weight:750; }
    .workspace { padding:0 8px; }
    .eyebrow { color:var(--faint); font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
    .product-name { font-size:14px; font-weight:650; margin:5px 0 3px; }
    .revision { color:var(--muted); font-size:12px; }
    .nav { margin-top:22px; display:grid; gap:4px; }
    .nav button { border:0; background:transparent; border-radius:8px; text-align:left; padding:9px 10px; color:var(--muted); cursor:pointer; }
    .nav button.active { color:var(--ink); background:var(--soft); font-weight:620; }
    .pulse { width:7px; height:7px; display:inline-block; border-radius:50%; margin-right:9px; background:#a6a6a0; }
    .nav .active .pulse { background:var(--green); }
    .rail-note { margin-top:auto; border-top:1px solid var(--line); padding:16px 8px 2px; color:var(--muted); font-size:12px; }
    .rail-note strong { color:var(--ink); display:block; margin-bottom:4px; }
    .main { min-width:0; display:flex; flex-direction:column; }
    .topbar { min-height:70px; display:flex; align-items:center; gap:12px; padding:14px 22px; border-bottom:1px solid var(--line); background:rgba(247,247,245,.92); position:sticky; top:0; z-index:20; }
    .title { min-width:0; }
    .title h1 { font-size:17px; margin:0; letter-spacing:-.02em; font-weight:670; }
    .title p { margin:2px 0 0; color:var(--muted); font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .top-actions { margin-left:auto; display:flex; gap:8px; }
    .btn { border:1px solid var(--line); background:#fff; border-radius:9px; padding:8px 11px; cursor:pointer; font-weight:590; box-shadow:0 1px 1px rgba(0,0,0,.02); }
    .btn:hover { border-color:#b9b9b3; }
    .btn.primary { background:#2d2d2b; border-color:#2d2d2b; color:#fff; }
    .modal { position:fixed; inset:0; z-index:60; display:grid; place-items:center; padding:14px; background:rgba(55,55,50,.2); backdrop-filter:blur(2px); }
    .modal[hidden] { display:none; }
    .modal-card { width:min(620px,100%); max-height:calc(100vh - 28px); overflow:auto; border:1px solid var(--line); border-radius:16px; color:var(--ink); background:#fff; box-shadow:0 24px 80px rgba(30,30,25,.18); }
    .dialog-form { padding:22px; }
    .dialog-form h2 { margin:0; font-size:20px; letter-spacing:-.03em; }
    .dialog-form > p { margin:5px 0 19px; color:var(--muted); font-size:12px; }
    .fields { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
    .field { display:grid; gap:6px; }
    .field.wide { grid-column:1/-1; }
    .field label { font-size:11px; color:var(--muted); font-weight:650; }
    .field input,.field textarea,.field select { width:100%; border:1px solid var(--line); border-radius:9px; padding:9px 10px; background:#fbfbfa; color:var(--ink); outline:0; resize:vertical; }
    .field input:focus,.field textarea:focus,.field select:focus { border-color:#999992; background:#fff; }
    .field textarea { min-height:72px; }
    .hint { color:var(--faint); font-size:10px; }
    .dialog-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:20px; padding-top:16px; border-top:1px solid var(--line); }
    .summary { display:grid; grid-template-columns:1fr repeat(3,auto); gap:12px; align-items:center; padding:16px 22px; border-bottom:1px solid var(--line); }
    .summary-copy strong { display:block; font-size:14px; }
    .summary-copy span { color:var(--muted); font-size:12px; }
    .metric { min-width:96px; padding-left:16px; border-left:1px solid var(--line); }
    .metric b { display:block; font-size:17px; font-weight:680; letter-spacing:-.03em; }
    .metric span { color:var(--muted); font-size:11px; }
    .metric.drift b { color:var(--red); }
    .canvas-wrap { position:relative; flex:1; min-height:650px; overflow:auto; background-image:radial-gradient(#d3d3ce 0.7px,transparent .7px); background-size:20px 20px; }
    .canvas-tools { position:sticky; left:16px; top:14px; width:max-content; z-index:8; display:flex; gap:7px; padding:7px; background:rgba(255,255,255,.92); border:1px solid var(--line); border-radius:11px; box-shadow:var(--shadow); }
    .canvas-tools input { width:180px; border:0; outline:0; padding:4px 6px; background:transparent; color:var(--ink); }
    .canvas-tools button { border:0; border-left:1px solid var(--line); background:transparent; padding:4px 8px; cursor:pointer; color:var(--muted); }
    .tree { width:max-content; min-width:100%; padding:34px 32px 90px; }
    .tree ul { padding-top:28px; position:relative; display:flex; justify-content:center; margin:0; padding-left:0; }
    .tree li { list-style:none; text-align:center; position:relative; padding:28px 8px 0; }
    .tree li::before,.tree li::after { content:""; position:absolute; top:0; width:50%; height:28px; border-top:1px solid #c9c9c3; }
    .tree li::before { right:50%; }
    .tree li::after { left:50%; border-left:1px solid #c9c9c3; }
    .tree li:only-child::before,.tree li:only-child::after { display:none; }
    .tree li:only-child { padding-top:0; }
    .tree li:first-child::before,.tree li:last-child::after { border:0; }
    .tree li:last-child::before { border-right:1px solid #c9c9c3; border-radius:0 8px 0 0; }
    .tree li:first-child::after { border-radius:8px 0 0; }
    .tree ul ul::before { content:""; position:absolute; top:0; left:50%; height:28px; border-left:1px solid #c9c9c3; }
    .node { width:214px; min-height:112px; border:1px solid var(--line); border-radius:13px; background:rgba(255,255,255,.98); padding:13px; text-align:left; cursor:pointer; box-shadow:var(--shadow); transition:.15s ease; }
    .node:hover { transform:translateY(-2px); border-color:#b9b9b3; }
    .node.selected { outline:2px solid #8a8a84; outline-offset:2px; }
    .node.dim { opacity:.24; }
    .node.needs-decision,.node.needs-review,.node.blocked { background:var(--red-bg); border-color:#e6c2bd; }
    .node.waiting,.node.needs-work { background:var(--amber-bg); border-color:#ead3ad; }
    .node.pass,.node.validated,.node.approved { background:var(--green-bg); border-color:#c9ddcf; }
    .node-top { display:flex; justify-content:space-between; gap:8px; align-items:center; }
    .type { color:var(--faint); font-size:10px; text-transform:uppercase; letter-spacing:.07em; font-weight:720; }
    .score { border:1px solid var(--line); background:rgba(255,255,255,.65); border-radius:999px; padding:2px 6px; font-size:10px; color:var(--muted); white-space:nowrap; }
    .node h3 { font-size:13px; line-height:1.28; margin:11px 0 6px; letter-spacing:-.01em; }
    .node p { margin:0; color:var(--muted); font-size:11px; line-height:1.4; }
    .node-foot { margin-top:10px; display:flex; gap:5px; flex-wrap:wrap; }
    .tag { font-size:9px; color:var(--muted); background:rgba(255,255,255,.7); border:1px solid var(--line); border-radius:5px; padding:2px 5px; }
    .detail { border-left:1px solid var(--line); min-width:0; padding:22px; overflow:auto; max-height:100vh; position:sticky; top:0; }
    .detail-head { display:flex; align-items:center; justify-content:space-between; gap:10px; }
    .state { border-radius:999px; padding:4px 8px; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.05em; background:var(--soft); color:var(--muted); }
    .state.danger { color:var(--red); background:var(--red-bg); }
    .state.good { color:var(--green); background:var(--green-bg); }
    .detail h2 { font-size:22px; line-height:1.15; letter-spacing:-.035em; margin:19px 0 9px; }
    .detail .lede { color:var(--muted); margin:0 0 18px; }
    .owner { padding:11px 0 17px; border-bottom:1px solid var(--line); color:var(--muted); font-size:12px; }
    .owner b { color:var(--ink); }
    .signal { margin:18px 0; }
    .signal-row { display:flex; justify-content:space-between; font-size:12px; margin-bottom:7px; }
    .bar { height:6px; border-radius:999px; background:var(--soft); overflow:hidden; }
    .bar span { display:block; height:100%; background:var(--green); border-radius:inherit; }
    .section { margin-top:21px; }
    .section h3 { color:var(--faint); font-size:10px; text-transform:uppercase; letter-spacing:.08em; margin:0 0 7px; }
    .section p { margin:0; color:#4f4f4c; font-size:13px; }
    .compare { border:1px solid var(--line); border-radius:11px; overflow:hidden; }
    .compare div { padding:11px; }
    .compare div + div { border-top:1px solid var(--line); }
    .compare small { display:block; color:var(--faint); margin-bottom:4px; }
    .danger-box { background:var(--red-bg); border:1px solid #e6c2bd; border-radius:11px; padding:12px; color:#71342e; }
    .links { display:flex; gap:7px; flex-wrap:wrap; margin-top:18px; }
    .link { display:inline-flex; align-items:center; text-decoration:none; border:1px solid var(--line); border-radius:8px; padding:7px 9px; background:#fff; color:var(--ink); font-size:11px; cursor:pointer; }
    .run-result { margin-top:18px; padding:12px; border:1px dashed #c9c9c3; border-radius:11px; color:var(--muted); font-size:12px; display:none; }
    .run-result.show { display:block; }
    .run-result strong { color:var(--ink); display:block; margin-bottom:5px; }
    .toast { position:fixed; left:50%; bottom:24px; transform:translate(-50%,20px); opacity:0; pointer-events:none; background:#2d2d2b; color:#fff; padding:10px 14px; border-radius:9px; transition:.2s; z-index:50; box-shadow:var(--shadow); }
    .toast.show { opacity:1; transform:translate(-50%,0); }
    @media(max-width:1100px) {
      .app { grid-template-columns:170px minmax(430px,1fr) 320px; }
      .topbar { flex-wrap:wrap; }
      .title { width:100%; }
      .top-actions { margin-left:0; }
      .detail { width:auto; box-shadow:none; }
    }
    @media(max-width:900px) {
      .app { grid-template-columns:minmax(430px,1fr) 320px; }
      .rail { display:none; }
    }
    @media(max-width:760px) {
      .app { display:block; }
      .detail { position:static; width:auto; max-height:none; border:1px solid var(--line); margin:12px; border-radius:14px; }
      .summary { grid-template-columns:1fr 1fr; }
      .summary-copy { grid-column:1/-1; }
      .metric { border:0; padding:0; }
      .topbar { padding:12px; }
      .top-actions { flex-wrap:wrap; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="rail">
      <div class="brand"><div class="mark">C</div>CodeTrust</div>
      <div class="workspace">
        <div class="eyebrow">Product workspace</div>
        <div class="product-name" id="railProductName">Checkout resilience</div>
        <div class="revision" id="railRevision">Intent revision 3 · approved</div>
      </div>
      <nav class="nav" aria-label="Workspace views">
        <button class="active" data-view="intent"><span class="pulse"></span>Intent map</button>
        <button data-view="verification"><span class="pulse"></span>Verification runs</button>
        <button data-view="decisions"><span class="pulse"></span>Human decisions</button>
        <button data-view="jira"><span class="pulse"></span>Jira connections</button>
        <button data-view="git"><span class="pulse"></span>Git evidence</button>
      </nav>
      <div class="rail-note">
        <strong>Shared context</strong>
        Product owns why. Jira owns planned work. Git owns changed code. CodeTrust preserves alignment.
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="title">
          <h1 id="viewTitle">Product intent map</h1>
          <p id="viewSubtitle">Business outcome → Jira work → reviewed commits → human decisions</p>
        </div>
        <div class="top-actions">
          <button class="btn" id="realPrDemo" data-testid="real-pr-demo">Real rejected PR</button>
          <button class="btn" id="newProduct" data-testid="new-product">New product</button>
          <button class="btn" id="addWork" data-testid="add-work">Add work</button>
          <button class="btn primary" id="runCheck" data-testid="run-check">Verify selected work</button>
        </div>
      </header>

      <section class="summary" aria-label="Product alignment summary">
        <div class="summary-copy">
          <strong id="productTagline">Loading product intent…</strong>
          <span>Percentages show evidence coverage signal, not guaranteed completion.</span>
        </div>
        <div class="metric"><b id="coverageMetric">—</b><span>scope coverage</span></div>
        <div class="metric drift"><b id="driftMetric">—</b><span>scope drift</span></div>
        <div class="metric"><b id="decisionMetric">—</b><span>human decision</span></div>
      </section>

      <section class="canvas-wrap" aria-label="Clickable product intent tree">
        <div class="canvas-tools">
          <input id="search" type="search" placeholder="Find task, owner, commit…" aria-label="Search tree">
          <button id="resetSearch">Clear</button>
        </div>
        <div class="tree" id="tree"></div>
      </section>
    </main>

    <aside class="detail" aria-live="polite">
      <div class="detail-head">
        <span class="eyebrow" id="detailType">Product intent</span>
        <span class="state good" id="detailState">Approved</span>
      </div>
      <h2 id="detailTitle">Reliable checkout across payment retries</h2>
      <p class="lede" id="detailSummary">Select any node to inspect intent, implementation, evidence, and next owner.</p>
      <div class="owner">Owner · <b id="detailOwner">Maya · Product</b></div>
      <div class="signal">
        <div class="signal-row"><span>Alignment signal</span><strong id="detailScore">100%</strong></div>
        <div class="bar"><span id="detailBar" style="width:100%"></span></div>
      </div>
      <div class="section">
        <h3>Original product clause vs current work</h3>
        <div class="compare">
          <div><small>Original</small><span id="detailOriginal"></span></div>
          <div><small>Current</small><span id="detailCurrent"></span></div>
        </div>
      </div>
      <div class="section"><h3>Evidence</h3><p id="detailEvidence"></p></div>
      <div class="section"><h3>Next action</h3><div class="danger-box" id="detailAction"></div></div>
      <div class="links" id="detailLinks"></div>
      <div class="run-result" id="runResult"></div>
    </aside>
  </div>
  <div class="modal" id="productDialog" hidden>
    <form class="dialog-form modal-card" id="productForm">
      <h2>Create product intent</h2>
      <p>Product owner records why, boundaries, and observable success before engineering branches.</p>
      <div class="fields">
        <div class="field"><label for="productName">Product name</label><input id="productName" required placeholder="Checkout resilience"></div>
        <div class="field"><label for="productOwner">Product owner</label><input id="productOwner" required placeholder="Maya · Product"></div>
        <div class="field wide"><label for="productOutcome">Business outcome</label><textarea id="productOutcome" required placeholder="What must improve for customer or business?"></textarea></div>
        <div class="field"><label for="productInScope">In scope</label><textarea id="productInScope" required placeholder="One behavior per line"></textarea></div>
        <div class="field"><label for="productOutScope">Out of scope</label><textarea id="productOutScope" placeholder="One protected boundary per line"></textarea></div>
        <div class="field wide"><label for="productCriteria">Acceptance criteria</label><textarea id="productCriteria" required placeholder="One observable result per line"></textarea></div>
        <div class="field"><label for="jiraProjectKey">Jira project key</label><input id="jiraProjectKey" placeholder="PAY"></div>
        <div class="field"><label for="jiraProjectUrl">Jira project URL</label><input id="jiraProjectUrl" type="url" placeholder="https://company.atlassian.net/jira/software/projects/PAY"></div>
      </div>
      <div class="dialog-actions"><button class="btn" type="button" data-close="productDialog">Cancel</button><button class="btn primary" type="submit">Create workspace</button></div>
    </form>
  </div>

  <div class="modal" id="workDialog" hidden>
    <form class="dialog-form modal-card" id="workForm">
      <h2>Add Jira work or commit</h2>
      <p>Every leaf keeps product clause, owner interpretation, Jira reference, and Git evidence together.</p>
      <div class="fields">
        <div class="field"><label for="workParent">Parent branch</label><select id="workParent" required></select></div>
        <div class="field"><label for="workKind">Work type</label><select id="workKind"><option value="jira task">Jira task</option><option value="commit">Commit / pull request</option><option value="decision">Product decision</option></select></div>
        <div class="field"><label for="workTitle">Title</label><input id="workTitle" required placeholder="Build safe retry worker"></div>
        <div class="field"><label for="workOwner">Owner</label><input id="workOwner" required placeholder="Nila · Developer"></div>
        <div class="field wide"><label for="workSummary">Expected work</label><textarea id="workSummary" required placeholder="What should this task or commit accomplish?"></textarea></div>
        <div class="field"><label for="workJiraKey">Jira issue key</label><input id="workJiraKey" placeholder="PAY-242"></div>
        <div class="field"><label for="workJiraUrl">Jira issue URL</label><input id="workJiraUrl" type="url" placeholder="https://company.atlassian.net/browse/PAY-242"></div>
        <div class="field"><label for="workCommit">Commit SHA</label><input id="workCommit" placeholder="2b7d867"></div>
        <div class="field"><label for="workGitUrl">GitHub pull-request URL</label><input id="workGitUrl" type="url" placeholder="https://github.com/owner/repo/pull/42"></div>
        <div class="field wide"><label for="workClause">Product clause being implemented</label><textarea id="workClause" placeholder="Copy approved outcome or acceptance criterion"></textarea></div>
        <div class="field"><label for="workRole">Interpretation owner</label><select id="workRole"><option value="developer">Developer</option><option value="senior">Senior reviewer</option><option value="product owner">Product owner</option></select></div>
        <div class="field"><label for="workInterpretation">Interpretation</label><textarea id="workInterpretation" placeholder="What does owner believe this requirement means?"></textarea></div>
        <div class="field wide"><label for="workChange">Current change</label><textarea id="workChange" placeholder="What behavior does code now create?"></textarea></div>
      </div>
      <div class="dialog-actions"><button class="btn" type="button" data-close="workDialog">Cancel</button><button class="btn primary" type="submit">Add to tree</button></div>
    </form>
  </div>
  <div class="toast" id="toast"></div>

  <script>
    let product = null;
    let selectedId = "product";
    let workspaceMode = false;
    let realPrMode = false;
    let activeView = "intent";
    const byId = id => document.getElementById(id);

    const views = {
      intent: {
        title:"Product intent map",
        subtitle:"Business outcome → Jira work → reviewed commits → human decisions",
        match:() => true
      },
      verification: {
        title:"Verification runs",
        subtitle:"Commits with deterministic evidence and current verdict",
        match:node => node.kind === "commit"
      },
      decisions: {
        title:"Human decisions",
        subtitle:"Product questions where automation must stop",
        match:node => node.kind === "decision" || node.state === "needs decision"
      },
      jira: {
        title:"Jira connections",
        subtitle:"Planned work linked to product intent",
        match:node => Boolean(node.jira) && !["missing", "unlinked", "not linked", "create on approval"].includes(node.jira.toLowerCase())
      },
      git: {
        title:"Git evidence",
        subtitle:"Changed code and pull requests attached to approved work",
        match:node => Boolean(node.commit || node.git_url)
      }
    };

    function toast(message) {
      const node = byId("toast");
      node.textContent = message;
      node.classList.add("show");
      setTimeout(() => node.classList.remove("show"), 2200);
    }

    function childrenOf(id) {
      return product.nodes.filter(node => node.parent === id);
    }

    function buildBranch(node) {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.className = `node ${node.state.replaceAll(" ", "-")}`;
      button.dataset.id = node.id;
      button.dataset.search = `${node.title} ${node.summary} ${node.owner} ${node.commit || ""}`.toLowerCase();
      button.setAttribute("aria-label", `${node.kind}: ${node.title}`);

      const top = document.createElement("div");
      top.className = "node-top";
      const kind = document.createElement("span");
      kind.className = "type";
      kind.textContent = node.kind;
      const score = document.createElement("span");
      score.className = "score";
      score.textContent = `${node.alignment}%`;
      top.append(kind, score);

      const title = document.createElement("h3");
      title.textContent = node.title;
      const summary = document.createElement("p");
      summary.textContent = node.summary;
      const foot = document.createElement("div");
      foot.className = "node-foot";
      [node.jira, node.commit].filter(Boolean).forEach(value => {
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = value;
        foot.append(tag);
      });
      button.append(top, title, summary, foot);
      button.onclick = () => selectNode(node.id);
      li.append(button);

      const children = childrenOf(node.id);
      if (children.length) {
        const ul = document.createElement("ul");
        children.forEach(child => ul.append(buildBranch(child)));
        li.append(ul);
      }
      return li;
    }

    function renderTree() {
      const rootList = document.createElement("ul");
      product.nodes.filter(node => node.parent === null).forEach(node => rootList.append(buildBranch(node)));
      byId("tree").replaceChildren(rootList);
      selectNode(selectedId);
    }

    function selectNode(id) {
      const node = product.nodes.find(item => item.id === id);
      if (!node) return;
      selectedId = id;
      document.querySelectorAll(".node").forEach(item => item.classList.toggle("selected", item.dataset.id === id));
      byId("detailType").textContent = node.kind;
      byId("detailTitle").textContent = node.title;
      byId("detailSummary").textContent = node.summary;
      byId("detailOwner").textContent = node.owner;
      byId("detailState").textContent = node.state;
      const dangerous = ["needs decision", "needs review", "blocked"].includes(node.state);
      const good = ["approved", "validated", "pass"].includes(node.state);
      byId("detailState").className = `state ${dangerous ? "danger" : good ? "good" : ""}`;
      byId("detailScore").textContent = `${node.alignment}%`;
      byId("detailBar").style.width = `${node.alignment}%`;
      byId("detailBar").style.background = dangerous ? "var(--red)" : node.alignment < 60 ? "var(--amber)" : "var(--green)";
      byId("detailOriginal").textContent = node.original;
      byId("detailCurrent").textContent = node.current;
      byId("detailEvidence").textContent = node.evidence;
      byId("detailAction").textContent = node.action;
      const links = byId("detailLinks");
      links.replaceChildren();
      const jira = document.createElement(node.jira_url ? "a" : "button");
      jira.className = "link";
      jira.textContent = `Jira · ${node.jira}`;
      if (node.jira_url) {
        jira.href = node.jira_url;
        jira.target = "_blank";
        jira.rel = "noreferrer";
      } else {
        jira.onclick = () => toast(`Add Jira URL for ${node.jira}`);
      }
      links.append(jira);
      if (node.git_url) {
        const git = document.createElement("a");
        git.className = "link";
        git.href = node.git_url;
        git.target = "_blank";
        git.rel = "noreferrer";
        git.textContent = `Open Git${node.commit ? ` · ${node.commit}` : ""}`;
        links.append(git);
      }
      if (workspaceMode && node.kind === "commit") {
        const verify = document.createElement("button");
        verify.className = "link";
        verify.textContent = "Verify this commit";
        verify.onclick = verifySelectedNode;
        links.append(verify);
      }
    }

    function searchTree(value) {
      const query = value.trim().toLowerCase();
      let first = null;
      document.querySelectorAll(".node").forEach(node => {
        const item = product.nodes.find(candidate => candidate.id === node.dataset.id);
        const match = views[activeView].match(item) && (!query || node.dataset.search.includes(query));
        node.classList.toggle("dim", !match);
        if (match && !first) first = node.dataset.id;
      });
      if (first) selectNode(first);
    }

    function switchWorkspaceView(view) {
      activeView = views[view] ? view : "intent";
      document.querySelectorAll(".nav button").forEach(button => {
        const active = button.dataset.view === activeView;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      });
      byId("viewTitle").textContent = views[activeView].title;
      byId("viewSubtitle").textContent = views[activeView].subtitle;
      byId("search").value = "";
      searchTree("");
    }

    function displayProduct(nextProduct, isWorkspace, isRealPr = false) {
      product = nextProduct;
      workspaceMode = isWorkspace;
      realPrMode = isRealPr;
      selectedId = "product";
      byId("railProductName").textContent = product.name;
      byId("railRevision").textContent = `Intent revision ${product.revision || 3} · approved`;
      byId("productTagline").textContent = product.tagline;
      byId("coverageMetric").textContent = `${product.summary.coverage}%`;
      byId("driftMetric").textContent = `${product.summary.drift}%`;
      byId("decisionMetric").textContent = product.summary.decisions;
      renderTree();
      switchWorkspaceView("intent");
    }

    function showVerification(data, validation = null) {
      const result = byId("runResult");
      result.replaceChildren();
      const heading = document.createElement("strong");
      heading.textContent = `${data.verdict} · ${data.findings.length} evidence-backed findings`;
      const copy = document.createElement("span");
      copy.textContent = data.findings.length
        ? data.findings.map(item => `${item.rule_id}: ${item.title}`).join(" · ")
        : "Configured gates found no blocker.";
      result.append(heading, copy);
      if (validation) {
        const proof = document.createElement("p");
        proof.textContent = validation.agreement
          ? `External match · GitHub ${validation.pr_state}, unmerged · ${validation.quote}`
          : `External mismatch · GitHub ${validation.pr_state} · ${validation.quote}`;
        const source = document.createElement("a");
        source.className = "link";
        source.href = validation.url;
        source.target = "_blank";
        source.rel = "noreferrer";
        source.textContent = "Open maintainer decision";
        result.append(proof, source);
      }
      result.classList.add("show");
    }

    async function loadRealPrDemo() {
      const button = byId("realPrDemo");
      button.disabled = true;
      button.textContent = "Loading…";
      try {
        const response = await fetch("/api/real-pr-demo");
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Real PR demo failed to load");
        displayProduct(data, false, true);
        selectedId = "real-pr";
        selectNode(selectedId);
        toast("Real PR ready · maintainer outcome hidden");
      } finally {
        button.disabled = false;
        button.textContent = "Real rejected PR";
      }
    }

    async function verifyRealPr() {
      const response = await fetch("/api/real-pr-demo/verify", {method:"POST"});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Real PR verification failed");
      displayProduct(data.product, false, true);
      selectedId = "real-pr";
      selectNode(selectedId);
      showVerification(data.report, data.validation);
      toast(data.validation.agreement ? "CodeTrust matched maintainer outcome" : "Outcome mismatch");
    }

    async function verifySelectedNode() {
      const node = product.nodes.find(item => item.id === selectedId);
      if (!workspaceMode || !node || node.kind !== "commit") {
        toast("Select commit in your product workspace");
        return;
      }
      if (!node.git_url) {
        toast("Add GitHub pull-request URL first");
        return;
      }
      const response = await fetch(`/api/workspaces/${product.id}/nodes/${node.id}/verify`, {method:"POST"});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Verification failed");
      const keepSelected = node.id;
      product = data.product;
      selectedId = keepSelected;
      displayProduct(product, true);
      selectedId = keepSelected;
      selectNode(keepSelected);
      showVerification(data.report);
      toast(`Verification finished: ${data.report.verdict}`);
    }

    async function runAlignment() {
      const button = byId("runCheck");
      button.disabled = true;
      button.textContent = "Checking…";
      if (realPrMode) {
        try {
          await verifyRealPr();
        } catch (error) {
          toast(error.message);
        } finally {
          button.disabled = false;
          button.textContent = "Verify selected work";
        }
        return;
      }
      if (workspaceMode) {
        try {
          await verifySelectedNode();
        } catch (error) {
          toast(error.message);
        } finally {
          button.disabled = false;
          button.textContent = "Verify selected work";
        }
        return;
      }
      const ticket = `# Payment retry telemetry

## Outcome
Improve visibility into failed payment reconciliation.

## In scope
- Emit retry counters for payment reconciliation.

## Out of scope
- Refund authorization behavior.

## Acceptance criteria
- Metrics only; refund policy must remain unchanged.`;
      const diff = `diff --git a/refunds/authorization.py b/refunds/authorization.py
--- a/refunds/authorization.py
+++ b/refunds/authorization.py
@@ -84 +84 @@ def can_refund(order):
-    return order.age_days <= 30
+    return order.age_days <= 7
`;
      try {
        const response = await fetch("/api/verify", {
          method:"POST",
          headers:{"content-type":"application/json"},
          body:JSON.stringify({
            ticket,
            diff,
            offline:true,
            interpretations:[{
              role:"senior",
              text:"Tighten refund authorization from 30 days to 7 days.",
              source:"review"
            }]
          })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Verification failed");
        byId("driftMetric").textContent = `${data.scope_drift}%`;
        selectNode("commit-drift");
        showVerification(data);
        toast("Scope drift routed to product owner");
      } catch (error) {
        toast(error.message);
      } finally {
        button.disabled = false;
        button.textContent = "Verify selected work";
      }
    }

    function splitLines(value) {
      return value.split("\n").map(item => item.trim()).filter(Boolean);
    }

    function fillParentOptions() {
      const select = byId("workParent");
      select.replaceChildren();
      product.nodes.filter(node => node.kind !== "commit").forEach(node => {
        const option = document.createElement("option");
        option.value = node.id;
        option.textContent = `${node.kind} · ${node.title}`;
        select.append(option);
      });
      if (product.nodes.some(node => node.id === selectedId && node.kind !== "commit")) {
        select.value = selectedId;
      }
    }

    async function submitProduct(event) {
      event.preventDefault();
      const body = {
        name:byId("productName").value,
        outcome:byId("productOutcome").value,
        owner:byId("productOwner").value,
        in_scope:splitLines(byId("productInScope").value),
        out_of_scope:splitLines(byId("productOutScope").value),
        acceptance_criteria:splitLines(byId("productCriteria").value),
        jira_project_key:byId("jiraProjectKey").value,
        jira_project_url:byId("jiraProjectUrl").value
      };
      const response = await fetch("/api/workspaces", {
        method:"POST", headers:{"content-type":"application/json"}, body:JSON.stringify(body)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Product creation failed");
      byId("productDialog").hidden = true;
      byId("productForm").reset();
      displayProduct(data, true);
      toast("Product workspace created");
    }

    async function submitWork(event) {
      event.preventDefault();
      const body = {
        parent:byId("workParent").value,
        kind:byId("workKind").value,
        title:byId("workTitle").value,
        summary:byId("workSummary").value,
        owner:byId("workOwner").value,
        jira_key:byId("workJiraKey").value,
        jira_url:byId("workJiraUrl").value,
        commit:byId("workCommit").value,
        git_url:byId("workGitUrl").value,
        interpretation_role:byId("workRole").value,
        interpretation:byId("workInterpretation").value,
        product_clause:byId("workClause").value,
        current_change:byId("workChange").value
      };
      const response = await fetch(`/api/workspaces/${product.id}/nodes`, {
        method:"POST", headers:{"content-type":"application/json"}, body:JSON.stringify(body)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Work creation failed");
      byId("workDialog").hidden = true;
      byId("workForm").reset();
      product = data;
      selectedId = data.nodes[data.nodes.length - 1].id;
      displayProduct(product, true);
      selectedId = data.nodes[data.nodes.length - 1].id;
      selectNode(selectedId);
      toast("Work added to intent tree");
    }

    async function init() {
      const [workspaceResponse, demoResponse] = await Promise.all([
        fetch("/api/workspaces"), fetch("/api/product-demo")
      ]);
      const workspaces = await workspaceResponse.json();
      const demo = await demoResponse.json();
      if (workspaces.products.length) displayProduct(workspaces.products[workspaces.products.length - 1], true);
      else displayProduct(demo, false);
      byId("search").oninput = event => searchTree(event.target.value);
      byId("resetSearch").onclick = () => { byId("search").value = ""; searchTree(""); };
      document.querySelectorAll(".nav button").forEach(button => {
        button.onclick = () => switchWorkspaceView(button.dataset.view);
      });
      byId("runCheck").onclick = runAlignment;
      byId("realPrDemo").onclick = () => loadRealPrDemo().catch(error => toast(error.message));
      byId("newProduct").onclick = () => { byId("productDialog").hidden = false; };
      byId("addWork").onclick = () => {
        if (!workspaceMode) {
          toast("Create product workspace first");
          byId("productDialog").hidden = false;
          return;
        }
        fillParentOptions();
        byId("workDialog").hidden = false;
      };
      document.querySelectorAll("[data-close]").forEach(button => {
        button.onclick = () => { byId(button.dataset.close).hidden = true; };
      });
      byId("productForm").onsubmit = event => submitProduct(event).catch(error => toast(error.message));
      byId("workForm").onsubmit = event => submitWork(event).catch(error => toast(error.message));
    }

    init().catch(error => toast(error.message));
  </script>
</body>
</html>"""
