(() => {
  const root = document.documentElement;
  const saved = localStorage.getItem('finansys-theme');
  const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  root.dataset.theme = saved || preferred;
  const button = document.getElementById('theme-toggle');
  button?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('finansys-theme', root.dataset.theme);
  });
})();
