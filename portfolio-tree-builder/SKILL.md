---
name: portfolio-tree-builder
description: Build or audit a hierarchical portfolio allocation tree from investor goals to holdings, revealing hidden factor concentration, role drift, and redundant exposure. Use when a user wants to structure or review a portfolio, map holdings to goals, distinguish core/alpha/tactical/experimental/hedge/cash roles, or decide whether a broad fund is sufficient versus active security selection. Do not use for single-stock research, price quotes, or trade execution.
---

# Portfolio Tree Builder

Turn a list of accounts and tickers into a decision architecture that explains why each position exists, what risk actually drives it, and whether the portfolio is structurally coherent.

This is a portfolio-design and audit workflow. It does not create orders.

## Core principles

1. **Structure before securities.** Decide what the portfolio needs before choosing an ETF, stock, bond, or derivative.
2. **Ticker count is not diversification.** Merge positions that share the same economic driver before judging concentration.
3. **Accounts are containers.** Analyze allocation within a clearly defined capital scope; do not treat brokerage accounts as asset classes.
4. **Derivatives and leverage are overlays.** Map them to the underlying asset, factor exposure, maximum loss, cash obligation, and expiry instead of counting them as separate diversification.
5. **Capacity is not a task.** Being below a target or limit means there may be room to invest, not that the user should automatically buy.
6. **Cost basis is not a thesis.** Use cost for accounting and tax context, never as the reason to hold, add, or wait for breakeven.

## Required tree

Build the portfolio in this order:

```text
Investable capital
└── Purpose / liability and time horizon
    └── Asset class / currency / region
        └── Real risk factor
            └── Portfolio role
                └── Instrument
                    └── Position or lot
```

Do not skip directly from account to ticker. If information is missing, keep the node as `Unknown` and list what would resolve it.

## Workflow

### 1. Define the allocation scope

State what capital the percentages refer to:

- total household investable assets;
- one portfolio or strategy;
- one brokerage account; or
- a user-selected subset.

Use one denominator within a sibling group. Do not add percentages from different scopes until their market values have been converted to the same scope.

Collect or infer, while labeling assumptions:

- goals and required liquidity;
- relevant liabilities and time horizons;
- accounts, currencies, and market values;
- holdings, funds, derivatives, and cash;
- existing targets, limits, or restrictions;
- the user's claimed thesis or role for each active position.

If live portfolio data is unavailable, analyze the user-provided snapshot and state its date. Never invent current prices, weights, or account values.

### 2. Apply the Edge Gate at every branch

At each node ask:

> Is there a low-cost, sufficiently liquid diversified instrument that expresses this node completely? If so, what verifiable edge justifies branching further?

Classify the answer:

- **No demonstrated edge:** stop at the higher node and prefer a broad or sector fund as the default expression.
- **Partial edge:** use a diversified core for most exposure and a deliberately limited active satellite.
- **Demonstrated edge:** continue to a narrower bucket or security, documenting the evidence, expected advantage, failure condition, and added complexity.

Do not accept enthusiasm, familiarity, historical profit, or a compelling story as evidence of edge.

### 3. Assign one primary role to every position

Each position or lot must have exactly one primary role:

| Role | Purpose | Minimum requirement |
|---|---|---|
| Core beta | Long-term market or durable theme exposure | Low turnover and a clear target range |
| Active alpha | Exploit a researched expectation gap | Thesis, catalyst, invalidation, and size limit |
| Tactical / event | Express a temporary setup or event | Deadline, maximum loss, and exit plan |
| Experimental | Test a strategy, signal, or data source | Small size and a separate evaluation record |
| Hedge | Protect a named risk for a defined period | Protected exposure, horizon, and cost budget |
| Liquidity reserve | Meet obligations and preserve optionality | Currency, availability, and minimum requirement |

If one ticker serves several strategies, split it by lot or notional allocation. Flag any position that quietly changed role, such as a failed tactical trade being relabeled as a long-term core holding.

