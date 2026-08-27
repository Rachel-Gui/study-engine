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
      window.dispatchEvent(new CustomEvent('course:topicchange', { detail: { id: page.dataset.topic } }));
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

  const svgNode = (name, attributes = {}) => {
    const node = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  };

  const buildRegressionStaticVisuals = () => {
    const comparison = document.getElementById('regression-classification-comparison');
    if (comparison) comparison.innerHTML = `
      <div class="prediction-compare" aria-label="Comparison of regression and classification">
        <section class="prediction-compare__card prediction-compare__card--active">
          <strong class="prediction-compare__type">Regression</strong>
          <div class="prediction-flow"><span>Building features</span><b>→</b><span>Model</span><b>→</b><span>Annual energy use</span></div>
          <p><strong>Continuous number:</strong> 1,370,845 kWh</p>
        </section>
        <section class="prediction-compare__card">
          <strong class="prediction-compare__type">Classification</strong>
          <div class="prediction-flow"><span>Building features</span><b>→</b><span>Model</span><b>→</b><span>Energy class</span></div>
          <p><strong>Discrete category:</strong> Low / Medium / High</p>
        </section>
      </div>`;
    const featureFlow = document.getElementById('regression-architectural-feature-flow');
    if (featureFlow) featureFlow.innerHTML = `
      <div class="feature-flow" aria-label="Building characteristics become model inputs for annual energy prediction">
        <div class="feature-flow__groups">
          <section><h5>Geometric features</h5><ul><li>Area</li><li>Height</li><li>Building length</li><li>Orientation</li><li>Relative compactness</li></ul></section>
          <section><h5>Non-geometric features</h5><ul><li>Year built</li><li>Occupancy / program information</li></ul></section>
          <section><h5>Environmental features</h5><ul><li>Tree canopy</li><li>Land-surface temperature</li></ul></section>
        </div>
        <div class="feature-flow__equation"><strong>Building characteristics (X)</strong><span>→</span><strong>Multiple Linear Regression</strong><span>→</span><strong>Predicted Annual Energy Use (ŷ)</strong></div>
      </div>`;
  };

  const buildConceptRegression = () => {
    const host = document.getElementById('interactive-regression-plot');
    if (!host) return;

    const points = [
      { x: 14, y: 23 }, { x: 25, y: 34 }, { x: 36, y: 31 },
      { x: 48, y: 53 }, { x: 61, y: 57 }, { x: 72, y: 73 }, { x: 86, y: 78 }
    ];
    host.innerHTML = `
      <section class="regression-visual">
        <div class="regression-visual__header">
          <div><h5>Drag → inspect the residual → refit</h5><p>Move a purple observation, watch its dashed error gap change, then refit the line.</p></div>
          <output data-equation aria-live="polite"></output>
        </div>
        <svg viewBox="0 0 720 390" role="img" aria-label="Observed data, fitted line, predictions, and residual gaps"></svg>
        <div class="regression-visual__controls">
          <div><button type="button" data-fit disabled>Refit best-fit line</button><p>Find the least-squares line for the current observations.</p></div>
          <button type="button" class="secondary" data-reset-points>Reset observations</button>
        </div>
        <details class="regression-visual__manual"><summary>Explore the line manually</summary><p><strong>Slope</strong> — how much predicted y changes when x increases by one unit.</p><label>Slope <input data-slope type="range" min="-0.2" max="1.4" value="0.78" step="0.02"><output></output></label><p><strong>Intercept</strong> — the predicted y value when x = 0. It may not have a meaningful architectural interpretation when x = 0 lies outside the data range.</p><label>Intercept <input data-intercept type="range" min="0" max="50" value="12" step="1"><output></output></label></details>
      </section>`;

    const svg = host.querySelector('svg');
    const slopeInput = host.querySelector('[data-slope]');
    const interceptInput = host.querySelector('[data-intercept]');
    const equation = host.querySelector('[data-equation]');
    const fitButton = host.querySelector('[data-fit]');
    const xScale = (value) => 70 + value * 5.9;
    const yScale = (value) => 335 - value * 3.05;
    let dragging = null;

    const bestFit = () => {
      const meanX = points.reduce((sum, point) => sum + point.x, 0) / points.length;
      const meanY = points.reduce((sum, point) => sum + point.y, 0) / points.length;
      const numerator = points.reduce((sum, point) => sum + (point.x - meanX) * (point.y - meanY), 0);
      const denominator = points.reduce((sum, point) => sum + (point.x - meanX) ** 2, 0);
      const slope = numerator / denominator;
      return { slope, intercept: meanY - slope * meanX };
    };
    const fitLine = () => {
      const startSlope = Number(slopeInput.value), startIntercept = Number(interceptInput.value);
      const target = bestFit(), started = performance.now(), duration = 420;
      const animate = (now) => {
        const progress = Math.min(1, (now - started) / duration);
        const eased = 1 - (1 - progress) ** 3;
        slopeInput.value = startSlope + (target.slope - startSlope) * eased;
        interceptInput.value = startIntercept + (target.intercept - startIntercept) * eased;
        draw();
        if (progress < 1) requestAnimationFrame(animate);
        else fitButton.disabled = true;
      };
      requestAnimationFrame(animate);
    };

    const draw = () => {
      const slope = Number(slopeInput.value);
      const intercept = Number(interceptInput.value);
      svg.replaceChildren();
      svg.append(
        svgNode('line', { x1: 70, y1: 335, x2: 660, y2: 335, class: 'plot-axis' }),
        svgNode('line', { x1: 70, y1: 335, x2: 70, y2: 30, class: 'plot-axis' })
      );
      const xLabel = svgNode('text', { x: 365, y: 378, class: 'plot-label' });
      xLabel.textContent = 'Building area (illustrative scale)';
      const yLabel = svgNode('text', { x: 22, y: 195, class: 'plot-label', transform: 'rotate(-90 22 195)' });
      yLabel.textContent = 'Annual energy use (illustrative scale)';
      svg.append(xLabel, yLabel);

      points.forEach((point, index) => {
        const predicted = slope * point.x + intercept;
        svg.append(svgNode('line', {
          x1: xScale(point.x), y1: yScale(point.y),
          x2: xScale(point.x), y2: yScale(predicted), class: 'plot-residual'
        }));
        svg.append(svgNode('circle', {
          cx: xScale(point.x), cy: yScale(predicted), r: 4, class: 'plot-prediction'
        }));
        const observed = svgNode('circle', {
          cx: xScale(point.x), cy: yScale(point.y), r: 8, class: 'plot-observed',
          tabindex: 0, 'data-point': index, 'aria-label': `Observed point ${index + 1}. Drag to move.`
        });
        svg.append(observed);
        if (index === 3 && !host.dataset.interacted) {
          const cue = svgNode('g', { class: 'drag-cue', 'aria-hidden': 'true' });
          const cueText = svgNode('text', { x: xScale(point.x) + 17, y: yScale(point.y) - 13 });
          cueText.textContent = 'Drag me ↕';
          cue.append(svgNode('line', { x1: xScale(point.x) + 7, y1: yScale(point.y) - 6, x2: xScale(point.x) + 14, y2: yScale(point.y) - 11 }), cueText);
          svg.append(cue);
        }
      });
      svg.append(svgNode('line', {
        x1: xScale(0), y1: yScale(intercept), x2: xScale(100),
        y2: yScale(slope * 100 + intercept), class: 'plot-fit'
      }));
      equation.textContent = `ŷ = ${slope.toFixed(2)}x + ${intercept.toFixed(0)}`;
      slopeInput.nextElementSibling.textContent = slope.toFixed(2);
      interceptInput.nextElementSibling.textContent = intercept.toFixed(0);
    };

    const movePoint = (event) => {
      if (dragging === null) return;
      const bounds = svg.getBoundingClientRect();
      const x = ((event.clientX - bounds.left) / bounds.width) * 720;
      const y = ((event.clientY - bounds.top) / bounds.height) * 390;
      points[dragging].x = Math.max(0, Math.min(100, (x - 70) / 5.9));
      points[dragging].y = Math.max(0, Math.min(100, (335 - y) / 3.05));
      host.dataset.interacted = 'true';
      fitButton.disabled = false;
      draw();
    };
    svg.addEventListener('pointerdown', (event) => {
      const point = event.target.closest('[data-point]');
      if (!point) return;
      dragging = Number(point.dataset.point);
      svg.setPointerCapture(event.pointerId);
    });
    svg.addEventListener('pointermove', movePoint);
    svg.addEventListener('pointerup', () => { dragging = null; });
    const manualChange = () => { host.dataset.interacted = 'true'; fitButton.disabled = false; draw(); };
    slopeInput.addEventListener('input', manualChange);
    interceptInput.addEventListener('input', manualChange);
    fitButton.addEventListener('click', fitLine);
    host.querySelector('[data-reset-points]').addEventListener('click', () => {
      const defaults = [[14, 23], [25, 34], [36, 31], [48, 53], [61, 57], [72, 73], [86, 78]];
      points.forEach((point, index) => { [point.x, point.y] = defaults[index]; });
      slopeInput.value = 0.78;
      interceptInput.value = 12;
      delete host.dataset.interacted;
      fitButton.disabled = true;
      draw();
    });
    draw();
  };

  const parseCsv = (text) => {
    const rows = [];
    let row = [], value = '', quoted = false;
    for (let index = 0; index < text.length; index += 1) {
      const character = text[index];
      if (character === '"' && quoted && text[index + 1] === '"') { value += '"'; index += 1; }
      else if (character === '"') quoted = !quoted;
      else if (character === ',' && !quoted) { row.push(value); value = ''; }
      else if ((character === '\n' || character === '\r') && !quoted) {
        if (character === '\r' && text[index + 1] === '\n') index += 1;
        row.push(value); value = '';
        if (row.some((cell) => cell.length)) rows.push(row);
        row = [];
      } else value += character;
    }
    if (value || row.length) { row.push(value); rows.push(row); }
    const headers = rows.shift().map((header) => header.replace(/^\uFEFF/, '').trim());
    return rows.map((cells) => Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ''])));
  };

  const solveLinearSystem = (matrix, vector) => {
    const augmented = matrix.map((row, index) => [...row, vector[index]]);
    for (let column = 0; column < matrix.length; column += 1) {
      let pivot = column;
      for (let row = column + 1; row < matrix.length; row += 1) {
        if (Math.abs(augmented[row][column]) > Math.abs(augmented[pivot][column])) pivot = row;
      }
      [augmented[column], augmented[pivot]] = [augmented[pivot], augmented[column]];
      if (Math.abs(augmented[column][column]) < 1e-10) throw new Error('singular-design-matrix');
      const divisor = augmented[column][column];
      for (let item = column; item <= matrix.length; item += 1) augmented[column][item] /= divisor;
      for (let row = 0; row < matrix.length; row += 1) {
        if (row === column) continue;
        const factor = augmented[row][column];
        for (let item = column; item <= matrix.length; item += 1) augmented[row][item] -= factor * augmented[column][item];
      }
    }
    return augmented.map((row) => row.at(-1));
  };

  const findRedundantFeatures = (rows, features) => {
    const basis = [];
    const redundant = [];
    const columns = [null, ...features];
    columns.forEach((feature, columnIndex) => {
      const original = rows.map((row) => columnIndex === 0 ? 1 : Number(row[feature]));
      const originalNorm = Math.sqrt(original.reduce((sum, value) => sum + value * value, 0));
      let residual = [...original];
      for (let pass = 0; pass < 2; pass += 1) {
        basis.forEach((unit) => {
          const projection = residual.reduce((sum, value, index) => sum + value * unit[index], 0);
          residual = residual.map((value, index) => value - projection * unit[index]);
        });
      }
      const residualNorm = Math.sqrt(residual.reduce((sum, value) => sum + value * value, 0));
      if (originalNorm === 0 || residualNorm <= Math.max(1, originalNorm) * 1e-9) {
        if (feature) redundant.push(feature);
      } else basis.push(residual.map((value) => value / residualNorm));
    });
    return redundant;
  };

  const fitOls = (rows, features) => {
    const redundant = findRedundantFeatures(rows, features);
    if (redundant.length) throw new Error(`Redundant columns detected in the selected design matrix: ${redundant.join(', ')}. Their information is linearly dependent on columns already selected, so the coefficients are not uniquely identifiable. This is multicollinearity among predictors—not evidence that the X–Y relationship is nonlinear.`);
    const columns = features.length + 1;
    const matrix = Array.from({ length: columns }, () => Array(columns).fill(0));
    const vector = Array(columns).fill(0);
    rows.forEach((row) => {
      const x = [1, ...features.map((feature) => Number(row[feature]))];
      const y = Number(row.Energy_Use_kWh);
      for (let i = 0; i < columns; i += 1) {
        vector[i] += x[i] * y;
        for (let j = 0; j < columns; j += 1) matrix[i][j] += x[i] * x[j];
      }
    });
    try { return solveLinearSystem(matrix, vector); }
    catch (_) { throw new Error('The JavaScript OLS solver found a singular design matrix. The selected predictors contain redundant or linearly dependent information, so regression coefficients are not uniquely identifiable. This is multicollinearity among predictors—not a nonlinear X–Y relationship. Remove a redundant predictor and retrain.'); }
  };

  const seededSplit = (rows) => {
    const shuffled = [...rows];
    let seed = 42;
    const random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
    for (let index = shuffled.length - 1; index > 0; index -= 1) {
      const swap = Math.floor(random() * (index + 1));
      [shuffled[index], shuffled[swap]] = [shuffled[swap], shuffled[index]];
    }
    const testSize = Math.ceil(shuffled.length * 0.2);
    return { test: shuffled.slice(0, testSize), train: shuffled.slice(testSize) };
  };

  const modelMetrics = (rows, features, coefficients) => {
    const actual = rows.map((row) => Number(row.Energy_Use_kWh));
    const predicted = rows.map((row) => coefficients[0] + features.reduce(
      (sum, feature, index) => sum + coefficients[index + 1] * Number(row[feature]), 0
    ));
    const mean = actual.reduce((sum, value) => sum + value, 0) / actual.length;
    const squaredError = actual.reduce((sum, value, index) => sum + (value - predicted[index]) ** 2, 0);
    const totalSquares = actual.reduce((sum, value) => sum + (value - mean) ** 2, 0);
    return { actual, predicted, rmse: Math.sqrt(squaredError / actual.length), r2: 1 - squaredError / totalSquares };
  };

  const histogramSvg = (values, label) => {
    const bins = 12;
    const min = Math.min(...values), max = Math.max(...values);
    const counts = Array(bins).fill(0);
    values.forEach((value) => counts[Math.min(bins - 1, Math.floor(((value - min) / (max - min || 1)) * bins))] += 1);
    const highest = Math.max(...counts);
    const bars = counts.map((count, index) => {
      const height = count / highest * 104;
      return `<rect x="${34 + index * 22}" y="${130 - height}" width="18" height="${height}" />`;
    }).join('');
    return `<svg class="mini-histogram" viewBox="0 0 320 170" role="img" aria-label="${label} distribution">${bars}<line x1="30" y1="130" x2="302" y2="130"/><text x="166" y="157">${label}</text></svg>`;
  };

  const scatterSvg = (actual, predicted, options = {}) => {
    const values = [...actual, ...predicted, ...(options.previous || [])];
    const min = options.min ?? Math.min(...values);
    const max = options.max ?? Math.max(...values);
    const scale = (value) => 40 + ((Math.max(min, Math.min(max, value)) - min) / (max - min || 1)) * 240;
    const y = (value) => 340 - scale(value);
    const previous = options.previous || null;
    const connectors = options.compare && previous ? actual.map((value, index) => `<line class="prediction-shift" x1="${scale(value)}" x2="${scale(value)}" y1="${y(previous[index])}" y2="${y(predicted[index])}" />`).join('') : '';
    const ghosts = options.compare && previous ? actual.map((value, index) => `<circle class="prediction-ghost" cx="${scale(value)}" cy="${y(previous[index])}" r="5"><title>Previous prediction ${Math.round(previous[index]).toLocaleString()} kWh</title></circle>`).join('') : '';
    const points = actual.map((value, index) => `<circle class="prediction-current" cx="${scale(value)}" cy="${y(predicted[index])}" r="5"><title>Actual ${Math.round(value).toLocaleString()} kWh; current prediction ${Math.round(predicted[index]).toLocaleString()} kWh</title>${previous ? `<animate attributeName="cy" from="${y(previous[index])}" to="${y(predicted[index])}" dur="0.45s" fill="freeze" />` : ''}</circle>`).join('');
    return `<svg class="prediction-scatter" viewBox="0 0 340 340" role="img" aria-label="Predicted versus actual energy use"><line x1="${scale(min)}" y1="${y(min)}" x2="${scale(max)}" y2="${y(max)}" class="identity"/>${connectors}${ghosts}${points}<line x1="40" y1="300" x2="300" y2="300"/><line x1="40" y1="300" x2="40" y2="40"/><text x="170" y="330">Actual energy use</text><text x="16" y="180" transform="rotate(-90 16 180)">Predicted energy use</text></svg>`;
  };

  const heatmapHtml = (payload) => {
    const color = (value) => value >= 0
      ? `rgba(75,46,131,${0.12 + Math.abs(value) * 0.78})`
      : `rgba(239,120,158,${0.12 + Math.abs(value) * 0.78})`;
    const short = { Energy_Use_kWh: 'Energy', Area_m: 'Area', Year_Built: 'Year', Building_Length_m: 'Length', Tree_Canopy: 'Canopy', Land_Surface_Temp: 'LST' };
    const label = (name) => short[name] || name;
    return `<div class="correlation-grid" style="--columns:${payload.labels.length}"><span></span>${payload.labels.map((name) => `<span class="correlation-grid__column" title="${name}">${label(name)}</span>`).join('')}${payload.values.map((row, rowIndex) => `<span class="correlation-grid__label" title="${payload.labels[rowIndex]}">${label(payload.labels[rowIndex])}</span>${row.map((value, columnIndex) => `<span class="correlation-grid__cell" style="background:${color(value)}" title="${payload.labels[rowIndex]} × ${payload.labels[columnIndex]}: ${value.toFixed(2)}">${value.toFixed(2)}</span>`).join('')}`).join('')}</div>`;
  };

  const buildPythonWorkflow = () => {
    const host = document.getElementById('python-regression-workflow');
    if (!host) return;
    const steps = [
      { title: 'Load and inspect data', explanation: 'Read the UW CSV and inspect its structure, a focused preview, and missing values.', code: `import pandas as pd\n\ndf = pd.read_csv('UW_building_energy.csv')\npreview_columns = ['Name', 'Energy_Use_kWh', 'Area_m',\n                   'Height', 'Year_Built', 'Occupants']\nresult = {\n    "shape": list(df.shape),\n    "columns": df.columns.tolist(),\n    "head": df[preview_columns].head().fillna('').to_dict(orient='records'),\n    "missing": int(df.isna().sum().sum())\n}` },
      { title: 'Visualize distributions', explanation: 'Use NumPy to bin the real energy-use and floor-area observations.', code: `import numpy as np\n\ndef histogram(column):\n    counts, edges = np.histogram(df[column], bins=12)\n    return {"counts": counts.tolist(), "edges": edges.tolist()}\n\nresult = {\n    "energy": histogram('Energy_Use_kWh'),\n    "area": histogram('Area_m')\n}` },
      { title: 'Remove outliers', explanation: 'Apply the two thresholds specified by the assignment and retain a separate model-ready dataframe.', code: `outlier_mask = (df['Energy_Use_kWh'] > 10_000_000) | (df['Area_m'] > 60_000)\nremoved = df.loc[outlier_mask, ['Name', 'Energy_Use_kWh', 'Area_m']]\ndf_noout = df.loc[~outlier_mask].copy()\n\nresult = {\n    "original": len(df),\n    "removed_count": len(removed),\n    "remaining": len(df_noout),\n    "removed": removed.to_dict(orient='records')\n}` },
      { title: 'Explore relationships', explanation: 'Calculate correlations among a readable subset of architectural variables.', code: `corr_features = ['Energy_Use_kWh', 'Area_m', 'Height', 'Year_Built',\n                 'Occupants', 'Building_Length_m', 'Tree_Canopy',\n                 'Land_Surface_Temp']\ncorr = df_noout[corr_features].corr()\nresult = {"labels": corr_features, "values": corr.values.tolist()}` },
      { title: 'Select X and Y / split data', explanation: 'Define inputs and target, then create the reproducible 80/20 training and testing split.', code: `from sklearn.model_selection import train_test_split\n\nfeatures = ['Area_m', 'Height', 'Year_Built']\ntarget = 'Energy_Use_kWh'\nX = df_noout[features]\ny = df_noout[target]\nX_train, X_test, y_train, y_test = train_test_split(\n    X, y, test_size=0.2, random_state=42\n)\nresult = {"features": features, "target": target,\n          "train_count": len(X_train), "test_count": len(X_test)}` },
      { title: 'Fit the regression model', explanation: 'Fit the notebook’s multiple linear regression using only the training buildings.', code: `from sklearn.linear_model import LinearRegression\n\nmlr_model = LinearRegression()\nmlr_model.fit(X_train, y_train)\nresult = {\n    "intercept": float(mlr_model.intercept_),\n    "coefficients": dict(zip(features, mlr_model.coef_.tolist()))\n}` },
      { title: 'Predict', explanation: 'Predict unseen testing buildings and inspect actual values, predictions, and residuals.', code: `test_pred = mlr_model.predict(X_test)\ntrain_pred = mlr_model.predict(X_train)\nprediction_examples = pd.DataFrame({\n    'Actual energy use': y_test.to_numpy(),\n    'Predicted energy use': test_pred,\n    'Residual': y_test.to_numpy() - test_pred\n}).head(6)\nresult = {"rows": prediction_examples.to_dict(orient='records')}` },
      { title: 'Evaluate', explanation: 'Calculate train/test RMSE and testing R², then compare every test prediction with its actual value.', code: `from sklearn.metrics import mean_squared_error, r2_score\n\nresult = {\n    "train_rmse": float(mean_squared_error(y_train, train_pred) ** 0.5),\n    "test_rmse": float(mean_squared_error(y_test, test_pred) ** 0.5),\n    "test_r2": float(r2_score(y_test, test_pred)),\n    "actual": y_test.tolist(),\n    "predicted": test_pred.tolist()\n}` }
    ];
    host.innerHTML = `<section class="python-workflow"><div class="python-workflow__runtime" data-python-status>Open this episode to prepare the Python environment.</div><div class="python-workflow__fallback" data-python-fallback hidden><label>Connect UW_building_energy.csv <input type="file" accept=".csv,text/csv"></label><p>Select the file once in either regression activity. It stays in this browser and is copied only into Pyodide's temporary in-memory filesystem.</p></div><div class="python-workflow__steps">${steps.map((step, index) => `<section class="python-step" data-python-step="${index}"><header><span>${index + 1}</span><div><h5>${step.title}</h5><p>${step.explanation}</p></div></header><pre><code class="language-python"></code></pre><button type="button" data-run-python="${index}" ${index ? 'disabled' : ''}>Run step</button><div class="python-step__output" data-python-output aria-live="polite">Run this step to see its Python output.</div></section>`).join('')}</div></section>`;
    host.querySelectorAll('[data-python-step]').forEach((node, index) => { node.querySelector('code').textContent = steps[index].code; });
    const status = host.querySelector('[data-python-status]');
    const fallback = host.querySelector('[data-python-fallback]');
    let pythonWorker = null, csvText = null, preparing = null, requestId = 0;
    const pending = new Map();
    const workerSource = [
      "let pyodideRuntime = null, modelingReady = false;",
      "const INDEX_URL = 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/';",
      "const respond = (id, ok, payload) => self.postMessage({ id, ok, ...payload });",
      "self.onmessage = async ({ data }) => {",
      "  const { id, type } = data;",
      "  try {",
      "    if (type === 'init') {",
      "      if (!pyodideRuntime) {",
      "        self.postMessage({ type: 'status', message: 'Preparing Python environment in the background…' });",
      "        importScripts(INDEX_URL + 'pyodide.js');",
      "        pyodideRuntime = await loadPyodide({ indexURL: INDEX_URL });",
      "        self.postMessage({ type: 'status', message: 'Loading pandas and NumPy for Steps 1–4…' });",
      "        await pyodideRuntime.loadPackage(['pandas', 'numpy']);",
      "      }",
      "      pyodideRuntime.FS.writeFile('UW_building_energy.csv', data.csvText, { encoding: 'utf8' });",
      "      respond(id, true, { stage: 'base' });",
      "    } else if (type === 'ensure-modeling') {",
      "      if (!modelingReady) {",
      "        self.postMessage({ type: 'status', message: 'Loading scikit-learn for Steps 5–8…' });",
      "        await pyodideRuntime.loadPackage('scikit-learn'); modelingReady = true;",
      "      }",
      "      respond(id, true, { stage: 'modeling' });",
      "    } else if (type === 'run') {",
      "      const json = await pyodideRuntime.runPythonAsync('import json\\n' + data.code + '\\njson.dumps(result)');",
      "      respond(id, true, { json });",
      "    }",
      "  } catch (error) { respond(id, false, { error: error.message || String(error) }); }",
      "};"
    ].join('\n');
    const createWorker = () => {
      if (pythonWorker) return pythonWorker;
      pythonWorker = new Worker(URL.createObjectURL(new Blob([workerSource], { type: 'text/javascript' })));
      pythonWorker.onmessage = ({ data }) => {
        if (data.type === 'status') { status.textContent = data.message; return; }
        const request = pending.get(data.id); if (!request) return;
        pending.delete(data.id); data.ok ? request.resolve(data) : request.reject(new Error(data.error));
      };
      return pythonWorker;
    };
    const requestWorker = (type, payload = {}) => new Promise((resolve, reject) => {
      const id = ++requestId; pending.set(id, { resolve, reject }); createWorker().postMessage({ id, type, ...payload });
    });
    const prepare = async () => {
      if (preparing) return preparing;
      preparing = (async () => {
        if (!csvText) {
          try { const response = await fetch('reference_materials/UW_building_energy.csv'); if (!response.ok) throw new Error(); csvText = await response.text(); }
          catch (_) { fallback.hidden = false; status.textContent = 'Connect the local UW CSV before running Python.'; throw new Error('UW CSV is not available in this deployment.'); }
        }
        await requestWorker('init', { csvText });
        status.textContent = 'Python ready for Steps 1–4. scikit-learn will load only when Step 5 needs it.';
        return true;
      })().catch((error) => { preparing = null; status.textContent = `Python environment unavailable: ${error.message}`; throw error; });
      return preparing;
    };

    const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
    const tableLabels = { Energy_Use_kWh: 'Energy use', Area_m: 'Area', Year_Built: 'Year built', 'Actual energy use': 'Actual', 'Predicted energy use': 'Predicted' };
    const table = (rows) => `<div class="python-table-wrap"><table><thead><tr>${Object.keys(rows[0] || {}).map((key) => `<th title="${escapeHtml(key)}">${tableLabels[key] || escapeHtml(key)}</th>`).join('')}</tr></thead><tbody>${rows.map((row) => `<tr>${Object.values(row).map((value) => `<td>${typeof value === 'number' ? Math.round(value).toLocaleString() : escapeHtml(value)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    const binsSvg = (item, label) => {
      const highest = Math.max(...item.counts);
      return `<svg class="mini-histogram" viewBox="0 0 320 170" role="img" aria-label="${label} distribution">${item.counts.map((count, index) => { const height = count / highest * 104; return `<rect x="${34 + index * 22}" y="${130 - height}" width="18" height="${height}" />`; }).join('')}<line x1="30" y1="130" x2="302" y2="130"/><text x="166" y="157">${label}</text></svg>`;
    };
    const render = (index, result) => {
      if (index === 0) return `<div class="python-summary"><strong>${result.shape[0]} buildings</strong><strong>${result.shape[1]} columns</strong><strong>${result.missing} missing values</strong></div>${table(result.head)}<details class="all-columns"><summary>View all 19 column names</summary><p>${result.columns.join(' · ')}</p></details>`;
      if (index === 1) return `<div class="python-histograms">${binsSvg(result.energy, 'Energy use (kWh)')}${binsSvg(result.area, 'Building area (m²)')}</div>`;
      if (index === 2) return `<div class="outlier-flow"><strong>${result.original} original buildings</strong><span>→</span><strong>${result.removed_count} removed</strong><span>→</span><strong>${result.remaining} model-ready</strong></div><details><summary>Show removed observations</summary>${table(result.removed)}</details>`;
      if (index === 3) return `${heatmapHtml(result)}<p class="python-prompt">Which features appear most strongly related to annual energy use?</p>`;
      if (index === 4) return `<div class="xy-split"><section><strong>X</strong><p>${result.features.join(' · ')}</p></section><section><strong>Y</strong><p>Annual energy consumption</p></section><section><strong>${result.train_count}</strong><p>training buildings</p></section><section><strong>${result.test_count}</strong><p>testing buildings</p></section></div>`;
      if (index === 5) return `<p><strong>Intercept:</strong> ${Math.round(result.intercept).toLocaleString()}</p><div class="coefficient-list">${Object.entries(result.coefficients).map(([key, value]) => `<span>${key}<strong>${Math.round(value).toLocaleString()}</strong></span>`).join('')}</div>`;
      if (index === 6) return table(result.rows);
      return `<div class="metric-cards metric-cards--compact"><section><strong>${Math.round(result.train_rmse).toLocaleString()} kWh</strong><p>Training RMSE</p></section><section><strong>${Math.round(result.test_rmse).toLocaleString()} kWh</strong><p>Testing RMSE</p></section><section><strong>${result.test_r2.toFixed(3)}</strong><p>Testing R²</p></section></div>${scatterSvg(result.actual, result.predicted)}`;
    };
    host.addEventListener('click', async (event) => {
      const button = event.target.closest('[data-run-python]'); if (!button) return;
      const index = Number(button.dataset.runPython), output = host.querySelector(`[data-python-step="${index}"] [data-python-output]`);
      button.disabled = true; output.textContent = 'Running Python…';
      try {
        await prepare();
        if (index >= 4) { await requestWorker('ensure-modeling'); status.textContent = 'Python ready — pandas, NumPy, and scikit-learn loaded.'; }
        const response = await requestWorker('run', { code: steps[index].code });
        output.innerHTML = render(index, JSON.parse(response.json));
        button.textContent = 'Run again'; button.disabled = false;
        const next = host.querySelector(`[data-run-python="${index + 1}"]`); if (next) next.disabled = false;
      } catch (error) { output.textContent = `Python error: ${error.message}`; button.disabled = false; }
    });
    fallback.querySelector('input').addEventListener('change', async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      window.dispatchEvent(new CustomEvent('uw:csvconnected', { detail: { text: await file.text(), source: file.name } }));
    });
    window.addEventListener('uw:csvconnected', (event) => {
      csvText = event.detail.text;
      fallback.hidden = true;
      preparing = null;
      status.textContent = `Data connected from ${event.detail.source}. Preparing the shared Python environment…`;
      prepare().catch(() => {});
    });
    window.addEventListener('course:topicchange', (event) => {
      if (['episode-2.6-demo-uw-campus-building-energy-regression', 'regression-guided-workflow'].includes(event.detail.id)) prepare().catch(() => {});
    });
    const preload = () => prepare().catch(() => {});
    if ('requestIdleCallback' in window) window.requestIdleCallback(preload, { timeout: 3500 });
    else window.setTimeout(preload, 1800);
  };

  const buildUwRegressionDemo = () => {
    const host = document.getElementById('uw-regression-demo');
    if (!host) return;
    const features = [
      'Height', 'Area_m', 'Building_Length_m', 'Orientation (degrees north)',
      'Relative Compactness', 'Year_Built', 'Occupants', 'apartments', 'parking',
      'stadium', 'university', 'utility', 'warehouse', 'Tree_Canopy', 'Land_Surface_Temp'
    ];
    const labels = {
      Area_m: 'Area', Building_Length_m: 'Building length',
      'Orientation (degrees north)': 'Orientation', 'Relative Compactness': 'Relative compactness',
      Year_Built: 'Year built', Tree_Canopy: 'Tree canopy', Land_Surface_Temp: 'Land-surface temperature'
    };
    const groups = {
      Geometric: ['Area_m', 'Height', 'Building_Length_m', 'Orientation (degrees north)', 'Relative Compactness'],
      'Non-geometric': ['Year_Built', 'Occupants', 'apartments', 'parking', 'stadium', 'university', 'utility', 'warehouse'],
      Environmental: ['Tree_Canopy', 'Land_Surface_Temp']
    };
    host.innerHTML = `
      <section class="uw-demo">
        <div class="uw-demo__status" data-status aria-live="polite">Loading the local UW dataset…</div>
        <div class="uw-demo__fallback" data-fallback hidden>
          <label for="uw-csv">Connect UW_building_energy.csv</label>
          <input id="uw-csv" type="file" accept=".csv,text/csv">
          <p>The reference CSV is not deployed. Select it once here or in the guided workflow; both activities share the same browser-local copy.</p>
        </div>
        <div data-interface hidden>
          <div class="uw-demo__overview" data-overview></div>
          <div class="uw-demo__workspace">
            <fieldset><legend>Choose features</legend><div class="feature-toggles">${Object.entries(groups).map(([group, items]) => `<section><h5>${group}</h5>${items.map((feature) => `<label><input type="checkbox" value="${feature}" ${['Area_m', 'Height', 'Year_Built'].includes(feature) ? 'checked' : ''}><span>${labels[feature] || feature}</span></label>`).join('')}</section>`).join('')}</div><button type="button" data-train>Train model</button></fieldset>
            <div class="uw-demo__results" data-results aria-live="polite"></div>
          </div>
          <div class="uw-demo__plot" data-plot></div>
        </div>
      </section>`;
    const status = host.querySelector('[data-status]');
    const fallback = host.querySelector('[data-fallback]');
    const interfaceNode = host.querySelector('[data-interface]');
    let data = [];
    let previousModel = null, currentModel = null, axisMax = 1;

    const renderFeaturePlot = (compare = false) => {
      if (!currentModel) return;
      const plot = host.querySelector('[data-plot]');
      plot.innerHTML = `<div><h5>Predicted versus actual — test buildings</h5><p>The dashed diagonal and axes stay fixed across retraining.</p><label class="compare-models"><input type="checkbox" data-compare-models ${compare ? 'checked' : ''} ${previousModel ? '' : 'disabled'}> Compare previous model</label></div>${scatterSvg(currentModel.actual, currentModel.predicted, { min: 0, max: axisMax, previous: previousModel?.predicted, compare })}`;
    };

    const load = (text, source) => {
      const parsed = parseCsv(text).map((row) => {
        const normalized = {};
        Object.entries(row).forEach(([key, value]) => { normalized[key.trim()] = value.trim(); });
        return normalized;
      });
      const required = ['Energy_Use_kWh', 'Area_m', 'Height', 'Year_Built'];
      if (!parsed.length || required.some((column) => !(column in parsed[0]))) throw new Error('This file does not match the UW building-energy schema.');
      data = parsed;
      fallback.hidden = true;
      interfaceNode.hidden = false;
      status.textContent = `Data connected from ${source}. Results below are calculated from ${data.length} real records.`;
      const filtered = data.filter((row) => Number(row.Energy_Use_kWh) <= 10000000 && Number(row.Area_m) <= 60000);
      axisMax = Math.max(...filtered.map((row) => Number(row.Energy_Use_kWh))) * 1.05;
      host.querySelector('[data-overview]').innerHTML = `<section><strong>${data.length}</strong><span>buildings loaded</span></section><section><strong>${Object.keys(data[0]).length}</strong><span>dataset columns</span></section><section><strong>${data.length - filtered.length}</strong><span>outliers removed</span></section><section><strong>${filtered.length}</strong><span>model-ready rows</span></section>`;
      train();
    };

    const train = (requestedFeatures = null, renderInterface = true) => {
      const selected = requestedFeatures || [...host.querySelectorAll('.feature-toggles input:checked')].map((input) => input.value);
      const results = host.querySelector('[data-results]');
      if (!selected.length) { if (renderInterface) { results.innerHTML = '<p class="uw-demo__error">Select at least one feature before training.</p>'; host.querySelector('[data-plot]').replaceChildren(); } return null; }
      const filtered = data.filter((row) => Number(row.Energy_Use_kWh) <= 10000000 && Number(row.Area_m) <= 60000)
        .filter((row) => ['Energy_Use_kWh', ...selected].every((column) => Number.isFinite(Number(row[column]))));
      try {
        const split = seededSplit(filtered);
        const coefficients = fitOls(split.train, selected);
        const trainResult = modelMetrics(split.train, selected, coefficients);
        const testResult = modelMetrics(split.test, selected, coefficients);
        const formatter = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 });
        const current = { features: [...selected], trainRmse: trainResult.rmse, testRmse: testResult.rmse, r2: testResult.r2, actual: testResult.actual, predicted: testResult.predicted };
        if (renderInterface) {
          previousModel = currentModel;
          const rmseDelta = previousModel ? (current.testRmse - previousModel.testRmse) / previousModel.testRmse : null;
          const r2Delta = previousModel ? current.r2 - previousModel.r2 : null;
          const delta = (value, lowerIsBetter = false) => value === null ? '' : `<span class="model-delta ${(lowerIsBetter ? value < 0 : value > 0) ? 'positive' : ''}">${value < 0 ? '↓' : '↑'} ${lowerIsBetter ? Math.abs(value * 100).toFixed(0) + '%' : Math.abs(value).toFixed(3)} vs previous</span>`;
          results.innerHTML = `<div class="metric-cards metric-cards--compact"><section><strong>${formatter.format(trainResult.rmse)} kWh</strong><p>Training RMSE</p></section><section><strong>${formatter.format(testResult.rmse)} kWh</strong>${delta(rmseDelta, true)}<p>Testing RMSE</p></section><section><strong>${testResult.r2.toFixed(3)}</strong>${delta(r2Delta)}<p>Testing R²</p></section></div><h5>Selected features</h5><p>${selected.map((feature) => labels[feature] || feature).join(' · ')}</p><h5>Regression coefficients</h5><div class="coefficient-list"><span>Intercept <strong>${formatter.format(coefficients[0])}</strong></span>${selected.map((feature, index) => `<span>${labels[feature] || feature} <strong>${formatter.format(coefficients[index + 1])}</strong></span>`).join('')}</div><aside class="coefficient-note" aria-label="How to interpret regression coefficients"><h5>How to interpret coefficients</h5><dl><div><dt>Direction</dt><dd>A positive coefficient means predicted energy use tends to increase as this feature increases, holding the other selected features constant. A negative coefficient means the predicted value tends to decrease.</dd></div><div><dt>Units</dt><dd>A coefficient describes the predicted change in energy use for a one-unit change in that feature. Because features use different units—such as m², meters, years, or binary categories—raw coefficient magnitudes should not be directly compared as feature importance.</dd></div><div><dt>Correlated inputs</dt><dd>If selected predictors contain overlapping information, the model may distribute their effects differently. Individual coefficients can therefore change substantially when correlated features are added or removed. This is related to multicollinearity and connects to the linear-dependence message shown when coefficients cannot be uniquely identified.</dd></div></dl></aside>`;
          currentModel = current;
          renderFeaturePlot(false);
          const plot = host.querySelector('[data-plot]');
          plot.classList.remove('is-updated'); requestAnimationFrame(() => plot.classList.add('is-updated'));
        }
        window.dispatchEvent(new CustomEvent('uw:modeltrained', { detail: current }));
        return current;
      } catch (error) {
        if (renderInterface) { results.innerHTML = `<p class="uw-demo__error">${error.message}</p>`; host.querySelector('[data-plot]').replaceChildren(); }
        return null;
      }
    };

    host.querySelector('[data-train]').addEventListener('click', () => train());
    host.querySelector('[data-plot]').addEventListener('change', (event) => { if (event.target.matches('[data-compare-models]')) renderFeaturePlot(event.target.checked); });
    window.uwRegressionTrainer = { run: (selected) => train(selected, false), get features() { return features; } };
    host.querySelector('input[type="file"]').addEventListener('change', async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      window.dispatchEvent(new CustomEvent('uw:csvconnected', { detail: { text: await file.text(), source: file.name } }));
    });
    window.addEventListener('uw:csvconnected', (event) => {
      try { load(event.detail.text, event.detail.source); }
      catch (error) { status.textContent = error.message; }
    });
    fetch('reference_materials/UW_building_energy.csv')
      .then((response) => { if (!response.ok) throw new Error(); return response.text(); })
      .then((text) => load(text, 'the local reference materials'))
      .catch(() => {
        status.textContent = 'The UW dataset is not included in this deployment. Connect the local CSV to begin; no numerical results are fabricated.';
        fallback.hidden = false;
      });
  };

  const buildRegressionChallenge = () => {
    const host = document.getElementById('regression-final-challenge');
    if (!host) return;
    const extraFeatures = [
      ['Occupants', 'Occupants'], ['Building_Length_m', 'Building length'],
      ['Orientation (degrees north)', 'Orientation'], ['Relative Compactness', 'Relative compactness'],
      ['Tree_Canopy', 'Tree canopy'], ['Land_Surface_Temp', 'Land-surface temperature'],
      ['university', 'University program'], ['parking', 'Parking program']
    ];
    host.innerHTML = `<section class="regression-challenge"><header><span>Try three models</span><h5>Does adding inputs improve unseen-building performance?</h5></header><div class="challenge-grid"><section><strong>Challenge 1</strong><p>Train with Area only.</p><button type="button" data-challenge="one">Run Area model</button><output data-challenge-output="one">Not run yet</output></section><section><strong>Challenge 2</strong><p>Train with Area + Height + Year Built.</p><button type="button" data-challenge="two">Run three-feature model</button><output data-challenge-output="two">Not run yet</output></section><section><strong>Challenge 3</strong><p>Add exactly three more features.</p><div class="challenge-extras">${extraFeatures.map(([value, label]) => `<label><input type="checkbox" value="${value}"> ${label}</label>`).join('')}</div><button type="button" data-challenge="three">Run expanded model</button><output data-challenge-output="three">Not run yet</output></section></div><fieldset class="challenge-reflection" disabled><legend>Reflect after all three models</legend><p>Did adding more features necessarily improve testing performance?</p><div><label><input type="radio" name="improved" value="yes"> Yes</label><label><input type="radio" name="improved" value="no"> No</label></div><button type="button" data-check-answer>Check answer</button><output class="challenge-feedback" data-answer-feedback></output><label for="challenge-why">Why?</label><textarea id="challenge-why" rows="3"></textarea><button type="button" data-example="why" hidden>Compare with example response</button><div class="challenge-example" data-example-output="why" hidden>More predictors can reduce or increase testing error. Extra inputs may add useful information, but they may also add noise, redundancy, or instability. Compare testing—not training—performance.</div><label for="challenge-limit">What can this regression model tell an architect, and what can it not tell us?</label><textarea id="challenge-limit" rows="4"></textarea><button type="button" data-example="limit" hidden>Compare with example response</button><div class="challenge-example" data-example-output="limit" hidden>The model can estimate energy use and reveal fitted associations within this dataset. It cannot establish causation, guarantee performance for other campuses, or replace physical analysis and professional judgment.</div></fieldset></section>`;
    const completed = new Set();
    const challengeResults = new Map();
    const run = (name, selected) => {
      const output = host.querySelector(`[data-challenge-output="${name}"]`);
      if (!window.uwRegressionTrainer) { output.textContent = 'Open Interactive Feature Selection and connect the UW CSV first.'; return; }
      const result = window.uwRegressionTrainer.run(selected);
      if (!result) { output.textContent = 'The dataset is still loading or these inputs cannot be fitted.'; return; }
      output.innerHTML = `<strong>Test RMSE ${Math.round(result.testRmse).toLocaleString()} kWh</strong><span>Test R² ${result.r2.toFixed(3)}</span>`;
      challengeResults.set(name, result);
      completed.add(name);
      if (completed.size === 3) host.querySelector('.challenge-reflection').disabled = false;
    };
    host.addEventListener('click', (event) => {
      const check = event.target.closest('[data-check-answer]');
      if (check) {
        const selected = host.querySelector('input[name="improved"]:checked');
        const feedback = host.querySelector('[data-answer-feedback]');
        if (!selected) { feedback.textContent = 'Choose Yes or No first.'; return; }
        const one = challengeResults.get('one'), two = challengeResults.get('two'), three = challengeResults.get('three');
        const everyAdditionImproved = two.testRmse < one.testRmse && three.testRmse < two.testRmse;
        const answer = everyAdditionImproved ? 'yes' : 'no';
        feedback.textContent = selected.value === answer
          ? `That matches these results. ${everyAdditionImproved ? 'Both additions lowered testing RMSE in these runs, though that does not guarantee more features always help.' : 'At least one added feature set did not lower testing RMSE.'}`
          : `Compare the recorded testing RMSE values again. ${everyAdditionImproved ? 'Both additions lowered testing RMSE in these particular runs.' : 'At least one step added features without lowering testing RMSE.'}`;
        return;
      }
      const example = event.target.closest('[data-example]');
      if (example) { host.querySelector(`[data-example-output="${example.dataset.example}"]`).hidden = false; return; }
      const button = event.target.closest('[data-challenge]'); if (!button) return;
      if (button.dataset.challenge === 'one') run('one', ['Area_m']);
      if (button.dataset.challenge === 'two') run('two', ['Area_m', 'Height', 'Year_Built']);
      if (button.dataset.challenge === 'three') {
        const extra = [...host.querySelectorAll('.challenge-extras input:checked')].map((input) => input.value);
        if (extra.length !== 3) { host.querySelector('[data-challenge-output="three"]').textContent = 'Choose exactly three additional features.'; return; }
        run('three', ['Area_m', 'Height', 'Year_Built', ...extra]);
      }
    });
    host.addEventListener('input', (event) => {
      if (!event.target.matches('textarea')) return;
      const key = event.target.id === 'challenge-why' ? 'why' : 'limit';
      host.querySelector(`[data-example="${key}"]`).hidden = !event.target.value.trim();
    });
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

  buildRegressionStaticVisuals();
  buildConceptRegression();
  buildPythonWorkflow();
  buildUwRegressionDemo();
  buildRegressionChallenge();
  buildCodeLab();
  buildCourseShell();
})();
