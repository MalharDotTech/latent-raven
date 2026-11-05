document.addEventListener('alpine:init', () => {
  Alpine.data('readingLines', () => ({
    index: 0, timer: null,
    lines: ['Sharpening beaks. Checking receipts.', 'Raven 1 has highlighted everything. Again.', 'Raven 2 is asking for a second source.', 'Raven 3 is quietly checking the footnotes.', 'Separating “familiar with” from “fixed at 2 a.m.”', 'Your evidence is getting the full panel treatment.'],
    init() { this.timer = setInterval(() => { this.index = (this.index + 1) % this.lines.length; }, 4200); },
    destroy() { clearInterval(this.timer); }
  }));
  Alpine.data('panelReveal', outcome => ({
    shown: 0, timers: [],
    init() {
      for (let n = 1; n <= 4; n++) this.timers.push(setTimeout(() => {
        this.shown = n;
        if (n === 4 && outcome === 'latent_winner') this.$nextTick(() => goldBurst(this.$el));
      }, n * 700));
    },
    destroy() { this.timers.forEach(clearTimeout); }
  }));
});
function goldBurst(element) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const box = element.getBoundingClientRect();
  if (box.bottom < 0 || box.top > innerHeight) return;
  for (let i = 0; i < 38; i++) {
    const p = document.createElement('i'); p.className = 'confetti';
    p.style.left = Math.min(innerWidth - 20, Math.max(20, box.left + box.width / 2)) + 'px';
    p.style.top = Math.min(innerHeight * .65, Math.max(100, box.top + box.height * .6)) + 'px';
    p.style.setProperty('--dx', (Math.random() - .5) * 560 + 'px');
    p.style.setProperty('--dy', 100 + Math.random() * 330 + 'px');
    p.style.setProperty('--spin', Math.random() * 720 + 'deg');
    p.style.background = ['#dfba67', '#f7e0a5', '#a5823e'][i % 3];
    p.style.animationDelay = Math.random() * .12 + 's';
    document.body.appendChild(p); setTimeout(() => p.remove(), 2000);
  }
}
document.addEventListener('htmx:responseError', event => {
  const node = document.getElementById('network-message');
  node.textContent = event.detail.xhr.status === 403 ? 'This action is locked. Refresh the page to check your round.' : 'That didn’t save. Please try again, or refresh to check your round.';
  node.hidden = false; setTimeout(() => { node.hidden = true; }, 6500);
});
document.addEventListener('htmx:sendError', () => {
  const node = document.getElementById('network-message');
  node.textContent = 'Connection interrupted. Keep this page open; try again when Raven reconnects.';
  node.hidden = false;
});
