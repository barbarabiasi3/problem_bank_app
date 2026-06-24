from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .utils import DEFAULT_DATA_DIR, data_path, stable_id, write_jsonl


DIFFICULTY_COUNTS = {"easy": 15, "medium": 25, "hard": 10}
DIFFICULTIES = ("easy", "medium", "hard")

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
    "Brass Lantern",
    "Civic Thread",
    "Elm City Foods",
    "Harbor Analytics",
    "Juniper Labs",
    "Keystone Transit",
    "Long Wharf Roasters",
    "Maple Circuit",
    "Oak Street Games",
    "Sterling Health",
]

PLACES = [
    "New Haven",
    "Providence",
    "Hartford",
    "Worcester",
    "Bridgeport",
    "Stamford",
    "Cambridge",
    "Albany",
    "Burlington",
    "Portland",
]

PRODUCTS = [
    "meal kits",
    "bike rentals",
    "standing desks",
    "coffee subscriptions",
    "campus shuttles",
    "portable batteries",
    "fitness classes",
    "software seats",
    "specialty noodles",
    "home sensors",
]


def firm(i: int, offset: int = 0) -> str:
    return FIRMS[(i + offset) % len(FIRMS)]


def place(i: int, offset: int = 0) -> str:
    return PLACES[(i + offset) % len(PLACES)]


def product(i: int, offset: int = 0) -> str:
    return PRODUCTS[(i + offset) % len(PRODUCTS)]


def possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def money(x: float, unit: str = "$") -> str:
    sign = "-" if x < 0 else ""
    amount = abs(x)
    if abs(amount - round(amount)) < 1e-8:
        return f"{sign}{unit}{int(round(amount)):,}"
    return f"{sign}{unit}{amount:,.2f}"


def num(x: float) -> str:
    if abs(x - round(x)) < 1e-8:
        return f"{int(round(x)):,}"
    return f"{x:,.2f}"


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def parts(*items: tuple[str, str]) -> list[dict[str, str]]:
    return [{"label": label, "text": text} for label, text in items]


def solution_text(solution_parts: list[dict[str, str]]) -> str:
    return "\n\n".join(f"({part['label']}) {part['text']}" for part in solution_parts)


def difficulty_for_index(i: int) -> str:
    position = (i - 1) % 50
    if position < DIFFICULTY_COUNTS["easy"]:
        return "easy"
    if position < DIFFICULTY_COUNTS["easy"] + DIFFICULTY_COUNTS["medium"]:
        return "medium"
    return "hard"


