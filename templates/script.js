const items = __ITEMS_JSON__;
const isMobile = window.innerWidth <= 1100;
let expandedId = null;
let isEnlarged = false;

function getIdx() {
  return items.findIndex(i => i.id === expandedId);
}

function closeExpanded() {
  expandedId = null;
  isEnlarged = false;
  history.replaceState(null, '', window.location.pathname);
  render();
  // scroll back to the item in grid
  requestAnimationFrame(() => {
    const hash = expandedId;
    // find closest grid item
  });
}

function navigateArrow(newId) {
  const stage = document.getElementById('img-stage');
  if (!stage) { expandedId = newId; history.replaceState(null, '', '#' + newId); render(); return; }

  const item = items.find(i => i.id === newId);
  if (!item || item.type !== 'image') { expandedId = newId; history.replaceState(null, '', '#' + newId); render(); return; }

  const front = document.getElementById('img-front');
  const back = document.getElementById('img-back');

  back.src = item.full;
  back.onload = () => {
    back.classList.add('visible');
    setTimeout(() => {
      expandedId = newId;
      isEnlarged = false;
      history.replaceState(null, '', '#' + newId);
      render();
    }, 300);
  };
}

function preloadNeighbors(idx) {
  [-1, 1].forEach(d => {
    const n = items[idx + d];
    if (n && n.type === 'image') { const img = new Image(); img.src = n.full; }
  });
}

function rebindArrows(idx) {
  document.querySelectorAll('.nav-arrow').forEach(btn => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const dir = btn.dataset.dir;
      const next = dir === 'prev' ? idx - 1 : idx + 1;
      if (next >= 0 && next < items.length) navigateArrow(items[next].id);
    };
  });
}

function render() {
  const flow = document.getElementById('flow');
  flow.innerHTML = '';

  if (expandedId && !isMobile) {
    const idx = getIdx();
    const item = items[idx];
    const hasPrev = idx > 0;
    const hasNext = idx < items.length - 1;

    // Grid before
    const gridBefore = document.createElement('div');
    gridBefore.className = 'grid';
    items.slice(0, idx).forEach(i => gridBefore.appendChild(makeGridItem(i)));
    flow.appendChild(gridBefore);

    // Expanded section
    const el = document.createElement('div');
    el.className = 'expanded-section' + (item.type === 'text' ? ' text-expanded' : '');
    el.id = item.id;

    if (item.type === 'image') {
      el.innerHTML = `
        <button class="close-btn">&times;</button>
        <button class="nav-arrow" ${!hasPrev ? 'disabled' : ''} data-dir="prev">&#8592;</button>
        <div class="img-stage" id="img-stage">
          <img id="img-front" src="${item.full}" alt="${item.id}">
          <img id="img-back" class="img-back" src="" alt="">
        </div>
        <button class="nav-arrow" ${!hasNext ? 'disabled' : ''} data-dir="next">&#8594;</button>
      `;
    } else {
      el.innerHTML = `
        <button class="close-btn">&times;</button>
        <button class="nav-arrow" ${!hasPrev ? 'disabled' : ''} data-dir="prev">&#8592;</button>
        <div class="text-content-expanded">${item.text}</div>
        <button class="nav-arrow" ${!hasNext ? 'disabled' : ''} data-dir="next">&#8594;</button>
      `;
    }

    flow.appendChild(el);
    el.querySelector('.close-btn').addEventListener('click', (e) => { e.stopPropagation(); closeExpanded(); });
    rebindArrows(idx);

    if (item.type === 'image') {
      const stage = el.querySelector('#img-stage');
      stage.addEventListener('click', (e) => {
        e.stopPropagation();
        isEnlarged = !isEnlarged;
        stage.classList.toggle('enlarged', isEnlarged);
      });
      preloadNeighbors(idx);
    }

    // Grid after
    const gridAfter = document.createElement('div');
    gridAfter.className = 'grid';
    items.slice(idx + 1).forEach(i => gridAfter.appendChild(makeGridItem(i)));
    flow.appendChild(gridAfter);

  } else {
    // Simple grid (mobile or no expanded)
    const grid = document.createElement('div');
    grid.className = 'grid';
    items.forEach(i => grid.appendChild(makeGridItem(i)));
    flow.appendChild(grid);
  }
}

function makeGridItem(item) {
  const div = document.createElement('div');
  div.className = 'grid-item' + (item.type === 'text' ? ' text-block' : '');
  div.id = 'grid-' + item.id;

  if (item.type === 'image') {
    const src = isMobile ? item.full : item.thumb;
    div.innerHTML = `<img src="${src}" alt="${item.id}" loading="lazy">`;
    if (!isMobile) {
      div.addEventListener('click', () => {
        expandedId = item.id;
        history.replaceState(null, '', '#' + item.id);
        render();
        requestAnimationFrame(() => {
          const el = document.getElementById(item.id);
          if (el) el.scrollIntoView({ block: 'center', behavior: 'smooth' });
        });
      });
    }
  } else {
    div.innerHTML = `<div class="text-content">${item.text}</div>`;
    if (!isMobile) {
      div.addEventListener('click', () => {
        expandedId = item.id;
        history.replaceState(null, '', '#' + item.id);
        render();
        requestAnimationFrame(() => {
          const el = document.getElementById(item.id);
          if (el) el.scrollIntoView({ block: 'center', behavior: 'smooth' });
        });
      });
    }
  }

  return div;
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (!expandedId) return;
  const idx = getIdx();
  if (e.key === 'Escape') {
    if (isEnlarged) {
      isEnlarged = false;
      const s = document.getElementById('img-stage');
      if (s) s.classList.remove('enlarged');
    } else {
      closeExpanded();
    }
  } else if (e.key === 'ArrowLeft' && idx > 0) {
    navigateArrow(items[idx - 1].id);
  } else if (e.key === 'ArrowRight' && idx < items.length - 1) {
    navigateArrow(items[idx + 1].id);
  }
});

// Copy protection
document.addEventListener('contextmenu', (e) => {
  if (e.target.tagName === 'IMG') e.preventDefault();
});
document.addEventListener('dragstart', (e) => {
  if (e.target.tagName === 'IMG') e.preventDefault();
});

// Hash navigation on load
const hash = window.location.hash.slice(1);
if (hash) {
  const item = items.find(i => i.id === hash);
  if (item) expandedId = item.id;
}

render();

if (expandedId) {
  requestAnimationFrame(() => {
    const el = document.getElementById(expandedId);
    if (el) el.scrollIntoView({ block: 'start' });
  });
}
