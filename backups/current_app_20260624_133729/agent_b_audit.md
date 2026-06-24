# Agent B Audit - Generated Problem Bank

## Coverage
- Topics audited: Monopoly, Price Discrimination, Oligopoly and Strategic Competition, Game Theory, Risk and Insurance, Asymmetric Information, Incentives and Contracts, Mixed Review.
- Rows audited: 400 total, 50 per assigned topic.
- Files read: `data/generated_problems.jsonl`, `problem_bank_tools/curated_bank.py`.
- Direct data edits: none.

## Checks performed
- Rebuilt the 800-row bank with `build_curated_bank(50)` and confirmed every assigned row matches the current generator, excluding only `created_at`.
- Checked all 400 assigned rows for subpart/solution label alignment, empty subparts, repeated setup sentences, and forbidden student-facing terms: template, source, exam, problem set, generated, original.
- Programmatically validated arithmetic/formula outputs for all formula families in the assigned topics, including the Mixed Review rows produced from monopoly, demand shift, cross-price elasticity, marginal cost estimate, and expenditure minimization generators.
- Parsed Game Theory payoff prose and checked dominant-strategy, Nash, backward-induction, coordination, and prisoners-dilemma claims on all 50 Game Theory rows.

## Clean findings
- No subpart/solution label mismatches.
- No empty subparts or solution subparts.
- No repeated setup sentence detected in assigned problem text.
- No student-facing references to templates, sources, exams, problem sets, generated records, or originals.
- No arithmetic errors found in Monopoly, Oligopoly and Strategic Competition, Risk and Insurance, Mixed Review, or non-self-selection Price Discrimination formula rows.

## Proposed fixes

### 1. Game Theory - Prisoners' dilemma payoff contradiction
Reason: In all 10 rows, Clean/Clean net payoff equals Pollute/Pollute, but solution_subparts[c] says Clean/Clean is better. This is not a prisoners' dilemma as written.

Generator patch: in `problem_bank_tools/curated_bank.py`, `game_theory()`, line 596, change `both_pollute = 40 + i` to `both_pollute = 38 + i` or equivalently define `both_pollute = both_clean - clean_cost - 2`. Regenerate the bank. This keeps Pollute dominant and makes Clean/Clean Pareto-superior.

| generated_id | field(s) | old text snippet | replacement text |
|---|---|---|---|
| gen_d841d74c3188fda4 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 43; solution says Pollute/Pollute (43,43) | If both pollute, each gets 41; solution_subparts[a]: Both pollute gives 41 each.; solution_subparts[c]: Both would be better at Clean/Clean (43,43) than Pollute/Pollute (41,41), but individual incentives lead to pollution. |
| gen_95696017f460f997 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 48; solution says Pollute/Pollute (48,48) | If both pollute, each gets 46; solution_subparts[a]: Both pollute gives 46 each.; solution_subparts[c]: Both would be better at Clean/Clean (48,48) than Pollute/Pollute (46,46), but individual incentives lead to pollution. |
| gen_691ea02d9da5f807 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 53; solution says Pollute/Pollute (53,53) | If both pollute, each gets 51; solution_subparts[a]: Both pollute gives 51 each.; solution_subparts[c]: Both would be better at Clean/Clean (53,53) than Pollute/Pollute (51,51), but individual incentives lead to pollution. |
| gen_0bc3552a395ea892 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 58; solution says Pollute/Pollute (58,58) | If both pollute, each gets 56; solution_subparts[a]: Both pollute gives 56 each.; solution_subparts[c]: Both would be better at Clean/Clean (58,58) than Pollute/Pollute (56,56), but individual incentives lead to pollution. |
| gen_d4e0b7c6dac0836c | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 63; solution says Pollute/Pollute (63,63) | If both pollute, each gets 61; solution_subparts[a]: Both pollute gives 61 each.; solution_subparts[c]: Both would be better at Clean/Clean (63,63) than Pollute/Pollute (61,61), but individual incentives lead to pollution. |
| gen_683893e7accf88d0 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 68; solution says Pollute/Pollute (68,68) | If both pollute, each gets 66; solution_subparts[a]: Both pollute gives 66 each.; solution_subparts[c]: Both would be better at Clean/Clean (68,68) than Pollute/Pollute (66,66), but individual incentives lead to pollution. |
| gen_cd8e23f5616a8ff7 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 73; solution says Pollute/Pollute (73,73) | If both pollute, each gets 71; solution_subparts[a]: Both pollute gives 71 each.; solution_subparts[c]: Both would be better at Clean/Clean (73,73) than Pollute/Pollute (71,71), but individual incentives lead to pollution. |
| gen_b3d2231514932024 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 78; solution says Pollute/Pollute (78,78) | If both pollute, each gets 76; solution_subparts[a]: Both pollute gives 76 each.; solution_subparts[c]: Both would be better at Clean/Clean (78,78) than Pollute/Pollute (76,76), but individual incentives lead to pollution. |
| gen_9a7e5e66f128537f | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 83; solution says Pollute/Pollute (83,83) | If both pollute, each gets 81; solution_subparts[a]: Both pollute gives 81 each.; solution_subparts[c]: Both would be better at Clean/Clean (83,83) than Pollute/Pollute (81,81), but individual incentives lead to pollution. |
| gen_96bc80458e417d41 | `problem_text`, `solution_subparts[a]`, `solution_subparts[c]`, `solution` | If both pollute, each gets 88; solution says Pollute/Pollute (88,88) | If both pollute, each gets 86; solution_subparts[a]: Both pollute gives 86 each.; solution_subparts[c]: Both would be better at Clean/Clean (88,88) than Pollute/Pollute (86,86), but individual incentives lead to pollution. |

