(() => {
  const input = document.getElementById('help-search');
  const sections = [...document.querySelectorAll('.help-section')];
  const empty = document.getElementById('help-empty');
  const links = [...document.querySelectorAll('.help-toc a')];
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

  input?.addEventListener('input', () => {
    const query = normalize(input.value);
    let visible = 0;
    sections.forEach(section => {
      const haystack = normalize(`${section.dataset.help || ''} ${section.textContent}`);
      const match = !query || haystack.includes(query);
      section.hidden = !match;
      if (match) visible += 1;
    });
    empty?.classList.toggle('visible', visible === 0);
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const current = entries.find(entry => entry.isIntersecting);
      if (!current) return;
      links.forEach(link => link.classList.toggle('active', link.hash === `#${current.target.id}`));
    }, { rootMargin: '-15% 0px -70% 0px' });
    sections.forEach(section => observer.observe(section));
  }
})();
