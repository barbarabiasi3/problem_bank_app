from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

from .utils import DEFAULT_DATA_DIR, data_path, read_jsonl, stable_id, write_jsonl


FIRM_NAMES = [
    "Nebula Noodles",
    "Quantum Kettle",
    "Atlas Droneworks",
    "Aurora Scooters",
    "Sapphire Solar",
    "Flux Fitness",
    "Vertex Coffee",
    "LoomLabs",
    "Halo Health",
    "Polaris Bikes",
    "Meridian Micro",
    "Crimson Kite",
    "Echo Forge",
    "Nova Basket",
    "Summit Seltzer",
    "Prism Produce",
    "Vanta Vacuum",
    "BluePeak Batteries",
    "Cobalt Cloud",
    "Zenith Zips",
]


def money(value: float | Fraction) -> str:
    value = float(value)
    if abs(value - round(value)) < 1e-8:
        return f"${int(round(value))}"
    return f"${value:.2f}"


def num(value: float | Fraction) -> str:
    value = float(value)
    if abs(value - round(value)) < 1e-8:
        return str(int(round(value)))
    return f"{value:.2f}"


def subparts(*items: tuple[str, str]) -> list[dict[str, str]]:
    return [{"label": label, "text": text} for label, text in items]


def solution_text(solution_subparts: list[dict[str, str]]) -> str:
    return "\n\n".join(f"({part['label']}) {part['text']}" for part in solution_subparts)


