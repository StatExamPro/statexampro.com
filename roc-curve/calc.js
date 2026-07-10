/* Pure math for the ROC / threshold playground. Own file so the node test
   suite verifies exactly the code the page runs, against scipy goldens.
   Model: healthy ~ N(-d/2, 1), diseased ~ N(+d/2, 1); test positive if
   the measured value exceeds threshold t. d is the separation (d-prime). */
(function (root) {
  'use strict';

  // erf via Abramowitz & Stegun 7.1.26 (max abs error ~1.5e-7)
  function erf(x) {
    var s = x < 0 ? -1 : 1; x = Math.abs(x);
    var t = 1 / (1 + 0.3275911 * x);
    var y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
      - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return s * y;
  }
  function normCdf(x) { return 0.5 * (1 + erf(x / Math.SQRT2)); }
  function normPdf(x) { return Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI); }

  function metrics(d, t) {
    var se = normCdf(d / 2 - t);        // P(diseased > t)  = TPR
    var sp = normCdf(t + d / 2);        // P(healthy  < t)  = TNR
    return { se: se, sp: sp, fpr: 1 - sp, auc: normCdf(d / Math.SQRT2) };
  }

  // ROC as an array of [fpr, tpr] points, threshold swept high->low
  function roc(d, n) {
    var pts = [], i, t;
    for (i = 0; i <= n; i++) {
      t = 4.5 - (9 * i / n);            // +4.5 .. -4.5
      pts.push([1 - normCdf(t + d / 2), normCdf(d / 2 - t)]);
    }
    return pts;
  }

  var api = { erf: erf, normCdf: normCdf, normPdf: normPdf, metrics: metrics, roc: roc };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
  else { root.SXProc = api; }
})(typeof self !== 'undefined' ? self : this);
