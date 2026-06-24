# Agent A Audit: Generated Problem Bank

Assigned topics audited:

- Supply and Demand
- Elasticity
- Taxes and Government Intervention
- Externalities and Public Goods
- Consumer Choice
- Production and Costs
- Trade and Welfare
- Perfect Competition

## Coverage and Checks

- Audited 400 generated rows from `data/generated_problems.jsonl`: 50 rows for each of the 8 assigned topics.
- Verified 400 unique `generated_id` values and 400 unique `problem_text` values.
- Verified every assigned row has nonempty `problem_text`, `subparts`, and `solution_subparts`.
- Verified every assigned row has aligned subpart labels: `["a", "b", "c"]` in both `subparts` and `solution_subparts`.
- Checked student-facing prompt/subpart text for forbidden/internal terms: `template`, `source`, `exam`, `problem set`, `generated vs original`, `Gemini`, and `model`. No assigned prompt/subpart text contained these terms.
- Checked repeated setup sentences in `problem_text`. No exact repeated sentences were found.
- Checked all assigned rows for `disabled`; all assigned rows are enabled.
- Programmatically recomputed formula outputs from row `parameters` for all assigned formula families:
  - Supply and Demand: tax incidence, demand shift, price ceiling, subsidy wedge, supply shock.
  - Elasticity: price elasticity, point elasticity, cross-price elasticity, income elasticity, markup rule.
  - Taxes and Government Intervention: tax DWL, price floor, price ceiling, subsidy incidence, import quota.
  - Externalities and Public Goods: Pigouvian tax, public goods, positive externality, free riding.
  - Consumer Choice: Cobb-Douglas demand, perfect complements, perfect substitutes, price change, expenditure minimization.
  - Production and Costs: short-run cost, cost minimization, minimum efficient scale, marginal cost estimate, returns to scale.
  - Trade and Welfare: tariff, quota, exports, tariff quantity effects, tariff welfare.
  - Perfect Competition: industry supply, long-run entry, shutdown decision, marginal output rule, profit and entry.

## Summary

I found 2 substantive solution-text errors. Both are Supply and Demand price-ceiling rows where the ceiling equals the unregulated equilibrium price, but solution part (b) says the ceiling is below equilibrium and binding.

I also found 43 wording-polish issues where firm names ending in `s` are rendered with awkward possessives such as `LoomLabs's`. These are not math errors, but they are student-facing wording issues and should be fixed systematically in the generator.

## Proposed Fixes: Substantive Errors

### 1. `gen_c78b9ac9f22537e1`

- Topic: Supply and Demand
- Subtopic: Price ceiling
- Fields: `solution_subparts` labels `b` and `c`
- Reason: The unregulated equilibrium price is `$22` and the ceiling is also `$22`. A ceiling equal to equilibrium is not binding.

Current label `b` text:

```text
The ceiling is binding if it is below $22. Here $22 is below the equilibrium price, so it binds.
```

Replacement label `b` text:

```text
The ceiling is binding only if it is below $22. Here the ceiling equals the equilibrium price, so it is not binding.
```

Current label `c` text:

```text
At $22, Qd = 54 and Qs = 54, so the shortage is 0.
```

Replacement label `c` text:

```text
Because the ceiling is not binding, there is no shortage. At $22, Qd = 54 and Qs = 54.
```

### 2. `gen_67476ef9b5bb2e63`

- Topic: Supply and Demand
- Subtopic: Price ceiling
- Fields: `solution_subparts` labels `b` and `c`
- Reason: The unregulated equilibrium price is `$22` and the ceiling is also `$22`. A ceiling equal to equilibrium is not binding.

Current label `b` text:

```text
The ceiling is binding if it is below $22. Here $22 is below the equilibrium price, so it binds.
```

Replacement label `b` text:

```text
The ceiling is binding only if it is below $22. Here the ceiling equals the equilibrium price, so it is not binding.
```

Current label `c` text:

```text
At $22, Qd = 59 and Qs = 59, so the shortage is 0.
```

Replacement label `c` text:

```text
Because the ceiling is not binding, there is no shortage. At $22, Qd = 59 and Qs = 59.
```