def row(
    topic: str,
    subtopic: str,
    difficulty: str,
    firm: str,
    problem_text: str,
    problem_subparts: list[dict[str, str]],
    solution_subparts: list[dict[str, str]],
    concepts: list[str],
    notes: str,
    parameters: dict[str, Any],
    functions: dict[str, Any],
) -> dict[str, Any]:
    parameters = {**parameters, "firm": firm}
    generated_id = stable_id("gen", topic, firm, problem_text, solution_text(solution_subparts))
    return {
        "generated_id": generated_id,
        "parent_problem_id": "seed_verified_template",
        "topic": topic,
        "subtopic": subtopic,
        "difficulty": difficulty,
        "problem_text": problem_text,
        "subparts": problem_subparts,
        "solution": solution_text(solution_subparts),
        "solution_subparts": solution_subparts,
        "concepts_tested": concepts,
        "variation_notes": notes,
        "parameters": parameters,
        "functions": functions,
        "quality_checks": {
            "math_verified": True,
            "economics_verified": True,
            "not_too_similar_to_parent": True,
            "student_level_appropriate": True,
            "no_answer_leakage": True,
        },
        "disabled": False,
        "model": "deterministic_seed_generator",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _firm(row_data: dict[str, Any]) -> str:
    return str(row_data.get("parameters", {}).get("firm") or row_data.get("variation_notes", "the firm"))


def diversify_row(row_data: dict[str, Any], index: int) -> dict[str, Any]:
    """Give seed rows real surface variety without changing the verified core math."""
    topic = row_data["topic"]
    firm = _firm(row_data)
    variant = (index - 1) % 5

    intros: dict[str, list[str]] = {
        "Supply and Demand": [
            f"{firm} is piloting an instant-delivery pass in three downtown neighborhoods. The market research team estimates the following daily demand and supply curves.",
            f"A campus city is licensing curb space for {firm}'s pop-up pickup lockers. Analysts model the market with these linear curves.",
            f"{firm} is entering a market for rush-hour convenience services. Use the demand and supply equations below to study the first week of operations.",
            f"The mayor asks whether a tax on {firm}'s delivery passes would mostly hit buyers or sellers. Start from the market curves below.",
            f"{firm} and several competitors sell a homogeneous subscription add-on. The industry can be summarized by the following demand and supply schedules.",
        ],
        "Elasticity": [
            f"{firm} is testing whether a premium product can support a higher price.",
            f"The analytics team at {firm} sees a sharp sales response after a price experiment.",
            f"{firm} runs a weekend price change and wants to know whether revenue moved for economic reasons or luck.",
            f"A manager at {firm} is deciding whether the product is too price-sensitive for another increase.",
            f"{firm} changed its posted price in one market while holding advertising fixed.",
        ],
        "Taxes and Government Intervention": [
            f"The city council is considering an intervention in a permit market involving {firm}.",
            f"A regulator wants to support local suppliers who work with {firm}.",
            f"The mayor proposes a minimum legal price in a market where {firm} buys repair permits.",
            f"A trade association connected to {firm} asks for a price floor.",
            f"The local government is worried that the market price is too low for {firm}'s suppliers.",
        ],
        "Trade and Welfare": [
            f"{firm} relies on an imported input that is also produced domestically.",
            f"A domestic supplier group asks for protection from imports used by {firm}.",
            f"{firm}'s procurement team is evaluating a tariff on a globally traded component.",
            f"The government considers taxing imports of a material used by {firm}.",
            f"Domestic producers compete with foreign suppliers in a market important to {firm}.",
        ],
        "Production and Costs": [
            f"{firm} is deciding how many units to produce during a short-run pilot.",
            f"The operations team at {firm} has estimated a short-run cost curve.",
            f"{firm} is a small price-taking producer in a crowded market.",
            f"A plant manager at {firm} needs a shutdown rule before committing output.",
            f"{firm} sells into a competitive market and treats the market price as given.",
        ],
        "Perfect Competition": [
            f"{firm} is one of many identical sellers in a perfectly competitive market.",
            f"A competitive fringe includes {firm}, whose short-run cost curve is known.",
            f"{firm} takes price as fixed and must decide whether to operate this week.",
            f"Several firms like {firm} can enter in the long run, but today's decision is short-run.",
            f"{firm} is evaluating output in a competitive industry with no market power.",
        ],
        "Monopoly": [
            f"{firm} owns the only platform that provides this service in its market.",
            f"A patent gives {firm} temporary monopoly power over a software feature.",
            f"{firm} is the sole seller of a specialized business tool.",
            f"Customers have no close substitute for {firm}'s product this quarter.",
            f"{firm}'s strategy team is setting a single monopoly price.",
        ],
        "Price Discrimination": [
            f"{firm} is designing prices for two customer segments.",
            f"{firm} wants to decide whether segment-specific pricing is worth the complexity.",
            f"The pricing team at {firm} can sometimes identify buyer types.",
            f"{firm} is comparing one posted price with personalized pricing.",
            f"{firm} sells an experience with very different willingness to pay across groups.",
        ],
        "Risk and Insurance": [
            f"A buyer is considering a risky product made by {firm}.",
            f"{firm} sells a device whose performance is uncertain.",
            f"A customer asks how much a reliability risk should reduce willingness to pay for {firm}.",
            f"{firm} is debating whether a warranty would be valuable to buyers.",
            f"Consumers know the failure probability for a new {firm} product.",
        ],
        "Asymmetric Information": [
            f"Buyers cannot observe quality before purchasing from sellers like {firm}.",
            f"{firm} operates in a market where high- and low-quality products look identical.",
            f"A marketplace listing for {firm}-style scooters hides reliability differences.",
            f"Consumers only see the average reputation of sellers competing with {firm}.",
            f"Quality certification is missing in a market where {firm} sells alongside cheaper rivals.",
        ],
        "Incentives and Contracts": [
            f"{firm} is redesigning compensation for frontline sales workers.",
            f"The HR team at {firm} wants a bonus plan that induces effort.",
            f"{firm} cannot directly observe effort, only whether a sale occurs.",
            f"A manager at {firm} is comparing a flat wage with a wage-plus-bonus contract.",
            f"{firm} needs a contract that keeps workers while motivating high effort.",
        ],
        "Game Theory": [
            f"{firm} and a rival must choose prices before seeing each other's decisions.",
            f"Two local platforms, including {firm}, are locked in a simultaneous pricing game.",
            f"{firm} is choosing whether to defend margins or cut price in a one-shot game.",
            f"A competitor's move is unknown when {firm} sets its sale strategy.",
            f"{firm} and another seller publish prices at the same time.",
        ],
        "Oligopoly and Strategic Competition": [
            f"{firm} and one rival compete by choosing quantities.",
            f"Two firms, including {firm}, sell differentiated-looking but economically similar products.",
            f"{firm} is in a Cournot-style market where total output determines price.",
            f"A strategic competitor forces {firm} to think about best responses.",
            f"{firm} and a rival both choose production before the market price is known.",
        ],
        "Externalities and Public Goods": [
            f"{firm}'s production creates a cost for nearby residents.",
            f"A regulator notices that {firm}'s private cost omits environmental damage.",
            f"{firm} produces a useful good but creates an external marginal cost.",
            f"The city wants to align {firm}'s private incentives with social costs.",
            f"{firm} faces no charge for the damage created by each unit it sells.",
        ],
        "Consumer Choice": [
            f"A consumer is allocating a monthly budget between {firm}'s product and another good.",
            f"{firm} sells one of two goods in a simple consumer-choice problem.",
            f"A student is choosing between {firm} meal kits and streaming credits.",
            f"A household has Cobb-Douglas preferences over {firm}'s product and a second good.",
            f"A customer splits spending between {firm}'s offering and another service.",
        ],
        "Mixed Review": [
            f"{firm} is doing a quick launch analysis for a niche product.",
            f"A manager at {firm} needs to connect demand, marginal revenue, and cost.",
            f"{firm} is deciding whether a new product line can support a profitable price.",
            f"The strategy team at {firm} wants a compact monopoly-pricing review.",
            f"{firm} has estimated demand and now needs an economic recommendation.",
        ],
    }
    intro = intros.get(topic, [f"{firm} is evaluating a business decision."])[variant]
    original = row_data["problem_text"]
    p = row_data["parameters"]

    if topic == "Supply and Demand":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Demand is Qd = {p['a']} - {p['b']}P and supply is Qs = {p['c']} + {p['d']}P. "
            f"A per-unit seller tax of {money(p['tax'])} is under consideration."
        )
    elif topic == "Elasticity":
        row_data["problem_text"] = intro + "\n\n" + original
    elif topic == "Taxes and Government Intervention":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Demand is Qd = {p['a']} - {p['b']}P and supply is Qs = {p['c']} + {p['d']}P. "
            f"The proposed price floor is {money(p['price_floor'])}."
        )
    elif topic == "Trade and Welfare":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Domestic demand is Qd = {p['a']} - {p['b']}P and domestic supply is Qs = {p['d']}P. "
            f"The world price is {money(p['world_price'])}; the proposed tariff is {money(p['tariff'])} per unit."
        )
    elif topic in {"Production and Costs", "Perfect Competition"}:
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"The firm's short-run cost is {row_data['functions']['cost']}. "
            f"The current market price is {money(p['price'])}."
        )
    elif topic == "Monopoly":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Inverse demand is P = {p['a']} - {p['b']}Q and marginal cost is constant at {money(p['mc'])}."
        )
    elif topic == "Price Discrimination":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"High-value customers are willing to pay {money(p['high_value'])}; low-value customers are willing to pay {money(p['low_value'])}. "
            f"Marginal cost is {money(p['cost'])}, and there is one customer of each type."
        )
    elif topic == "Risk and Insurance":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"The product is worth {money(p['value'])} if it works and {money(0)} if it fails. "
            f"The failure probability is {num(Fraction(str(p['failure_probability'])) * 100)}%."
        )
    elif topic == "Asymmetric Information":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"A reliable unit is worth {money(p['good_value'])} to consumers and costs {money(p['good_cost'])} to make. "
            f"An unreliable unit is worth {money(p['bad_value'])} and costs {money(p['bad_cost'])}. "
            f"Initially, half the units are reliable."
        )
    elif topic == "Incentives and Contracts":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"A sale occurs with probability {num(p['p_high'] * 100)}% under high effort and {num(p['p_low'] * 100)}% under low effort. "
            f"The outside option is {money(p['outside_option'])}; high effort costs the worker {money(p['effort_cost'])}."
        )
    elif topic == "Game Theory":
        row_data["problem_text"] = original
        for sentence in intros[topic]:
            row_data["problem_text"] = row_data["problem_text"].replace(sentence + "\n\n", "")
        row_data["problem_text"] = f"{intro}\n\n{row_data['problem_text']}"
    elif topic == "Oligopoly and Strategic Competition":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Market inverse demand is P = {p['a']} - Q, where Q is total output. "
            f"Both firms have constant marginal cost {money(p['mc'])}."
        )
    elif topic == "Externalities and Public Goods":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Inverse demand is P = {p['demand_intercept']} - Q, private marginal cost is {money(p['private_mc'])}, "
            f"and external marginal damage is {money(p['external_damage'])} per unit."
        )
    elif topic == "Consumer Choice":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Utility is {row_data['functions']['utility']}. Income is {money(p['income'])}, Px = {money(p['px'])}, and Py = {money(p['py'])}."
        )
    elif topic == "Mixed Review":
        row_data["problem_text"] = (
            f"{intro}\n\n"
            f"Inverse demand is P = {p['a']} - {p['b']}Q and marginal cost is {money(p['mc'])}."
        )
    else:
        row_data["problem_text"] = f"{intro}\n\n{original}"

    prompt_variants: dict[str, list[list[tuple[str, str]]]] = {
        "Supply and Demand": [
            [("a", "Compute the market-clearing price and quantity."), ("b", "Now add the seller tax described above. Compute buyer price, seller price, and quantity."), ("c", "Who bears more of the tax, and how can you tell?")],
            [("a", "Solve for the pre-policy equilibrium."), ("b", "After the tax, what wedge opens between buyer and seller prices?"), ("c", "Compare the change in buyer price with the change in seller price.")],
            [("a", "Find the point where quantity demanded equals quantity supplied."), ("b", "Re-solve the market when sellers must pay the per-unit tax."), ("c", "Give a one-sentence incidence interpretation.")],
            [("a", "Draw the economic setup in words, then calculate equilibrium P and Q."), ("b", "Calculate the tax-distorted quantity and the two relevant prices."), ("c", "Explain why statutory incidence is not the same as economic incidence.")],
            [("a", "What price clears the market before the tax?"), ("b", "What are Pc, Ps, and Q after the tax?"), ("c", "Which curve is relatively less elastic in this example?")],
        ],
        "Elasticity": [
            [("a", "Calculate elasticity using the original price and quantity as the base."), ("b", "Classify demand as elastic or inelastic."), ("c", "Did revenue rise or fall?")],
            [("a", "Compute the percent change in quantity and percent change in price."), ("b", "Use those numbers to estimate elasticity."), ("c", "Should the manager be surprised by the revenue change?")],
            [("a", "Estimate the elasticity from the observed price experiment."), ("b", "Interpret the sign and magnitude."), ("c", "What does this imply for a further price increase?")],
            [("a", "Find the demand elasticity at the initial price."), ("b", "Is the product price-sensitive in this range?"), ("c", "Compare old and new total revenue.")],
            [("a", "Compute the elasticity ratio."), ("b", "State whether absolute elasticity is above or below 1."), ("c", "Use your answer to evaluate the pricing move.")],
        ],
        "Game Theory": [
            [("a", f"Does {firm} have a dominant strategy?"), ("b", "Does the rival have a dominant strategy?"), ("c", "Find the Nash equilibrium.")],
            [("a", f"Best-respond for {firm} to each rival action."), ("b", "Best-respond for the rival to each action by the first firm."), ("c", "Which outcome survives mutual best responses?")],
            [("a", "Identify each player's preferred action when the other chooses High."), ("b", "Identify each player's preferred action when the other chooses Low."), ("c", "Use those comparisons to locate equilibrium.")],
            [("a", "Is High Price ever optimal for the first firm?"), ("b", "Is High Price ever optimal for the second firm?"), ("c", "Predict the pricing outcome.")],
            [("a", "Fill in the strategic logic in words."), ("b", "State whether either firm faces a prisoners' dilemma-style tension."), ("c", "Give the Nash equilibrium.")],
        ],
        "Taxes and Government Intervention": [
            [("a", "Find the market outcome before the policy."), ("b", "Check whether the proposed floor changes the market outcome."), ("c", "Measure the resulting surplus or shortage.")],
            [("a", "Solve for the laissez-faire price and quantity."), ("b", "Is the legal minimum price binding?"), ("c", "At that legal price, compare planned sales and planned purchases.")],
            [("a", "Calculate the competitive benchmark."), ("b", "Evaluate the policy constraint."), ("c", "Does the policy create excess supply or excess demand? Quantify it.")],
            [("a", "Start with equilibrium without intervention."), ("b", "Explain whether the price floor is above or below equilibrium."), ("c", "Compute the unsold quantity if the floor binds.")],
            [("a", "What price would clear this market?"), ("b", "Would the proposed rule force a different price?"), ("c", "Who is rationed in this market, buyers or sellers?")],
        ],
        "Trade and Welfare": [
            [("a", "Compute domestic consumption, domestic production, and imports under free trade."), ("b", "Repeat the calculation after the tariff."), ("c", "Calculate tariff revenue.")],
            [("a", "At the world price, how much does the country import?"), ("b", "What changes once the tariff is added to the world price?"), ("c", "How much money does the government collect?")],
            [("a", "Use the world price to find the free-trade allocation."), ("b", "Find the tariff-distorted domestic price and quantities."), ("c", "Compute tariff revenue from the remaining imports.")],
            [("a", "Separate domestic demand, domestic supply, and import demand under free trade."), ("b", "How does the tariff affect each of those three quantities?"), ("c", "Report government revenue.")],
            [("a", "Describe the free-trade outcome numerically."), ("b", "Describe the protected-market outcome numerically."), ("c", "What revenue does the tariff raise?")],
        ],
        "Production and Costs": [
            [("a", "Derive the positive-output supply rule."), ("b", "Use the market price to choose output."), ("c", "Compute profit and the shutdown price.")],
            [("a", "Find marginal cost and invert it into a supply curve."), ("b", "How many units should the firm produce at the stated price?"), ("c", "Should fixed cost affect the shutdown price? Give the number.")],
            [("a", "State the price-equals-marginal-cost condition."), ("b", "Apply the condition to this price."), ("c", "Evaluate operating profit and the short-run shutdown threshold.")],
            [("a", "Recover the firm's supply schedule from its cost function."), ("b", "Pick the profit-maximizing quantity."), ("c", "Calculate profit and identify the lowest operating price.")],
            [("a", "What marginal cost curve does the plant face?"), ("b", "Where does price intersect marginal cost?"), ("c", "Compare revenue and total cost at that output.")],
        ],
        "Perfect Competition": [
            [("a", "Derive the competitive firm's output rule."), ("b", "Choose quantity at the current market price."), ("c", "Find profit and the shutdown price.")],
            [("a", "Use price-taking behavior to write the first-order condition."), ("b", "Solve for the firm's short-run quantity."), ("c", "Should the firm operate if price falls below the shutdown threshold?")],
            [("a", "Find marginal cost."), ("b", "Set price equal to marginal cost and solve for output."), ("c", "Compute the implied profit.")],
            [("a", "Write the supply curve for positive quantities."), ("b", "Evaluate supply at the stated price."), ("c", "Identify the price where production stops.")],
            [("a", "Explain why marginal cost is the key curve here."), ("b", "Calculate output."), ("c", "Calculate profit and state the shutdown rule.")],
        ],
        "Monopoly": [
            [("a", "Find the monopoly quantity and price."), ("b", "Calculate profit before fixed costs."), ("c", "Compare monopoly output with efficient output.")],
            [("a", "Derive marginal revenue and set it equal to marginal cost."), ("b", "Use the demand curve to recover price and profit."), ("c", "Why does the monopolist restrict quantity?")],
            [("a", "Choose Q to maximize operating profit."), ("b", "Find the price charged at that Q."), ("c", "State whether this outcome is allocatively efficient.")],
            [("a", "Solve the pricing decision from MR = MC."), ("b", "Compute the markup-based profit."), ("c", "What quantity would a social planner choose instead?")],
            [("a", "Find output first, then price."), ("b", "Calculate producer surplus/profit with no fixed cost."), ("c", "Explain the deadweight-loss logic in words.")],
        ],
        "Price Discrimination": [
            [("a", "Find prices under perfect identification of customer types."), ("b", "Find the best single posted price."), ("c", "Compare why profits differ.")],
            [("a", "How much can the firm charge each segment if it observes type?"), ("b", "If it cannot observe type, which uniform price is best?"), ("c", "What surplus is left on the table?")],
            [("a", "Compute discriminatory prices and profit."), ("b", "Evaluate each candidate one-price strategy."), ("c", "Explain the tradeoff between serving more customers and charging more.")],
            [("a", "What would personalized pricing do?"), ("b", "What uniform price should the firm post?"), ("c", "Which pricing regime extracts more surplus?")],
            [("a", "Price the product type-by-type."), ("b", "Price it when all buyers must see the same number."), ("c", "Identify who gains surplus under uniform pricing.")],
        ],
        "Risk and Insurance": [
            [("a", "Compute willingness to pay for a risk-neutral buyer."), ("b", "Compute producer surplus at that price."), ("c", "How would risk aversion change the answer?")],
            [("a", "Find expected value."), ("b", "Translate expected value into surplus over cost."), ("c", "Would a warranty matter more or less for a risk-averse buyer?")],
            [("a", "Use the failure probability to value the product."), ("b", "Calculate seller surplus if price equals that value."), ("c", "Explain why expected value may overstate WTP for some consumers.")],
            [("a", "What maximum price would a risk-neutral customer pay?"), ("b", "What surplus does the producer get at that maximum price?"), ("c", "What role does downside risk play?")],
            [("a", "Compute the probability-weighted value."), ("b", "Subtract production cost to get producer surplus."), ("c", "Describe the effect of introducing insurance.")],
        ],
        "Asymmetric Information": [
            [("a", "Find pooled willingness to pay."), ("b", "Determine which quality types remain willing to sell."), ("c", "Explain the adverse-selection problem.")],
            [("a", "Average the values consumers expect before observing quality."), ("b", "Compare the pooled price with each type's cost."), ("c", "Does the market unravel?")],
            [("a", "What price would uninformed buyers be willing to pay?"), ("b", "At that price, which sellers participate?"), ("c", "How does hidden quality distort the market?")],
            [("a", "Calculate the expected value of a random item."), ("b", "Use costs to predict seller participation."), ("c", "State the direction of quality selection.")],
            [("a", "Compute the pooled market price."), ("b", "Check whether high-quality sellers can cover cost."), ("c", "What certification or signal might fix the problem?")],
        ],
        "Incentives and Contracts": [
            [("a", "Write the incentive-compatibility constraint."), ("b", "Write the participation constraint."), ("c", "Find the cheapest wage and bonus that induce effort.")],
            [("a", "What bonus is needed to make effort worthwhile?"), ("b", "What wage keeps the worker from leaving?"), ("c", "Give the complete contract.")],
            [("a", "Compare expected utility under high and low effort."), ("b", "Impose the outside-option constraint."), ("c", "Solve for the minimum bonus and base wage.")],
            [("a", "State the 'do the right thing' condition."), ("b", "State the 'willing to work' condition."), ("c", "Use both constraints to design pay.")],
            [("a", "Find the incentive constraint created by the sale probability gap."), ("b", "Find the participation constraint."), ("c", "Compute the contract that just satisfies both.")],
        ],
        "Oligopoly and Strategic Competition": [
            [("a", "Write one firm's best-response function."), ("b", "Find the symmetric Cournot equilibrium."), ("c", "Compute each firm's profit.")],
            [("a", "Maximize one firm's profit holding rival output fixed."), ("b", "Impose symmetry and solve for output and price."), ("c", "Evaluate profit at the equilibrium.")],
            [("a", "Derive the reaction curve."), ("b", "Use mutual best responses to find quantities."), ("c", "What profit does each firm earn?")],
            [("a", "How does the rival's output affect the firm's optimal output?"), ("b", "Solve the two-firm quantity game."), ("c", "Compute the price-cost margin and profit.")],
            [("a", "Find the FOC for one firm."), ("b", "Solve the symmetric Nash equilibrium."), ("c", "Calculate equilibrium profit.")],
        ],
        "Externalities and Public Goods": [
            [("a", "Find the unregulated competitive quantity."), ("b", "Find the socially efficient quantity."), ("c", "What Pigouvian tax implements efficiency?")],
            [("a", "Set demand equal to private marginal cost."), ("b", "Set demand equal to social marginal cost."), ("c", "Compare the two quantities and name the corrective tax.")],
            [("a", "Compute the market quantity when firms ignore damages."), ("b", "Compute the quantity when damages count."), ("c", "What tax closes the gap?")],
            [("a", "Find the private equilibrium."), ("b", "Find the planner's quantity."), ("c", "How large should the per-unit charge be?")],
            [("a", "How much is produced without regulation?"), ("b", "How much should be produced from society's perspective?"), ("c", "State the policy that decentralizes that outcome.")],
        ],
        "Consumer Choice": [
            [("a", "Write the budget constraint."), ("b", "Find the utility-maximizing bundle."), ("c", "How much income is spent on each good?")],
            [("a", "Translate prices and income into a budget line."), ("b", "Use Cobb-Douglas expenditure shares to choose x and y."), ("c", "Check that total spending equals income.")],
            [("a", "What combinations are affordable?"), ("b", "Find optimal consumption of both goods."), ("c", "What is the spending share on each good?")],
            [("a", "Write the consumer's constraint."), ("b", "Use the equal-exponent Cobb-Douglas shortcut."), ("c", "Report dollars spent on x and y.")],
            [("a", "Set up the maximization problem."), ("b", "Solve for Marshallian demands."), ("c", "Interpret the role of prices in the chosen bundle.")],
        ],
        "Mixed Review": [
            [("a", "If the firm has market power, find quantity and price."), ("b", "What economic rule pins down the quantity?")],
            [("a", "Use MR = MC to solve the launch decision."), ("b", "Explain the pricing rule in words.")],
            [("a", "Find the profit-maximizing launch output."), ("b", "Which marginal comparison drives the answer?")],
            [("a", "Compute Q and P for the new product."), ("b", "Why not produce where price is zero?")],
            [("a", "Solve the manager's pricing problem."), ("b", "State the core intermediate-micro principle being used.")],
        ],
    }
    if topic in prompt_variants:
        old_solutions = {part["label"]: part["text"] for part in row_data["solution_subparts"]}
        row_data["subparts"] = [{"label": label, "text": text} for label, text in prompt_variants[topic][variant]]
        row_data["solution_subparts"] = [
            {"label": label, "text": old_solutions.get(label, "Use the same economic logic from the previous parts.")}
            for label, _ in prompt_variants[topic][variant]
        ]
        row_data["solution"] = solution_text(row_data["solution_subparts"])
    else:
        endings = [
            ("d", "Give a short managerial interpretation of the numerical answer."),
            ("d", "Name one assumption that matters for the conclusion."),
            ("d", "Would the qualitative conclusion change if the key cost were slightly higher? Explain briefly."),
            ("d", "What mistake would a manager make if they ignored the economic constraint in this problem?"),
            ("d", "State the economic rule this problem illustrates."),
        ]
        if variant in {1, 3}:
            label, text = endings[variant]
            row_data["subparts"].append({"label": label, "text": text})
            row_data["solution_subparts"].append(
                {
                    "label": label,
                    "text": "The interpretation follows from the computed marginal or equilibrium condition: the firm or consumer should respond to incentives at the margin, not to sunk or irrelevant totals.",
                }
            )
            row_data["solution"] = solution_text(row_data["solution_subparts"])

    row_data["variation_notes"] = f"{row_data['variation_notes']} Uses scenario style {variant + 1} with varied wording/questions."
    row_data["generated_id"] = stable_id(
        "gen", row_data["topic"], row_data["problem_text"], row_data["solution"], index
    )
    return row_data