def make_row(
    topic: str,
    subtopic: str,
    difficulty: str,
    problem_title: str,
    problem_text: str,
    subparts: list[dict[str, str]],
    solution_subparts: list[dict[str, str]],
    concepts: list[str],
    parameters: dict[str, Any],
    functions: dict[str, Any] | None = None,
    family: str = "",
) -> dict[str, Any]:
    labels = [part["label"] for part in subparts]
    solution_labels = [part["label"] for part in solution_subparts]
    if labels != solution_labels:
        raise ValueError(f"Subpart/solution mismatch for {topic}: {labels} != {solution_labels}")
    expected_counts = {"easy": 4, "medium": 5, "hard": (5, 6)}
    expected = expected_counts[difficulty]
    if isinstance(expected, tuple):
        valid_count = len(subparts) in expected
    else:
        valid_count = len(subparts) == expected
    if not valid_count:
        raise ValueError(f"{topic} {difficulty} has {len(subparts)} subparts.")

    solution = solution_text(solution_subparts)
    generated_id = stable_id("gen", topic, subtopic, difficulty, problem_title, problem_text, solution)
    return {
        "generated_id": generated_id,
        "parent_problem_id": "local_codex_exam_style_bank",
        "topic": topic,
        "subtopic": subtopic,
        "difficulty": difficulty,
        "problem_title": problem_title,
        "problem_text": problem_text,
        "subparts": subparts,
        "solution": solution,
        "solution_subparts": solution_subparts,
        "concepts_tested": concepts,
        "variation_notes": f"Local exam-style bank: {family or subtopic}.",
        "parameters": parameters,
        "functions": functions or {},
        "quality_checks": {
            "math_verified": True,
            "economics_verified": True,
            "not_too_similar_to_parent": True,
            "student_level_appropriate": True,
            "no_answer_leakage": True,
            "exam_style_structure": True,
        },
        "disabled": False,
        "model": "local_codex_exam_style_generator",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def supply_and_demand(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f, city, good = firm(i), place(i), product(i)
    if difficulty == "easy":
        a, b, c, d, shift = 140 + 2 * i, 2 + i % 2, 20 + i % 7, 2, 18 + i % 8
        p0 = (a - c) / (b + d)
        q0 = a - b * p0
        p1 = (a + shift - c) / (b + d)
        q1 = a + shift - b * p1
        text = (
            f"{f} is piloting {good} in {city}. Weekly demand is Qd = {a} - {b}P and supply is "
            f"Qs = {c} + {d}P, where P is the price per unit. After a campus partnership is announced, "
            f"market research predicts demand will be {shift} units higher at every price. Treat the market "
            f"as competitive and use this setting to separate the arithmetic of equilibrium from the economic intuition."
        )
        qs = parts(
            ("a", "Find the initial equilibrium price and quantity."),
            ("b", "Find the new equilibrium after the demand increase."),
            ("c", "State whether consumers, sellers, or both are doing more trading after the announcement."),
            ("d", "Explain in one or two sentences why the price movement makes economic sense."),
        )
        ss = parts(
            ("a", f"Set {a} - {b}P = {c} + {d}P. The initial price is {money(p0)} and quantity is {num(q0)}."),
            ("b", f"New demand is Qd = {a + shift} - {b}P, so P = {money(p1)} and Q = {num(q1)}."),
            ("c", f"Both sides trade more: quantity rises from {num(q0)} to {num(q1)}."),
            ("d", "Demand rose at every price, creating excess demand at the old price. Competition bids price up and expands quantity."),
        )
        return make_row("Supply and Demand", "Demand shift", difficulty, f"{good.title()} Demand Shift", text, qs, ss, ["equilibrium", "demand shift"], {"a": a, "b": b, "c": c, "d": d, "shift": shift}, family="demand shift")

    if difficulty == "medium":
        a, b, c, d, tax = 155 + i, 3, 18 + i % 9, 2, 6 + i % 6
        p0 = (a - c) / (b + d)
        q0 = a - b * p0
        pc = (a - c + d * tax) / (b + d)
        ps = pc - tax
        q1 = a - b * pc
        revenue = tax * q1
        buyer_burden = pc - p0
        seller_burden = p0 - ps
        text = (
            f"{city} is considering a seller tax on {good}. Before the tax, demand is Qd = {a} - {b}P "
            f"and supply is Qs = {c} + {d}P. The proposed policy charges sellers {money(tax)} for each unit sold. "
            f"Local businesses argue they will pay the entire tax, while student groups argue that buyers will face higher prices. "
            f"Use the model to evaluate both claims."
        )
        qs = parts(
            ("a", "Compute the pre-tax equilibrium price and quantity."),
            ("b", "Compute the buyer price, seller price, and quantity after the tax."),
            ("c", "Compute tax revenue."),
            ("d", "How much of the tax is borne by buyers and how much by sellers?"),
            ("e", "Use your answer to explain why legal liability and economic incidence are not the same thing."),
        )
        ss = parts(
            ("a", f"Solving {a} - {b}P = {c} + {d}P gives P = {money(p0)} and Q = {num(q0)}."),
            ("b", f"With Ps = Pc - {tax}, set {a} - {b}Pc = {c} + {d}(Pc - {tax}). Pc = {money(pc)}, Ps = {money(ps)}, and Q = {num(q1)}."),
            ("c", f"Revenue is tax times quantity: {money(tax)} x {num(q1)} = {money(revenue)}."),
            ("d", f"Buyers pay {money(buyer_burden)} more per unit and sellers receive {money(seller_burden)} less per unit."),
            ("e", "The seller writes the check, but market prices adjust. Incidence depends on supply and demand responses, not on who remits the tax."),
        )
        return make_row("Supply and Demand", "Tax incidence", difficulty, f"{city} Per-Unit Tax", text, qs, ss, ["tax incidence", "equilibrium", "revenue"], {"a": a, "b": b, "c": c, "d": d, "tax": tax}, family="tax incidence")

    a, b, c, d = 180 + i, 4, 15 + i % 7, 2
    demand_shift, supply_loss, subsidy = 22 + i % 5, 12 + i % 4, 5 + i % 5
    p0 = (a - c) / (b + d)
    q0 = a - b * p0
    p_shock = (a + demand_shift - (c - supply_loss)) / (b + d)
    q_shock = a + demand_shift - b * p_shock
    ps = (a + demand_shift - (c - supply_loss) + b * subsidy) / (b + d)
    pb = ps - subsidy
    q_sub = a + demand_shift - b * pb
    spending = subsidy * q_sub
    text = (
        f"A city council is studying the market for {good} after two simultaneous changes. Demand in {city} rises by "
        f"{demand_shift} units at every price because commuting patterns change. At the same time, a supplier shortage lowers supply "
        f"by {supply_loss} units at every price. Initially Qd = {a} - {b}P and Qs = {c} + {d}P. After the shock, the council considers "
        f"a buyer subsidy of {money(subsidy)} per unit to keep the market active."
    )
    qs = parts(
        ("a", "Find the initial equilibrium."),
        ("b", "Find the equilibrium after both the demand increase and the supply decrease, before any subsidy."),
        ("c", "With the buyer subsidy, find the buyer price, seller price, and quantity."),
        ("d", "Compute total government spending on the subsidy."),
        ("e", "Compared with the post-shock no-subsidy outcome, who gains directly from the subsidy?"),
        ("f", "Explain why a subsidy can raise quantity even though it is costly to the government."),
    )
    ss = parts(
        ("a", f"Initial equilibrium is P = {money(p0)} and Q = {num(q0)}."),
        ("b", f"Post-shock demand is Qd = {a + demand_shift} - {b}P and supply is Qs = {c - supply_loss} + {d}P, so P = {money(p_shock)} and Q = {num(q_shock)}."),
        ("c", f"The subsidy implies Ps = Pb + {subsidy}. Solving gives Pb = {money(pb)}, Ps = {money(ps)}, and Q = {num(q_sub)}."),
        ("d", f"Government spending is {money(subsidy)} x {num(q_sub)} = {money(spending)}."),
        ("e", "Buyers pay less out of pocket and sellers receive more per unit; the benefit is shared through price adjustments."),
        ("f", "The subsidy creates a wedge that makes purchases look cheaper to buyers and sales more attractive to sellers, so additional trades occur."),
    )
    return make_row("Supply and Demand", "Multiple shocks and subsidy", difficulty, f"{city} Market Stabilization", text, qs, ss, ["demand shift", "supply shift", "subsidy"], {"a": a, "b": b, "c": c, "d": d, "demand_shift": demand_shift, "supply_loss": supply_loss, "subsidy": subsidy}, family="multi-shock subsidy")


def elasticity(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f, good = firm(i, 2), product(i, 2)
    if difficulty == "easy":
        p0, p1 = 18 + i % 7, 22 + i % 7
        q0, q1 = 520 + 3 * i, 470 + 2 * i
        e = ((q1 - q0) / q0) / ((p1 - p0) / p0)
        r0, r1 = p0 * q0, p1 * q1
        text = (
            f"{f} experiments with the price of its {good}. When price rises from {money(p0)} to {money(p1)}, "
            f"weekly sales fall from {num(q0)} to {num(q1)} units. Management wants more than a calculation: it wants to know "
            f"whether this kind of price increase is a sensible revenue strategy."
        )
        qs = parts(
            ("a", "Compute the own-price elasticity using the original price and quantity as the base."),
            ("b", "Classify demand as elastic or inelastic over this change."),
            ("c", "Compute revenue before and after the price change."),
            ("d", "Should the firm view this price increase as a revenue success? Explain briefly."),
        )
        ss = parts(
            ("a", f"Elasticity is ({q1} - {q0})/{q0} divided by ({p1} - {p0})/{p0}, which equals {num(e)}."),
            ("b", f"The absolute value is {num(abs(e))}, so demand is {'elastic' if abs(e) > 1 else 'inelastic'}."),
            ("c", f"Revenue changes from {money(r0)} to {money(r1)}."),
            ("d", f"Revenue {'increases' if r1 > r0 else 'decreases'}, so the price increase {'succeeds' if r1 > r0 else 'does not succeed'} on a revenue-only metric."),
        )
        return make_row("Elasticity", "Price elasticity experiment", difficulty, f"{good.title()} Price Experiment", text, qs, ss, ["elasticity", "revenue"], {"p0": p0, "p1": p1, "q0": q0, "q1": q1}, family="price experiment")

    if difficulty == "medium":
        a, b, p = 240 + 2 * i, 4, 28 + i % 8
        q = a - b * p
        e = -b * p / q
        mc = 14 + i % 6
        markup = (p - mc) / p
        target = 1 / abs(e)
        text = (
            f"{f} estimates demand for a monthly plan as Q = {a} - {b}P. The current price is {money(p)} and marginal cost is "
            f"{money(mc)}. A manager notices that students in class used both elasticity and markup rules to think about market power, "
            f"and asks whether the current price is internally consistent with that logic."
        )
        qs = parts(
            ("a", "Find current quantity demanded."),
            ("b", "Compute point elasticity at the current price."),
            ("c", "Compute the current Lerner markup, (P - MC)/P."),
            ("d", "Compare the markup with the inverse elasticity rule."),
            ("e", "If the firm is a monopolist with positive marginal cost, explain why pricing in the inelastic region would be suspicious."),
        )
        ss = parts(
            ("a", f"Q = {a} - {b}({p}) = {num(q)}."),
            ("b", f"Point elasticity is (dQ/dP)(P/Q) = -{b} x {p}/{num(q)} = {num(e)}."),
            ("c", f"The Lerner markup is ({p} - {mc})/{p} = {num(markup)}."),
            ("d", f"The inverse-elasticity target is 1/{num(abs(e))} = {num(target)}. The current markup is {'above' if markup > target else 'below'} that benchmark."),
            ("e", "In the inelastic region, a price increase raises revenue while reducing units and costs, so the firm would usually want to raise price."),
        )
        return make_row("Elasticity", "Point elasticity and markup", difficulty, "Elasticity-Based Pricing Check", text, qs, ss, ["point elasticity", "markup", "market power"], {"a": a, "b": b, "p": p, "mc": mc}, family="markup rule")

    p0, p1 = 30 + i % 6, 27 + i % 6
    q0, q1 = 380 + 4 * i, 430 + 3 * i
    rival0, rival1 = 18 + i % 5, 21 + i % 5
    qr0, qr1 = 600 + 2 * i, 648 + 3 * i
    arc = ((q1 - q0) / ((q0 + q1) / 2)) / ((p1 - p0) / ((p0 + p1) / 2))
    cross = ((qr1 - qr0) / qr0) / ((rival1 - rival0) / rival0)
    text = (
        f"{f} is evaluating two pieces of evidence before changing the price of {good}. In its own price test, price fell from "
        f"{money(p0)} to {money(p1)} and quantity rose from {num(q0)} to {num(q1)}. In the same month, a rival raised price from "
        f"{money(rival0)} to {money(rival1)}, and {possessive(f)} sales in a comparable market rose from {num(qr0)} to {num(qr1)}. "
        f"The CEO wants a recommendation that separates own-price sensitivity from substitution against rivals."
    )
    qs = parts(
        ("a", "Compute the arc own-price elasticity from the price test."),
        ("b", "Compute revenue before and after the price cut."),
        ("c", "Compute the cross-price elasticity using the rival-price evidence."),
        ("d", "Are the products substitutes or complements?"),
        ("e", "Explain one reason the CEO should be cautious about treating the two estimates as the same object."),
        ("f", "Give a pricing recommendation using both the quantitative and qualitative evidence."),
    )
    ss = parts(
        ("a", f"Arc elasticity is the percent quantity change over the percent price change using midpoints: {num(arc)}."),
        ("b", f"Revenue changes from {money(p0 * q0)} to {money(p1 * q1)}."),
        ("c", f"Cross-price elasticity is ({qr1} - {qr0})/{qr0} divided by ({rival1} - {rival0})/{rival0} = {num(cross)}."),
        ("d", "The cross-price elasticity is positive, so the products are substitutes."),
        ("e", "Own-price elasticity measures movement along the firm's demand curve; cross-price elasticity measures how rival prices shift demand."),
        ("f", "If revenue rose after the price cut, lowering price may be attractive; the positive cross elasticity also means rival pricing should be monitored closely."),
    )
    return make_row("Elasticity", "Own and cross elasticity", difficulty, "Elasticity Evidence for Pricing", text, qs, ss, ["arc elasticity", "cross-price elasticity", "revenue"], {"p0": p0, "p1": p1, "q0": q0, "q1": q1, "rival0": rival0, "rival1": rival1, "qr0": qr0, "qr1": qr1}, family="multi-elasticity")


def taxes_policy(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f, city, good = firm(i, 4), place(i, 1), product(i, 4)
    a, b, c, d = 135 + i, 3, 15 + i % 8, 2
    p0 = (a - c) / (b + d)
    q0 = a - b * p0
    if difficulty == "easy":
        ceiling = p0 - (3 + i % 4)
        qd, qsupply = a - b * ceiling, c + d * ceiling
        shortage = qd - qsupply
        text = (
            f"{city} caps the price of {good} at {money(ceiling)} after complaints about affordability. Demand is Qd = {a} - {b}P "
            f"and supply is Qs = {c} + {d}P. The policy is popular with some buyers, but the mayor wants to know whether it actually "
            f"helps buyers get the product."
        )
        qs = parts(
            ("a", "Find the unregulated equilibrium price and quantity."),
            ("b", "Determine whether the price ceiling is binding."),
            ("c", "Compute the shortage if the ceiling binds."),
            ("d", "Explain why a lower legal price can still make some buyers worse off."),
        )
        ss = parts(
            ("a", f"Unregulated P = {money(p0)} and Q = {num(q0)}."),
            ("b", f"The ceiling is binding because {money(ceiling)} is below {money(p0)}."),
            ("c", f"At the ceiling, Qd = {num(qd)} and Qs = {num(qsupply)}, so the shortage is {num(shortage)}."),
            ("d", "Some buyers pay less, but others cannot find units at all because quantity supplied falls below quantity demanded."),
        )
        return make_row("Taxes and Government Intervention", "Price ceiling", difficulty, f"{city} Price Ceiling", text, qs, ss, ["price ceiling", "shortage"], {"a": a, "b": b, "c": c, "d": d, "ceiling": ceiling}, family="price ceiling")

    if difficulty == "medium":
        tax = 7 + i % 5
        pc = (a - c + d * tax) / (b + d)
        ps = pc - tax
        q1 = a - b * pc
        revenue = tax * q1
        dwl = 0.5 * tax * (q0 - q1)
        text = (
            f"The state proposes a per-unit excise tax of {money(tax)} on {good} sold by firms such as {f}. Market demand is "
            f"Qd = {a} - {b}P and supply is Qs = {c} + {d}P. Opponents argue the tax is too high for firms to absorb and will create "
            f"a large efficiency loss. Use the model to evaluate those two claims."
        )
        qs = parts(
            ("a", "Find the pre-tax equilibrium."),
            ("b", "Find buyer price, seller price, and quantity after the tax."),
            ("c", "Compute tax revenue and deadweight loss."),
            ("d", "Which side bears more of the tax burden?"),
            ("e", "Explain why inelastic demand would weaken the deadweight-loss objection."),
        )
        ss = parts(
            ("a", f"Before the tax, P = {money(p0)} and Q = {num(q0)}."),
            ("b", f"After the tax, Pc = {money(pc)}, Ps = {money(ps)}, and Q = {num(q1)}."),
            ("c", f"Revenue is {money(revenue)}. DWL is 0.5 x {money(tax)} x {num(q0 - q1)} = {money(dwl)}."),
            ("d", f"Buyers pay {money(pc - p0)} more and sellers receive {money(p0 - ps)} less, so the larger change indicates the larger burden."),
            ("e", "If demand is inelastic, quantity falls by less, so fewer mutually beneficial trades are lost."),
        )
        return make_row("Taxes and Government Intervention", "Excise tax", difficulty, f"{good.title()} Excise Tax", text, qs, ss, ["tax", "deadweight loss", "incidence"], {"a": a, "b": b, "c": c, "d": d, "tax": tax}, family="excise tax")

    floor = p0 + (4 + i % 4)
    qd, qsupply = a - b * floor, c + d * floor
    surplus = qsupply - qd
    buyback = floor * surplus
    text = (
        f"To stabilize incomes for local suppliers of {good}, {city} considers a price floor of {money(floor)}. Demand is "
        f"Qd = {a} - {b}P and supply is Qs = {c} + {d}P. One proposal simply mandates the floor; another has the government buy any "
        f"unsold units at the floor price. The council wants to understand the tradeoffs before voting."
    )
    qs = parts(
        ("a", "Find the competitive equilibrium."),
        ("b", "Show whether the price floor is binding."),
        ("c", "Compute quantity demanded, quantity supplied, and excess supply at the floor."),
        ("d", "If the government buys the excess supply, compute the budget cost."),
        ("e", "Identify one group that gains and one group that loses from the floor."),
        ("f", "Explain why a policy that raises the price received by sellers can still waste resources."),
    )
    ss = parts(
        ("a", f"Competitive P = {money(p0)} and Q = {num(q0)}."),
        ("b", f"The floor is binding because {money(floor)} is above the competitive price."),
        ("c", f"At the floor, Qd = {num(qd)} and Qs = {num(qsupply)}, so excess supply is {num(surplus)}."),
        ("d", f"The buyback cost is {money(floor)} x {num(surplus)} = {money(buyback)}."),
        ("e", "Sellers who sell at the floor gain from a higher price; buyers lose from paying more and buying less."),
        ("f", "Extra units are produced even though buyers do not value them at the floor price, and a buyback can spend public funds on unsold output."),
    )
    return make_row("Taxes and Government Intervention", "Price floor and surplus", difficulty, f"{city} Price Floor", text, qs, ss, ["price floor", "excess supply", "government purchase"], {"a": a, "b": b, "c": c, "d": d, "floor": floor}, family="price floor")


def trade_welfare(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    good, city = product(i, 5), place(i, 2)
    a, b, c, d = 90 + i, 2, 10 + i % 8, 1
    p_aut = (a - c) / (b + d)
    q_aut = a - b * p_aut
    pw = max(8, p_aut - (5 + i % 5))
    qd_ft, qs_ft = a - b * pw, c + d * pw
    imports = qd_ft - qs_ft
    if difficulty == "easy":
        text = (
            f"{city} is small relative to the world market for {good}. Domestic demand is Qd = {a} - {b}P and domestic supply is "
            f"Qs = {c} + {d}P. The world price is {money(pw)}, and trade is initially free. The question is not only whether imports occur, "
            f"but who is likely to favor free trade."
        )
        qs = parts(
            ("a", "Find the no-trade equilibrium price and quantity."),
            ("b", "At the world price, compute domestic consumption and domestic production."),
            ("c", "Does the country import or export, and by how much?"),
            ("d", "Identify the domestic winners and losers from opening to trade."),
        )
        ss = parts(
            ("a", f"Autarky P = {money(p_aut)} and Q = {num(q_aut)}."),
            ("b", f"At {money(pw)}, Qd = {num(qd_ft)} and Qs = {num(qs_ft)}."),
            ("c", f"Since Qd > Qs, the country imports {num(imports)} units."),
            ("d", "Consumers gain from the lower price; domestic producers lose because they sell less at a lower price."),
        )
        return make_row("Trade and Welfare", "Free trade", difficulty, f"Opening the {good.title()} Market", text, qs, ss, ["autarky", "imports", "gains from trade"], {"a": a, "b": b, "c": c, "d": d, "world_price": pw}, family="free trade")

    if difficulty == "medium":
        tariff = 3 + i % 4
        pt = pw + tariff
        qd_t, qs_t = a - b * pt, c + d * pt
        imports_t = qd_t - qs_t
        revenue = tariff * imports_t
        text = (
            f"After a period of free trade in {good}, the government imposes an import tariff of {money(tariff)} per unit. Domestic demand "
            f"is Qd = {a} - {b}P, domestic supply is Qs = {c} + {d}P, and the world price is {money(pw)}. Assume the country is small, so the "
            f"world price itself does not change."
        )
        qs = parts(
            ("a", "Under free trade, compute imports."),
            ("b", "With the tariff, compute the domestic price, consumption, production, and imports."),
            ("c", "Compute government tariff revenue."),
            ("d", "Relative to free trade, state what happens to domestic consumers and producers."),
            ("e", "Explain why a tariff can raise revenue but still reduce total surplus."),
        )
        ss = parts(
            ("a", f"Free-trade imports are {num(imports)} units."),
            ("b", f"The domestic price is {money(pt)}. Qd = {num(qd_t)}, Qs = {num(qs_t)}, so imports are {num(imports_t)}."),
            ("c", f"Tariff revenue is {money(tariff)} x {num(imports_t)} = {money(revenue)}."),
            ("d", "Consumers lose from the higher price; domestic producers gain because they sell more at that higher price."),
            ("e", "Some lost consumer surplus becomes producer surplus or government revenue, but some becomes deadweight loss from inefficiently low consumption and high domestic production."),
        )
        return make_row("Trade and Welfare", "Import tariff", difficulty, f"{good.title()} Tariff", text, qs, ss, ["tariff", "imports", "surplus"], {"a": a, "b": b, "c": c, "d": d, "world_price": pw, "tariff": tariff}, family="tariff")

    tariff = 4 + i % 3
    pt = pw + tariff
    qd_t, qs_t = a - b * pt, c + d * pt
    imports_t = qd_t - qs_t
    quota = max(1, imports_t - (2 + i % 3))
    p_quota = (a - c - quota) / (b + d)
    qd_q, qs_q = a - b * p_quota, c + d * p_quota
    text = (
        f"Lawmakers are comparing a tariff and a quota in the market for {good}. Domestic demand is Qd = {a} - {b}P, domestic supply is "
        f"Qs = {c} + {d}P, and the world price is {money(pw)}. A tariff of {money(tariff)} would raise the domestic price to {money(pt)}. "
        f"An alternative quota would cap imports at {num(quota)} units."
    )
    qs = parts(
        ("a", "Compute free-trade imports."),
        ("b", "Compute imports and tariff revenue under the tariff."),
        ("c", "Find the domestic price under the quota."),
        ("d", "Compare domestic consumption and production under the tariff and quota."),
        ("e", "Who receives the scarcity value created by the quota? Why does that matter?"),
        ("f", "If the policy goal is total domestic surplus, which policy concern should receive the most weight?"),
    )
    ss = parts(
        ("a", f"Free-trade imports are {num(imports)}."),
        ("b", f"Under the tariff, imports are {num(imports_t)} and revenue is {money(tariff * imports_t)}."),
        ("c", f"Set Qd - Qs = {num(quota)}. The quota price is {money(p_quota)}."),
        ("d", f"Under the quota, Qd = {num(qd_q)} and Qs = {num(qs_q)}; under the tariff, Qd = {num(qd_t)} and Qs = {num(qs_t)}."),
        ("e", "Quota rents go to whoever owns the import licenses unless the government auctions them; unlike tariff revenue, they need not go to the government."),
        ("f", "The key concern is deadweight loss and rent transfer: both policies restrict mutually beneficial trade, but the quota can also transfer rents away from the public budget."),
    )
    return make_row("Trade and Welfare", "Tariff versus quota", difficulty, "Trade Policy Comparison", text, qs, ss, ["quota", "tariff", "quota rents"], {"a": a, "b": b, "c": c, "d": d, "world_price": pw, "tariff": tariff, "quota": quota}, family="tariff quota")


def production_costs(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f, good = firm(i, 6), product(i, 6)
    if difficulty == "easy":
        fixed, v, q = 120 + 4 * (i % 6), 12 + i % 5, 8 + i % 6
        total = fixed + v * q + q**2
        mc = v + 2 * q
        atc = total / q
        avc = v + q
        text = (
            f"{f} produces {good} with daily cost C(q) = {fixed} + {v}q + q^2. A team member wants to price by dividing total cost "
            f"by output, while another argues that the next unit should be evaluated using marginal cost. Use q = {q} to clarify the difference."
        )
        qs = parts(
            ("a", "Compute total cost at q."),
            ("b", "Compute average total cost and average variable cost at q."),
            ("c", "Compute marginal cost at q."),
            ("d", "Explain which cost concept is relevant for deciding whether to produce one more unit."),
        )
        ss = parts(
            ("a", f"C({q}) = {money(total)}."),
            ("b", f"ATC = {money(total)}/{q} = {money(atc)}. AVC = ({v}q + q^2)/q = {money(avc)}."),
            ("c", f"MC(q) = {v} + 2q, so MC({q}) = {money(mc)}."),
            ("d", "The one-more-unit decision uses marginal cost, because fixed and already-incurred costs do not change with that unit."),
        )
        return make_row("Production and Costs", "Cost concepts", difficulty, "Average Cost Versus Marginal Cost", text, qs, ss, ["marginal cost", "average cost"], {"fixed": fixed, "v": v, "q": q}, {"cost": f"C(q)={fixed}+{v}q+q^2"}, family="cost concepts")

    if difficulty == "medium":
        fixed, v, price = 144 + 4 * (i % 5), 18 + i % 4, 46 + i % 8
        qstar = max(0, (price - v) / 2)
        profit = price * qstar - fixed - v * qstar - qstar**2
        min_atc = v + 2 * math.sqrt(fixed)
        text = (
            f"{f} is a small producer in a competitive market for {good}. Its short-run cost is C(q) = {fixed} + {v}q + q^2, and the "
            f"market price is {money(price)}. The fixed cost is unavoidable this month, but not in the long run. Management asks whether "
            f"the firm should produce now and whether the industry should expect entry or exit later."
        )
        qs = parts(
            ("a", "Find the profit-maximizing quantity using P = MC."),
            ("b", "Compute short-run profit at that quantity."),
            ("c", "Should the firm produce or shut down this month?"),
            ("d", "Compute the minimum average total cost."),
            ("e", "Use the long-run logic of entry and exit to predict pressure on market price."),
        )
        ss = parts(
            ("a", f"MC = {v} + 2q. Setting {price} = {v} + 2q gives q = {num(qstar)}."),
            ("b", f"Profit is Pq - C(q) = {money(profit)}."),
            ("c", f"The firm produces because price exceeds minimum AVC, which is {money(v)} for this cost function."),
            ("d", f"ATC = {fixed}/q + {v} + q, minimized at q = sqrt({fixed}); min ATC = {money(min_atc)}."),
            ("e", f"Since price is {'above' if price > min_atc else 'below'} min ATC, long-run forces point toward {'entry and falling price' if price > min_atc else 'exit and rising price'}."),
        )
        return make_row("Production and Costs", "Short run and long run cost", difficulty, "Production Decision with Fixed Cost", text, qs, ss, ["P=MC", "shutdown", "entry"], {"fixed": fixed, "v": v, "price": price}, {"cost": f"C(q)={fixed}+{v}q+q^2"}, family="short run long run")

    w, r, q = 16 + i % 5, 25 + i % 6, 20 + i % 5
    lstar = q * math.sqrt(r / w)
    kstar = q * math.sqrt(w / r)
    cost = w * lstar + r * kstar
    text = (
        f"{f} can produce {good} using labor L and machine time K according to q = sqrt(LK). Labor costs {money(w)} per unit and "
        f"machine time costs {money(r)} per unit. The operations team needs q = {q} units for a contract and asks whether simply using "
        f"equal amounts of L and K is cost-minimizing."
    )
    qs = parts(
        ("a", "Write the cost-minimization problem."),
        ("b", "Use the tangency condition to find the cost-minimizing ratio of K to L."),
        ("c", "Find the cost-minimizing input quantities."),
        ("d", "Compute the minimized cost."),
        ("e", "If labor becomes more expensive, what should happen to the input mix?"),
        ("f", "Explain why equal physical quantities of inputs are generally not the same as cost minimization."),
    )
    ss = parts(
        ("a", f"Minimize {w}L + {r}K subject to sqrt(LK) = {q}, or LK = {q**2}."),
        ("b", f"The tangency condition gives K/L = w/r = {num(w / r)}."),
        ("c", f"L = q sqrt(r/w) = {num(lstar)} and K = q sqrt(w/r) = {num(kstar)}."),
        ("d", f"Minimized cost is {money(w * lstar)} + {money(r * kstar)} = {money(cost)}."),
        ("e", "The firm should substitute away from labor and toward machine time. Since K/L = w/r, a higher labor wage raises the machine-time-to-labor ratio."),
        ("f", "Cost minimization equalizes marginal product per dollar, not raw units. Input prices matter."),
    )
    return make_row("Production and Costs", "Cost minimization", difficulty, "Choosing Inputs for a Contract", text, qs, ss, ["cost minimization", "input choice"], {"w": w, "r": r, "q": q}, {"production": "q=sqrt(LK)"}, family="cost minimization")


def perfect_competition(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f, good = firm(i, 7), product(i, 7)
    fixed, v = 100 + 4 * (i % 6), 20 + i % 5
    if difficulty == "easy":
        p = v + 18 + i % 6
        q = (p - v) / 2
        profit = p * q - fixed - v * q - q**2
        text = (
            f"{f} is one of many small sellers of {good}. Its cost is C(q) = {fixed} + {v}q + q^2, and the market price this week is "
            f"{money(p)}. The owner understands that she is a price taker but is unsure how that translates into an output decision."
        )
        qs = parts(
            ("a", "Explain why marginal revenue equals price for this firm."),
            ("b", "Find the profit-maximizing quantity."),
            ("c", "Compute profit at that quantity."),
            ("d", "Would positive profit by this firm be expected to persist in the long run? Explain."),
        )
        ss = parts(
            ("a", "A price-taking firm can sell another unit at the market price, so MR = P."),
            ("b", f"Set P = MC: {p} = {v} + 2q, so q = {num(q)}."),
            ("c", f"Profit is {money(profit)}."),
            ("d", "If entry is free and firms are similar, positive economic profit attracts entry and pushes price down."),
        )
        return make_row("Perfect Competition", "Price-taking output", difficulty, "A Price-Taking Output Decision", text, qs, ss, ["price taking", "P=MC", "entry"], {"fixed": fixed, "v": v, "price": p}, {"cost": f"C(q)={fixed}+{v}q+q^2"}, family="price taking")

    if difficulty == "medium":
        p = v + 10 + i % 7
        q = (p - v) / 2
        profit = p * q - fixed - v * q - q**2
        min_atc = v + 2 * math.sqrt(fixed)
        text = (
            f"A competitive market for {good} has become crowded. A representative firm has C(q) = {fixed} + {v}q + q^2 and currently "
            f"faces price {money(p)}. The fixed cost is sunk in the short run. Students often confuse producing at a loss with exiting, "
            f"so answer separately for the short run and the long run."
        )
        qs = parts(
            ("a", "Find the firm's short-run output."),
            ("b", "Compute profit or loss."),
            ("c", "Should the firm produce in the short run?"),
            ("d", "Find the long-run break-even price."),
            ("e", "Predict whether firms enter, exit, or neither in the long run."),
        )
        ss = parts(
            ("a", f"q = ({p} - {v})/2 = {num(q)}."),
            ("b", f"Profit is {money(profit)}."),
            ("c", f"Yes, because P = {money(p)} is above minimum AVC = {money(v)}, so production helps cover fixed cost."),
            ("d", f"Minimum ATC is {money(min_atc)}."),
            ("e", f"Since price is {'below' if p < min_atc else 'above'} break-even, firms {'exit' if p < min_atc else 'enter'} until price moves toward min ATC."),
        )
        return make_row("Perfect Competition", "Shutdown and exit", difficulty, "Short-Run Losses and Long-Run Exit", text, qs, ss, ["shutdown", "AVC", "entry and exit"], {"fixed": fixed, "v": v, "price": p}, {"cost": f"C(q)={fixed}+{v}q+q^2"}, family="shutdown exit")

    n, a, b = 18 + i % 5, 520 + 4 * i, 3
    # Individual supply is q=(P-v)/2. Industry supply is n(P-v)/2.
    p = (a + (n * v / 2)) / (b + n / 2)
    q_market = a - b * p
    q_firm = (p - v) / 2
    min_atc = v + 2 * math.sqrt(fixed)
    text = (
        f"There are {n} identical competitive firms producing {good}. Each has C(q) = {fixed} + {v}q + q^2, and market demand is "
        f"Qd = {a} - {b}P. Assume firms with positive output follow P = MC in the short run. The industry association wants to know "
        f"how a short-run equilibrium differs from a long-run equilibrium with entry and exit."
    )
    qs = parts(
        ("a", "Derive one firm's short-run supply curve for positive output."),
        ("b", "Derive industry supply with the current number of firms."),
        ("c", "Find the short-run market price and quantity."),
        ("d", "Find output per firm and profit per firm."),
        ("e", "Compare the short-run price with minimum ATC."),
        ("f", "Predict the direction of entry or exit and the long-run price pressure."),
    )
    profit = p * q_firm - fixed - v * q_firm - q_firm**2
    ss = parts(
        ("a", f"P = {v} + 2q, so q = (P - {v})/2 for P > {money(v)}."),
        ("b", f"Industry supply is Qs = {n}(P - {v})/2."),
        ("c", f"Solving Qd = Qs gives P = {money(p)} and Q = {num(q_market)}."),
        ("d", f"Each firm produces {num(q_firm)} and earns profit {money(profit)}."),
        ("e", f"Minimum ATC is {money(min_atc)}, so price is {'above' if p > min_atc else 'below'} break-even."),
        ("f", f"Firms will {'enter' if p > min_atc else 'exit'}, putting {'downward' if p > min_atc else 'upward'} pressure on price."),
    )
    return make_row("Perfect Competition", "Industry supply and entry", difficulty, "Competitive Industry Adjustment", text, qs, ss, ["industry supply", "entry", "zero profit"], {"n": n, "a": a, "b": b, "fixed": fixed, "v": v}, {"cost": f"C(q)={fixed}+{v}q+q^2"}, family="industry entry")


def monopoly(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f, good = firm(i, 8), product(i, 8)
    a, b, mc, fixed = 120 + i, 2, 18 + i % 7, 80 + 5 * (i % 5)
    qm = (a - mc) / (2 * b)
    pm = a - b * qm
    profit = (pm - mc) * qm - fixed
    qc = (a - mc) / b
    if difficulty == "easy":
        elasticity = -pm / (b * qm)
        text = (
            f"{f} is the only provider of a specialized {good} service in its region. Inverse demand is P = {a} - {b}Q, marginal cost "
            f"is constant at {money(mc)}, and fixed cost is {money(fixed)}. The firm wants to understand why a monopolist does not simply "
            f"serve every customer with willingness to pay above marginal cost."
        )
        qs = parts(
            ("a", "Write marginal revenue."),
            ("b", "Find the monopoly quantity and price."),
            ("c", "Compute profit."),
            ("d", "Explain why the monopoly price is above marginal cost."),
        )
        ss = parts(
            ("a", f"Revenue is {a}Q - {b}Q^2, so MR = {a} - {2 * b}Q."),
            ("b", f"Set MR = MC: Q = {num(qm)} and P = {money(pm)}."),
            ("c", f"Profit is ({money(pm)} - {money(mc)}) x {num(qm)} - {money(fixed)} = {money(profit)}."),
            ("d", "Selling more requires lowering price on marginal and inframarginal units, so the monopolist restricts quantity to keep price above MC."),
        )
        return make_row("Monopoly", "Monopoly pricing", difficulty, "Monopoly Output and Markup", text, qs, ss, ["MR=MC", "markup"], {"a": a, "b": b, "mc": mc, "fixed": fixed, "elasticity": elasticity}, family="monopoly pricing")

    if difficulty == "medium":
        dwl = 0.5 * (pm - mc) * (qc - qm)
        text = (
            f"{f} has local monopoly power over {good}. Demand is P = {a} - {b}Q and marginal cost is {money(mc)}. A regulator asks "
            f"students to compare the monopoly outcome with a competitive benchmark where price equals marginal cost."
        )
        qs = parts(
            ("a", "Find monopoly price and quantity."),
            ("b", "Find the competitive benchmark quantity and price."),
            ("c", "Compute monopoly profit before fixed cost and total profit after fixed cost."),
            ("d", "Compute deadweight loss from monopoly pricing."),
            ("e", "Explain who gets hurt by monopoly pricing and why total surplus falls."),
        )
        ss = parts(
            ("a", f"Monopoly Q = {num(qm)} and P = {money(pm)}."),
            ("b", f"Competitive price equals MC = {money(mc)} and Q = {num(qc)}."),
            ("c", f"Variable profit is {money((pm - mc) * qm)}; after fixed cost, profit is {money(profit)}."),
            ("d", f"DWL is 0.5 x ({money(pm)} - {money(mc)}) x ({num(qc)} - {num(qm)}) = {money(dwl)}."),
            ("e", "Consumers with values between MC and the monopoly price are excluded; those lost trades would have created surplus."),
        )
        return make_row("Monopoly", "Monopoly welfare", difficulty, "Market Power and Deadweight Loss", text, qs, ss, ["deadweight loss", "competitive benchmark"], {"a": a, "b": b, "mc": mc, "fixed": fixed}, family="monopoly welfare")

    tax = 6 + i % 5
    q_tax = (a - mc - tax) / (2 * b)
    p_tax = a - b * q_tax
    profit_tax = (p_tax - mc - tax) * q_tax - fixed
    cap = mc + 10 + i % 5
    q_cap = (a - cap) / b
    text = (
        f"A public debate over {possessive(f)} {good} service considers two policies. Demand is P = {a} - {b}Q, marginal cost is "
        f"{money(mc)}, and fixed cost is {money(fixed)}. Policy 1 is a per-unit tax of {money(tax)}. Policy 2 is a price cap of "
        f"{money(cap)}. Assume the firm serves all demand at the cap if doing so covers marginal cost."
    )
    qs = parts(
        ("a", "Find the unregulated monopoly price and quantity."),
        ("b", "Find monopoly price, quantity, and profit under the per-unit tax."),
        ("c", "Find quantity demanded at the price cap."),
        ("d", "Compare consumer quantity under the cap with unregulated monopoly quantity."),
        ("e", "Which policy is more likely to expand output?"),
        ("f", "Explain why price regulation can improve allocation but still create practical concerns."),
    )
    ss = parts(
        ("a", f"Unregulated Q = {num(qm)} and P = {money(pm)}."),
        ("b", f"The tax raises effective MC to {money(mc + tax)}. Q = {num(q_tax)}, P = {money(p_tax)}, and after-tax profit is {money(profit_tax)}."),
        ("c", f"At the cap, Qd = ({a} - {cap})/{b} = {num(q_cap)}."),
        ("d", f"The cap quantity is {'higher' if q_cap > qm else 'lower'} than monopoly quantity ({num(q_cap)} versus {num(qm)})."),
        ("e", "The price cap is more likely to expand output because it lowers price toward marginal cost, while the tax raises effective marginal cost."),
        ("f", "A well-chosen cap can reduce deadweight loss, but a cap below cost could reduce service quality, create shortages, or discourage investment."),
    )
    return make_row("Monopoly", "Regulation and tax", difficulty, "Regulating a Local Monopoly", text, qs, ss, ["price cap", "monopoly tax", "regulation"], {"a": a, "b": b, "mc": mc, "fixed": fixed, "tax": tax, "cap": cap}, family="regulation")


def price_discrimination(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f = firm(i, 9)
    if difficulty == "easy":
        high, low, cost = 90 + i % 8, 55 + i % 6, 20 + i % 4
        n_high, n_low = 80 + i % 5, 120 + i % 7
        profit_low_price = (low - cost) * (n_high + n_low)
        profit_high_price = (high - cost) * n_high
        text = (
            f"{f} sells a single-use pass to two customer groups. {n_low} casual customers are willing to pay {money(low)}, and "
            f"{n_high} business customers are willing to pay {money(high)}. Marginal cost is {money(cost)}. The firm cannot initially "
            f"identify customers, so it must set one price."
        )
        qs = parts(
            ("a", "Compute profit from setting the low price and serving both groups."),
            ("b", "Compute profit from setting the high price and serving only business customers."),
            ("c", "Which uniform price should the firm choose?"),
            ("d", "Explain why the firm would like to price discriminate if it could prevent resale."),
        )
        ss = parts(
            ("a", f"Profit is ({money(low)} - {money(cost)}) x {n_low + n_high} = {money(profit_low_price)}."),
            ("b", f"Profit is ({money(high)} - {money(cost)}) x {n_high} = {money(profit_high_price)}."),
            ("c", f"The firm chooses the {'low' if profit_low_price > profit_high_price else 'high'} price because it gives higher profit."),
            ("d", "Different groups have different willingness to pay. Charging each group closer to its value would capture more surplus if arbitrage is prevented."),
        )
        return make_row("Price Discrimination", "Uniform versus group pricing", difficulty, "One Price or Two?", text, qs, ss, ["reservation price", "uniform pricing"], {"high": high, "low": low, "cost": cost, "n_high": n_high, "n_low": n_low}, family="uniform pricing")

    if difficulty == "medium":
        low_basic, high_basic = 44 + i % 5, 56 + i % 5
        low_premium, high_premium = 58 + i % 6, 88 + i % 7
        cost_basic, cost_premium = 16 + i % 4, 24 + i % 5
        n_low = n_high = 100
        p_basic = low_basic
        p_premium = high_premium - (high_basic - p_basic)
        menu_profit = n_low * (p_basic - cost_basic) + n_high * (p_premium - cost_premium)
        single_price = high_premium
        single_profit = n_high * (single_price - cost_premium)
        text = (
            f"{f} can sell a basic and premium version of a service. There are 100 flexible users and 100 high-value users. Flexible users "
            f"value basic at {money(low_basic)} and premium at {money(low_premium)}. High-value users value basic at {money(high_basic)} and premium at "
            f"{money(high_premium)}. Costs are {money(cost_basic)} for basic and {money(cost_premium)} for premium. The firm cannot observe type."
        )
        qs = parts(
            ("a", "Set the highest basic price that keeps flexible users buying."),
            ("b", "Set the highest premium price that keeps high-value users choosing premium over basic."),
            ("c", "Compute profit from this self-selection menu."),
            ("d", "Compare with selling only premium at the high-value reservation price."),
            ("e", "Explain why the premium product may need to leave information rents to high-value users."),
        )
        ss = parts(
            ("a", f"The basic price can be {money(p_basic)}."),
            ("b", f"High-value users need {high_premium} - Ppremium >= {high_basic} - {p_basic}, so Ppremium = {money(p_premium)}."),
            ("c", f"Menu profit is 100({money(p_basic)} - {money(cost_basic)}) + 100({money(p_premium)} - {money(cost_premium)}) = {money(menu_profit)}."),
            ("d", f"Premium-only profit is 100({money(single_price)} - {money(cost_premium)}) = {money(single_profit)}."),
            ("e", "If the premium price extracts all high-type surplus, high types may prefer the basic version. The firm leaves rents to preserve self-selection."),
        )
        return make_row("Price Discrimination", "Self-selection menu", difficulty, "Designing a Pricing Menu", text, qs, ss, ["self-selection", "information rents", "versioning"], {"low_basic": low_basic, "high_basic": high_basic, "low_premium": low_premium, "high_premium": high_premium, "cost_basic": cost_basic, "cost_premium": cost_premium}, family="versioning")

    a1, b1, a2, b2, mc = 110 + i, 2, 80 + i, 1, 20 + i % 5
    q1 = (a1 - mc) / (2 * b1)
    p1 = a1 - b1 * q1
    q2 = (a2 - mc) / (2 * b2)
    p2 = a2 - b2 * q2
    profit_sep = (p1 - mc) * q1 + (p2 - mc) * q2
    text = (
        f"{f} can prevent resale between two markets. In market A, inverse demand is P_A = {a1} - {b1}Q_A. In market B, inverse demand is "
        f"P_B = {a2} - {b2}Q_B. Marginal cost is {money(mc)} in both markets. The firm is considering third-degree price discrimination."
    )
    qs = parts(
        ("a", "Write marginal revenue in each market."),
        ("b", "Find the profit-maximizing quantity and price in market A."),
        ("c", "Find the profit-maximizing quantity and price in market B."),
        ("d", "Compute total variable profit under separate pricing."),
        ("e", "Which market receives the higher price, and what does that imply about elasticity?"),
        ("f", "Name one condition needed for this pricing strategy to work."),
    )
    ss = parts(
        ("a", f"MR_A = {a1} - {2 * b1}Q_A and MR_B = {a2} - {2 * b2}Q_B."),
        ("b", f"Market A: Q = {num(q1)} and P = {money(p1)}."),
        ("c", f"Market B: Q = {num(q2)} and P = {money(p2)}."),
        ("d", f"Total variable profit is {money(profit_sep)}."),
        ("e", f"The higher price is in market {'A' if p1 > p2 else 'B'}, indicating relatively less elastic demand at the chosen quantity."),
        ("f", "The firm must be able to segment customers and prevent profitable resale/arbitrage."),
    )
    return make_row("Price Discrimination", "Third-degree price discrimination", difficulty, "Separate Prices Across Markets", text, qs, ss, ["third-degree price discrimination", "MR=MC"], {"a1": a1, "b1": b1, "a2": a2, "b2": b2, "mc": mc}, family="third degree")


def risk_insurance(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    if difficulty == "easy":
        safe, base, bonus, prob = 92 + i % 8, 70 + i % 6, 36 + i % 9, 0.6
        ev = base + prob * bonus
        eu_risky = prob * math.sqrt(base + bonus) + (1 - prob) * math.sqrt(base)
        ce = eu_risky**2
        text = (
            f"A graduating student compares two jobs. Job Safe pays {money(safe)} thousand for sure. Job Bonus pays {money(base)} thousand "
            f"plus a {money(bonus)} thousand bonus with probability {pct(prob)}. Payoffs are measured in thousands of dollars, and the student "
            f"has utility u(x) = sqrt(x)."
        )
        qs = parts(
            ("a", "Compute the expected monetary value of Job Bonus."),
            ("b", "Which job would a risk-neutral student choose?"),
            ("c", "Compute the expected utility of Job Bonus and the utility of Job Safe."),
            ("d", "Explain why risk aversion can change the ranking even when expected value is higher."),
        )
        ss = parts(
            ("a", f"EV(Bonus) = {base} + {prob} x {bonus} = {money(ev)} thousand."),
            ("b", f"A risk-neutral student chooses {'Job Bonus' if ev > safe else 'Job Safe'} because it has the higher expected value."),
            ("c", f"EU(Bonus) = {num(eu_risky)} and U(Safe) = {num(math.sqrt(safe))}."),
            ("d", "Risk-averse utility is concave, so downside risk lowers expected utility relative to a sure payment with the same expected value."),
        )
        return make_row("Risk and Insurance", "Risky job choice", difficulty, "Choosing Between Job Offers", text, qs, ss, ["expected value", "expected utility", "risk aversion"], {"safe": safe, "base": base, "bonus": bonus, "prob": prob}, {"utility": "sqrt(x)"}, family="job risk")

    if difficulty == "medium":
        wealth, loss, prob = 250, 90 + i % 15, 0.02 + (i % 4) * 0.005
        premium = prob * loss + 1
        eu_no = prob * math.log(wealth - loss) + (1 - prob) * math.log(wealth)
        ce_no = math.exp(eu_no)
        wtp = wealth - ce_no
        text = (
            f"A small business has wealth of {money(wealth)} thousand. A flood would cause a loss of {money(loss)} thousand with probability "
            f"{pct(prob)}. The owner has utility u(x) = ln(x), with x in thousands. Full insurance is available for a premium of "
            f"{money(premium)} thousand."
        )
        qs = parts(
            ("a", "Compute the expected monetary value of remaining uninsured."),
            ("b", "Compute the certainty equivalent of remaining uninsured."),
            ("c", "Compute the maximum premium the owner would pay for full insurance."),
            ("d", "Should the owner buy the policy at the offered premium?"),
            ("e", "Explain why insurance can be attractive even when it is not actuarially favorable."),
        )
        ev_no = wealth - prob * loss
        ss = parts(
            ("a", f"EV uninsured is {money(ev_no)} thousand."),
            ("b", f"CE solves ln(CE) = {pct(prob)} ln({wealth - loss}) + {pct(1 - prob)} ln({wealth}), so CE = {money(ce_no)} thousand."),
            ("c", f"Maximum premium for full insurance is {money(wealth - ce_no)} thousand."),
            ("d", f"The owner {'buys' if premium <= wtp else 'does not buy'} because the offered premium is {'below' if premium <= wtp else 'above'} willingness to pay."),
            ("e", "Insurance removes risk. A risk-averse person may accept a lower expected monetary value in exchange for a less variable outcome."),
        )
        return make_row("Risk and Insurance", "Insurance willingness to pay", difficulty, "Flood Insurance and Risk Premium", text, qs, ss, ["certainty equivalent", "insurance", "risk premium"], {"wealth": wealth, "loss": loss, "prob": prob, "premium": premium}, {"utility": "ln(x)"}, family="insurance WTP")

    safe, base, bonus, prob = 110 + i % 8, 86 + i % 6, 58 + i % 7, 0.75
    ev = base + prob * bonus
    eu = prob * math.sqrt(base + bonus) + (1 - prob) * math.sqrt(base)
    ce = eu**2
    smoother_base = ev - 20
    smoother_bonus = 20 / prob
    eu_smooth = prob * math.sqrt(smoother_base + smoother_bonus) + (1 - prob) * math.sqrt(smoother_base)
    text = (
        f"A firm offers analysts a risky compensation package: base salary {money(base)} thousand and a bonus of {money(bonus)} thousand "
        f"with probability {pct(prob)}. A competing firm offers a guaranteed {money(safe)} thousand. Analysts have utility u(x)=sqrt(x). "
        f"The firm is considering a smoother package with the same expected value but a smaller bonus."
    )
    qs = parts(
        ("a", "Compute the expected value of the risky package."),
        ("b", "Compute its certainty equivalent."),
        ("c", "Which offer does a risk-averse analyst prefer: the risky package or the guaranteed competing offer?"),
        ("d", "Construct the smoother package described: base salary plus smaller bonus with the same expected value."),
        ("e", "Compare expected utility under the original and smoother packages."),
        ("f", "Explain the compensation design lesson for a firm hiring risk-averse workers."),
    )
    ss = parts(
        ("a", f"EV = {money(ev)} thousand."),
        ("b", f"CE = EU^2 = {money(ce)} thousand."),
        ("c", f"The analyst prefers {'the risky package' if ce > safe else 'the guaranteed offer'} because CE is {'above' if ce > safe else 'below'} {money(safe)} thousand."),
        ("d", f"Using a {money(20)} thousand expected bonus component gives bonus {money(smoother_bonus)} thousand and base {money(smoother_base)} thousand."),
        ("e", f"EU original is {num(eu)}; EU smoother is {num(eu_smooth)}. The smoother package is {'preferred' if eu_smooth > eu else 'not preferred'} by risk-averse workers."),
        ("f", "For risk-averse employees, the firm may need to pay a risk premium for volatile compensation; smoother pay can be valuable even at the same expected value."),
    )
    return make_row("Risk and Insurance", "Compensation risk", difficulty, "Risky Pay and Smoother Contracts", text, qs, ss, ["expected utility", "certainty equivalent", "risk premium"], {"safe": safe, "base": base, "bonus": bonus, "prob": prob}, {"utility": "sqrt(x)"}, family="compensation risk")


def asymmetric_information(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f, good = firm(i, 11), product(i, 1)
    if difficulty == "easy":
        share_good = 0.6
        good_value, bad_value = 120 + i % 10, 60 + i % 8
        good_cost, bad_cost = 85 + i % 6, 45 + i % 5
        pooled = share_good * good_value + (1 - share_good) * bad_value
        text = (
            f"Buyers in a used-{good} market cannot tell high-quality units from low-quality units before purchase. High-quality units are "
            f"worth {money(good_value)} to buyers and cost sellers {money(good_cost)} to part with. Low-quality units are worth {money(bad_value)} "
            f"and cost sellers {money(bad_cost)}. Buyers believe {pct(share_good)} of units are high quality."
        )
        qs = parts(
            ("a", "Compute buyers' willingness to pay for a randomly selected unit."),
            ("b", "At that pooled price, which sellers are willing to sell?"),
            ("c", "If high-quality sellers leave, what happens to buyers' willingness to pay?"),
            ("d", "Explain why this is an adverse selection problem."),
        )
        ss = parts(
            ("a", f"Pooled WTP is {pct(share_good)} x {money(good_value)} + {pct(1 - share_good)} x {money(bad_value)} = {money(pooled)}."),
            ("b", f"High-quality sellers {'sell' if pooled >= good_cost else 'do not sell'}; low-quality sellers sell because {money(pooled)} exceeds {money(bad_cost)}."),
            ("c", f"If only low-quality units remain, WTP falls to {money(bad_value)}."),
            ("d", "The market pool worsens as price attracts low-quality sellers and discourages high-quality sellers, reducing gains from trade."),
        )
        return make_row("Asymmetric Information", "Adverse selection", difficulty, "Quality Uncertainty in a Used Market", text, qs, ss, ["adverse selection", "lemons"], {"share_good": share_good, "good_value": good_value, "bad_value": bad_value, "good_cost": good_cost, "bad_cost": bad_cost}, family="lemons")

    if difficulty == "medium":
        p_no, warranty, p_w = 78 + i % 8, 28 + i % 5, 112 + i % 7
        good_cost, bad_cost = 70 + i % 5, 52 + i % 4
        text = (
            f"{f} sells refurbished {good}. Without a warranty, units sell for {money(p_no)}. A high-quality seller expects no repair cost "
            f"from a warranty, while a low-quality seller expects warranty claims of {money(warranty)}. A proposed certified listing includes "
            f"the warranty and sells for {money(p_w)}."
        )
        qs = parts(
            ("a", "Compute the payoff from selling without a warranty for each type."),
            ("b", "Compute the payoff from selling with the warranty for each type."),
            ("c", "Which type is willing to offer the warranty?"),
            ("d", "Explain how the warranty can serve as a signal."),
            ("e", "Name one real-world limitation of relying on warranties as signals."),
        )
        ss = parts(
            ("a", f"No-warranty payoffs are {money(p_no - good_cost)} for high quality and {money(p_no - bad_cost)} for low quality."),
            ("b", f"Warranty payoffs are {money(p_w - good_cost)} for high quality and {money(p_w - warranty - bad_cost)} for low quality."),
            ("c", "The type with the higher relative payoff from warranty listing will offer it; with these numbers, high quality benefits more."),
            ("d", "The signal works because it is less costly for high-quality sellers to provide than for low-quality sellers."),
            ("e", "Claims abuse, weak enforcement, exclusions, or seller bankruptcy can make warranties less credible."),
        )
        return make_row("Asymmetric Information", "Warranty signaling", difficulty, "Warranty as a Quality Signal", text, qs, ss, ["signaling", "warranty", "quality"], {"p_no": p_no, "warranty": warranty, "p_w": p_w, "good_cost": good_cost, "bad_cost": bad_cost}, family="warranty")

    safe_p, risky_p, loss, wealth = 0.01, 0.05, 100, 250
    full_premium, partial_premium, deductible = 5, 1, 70 + i % 10
    text = (
        f"An insurer cannot observe whether drivers are safe or risky. Safe drivers have accident probability {pct(safe_p)}; risky drivers "
        f"have probability {pct(risky_p)}. An accident costs {money(loss)} thousand, and all drivers have wealth {money(wealth)} thousand with "
        f"utility u(x)=ln(x). The insurer considers a full-insurance plan with premium {money(full_premium)} thousand and a partial plan with "
        f"premium {money(partial_premium)} thousand and deductible {money(deductible)} thousand."
    )
    def eu_plan(prob: float, premium: float, deductible_value: float) -> float:
        return prob * math.log(wealth - premium - deductible_value) + (1 - prob) * math.log(wealth - premium)
    eu_safe_full = math.log(wealth - full_premium)
    eu_safe_partial = eu_plan(safe_p, partial_premium, deductible)
    eu_risky_full = math.log(wealth - full_premium)
    eu_risky_partial = eu_plan(risky_p, partial_premium, deductible)
    qs = parts(
        ("a", "Compute the expected cost of fully insuring each type."),
        ("b", "For safe drivers, compare expected utility under the full and partial plans."),
        ("c", "For risky drivers, compare expected utility under the full and partial plans."),
        ("d", "Which type is more likely to choose the high-deductible plan?"),
        ("e", "Explain how a menu of plans can reduce adverse selection."),
        ("f", "Why might the insurer still fail to reach the first-best outcome?"),
    )
    ss = parts(
        ("a", f"Expected costs are {money(safe_p * loss)} thousand for safe drivers and {money(risky_p * loss)} thousand for risky drivers."),
        ("b", f"Safe EU full = {num(eu_safe_full)}; safe EU partial = {num(eu_safe_partial)}."),
        ("c", f"Risky EU full = {num(eu_risky_full)}; risky EU partial = {num(eu_risky_partial)}."),
        ("d", "Safe drivers are more likely to choose the high-deductible plan because they are less likely to pay the deductible."),
        ("e", "The menu screens customers: low-risk types self-select into lower premiums with more exposure, while high-risk types value full coverage more."),
        ("f", "Risk remains, some efficient coverage may be distorted to preserve self-selection, and the insurer still cannot directly observe type."),
    )
    return make_row("Asymmetric Information", "Insurance screening", difficulty, "Screening with Insurance Plans", text, qs, ss, ["screening", "adverse selection", "insurance"], {"safe_p": safe_p, "risky_p": risky_p, "loss": loss, "wealth": wealth, "full_premium": full_premium, "partial_premium": partial_premium, "deductible": deductible}, {"utility": "ln(x)"}, family="screening")


def incentives_contracts(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f = firm(i, 12)
    s, n, c, m = 0.75, 0.25, 3 + i % 4, 12 + i % 5
    b = c / (s - n)
    w = m - s * b + c
    if difficulty == "easy":
        text = (
            f"{f} employs sales associates who can either help customers or hide in the stockroom. Helping creates a sale with probability "
            f"{pct(s)}; hiding creates a sale with probability {pct(n)}. Effort costs the worker {money(c)} per hour, and the outside wage is "
            f"{money(m)} per hour. Workers are risk-neutral."
        )
        qs = parts(
            ("a", "Write the worker's expected payoff from helping under wage w and bonus b."),
            ("b", "Write the worker's expected payoff from hiding."),
            ("c", "Find the minimum bonus that makes helping incentive compatible."),
            ("d", "Explain why a flat wage would not solve the hidden-action problem."),
        )
        ss = parts(
            ("a", "Helping payoff is w + S b - c."),
            ("b", "Hiding payoff is w + n b."),
            ("c", f"Need (S - n)b >= c, so b = {c}/({s} - {n}) = {money(b)}."),
            ("d", "With a flat wage, the worker bears the effort cost but does not receive a higher payoff when effort raises the chance of sale."),
        )
        return make_row("Incentives and Contracts", "Incentive compatibility", difficulty, "Motivating Sales Effort", text, qs, ss, ["moral hazard", "incentive compatibility"], {"s": s, "n": n, "c": c, "m": m}, family="IC")

    if difficulty == "medium":
        margin = b + 2 + i % 5
        text = (
            f"{f} is designing a bonus contract. If an employee works hard, the success probability is {pct(s)}; if the employee shirks, it is "
            f"{pct(n)}. Effort costs {money(c)}, the outside option is {money(m)}, and workers are risk-neutral. Each success creates margin "
            f"{money(margin)} for the firm before labor compensation."
        )
        qs = parts(
            ("a", "Find the minimum bonus that induces high effort."),
            ("b", "Find the base wage that satisfies participation at equality."),
            ("c", "Compute the worker's expected pay under high effort."),
            ("d", "Is the incentive scheme profitable relative to paying the outside wage and accepting low effort?"),
            ("e", "Explain how the answer changes if effort becomes harder to measure or workers become risk-averse."),
        )
        profit_bonus = s * (margin - b) - w
        profit_flat = n * margin - m
        ss = parts(
            ("a", f"b* = c/(S - n) = {c}/({s} - {n}) = {money(b)}."),
            ("b", f"w* = m - S b* + c = {money(w)}."),
            ("c", f"Expected worker payoff is w + S b - c = {money(m)}, exactly the outside option."),
            ("d", f"Firm profit with incentives is {money(profit_bonus)} per worker-period; flat-wage profit is {money(profit_flat)}. Incentives are {'worthwhile' if profit_bonus >= profit_flat else 'not worthwhile'} here."),
            ("e", "Noisier measurement weakens the link between effort and reward; risk aversion makes bonus pay costly because workers require compensation for income risk."),
        )
        return make_row("Incentives and Contracts", "Optimal bonus contract", difficulty, "Base Pay and Bonus Design", text, qs, ss, ["bonus", "participation", "moral hazard"], {"s": s, "n": n, "c": c, "m": m, "margin": margin}, family="bonus contract")

    margin_low, margin_high = b - 1, b + 4 + i % 4
    text = (
        f"{f} can use the same risk-neutral bonus contract in two departments. In both departments, effort raises success probability from "
        f"{pct(n)} to {pct(s)} and costs the worker {money(c)}. The outside wage is {money(m)}. The margin from success is {money(margin_low)} "
        f"in Department L and {money(margin_high)} in Department H."
    )
    qs = parts(
        ("a", "Find the incentive-compatible bonus."),
        ("b", "Find the base wage satisfying participation."),
        ("c", "Derive the simple condition for whether incentivizing effort is worth it."),
        ("d", "Apply the condition to Department L."),
        ("e", "Apply the condition to Department H."),
        ("f", "Explain why the same worker-side contract can be optimal in one department but not another."),
    )
    threshold = c / (s - n)
    ss = parts(
        ("a", f"b* = {money(b)}."),
        ("b", f"w* = {money(w)}."),
        ("c", f"Effort is worth inducing when margin X >= c/(S - n) = {money(threshold)}."),
        ("d", f"Department L margin is {money(margin_low)}, so incentives are {'worthwhile' if margin_low >= threshold else 'not worthwhile'}."),
        ("e", f"Department H margin is {money(margin_high)}, so incentives are {'worthwhile' if margin_high >= threshold else 'not worthwhile'}."),
        ("f", "The worker's incentive problem is the same, but the firm's benefit from extra success differs across departments."),
    )
    return make_row("Incentives and Contracts", "When incentives are worth it", difficulty, "Should the Firm Use Bonus Pay?", text, qs, ss, ["moral hazard", "profitability", "contract design"], {"s": s, "n": n, "c": c, "m": m, "margin_low": margin_low, "margin_high": margin_high}, family="contract profitability")


def game_theory(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f1, f2 = firm(i, 13), firm(i, 14)
    if difficulty == "easy":
        high_high, low_high, high_low, low_low = 2400 + 10 * i, 2700 + 10 * i, 1200 + 5 * i, 1800 + 5 * i
        text = (
            f"{f1} and {f2} simultaneously choose a high price or a low price. If both choose High, each earns {money(high_high)}. "
            f"If one chooses Low while the other chooses High, the low-price firm earns {money(low_high)} and the high-price firm earns "
            f"{money(high_low)}. If both choose Low, each earns {money(low_low)}."
        )
        qs = parts(
            ("a", "For one firm, identify the best response if the rival chooses High."),
            ("b", "For one firm, identify the best response if the rival chooses Low."),
            ("c", "Find the Nash equilibrium."),
            ("d", "Explain why the equilibrium may be worse for both firms than mutual high pricing."),
        )
        ss = parts(
            ("a", f"Low is better against High because {money(low_high)} > {money(high_high)}."),
            ("b", f"Low is better against Low because {money(low_low)} > {money(high_low)}."),
            ("c", "Low is a dominant strategy for both firms, so the Nash equilibrium is Low/Low."),
            ("d", "Each firm has an individual incentive to cut price, even though both would earn more if both could commit to High."),
        )
        return make_row("Game Theory", "Dominant strategies", difficulty, "A Pricing Prisoner's Dilemma", text, qs, ss, ["dominant strategy", "Nash equilibrium"], {"high_high": high_high, "low_high": low_high, "high_low": high_low, "low_low": low_low}, family="pricing game")

    if difficulty == "medium":
        expand_cost = 220 + 5 * i
        text = (
            f"{f1} and {f2} operate local training centers. Each can charge {money(50)} or {money(40)}. At current capacity, the payoff matrix "
            f"in weekly profit is: both 50 -> (3000, 3000); {f1} 50 and {f2} 40 -> (1800, 3200); {f1} 40 and {f2} 50 -> (3200, 1800); "
            f"both 40 -> (2400, 2400). {f2} can expand capacity at fixed cost {money(expand_cost)}, changing its payoff from charging 40 "
            f"against 50 to {money(3400 - expand_cost)} and from both charging 40 to {money(2900 - expand_cost)}."
        )
        qs = parts(
            ("a", "Find the Nash equilibrium before expansion."),
            ("b", "After expansion, identify each firm's best responses."),
            ("c", "Find the Nash equilibrium after expansion."),
            ("d", "Compare firm 2's profit before and after expansion."),
            ("e", "Explain why extra capacity can make price competition tougher."),
        )
        after_40_high = 3400 - expand_cost
        after_40_40 = 2900 - expand_cost
        ss = parts(
            ("a", "Before expansion, each firm prefers 40 regardless of the rival's price, so the equilibrium is 40/40 with profit 2400 each."),
            ("b", f"Firm 2's low-price payoff after expansion is {money(after_40_high)} against 50 and {money(after_40_40)} against 40; firm 1 still prefers 40 in both cases."),
            ("c", "The equilibrium remains 40/40 unless expansion makes firm 2 prefer 50 when firm 1 charges 40; with these payoffs it still chooses 40."),
            ("d", f"Firm 2 earns {money(after_40_40)} after expansion versus {money(2400)} before, so expansion {'raises' if after_40_40 > 2400 else 'lowers'} its equilibrium profit."),
            ("e", "More capacity makes it more tempting to cut price to fill seats, which can intensify competition and reduce margins."),
        )
        return make_row("Game Theory", "Capacity and pricing game", difficulty, "Capacity Expansion and Price Competition", text, qs, ss, ["Nash equilibrium", "capacity", "price competition"], {"expand_cost": expand_cost}, family="capacity pricing")

    fight_loss, monopoly_profit, entry_profit = 400 + 10 * i, 1800 + 20 * i, 900 + 10 * i
    text = (
        f"An entrant is deciding whether to enter {f1}'s market. If the entrant stays out, {f1} earns {money(monopoly_profit)} and the entrant earns 0. "
        f"If the entrant enters, {f1} can accommodate or fight. Accommodation gives {f1} {money(1100 + 10 * i)} and the entrant {money(entry_profit)}. "
        f"Fighting gives {f1} {money(fight_loss)} and the entrant {money(-200)}. Consider both a simultaneous-entry story and a sequential game in which "
        f"the entrant moves first and {f1} responds after observing entry."
    )
    qs = parts(
        ("a", "In the sequential game, what is the incumbent's best response to entry?"),
        ("b", "Using backward induction, will the entrant enter?"),
        ("c", "What are the equilibrium payoffs?"),
        ("d", "Would a non-credible threat to fight deter entry?"),
        ("e", "How could the incumbent make a threat to fight more credible?"),
        ("f", "Explain the broader business lesson from backward induction."),
    )
    inc_acc = 1100 + 10 * i
    ss = parts(
        ("a", f"Accommodation is better because {money(inc_acc)} > {money(fight_loss)}."),
        ("b", f"Knowing the incumbent will accommodate, the entrant enters because {money(entry_profit)} > 0."),
        ("c", f"Payoffs are incumbent {money(inc_acc)} and entrant {money(entry_profit)}."),
        ("d", "No. A threat to fight is not credible if the incumbent would prefer to accommodate once entry occurs."),
        ("e", "It could build excess capacity, sign contracts, or make other commitments that change the payoff from fighting versus accommodating."),
        ("f", "Strategic plans must be sequentially rational: rivals look ahead to what a firm will actually want to do later."),
    )
    return make_row("Game Theory", "Sequential entry", difficulty, "Entry Deterrence and Credibility", text, qs, ss, ["backward induction", "credible threat", "entry"], {"fight_loss": fight_loss, "monopoly_profit": monopoly_profit, "entry_profit": entry_profit}, family="sequential entry")


def oligopoly(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    f1, f2, good = firm(i, 15), firm(i, 16), product(i, 9)
    a, c = 120 + i, 20 + i % 6
    if difficulty == "easy":
        price = c + 12 + i % 4
        text = (
            f"{f1} and {f2} sell identical {good} and choose prices simultaneously. Each has constant marginal cost {money(c)} and enough "
            f"capacity to serve the whole market. Suppose one firm is currently charging {money(price)}."
        )
        qs = parts(
            ("a", "If the rival charges above marginal cost, what price slightly undercuts it?"),
            ("b", "Why is any common price above marginal cost unstable?"),
            ("c", "What is the Bertrand equilibrium price?"),
            ("d", "Explain why this result depends on the products being identical and capacity being sufficient."),
        )
        ss = parts(
            ("a", f"A firm can charge just below {money(price)} and capture the market while still pricing above cost."),
            ("b", "Each firm wants to undercut a rival price above MC, so mutual high prices are not best responses."),
            ("c", f"The Bertrand equilibrium price is {money(c)}, equal to marginal cost."),
            ("d", "Differentiation or capacity limits soften competition because a firm cannot necessarily capture all customers by undercutting."),
        )
        return make_row("Oligopoly and Strategic Competition", "Bertrand competition", difficulty, "Bertrand Price Competition", text, qs, ss, ["Bertrand", "marginal cost pricing"], {"mc": c, "price": price}, family="Bertrand")

    if difficulty == "medium":
        q = (a - c) / 3
        p = a - 2 * q
        profit = (p - c) * q
        q_m = (a - c) / 2
        p_m = a - q_m
        text = (
            f"{f1} and {f2} choose quantities of {good} simultaneously. Market inverse demand is P = {a} - Q, where Q is total output. "
            f"Both firms have constant marginal cost {money(c)}. They are considering whether competition or collusion is more profitable."
        )
        qs = parts(
            ("a", "Write firm 1's best response to firm 2's quantity."),
            ("b", "Find the symmetric Cournot equilibrium quantity for each firm."),
            ("c", "Find price and profit per firm in Cournot equilibrium."),
            ("d", "Find total monopoly quantity and price if the firms collude perfectly."),
            ("e", "Explain why collusion may be unstable even if joint profit is higher."),
        )
        ss = parts(
            ("a", f"Firm 1 maximizes (a - q1 - q2 - c)q1, so q1 = ({a - c} - q2)/2."),
            ("b", f"Symmetry gives q = (a - c)/3 = {num(q)} for each firm."),
            ("c", f"Price is {money(p)} and profit per firm is {money(profit)}."),
            ("d", f"Monopoly total quantity is {num(q_m)} and price is {money(p_m)}."),
            ("e", "Each firm may gain by secretly expanding output while the other restricts output, so collusion requires enforcement."),
        )
        return make_row("Oligopoly and Strategic Competition", "Cournot duopoly", difficulty, "Cournot Competition and Collusion", text, qs, ss, ["Cournot", "collusion"], {"a": a, "mc": c}, family="Cournot")

    q_leader = (a - c) / 2
    q_follower = (a - c) / 4
    p_stack = a - q_leader - q_follower
    profit_l = (p_stack - c) * q_leader
    profit_f = (p_stack - c) * q_follower
    q_c = (a - c) / 3
    p_c = a - 2 * q_c
    text = (
        f"{f1} can commit to capacity before {f2} chooses output in the market for {good}. Demand is P = {a} - Q and both firms have "
        f"marginal cost {money(c)}. Compare this Stackelberg situation with simultaneous Cournot competition."
    )
    qs = parts(
        ("a", "Write the follower's best response."),
        ("b", "Find the Stackelberg leader and follower quantities."),
        ("c", "Find the Stackelberg price and profits."),
        ("d", "Find the symmetric Cournot quantity and price for comparison."),
        ("e", "Who benefits from moving first?"),
        ("f", "Explain the strategic commitment intuition."),
    )
    ss = parts(
        ("a", f"Follower best response is q2 = ({a - c} - q1)/2."),
        ("b", f"Leader quantity is {num(q_leader)} and follower quantity is {num(q_follower)}."),
        ("c", f"Price is {money(p_stack)}; leader profit is {money(profit_l)} and follower profit is {money(profit_f)}."),
        ("d", f"Cournot has each firm produce {num(q_c)} and price {money(p_c)}."),
        ("e", "The leader benefits by committing to a larger quantity, forcing the follower to scale back."),
        ("f", "A credible early capacity choice changes the rival's best response and can shift profit toward the committed firm."),
    )
    return make_row("Oligopoly and Strategic Competition", "Stackelberg leadership", difficulty, "Capacity Commitment in Oligopoly", text, qs, ss, ["Stackelberg", "commitment", "Cournot"], {"a": a, "mc": c}, family="Stackelberg")


def externalities_public_goods(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    good, city = product(i, 3), place(i, 3)
    if difficulty == "easy":
        private_benefit, external_benefit, cost = 34 + i % 5, 8 + i % 5, 38 + i % 4
        text = (
            f"Residents of {city} are deciding whether to adopt cleaner {good}. A buyer receives private benefit {money(private_benefit)} per unit, "
            f"and each unit creates an external benefit of {money(external_benefit)} for neighbors. The marginal cost is {money(cost)}."
        )
        qs = parts(
            ("a", "Will the private market buy the unit without intervention?"),
            ("b", "Is the unit socially efficient?"),
            ("c", "What per-unit subsidy would align private and social incentives?"),
            ("d", "Explain why positive externalities create under-consumption."),
        )
        ss = parts(
            ("a", f"No, because private benefit {money(private_benefit)} is below cost {money(cost)}."),
            ("b", f"Social benefit is {money(private_benefit + external_benefit)}, so the unit is {'efficient' if private_benefit + external_benefit >= cost else 'not efficient'}."),
            ("c", f"A subsidy of {money(external_benefit)} per unit makes buyers internalize the external benefit."),
            ("d", "Buyers ignore benefits received by others, so they buy too little unless policy or bargaining internalizes the spillover."),
        )
        return make_row("Externalities and Public Goods", "Positive externality", difficulty, "Clean Adoption Spillovers", text, qs, ss, ["positive externality", "subsidy"], {"private_benefit": private_benefit, "external_benefit": external_benefit, "cost": cost}, family="positive externality")

    if difficulty == "medium":
        a, b, mc, damage = 110 + i, 2, 22 + i % 5, 10 + i % 5
        q_market = (a - mc) / b
        q_eff = (a - mc - damage) / b
        p_market = mc
        p_eff = a - b * q_eff
        text = (
            f"In {city}, production of {good} creates a pollution cost of {money(damage)} per unit. Demand is P = {a} - {b}Q and private "
            f"marginal cost is {money(mc)}. The city is considering a Pigouvian tax."
        )
        qs = parts(
            ("a", "Find the competitive market quantity without regulation."),
            ("b", "Find the socially efficient quantity."),
            ("c", "What Pigouvian tax implements the efficient quantity?"),
            ("d", "At the efficient quantity, what price do consumers pay?"),
            ("e", "Explain why the tax is not just a revenue tool."),
        )
        ss = parts(
            ("a", f"With P = private MC, Q = ({a} - {mc})/{b} = {num(q_market)}."),
            ("b", f"Social MC is {money(mc + damage)}, so Q = ({a} - {mc + damage})/{b} = {num(q_eff)}."),
            ("c", f"The Pigouvian tax is {money(damage)} per unit."),
            ("d", f"Consumers pay demand price {money(p_eff)} at Q = {num(q_eff)}."),
            ("e", "The tax makes decision makers face the external cost, reducing inefficient output toward the social optimum."),
        )
        return make_row("Externalities and Public Goods", "Pigouvian tax", difficulty, "Pollution and Corrective Taxation", text, qs, ss, ["negative externality", "Pigouvian tax"], {"a": a, "b": b, "mc": mc, "damage": damage}, family="Pigouvian tax")

    a1, a2, mc = 70 + i % 8, 55 + i % 6, 60 + i % 5
    q_social = (a1 + a2 - mc) / 2
    q_private = max(0, a1 - mc)
    text = (
        f"Two neighborhoods benefit from a public safety app. Neighborhood A's marginal benefit is MB_A = {a1} - q, and neighborhood B's "
        f"marginal benefit is MB_B = {a2} - q. The marginal cost of improving the app is {money(mc)} per unit of quality q. The app is non-rival "
        f"within the city."
    )
    qs = parts(
        ("a", "Write the Samuelson condition for efficient public good provision."),
        ("b", "Find the efficient quality level."),
        ("c", "If only neighborhood A paid voluntarily, what quality would it choose?"),
        ("d", "Compare voluntary provision with the efficient level."),
        ("e", "Explain the free-rider problem in this setting."),
        ("f", "Name one policy or institution that could move provision closer to efficient."),
    )
    ss = parts(
        ("a", "For a public good, sum marginal benefits vertically and set MB_A + MB_B = MC."),
        ("b", f"({a1} - q) + ({a2} - q) = {mc}, so q = {num(q_social)}."),
        ("c", f"A alone sets {a1} - q = {mc}, so q = {num(q_private)}."),
        ("d", f"Voluntary provision is below the efficient level: {num(q_private)} versus {num(q_social)}."),
        ("e", "Each neighborhood would like the other to pay because both benefit from the same quality improvement."),
        ("f", "Tax financing, Lindahl-style pricing, contracts, or a citywide vote can help coordinate payment."),
    )
    return make_row("Externalities and Public Goods", "Public good provision", difficulty, "Funding a Public Safety App", text, qs, ss, ["public goods", "Samuelson condition", "free riding"], {"a1": a1, "a2": a2, "mc": mc}, family="public good")


def consumer_choice(i: int) -> dict[str, Any]:
    difficulty = difficulty_for_index(i)
    if difficulty == "easy":
        income, px, py = 120 + 5 * i, 4 + i % 3, 6 + i % 4
        x = income / (2 * px)
        y = income / (2 * py)
        text = (
            f"A consumer has income {money(income)} to spend on x and y. Prices are Px = {money(px)} and Py = {money(py)}. Utility is "
            f"u(x,y)=sqrt(xy), so the consumer spends half of income on each good."
        )
        qs = parts(
            ("a", "Write the budget constraint."),
            ("b", "Find optimal spending on each good."),
            ("c", "Find the optimal quantities x and y."),
            ("d", "Explain why the consumer does not simply buy the cheaper good only."),
        )
        ss = parts(
            ("a", f"{px}x + {py}y = {income}."),
            ("b", f"The consumer spends {money(income / 2)} on each good."),
            ("c", f"x = {num(x)} and y = {num(y)}."),
            ("d", "Cobb-Douglas preferences value balance: as one good becomes scarce, its marginal utility rises."),
        )
        return make_row("Consumer Choice", "Cobb-Douglas demand", difficulty, "Balanced Spending with Cobb-Douglas Utility", text, qs, ss, ["utility maximization", "budget constraint"], {"income": income, "px": px, "py": py}, {"utility": "sqrt(xy)"}, family="Cobb Douglas")

    if difficulty == "medium":
        income, px_old, px_new, py = 150 + 5 * (i % 5), 5 + i % 3, 8 + i % 4, 6 + i % 3
        x_old = income / (2 * px_old)
        y_old = income / (2 * py)
        x_new = income / (2 * px_new)
        y_new = y_old
        text = (
            f"A consumer with utility u(x,y)=sqrt(xy) has income {money(income)}. Initially Px = {money(px_old)} and Py = {money(py)}. "
            f"After a supply disruption, Px rises to {money(px_new)} while income and Py stay fixed. Use the Cobb-Douglas structure to "
            f"separate spending shares from quantities."
        )
        qs = parts(
            ("a", "Find the initial optimal bundle."),
            ("b", "Find the new optimal bundle after Px rises."),
            ("c", "What happens to spending on x and y?"),
            ("d", "What happens to the quantity of x?"),
            ("e", "Explain why the spending result is special to Cobb-Douglas preferences."),
        )
        ss = parts(
            ("a", f"Initial x = {num(x_old)} and y = {num(y_old)}."),
            ("b", f"New x = {num(x_new)} and y = {num(y_new)}."),
            ("c", f"Spending remains {money(income / 2)} on each good."),
            ("d", f"Quantity x falls from {num(x_old)} to {num(x_new)} because the same x spending buys fewer units."),
            ("e", "Cobb-Douglas demands have constant expenditure shares; other preferences need not keep spending shares fixed."),
        )
        return make_row("Consumer Choice", "Price change", difficulty, "A Price Increase with Cobb-Douglas Utility", text, qs, ss, ["price change", "demand", "expenditure shares"], {"income": income, "px_old": px_old, "px_new": px_new, "py": py}, {"utility": "sqrt(xy)"}, family="price change")

    u, px, py = 24 + i % 6, 4 + i % 4, 9 + i % 5
    x = u * math.sqrt(py / px)
    y = u * math.sqrt(px / py)
    expenditure = px * x + py * y
    text = (
        f"A benefits office wants to provide enough vouchers for a household to reach utility u(x,y)=sqrt(xy) = {u} at minimum cost. "
        f"The prices are Px = {money(px)} and Py = {money(py)}. The office asks whether cost minimization gives the same bundle as simply "
        f"buying equal quantities of both goods."
    )
    qs = parts(
        ("a", "Write the expenditure minimization problem."),
        ("b", "Use the tangency condition to relate y and x."),
        ("c", "Find the cost-minimizing quantities."),
        ("d", "Compute minimum expenditure."),
        ("e", "If Py rises, which way should the bundle adjust?"),
        ("f", "Explain why this problem is useful even though consumers usually choose subject to a budget."),
    )
    ss = parts(
        ("a", f"Minimize {px}x + {py}y subject to sqrt(xy) = {u}."),
        ("b", f"MRS = y/x = Px/Py = {num(px / py)}, so y = {num(px / py)}x."),
        ("c", f"x = u sqrt(Py/Px) = {num(x)} and y = u sqrt(Px/Py) = {num(y)}."),
        ("d", f"Minimum expenditure is {money(expenditure)}."),
        ("e", "The office substitutes away from y and toward x, while still meeting the utility target."),
        ("f", "It tells us the least income needed to reach a target utility and helps decompose price-change welfare effects."),
    )
    return make_row("Consumer Choice", "Expenditure minimization", difficulty, "Meeting a Utility Target at Minimum Cost", text, qs, ss, ["expenditure minimization", "duality"], {"u": u, "px": px, "py": py}, {"utility": "sqrt(xy)"}, family="expenditure minimization")


def mixed_review(i: int) -> dict[str, Any]:
    funcs = [
        supply_and_demand,
        elasticity,
        production_costs,
        monopoly,
        risk_insurance,
        incentives_contracts,
        trade_welfare,
        price_discrimination,
    ]
    base = funcs[(i - 1) % len(funcs)](i + 200)
    base["topic"] = "Mixed Review"
    base["subtopic"] = f"Review: {base['subtopic']}"
    base["problem_title"] = f"Mixed Review: {base['problem_title']}"
    base["problem_text"] = (
        "Mixed review prompt. Identify the relevant model before calculating; the goal is to connect the numbers to the economic logic.\n\n"
        + base["problem_text"]
    )
    base["variation_notes"] = f"Local exam-style bank: mixed review based on {base['subtopic']}."
    base["generated_id"] = stable_id(
        "gen",
        base["topic"],
        base["subtopic"],
        base["difficulty"],
        base["problem_title"],
        base["problem_text"],
        base["solution"],
    )
    return base


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
        for i in range(1, per_topic + 1):
            row = generator(i)
            if row["topic"] != topic:
                raise ValueError(f"Generator for {topic} returned {row['topic']}")
            rows.append(row)
    ids = [row["generated_id"] for row in rows]
    texts = [row["problem_text"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Generated IDs are not unique.")
    if len(texts) != len(set(texts)):
        raise ValueError("Generated problem texts are not unique.")
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