## Proposed Generator Fix: Price Ceiling Binding Logic

- File/section: `problem_bank_tools/curated_bank.py`, `supply_and_demand(i)`, price-ceiling branch around lines 128-137.
- Reason: The branch always writes that the ceiling binds, even when `ceiling >= p0`.
- Recommended patch: compute binding dynamically and render solution text accordingly.

Suggested logic:

```python
binding = ceiling < p0
if binding:
    b_text = f"The ceiling is binding because {money(ceiling)} is below the equilibrium price of {money(p0)}."
    c_text = f"At {money(ceiling)}, Qd = {num(qd)} and Qs = {num(qsupply)}, so the shortage is {num(shortage)}."
else:
    relation = "equal to" if math.isclose(ceiling, p0) else "above"
    b_text = f"The ceiling is not binding because {money(ceiling)} is {relation} the equilibrium price of {money(p0)}."
    c_text = f"Because the ceiling is not binding, there is no shortage. At {money(ceiling)}, Qd = {num(qd)} and Qs = {num(qsupply)}."
```

Then use `b_text` and `c_text` in the label `b` and `c` solution parts.

## Proposed Fixes: Wording Polish

The following assigned rows contain possessive firm names ending in `s` rendered as `s's`. Replace only the listed snippet in `problem_text`.

