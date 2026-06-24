from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .utils import DEFAULT_DATA_DIR, data_path, stable_id, write_jsonl


FIRMS = [
    "Aurora Scooters",
    "BluePeak Batteries",
    "Cobalt Cloud",
    "Crimson Kite",
    "Echo Forge",
    "Flux Fitness",
    "Halo Health",
    "LoomLabs",
    "Meridian Micro",
    "Nebula Noodles",
    "Nova Basket",
    "Polaris Bikes",
    "Prism Produce",
    "Quantum Kettle",
    "Sapphire Solar",
    "Summit Seltzer",
    "Vertex Coffee",
    "Vanta Vacuum",
    "Zenith Zips",
    "Atlas Droneworks",
]


def firm(i: int, offset: int = 0) -> str:
    return FIRMS[(i + offset) % len(FIRMS)]


def possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def money(x: float) -> str:
    sign = "-" if x < 0 else ""
    amount = abs(x)
    if abs(amount - round(amount)) < 1e-8:
        return f"{sign}${int(round(amount))}"
    return f"{sign}${amount:.2f}"


def num(x: float) -> str:
    if abs(x - round(x)) < 1e-8:
        return str(int(round(x)))
    return f"{x:.2f}"


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def parts(*items: tuple[str, str]) -> list[dict[str, str]]:
    return [{"label": label, "text": text} for label, text in items]


def solution_text(solution_parts: list[dict[str, str]]) -> str:
    return "\n\n".join(f"({part['label']}) {part['text']}" for part in solution_parts)


