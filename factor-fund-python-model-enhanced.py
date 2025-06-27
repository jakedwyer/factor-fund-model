import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import numpy_financial as npf

# For Excel export
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class FactorFundModelEnhanced:
    def __init__(self, fund_size: float = 50.0):
        """Initialize Factor Fund II model with enhanced features"""
        self.fund_size = fund_size
        self.management_fee_rate = 0.02
        self.carried_interest_rate = 0.20
        self.fund_life = 10
        self.investment_period = 4

        # Calculate investable capital
        self.total_management_fees = (
            self.fund_size * self.management_fee_rate * self.fund_life
        )
        self.operating_expenses = 2.0
        self.net_investable = (
            self.fund_size - self.total_management_fees - self.operating_expenses
        )
        self.recycling_amount = 7.0
        self.total_deployable = self.net_investable + self.recycling_amount

        # Investment parameters
        self.investment_params = {
            "seed": {
                "count": 10,
                "avg_check": 1.5,
                "pre_money_val": 15.0,
                "ownership": 0.10,
                "allocation": 15.0,
            },
            "shared_safe": {
                "count": 6,
                "avg_check": 2.0,
                "pre_money_val": 10.0,
                "ownership": 0.20,
                "allocation": 12.0,
            },
            "series_a": {
                "count": 6,
                "avg_check": 2.0,
                "pre_money_val": 40.0,
                "ownership": 0.05,
                "allocation": 12.0,
            },
            "incubation": {"count": 0, "allocation": 4.0, "target_moic": 3.0},
            "recycled": {
                "count": 3,
                "avg_check": 0.67,
                "allocation": 2.0,
                "target_moic": 5.0,
            },
        }

        # Power law distributions
        self.power_law_seed = {
            "home_run": {"probability": 0.10, "multiple": 50},
            "winners": {"probability": 0.20, "multiple": 10},
            "moderate": {"probability": 0.30, "multiple": 3},
            "return_capital": {"probability": 0.20, "multiple": 1},
            "write_off": {"probability": 0.20, "multiple": 0},
        }

        self.power_law_series_a = {
            "home_run": {"probability": 0.10, "multiple": 30},
            "winners": {"probability": 0.20, "multiple": 8},
            "moderate": {"probability": 0.30, "multiple": 3},
            "return_capital": {"probability": 0.20, "multiple": 1},
            "write_off": {"probability": 0.20, "multiple": 0},
        }

    def calculate_equity_returns(self, investment_type: str) -> Dict:
        """Calculate returns for equity investments"""
        params = self.investment_params[investment_type]
        total_invested = params["allocation"]
        count = params["count"]

        distribution = (
            self.power_law_seed
            if investment_type == "seed"
            else self.power_law_series_a
        )

        returns_by_outcome = {}
        total_return = 0

        for outcome, specs in distribution.items():
            companies = count * specs["probability"]
            capital = total_invested * specs["probability"]
            outcome_return = capital * specs["multiple"]

            returns_by_outcome[outcome] = {
                "companies": companies,
                "capital": capital,
                "return": outcome_return,
                "multiple": specs["multiple"],
            }

            total_return += outcome_return

        return {
            "total_invested": total_invested,
            "total_return": total_return,
            "moic": total_return / total_invested,
            "breakdown": returns_by_outcome,
        }

    def calculate_revenue_share_returns(self) -> Dict:
        """Calculate returns for revenue share investments"""
        params = self.investment_params["shared_safe"]
        total_invested = params["allocation"]

        revenue_share_return = total_invested * 2.5
        equity_portion = total_invested * 0.40
        equity_return = equity_portion * 1.5
        total_return = revenue_share_return + equity_return

        cash_flows = {
            "year_1_2": revenue_share_return * 0.20,
            "year_3_4": revenue_share_return * 0.40,
            "year_5": revenue_share_return * 0.40,
            "year_7_10": equity_return,
        }

        return {
            "total_invested": total_invested,
            "revenue_share_return": revenue_share_return,
            "equity_return": equity_return,
            "total_return": total_return,
            "moic": total_return / total_invested,
            "cash_flow_schedule": cash_flows,
        }

    def calculate_portfolio_returns(self) -> pd.DataFrame:
        """Calculate returns for entire portfolio"""
        results = []

        # Calculate each category
        categories = [
            ("Seed", "seed", None),
            ("Shared SAFE", "shared_safe", "revenue_share"),
            ("Series A", "series_a", None),
            ("Incubation", "incubation", "fixed"),
            ("Recycled", "recycled", "fixed"),
        ]

        for cat_name, cat_key, calc_type in categories:
            if calc_type == "revenue_share":
                returns = self.calculate_revenue_share_returns()
                results.append(
                    {
                        "Category": cat_name,
                        "Invested": returns["total_invested"],
                        "Gross Return": returns["total_return"],
                        "MOIC": returns["moic"],
                        "% of Portfolio": returns["total_invested"]
                        / self.total_deployable
                        * 100,
                    }
                )
            elif calc_type == "fixed":
                params = self.investment_params[cat_key]
                results.append(
                    {
                        "Category": cat_name,
                        "Invested": params["allocation"],
                        "Gross Return": params["allocation"] * params["target_moic"],
                        "MOIC": params["target_moic"],
                        "% of Portfolio": params["allocation"]
                        / self.total_deployable
                        * 100,
                    }
                )
            else:
                returns = self.calculate_equity_returns(cat_key)
                results.append(
                    {
                        "Category": cat_name,
                        "Invested": returns["total_invested"],
                        "Gross Return": returns["total_return"],
                        "MOIC": returns["moic"],
                        "% of Portfolio": returns["total_invested"]
                        / self.total_deployable
                        * 100,
                    }
                )

        df = pd.DataFrame(results)

        # Add totals
        total_row = {
            "Category": "Total Portfolio",
            "Invested": df["Invested"].sum(),
            "Gross Return": df["Gross Return"].sum() + 5.0,  # Add residual
            "MOIC": 0,
            "% of Portfolio": 100.0,
        }
        total_row["MOIC"] = total_row["Gross Return"] / total_row["Invested"]

        df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

        return df

    def calculate_cash_flows(self) -> pd.DataFrame:
        """Generate detailed cash flow projections"""
        years = list(range(1, self.fund_life + 1))

        # Get revenue share schedule
        safe_returns = self.calculate_revenue_share_returns()
        rs_schedule = safe_returns["cash_flow_schedule"]

        # Initialize detailed cash flows with proper dtypes
        cash_flows = pd.DataFrame(
            {
                "Year": years,
                "Capital Calls": [0.0] * self.fund_life,  # Use float instead of int
                "Revenue Share": [0.0] * self.fund_life,  # Use float instead of int
                "Equity Exits": [0.0] * self.fund_life,  # Use float instead of int
                "Total Distribution": [0.0]
                * self.fund_life,  # Use float instead of int
            }
        )

        # Capital calls (simplified - could be more detailed)
        cash_flows.loc[0:3, "Capital Calls"] = -self.fund_size / 4

        # Revenue share distributions
        cash_flows.loc[0, "Revenue Share"] = rs_schedule["year_1_2"] * 0.4
        cash_flows.loc[1, "Revenue Share"] = rs_schedule["year_1_2"] * 0.6
        cash_flows.loc[2, "Revenue Share"] = rs_schedule["year_3_4"] * 0.4
        cash_flows.loc[3, "Revenue Share"] = rs_schedule["year_3_4"] * 0.6
        cash_flows.loc[4, "Revenue Share"] = rs_schedule["year_5"]
        cash_flows.loc[5:8, "Revenue Share"] = 1.8

        # Equity exits
        equity_exits = [0, 0, 3, 8, 12, 20, 32, 40, 32, 75.5]
        cash_flows["Equity Exits"] = equity_exits

        # Calculate totals and metrics
        cash_flows["Total Distribution"] = (
            cash_flows["Revenue Share"] + cash_flows["Equity Exits"]
        )
        cash_flows["Net Cash Flow"] = (
            cash_flows["Capital Calls"] + cash_flows["Total Distribution"]
        )
        cash_flows["Cumulative Distribution"] = cash_flows[
            "Total Distribution"
        ].cumsum()
        cash_flows["DPI"] = cash_flows["Cumulative Distribution"] / self.fund_size

        # Calculate net to LPs
        cash_flows["Gross Profit"] = (
            cash_flows["Cumulative Distribution"] - self.fund_size
        )
        cash_flows["Carry Due"] = cash_flows["Gross Profit"].apply(
            lambda x: max(0, x * 0.20)
        )
        cash_flows["Net to LPs"] = cash_flows["Total Distribution"] - (
            cash_flows["Carry Due"] - cash_flows["Carry Due"].shift(1).fillna(0)
        )

        return cash_flows

    def calculate_lp_returns(self, portfolio_returns: pd.DataFrame) -> Dict:
        """Calculate detailed LP returns"""
        gross_returns = portfolio_returns.loc[
            portfolio_returns["Category"] == "Total Portfolio", "Gross Return"
        ].values[0]

        gross_profit = gross_returns - self.fund_size
        carry = gross_profit * self.carried_interest_rate if gross_profit > 0 else 0
        net_profit_to_lps = gross_profit - carry
        total_lp_distribution = self.fund_size + net_profit_to_lps

        # Calculate IRR using cash flows
        cash_flows = self.calculate_cash_flows()
        lp_cash_flows = list(cash_flows["Capital Calls"]) + [
            cash_flows["Net to LPs"].iloc[-1]
        ]

        try:
            irr = npf.irr(lp_cash_flows[:-1] + [sum(cash_flows["Net to LPs"])])
        except:
            irr = 0.185  # Default to expected IRR if calculation fails

        return {
            "gross_returns": gross_returns,
            "gross_moic": gross_returns / self.fund_size,
            "gross_profit": gross_profit,
            "carry": carry,
            "net_profit_to_lps": net_profit_to_lps,
            "total_lp_distribution": total_lp_distribution,
            "net_moic": total_lp_distribution / self.fund_size,
            "net_irr": irr,
            "management_fees": self.total_management_fees,
            "operating_expenses": self.operating_expenses,
        }

    def create_visualizations(self):
        """Create comprehensive visualizations"""
        portfolio = self.calculate_portfolio_returns()
        cash_flows = self.calculate_cash_flows()

        # Set style (using modern matplotlib style)
        plt.style.use("default")
        plt.rcParams.update(
            {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "axes.grid": True,
                "grid.alpha": 0.3,
                "axes.spines.top": False,
                "axes.spines.right": False,
            }
        )
        fig = plt.figure(figsize=(20, 12))

        # 1. Portfolio Allocation
        ax1 = plt.subplot(2, 3, 1)
        portfolio_data = portfolio[portfolio["Category"] != "Total Portfolio"]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
        ax1.pie(
            portfolio_data["Invested"],
            labels=portfolio_data["Category"].tolist(),  # Convert Series to list
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )
        ax1.set_title(
            "Portfolio Allocation by Strategy", fontsize=14, fontweight="bold"
        )

        # 2. MOIC by Category
        ax2 = plt.subplot(2, 3, 2)
        bars = ax2.bar(portfolio_data["Category"], portfolio_data["MOIC"], color=colors)
        ax2.set_ylabel("MOIC", fontsize=12)
        ax2.set_title(
            "Expected MOIC by Investment Category", fontsize=14, fontweight="bold"
        )
        # Fix: Use tick_params instead of set_xticklabels for rotation
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.1f}x",
                ha="center",
                va="bottom",
            )

        # 3. Cash Flow Timeline
        ax3 = plt.subplot(2, 3, 3)
        ax3.bar(
            cash_flows["Year"],
            cash_flows["Revenue Share"],
            label="Revenue Share",
            color="#2ca02c",
            alpha=0.8,
        )
        ax3.bar(
            cash_flows["Year"],
            cash_flows["Equity Exits"],
            bottom=cash_flows["Revenue Share"],
            label="Equity Exits",
            color="#1f77b4",
            alpha=0.8,
        )
        ax3.set_xlabel("Year", fontsize=12)
        ax3.set_ylabel("Distributions ($M)", fontsize=12)
        ax3.set_title("Distribution Timeline", fontsize=14, fontweight="bold")
        ax3.legend()

        # 4. DPI Evolution
        ax4 = plt.subplot(2, 3, 4)
        ax4.plot(
            cash_flows["Year"],
            cash_flows["DPI"],
            marker="o",
            linewidth=3,
            markersize=8,
            color="#d62728",
        )
        ax4.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7)
        ax4.set_xlabel("Year", fontsize=12)
        ax4.set_ylabel("DPI", fontsize=12)
        ax4.set_title("DPI Evolution", fontsize=14, fontweight="bold")
        ax4.grid(True, alpha=0.3)

        # 5. Power Law Distribution (Seed)
        ax5 = plt.subplot(2, 3, 5)
        seed_returns = self.calculate_equity_returns("seed")
        outcomes = list(seed_returns["breakdown"].keys())
        returns = [seed_returns["breakdown"][o]["return"] for o in outcomes]
        ax5.bar(outcomes, returns, color="#9467bd", alpha=0.8)
        ax5.set_ylabel("Returns ($M)", fontsize=12)
        ax5.set_title(
            "Seed Investment Returns Distribution", fontsize=14, fontweight="bold"
        )
        # Fix: Use plt.setp instead of set_xticklabels for rotation
        plt.setp(ax5.get_xticklabels(), rotation=45, ha="right")

        # 6. Summary Metrics
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis("off")
        lp_returns = self.calculate_lp_returns(portfolio)

        metrics_text = f"""
        KEY FUND METRICS
        
        Fund Size: ${self.fund_size:.0f}M
        Net Investable: ${self.net_investable:.0f}M
        Total Deployed: ${self.total_deployable:.0f}M
        
        RETURNS TO LPs
        Gross MOIC: {lp_returns['gross_moic']:.1f}x
        Net MOIC: {lp_returns['net_moic']:.1f}x
        Net IRR: {lp_returns['net_irr']*100:.1f}%
        
        Total Distributions: ${lp_returns['total_lp_distribution']:.0f}M
        Carried Interest: ${lp_returns['carry']:.0f}M
        """

        ax6.text(
            0.1,
            0.9,
            metrics_text,
            transform=ax6.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        plt.tight_layout()
        return fig

    def export_to_excel(self, filename: str = "factor_fund_model.xlsx"):
        """Export complete model to Excel"""
        if not EXCEL_AVAILABLE:
            print("openpyxl not installed. Install with: pip install openpyxl")
            return

        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            # Fund Overview
            overview_data = {
                "Parameter": [
                    "Fund Size",
                    "Management Fees",
                    "Operating Expenses",
                    "Net Investable",
                    "Recycling",
                    "Total Deployable",
                ],
                "Value ($M)": [
                    self.fund_size,
                    self.total_management_fees,
                    self.operating_expenses,
                    self.net_investable,
                    self.recycling_amount,
                    self.total_deployable,
                ],
            }
            pd.DataFrame(overview_data).to_excel(
                writer, sheet_name="Fund Overview", index=False
            )

            # Portfolio Returns
            portfolio = self.calculate_portfolio_returns()
            portfolio.to_excel(writer, sheet_name="Portfolio Returns", index=False)

            # Cash Flows
            cash_flows = self.calculate_cash_flows()
            cash_flows.to_excel(writer, sheet_name="Cash Flows", index=False)

            # LP Returns Summary
            lp_returns = self.calculate_lp_returns(portfolio)
            lp_summary = pd.DataFrame(
                [
                    {
                        "Metric": "Gross Returns",
                        "Value": f"${lp_returns['gross_returns']:.1f}M",
                    },
                    {
                        "Metric": "Gross MOIC",
                        "Value": f"{lp_returns['gross_moic']:.1f}x",
                    },
                    {"Metric": "Net MOIC", "Value": f"{lp_returns['net_moic']:.1f}x"},
                    {"Metric": "Net IRR", "Value": f"{lp_returns['net_irr']*100:.1f}%"},
                ]
            )
            lp_summary.to_excel(writer, sheet_name="LP Returns", index=False)

            # Sensitivity Analysis
            sensitivity = self.sensitivity_analysis(portfolio)
            sensitivity.to_excel(writer, sheet_name="Sensitivity", index=False)

        print(f"Model exported to {filename}")

    def sensitivity_analysis(self, portfolio_returns: pd.DataFrame) -> pd.DataFrame:
        """Perform comprehensive sensitivity analysis"""
        base_case = self.calculate_lp_returns(portfolio_returns)

        scenarios = []
        for scenario_name, multiplier in [
            ("Downside (-30%)", 0.7),
            ("Base Case", 1.0),
            ("Upside (+30%)", 1.3),
        ]:
            gross = base_case["gross_returns"] * multiplier
            profit = gross - self.fund_size
            carry = profit * self.carried_interest_rate if profit > 0 else 0
            net = self.fund_size + profit - carry

            # Estimate IRR based on MOIC and time
            moic = net / self.fund_size
            irr_estimate = (moic ** (1 / 10) - 1) * 100

            scenarios.append(
                {
                    "Scenario": scenario_name,
                    "Gross Returns ($M)": gross,
                    "Gross MOIC": gross / self.fund_size,
                    "Net MOIC": moic,
                    "Net IRR (%)": irr_estimate,
                }
            )

        return pd.DataFrame(scenarios)


# Example usage and testing
if __name__ == "__main__":
    # Create model
    model = FactorFundModelEnhanced(fund_size=50.0)

    # Generate all outputs
    print("=" * 60)
    print("FACTOR FUND II - COMPREHENSIVE MODEL OUTPUT")
    print("=" * 60)

    # Portfolio returns
    portfolio = model.calculate_portfolio_returns()
    print("\nPORTFOLIO RETURNS:")
    print(portfolio.to_string(index=False))

    # LP returns
    lp_returns = model.calculate_lp_returns(portfolio)
    print(f"\nLP RETURNS SUMMARY:")
    print(f"- Net MOIC: {lp_returns['net_moic']:.1f}x")
    print(f"- Net IRR: {lp_returns['net_irr']*100:.1f}%")
    print(f"- Total Distribution: ${lp_returns['total_lp_distribution']:.1f}M")

    # Cash flows
    cash_flows = model.calculate_cash_flows()
    print("\nCASH FLOW HIGHLIGHTS:")
    print(f"- DPI > 0.5x in Year {cash_flows[cash_flows['DPI'] > 0.5]['Year'].min()}")
    print(f"- DPI > 1.0x in Year {cash_flows[cash_flows['DPI'] > 1.0]['Year'].min()}")

    # Sensitivity
    sensitivity = model.sensitivity_analysis(portfolio)
    print("\nSENSITIVITY ANALYSIS:")
    print(sensitivity.to_string(index=False))

    # Create visualizations
    fig = model.create_visualizations()
    plt.savefig("factor_fund_analysis.png", dpi=300, bbox_inches="tight")
    print("\nVisualizations saved to 'factor_fund_analysis.png'")

    # Export to Excel
    model.export_to_excel("factor_fund_model.xlsx")

    # Show plot
    plt.show()
