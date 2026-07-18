# Monte Carlo notebooks — Stat Exam Pro

Companion notebooks for the four-part **[Monte Carlo simulation guide](https://statexampro.com/lessons/monte-carlo/)** on Stat Exam Pro. The lessons do the explaining; these run the code and produce every figure and number the lessons quote. Read a section on the site, run the matching one here, then change a parameter and watch it move.

Everything uses only `numpy`, `scipy` and `matplotlib` — all preinstalled in Google Colab, so the fastest way in is one click, nothing to set up.

## The two notebooks

### `monte-carlo-entry.ipynb` — the beginner's guide (parts 1–2)

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/StatExamPro/statexampro.com/blob/main/notebooks/monte-carlo-entry.ipynb)

Pairs with:

- **[Part 1 — Monte Carlo from first principles](https://statexampro.com/lessons/monte-carlo/first-principles/)** · sections 2–5: estimating π by throwing darts, the law of large numbers watched live, standard errors and confidence intervals, seeds and the parallel-seed trap.
- **[Part 2 — The recipe, and two real projects](https://statexampro.com/lessons/monte-carlo/recipe-and-projects/)** · sections 6–9: building any distribution from uniforms, a valuation DCF turned into a distribution of value, and statistical power by simulation.

### `monte-carlo-pro.ipynb` — the pro guide (parts 3–4)

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/StatExamPro/statexampro.com/blob/main/notebooks/monte-carlo-pro.ipynb)

Pairs with:

- **[Part 3 — Paths, options and correlated inputs](https://statexampro.com/lessons/monte-carlo/paths-and-options/)** · sections 1–3: geometric Brownian motion, option pricing certified against Black–Scholes, Cholesky and copulas.
- **[Part 4 — Beating the square-root law](https://statexampro.com/lessons/monte-carlo/variance-reduction/)** · sections 4–8: antithetic and control variates, importance sampling, quasi-Monte Carlo (Sobol'), simulation studies, and the bridge to MCMC.

Each notebook ends with a short set of exercises.

## Running them

**In the browser (recommended).** Click an *Open in Colab* badge above. Nothing to install — `numpy`, `scipy` and `matplotlib` are already there. Runtime is about 1–2 minutes for the entry notebook, 2–3 for the pro one.

**Locally.** Download the `.ipynb` and open it in Jupyter:

```
pip install numpy scipy matplotlib
```

(`scipy` ≥ 1.7 is needed for the Sobol' sequences in the pro notebook.)

## Reproducible to the digit

Every random generator is explicitly seeded, so the figures and numbers reproduce run to run — the values the lessons quote are this notebook's own output: the Black–Scholes check lands on 9.1218, the control variate collects its 683× variance reduction, importance sampling its ~68,000×, and so on. Change a seed or an `N` and watch the error bars move; that is the whole point of running them yourself.

## More

- The full course — **[Monte Carlo simulation, a four-part guide](https://statexampro.com/lessons/monte-carlo/)**
- Interactive calculators, worked lessons and cheat sheets for medical biostatistics — **[statexampro.com](https://statexampro.com/)**
- The app — **[Stat Exam Pro on the App Store](https://apps.apple.com/us/app/stat-exam-pro/id6755912771)**