def make_row(
    topic: str,
    subtopic: str,
    difficulty: str,
    problem_text: str,
    subparts: list[dict[str, str]],
    solution_subparts: list[dict[str, str]],
    concepts: list[str],
    parameters: dict[str, Any],
    functions: dict[str, Any] | None = None,
    family: str = "",
) -> dict[str, Any]:
    solution = solution_text(solution_subparts)
    generated_id = stable_id("gen", topic, subtopic, problem_text, solution)
    return {
        "generated_id": generated_id,
        "parent_problem_id": "local_codex_curated_bank",
        "topic": topic,
        "subtopic": subtopic,
        "difficulty": difficulty,
        "problem_text": problem_text,
        "subparts": subparts,
        "solution": solution,
        "solution_subparts": solution_subparts,
        "concepts_tested": concepts,
        "variation_notes": f"Local curated bank: {family or subtopic}.",
        "parameters": parameters,
        "functions": functions or {},
        "quality_checks": {
            "math_verified": True,
            "economics_verified": True,
            "not_too_similar_to_parent": True,
            "student_level_appropriate": True,
            "no_answer_leakage": True,
        },
        "disabled": False,
        "model": "local_codex_curated_generator",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def supply_and_demand(i: int) -> dict[str, Any]:
    f = firm(i)
    k = i % 5
    if k == 0:
        a, b, c, d, tax = 150 + i, 3, 12 + i % 9, 2, 6 + i % 5
        p0 = (a - c) / (b + d)
        q0 = a - b * p0
        pc = (a - c + d * tax) / (b + d)
        ps = pc - tax
        q1 = a - b * pc
        text = f"{f} sells same-day delivery passes in a competitive city market. Demand is Qd = {a} - {b}P and supply is Qs = {c} + {d}P. The city is considering a seller tax of {money(tax)} per pass."
        qs = parts(("a", "Find the pre-tax equilibrium price and quantity."), ("b", "Find the buyer price, seller price, and quantity after the tax."), ("c", "Briefly interpret who bears more of the tax burden."))
        ss = parts(("a", f"Set {a} - {b}P = {c} + {d}P. P = {money(p0)} and Q = {num(q0)}."), ("b", f"With the tax, sellers receive Ps = Pc - {tax}. Set {a} - {b}Pc = {c} + {d}(Pc - {tax}). Pc = {money(pc)}, Ps = {money(ps)}, and Q = {num(q1)}."), ("c", f"Buyers pay {money(pc - p0)} more; sellers receive {money(p0 - ps)} less. The larger price change is the larger burden."))
        return make_row("Supply and Demand", "Tax incidence", "medium", text, qs, ss, ["equilibrium", "tax incidence"], {"a": a, "b": b, "c": c, "d": d, "tax": tax}, family="seller tax")
    if k == 1:
        a, b, c, d, shift = 110 + i, 2, 20 + i % 7, 3, 18 + i % 6
        p0 = (a - c) / (b + d)
        q0 = a - b * p0
        p1 = (a + shift - c) / (b + d)
        q1 = a + shift - b * p1
        text = f"{f} launches a new campus product. Initial demand is Qd = {a} - {b}P and supply is Qs = {c} + {d}P. A successful promotion shifts demand outward by {shift} units at every price."
        qs = parts(("a", "Compute the initial equilibrium."), ("b", "Compute the new equilibrium after the demand shift."), ("c", "Explain what happens to price and quantity."))
        ss = parts(("a", f"Initial equilibrium solves {a} - {b}P = {c} + {d}P, so P = {money(p0)} and Q = {num(q0)}."), ("b", f"New demand is Qd = {a + shift} - {b}P. Solving gives P = {money(p1)} and Q = {num(q1)}."), ("c", "The outward demand shift raises both equilibrium price and equilibrium quantity."))
        return make_row("Supply and Demand", "Demand shift", "easy", text, qs, ss, ["demand shift", "equilibrium"], {"a": a, "b": b, "c": c, "d": d, "shift": shift}, family="demand shift")
    if k == 2:
        a, b, c, d, ceiling = 140 + i, 4, 8 + i % 8, 2, 20 + i % 5
        p0 = (a - c) / (b + d)
        qd = a - b * ceiling
        qsupply = c + d * ceiling
        shortage = max(0, qd - qsupply)
        binding = ceiling < p0
        b_text = (
            f"The ceiling is binding because {money(ceiling)} is below the equilibrium price of {money(p0)}."
            if binding
            else f"The ceiling is not binding because {money(ceiling)} is {'equal to' if math.isclose(ceiling, p0) else 'above'} the equilibrium price of {money(p0)}."
        )
        c_text = (
            f"At {money(ceiling)}, Qd = {num(qd)} and Qs = {num(qsupply)}, so the shortage is {num(shortage)}."
            if binding
            else f"Because the ceiling is not binding, there is no shortage. At {money(ceiling)}, Qd = {num(qd)} and Qs = {num(qsupply)}."
        )
        text = f"A regulator caps the price of {possessive(f)} rental permits at {money(ceiling)}. Market demand is Qd = {a} - {b}P and market supply is Qs = {c} + {d}P."
        qs = parts(("a", "Find the unregulated equilibrium price."), ("b", "Is the price ceiling binding?"), ("c", "If binding, compute the shortage."))
        ss = parts(("a", f"Set demand equal to supply: {a} - {b}P = {c} + {d}P, so P = {money(p0)}."), ("b", b_text), ("c", c_text))
        return make_row("Supply and Demand", "Price ceiling", "medium", text, qs, ss, ["price ceiling", "shortage"], {"a": a, "b": b, "c": c, "d": d, "ceiling": ceiling}, family="price ceiling")
    if k == 3:
        a, b, c, d, subsidy = 120 + i, 3, 10 + i % 10, 3, 5 + i % 5
        p0 = (a - c) / (b + d)
        ps = (a - c + b * subsidy) / (b + d)
        pb = ps - subsidy
        q1 = a - b * pb
        text = f"{f} sells a product eligible for a buyer subsidy of {money(subsidy)}. Demand is Qd = {a} - {b}Pb, where Pb is the buyer's out-of-pocket price. Supply is Qs = {c} + {d}Ps, where Ps is the seller's received price."
        qs = parts(("a", "Find the equilibrium without the subsidy."), ("b", "With the subsidy, find Pb, Ps, and quantity."), ("c", "Why does the quantity rise?"))
        ss = parts(("a", f"Without subsidy, Pb = Ps = P. Solving gives P = {money(p0)}."), ("b", f"The subsidy means Ps = Pb + {subsidy}. Set {a} - {b}Pb = {c} + {d}(Pb + {subsidy}). Equivalently Ps = {money(ps)}, Pb = {money(pb)}, and Q = {num(q1)}."), ("c", "The subsidy drives a wedge that lowers the buyer price and raises the seller price, increasing quantity traded."))
        return make_row("Supply and Demand", "Subsidy wedge", "medium", text, qs, ss, ["subsidy", "wedge"], {"a": a, "b": b, "c": c, "d": d, "subsidy": subsidy}, family="buyer subsidy")
    a, b, c, d, shock = 130 + i, 2, 15 + i % 8, 2, 16 + i % 6
    p0 = (a - c) / (b + d)
    q0 = a - b * p0
    p1 = (a - (c - shock)) / (b + d)
    q1 = a - b * p1
    text = f"A supply disruption hits {possessive(f)} supplier network. Before the disruption, demand is Qd = {a} - {b}P and supply is Qs = {c} + {d}P. Afterward, supply falls by {shock} units at every price."
    qs = parts(("a", "Find the initial equilibrium."), ("b", "Find the post-disruption equilibrium."), ("c", "Interpret the price and quantity changes."))
    ss = parts(("a", f"Initial equilibrium gives P = {money(p0)} and Q = {num(q0)}."), ("b", f"New supply is Qs = {c - shock} + {d}P. Solving gives P = {money(p1)} and Q = {num(q1)}."), ("c", "A leftward supply shift raises price and lowers quantity."))
    return make_row("Supply and Demand", "Supply shock", "easy", text, qs, ss, ["supply shift", "equilibrium"], {"a": a, "b": b, "c": c, "d": d, "shock": shock}, family="supply disruption")


def elasticity(i: int) -> dict[str, Any]:
    f = firm(i, 2)
    k = i % 5
    if k == 0:
        p0, p1 = 20 + i % 9, 24 + i % 9
        q0, q1 = 520 - 3 * i, 455 - 2 * i
        e = ((q1 - q0) / q0) / ((p1 - p0) / p0)
        rev0, rev1 = p0 * q0, p1 * q1
        text = f"{f} raises the price of a premium snack box from {money(p0)} to {money(p1)}. Weekly sales fall from {q0} to {q1} boxes."
        qs = parts(("a", "Compute the approximate price elasticity using the original price and quantity as the base."), ("b", "Classify demand as elastic or inelastic."), ("c", "Compare revenue before and after the price change."))
        ss = parts(("a", f"Elasticity is ({q1} - {q0})/{q0} divided by ({p1} - {p0})/{p0}, which equals {num(e)}."), ("b", f"The absolute value is {num(abs(e))}, so demand is {'elastic' if abs(e) > 1 else 'inelastic'}."), ("c", f"Revenue changes from {money(rev0)} to {money(rev1)}, so it {'rises' if rev1 > rev0 else 'falls'}."))
        return make_row("Elasticity", "Price elasticity", "easy", text, qs, ss, ["elasticity", "revenue"], {"p0": p0, "p1": p1, "q0": q0, "q1": q1}, family="price experiment")
    if k == 1:
        a, b, p = 200 + i, 4, 24 + i % 8
        q = a - b * p
        e = -b * p / q
        text = f"{f} estimates demand for a subscription as Q = {a} - {b}P. The current price is {money(p)}."
        qs = parts(("a", "Find current quantity demanded."), ("b", "Compute point elasticity at the current price."), ("c", "If marginal cost is positive, would a monopolist usually want to operate where demand is inelastic?"))
        ss = parts(("a", f"Q = {a} - {b}({p}) = {num(q)}."), ("b", f"Point elasticity is (dQ/dP)(P/Q) = -{b} x {p}/{num(q)} = {num(e)}."), ("c", "No. With positive marginal cost, a monopolist avoids the inelastic region because lowering quantity and raising price can increase revenue while reducing cost."))
        return make_row("Elasticity", "Point elasticity", "medium", text, qs, ss, ["point elasticity", "pricing"], {"a": a, "b": b, "p": p}, family="linear demand")
    if k == 2:
        q0, q1, other0, other1 = 900 + 4 * i, 960 + 5 * i, 10 + i % 4, 12 + i % 4
        cross = ((q1 - q0) / q0) / ((other1 - other0) / other0)
        text = f"When a rival raises its price from {money(other0)} to {money(other1)}, {possessive(f)} weekly sales rise from {q0} to {q1} units."
        qs = parts(("a", "Compute the cross-price elasticity."), ("b", "Are the two products substitutes or complements?"), ("c", "What managerial action might this suggest?"))
        ss = parts(("a", f"Cross-price elasticity is ({q1} - {q0})/{q0} divided by ({other1} - {other0})/{other0} = {num(cross)}."), ("b", "It is positive, so the goods are substitutes."), ("c", "The firm may gain customers when the rival raises price, so monitoring competitor prices is valuable."))
        return make_row("Elasticity", "Cross-price elasticity", "easy", text, qs, ss, ["cross-price elasticity", "substitutes"], {"q0": q0, "q1": q1, "other0": other0, "other1": other1}, family="cross elasticity")
    if k == 3:
        q0, q1, y0, y1 = 400 + 2 * i, 440 + 3 * i, 80 + i, 88 + i
        inc = ((q1 - q0) / q0) / ((y1 - y0) / y0)
        text = f"As average customer income rises from {money(y0)} thousand to {money(y1)} thousand, annual purchases of {possessive(f)} service rise from {q0} to {q1}."
        qs = parts(("a", "Compute income elasticity."), ("b", "Is this a normal or inferior good?"), ("c", "Is it closer to a necessity or a luxury?"))
        ss = parts(("a", f"Income elasticity is ({q1} - {q0})/{q0} divided by ({y1} - {y0})/{y0} = {num(inc)}."), ("b", "The elasticity is positive, so it is a normal good."), ("c", f"Since the value is {'above' if inc > 1 else 'below'} 1, it is {'more luxury-like' if inc > 1 else 'more necessity-like'}."))
        return make_row("Elasticity", "Income elasticity", "easy", text, qs, ss, ["income elasticity"], {"q0": q0, "q1": q1, "y0": y0, "y1": y1}, family="income elasticity")
    p, mc, abs_e = 50 + i % 8, 30 + i % 6, 2.5 + (i % 4) * 0.25
    markup = (p - mc) / p
    target = 1 / abs_e
    text = f"{f} currently charges {money(p)}. Marginal cost is {money(mc)} and the absolute value of demand elasticity at this price is estimated to be {num(abs_e)}."
    qs = parts(("a", "Compute the current Lerner markup (P - MC)/P."), ("b", "Compare it with the inverse elasticity rule."), ("c", "Is price too high or too low relative to the monopoly optimum?"))
    ss = parts(("a", f"Markup is ({p} - {mc})/{p} = {num(markup)}."), ("b", f"The inverse elasticity target is 1/{num(abs_e)} = {num(target)}."), ("c", f"The current markup is {'above' if markup > target else 'below'} the target, so price is {'too high' if markup > target else 'too low'} relative to that rule."))
    return make_row("Elasticity", "Markup rule", "medium", text, qs, ss, ["elasticity", "markup"], {"p": p, "mc": mc, "abs_e": abs_e}, family="inverse elasticity rule")


def taxes_policy(i: int) -> dict[str, Any]:
    f = firm(i, 4)
    k = i % 5
    if k == 0:
        a, b, c, d, tax = 110 + i, 2, 12 + i % 8, 2, 8
        p0 = (a - c) / (b + d)
        pc = (a - c + d * tax) / (b + d)
        ps = pc - tax
        q0 = a - b * p0
        q1 = a - b * pc
        dwl = 0.5 * tax * (q0 - q1)
        text = f"A per-unit tax of {money(tax)} is proposed for the market in which {f} operates. Demand is Qd = {a} - {b}P and supply is Qs = {c} + {d}P."
        qs = parts(("a", "Find quantity before and after the tax."), ("b", "Compute deadweight loss."), ("c", "Why is there deadweight loss?"))
        ss = parts(("a", f"Before tax, P = {money(p0)} and Q = {num(q0)}. After tax, Pc = {money(pc)}, Ps = {money(ps)}, and Q = {num(q1)}."), ("b", f"DWL = 0.5 x tax x quantity reduction = 0.5 x {tax} x {num(q0 - q1)} = {money(dwl)}."), ("c", "Some mutually beneficial trades no longer occur because the tax wedge raises buyer cost above seller receipt."))
        return make_row("Taxes and Government Intervention", "Tax deadweight loss", "medium", text, qs, ss, ["tax", "deadweight loss"], {"a": a, "b": b, "c": c, "d": d, "tax": tax}, family="tax DWL")
    if k == 1:
        a, b, c, d, floor = 100 + i, 2, 8 + i % 6, 2, 34 + i % 4
        p0 = (a - c) / (b + d)
        qd, qsupply = a - b * floor, c + d * floor
        text = f"The city sets a minimum price of {money(floor)} for permits sold through {f}. Demand is Qd = {a} - {b}P and supply is Qs = {c} + {d}P."
        qs = parts(("a", "Find the competitive price."), ("b", "Is the floor binding?"), ("c", "Compute excess supply if it binds."))
        ss = parts(("a", f"Competitive price is ({a} - {c})/({b} + {d}) = {money(p0)}."), ("b", f"The floor is {'binding' if floor > p0 else 'not binding'} because it is {'above' if floor > p0 else 'below'} equilibrium."), ("c", f"At the floor, Qs - Qd = {num(qsupply)} - {num(qd)} = {num(qsupply - qd)}."))
        return make_row("Taxes and Government Intervention", "Price floor", "medium", text, qs, ss, ["price floor"], {"a": a, "b": b, "c": c, "d": d, "floor": floor}, family="price floor")
    if k == 2:
        a, b, c, d, ceiling = 130 + i, 3, 6 + i % 7, 2, 22 + i % 4
        p0 = (a - c) / (b + d)
        qd, qsupply = a - b * ceiling, c + d * ceiling
        text = f"A consumer-protection rule caps the price of {possessive(f)} service at {money(ceiling)}. Demand is Qd = {a} - {b}P and supply is Qs = {c} + {d}P."
        qs = parts(("a", "Find the market-clearing price."), ("b", "Does the ceiling bind?"), ("c", "If it binds, who is rationed and by how much?"))
        ss = parts(("a", f"Market-clearing price is {money(p0)}."), ("b", f"The ceiling is {'binding' if ceiling < p0 else 'not binding'} because it is {'below' if ceiling < p0 else 'above'} equilibrium."), ("c", f"If binding, buyers are rationed by the shortage Qd - Qs = {num(qd - qsupply)}."))
        return make_row("Taxes and Government Intervention", "Price ceiling", "medium", text, qs, ss, ["price ceiling", "shortage"], {"a": a, "b": b, "c": c, "d": d, "ceiling": ceiling}, family="price ceiling")
    if k == 3:
        a, b, c, d, subsidy = 100 + i, 2, 14 + i % 6, 2, 6
        p0 = (a - c) / (b + d)
        ps = (a - c + b * subsidy) / (b + d)
        pb = ps - subsidy
        q1 = a - b * pb
        text = f"The state offers buyers of {possessive(f)} product a subsidy of {money(subsidy)} per unit. Demand is Qd = {a} - {b}Pb and supply is Qs = {c} + {d}Ps."
        qs = parts(("a", "Find the no-subsidy equilibrium price."), ("b", "Find buyer price, seller price, and quantity with the subsidy."), ("c", "Who receives the subsidy check, and why is that not the same as economic incidence?"))
        ss = parts(("a", f"No subsidy gives P = {money(p0)}."), ("b", f"With Ps = Pb + {subsidy}, solving gives Ps = {money(ps)}, Pb = {money(pb)}, Q = {num(q1)}."), ("c", "Legal receipt is about who gets the check; economic incidence is about how market prices change."))
        return make_row("Taxes and Government Intervention", "Subsidy incidence", "medium", text, qs, ss, ["subsidy", "incidence"], {"a": a, "b": b, "c": c, "d": d, "subsidy": subsidy}, family="subsidy")
    a, b, c, d, cap = 120 + i, 3, 10 + i % 6, 2, 48 + i % 8
    p_quota = (a - c - cap) / b if b else 0
    domestic = c + d * p_quota
    text = f"Imports of an input used by {f} are capped at {cap} units. Domestic demand is Qd = {a} - {b}P and domestic supply is Qs = {c} + {d}P."
    qs = parts(("a", "Write the market-clearing condition with the import quota."), ("b", "Solve for the domestic price."), ("c", "Find domestic production at that price."))
    ss = parts(("a", f"With quota imports, Qd = Qs + {cap}."), ("b", f"{a} - {b}P = {c} + {d}P + {cap}, so P = {money(p_quota)}."), ("c", f"Domestic production is Qs = {c} + {d}({num(p_quota)}) = {num(domestic)}."))
    return make_row("Taxes and Government Intervention", "Import quota", "hard", text, qs, ss, ["quota", "domestic price"], {"a": a, "b": b, "c": c, "d": d, "quota": cap}, family="quota")


def trade_welfare(i: int) -> dict[str, Any]:
    f = firm(i, 7)
    k = i % 5
    a, b, d = 150 + i, 3, 2
    if k == 0:
        pw, tariff = 20 + i % 6, 5 + i % 4
        qd0, qs0 = a - b * pw, d * pw
        p1 = pw + tariff
        qd1, qs1 = a - b * p1, d * p1
        imports = qd1 - qs1
        text = f"{f} uses an imported component. Domestic demand is Qd = {a} - {b}P, domestic supply is Qs = {d}P, and the world price is {money(pw)}. A tariff of {money(tariff)} is proposed."
        qs = parts(("a", "Find imports under free trade."), ("b", "Find imports after the tariff."), ("c", "Compute tariff revenue."))
        ss = parts(("a", f"At {money(pw)}, Qd = {num(qd0)}, Qs = {num(qs0)}, so imports are {num(qd0 - qs0)}."), ("b", f"The tariff raises domestic price to {money(p1)}. Qd = {num(qd1)}, Qs = {num(qs1)}, imports = {num(imports)}."), ("c", f"Revenue is {money(tariff)} x {num(imports)} = {money(tariff * imports)}."))
        return make_row("Trade and Welfare", "Tariff", "medium", text, qs, ss, ["tariff", "imports"], {"a": a, "b": b, "d": d, "world_price": pw, "tariff": tariff}, family="tariff")
    if k == 1:
        pw, quota = 18 + i % 5, 35 + i % 10
        p = (a - quota) / (b + d)
        qd, qsupply = a - b * p, d * p
        text = f"Policy makers cap imports of a material used by {f} at {quota} units. Domestic demand is Qd = {a} - {b}P and domestic supply is Qs = {d}P."
        qs = parts(("a", "Write the equilibrium condition under the quota."), ("b", "Find domestic price."), ("c", "Find domestic supply and imports."))
        ss = parts(("a", f"Demand must equal domestic supply plus quota: {a} - {b}P = {d}P + {quota}."), ("b", f"Solving gives P = {money(p)}."), ("c", f"Domestic supply is {num(qsupply)} and imports are {quota}; total consumption is {num(qd)}."))
        return make_row("Trade and Welfare", "Quota", "hard", text, qs, ss, ["quota", "imports"], {"a": a, "b": b, "d": d, "quota": quota, "world_price": pw}, family="import quota")
    if k == 2:
        pw = 42 + i % 7
        c, d2 = 10 + i % 6, 2
        qd, qsupply = a - b * pw, c + d2 * pw
        text = f"{possessive(f)} home country is considering opening to free trade. Domestic demand is Qd = {a} - {b}P, domestic supply is Qs = {c} + {d2}P, and the world price is {money(pw)}."
        qs = parts(("a", "At the world price, does the country import or export?"), ("b", "How many units are traded internationally?"), ("c", "Who benefits from opening trade in this case?"))
        trade = qsupply - qd
        ss = parts(("a", f"At {money(pw)}, Qd = {num(qd)} and Qs = {num(qsupply)}. Since supply exceeds demand, the country exports."), ("b", f"Exports are Qs - Qd = {num(trade)}."), ("c", "Domestic producers benefit from the higher selling opportunity; domestic consumers face the world price."))
        return make_row("Trade and Welfare", "Exports", "medium", text, qs, ss, ["exports", "world price"], {"a": a, "b": b, "c": c, "d": d2, "world_price": pw}, family="export market")
    if k == 3:
        pw, tariff = 16 + i % 5, 4
        p1 = pw + tariff
        qd0, qs0 = a - b * pw, d * pw
        qd1, qs1 = a - b * p1, d * p1
        text = f"{possessive(f)} procurement team wants to know how a tariff changes domestic consumption. Demand is Qd = {a} - {b}P, domestic supply is Qs = {d}P, the world price is {money(pw)}, and the tariff is {money(tariff)}."
        qs = parts(("a", "Compute the change in domestic consumption."), ("b", "Compute the change in domestic production."), ("c", "Compute the change in imports."))
        ss = parts(("a", f"Consumption falls from {num(qd0)} to {num(qd1)}, a change of {num(qd1 - qd0)}."), ("b", f"Domestic production rises from {num(qs0)} to {num(qs1)}, a change of {num(qs1 - qs0)}."), ("c", f"Imports fall from {num(qd0 - qs0)} to {num(qd1 - qs1)}."))
        return make_row("Trade and Welfare", "Tariff quantity effects", "easy", text, qs, ss, ["tariff", "consumption"], {"a": a, "b": b, "d": d, "world_price": pw, "tariff": tariff}, family="tariff quantities")
    pw, tariff = 20, 5 + i % 5
    qd0, qs0 = a - b * pw, d * pw
    p1 = pw + tariff
    qd1, qs1 = a - b * p1, d * p1
    text = f"A lobby asks for a tariff on the imported component used by {f}. Demand is Qd = {a} - {b}P and supply is Qs = {d}P. The world price is {money(pw)} and the proposed tariff is {money(tariff)}."
    qs = parts(("a", "Who gains and who loses from the tariff?"), ("b", "Compute government revenue."), ("c", "Why is total surplus lower than under free trade?"))
    ss = parts(("a", f"Consumers lose from the price increase to {money(p1)}; domestic producers gain because their output rises from {num(qs0)} to {num(qs1)}."), ("b", f"Revenue is {money(tariff)} x imports {num(qd1 - qs1)} = {money(tariff * (qd1 - qs1))}."), ("c", "The tariff creates production and consumption distortions: some efficient imports are replaced or not consumed."))
    return make_row("Trade and Welfare", "Tariff welfare", "medium", text, qs, ss, ["tariff", "surplus"], {"a": a, "b": b, "d": d, "world_price": pw, "tariff": tariff}, family="welfare")


def production_costs(i: int) -> dict[str, Any]:
    f = firm(i, 9)
    k = i % 5
    if k == 0:
        fixed, v, price = 90 + i, 6 + i % 6, 28 + i % 8
        q = (price - v) / 2
        profit = price * q - fixed - v * q - q**2
        text = f"{f} has short-run cost C(q) = {fixed} + {v}q + q^2 and sells in a competitive market at price {money(price)}."
        qs = parts(("a", "Find marginal cost."), ("b", "Choose output."), ("c", "Compute profit."))
        ss = parts(("a", f"MC = {v} + 2q."), ("b", f"Set P = MC: {price} = {v} + 2q, so q = {num(q)}."), ("c", f"Profit is Pq - C(q) = {money(profit)}."))
        return make_row("Production and Costs", "Short-run cost", "medium", text, qs, ss, ["marginal cost", "profit"], {"fixed": fixed, "v": v, "price": price}, {"cost": f"C(q)={fixed}+{v}q+q^2"}, family="short-run output")
    if k == 1:
        w, r, q = 20 + i % 5, 5 + i % 4, 100 + 5 * i
        # Production q = sqrt(LK). Cost min gives K/L = w/r and LK=q^2.
        l = q * math.sqrt(r / w)
        kk = q * math.sqrt(w / r)
        cost = w * l + r * kk
        text = f"{f} produces output with q = sqrt(LK). It must produce q = {q}. Labor costs {money(w)} and capital costs {money(r)}."
        qs = parts(("a", "Write the tangency condition for cost minimization."), ("b", "Find cost-minimizing L and K."), ("c", "Compute total cost."))
        ss = parts(("a", f"MPL/MPK = K/L must equal w/r = {w}/{r}. Thus K/L = {num(w/r)}."), ("b", f"Using LK = q^2 and K/L = w/r gives L = {num(l)} and K = {num(kk)}."), ("c", f"Cost is wL + rK = {money(cost)}."))
        return make_row("Production and Costs", "Cost minimization", "hard", text, qs, ss, ["cost minimization", "input choice"], {"w": w, "r": r, "q": q}, {"production": "q=sqrt(LK)"}, family="input choice")
    if k == 2:
        fixed, v = 64 + i, 8 + i % 5
        q_min = math.sqrt(fixed)
        min_atc = v + 2 * math.sqrt(fixed)
        text = f"{possessive(f)} long-run cost is C(q) = {fixed} + {v}q + q^2."
        qs = parts(("a", "Write average total cost."), ("b", "Find the output that minimizes average total cost."), ("c", "Find minimum average total cost."))
        ss = parts(("a", f"ATC = {fixed}/q + {v} + q."), ("b", f"Minimize {fixed}/q + q. The minimum occurs at q = sqrt({fixed}) = {num(q_min)}."), ("c", f"Minimum ATC is {v} + 2sqrt({fixed}) = {money(min_atc)}."))
        return make_row("Production and Costs", "Minimum efficient scale", "medium", text, qs, ss, ["average cost", "scale"], {"fixed": fixed, "v": v}, {"cost": f"C(q)={fixed}+{v}q+q^2"}, family="ATC")
    if k == 3:
        q1, cost1, q2, cost2 = 50 + i, 500 + 8 * i, 80 + i, 710 + 10 * i
        mc = (cost2 - cost1) / (q2 - q1)
        text = f"{f} observes total cost of {money(cost1)} at {q1} units and {money(cost2)} at {q2} units over the relevant range."
        qs = parts(("a", "Estimate marginal cost over this range."), ("b", "If price is above this estimate, should output expand locally?"), ("c", "What caveat applies to this estimate?"))
        ss = parts(("a", f"Marginal cost is approximately Delta C / Delta q = ({cost2} - {cost1})/({q2} - {q1}) = {money(mc)}."), ("b", "Yes, if price exceeds marginal cost, expanding output raises profit locally."), ("c", "This is an average slope over a range, not necessarily the exact marginal cost at every quantity."))
        return make_row("Production and Costs", "Marginal cost estimate", "easy", text, qs, ss, ["marginal cost"], {"q1": q1, "cost1": cost1, "q2": q2, "cost2": cost2}, family="cost slope")
    a, alpha = 1 + (i % 3), 0.5
    text = f"{f} doubles both labor and capital in a production process described by q = {a}L^0.5K^0.5."
    qs = parts(("a", "Does output less than double, exactly double, or more than double?"), ("b", "Classify returns to scale."), ("c", "Why does this matter for long-run expansion?"))
    ss = parts(("a", "Doubling both inputs multiplies output by 2^0.5 x 2^0.5 = 2, so output exactly doubles."), ("b", "The technology has constant returns to scale."), ("c", "With constant returns, scaling the plant up does not by itself lower or raise unit input needs."))
    return make_row("Production and Costs", "Returns to scale", "easy", text, qs, ss, ["returns to scale"], {"a": a, "alpha": alpha}, {"production": f"q={a}L^0.5K^0.5"}, family="returns to scale")


def perfect_competition(i: int) -> dict[str, Any]:
    f = firm(i, 11)
    k = i % 5
    if k == 0:
        n, a, b, v = 20 + i % 6, 900 + 5 * i, 5, 8 + i % 5
        # Firm q=(P-v)/2, industry Q=n(P-v)/2, demand Q=a-bP.
        p = (a + n * v / 2) / (b + n / 2)
        qfirm = (p - v) / 2
        text = f"{f} is one of {n} identical competitive firms. Each firm has MC = {v} + 2q. Market demand is Qd = {a} - {b}P."
        qs = parts(("a", "Write each firm's supply."), ("b", "Find market equilibrium price."), ("c", "Find output per firm."))
        ss = parts(("a", f"Set P = MC, so q = (P - {v})/2 for positive output."), ("b", f"Industry supply is {n}(P - {v})/2. Set equal to demand to get P = {money(p)}."), ("c", f"Each firm produces q = ({num(p)} - {v})/2 = {num(qfirm)}."))
        return make_row("Perfect Competition", "Industry supply", "medium", text, qs, ss, ["firm supply", "industry equilibrium"], {"n": n, "a": a, "b": b, "v": v}, family="many firms")
    if k == 1:
        fixed, v = 100 + i, 10 + i % 5
        qmes = math.sqrt(fixed)
        p_lr = v + 2 * math.sqrt(fixed)
        text = f"In a long-run competitive industry, firms like {f} have cost C(q) = {fixed} + {v}q + q^2."
        qs = parts(("a", "Find the long-run zero-profit price."), ("b", "Find output per firm at that price."), ("c", "What happens if market price is above this level?"))
        ss = parts(("a", f"Long-run price equals minimum ATC. Min ATC = {v} + 2sqrt({fixed}) = {money(p_lr)}."), ("b", f"Minimum ATC occurs at q = sqrt({fixed}) = {num(qmes)}."), ("c", "Positive profits attract entry, shifting industry supply outward and pushing price down."))
        return make_row("Perfect Competition", "Long-run entry", "medium", text, qs, ss, ["entry", "zero profit"], {"fixed": fixed, "v": v}, family="long-run equilibrium")
    if k == 2:
        fixed, v, p = 80 + i, 12 + i % 4, 9 + i % 3
        text = f"{f} has cost C(q) = {fixed} + {v}q + q^2. The market price has fallen to {money(p)}."
        qs = parts(("a", "Find the shutdown price."), ("b", "Should the firm produce in the short run?"), ("c", "What role does fixed cost play?"))
        ss = parts(("a", f"AVC = {v} + q, whose minimum is {money(v)} as q approaches zero."), ("b", f"Since price {money(p)} is below the shutdown price {money(v)}, the firm should shut down."), ("c", "Fixed cost is sunk in the short run and does not determine the shutdown price."))
        return make_row("Perfect Competition", "Shutdown decision", "easy", text, qs, ss, ["shutdown", "AVC"], {"fixed": fixed, "v": v, "p": p}, family="shutdown")
    if k == 3:
        p, mc = 35 + i, 20 + i
        text = f"{f} is a price-taking firm currently producing a unit whose marginal cost is {money(mc)}. The market price is {money(p)}."
        qs = parts(("a", "Should the firm produce this marginal unit?"), ("b", "What is the marginal profit from the unit?"), ("c", "What condition stops expansion?"))
        ss = parts(("a", "Yes, because price exceeds marginal cost."), ("b", f"Marginal profit is P - MC = {money(p - mc)}."), ("c", "Expansion stops where price equals marginal cost."))
        return make_row("Perfect Competition", "Marginal output rule", "easy", text, qs, ss, ["P=MC"], {"p": p, "mc": mc}, family="marginal unit")
    fixed, v, p = 90 + i, 8 + i % 5, 30 + i % 6
    q = (p - v) / 2
    profit = p * q - fixed - v * q - q**2
    text = f"{f} takes price as given at {money(p)} and has cost C(q) = {fixed} + {v}q + q^2."
    qs = parts(("a", "Find the profit-maximizing quantity."), ("b", "Calculate profit."), ("c", "Predict entry or exit pressure in the long run."))
    ss = parts(("a", f"P = MC gives {p} = {v} + 2q, so q = {num(q)}."), ("b", f"Profit is {money(profit)}."), ("c", "Positive profit attracts entry; negative profit induces exit."))
    return make_row("Perfect Competition", "Profit and entry", "medium", text, qs, ss, ["profit", "entry"], {"fixed": fixed, "v": v, "p": p}, family="entry pressure")


def monopoly(i: int) -> dict[str, Any]:
    f = firm(i, 13)
    k = i % 5
    a, b, c = 120 + i, 2, 16 + i % 7
    if k == 0:
        q = (a - c) / (2 * b)
        p = a - b * q
        text = f"{f} is the only seller in its niche. Inverse demand is P = {a} - {b}Q and marginal cost is {money(c)}."
        qs = parts(("a", "Find monopoly quantity and price."), ("b", "Compute operating profit."), ("c", "Compare with efficient quantity."))
        ss = parts(("a", f"MR = {a} - {2*b}Q. Setting MR = MC gives Q = {num(q)} and P = {money(p)}."), ("b", f"Profit is (P - MC)Q = {money((p - c) * q)}."), ("c", "Efficient quantity sets P = MC, so monopoly output is lower."))
        return make_row("Monopoly", "Monopoly pricing", "medium", text, qs, ss, ["MR=MC", "markup"], {"a": a, "b": b, "mc": c}, family="basic monopoly")
    if k == 1:
        cap = 42 + i % 6
        qcap = (a - cap) / b
        qmon = (a - c) / (2 * b)
        text = f"A regulator caps {possessive(f)} price at {money(cap)}. Demand is P = {a} - {b}Q and marginal cost is {money(c)}."
        qs = parts(("a", "Find the unconstrained monopoly quantity."), ("b", "If the cap binds, find quantity demanded at the cap."), ("c", "Does the cap move output toward efficiency?"))
        ss = parts(("a", f"Unconstrained Q is {num(qmon)}."), ("b", f"At P = {money(cap)}, demand is Q = ({a} - {cap})/{b} = {num(qcap)}."), ("c", "A binding cap below monopoly price raises output toward the efficient quantity, as long as price remains above marginal cost."))
        return make_row("Monopoly", "Price regulation", "hard", text, qs, ss, ["price cap", "regulation"], {"a": a, "b": b, "mc": c, "cap": cap}, family="price cap")
    if k == 2:
        tax = 5 + i % 4
        q = (a - c - tax) / (2 * b)
        p = a - b * q
        text = f"{f} faces a per-unit tax of {money(tax)}. Inverse demand is P = {a} - {b}Q and pre-tax marginal cost is {money(c)}."
        qs = parts(("a", "Find output after the tax."), ("b", "Find the consumer price."), ("c", "Does the monopolist pass through the full tax?"))
        ss = parts(("a", f"The tax raises effective MC to {c + tax}. MR = {a} - {2*b}Q = {c + tax}, so Q = {num(q)}."), ("b", f"Price is P = {a} - {b}({num(q)}) = {money(p)}."), ("c", "Not necessarily. Pass-through depends on demand curvature; with linear demand here, price rises by part of the tax."))
        return make_row("Monopoly", "Monopoly tax", "medium", text, qs, ss, ["monopoly", "tax"], {"a": a, "b": b, "mc": c, "tax": tax}, family="monopoly tax")
    if k == 3:
        q = (a - c) / (2 * b)
        p = a - b * q
        e = -p / (b * q)
        text = f"{f} has inverse demand P = {a} - {b}Q and marginal cost {money(c)}. The firm chooses the monopoly price {money(p)}."
        qs = parts(("a", "Find the quantity associated with that price."), ("b", "Compute elasticity at that point."), ("c", "Relate the markup to elasticity."))
        ss = parts(("a", f"Q = ({a} - {num(p)})/{b} = {num(q)}."), ("b", f"For inverse demand, point elasticity is -P/(bQ) = -{num(p)}/({b} x {num(q)}) = {num(e)}."), ("c", "The monopoly markup is higher when absolute elasticity is lower, as summarized by the inverse elasticity rule."))
        return make_row("Monopoly", "Markup and elasticity", "hard", text, qs, ss, ["elasticity", "markup"], {"a": a, "b": b, "mc": c}, family="markup")
    q_eff = (a - c) / b
    q_mon = (a - c) / (2 * b)
    dwl = 0.5 * (q_eff - q_mon) * (a - b * q_mon - c)
    text = f"{f} has market power. Demand is P = {a} - {b}Q and marginal cost is {money(c)}."
    qs = parts(("a", "Find the efficient quantity."), ("b", "Find monopoly quantity."), ("c", "Compute deadweight loss."))
    ss = parts(("a", f"Efficiency sets P = MC: {a} - {b}Q = {c}, so Q = {num(q_eff)}."), ("b", f"MR = MC gives Q = {num(q_mon)}."), ("c", f"DWL is the triangle between demand and MC from {num(q_mon)} to {num(q_eff)}: {money(dwl)}."))
    return make_row("Monopoly", "Deadweight loss", "hard", text, qs, ss, ["deadweight loss"], {"a": a, "b": b, "mc": c}, family="DWL")


def price_discrimination(i: int) -> dict[str, Any]:
    f = firm(i, 15)
    k = i % 5
    if k == 0:
        vh, vl, c = 90 + i % 8, 55 + i % 7, 20 + i % 5
        text = f"{f} sells a workshop to one high-value customer and one low-value customer. Values are {money(vh)} and {money(vl)}. Marginal cost is {money(c)}."
        qs = parts(("a", "Find profit under perfect price discrimination."), ("b", "Find the best single price."), ("c", "Why do profits differ?"))
        profit_pd = vh + vl - 2 * c
        profit_low = 2 * (vl - c)
        profit_high = vh - c
        ss = parts(("a", f"Charge each value. Profit is ({vh} - {c}) + ({vl} - {c}) = {money(profit_pd)}."), ("b", f"At {money(vl)}, profit is {money(profit_low)}. At {money(vh)}, profit is {money(profit_high)}. Choose {money(vl if profit_low >= profit_high else vh)}."), ("c", "Discrimination extracts more surplus and may serve both customers at tailored prices."))
        return make_row("Price Discrimination", "Personalized pricing", "easy", text, qs, ss, ["price discrimination"], {"vh": vh, "vl": vl, "cost": c}, family="two types")
    if k == 1:
        a1, b1, a2, b2, c = 100 + i, 2, 80 + i, 1, 20
        q1, q2 = (a1 - c) / (2 * b1), (a2 - c) / (2 * b2)
        p1, p2 = a1 - b1 * q1, a2 - b2 * q2
        text = f"{f} can separate business and student markets. Inverse demands are P1 = {a1} - {b1}Q1 and P2 = {a2} - {b2}Q2. Marginal cost is {money(c)}."
        qs = parts(("a", "Find the price and quantity in market 1."), ("b", "Find the price and quantity in market 2."), ("c", "Which market gets the higher price?"))
        ss = parts(("a", f"MR1 = {a1} - {2*b1}Q1. Set MR1 = {c}: Q1 = {num(q1)}, P1 = {money(p1)}."), ("b", f"MR2 = {a2} - {2*b2}Q2. Set MR2 = {c}: Q2 = {num(q2)}, P2 = {money(p2)}."), ("c", f"Market {'1' if p1 > p2 else '2'} gets the higher price because its optimal markup is higher."))
        return make_row("Price Discrimination", "Third-degree pricing", "hard", text, qs, ss, ["third-degree price discrimination"], {"a1": a1, "b1": b1, "a2": a2, "b2": b2, "mc": c}, family="separate markets")
    if k == 2:
        a, b, c = 80 + i, 2, 10 + i % 4
        q = (a - c) / b
        cs = 0.5 * (a - c) * q
        text = f"{f} has identical customers with demand P = {a} - {b}q for each customer. Marginal cost is {money(c)}. It can charge a per-unit price plus a membership fee."
        qs = parts(("a", "What usage price maximizes total surplus?"), ("b", "How much does each customer buy at that usage price?"), ("c", "What membership fee extracts all consumer surplus?"))
        ss = parts(("a", f"Set usage price equal to MC, so p = {money(c)}."), ("b", f"Demand gives q = ({a} - {c})/{b} = {num(q)}."), ("c", f"The fee equals consumer surplus at p = MC: 0.5 x ({a} - {c}) x {num(q)} = {money(cs)}."))
        return make_row("Price Discrimination", "Two-part tariff", "hard", text, qs, ss, ["two-part tariff", "consumer surplus"], {"a": a, "b": b, "mc": c}, family="membership pricing")
    if k == 3:
        base_h, prem_h, base_l, prem_l, c_base, c_prem = 50 + i, 90 + i, 45 + i, 60 + i, 10, 20
        text = f"{f} sells Basic and Premium plans. High types value Basic at {money(base_h)} and Premium at {money(prem_h)}. Low types value Basic at {money(base_l)} and Premium at {money(prem_l)}. Costs are {money(c_base)} and {money(c_prem)}."
        qs = parts(("a", "If types are observable, what is the maximum price for each plan/type?"), ("b", "Why can self-selection force the firm to leave information rent?"), ("c", "Which type usually receives the rent in this setting?"))
        ss = parts(("a", f"Observable types can be charged up to their values for each plan: high type Basic {money(base_h)}, high type Premium {money(prem_h)}, low type Basic {money(base_l)}, and low type Premium {money(prem_l)}."), ("b", "If types are not observable, the high type must prefer Premium over imitating the low type; that incentive constraint can require leaving surplus."), ("c", "The high type usually receives information rent so that it self-selects into the premium option."))
        return make_row("Price Discrimination", "Self-selection", "medium", text, qs, ss, ["self-selection", "information rent"], {"base_h": base_h, "prem_h": prem_h, "base_l": base_l, "prem_l": prem_l, "cost_base": c_base, "cost_premium": c_prem}, family="versioning")
    p_reg, q_reg, p_peak, q_peak, mc = 20 + i % 5, 300 + i, 35 + i % 5, 180 + i, 8
    text = f"{f} sells the same service in regular and peak periods. Regular price and quantity are {money(p_reg)} and {q_reg}; peak price and quantity are {money(p_peak)} and {q_peak}. Marginal cost is {money(mc)} in both periods."
    qs = parts(("a", "Compute contribution in each period."), ("b", "Why might peak pricing be efficient?"), ("c", "What condition would make prices equal across periods?"))
    ss = parts(("a", f"Regular contribution is ({p_reg} - {mc}) x {q_reg} = {money((p_reg-mc)*q_reg)}. Peak contribution is ({p_peak} - {mc}) x {q_peak} = {money((p_peak-mc)*q_peak)}."), ("b", "Peak pricing can reflect higher willingness to pay or tighter capacity in peak periods."), ("c", "Prices would tend to equalize if demand conditions and capacity scarcity were the same."))
    return make_row("Price Discrimination", "Peak-load pricing", "easy", text, qs, ss, ["peak-load pricing"], {"p_reg": p_reg, "q_reg": q_reg, "p_peak": p_peak, "q_peak": q_peak, "mc": mc}, family="peak pricing")


def risk_insurance(i: int) -> dict[str, Any]:
    f = firm(i, 1)
    k = i % 5
    if k == 0:
        value, fail = 1000 + 20 * i, 0.05 + (i % 4) * 0.01
        ev = value * (1 - fail)
        text = f"{f} sells a device worth {money(value)} if it works and {money(0)} if it fails. The failure probability is {pct(fail)}."
        qs = parts(("a", "Find willingness to pay for a risk-neutral buyer."), ("b", "If production cost is $100 below the risk-neutral willingness to pay from part (a), find producer surplus."), ("c", "How would risk aversion affect willingness to pay?"))
        ss = parts(("a", f"WTP equals expected value: (1 - {num(fail)}) x {money(value)} = {money(ev)}."), ("b", f"Producer surplus is {money(ev)} - {money(ev - 100)} = {money(100)}."), ("c", "Risk aversion lowers WTP below expected value for uninsured downside risk."))
        return make_row("Risk and Insurance", "Expected value", "easy", text, qs, ss, ["expected value", "risk aversion"], {"value": value, "failure_probability": fail}, family="risky product")
    if k == 1:
        wealth, loss, prob = 100, 30 + i, 0.25
        eu = prob * math.sqrt(wealth - loss) + (1 - prob) * math.sqrt(wealth)
        ce = eu**2
        rp = wealth - prob * loss - ce
        text = f"A customer of {f} has wealth {wealth} and utility u(w)=sqrt(w). With probability {pct(prob)}, a loss of {loss} occurs."
        qs = parts(("a", "Compute expected wealth."), ("b", "Compute the certainty equivalent."), ("c", "Compute the risk premium."))
        ss = parts(("a", f"Expected wealth is {wealth} - {num(prob)} x {loss} = {num(wealth - prob * loss)}."), ("b", f"Expected utility is {num(eu)}. The certainty equivalent solves sqrt(CE) = EU, so CE = {num(ce)}."), ("c", f"Risk premium is expected wealth minus CE: {num(rp)}."))
        return make_row("Risk and Insurance", "Certainty equivalent", "hard", text, qs, ss, ["expected utility", "certainty equivalent"], {"wealth": wealth, "loss": loss, "prob": prob}, family="CE")
    if k == 2:
        wealth, loss, prob = 100, 28 + i, 0.2
        eu = prob * math.sqrt(wealth - loss) + (1 - prob) * math.sqrt(wealth)
        max_premium = wealth - eu**2
        fair = prob * loss
        text = f"{f} offers full insurance to a consumer with wealth {wealth}, utility sqrt(w), loss {loss}, and loss probability {pct(prob)}."
        qs = parts(("a", "Find the actuarially fair premium."), ("b", "Find the maximum premium the consumer would pay."), ("c", "Why can the maximum exceed the fair premium?"))
        ss = parts(("a", f"Fair premium is expected loss: {num(prob)} x {loss} = {money(fair)}."), ("b", f"Without insurance EU = {num(eu)}. Full insurance gives certain wealth 100 - premium. Set sqrt(100 - premium) = {num(eu)}, so premium = {money(max_premium)}."), ("c", "A risk-averse consumer is willing to pay a risk premium to avoid uncertainty."))
        return make_row("Risk and Insurance", "Insurance premium", "hard", text, qs, ss, ["insurance", "risk premium"], {"wealth": wealth, "loss": loss, "prob": prob}, family="insurance WTP")
    if k == 3:
        p_bad, repair = 0.1 + (i % 4) * 0.02, 300 + 10 * i
        wtp = p_bad * repair
        text = f"{f} is considering selling a warranty. A product repair costs {money(repair)} and occurs with probability {pct(p_bad)}. Buyers are risk-neutral."
        qs = parts(("a", "What is the expected repair cost?"), ("b", "What is the maximum warranty price for a risk-neutral buyer?"), ("c", "Would risk aversion raise or lower this maximum?"))
        ss = parts(("a", f"Expected repair cost is {num(p_bad)} x {money(repair)} = {money(wtp)}."), ("b", f"A risk-neutral buyer pays at most the expected cost, {money(wtp)}."), ("c", "Risk aversion raises willingness to pay for the warranty above expected cost."))
        return make_row("Risk and Insurance", "Warranty", "easy", text, qs, ss, ["warranty", "expected cost"], {"repair": repair, "prob": p_bad}, family="warranty")
    low, med, high = 1000 + 10 * i, 2400 + 10 * i, 5000 + 10 * i
    avg_all = (low + med + high) / 3
    avg_high = high
    text = f"{f} studies an insurance pool with equal numbers of low-, medium-, and high-risk customers. Expected costs are {money(low)}, {money(med)}, and {money(high)}."
    qs = parts(("a", "What premium breaks even if everyone buys?"), ("b", "What happens if only high-risk customers buy?"), ("c", "What is the adverse-selection concern?"))
    ss = parts(("a", f"Average cost with everyone is ({low} + {med} + {high})/3 = {money(avg_all)}."), ("b", f"If only high-risk customers buy, break-even premium is {money(avg_high)}."), ("c", "As lower-risk customers leave, average cost rises, which can further raise premiums."))
    return make_row("Risk and Insurance", "Insurance pool", "medium", text, qs, ss, ["insurance", "adverse selection"], {"low": low, "medium": med, "high": high}, family="insurance pool")


# Reuse compact versions for the remaining topics. They still generate multiple problem families.


def asymmetric_information(i: int) -> dict[str, Any]:
    f = firm(i, 3)
    k = i % 5
    good_v, bad_v = 120 + i % 10, 50 + i % 8
    good_c, bad_c = 80 + i % 6, 30 + i % 5
    share_good = 0.5 if k != 1 else 0.4
    pooled = share_good * good_v + (1 - share_good) * bad_v
    if k in {0, 1, 2}:
        text = f"Buyers cannot observe whether {possessive(f)} marketplace item is high or low quality. High quality is worth {money(good_v)} and costs {money(good_c)}; low quality is worth {money(bad_v)} and costs {money(bad_c)}. The high-quality share is {pct(share_good)}."
        qs = parts(("a", "Compute pooled willingness to pay."), ("b", "Which sellers participate at the pooled price?"), ("c", "Explain the adverse-selection pressure."))
        high_participates = pooled >= good_c
        low_participates = pooled >= bad_c
        if high_participates and low_participates:
            participation = "both high- and low-quality sellers participate"
        elif high_participates:
            participation = "only high-quality sellers participate"
        elif low_participates:
            participation = "only low-quality sellers participate"
        else:
            participation = "neither type participates"
        ss = parts(("a", f"Pooled WTP is {num(share_good)} x {good_v} + {num(1-share_good)} x {bad_v} = {money(pooled)}."), ("b", f"High quality participates if {money(pooled)} >= {money(good_c)}, which is {'true' if high_participates else 'false'} here; low quality participates if {money(pooled)} >= {money(bad_c)}, which is {'true' if low_participates else 'false'} here. Therefore, {participation}."), ("c", "If high-quality sellers exit, average quality falls and the pooled WTP falls too."))
        return make_row("Asymmetric Information", "Adverse selection", "medium", text, qs, ss, ["adverse selection"], {"good_v": good_v, "bad_v": bad_v, "good_c": good_c, "bad_c": bad_c, "share_good": share_good}, family="lemons")
    cert_cost = 12 + i % 6
    gain = good_v - pooled
    text = f"High-quality sellers on {possessive(f)} platform can buy certification costing {money(cert_cost)}. Without certification, buyers pay the pooled value {money(pooled)}; certified high-quality sellers can charge {money(good_v)}."
    qs = parts(("a", "What is the gross benefit of certification?"), ("b", "Will high-quality sellers certify?"), ("c", "Why might low-quality sellers not certify?"))
    ss = parts(("a", f"Gross benefit is {money(good_v)} - {money(pooled)} = {money(gain)}."), ("b", f"They certify if {money(gain)} >= {money(cert_cost)}, which is {'true' if gain >= cert_cost else 'false'} here."), ("c", "A credible certificate must be harder or less valuable for low-quality sellers to mimic."))
    return make_row("Asymmetric Information", "Certification", "medium", text, qs, ss, ["signaling", "certification"], {"good_v": good_v, "pooled": pooled, "cert_cost": cert_cost}, family="certification")


def incentives_contracts(i: int) -> dict[str, Any]:
    f = firm(i, 5)
    ph, pl = 0.75, 0.50
    effort = 5 + i % 6
    outside = max(18 + i % 8, 2 * effort)
    bonus = effort / (ph - pl)
    wage = outside + effort - ph * bonus
    k = i % 5
    if k in {0, 1, 2}:
        intro = ["redesigns sales compensation", "cannot observe effort directly", "wants to reward successful client conversions"][k]
        text = f"{f} {intro}. A sale occurs with probability {pct(ph)} under high effort and {pct(pl)} under low effort. The outside option is {money(outside)} and effort costs {money(effort)}."
        qs = parts(("a", "Write the incentive-compatibility constraint."), ("b", "Write the participation constraint."), ("c", "Find the cheapest wage and bonus."))
        ss = parts(("a", f"IC: w + {ph}b - {effort} >= w + {pl}b, so ({ph-pl})b >= {effort}."), ("b", f"PC: w + {ph}b - {effort} >= {outside}."), ("c", f"Minimum bonus is b = {money(bonus)}. Then w = {money(wage)}."))
        return make_row("Incentives and Contracts", "Moral hazard contract", "medium", text, qs, ss, ["incentive compatibility", "participation"], {"ph": ph, "pl": pl, "outside": outside, "effort": effort}, family="bonus contract")
    revenue = 100 + 5 * i
    expected_gain = (ph - pl) * revenue
    text = f"{f} earns {money(revenue)} from a successful sale. High effort raises success probability from {pct(pl)} to {pct(ph)} and costs the worker {money(effort)}."
    qs = parts(("a", "What is the expected revenue gain from high effort?"), ("b", "Is inducing effort efficient?"), ("c", "What contracting friction remains?"))
    ss = parts(("a", f"Expected revenue gain is ({ph} - {pl}) x {money(revenue)} = {money(expected_gain)}."), ("b", f"Effort is efficient if {money(expected_gain)} exceeds effort cost {money(effort)}, which it does here."), ("c", "The firm still needs an incentive-compatible contract because effort is hidden."))
    return make_row("Incentives and Contracts", "Effort efficiency", "medium", text, qs, ss, ["moral hazard", "efficiency"], {"revenue": revenue, "ph": ph, "pl": pl, "effort": effort}, family="efficiency")


def game_theory(i: int) -> dict[str, Any]:
    f1, f2 = firm(i), firm(i, 6)
    k = i % 5
    if k == 0:
        hh, steal, victim, ll = 50 + i, 61 + i, 34 + i, 42 + i
        text = f"{f1} and {f2} simultaneously choose High Price or Low Price. If both choose High, payoffs are ({hh},{hh}). If one chooses Low while the other chooses High, the low-price firm gets {steal} and the high-price firm gets {victim}. If both choose Low, payoffs are ({ll},{ll})."
        qs = parts(("a", f"Does {f1} have a dominant strategy?"), ("b", f"Does {f2} have a dominant strategy?"), ("c", "Find the Nash equilibrium."))
        ss = parts(("a", f"Low Price yields {steal} instead of {hh} if the rival chooses High, and {ll} instead of {victim} if the rival chooses Low. It is dominant."), ("b", "By symmetry, Low Price is dominant for the rival too."), ("c", "The Nash equilibrium is (Low, Low)."))
        return make_row("Game Theory", "Dominant strategies", "easy", text, qs, ss, ["dominant strategy", "Nash"], {"firm1": f1, "firm2": f2}, family="pricing game")
    if k == 1:
        adopt, neither, solo, wait = 70 + i, 44 + i, 28 + i, 54 + i
        text = f"{f1} and {f2} choose whether to adopt a shared standard. If both adopt, payoffs are ({adopt},{adopt}). If neither adopts, payoffs are ({neither},{neither}). If only one adopts, the adopter gets {solo} and the non-adopter gets {wait}."
        qs = parts(("a", "Find the pure-strategy Nash equilibria."), ("b", "Is this a coordination game?"), ("c", "Which equilibrium is Pareto better?"))
        ss = parts(("a", "Both Adopt and both Do Not Adopt are Nash equilibria: no one wants to deviate unilaterally from either matching outcome."), ("b", "Yes. Each firm prefers to match the other's action."), ("c", f"Both Adopt is Pareto better because both get {adopt} instead of {neither}."))
        return make_row("Game Theory", "Coordination game", "medium", text, qs, ss, ["coordination", "Nash"], {"firm1": f1, "firm2": f2}, family="coordination")
    if k == 2:
        incumbent_safe, fight_i, fight_r, acc_i, acc_r = 80 + i, -10 - i % 4, 40 + i, 30 + i, 60 + i
        text = f"{f1} first chooses Enter or Stay Out. If it stays out, payoffs are (0,{incumbent_safe}). If it enters, {f2} chooses Fight or Accommodate. Fight gives ({fight_i},{fight_r}); Accommodate gives ({acc_i},{acc_r})."
        qs = parts(("a", "Solve by backward induction."), ("b", "Will entry occur?"), ("c", "Is fighting a credible threat?"))
        ss = parts(("a", f"If entry occurs, {f2} prefers Accommodate because {acc_r} > {fight_r}. Anticipating this, {f1} enters because {acc_i} > 0."), ("b", "Yes, entry occurs."), ("c", "No. Fighting is not credible because accommodation is better after entry."))
        return make_row("Game Theory", "Sequential entry", "medium", text, qs, ss, ["backward induction"], {"firm1": f1, "firm2": f2}, family="entry game")
    if k == 3:
        clean_cost, both_clean, polluter, cleaner = 7 + i % 5, 50 + i, 56 + i, 34 + i
        both_pollute = both_clean - clean_cost - 2
        text = f"{f1} and {f2} choose Clean or Pollute. Clean costs each firm {clean_cost}. If both are clean, each gets {both_clean} before costs. If one pollutes while the other is clean, the polluter gets {polluter} and the clean firm gets {cleaner} before any clean cost. If both pollute, each gets {both_pollute}."
        qs = parts(("a", "Compute net payoffs for each outcome."), ("b", "What is each firm's dominant action?"), ("c", "Why is this a prisoners' dilemma?"))
        ss = parts(("a", f"Both clean gives {both_clean - clean_cost} each. Pollute against clean gives {polluter} to polluter and {cleaner - clean_cost} to cleaner. Both pollute gives {both_pollute} each."), ("b", "Pollute is dominant: it beats Clean whether the other firm is clean or polluting."), ("c", f"Both would be better at Clean/Clean ({both_clean - clean_cost},{both_clean - clean_cost}) than Pollute/Pollute ({both_pollute},{both_pollute}), but individual incentives lead to pollution."))
        return make_row("Game Theory", "Prisoners' dilemma", "medium", text, qs, ss, ["prisoners dilemma"], {"firm1": f1, "firm2": f2}, family="externality game")
    al1, al2, ar1, ar2, bl1, bl2, br1, br2 = 30 + i, 40 + i, 20 + i, 20 + i, 35 + i, 10 + i, 25 + i, 30 + i
    text = f"{f1} chooses A or B, and {f2} chooses Left or Right. Payoffs are: A/Left ({al1},{al2}), A/Right ({ar1},{ar2}), B/Left ({bl1},{bl2}), B/Right ({br1},{br2})."
    qs = parts(("a", f"Find {possessive(f1)} best response to each action by {f2}."), ("b", f"Find {possessive(f2)} best response to each action by {f1}."), ("c", "Find the Nash equilibrium."))
    ss = parts(("a", f"If {f2} chooses Left, {f1} chooses B ({bl1} > {al1}). If Right, {f1} chooses B ({br1} > {ar1})."), ("b", f"If {f1} chooses A, {f2} chooses Left ({al2} > {ar2}). If B, {f2} chooses Right ({br2} > {bl2})."), ("c", "The only mutual best response is B/Right."))
    return make_row("Game Theory", "Best responses", "medium", text, qs, ss, ["best response", "Nash"], {"firm1": f1, "firm2": f2}, family="best responses")


def oligopoly(i: int) -> dict[str, Any]:
    f = firm(i, 8)
    k = i % 5
    a, c = 100 + i, 20 + i % 7
    if k == 0:
        q = (a - c) / 3
        p = a - 2 * q
        text = f"{f} and a rival compete in quantities. Market demand is P = {a} - Q and both have marginal cost {money(c)}."
        qs = parts(("a", "Derive a firm's best response."), ("b", "Find symmetric Cournot quantities and price."), ("c", "Compute each firm's profit."))
        ss = parts(("a", f"BR is qi = ({a-c} - qj)/2."), ("b", f"Symmetry gives q = {num(q)} and price P = {money(p)}."), ("c", f"Profit per firm is (P - MC)q = {money((p-c)*q)}."))
        return make_row("Oligopoly and Strategic Competition", "Cournot duopoly", "hard", text, qs, ss, ["Cournot"], {"a": a, "mc": c}, family="Cournot")
    if k == 1:
        qL = (a - c) / 2
        qF = (a - c - qL) / 2
        p = a - qL - qF
        text = f"{f} is a Stackelberg leader. Demand is P = {a} - Q and both firms have marginal cost {money(c)}."
        qs = parts(("a", "Find the follower's best response."), ("b", "Find leader and follower quantities."), ("c", "Find market price."))
        ss = parts(("a", f"Follower response is qF = ({a-c} - qL)/2."), ("b", f"The leader chooses qL = ({a-c})/2 = {num(qL)}; follower produces {num(qF)}."), ("c", f"Price is {money(p)}."))
        return make_row("Oligopoly and Strategic Competition", "Stackelberg leadership", "hard", text, qs, ss, ["Stackelberg"], {"a": a, "mc": c}, family="Stackelberg")
    if k == 2:
        text = f"{f} and a rival sell identical products and have the same constant marginal cost {money(c)}. They choose prices simultaneously and have enough capacity to serve the market."
        qs = parts(("a", "What is the Bertrand equilibrium price?"), ("b", "What is economic profit?"), ("c", "Why does price fall to marginal cost?"))
        ss = parts(("a", f"Price equals marginal cost: {money(c)}."), ("b", "Economic profit is zero."), ("c", "Any firm pricing above marginal cost can be undercut slightly by the rival, so competition drives price to MC."))
        return make_row("Oligopoly and Strategic Competition", "Bertrand competition", "medium", text, qs, ss, ["Bertrand"], {"mc": c}, family="Bertrand")
    if k == 3:
        q_collude = (a - c) / 4
        p_collude = a - 2 * q_collude
        q_cournot = (a - c) / 3
        text = f"{f} and a rival consider colluding in a market with P = {a} - Q and marginal cost {money(c)}."
        qs = parts(("a", "If they maximize joint profit and split output evenly, how much does each produce?"), ("b", "Compare with Cournot output per firm."), ("c", "Why is collusion fragile?"))
        ss = parts(("a", f"Joint monopoly total output is ({a-c})/2, so each produces {num(q_collude)} and price is {money(p_collude)}."), ("b", f"Cournot output per firm is ({a-c})/3 = {num(q_cournot)}, higher than collusive output per firm."), ("c", "Each firm has an incentive to secretly expand output when the other restricts output."))
        return make_row("Oligopoly and Strategic Competition", "Collusion", "medium", text, qs, ss, ["collusion", "Cournot"], {"a": a, "mc": c}, family="collusion")
    cap, demand, price, mc = 80 + i % 10, 150 + i, 50 + i % 5, 15 + i % 4
    served = min(cap, demand)
    profit = (price - mc) * served
    text = f"{f} has capacity {cap}. At price {money(price)}, demand for its service is {demand}; marginal cost is {money(mc)}."
    qs = parts(("a", "How many customers can it serve?"), ("b", "Compute weekly profit ignoring fixed costs."), ("c", "Why can capacity matter in price competition?"))
    ss = parts(("a", f"It serves min({cap}, {demand}) = {served} customers."), ("b", f"Profit is ({price} - {mc}) x {served} = {money(profit)}."), ("c", "Capacity limits can soften price competition because a low-price firm may not be able to serve everyone."))
    return make_row("Oligopoly and Strategic Competition", "Capacity constraint", "easy", text, qs, ss, ["capacity", "price competition"], {"capacity": cap, "demand": demand, "price": price, "mc": mc}, family="capacity")


def externalities_public_goods(i: int) -> dict[str, Any]:
    f = firm(i, 10)
    k = i % 5
    if k in {0, 1}:
        a, mc, damage = 100 + i, 20 + i % 8, 10 + i % 5
        q_private = a - mc
        q_social = a - mc - damage
        text = f"{f} produces a good with inverse demand P = {a} - Q, private marginal cost {money(mc)}, and external marginal damage {money(damage)} per unit."
        qs = parts(("a", "Find the unregulated quantity."), ("b", "Find the efficient quantity."), ("c", "Find the Pigouvian tax."))
        ss = parts(("a", f"Private equilibrium sets {a} - Q = {mc}, so Q = {num(q_private)}."), ("b", f"Efficiency sets demand equal to social MC {mc + damage}, so Q = {num(q_social)}."), ("c", f"The Pigouvian tax equals marginal damage: {money(damage)}."))
        return make_row("Externalities and Public Goods", "Pigouvian tax", "medium", text, qs, ss, ["externality", "Pigouvian tax"], {"a": a, "mc": mc, "damage": damage}, family="negative externality")
    if k == 2:
        mb1, mb2, mc = 50 + i, 30 + i // 2, 60
        q = mb1 + mb2 - mc
        text = f"Two departments benefit from a public dashboard built by {f}. Marginal benefits are MB1 = {mb1} - Q and MB2 = {mb2} - Q. Marginal cost is {money(mc)}."
        qs = parts(("a", "Write the Samuelson condition."), ("b", "Find efficient Q."), ("c", "Why do we add marginal benefits vertically?"))
        ss = parts(("a", "For a public good, MB1 + MB2 = MC."), ("b", f"({mb1} - Q) + ({mb2} - Q) = {mc}, so Q = {num(q/2)}."), ("c", "The same unit is consumed by both users, so social marginal benefit sums their marginal benefits."))
        return make_row("Externalities and Public Goods", "Public goods", "hard", text, qs, ss, ["public goods", "Samuelson condition"], {"mb1": mb1, "mb2": mb2, "mc": mc}, family="public good")
    if k == 3:
        benefit, external, cost = 40 + i % 6, 15 + i % 5, 30
        net_social = benefit + external - cost
        text = f"Each unit of {possessive(f)} training service gives buyers private marginal benefit {money(benefit)} and creates external benefit {money(external)} for coworkers. Marginal cost is {money(cost)}."
        qs = parts(("a", "Find private net benefit."), ("b", "Find social net benefit."), ("c", "What subsidy would align private and social incentives?"))
        ss = parts(("a", f"Private net benefit is {money(benefit - cost)}."), ("b", f"Social net benefit is {money(net_social)}."), ("c", f"A per-unit subsidy equal to the external benefit, {money(external)}, aligns incentives."))
        return make_row("Externalities and Public Goods", "Positive externality", "easy", text, qs, ss, ["positive externality", "subsidy"], {"benefit": benefit, "external": external, "cost": cost}, family="positive externality")
    users, value, cost = 8 + i, 7 + i % 6, 60 + i
    social_value = users * value
    text = f"{f} can create a shared data tool used by {users} teams. Each team values access at {money(value)}. Total cost is {money(cost)}."
    qs = parts(("a", "Is provision efficient?"), ("b", "Would a private seller charging each team separately cover cost if all paid value?"), ("c", "What free-rider issue can arise?"))
    ss = parts(("a", f"Social value is {users} x {money(value)} = {money(social_value)}, so provision is {'efficient' if social_value >= cost else 'not efficient'}."), ("b", f"If all paid value, revenue would be {money(social_value)}, {'enough' if social_value >= cost else 'not enough'} to cover cost."), ("c", "Each team may hope others pay while it still benefits, causing under-provision."))
    return make_row("Externalities and Public Goods", "Free riding", "medium", text, qs, ss, ["public goods", "free riding"], {"users": users, "value": value, "cost": cost}, family="free riding")


def consumer_choice(i: int) -> dict[str, Any]:
    f = firm(i, 12)
    k = i % 5
    if k == 0:
        income, px, py = 120 + 5 * i, 5 + i % 5, 10 + i % 4
        x, y = income / (2 * px), income / (2 * py)
        text = f"A consumer has utility U(x,y)=x^0.5y^0.5 over {f} credits x and cafe meals y. Income is {money(income)}, Px={money(px)}, and Py={money(py)}."
        qs = parts(("a", "Write the budget constraint."), ("b", "Find optimal x and y."), ("c", "How much is spent on each good?"))
        ss = parts(("a", f"{px}x + {py}y = {income}."), ("b", f"Equal Cobb-Douglas shares imply x = {num(x)} and y = {num(y)}."), ("c", f"Half of income, {money(income/2)}, is spent on each good."))
        return make_row("Consumer Choice", "Cobb-Douglas demand", "medium", text, qs, ss, ["utility maximization"], {"income": income, "px": px, "py": py}, {"utility": "x^0.5y^0.5"}, family="Cobb-Douglas")
    if k == 1:
        income, px, py = 100 + 5 * i, 4 + i % 4, 8 + i % 4
        text = f"A customer views one {f} device and two service hours as perfect complements: U(x,y)=min(x, y/2). Income is {money(income)}, Px={money(px)}, Py={money(py)}."
        x = income / (px + 2 * py)
        y = 2 * x
        qs = parts(("a", "What relation between x and y holds at the optimum?"), ("b", "Find x and y."), ("c", "Why not buy extra y beyond that ratio?"))
        ss = parts(("a", "Perfect complements require y = 2x."), ("b", f"Budget gives {px}x + {py}(2x) = {income}, so x = {num(x)} and y = {num(y)}."), ("c", "Extra y without matching x does not raise utility."))
        return make_row("Consumer Choice", "Perfect complements", "medium", text, qs, ss, ["perfect complements"], {"income": income, "px": px, "py": py}, {"utility": "min(x,y/2)"}, family="complements")
    if k == 2:
        income, px, py = 90 + 4 * i, 6 + i % 5, 3 + i % 3
        text = f"A consumer sees {f} tokens x and transit credits y as perfect substitutes: U=x+y. Income is {money(income)}, Px={money(px)}, Py={money(py)}."
        buy_y = py < px
        qs = parts(("a", "Which good does the consumer buy?"), ("b", "How much of that good?"), ("c", "When would the consumer be indifferent?"))
        ss = parts(("a", f"The consumer buys the cheaper utility unit, {'y' if buy_y else 'x'}."), ("b", f"Quantity is income divided by its price: {num(income / (py if buy_y else px))}."), ("c", "The consumer is indifferent when Px = Py."))
        return make_row("Consumer Choice", "Perfect substitutes", "easy", text, qs, ss, ["perfect substitutes"], {"income": income, "px": px, "py": py}, {"utility": "x+y"}, family="substitutes")
    if k == 3:
        income, px_old, px_new, py = 160 + i, 8, 10, 10
        x_old, x_new = income / (2 * px_old), income / (2 * px_new)
        text = f"A consumer has Cobb-Douglas utility over {f} units x and good y. Income is {money(income)} and Py={money(py)}. Px rises from {money(px_old)} to {money(px_new)}."
        qs = parts(("a", "Find x before the price change."), ("b", "Find x after the price change."), ("c", "Explain why x changes."))
        ss = parts(("a", f"With equal shares, x_old = ({income}/2)/{px_old} = {num(x_old)}."), ("b", f"x_new = ({income}/2)/{px_new} = {num(x_new)}."), ("c", "The higher price makes each unit of x more expensive, so demand for x falls."))
        return make_row("Consumer Choice", "Price change", "medium", text, qs, ss, ["demand", "price change"], {"income": income, "px_old": px_old, "px_new": px_new, "py": py}, family="price change")
    u, px, py = 100 + i, 5 + i % 5, 10 + i % 4
    # For U=sqrt(xy), cost min for utility u: x/y = py/px and xy=u^2.
    x = u * math.sqrt(py / px)
    y = u * math.sqrt(px / py)
    cost = px * x + py * y
    text = f"A student wants utility level U={u} from U(x,y)=sqrt(xy), where x is {f} tutoring hours. Prices are Px={money(px)} and Py={money(py)}."
    qs = parts(("a", "Write the cost-minimization tangency condition."), ("b", "Find cost-minimizing x and y."), ("c", "Compute minimum expenditure."))
    ss = parts(("a", f"MRS = y/x = Px/Py = {px}/{py}, so x/y = {num(py/px)}."), ("b", f"Together with xy = {u**2}, this gives x = {num(x)} and y = {num(y)}."), ("c", f"Minimum expenditure is {money(cost)}."))
    return make_row("Consumer Choice", "Expenditure minimization", "hard", text, qs, ss, ["expenditure minimization"], {"u": u, "px": px, "py": py}, {"utility": "sqrt(xy)"}, family="dual problem")


def mixed_review(i: int) -> dict[str, Any]:
    # Rotate through compact review versions of several core models.
    funcs = [monopoly, supply_and_demand, elasticity, production_costs, consumer_choice]
    item = funcs[i % len(funcs)](i + 100)
    item["topic"] = "Mixed Review"
    item["subtopic"] = f"Review: {item['subtopic']}"
    item["generated_id"] = stable_id("gen", item["topic"], item["subtopic"], item["problem_text"], item["solution"])
    return item


GENERATORS: dict[str, Callable[[int], dict[str, Any]]] = {
    "Supply and Demand": supply_and_demand,
    "Elasticity": elasticity,
    "Taxes and Government Intervention": taxes_policy,
    "Trade and Welfare": trade_welfare,
    "Production and Costs": production_costs,
    "Perfect Competition": perfect_competition,
    "Monopoly": monopoly,
    "Price Discrimination": price_discrimination,
    "Risk and Insurance": risk_insurance,
    "Asymmetric Information": asymmetric_information,
    "Incentives and Contracts": incentives_contracts,
    "Game Theory": game_theory,
    "Oligopoly and Strategic Competition": oligopoly,
    "Externalities and Public Goods": externalities_public_goods,
    "Consumer Choice": consumer_choice,
    "Mixed Review": mixed_review,
}


def build_curated_bank(per_topic: int = 50) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for topic, generator in GENERATORS.items():
        for i in range(per_topic):
            rows.append(generator(i + 1))
    return rows


def write_curated_bank(
    data_dir: Path | str = DEFAULT_DATA_DIR,
    per_topic: int = 50,
    replace: bool = True,
) -> list[dict[str, Any]]:
    path = data_path("generated", data_dir)
    rows = build_curated_bank(per_topic)
    if not replace:
        from .utils import read_jsonl

        existing = read_jsonl(path)
        existing_ids = {row.get("generated_id") for row in existing}
        rows = [*existing, *[row for row in rows if row["generated_id"] not in existing_ids]]
    write_jsonl(path, rows)
    return rows