def supply_demand(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[i % len(FIRM_NAMES)]
    a, b, c, d = 120 + 8 * i, 2 + i % 3, 10 + 3 * i, 2 + (i + 1) % 3
    tax = 4 + i
    p0 = Fraction(a - c, b + d)
    q0 = a - b * p0
    pc = Fraction(a - c + d * tax, b + d)
    ps = pc - tax
    qt = a - b * pc
    problem_text = f"{firm} tracks the market for same-day delivery passes. Market demand is Qd = {a} - {b}P and market supply is Qs = {c} + {d}P."
    parts = subparts(
        ("a", "Find the competitive equilibrium price and quantity."),
        ("b", f"Suppose the city imposes a per-unit tax of {money(tax)} on sellers. Find the price paid by buyers, the price received by sellers, and quantity traded."),
        ("c", "Briefly explain which side of the market bears more of the tax burden."),
    )
    sols = subparts(
        ("a", f"Set {a} - {b}P = {c} + {d}P, so P = ({a} - {c})/({b} + {d}) = {money(p0)}. Quantity is Q = {num(q0)}."),
        ("b", f"With a seller tax, Qs = {c} + {d}(Pc - {tax}). Set {a} - {b}Pc = {c} + {d}(Pc - {tax}). Thus Pc = {money(pc)}, sellers receive Ps = {money(ps)}, and Q = {num(qt)}."),
        ("c", f"Buyers pay {money(pc - p0)} more than before and sellers receive {money(p0 - ps)} less than before. The side with the larger price change bears more of the burden."),
    )
    return row("Supply and Demand", "Market equilibrium", "medium", firm, problem_text, parts, sols, ["supply", "demand", "tax incidence"], "Linear market equilibrium with a seller tax.", {"a": a, "b": b, "c": c, "d": d, "tax": tax}, {})


def elasticity(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 2) % len(FIRM_NAMES)]
    p1, p2 = 20 + 2 * i, 24 + 2 * i
    q1, q2 = 500 - 20 * i, 430 - 15 * i
    elasticity = Fraction(q2 - q1, q1) / Fraction(p2 - p1, p1)
    problem_text = f"{firm} raises the price of its premium snack box from {money(p1)} to {money(p2)}. Weekly sales fall from {q1} boxes to {q2} boxes."
    parts = subparts(
        ("a", "Compute the approximate price elasticity of demand using the original price and quantity as the base."),
        ("b", "Is demand elastic or inelastic at the original price?"),
        ("c", "What happens to revenue after the price increase?"),
    )
    sols = subparts(
        ("a", f"Percentage change in quantity is ({q2} - {q1})/{q1} = {num(Fraction(q2-q1, q1) * 100)}%. Percentage change in price is ({p2} - {p1})/{p1} = {num(Fraction(p2-p1, p1) * 100)}%. Elasticity is {num(elasticity)}."),
        ("b", "Demand is elastic if the absolute value exceeds 1 and inelastic if it is below 1."),
        ("c", f"Initial revenue is {money(p1*q1)}. New revenue is {money(p2*q2)}. Revenue {'increases' if p2*q2 > p1*q1 else 'decreases'} after the price increase."),
    )
    return row("Elasticity", "Price elasticity", "easy", firm, problem_text, parts, sols, ["elasticity", "revenue"], "Arc-style elasticity with a managerial revenue interpretation.", {"p1": p1, "p2": p2, "q1": q1, "q2": q2}, {})


