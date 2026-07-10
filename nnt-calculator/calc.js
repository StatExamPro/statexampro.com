/* Pure math for the RR / ARR / NNT playground. Own file so the node test
   suite verifies exactly the code the page runs, against Python goldens. */
(function (root) {
  'use strict';
  // cer = control event rate, eer = experimental (treatment) event rate, both in [0,1]
  function metrics(cer, eer) {
    var rr  = cer > 0 ? eer / cer : NaN;
    var arr = cer - eer;                       // >0 benefit, <0 harm
    var rrr = cer > 0 ? arr / cer : NaN;       // relative risk reduction (or increase if <0)
    var nnt = arr !== 0 ? 1 / Math.abs(arr) : Infinity; // NNT (benefit) or NNH (harm)
    var or_ = (cer > 0 && cer < 1 && eer < 1)
      ? (eer / (1 - eer)) / (cer / (1 - cer)) : NaN;
    return { rr: rr, arr: arr, rrr: rrr, nnt: nnt, or: or_, benefit: arr >= 0 };
  }
  // 100-person (or n) counterfactual breakdown, cells always sum to n
  function groups(cer, eer, n) {
    if (cer >= eer) {                          // benefit (or neutral)
      var ev = Math.round(eer * n);            // event despite treatment
      var un = Math.round((1 - cer) * n);      // no event either way
      return { mode: 'benefit', event: ev, helped: n - ev - un, unaffected: un };
    }
    var evH = Math.round(cer * n);             // event either way
    var unH = Math.round((1 - eer) * n);       // no event either way
    return { mode: 'harm', event: evH, harmed: n - evH - unH, unaffected: unH };
  }
  var api = { metrics: metrics, groups: groups };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SXPrr = api;
})(typeof self !== 'undefined' ? self : this);
