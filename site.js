/* Stat Exam Pro - shared chrome script (single source): theme toggle.
   Pages with live JS charts may set window.sxpOnTheme to redraw after a switch. */
function currentTheme() {
  var t = document.documentElement.getAttribute('data-theme');
  if (t) return t;
  return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
}
function setTheme(th) {
  document.documentElement.setAttribute('data-theme', th);
  document.getElementById('themeBtn').innerHTML = (th === 'dark') ? '\u263C' : '\u263D';
  try { localStorage.setItem('sxp-theme', th); } catch(e) {}
  if (window.sxpOnTheme) window.sxpOnTheme();
}
function toggleTheme() { setTheme(currentTheme() === 'dark' ? 'light' : 'dark'); }
(function() {
  var theme = null;
  try { theme = localStorage.getItem('sxp-theme'); } catch(e) {}
  if (theme) setTheme(theme);
  else document.getElementById('themeBtn').innerHTML = (currentTheme() === 'dark') ? '\u263C' : '\u263D';
})();