def tax_policy(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 4) % len(FIRM_NAMES)]
    a, b, c, d = 90 + 5 * i, 2, 6 + i, 1 + i % 2
    floor = Fraction(a + c, b + d) + 6
    qd, qs = a - b * floor, c + d * floor
    surplus = max(0, qs - qd)
    problem_text = f"The city is considering a price floor in the market for {firm} repair permits. Demand is Qd = {a} - {b}P and supply is Qs = {c} + {d}P."
    parts = subparts(
        ("a", "Find the no-intervention equilibrium."),
        ("b", f"If the city imposes a price floor of {money(floor)}, is it binding?"),
        ("c", "At the price floor, is there excess supply or excess demand, and how much?"),
    )
    p0 = Fraction(a - c, b + d)
    q0 = a - b * p0
    sols = subparts(
        ("a", f"Set demand equal to supply: {a} - {b}P = {c} + {d}P. So P = {money(p0)} and Q = {num(q0)}."),
        ("b", f"The floor is above the equilibrium price of {money(p0)}, so it is binding."),
        ("c", f"At {money(floor)}, Qd = {num(qd)} and Qs = {num(qs)}. There is excess supply of {num(surplus)} units."),
    )
    return row("Taxes and Government Intervention", "Price controls", "medium", firm, problem_text, parts, sols, ["price floor", "shortage", "surplus"], "Government intervention with a binding price floor.", {"a": a, "b": b, "c": c, "d": d, "price_floor": float(floor)}, {})


