(() => {
  const buildCourseShell = () => {
    const body = document.body;
    const movableNodes = [...body.children].filter(
      (node) => node.tagName !== 'SCRIPT'
    );

    const topbar = document.createElement('header');
    topbar.className = 'course-topbar';
    topbar.innerHTML = `
      <nav class="course-topbar__links" aria-label="Course utilities">
        <a href="#course-home">Back to course</a>
        <a href="#interactive-mini-code-lab-run-an-artificial-neuron">Sandbox</a>
        <a href="#accuracy-boundaries-for-scripts-and-diagrams">Course Notes ↗</a>
      </nav>
      <div class="course-topbar__account">
        <button class="course-settings" type="button" aria-label="Settings">⚙</button>
        <span class="course-avatar" aria-label="Course profile">
          <img src="assets/uw_husky_avatar.png" alt="Animated cartoon husky profile" />
        </span>
        <span class="course-account-caret" aria-hidden="true">▼</span>
      </div>`;

    const sidebar = document.createElement('aside');
    sidebar.className = 'course-sidebar';
    sidebar.setAttribute('aria-label', 'Module navigation');
    sidebar.innerHTML = `
      <a class="course-sidebar__module" href="#course-home">Modules 2–3</a>
      <ol class="course-sidebar__nav"></ol>`;

    const main = document.createElement('main');
    main.className = 'course-main';
    const article = document.createElement('article');
    article.className = 'course-content';
    movableNodes.forEach((node) => article.appendChild(node));

    article.querySelector('#title-block-header')?.remove();
    article.querySelector('#TOC')?.remove();

    const sourceNodes = [...article.children];
    article.replaceChildren();
    const homePage = document.createElement('section');
    homePage.className = 'course-topic-page';
    homePage.id = 'course-home';
    homePage.dataset.topic = 'course-home';
    article.appendChild(homePage);

    let currentPage = homePage;
    sourceNodes.forEach((node) => {
      if (node.matches?.('h2[id], h3[id], h4[id]')) {
        currentPage = document.createElement('section');
        currentPage.className = 'course-topic-page';
        currentPage.dataset.topic = node.id;
        article.appendChild(currentPage);
      }
      currentPage.appendChild(node);
    });

    const pager = document.createElement('nav');
    pager.className = 'course-page-nav';
    pager.setAttribute('aria-label', 'Topic pagination');
    pager.innerHTML = `
      <button class="course-page-nav__previous" type="button">← Previous</button>
      <span class="course-page-nav__status" aria-live="polite"></span>
      <button class="course-page-nav__next" type="button">Next →</button>`;
    article.appendChild(pager);
    main.appendChild(article);

    const complete = document.createElement('div');
    complete.className = 'course-complete';
    complete.setAttribute('aria-label', 'Section complete');
    complete.textContent = '✓';

    const tools = document.createElement('div');
    tools.className = 'course-tools';
    tools.setAttribute('aria-label', 'Page tools');
    tools.innerHTML = `
      <button class="course-tool" type="button" aria-label="Page tools">⌘</button>
      <button class="course-tool" type="button" aria-label="Language tools">A</button>`;

    body.prepend(sidebar);
    body.prepend(topbar);
    body.appendChild(main);
    body.appendChild(complete);
    body.appendChild(tools);

    const sidebarNav = sidebar.querySelector('.course-sidebar__nav');
    const headings = [...article.querySelectorAll('h2[id], h3[id], h4[id]')];
    const topicPages = [...article.querySelectorAll('.course-topic-page')];
    const pageByTopic = new Map(topicPages.map((page) => [page.dataset.topic, page]));
    const previousButton = pager.querySelector('.course-page-nav__previous');
    const nextButton = pager.querySelector('.course-page-nav__next');
    const pageStatus = pager.querySelector('.course-page-nav__status');

    headings.forEach((heading, index) => {
      const page = pageByTopic.get(heading.id);
      const hasBodyContent = [...page.children].some((child) => child !== heading);
      if (hasBodyContent) return;

      const level = Number(heading.tagName.slice(1));
      const children = [];
      for (let childIndex = index + 1; childIndex < headings.length; childIndex += 1) {
        const candidate = headings[childIndex];
        const candidateLevel = Number(candidate.tagName.slice(1));
        if (candidateLevel <= level) break;
        if (candidateLevel === level + 1) children.push(candidate);
      }

      if (children.length) {
        const introduction = document.createElement('p');
        introduction.className = 'course-topic-page__introduction';
        introduction.textContent = 'Topics in this section:';
        const list = document.createElement('ul');
        list.className = 'course-topic-page__index';
        children.forEach((child) => {
          const item = document.createElement('li');
          const link = document.createElement('a');
          link.href = `#${child.id}`;
          link.textContent = child.textContent;
          item.appendChild(link);
          list.appendChild(item);
        });
        page.append(introduction, list);
      }
    });

    const navStack = [{ level: 1, list: sidebarNav }];

    headings.forEach((heading) => {
      const level = Number(heading.tagName.slice(1));
      while (navStack.length > 1 && navStack.at(-1).level >= level) navStack.pop();

      const item = document.createElement('li');
      item.className = `level-${level} course-sidebar__node`;
      item.dataset.target = heading.id;

      const row = document.createElement('div');
      row.className = 'course-sidebar__node-row';
      const toggle = document.createElement('button');
      toggle.className = 'course-sidebar__toggle';
      toggle.type = 'button';
      toggle.dataset.toggle = heading.id;
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', `Expand ${heading.textContent}`);
      toggle.innerHTML = '<span aria-hidden="true">▶</span>';

      const link = document.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent.replace(/^\d+\.\s*/, '');

      const subnav = document.createElement('ol');
      subnav.className = 'course-sidebar__subnav';
      subnav.id = `sidebar-group-${heading.id}`;
      toggle.setAttribute('aria-controls', subnav.id);

      row.append(toggle, link);
      item.append(row, subnav);
      navStack.at(-1).list.appendChild(item);
      navStack.push({ level, list: subnav, item });
    });

    sidebarNav.querySelectorAll('.course-sidebar__node').forEach((node) => {
      if (!node.querySelector(':scope > .course-sidebar__subnav > .course-sidebar__node')) {
        node.classList.add('has-no-children');
        node.querySelector(':scope > .course-sidebar__node-row .course-sidebar__toggle').disabled = true;
      }
    });

    const setExpanded = (node, expanded, exclusive = false) => {
      if (!node || node.classList.contains('has-no-children')) return;
      if (expanded && exclusive) {
        [...node.parentElement.children].forEach((sibling) => {
          if (sibling !== node && sibling.classList.contains('is-expanded')) {
            setExpanded(sibling, false);
          }
        });
      }
      node.classList.toggle('is-expanded', expanded);
      const toggle = node.querySelector(':scope > .course-sidebar__node-row .course-sidebar__toggle');
      toggle.setAttribute('aria-expanded', String(expanded));
      toggle.setAttribute(
        'aria-label',
        `${expanded ? 'Collapse' : 'Expand'} ${node.querySelector(':scope > .course-sidebar__node-row > a').textContent}`
      );
    };

    const setActive = (id) => {
      sidebarNav.querySelectorAll('.course-sidebar__node').forEach((node) => {
        node.classList.toggle('is-active', node.dataset.target === id);
        node.classList.remove('contains-active');
      });

      const active = [...sidebarNav.querySelectorAll('.course-sidebar__node')]
        .find((node) => node.dataset.target === id);
      if (!active) return;

      setExpanded(active, true, true);
      let ancestor = active.parentElement.closest('.course-sidebar__node');
      while (ancestor) {
        ancestor.classList.add('contains-active');
        setExpanded(ancestor, true, true);
        ancestor = ancestor.parentElement.closest('.course-sidebar__node');
      }
      active.scrollIntoView({ block: 'nearest' });
    };

    const showTopic = (id, scrollToTop = true) => {
      const page = pageByTopic.get(id) || homePage;
      const activeIndex = topicPages.indexOf(page);
      topicPages.forEach((topicPage) => {
        topicPage.hidden = topicPage !== page;
        topicPage.classList.toggle('is-current', topicPage === page);
      });

      previousButton.disabled = activeIndex <= 0;
      nextButton.disabled = activeIndex >= topicPages.length - 1;
      pageStatus.textContent = `Topic ${activeIndex + 1} of ${topicPages.length}`;

      const pageHeading = page.querySelector('h1, h2, h3, h4');
      previousButton.setAttribute(
        'aria-label',
        activeIndex > 0
          ? `Previous topic: ${topicPages[activeIndex - 1].querySelector('h1, h2, h3, h4')?.textContent || 'Course home'}`
          : 'No previous topic'
      );
      nextButton.setAttribute(
        'aria-label',
        activeIndex < topicPages.length - 1
          ? `Next topic: ${topicPages[activeIndex + 1].querySelector('h1, h2, h3, h4')?.textContent || 'Next topic'}`
          : 'No next topic'
      );
      document.title = pageHeading
        ? `${pageHeading.textContent} | AI in Architecture`
        : 'Machine Learning and Deep Learning for Architecture';

      setActive(page.dataset.topic);
      if (scrollToTop) window.scrollTo({ top: 0, behavior: 'auto' });
    };

    const updateFromHash = () => {
      const requestedId = decodeURIComponent(location.hash.slice(1));
      const requestedElement = requestedId ? document.getElementById(requestedId) : null;
      const containingPage = requestedElement?.closest('.course-topic-page');
      const topicId = pageByTopic.has(requestedId)
        ? requestedId
        : containingPage?.dataset.topic || 'course-home';
      showTopic(topicId, !requestedElement || requestedElement === containingPage?.querySelector('h1, h2, h3, h4'));
      if (requestedElement && requestedId !== topicId) {
        requestAnimationFrame(() => requestedElement.scrollIntoView());
      }
    };

    sidebarNav.addEventListener('click', (event) => {
      const toggle = event.target.closest('[data-toggle]');
      if (toggle) {
        const node = toggle.closest('.course-sidebar__node');
        setExpanded(node, !node.classList.contains('is-expanded'), true);
        return;
      }
      const link = event.target.closest('a');
      if (link && link.hash === location.hash) updateFromHash();
    });
    previousButton.addEventListener('click', () => {
      const currentIndex = topicPages.findIndex((page) => !page.hidden);
      if (currentIndex > 0) location.hash = topicPages[currentIndex - 1].dataset.topic;
    });
    nextButton.addEventListener('click', () => {
      const currentIndex = topicPages.findIndex((page) => !page.hidden);
      if (currentIndex < topicPages.length - 1) {
        location.hash = topicPages[currentIndex + 1].dataset.topic;
      }
    });
    window.addEventListener('hashchange', updateFromHash);
    updateFromHash();
  };

  const buildCodeLab = () => {
    const host = document.getElementById('interactive-neuron-lab');
    if (!host) return;

    const initialCode = `// Normalized building features
const inputs = {
  floorArea: 0.80,
  windowToWallRatio: 0.45,
  solarExposure: 0.70
};

// Learned parameters (illustrative values)
const weights = {
  floorArea: 0.60,
  windowToWallRatio: -0.35,
  solarExposure: 0.50
};
const bias = -0.10;

// Weighted sum: z = Σ(xᵢwᵢ) + b
const z =
  inputs.floorArea * weights.floorArea +
  inputs.windowToWallRatio * weights.windowToWallRatio +
  inputs.solarExposure * weights.solarExposure +
  bias;

// ReLU activation: max(0, z)
const neuronOutput = Math.max(0, z);

console.log("Weighted sum (z):", z.toFixed(4));
console.log("ReLU output:", neuronOutput.toFixed(4));
console.log(neuronOutput > 0
  ? "The neuron is active."
  : "The neuron is inactive.");`;

    host.innerHTML = `
      <section class="code-lab" data-code-lab>
        <div class="code-lab__header">
          <h4>Mini Code Lab: From Building Features to a Neuron Output</h4>
          <p>This simplified forward pass is an instructional example, not a trained building-performance model.</p>
        </div>
        <div class="code-lab__editor">
          <label for="neuron-code">Editable JavaScript</label>
          <textarea id="neuron-code" spellcheck="false" aria-label="Editable JavaScript code"></textarea>
          <div class="code-lab__actions">
            <button type="button" data-run>Run code</button>
            <button type="button" class="code-lab__reset" data-reset>Reset</button>
          </div>
        </div>
        <div class="code-lab__result">
          <label>Result</label>
          <output aria-live="polite">Select “Run code” to see the result.</output>
          <p class="code-lab__note">Shortcut: Command/Ctrl + Enter. Code runs inside a sandboxed browser frame.</p>
        </div>
        <iframe title="Code execution sandbox" sandbox="allow-scripts" hidden></iframe>
      </section>`;

    const lab = host.querySelector('[data-code-lab]');
    const editor = lab.querySelector('textarea');
    const runButton = lab.querySelector('[data-run]');
    const resetButton = lab.querySelector('[data-reset]');
    const output = lab.querySelector('output');
    const frame = lab.querySelector('iframe');
    const labId = 'neuron-code-lab';
    editor.value = initialCode;

    window.addEventListener('message', (event) => {
      if (event.source !== frame.contentWindow || event.data?.labId !== labId) return;
      output.textContent = event.data.lines.join('\n') || '(The program finished without output.)';
    });

    const run = () => {
      output.textContent = 'Running…';
      const encodedCode = btoa(unescape(encodeURIComponent(editor.value)));
      frame.srcdoc = `<!doctype html><meta charset="utf-8"><script>
        const lines = [];
        const format = value => {
          if (typeof value === 'string') return value;
          try { return JSON.stringify(value, null, 2); }
          catch (_) { return String(value); }
        };
        console.log = (...values) => lines.push(values.map(format).join(' '));
        console.error = (...values) => lines.push('Error: ' + values.map(format).join(' '));
        try {
          const code = decodeURIComponent(escape(atob('${encodedCode}')));
          const result = (0, eval)(code);
          if (result !== undefined) lines.push('Returned: ' + format(result));
        } catch (error) {
          lines.push('Error: ' + error.message);
        }
        parent.postMessage({ labId: '${labId}', lines }, '*');
      <\/script>`;
    };

    runButton.addEventListener('click', run);
    resetButton.addEventListener('click', () => {
      editor.value = initialCode;
      run();
    });
    editor.addEventListener('keydown', (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') run();
    });
    run();
  };

  buildCodeLab();
  buildCourseShell();
})();
