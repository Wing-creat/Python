"""Estimate a starting oxygen stock for one illustrative outage scenario."""

from pathlib import Path

from mars_oxygen_budget import simulate_oxygen_budget

import matplotlib.pyplot as plt


OUTPUT_PATH = "assets/mars_oxygen_reserve.png"


def required_starting_stock_kg(
    target_end_kg: float,
    days_before_outage: int,
    outage_days: int,
    production_kg_per_day: float,
    use_and_leak_kg_per_day: float,
) -> float:
    """Return initial stock needed to end an outage at the chosen target.

    This hand calculation assumes stock does not hit zero or tank capacity
    before the outage ends; compare its answer with the simulation.
    """
    daily_gain_kg = production_kg_per_day - use_and_leak_kg_per_day
    return (
        target_end_kg
        - days_before_outage * daily_gain_kg
        + outage_days * use_and_leak_kg_per_day
    )


def save_reserve_plot(
    starting_stocks_kg: list[float],
    ending_stocks_kg: list[float],
    target_end_kg: float,
    required_start_kg: float,
    output_path: str = OUTPUT_PATH,
) -> None:
    """Plot end-of-outage stock against several assumed starting stocks."""
    figure, axis = plt.subplots(figsize=(8, 5), layout="constrained")
    axis.plot(starting_stocks_kg, ending_stocks_kg, marker="o", linewidth=2,
              label="Simulated end-of-outage stock")
    axis.axhline(target_end_kg, color="#dc2626", linestyle="--",
                 label="Chosen reserve target")
    axis.axvline(required_start_kg, color="gray", linestyle=":",
                 label="Hand-calculated starting stock")
    axis.set_title("Mars Habitat: Starting Oxygen for a Four-Day Outage")
    axis.set_xlabel("Starting stored oxygen (kg)")
    axis.set_ylabel("Stored oxygen after outage (kg)")
    axis.set_ylim(bottom=0)
    axis.grid(alpha=0.3)
    axis.legend()

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180)
    plt.close(figure)


def main() -> None:
    """Check a hand estimate against the existing daily inventory model."""
    outage_day = 8
    outage_days = 4
    target_end_kg = 2.0  # bookkeeping target, not a safe breathing threshold
    production_kg_per_day = 4.5
    crew_size = 4
    use_per_person_kg_per_day = 1.0
    leak_kg_per_day = 0.1
    capacity_kg = 20.0
    daily_use_and_leak_kg = crew_size * use_per_person_kg_per_day + leak_kg_per_day

    required_start_kg = required_starting_stock_kg(
        target_end_kg=target_end_kg,
        days_before_outage=outage_day - 1,
        outage_days=outage_days,
        production_kg_per_day=production_kg_per_day,
        use_and_leak_kg_per_day=daily_use_and_leak_kg,
    )

    starting_stocks_kg = [10.0, 12.0, 14.0, required_start_kg, 17.0]
    ending_stocks_kg = []
    for starting_stock_kg in starting_stocks_kg:
        levels = simulate_oxygen_budget(
            initial_oxygen_kg=starting_stock_kg,
            production_kg_per_day=production_kg_per_day,
            crew_size=crew_size,
            use_per_person_kg_per_day=use_per_person_kg_per_day,
            leak_kg_per_day=leak_kg_per_day,
            capacity_kg=capacity_kg,
            days=outage_day + outage_days - 1,
            outage_day=outage_day,
            outage_duration_days=outage_days,
        )
        ending_stocks_kg.append(levels[-1])

    save_reserve_plot(
        starting_stocks_kg, ending_stocks_kg,
        target_end_kg, required_start_kg,
    )
    print("--- Mars Habitat: Day 5 Starting Oxygen Reserve ---")
    print("Teaching scenario: four-day outage from day 8, 20 kg tank capacity.")
    print(f"Chosen end-of-outage reserve: {target_end_kg:.1f} kg (not a safety threshold)")
    print(f"Hand-calculated starting stock: {required_start_kg:.1f} kg")
    print(f"Simulated end-of-outage stock: {ending_stocks_kg[3]:.1f} kg")
    print("The hand calculation assumes storage never reaches zero or tank capacity first.")
    print(f"Plot saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