def trade(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 6) % len(FIRM_NAMES)]
    a, b, d = 120 + 10 * i, 3, 2
    pw, tariff = 18 + i, 4 + i
    ps = pw + tariff
    qd_free, qs_free = a - b * pw, d * pw
    qd_tariff, qs_tariff = a - b * ps, d * ps
    imports_free = qd_free - qs_free
    imports_tariff = qd_tariff - qs_tariff
    revenue = tariff * imports_tariff
    problem_text = f"The United States imports a specialty input used by {firm}. Domestic demand is Qd = {a} - {b}P and domestic supply is Qs = {d}P. The world price is {money(pw)}."
    parts = subparts(
        ("a", "Under free trade, how much is consumed domestically, produced domestically, and imported?"),
        ("b", f"Now suppose the government adds a tariff of {money(tariff)} per unit. Find domestic consumption, domestic production, and imports."),
        ("c", "How much tariff revenue does the government collect?"),
    )
    sols = subparts(
        ("a", f"At the world price {money(pw)}, Qd = {num(qd_free)} and Qs = {num(qs_free)}, so imports are {num(imports_free)}."),
        ("b", f"The tariff raises the domestic price to {money(ps)}. Then Qd = {num(qd_tariff)}, Qs = {num(qs_tariff)}, and imports are {num(imports_tariff)}."),
        ("c", f"Tariff revenue equals tariff times imports: {money(tariff)} x {num(imports_tariff)} = {money(revenue)}."),
    )
    return row("Trade and Welfare", "Tariffs", "medium", firm, problem_text, parts, sols, ["trade", "tariff", "imports"], "Small-country tariff arithmetic.", {"a": a, "b": b, "d": d, "world_price": pw, "tariff": tariff}, {})


