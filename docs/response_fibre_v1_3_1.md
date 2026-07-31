# Scientific status of the v1.3.1 response-fibre audit

## Certified objects

Let \(R\) denote the eight-real-dimensional response map formed from the real
and imaginary parts of the projective coefficients \(a_0,\ldots,a_3\).
The audit uses one frozen eight-dimensional transverse gauge in a
14-dimensional phase-control space.

Parameter-dependent, outward-rounded Arb Krawczyk operators certify a unique
transverse correction over each of 640 parameter boxes. Nine shared-endpoint
inclusions prove that the ten local parameterized segments form one connected
local curve of exact solutions to

\[
R(\theta)=R(\theta_{\mathrm{ref}}).
\]

Eleven endpoint root boxes are independently certified. For all ten
consecutive endpoint pairs, outward-rounded Cauchy coefficient enclosures of
the analytic symmetric-loss difference give a strictly negative sixth-order
coefficient difference.

## Theorem-ready statement

> **Certified local response-fibre curve and discrete sixth-order descent.**
> In the declared 14-segment driven-qubit model, there exists a connected
> local curve covered by 640 validated parameter boxes on which the
> projective coefficients \(a_0,\ldots,a_3\) equal their declared reference
> values. For the eleven certified endpoint roots \(x_0,\ldots,x_{10}\), all
> ten consecutive sixth-order symmetric-loss coefficient differences satisfy
> \(L_6(x_{j+1})-L_6(x_j)<0\). The largest certified upper bound among these
> differences is \(-0.014024530042661354\).

This is a discrete endpoint-descent theorem on a validated local curve. It is
not a theorem of pointwise monotonicity in the curve parameter.

## Finite-error statement

For the common error window \([0.035,0.13]\), strict symmetric-loss descent is
certified for the first two endpoint steps. The remaining eight steps are
interval-inconclusive because their certified upper enclosures cross zero.
Positive enclosure endpoints are not evidence of an actual reversal.

The finite-error result should therefore be reported separately:

> Uniform finite-error descent over the common window \([0.035,0.13]\) is
> certified for two of ten endpoint steps and remains interval-inconclusive
> for the other eight.

## Method wording

The proof description should say:

> The endpoint root boxes are propagated through outward-rounded Cauchy
> enclosures of the analytic symmetric-loss difference. Exact equality of
> the projective response coefficients \(a_0,\ldots,a_3\) fixes the
> symmetric-loss difference through degree five; the sixth coefficient is
> then enclosed strictly below zero for every consecutive endpoint pair.

Avoid describing this calculation as a direct substitution into a
floating-point formula for \(L_6\).

## Non-claims

Do not promote the result to a global fibre or geometric-flow theorem. The
audit does not establish:

- a complete six-dimensional global response fibre;
- a canonical metric;
- pointwise descent along the complete parameter continuum;
- holonomy or geometric memory;
- many-body or cross-platform universality;
- hardware performance.