### 2. Asymmetric Information - adverse-selection participation answer incomplete
Reason: Subpart b asks which sellers participate, but the solution only restates participation inequalities. Some rows have high-quality sellers exiting, so students need the explicit conclusion.

Generator patch: in `asymmetric_information()`, line 543, compute `high_participates = pooled >= good_c` and `low_participates = pooled >= bad_c`, then make solution_subparts[b] state both the inequalities and the conclusion. Regenerate the bank.

| generated_id | field(s) | old text snippet | replacement text |
|---|---|---|---|
| gen_4515c0cd790055d3 | `solution_subparts[b]`, `solution` | High quality participates if $79 >= $81; low quality participates if $79 >= $31. | High quality participates if $79 >= $81, which is false here; low quality participates if $79 >= $31, which is true here. Therefore, only low-quality sellers participate. |
| gen_3b0a20b479530290 | `solution_subparts[b]`, `solution` | High quality participates if $87 >= $82; low quality participates if $87 >= $32. | High quality participates if $87 >= $82, which is true here; low quality participates if $87 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_e80230f2a5663c62 | `solution_subparts[b]`, `solution` | High quality participates if $90 >= $85; low quality participates if $90 >= $30. | High quality participates if $90 >= $85, which is true here; low quality participates if $90 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_bb60a7a52dd74d41 | `solution_subparts[b]`, `solution` | High quality participates if $84 >= $80; low quality participates if $84 >= $31. | High quality participates if $84 >= $80, which is true here; low quality participates if $84 >= $31, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_0bc8d7d2f902ff1a | `solution_subparts[b]`, `solution` | High quality participates if $92 >= $81; low quality participates if $92 >= $32. | High quality participates if $92 >= $81, which is true here; low quality participates if $92 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_1852403ff18d2aa9 | `solution_subparts[b]`, `solution` | High quality participates if $86 >= $84; low quality participates if $86 >= $30. | High quality participates if $86 >= $84, which is true here; low quality participates if $86 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_9f74f612f1420081 | `solution_subparts[b]`, `solution` | High quality participates if $80.20 >= $85; low quality participates if $80.20 >= $31. | High quality participates if $80.20 >= $85, which is false here; low quality participates if $80.20 >= $31, which is true here. Therefore, only low-quality sellers participate. |
| gen_04a19a1920dd16c9 | `solution_subparts[b]`, `solution` | High quality participates if $88 >= $80; low quality participates if $88 >= $32. | High quality participates if $88 >= $80, which is true here; low quality participates if $88 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_179f492ecceb8dd1 | `solution_subparts[b]`, `solution` | High quality participates if $91 >= $83; low quality participates if $91 >= $30. | High quality participates if $91 >= $83, which is true here; low quality participates if $91 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_950339d93ebdef67 | `solution_subparts[b]`, `solution` | High quality participates if $80.40 >= $84; low quality participates if $80.40 >= $31. | High quality participates if $80.40 >= $84, which is false here; low quality participates if $80.40 >= $31, which is true here. Therefore, only low-quality sellers participate. |
| gen_9dac7db91635c023 | `solution_subparts[b]`, `solution` | High quality participates if $89 >= $85; low quality participates if $89 >= $32. | High quality participates if $89 >= $85, which is true here; low quality participates if $89 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_8ea1c893fe4a2ed5 | `solution_subparts[b]`, `solution` | High quality participates if $87 >= $82; low quality participates if $87 >= $30. | High quality participates if $87 >= $82, which is true here; low quality participates if $87 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_b27b514a63e7600c | `solution_subparts[b]`, `solution` | High quality participates if $81.40 >= $83; low quality participates if $81.40 >= $31. | High quality participates if $81.40 >= $83, which is false here; low quality participates if $81.40 >= $31, which is true here. Therefore, only low-quality sellers participate. |
| gen_45f911aeee631cb6 | `solution_subparts[b]`, `solution` | High quality participates if $89 >= $84; low quality participates if $89 >= $32. | High quality participates if $89 >= $84, which is true here; low quality participates if $89 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_80b76b278ddb0e4c | `solution_subparts[b]`, `solution` | High quality participates if $88 >= $81; low quality participates if $88 >= $30. | High quality participates if $88 >= $81, which is true here; low quality participates if $88 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_31bd9d5a154c12ad | `solution_subparts[b]`, `solution` | High quality participates if $81.60 >= $82; low quality participates if $81.60 >= $31. | High quality participates if $81.60 >= $82, which is false here; low quality participates if $81.60 >= $31, which is true here. Therefore, only low-quality sellers participate. |
| gen_8da3cb6efdb04965 | `solution_subparts[b]`, `solution` | High quality participates if $90 >= $83; low quality participates if $90 >= $32. | High quality participates if $90 >= $83, which is true here; low quality participates if $90 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_15494fdd8ca3d502 | `solution_subparts[b]`, `solution` | High quality participates if $88 >= $80; low quality participates if $88 >= $30. | High quality participates if $88 >= $80, which is true here; low quality participates if $88 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_f0e758526cf4167a | `solution_subparts[b]`, `solution` | High quality participates if $82.60 >= $81; low quality participates if $82.60 >= $31. | High quality participates if $82.60 >= $81, which is true here; low quality participates if $82.60 >= $31, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_543845f81a79ce3a | `solution_subparts[b]`, `solution` | High quality participates if $86 >= $82; low quality participates if $86 >= $32. | High quality participates if $86 >= $82, which is true here; low quality participates if $86 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_fe5c0ad0e164c4e5 | `solution_subparts[b]`, `solution` | High quality participates if $89 >= $85; low quality participates if $89 >= $30. | High quality participates if $89 >= $85, which is true here; low quality participates if $89 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_06417fe50f76b657 | `solution_subparts[b]`, `solution` | High quality participates if $82.80 >= $80; low quality participates if $82.80 >= $31. | High quality participates if $82.80 >= $80, which is true here; low quality participates if $82.80 >= $31, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_3a28860c3edf42dc | `solution_subparts[b]`, `solution` | High quality participates if $91 >= $81; low quality participates if $91 >= $32. | High quality participates if $91 >= $81, which is true here; low quality participates if $91 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_70863dc9d526faee | `solution_subparts[b]`, `solution` | High quality participates if $85 >= $84; low quality participates if $85 >= $30. | High quality participates if $85 >= $84, which is true here; low quality participates if $85 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_c74cfe4a0cb7657f | `solution_subparts[b]`, `solution` | High quality participates if $79 >= $85; low quality participates if $79 >= $31. | High quality participates if $79 >= $85, which is false here; low quality participates if $79 >= $31, which is true here. Therefore, only low-quality sellers participate. |
| gen_5174a71f6d3bb6a3 | `solution_subparts[b]`, `solution` | High quality participates if $87 >= $80; low quality participates if $87 >= $32. | High quality participates if $87 >= $80, which is true here; low quality participates if $87 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_2209b07db7f0c3eb | `solution_subparts[b]`, `solution` | High quality participates if $90 >= $83; low quality participates if $90 >= $30. | High quality participates if $90 >= $83, which is true here; low quality participates if $90 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_bdcea75a38c07a53 | `solution_subparts[b]`, `solution` | High quality participates if $84 >= $84; low quality participates if $84 >= $31. | High quality participates if $84 >= $84, which is true here; low quality participates if $84 >= $31, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_f27a5d1e65535d06 | `solution_subparts[b]`, `solution` | High quality participates if $92 >= $85; low quality participates if $92 >= $32. | High quality participates if $92 >= $85, which is true here; low quality participates if $92 >= $32, which is true here. Therefore, both high- and low-quality sellers participate. |
| gen_5895cee708e1b959 | `solution_subparts[b]`, `solution` | High quality participates if $86 >= $82; low quality participates if $86 >= $30. | High quality participates if $86 >= $82, which is true here; low quality participates if $86 >= $30, which is true here. Therefore, both high- and low-quality sellers participate. |