| generated_id | topic | subtopic | old snippet | replacement |
|---|---|---|---|---|
| `gen_67476ef9b5bb2e63` | Supply and Demand | Price ceiling | `LoomLabs's` | `LoomLabs'` |
| `gen_cd600e623423404d` | Supply and Demand | Supply shock | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_64cc083e1245cecb` | Supply and Demand | Supply shock | `Atlas Droneworks's` | `Atlas Droneworks'` |
| `gen_b85e810aea2d970e` | Supply and Demand | Price ceiling | `LoomLabs's` | `LoomLabs'` |
| `gen_40da067738eb513a` | Supply and Demand | Supply shock | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_f8a84c7aa1f90e47` | Supply and Demand | Supply shock | `Atlas Droneworks's` | `Atlas Droneworks'` |
| `gen_edc2d4a1500cb1db` | Supply and Demand | Price ceiling | `LoomLabs's` | `LoomLabs'` |
| `gen_82829524a0bed587` | Supply and Demand | Supply shock | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_62f9b6786caf8b14` | Elasticity | Income elasticity | `Flux Fitness's` | `Flux Fitness'` |
| `gen_07b64d165042ca00` | Elasticity | Cross-price elasticity | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_f412de3b87d4866a` | Elasticity | Cross-price elasticity | `Atlas Droneworks's` | `Atlas Droneworks'` |
| `gen_82554b0b89b57fd3` | Elasticity | Income elasticity | `Aurora Scooters's` | `Aurora Scooters'` |
| `gen_3787b07b8b008b08` | Elasticity | Income elasticity | `Flux Fitness's` | `Flux Fitness'` |
| `gen_591de72fbdc136c2` | Elasticity | Cross-price elasticity | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_725a8af307377e73` | Elasticity | Cross-price elasticity | `Atlas Droneworks's` | `Atlas Droneworks'` |
| `gen_38bcf3eb1ad233a7` | Elasticity | Income elasticity | `Aurora Scooters's` | `Aurora Scooters'` |
| `gen_b86f2dae46c8ec67` | Elasticity | Income elasticity | `Flux Fitness's` | `Flux Fitness'` |
| `gen_03c96ec3db98ce93` | Elasticity | Cross-price elasticity | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_6e3f91706e451cea` | Taxes and Government Intervention | Subsidy incidence | `LoomLabs's` | `LoomLabs'` |
| `gen_2ffbf6317616caea` | Taxes and Government Intervention | Price ceiling | `Polaris Bikes's` | `Polaris Bikes'` |
| `gen_cccd4804d84b6bd2` | Taxes and Government Intervention | Price ceiling | `BluePeak Batteries's` | `BluePeak Batteries'` |
| `gen_82ef75ac0129f69c` | Taxes and Government Intervention | Subsidy incidence | `LoomLabs's` | `LoomLabs'` |
| `gen_5edd679e4d0f1be1` | Taxes and Government Intervention | Price ceiling | `Polaris Bikes's` | `Polaris Bikes'` |
| `gen_0b3c88e716dd6d7e` | Taxes and Government Intervention | Price ceiling | `BluePeak Batteries's` | `BluePeak Batteries'` |
| `gen_1260a50a5593f540` | Taxes and Government Intervention | Subsidy incidence | `LoomLabs's` | `LoomLabs'` |
| `gen_bd29b4b55710bb83` | Taxes and Government Intervention | Price ceiling | `Polaris Bikes's` | `Polaris Bikes'` |
| `gen_3dd16da1193b3eb0` | Trade and Welfare | Exports | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_9185a964d6362d3d` | Trade and Welfare | Exports | `Atlas Droneworks's` | `Atlas Droneworks'` |
| `gen_0a506d4b3b912969` | Trade and Welfare | Tariff quantity effects | `Aurora Scooters's` | `Aurora Scooters'` |
| `gen_5dedabd119e49074` | Trade and Welfare | Tariff quantity effects | `Flux Fitness's` | `Flux Fitness'` |
| `gen_c33987070d344407` | Trade and Welfare | Exports | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_8edeed4d3646ccee` | Trade and Welfare | Exports | `Atlas Droneworks's` | `Atlas Droneworks'` |
| `gen_f794d3adc4d234ef` | Trade and Welfare | Tariff quantity effects | `Aurora Scooters's` | `Aurora Scooters'` |
| `gen_a9f2078a829fad82` | Trade and Welfare | Tariff quantity effects | `Flux Fitness's` | `Flux Fitness'` |
| `gen_6774c83df31f05dd` | Trade and Welfare | Exports | `Nebula Noodles's` | `Nebula Noodles'` |
| `gen_ddd40dfa901f2580` | Production and Costs | Minimum efficient scale | `Polaris Bikes's` | `Polaris Bikes'` |
| `gen_8963c04e50e0348d` | Production and Costs | Minimum efficient scale | `BluePeak Batteries's` | `BluePeak Batteries'` |
| `gen_eae1f01498e3e9f8` | Production and Costs | Minimum efficient scale | `Polaris Bikes's` | `Polaris Bikes'` |
| `gen_5c9e25c2ff6cdb2f` | Production and Costs | Minimum efficient scale | `BluePeak Batteries's` | `BluePeak Batteries'` |
| `gen_5113ad2e16909767` | Production and Costs | Minimum efficient scale | `Polaris Bikes's` | `Polaris Bikes'` |
| `gen_a803ca2b02795a00` | Externalities and Public Goods | Positive externality | `Zenith Zips's` | `Zenith Zips'` |
| `gen_67bfc7c95021498e` | Externalities and Public Goods | Positive externality | `Zenith Zips's` | `Zenith Zips'` |
| `gen_22e0b4aa20df0b91` | Externalities and Public Goods | Positive externality | `Zenith Zips's` | `Zenith Zips'` |

## Proposed Generator Fix: Possessive Firm Names

- File/section: `problem_bank_tools/curated_bank.py`, shared helpers near `firm(i)`, and all text f-strings using `{f}'s`, `{f1}'s`, or `{f2}'s`.
- Reason: Several generated firm names end in `s`, producing awkward student-facing text such as `Nebula Noodles's`.
- Recommended patch: add a small helper and use it in possessive contexts.

Suggested helper:

```python
def possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"
```

Then replace strings such as:

```python
f"{f}'s service"
```

with:

```python
f"{possessive(f)} service"
```

This should be applied at least to `curated_bank.py` lines 134, 153, 182, 189, 229, 239, 278, 288, 327, and 655 for Agent A's assigned topics, and preferably to the analogous unassigned-topic occurrences too.

## No Fix Needed

No additional math errors, label-alignment errors, empty-field issues, duplicate problem texts, repeated setup sentences, disabled assigned rows, forbidden student-facing source references, or answer-leakage flags were found in the assigned topics.