### 4. Consolidate real risk factors

Look through labels and instruments to identify common drivers. Examples include:

- interest rates and duration;
- economic growth or recession;
- inflation and commodity prices;
- one country's policy or currency;
- AI capital expenditure;
- a single customer, supplier, platform, or regulatory outcome;
- volatility, leverage, liquidity, or short-option exposure.

Merge direct holdings, funds, and derivative delta that depend on the same driver. Explain where apparently different sectors are likely to fail together.

Use quantitative correlation or risk-contribution data when available, but do not treat historical correlation as the only definition of a shared factor. Business-model and supply-chain dependence can reveal concentration that a short price history misses.

### 5. Validate every leaf

Each investable leaf should have:

- purpose and primary role;
- target range and hard limit, if supplied or justified;
- real risk factors;
- allowed instrument types;
- liquidity requirement;
- thesis or selection rule;
- failure or exit condition;
- for derivatives: maximum loss, assignment or collateral cash, coverage relationship, and expiry.

Flag leaves whose siblings cannot be reconciled to one denominator, whose limits overlap, or whose exposures are double-counted.

### 6. Diagnose the structure

Check for:

- hidden factor concentration;
- duplicate instruments expressing the same idea;
- missing liquidity for known obligations;
- active positions without a verifiable edge;
- role drift or positions with no role;
- targets treated as mandatory deployment;
- derivatives counted separately from their underlying exposure;
- diversification by ticker name rather than economic driver;
- a complex tree whose maintenance cost exceeds its benefit.

Prioritize structural problems that could force a bad decision during a drawdown over small optimization opportunities.

### 7. Recommend structural actions

Use these action labels:

- `KEEP` — the node has a clear role and appropriate expression;
- `MERGE` — combine duplicate exposures for analysis or implementation;
- `MOVE` — reclassify a position under its true factor or role;
- `SPLIT` — separate lots or strategies that currently share one ticker;
- `SIMPLIFY` — stop branching and use a broader instrument;
- `RESEARCH` — evidence is insufficient to justify the current branch;
- `REDUCE RISK` — concentration, leverage, or liquidity is structurally unsafe;
- `WAIT` — there may be capacity, but no decision-quality reason to deploy it.

Recommendations must preserve user control. Do not turn them into trades, exact order quantities, or personalized guarantees.

## Output format

### 1. Structural verdict

State whether the portfolio is coherent, over-branched, under-specified, or concentrated behind misleading labels. Lead with the three most important findings.

### 2. Portfolio tree

Render the hierarchy as an indented tree. Show weights only when they use a verified common denominator.

### 3. Leaf registry

| Leaf | Holdings | Role | Real factors | Target / limit | Edge evidence | Exit condition | Status |
|---|---|---|---|---|---|---|---|

### 4. Hidden-factor consolidation

| Real factor | Direct exposure | Indirect / derivative exposure | Combined concern | Why it may move together |
|---|---|---|---|---|

### 5. Edge Gate decisions

For every actively selected branch, state `STOP AT FUND`, `CORE + SATELLITE`, or `CONTINUE TO SECURITY`, with the evidence and missing proof.

### 6. Priority changes

List structural actions in order of risk reduction and decision value. Separate actions possible with existing information from items requiring more data.

### 7. Assumptions and missing data

Record the valuation date, allocation scope, unavailable data, and any inference that materially affects the result.

## Boundaries

- This skill designs and audits portfolio structure; it does not replace security research, tax advice, legal advice, or trade authorization.
- Do not prescribe universal allocation percentages. Targets must follow the user's goals, constraints, horizon, and risk capacity.
- Do not infer that institutional ownership, popularity, past returns, or a low valuation alone creates an active-selection edge.
- Do not use an underweight node as sufficient reason to buy.
- When the user requests execution, hand off to the applicable trading workflow and require its normal live-data, risk, and authorization checks.
