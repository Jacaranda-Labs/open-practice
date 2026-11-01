// Earn by Doing: search and filter the 40-method directory. Cards are server-rendered; this only shows and hides them.
const list = document.getElementById('method-list');
const search = document.getElementById('method-search');
const filters = document.getElementById('method-filters');
const count = document.getElementById('method-count');
const empty = document.getElementById('no-results');
if (list && search && filters && count) {
  const cards = [...list.querySelectorAll('.method-card')];
  let cat = 'all', only = null, label = '';
  const render = () => {
    const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const card of cards) {
      const ok = (cat === 'all' || card.dataset.cat === cat) && (!only || only.has(card.dataset.n)) && words.every(w => card.dataset.text.includes(w));
      card.hidden = !ok;
      if (ok) shown++;
    }
    count.textContent = '';
    if (only) {
      count.append(`Showing ${shown} method${shown === 1 ? '' : 's'} related to “${label}”. `);
      const all = document.createElement('button');
      all.type = 'button'; all.className = 'text-link'; all.textContent = 'Show all 40';
      all.addEventListener('click', () => { only = null; render(); });
      count.append(all);
    } else {
      count.textContent = shown === cards.length ? `Showing all ${cards.length} methods.` : `Showing ${shown} of ${cards.length} methods.`;
    }
    if (empty) empty.hidden = shown > 0;
  };
  filters.addEventListener('click', ev => {
    const b = ev.target.closest('button[data-filter]');
    if (!b) return;
    cat = b.dataset.filter; only = null;
    for (const x of filters.querySelectorAll('button')) { const on = x === b; x.classList.toggle('active', on); x.setAttribute('aria-pressed', String(on)); }
    render();
  });
  search.addEventListener('input', () => { only = null; render(); });
  for (const a of document.querySelectorAll('a[data-methods]')) {
    a.addEventListener('click', () => {
      only = new Set(a.dataset.methods.split(','));
      label = a.closest('.card')?.querySelector('h3')?.textContent || 'this build';
      search.value = ''; cat = 'all';
      for (const x of filters.querySelectorAll('button')) { const on = x.dataset.filter === 'all'; x.classList.toggle('active', on); x.setAttribute('aria-pressed', String(on)); }
      render();
    });
  }
  render();
}