### 3. Price Discrimination - self-selection answer omits two requested values
Reason: Subpart a asks for the maximum price for each plan/type, but the solution gives high-type Premium and low-type Basic/Premium only. It omits high-type Basic and frames low-type pricing ambiguously.

Generator patch: in `price_discrimination()`, line 477, replace solution_subparts[a] with a four-value statement. Also consider adding `cost_base` and `cost_premium` to the row parameters at line 478 for auditability, since the problem text includes those costs.

| generated_id | field(s) | old text snippet | replacement text |
|---|---|---|---|
| gen_da4b3229a4c23e02 | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $93 for Premium and low $48 or $63 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $53, high type Premium $93, low type Basic $48, and low type Premium $63. |
| gen_accca6598464ef0b | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $98 for Premium and low $53 or $68 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $58, high type Premium $98, low type Basic $53, and low type Premium $68. |
| gen_5b69ef5296dd39a0 | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $103 for Premium and low $58 or $73 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $63, high type Premium $103, low type Basic $58, and low type Premium $73. |
| gen_c2c1be356c03697a | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $108 for Premium and low $63 or $78 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $68, high type Premium $108, low type Basic $63, and low type Premium $78. |
| gen_d5e8660b449cb234 | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $113 for Premium and low $68 or $83 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $73, high type Premium $113, low type Basic $68, and low type Premium $83. |
| gen_b7f986f23c089b6a | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $118 for Premium and low $73 or $88 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $78, high type Premium $118, low type Basic $73, and low type Premium $88. |
| gen_b4928c6aeaa71e34 | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $123 for Premium and low $78 or $93 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $83, high type Premium $123, low type Basic $78, and low type Premium $93. |
| gen_727ec50e0710b5e3 | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $128 for Premium and low $83 or $98 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $88, high type Premium $128, low type Basic $83, and low type Premium $98. |
| gen_9966f54bc33188a3 | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $133 for Premium and low $88 or $103 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $93, high type Premium $133, low type Basic $88, and low type Premium $103. |
| gen_a2820696f482f9b2 | `solution_subparts[a]`, `solution` | Observable types can be charged up to their values: high $138 for Premium and low $93 or $108 depending on assigned plan. | Observable types can be charged up to their values for each plan: high type Basic $98, high type Premium $138, low type Basic $93, and low type Premium $108. |