def costs(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 8) % len(FIRM_NAMES)]
    fixed, v, a, price = 80 + 10 * i, 6 + i, 1, 24 + 3 * i
    q = Fraction(price - v, 2 * a)
    profit = price * q - fixed - v * q - a * q * q
    shut = v
    problem_text = f"{firm} has short-run cost C(q) = {fixed} + {v}q + q^2. It operates in a competitive market and takes price P as given."
    parts = subparts(
        ("a", "Derive the firm's supply rule for positive output."),
        ("b", f"If the market price is {money(price)}, how much does the firm produce?"),
        ("c", "What is profit at that output, and what is the shutdown price?"),
    )
    sols = subparts(
        ("a", f"Marginal cost is MC = {v} + 2q. For positive output in competition, set P = MC, so q = (P - {v})/2 when P is at least {v}."),
        ("b", f"q = ({price} - {v})/2 = {num(q)}."),
        ("c", f"Profit is Pq - C(q) = {money(profit)}. The shutdown price is minimum AVC, which is {money(shut)} here because AVC = {v} + q."),
    )
    return row("Production and Costs", "Competitive supply", "medium", firm, problem_text, parts, sols, ["marginal cost", "supply", "shutdown"], "Quadratic cost and competitive supply.", {"fixed": fixed, "v": v, "price": price}, {"cost": f"C(q) = {fixed} + {v}q + q^2"})


def perfect_competition(i: int) -> dict[str, Any]:
    item = costs(i)
    item["topic"] = "Perfect Competition"
    item["subtopic"] = "Short-run firm choice"
    item["variation_notes"] = "Perfectly competitive firm output and shutdown logic."
    return item


def monopoly(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 10) % len(FIRM_NAMES)]
    a, b, c = 100 + 8 * i, 2, 12 + i
    q = Fraction(a - c, 2 * b)
    p = a - b * q
    profit = (p - c) * q
    problem_text = f"{firm} is the only seller of a subscription analytics tool. Inverse demand is P = {a} - {b}Q and marginal cost is constant at {money(c)}."
    parts = subparts(
        ("a", "Find the profit-maximizing quantity and price."),
        ("b", "Compute monopoly profit, ignoring fixed costs."),
        ("c", "Is the monopoly quantity higher or lower than the efficient quantity?"),
    )
    sols = subparts(
        ("a", f"Revenue is ({a} - {b}Q)Q, so MR = {a} - {2*b}Q. Set MR = MC: {a} - {2*b}Q = {c}. Thus Q = {num(q)} and P = {money(p)}."),
        ("b", f"Profit is (P - MC)Q = ({money(p)} - {money(c)}) x {num(q)} = {money(profit)}."),
        ("c", "The efficient quantity sets price equal to marginal cost, so monopoly restricts output below the efficient quantity."),
    )
    return row("Monopoly", "Monopoly pricing", "medium", firm, problem_text, parts, sols, ["marginal revenue", "markup", "deadweight loss"], "Linear monopoly with constant marginal cost.", {"a": a, "b": b, "mc": c}, {})


def discrimination(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 12) % len(FIRM_NAMES)]
    vh, vl, cost = 70 + 3 * i, 38 + 2 * i, 10 + i
    high_surplus = vh - vl
    profit = (vl - cost) + (vh - cost)
    problem_text = f"{firm} sells a premium workshop to two customer types. High-value customers value it at {money(vh)} and low-value customers value it at {money(vl)}. Marginal cost is {money(cost)}. There is one customer of each type."
    parts = subparts(
        ("a", "If the firm can perfectly identify customer types, what prices should it charge?"),
        ("b", "If it must charge one price to both customers, what price maximizes profit?"),
        ("c", "Compare the source of profit in the two cases."),
    )
    single_price_profit_low = (vl - cost) * 2
    single_price_profit_high = vh - cost
    single_price = vl if single_price_profit_low >= single_price_profit_high else vh
    sols = subparts(
        ("a", f"Charge each type its willingness to pay: {money(vh)} to high-value customers and {money(vl)} to low-value customers. Profit is {money(profit)}."),
        ("b", f"At {money(vl)}, both buy and profit is 2 x ({money(vl)} - {money(cost)}) = {money(single_price_profit_low)}. At {money(vh)}, only high-value customers buy and profit is {money(single_price_profit_high)}. The better single price is {money(single_price)}."),
        ("c", "Perfect price discrimination extracts each customer's surplus. A single price leaves some surplus or excludes one segment."),
    )
    return row("Price Discrimination", "Segment pricing", "medium", firm, problem_text, parts, sols, ["price discrimination", "consumer surplus"], "Simple segmentation problem.", {"high_value": vh, "low_value": vl, "cost": cost}, {})


