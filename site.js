/* Stat Exam Pro - shared chrome script (single source): theme toggle, number
   formatting and the KaTeX hook. Pages with live JS charts may set
   window.sxpOnTheme to redraw after a switch.
   The saved theme is applied by a boot snippet in each page's <head>, before
   first paint; this file owns the button and everything after that. */
function currentTheme() {
  var t = document.documentElement.getAttribute('data-theme');
  if (t) return t;
  return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
}
function themeIcon(th) {
  var b = document.getElementById('themeBtn');
  if (b) b.innerHTML = (th === 'dark') ? '☼' : '☽';
}
function setTheme(th) {
  document.documentElement.setAttribute('data-theme', th);
  themeIcon(th);
  try { localStorage.setItem('sxp-theme', th); } catch(e) {}
  if (window.sxpOnTheme) window.sxpOnTheme();
}
function toggleTheme() { setTheme(currentTheme() === 'dark' ? 'light' : 'dark'); }
/* goatcounter event helper (every App Store CTA calls this) */
function sxpGo(path, title) { if (window.goatcounter) goatcounter.count({ path: path, title: title, event: true }); }
/* Number formatting. Each interactive page sets `var LANG`; the French build flips it to 'fr'. */
function sxpFmtPct(x, digits) {
  var s = (100 * x).toFixed(digits);
  return (window.LANG === 'fr') ? s.replace('.', ',') + ' %' : s + '%';
}
function sxpNum(x) {
  var s = String(x);
  return (window.LANG === 'fr') ? s.replace('.', ',') : s;
}
/* thousands separator: 10,000 in English, 10 000 (narrow no-break space) in French */
function sxpInt(n) {
  var s = String(Math.round(n));
  return s.replace(/\B(?=(\d{3})+(?!\d))/g, (window.LANG === 'fr') ? ' ' : ',');
}
/* n identical spans - the dot and person fields of the playgrounds */
function sxpRepeat(cls, n) {
  var s = '';
  for (var i = 0; i < n; i++) { s += '<span class="' + cls + '"></span>'; }
  return s;
}
/* KaTeX auto-render, registered here so KaTeX pages carry no boilerplate. */
function sxpRenderMath() {
  if (!window.renderMathInElement) return;
  renderMathInElement(document.body, {
    delimiters: [{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],
    throwOnError: false
  });
}
window.addEventListener('load', sxpRenderMath);
/* The head snippet already set data-theme; just sync the button icon to it. */
themeIcon(currentTheme());