### 4. Incentives and Contracts - negative base wage in moral-hazard contract
Reason: Two rows produce `w = $-1`. A negative base wage is mathematically possible only with no limited-liability constraint, but that assumption is not stated and the `$-1` formatting is awkward for students.

Generator patch: in `incentives_contracts()`, after line 556 set `outside = max(outside, 2 * effort)` before computing `bonus` and `wage`, or choose an outside-option schedule that guarantees `outside >= 2 * effort`. Regenerate the bank. This changes the two affected rows from outside option $19 to $20 and wage $0.

| generated_id | field(s) | old text snippet | replacement text |
|---|---|---|---|
| gen_d3bad3c3ae79b141 | `parameters.outside`, `problem_text`, `solution_subparts[b]`, `solution_subparts[c]`, `solution` | The outside option is $19 and effort costs $10. / PC: w + 0.75b - 10 >= 19. / Minimum bonus is b = $40. Then w = $-1. | parameters.outside: 20; The outside option is $20 and effort costs $10. / PC: w + 0.75b - 10 >= 20. / Minimum bonus is b = $40. Then w = $0. |
| gen_ae4d8874e94d6495 | `parameters.outside`, `problem_text`, `solution_subparts[b]`, `solution_subparts[c]`, `solution` | The outside option is $19 and effort costs $10. / PC: w + 0.75b - 10 >= 19. / Minimum bonus is b = $40. Then w = $-1. | parameters.outside: 20; The outside option is $20 and effort costs $10. / PC: w + 0.75b - 10 >= 20. / Minimum bonus is b = $40. Then w = $0. |

### 5. Risk and Insurance - expected-value cost wording ambiguous
Reason: Subpart b says "If cost is lower by $100" without specifying lower than what. The solution assumes cost is $100 below the risk-neutral WTP from part a.

Generator patch: in `risk_insurance()`, line 493, change subpart b wording to `If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus.` Regenerate the bank. No numeric solution changes are needed.

| generated_id | field(s) | old text snippet | replacement text |
|---|---|---|---|
| gen_ccae2113611f0220 | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_0264a504bc84843a | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_e3723096392a0f42 | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_d538cee8506fe1ba | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_ab023f74ad655d4a | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_5ab37416123c6586 | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_4e5dd5b868d1e3eb | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_f27c171be12407cd | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_839b6ef6170985d7 | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |
| gen_8d113d0eb2462ac4 | `subparts[b]` | If cost is lower by $100, find producer surplus. | If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus. |

## Verification summary
- Assigned rows checked: 400/400.
- Proposed-fix rows: 62 row-level recommendations across 5 systematic generator fixes.
- Highest-priority fixes before publishing: Game Theory prisoners' dilemma contradiction and Incentives negative wage rows.