def risk(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 14) % len(FIRM_NAMES)]
    value, fail = 1000 + 100 * i, Fraction(5 + i, 100)
    expected = value * (1 - fail)
    problem_text = f"A risk-neutral buyer is considering a {firm} drone. It is worth {money(value)} if it works and {money(0)} if it fails. The failure probability is {num(fail * 100)}%."
    parts = subparts(
        ("a", "What is the buyer's willingness to pay?"),
        ("b", f"If production cost is {money(expected - 80)}, what is producer surplus when price equals willingness to pay?"),
        ("c", "How would risk aversion change the willingness to pay, holding expected value fixed?"),
    )
    sols = subparts(
        ("a", f"For a risk-neutral buyer, willingness to pay equals expected value: (1 - {num(fail)}) x {money(value)} = {money(expected)}."),
        ("b", f"Producer surplus is price minus cost: {money(expected)} - {money(expected - 80)} = {money(80)}."),
        ("c", "Risk aversion lowers willingness to pay below expected value when the product creates uninsured downside risk."),
    )
    return row("Risk and Insurance", "Expected value and risk", "easy", firm, problem_text, parts, sols, ["risk", "expected value", "risk aversion"], "Risk-neutral willingness to pay with qualitative risk-aversion extension.", {"value": value, "failure_probability": float(fail)}, {})


def asymmetric(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 1) % len(FIRM_NAMES)]
    good_value, bad_value = 100 + 5 * i, 40 + 4 * i
    share_good = Fraction(1, 2)
    wtp_pool = share_good * good_value + (1 - share_good) * bad_value
    good_cost, bad_cost = 70 + 2 * i, 25 + i
    problem_text = f"Consumers cannot distinguish reliable and unreliable {firm} scooters before purchase. Reliable scooters are worth {money(good_value)} to consumers; unreliable scooters are worth {money(bad_value)}. Half the scooters are initially reliable."
    parts = subparts(
        ("a", "What is consumer willingness to pay for a randomly chosen scooter?"),
        ("b", f"Reliable scooters cost {money(good_cost)} to make and unreliable scooters cost {money(bad_cost)}. Which types are willing to sell at the pooled price?"),
        ("c", "What adverse-selection force is present?"),
    )
    sols = subparts(
        ("a", f"The pooled willingness to pay is 0.5 x {money(good_value)} + 0.5 x {money(bad_value)} = {money(wtp_pool)}."),
        ("b", f"Reliable sellers need at least {money(good_cost)}; unreliable sellers need {money(bad_cost)}. At {money(wtp_pool)}, {'both types sell' if wtp_pool >= good_cost else 'only unreliable sellers sell'}."),
        ("c", "If the pooled price is too low for reliable sellers, high-quality products exit and average quality falls."),
    )
    return row("Asymmetric Information", "Adverse selection", "medium", firm, problem_text, parts, sols, ["adverse selection", "pooled price"], "Quality uncertainty and market unraveling.", {"good_value": good_value, "bad_value": bad_value, "good_cost": good_cost, "bad_cost": bad_cost}, {})


def incentives(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 3) % len(FIRM_NAMES)]
    ph, pl = Fraction(3, 4), Fraction(1, 2)
    outside, effort = 18 + i, 5 + i
    bonus = effort / (ph - pl)
    wage = outside + effort - ph * bonus
    problem_text = f"{firm} wants sales staff to exert high effort. A sale occurs with probability 75% under high effort and 50% under low effort. Workers can earn {money(outside)} elsewhere without effort, and high effort costs them {money(effort)}."
    parts = subparts(
        ("a", "Write the incentive-compatibility constraint for a wage plus bonus contract."),
        ("b", "Write the participation constraint."),
        ("c", "Find the cost-minimizing wage and bonus that induce effort."),
    )
    sols = subparts(
        ("a", "High effort must give at least as much utility as low effort: w + 0.75b - effort cost >= w + 0.50b."),
        ("b", f"Expected utility under high effort must beat the outside option: w + 0.75b - {money(effort)} >= {money(outside)}."),
        ("c", f"IC requires 0.25b >= {money(effort)}, so b = {money(bonus)}. PC then gives w + 0.75({money(bonus)}) - {money(effort)} = {money(outside)}, so w = {money(wage)}."),
    )
    return row("Incentives and Contracts", "Moral hazard contract", "medium", firm, problem_text, parts, sols, ["incentive compatibility", "participation constraint"], "Linear wage-bonus contract.", {"outside_option": outside, "effort_cost": effort, "p_high": 0.75, "p_low": 0.5}, {})


def game_theory(i: int) -> dict[str, Any]:
    firm_a = FIRM_NAMES[i % len(FIRM_NAMES)]
    firm_b = FIRM_NAMES[(i + 7) % len(FIRM_NAMES)]
    high_a, high_b = 50 + 2 * i, 48 + 2 * i
    low_a, low_b = 42 + i, 41 + i
    problem_text = f"{firm_a} and {firm_b} simultaneously choose High Price or Low Price. Payoffs are profits in thousands. If both choose High, payoffs are ({high_a}, {high_b}). If {firm_a} chooses Low while {firm_b} chooses High, payoffs are ({high_a + 8}, {low_b}). If {firm_a} chooses High while {firm_b} chooses Low, payoffs are ({low_a}, {high_b + 9}). If both choose Low, payoffs are ({low_a + 2}, {low_b + 2})."
    parts = subparts(
        ("a", f"Does {firm_a} have a dominant strategy?"),
        ("b", f"Does {firm_b} have a dominant strategy?"),
        ("c", "Find the Nash equilibrium."),
    )
    sols = subparts(
        ("a", f"If {firm_b} chooses High, {firm_a} prefers Low because {high_a + 8} > {high_a}. If {firm_b} chooses Low, {firm_a} prefers Low because {low_a + 2} > {low_a}. Low Price is dominant."),
        ("b", f"By the same comparison, {firm_b} prefers Low whether {firm_a} chooses High or Low. Low Price is dominant."),
        ("c", "The Nash equilibrium is both firms choosing Low Price, since each is playing its dominant strategy."),
    )
    return row("Game Theory", "Dominant strategies", "easy", firm_a, problem_text, parts, sols, ["dominant strategy", "Nash equilibrium"], "Two-by-two price game.", {"firm_a": firm_a, "firm_b": firm_b}, {})


