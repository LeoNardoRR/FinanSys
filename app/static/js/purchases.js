(() => {
  const total = document.getElementById('purchase-total');
  const installments = document.getElementById('purchase-installments');
  const date = document.getElementById('purchase-date');
  const product = document.getElementById('product-name');
  const card = document.getElementById('purchase-card');
  if (!total || !installments || !date || !product || !card) return;

  const money = value => {
    const clean = value.replace(/R\$/gi, '').replace(/\s/g, '');
    const normalized = clean.includes(',') ? clean.replace(/\./g, '').replace(',', '.') : clean;
    return Number(normalized) || 0;
  };
  const brl = value => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  const addMonths = (iso, count) => {
    if (!iso) return null;
    const [year, month, day] = iso.split('-').map(Number);
    const target = new Date(year, month - 1 + count, 1);
    const lastDay = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate();
    target.setDate(Math.min(day, lastDay));
    return target;
  };
  const formatDate = value => value ? value.toLocaleDateString('pt-BR') : '—';

  function updatePreview() {
    const value = money(total.value);
    const count = Math.max(Number(installments.value) || 1, 1);
    const selected = card.options[card.selectedIndex];
    document.getElementById('preview-title').textContent = product.value.trim() || 'Informe produto e valor';
    document.getElementById('preview-installment').textContent = value ? `${count}x de aproximadamente ${brl(value / count)}` : '—';
    document.getElementById('preview-end').textContent = formatDate(addMonths(date.value, count - 1));
    document.getElementById('preview-card').textContent = selected?.value ? selected.textContent.split(' · ')[0] : '—';
  }
  [total, installments, date, product, card].forEach(control => control.addEventListener('input', updatePreview));
  card.addEventListener('change', updatePreview);
  updatePreview();
})();
