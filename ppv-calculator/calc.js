/* Pure math for the PPV/NPV playground. Kept in its own file so the
   node test suite (ppv-tests/) can require() exactly the code the
   page runs - one implementation, verified against Python goldens. */
(function (root) {
  'use strict';

  function ppv(se, sp, p) {
    return (se * p) / (se * p + (1 - sp) * (1 - p));
  }

  function npv(se, sp, p) {
    return (sp * (1 - p)) / (sp * (1 - p) + (1 - se) * p);
  }

  /* Integer 2x2 counts for a population of n, for the dot field and
     the table. Rounding is done so the four cells always sum to n. */
  function counts(se, sp, p, n) {
    var sick = Math.round(n * p);
    var tp = Math.round(sick * se);
    var fn = sick - tp;
    var healthy = n - sick;
    var tn = Math.round(healthy * sp);
    var fp = healthy - tn;
    return { sick: sick, healthy: healthy, tp: tp, fn: fn, tn: tn, fp: fp };
  }

  var api = { ppv: ppv, npv: npv, counts: counts };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
  else { root.SXPCalc = api; }
})(typeof self !== 'undefined' ? self : this);