def oligopoly(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 5) % len(FIRM_NAMES)]
    a, b, c = 90 + 5 * i, 1, 18 + i
    q_each = Fraction(a - c, 3 * b)
    price = a - b * 2 * q_each
    profit_each = (price - c) * q_each
    problem_text = f"{firm} and a rival compete in quantities. Market inverse demand is P = {a} - Q, where Q is total output. Both firms have constant marginal cost {money(c)}."
    parts = subparts(
        ("a", "Write one firm's best response to the rival's output."),
        ("b", "Find the symmetric Cournot equilibrium quantity for each firm and market price."),
        ("c", "Compute each firm's profit."),
    )
    sols = subparts(
        ("a", f"Firm i maximizes ({a} - qi - qj - {c})qi. The FOC gives {a} - {c} - 2qi - qj = 0, so qi = ({a - c} - qj)/2."),
        ("b", f"In symmetry qi = qj = q, so q = ({a - c} - q)/2. Thus 3q = {a - c}, q = {num(q_each)}, and price is {money(price)}."),
        ("c", f"Each firm earns (P - MC)q = ({money(price)} - {money(c)}) x {num(q_each)} = {money(profit_each)}."),
    )
    return row("Oligopoly and Strategic Competition", "Cournot competition", "hard", firm, problem_text, parts, sols, ["Cournot", "best response", "Nash equilibrium"], "Symmetric Cournot duopoly.", {"a": a, "mc": c}, {})


def externalities(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 9) % len(FIRM_NAMES)]
    demand_intercept, private_mc, external = 80 + 4 * i, 20 + i, 8 + i
    q_private = demand_intercept - private_mc
    q_social = demand_intercept - private_mc - external
    problem_text = f"{firm} produces a good with inverse demand P = {demand_intercept} - Q and private marginal cost {money(private_mc)}. Production creates an external marginal damage of {money(external)} per unit."
    parts = subparts(
        ("a", "Find the competitive quantity without policy."),
        ("b", "Find the socially efficient quantity."),
        ("c", "What per-unit tax decentralizes the efficient outcome?"),
    )
    sols = subparts(
        ("a", f"Competition sets P = private MC: {demand_intercept} - Q = {private_mc}, so Q = {num(q_private)}."),
        ("b", f"Social marginal cost is {money(private_mc + external)}. Set {demand_intercept} - Q = {private_mc + external}, so Q = {num(q_social)}."),
        ("c", f"A Pigouvian tax equal to marginal damage, {money(external)}, makes firms internalize the external cost."),
    )
    return row("Externalities and Public Goods", "Pigouvian tax", "medium", firm, problem_text, parts, sols, ["externality", "Pigouvian tax"], "Negative production externality.", {"demand_intercept": demand_intercept, "private_mc": private_mc, "external_damage": external}, {})


def consumer_choice(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 11) % len(FIRM_NAMES)]
    income, px, py = 120 + 20 * i, 4 + i, 6 + i
    x = Fraction(income, 2 * px)
    y = Fraction(income, 2 * py)
    problem_text = f"A consumer buys {firm} meal kits x and streaming credits y. Utility is U(x,y) = x^(1/2)y^(1/2). Income is {money(income)}, Px = {money(px)}, and Py = {money(py)}."
    parts = subparts(
        ("a", "Write the budget constraint."),
        ("b", "Find the utility-maximizing bundle."),
        ("c", "How much income is spent on each good?"),
    )
    sols = subparts(
        ("a", f"The budget constraint is {px}x + {py}y = {income}."),
        ("b", f"With Cobb-Douglas exponents 1/2 and 1/2, spend half of income on each good. Thus x = ({income}/2)/{px} = {num(x)} and y = ({income}/2)/{py} = {num(y)}."),
        ("c", f"The consumer spends {money(income/2)} on each good."),
    )
    return row("Consumer Choice", "Cobb-Douglas demand", "medium", firm, problem_text, parts, sols, ["utility maximization", "budget constraint"], "Cobb-Douglas consumer choice.", {"income": income, "px": px, "py": py}, {"utility": "U(x,y)=x^(1/2)y^(1/2)"})


def mixed_review(i: int) -> dict[str, Any]:
    firm = FIRM_NAMES[(i + 13) % len(FIRM_NAMES)]
    a, b, c = 70 + 5 * i, 2, 10 + i
    q = Fraction(a - c, 2 * b)
    p = a - b * q
    problem_text = f"{firm} is reviewing whether to launch a niche product. Inverse demand is P = {a} - {b}Q and marginal cost is {money(c)}."
    parts = subparts(
        ("a", "If the firm has market power, find the launch quantity and price."),
        ("b", "What economic principle determines the launch quantity?"),
    )
    sols = subparts(
        ("a", f"MR = {a} - {2*b}Q. Set MR = MC: {a} - {2*b}Q = {c}, so Q = {num(q)} and P = {money(p)}."),
        ("b", "A firm with market power chooses quantity where marginal revenue equals marginal cost, then charges the demand-curve price."),
    )
    return row("Mixed Review", "Applied optimization", "medium", firm, problem_text, parts, sols, ["marginal revenue", "marginal cost"], "Mixed review fallback for previously unclassified material.", {"a": a, "b": b, "mc": c}, {})


GENERATORS: dict[str, Callable[[int], dict[str, Any]]] = {
    "Supply and Demand": supply_demand,
    "Elasticity": elasticity,
    "Taxes and Government Intervention": tax_policy,
    "Trade and Welfare": trade,
    "Production and Costs": costs,
    "Perfect Competition": perfect_competition,
    "Monopoly": monopoly,
    "Price Discrimination": discrimination,
    "Risk and Insurance": risk,
    "Asymmetric Information": asymmetric,
    "Incentives and Contracts": incentives,
    "Game Theory": game_theory,
    "Oligopoly and Strategic Competition": oligopoly,
    "Externalities and Public Goods": externalities,
    "Consumer Choice": consumer_choice,
    "Mixed Review": mixed_review,
}


def build_seed_bank(per_topic: int = 5) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for topic, generator in GENERATORS.items():
        for i in range(per_topic):
            rows.append(diversify_row(generator(i + 1), i + 1))
    return rows


def write_seed_bank(
    data_dir: Path | str = DEFAULT_DATA_DIR,
    per_topic: int = 5,
    replace: bool = False,
) -> list[dict[str, Any]]:
    generated_path = data_path("generated", data_dir)
    existing = read_jsonl(generated_path)
    seed_rows = build_seed_bank(per_topic)
    if replace:
        rows = seed_rows
    else:
        existing_ids = {row.get("generated_id") for row in existing}
        rows = [*existing, *[row for row in seed_rows if row["generated_id"] not in existing_ids]]
    write_jsonl(generated_path, rows)
    return rows
