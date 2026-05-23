"""
H-Automate — data_cleaner.py
Pandas preprocessing layer for Nigerian SME sales data.

This file is the CRITICAL layer between raw CSV uploads and groq_client.py.
ALL business calculations happen here. The AI receives only pre-computed
summaries — it never calculates, only interprets.

Output contract: clean_and_summarize() returns a dict (see bottom of file).
Bob/Manus: pass the "summary_text" field to get_diagnosis() in groq_client.py.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from dateutil import parser as dateutil_parser


# ─────────────────────────────────────────────
# CONFIDENCE LEVELS
# ─────────────────────────────────────────────
HIGH   = "high"
MEDIUM = "medium"
LOW    = "low"


# ─────────────────────────────────────────────
# UNIVERSAL DATE PARSER
# Handles virtually any date format a Nigerian SME
# file might contain. Tries multiple strategies in order.
#
# Handles formats including:
#   2026-01-15        (ISO standard)
#   15/01/2026        (DD/MM/YYYY)
#   01/15/2026        (MM/DD/YYYY)
#   15-Jan-2026       (DD-Mon-YYYY)
#   Jan 15, 2026      (Mon DD, YYYY)
#   15 January 2026   (DD Month YYYY)
#   20260115          (YYYYMMDD compact)
#   15.01.2026        (dot-separated)
#   2026/01/15        (slash ISO)
#   Tuesday 15 Jan    (partial — uses current year)
# ─────────────────────────────────────────────
def parse_dates_universal(series: pd.Series) -> tuple:
    """
    Attempt to parse a date column using multiple strategies.
    Returns (parsed_series, n_failed, strategy_used).
    """

    # Strategy 1: pandas with dayfirst=True (handles DD/MM/YYYY)
    try:
        parsed = pd.to_datetime(series, dayfirst=True, errors="coerce")
        n_failed = parsed.isna().sum()
        if n_failed < len(series) * 0.1:   # <10% failed — good enough
            return parsed, int(n_failed), "pandas dayfirst"
    except Exception:
        pass

    # Strategy 2: pandas with dayfirst=False (handles MM/DD/YYYY)
    try:
        parsed = pd.to_datetime(series, dayfirst=False, errors="coerce")
        n_failed = parsed.isna().sum()
        if n_failed < len(series) * 0.1:
            return parsed, int(n_failed), "pandas monthfirst"
    except Exception:
        pass

    # Strategy 3: pandas infer_datetime_format (fast path for consistent formats)
    try:
        parsed = pd.to_datetime(series, infer_datetime_format=True, errors="coerce")
        n_failed = parsed.isna().sum()
        if n_failed < len(series) * 0.1:
            return parsed, int(n_failed), "pandas infer"
    except Exception:
        pass

    # Strategy 4: Try common explicit formats one by one
    EXPLICIT_FORMATS = [
        "%Y-%m-%d",      # 2026-01-15
        "%d/%m/%Y",      # 15/01/2026
        "%m/%d/%Y",      # 01/15/2026
        "%d-%m-%Y",      # 15-01-2026
        "%d-%b-%Y",      # 15-Jan-2026
        "%d %b %Y",      # 15 Jan 2026
        "%b %d, %Y",     # Jan 15, 2026
        "%B %d, %Y",     # January 15, 2026
        "%d %B %Y",      # 15 January 2026
        "%Y/%m/%d",      # 2026/01/15
        "%d.%m.%Y",      # 15.01.2026
        "%Y%m%d",        # 20260115
        "%d-%b-%y",      # 15-Jan-26
        "%m-%d-%Y",      # 01-15-2026
        "%b-%d-%Y",      # Jan-15-2026
        "%d/%b/%Y",      # 15/Jan/2026
        "%Y-%b-%d",      # 2026-Jan-15
    ]
    best_parsed   = None
    best_n_failed = len(series)
    best_fmt      = None

    for fmt in EXPLICIT_FORMATS:
        try:
            parsed   = pd.to_datetime(series, format=fmt, errors="coerce")
            n_failed = parsed.isna().sum()
            if n_failed < best_n_failed:
                best_parsed   = parsed
                best_n_failed = n_failed
                best_fmt      = fmt
                if n_failed == 0:
                    break
        except Exception:
            continue

    if best_parsed is not None and best_n_failed < len(series) * 0.3:
        return best_parsed, int(best_n_failed), f"explicit format {best_fmt}"

    # Strategy 5: dateutil row-by-row (slowest but most flexible)
    # Handles: "Tuesday 15 Jan", "15th January 2026", mixed formats
    def try_parse(val):
        if pd.isna(val):
            return pd.NaT
        try:
            return pd.Timestamp(
                dateutil_parser.parse(str(val), dayfirst=True, fuzzy=True)
            )
        except Exception:
            return pd.NaT

    parsed   = series.apply(try_parse)
    n_failed = parsed.isna().sum()
    return parsed, int(n_failed), "dateutil fuzzy"


# ─────────────────────────────────────────────
# COLUMN NAME NORMALIZER
# Handles inconsistent headers from real SME files.
# ─────────────────────────────────────────────
COLUMN_ALIASES = {
    "date":        ["date", "sale date", "transaction date", "trans date",
                    "sales date", "day", "transaction_date", "sale_date",
                    "date_of_sale", "saledate", "transactiondate"],
    "product":     ["product", "item", "product name", "item name", "goods",
                    "description", "product_name", "item_name", "sku",
                    "drug", "drug name", "drug_name", "drug_product",
                    "medication", "medicine", "drug/product",
                    "transaction type", "service", "service type",
                    "transaction_type", "service_type"],
    "quantity":    ["quantity", "qty", "units", "amount sold", "quantity sold",
                    "qty_sold", "quantity_sold", "units sold", "units_sold",
                    "packs", "tablets", "dispensed", "qty_dispensed"],
    "revenue":     ["revenue", "sales", "total", "amount", "total sales",
                    "income", "total_sales", "total_revenue", "price",
                    "sale amount", "value", "revenue_ngn", "sales_ngn",
                    "amount_ngn", "total_ngn", "turnover",
                    "transaction amount", "transfer amount", "float used",
                    "transaction_amount", "transfer_amount", "unit_price_ngn"],
    "cost":        ["cost", "cost price", "unit cost", "buying price",
                    "purchase price", "cost_price", "cogs", "cost_ngn",
                    "wholesale price", "supplier price", "wholesale_price",
                    "cost_price_ngn"],
    "category":    ["category", "type", "product type", "department",
                    "product_type", "cat",
                    "drug class", "drug category", "otc/prescription",
                    "drug_class", "drug_category", "therapeutic_class"],
    "payment":     ["payment", "payment method", "payment type", "mode",
                    "payment_method", "pay method", "transaction type",
                    "payment_type", "pay_method", "mode_of_payment"],
    "expiry":      ["expiry", "expiry date", "expiration", "exp date",
                    "best before", "expiry_date", "expiry_month",
                    "exp_date", "expiration_date"],
    "float":       ["float", "float balance", "opening float", "closing float",
                    "cash float", "agent float", "float_balance"],
    "customer":    ["customer", "customer name", "client", "customer_id",
                    "buyer", "phone", "customer phone", "customer_name",
                    "client_name"],
    "profit":      ["profit", "profit_ngn", "gross profit", "net profit",
                    "margin", "profit_margin"],
    "stock":       ["stock", "stock remaining", "stock_remaining",
                    "remaining stock", "inventory", "stock_level",
                    "closing stock", "balance"],
}


def normalize_columns(df: pd.DataFrame) -> dict:
    """
    Map actual column names to standard names.
    Uses partial matching so Revenue_NGN matches revenue, Drug_Product matches product, etc.
    """
    found = {}
    # Build lookup with both original and underscore-normalized versions
    df_cols_lower = {}
    for col in df.columns:
        df_cols_lower[col.lower().strip()] = col
        df_cols_lower[col.lower().strip().replace(" ", "_")] = col

    for standard, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            alias_norm = alias.lower().strip()
            alias_under = alias_norm.replace(" ", "_")
            # 1. Exact match
            if alias_norm in df_cols_lower:
                found[standard] = df_cols_lower[alias_norm]
                break
            if alias_under in df_cols_lower:
                found[standard] = df_cols_lower[alias_under]
                break
            # 2. Partial match — alias contained in column name
            matched = False
            for col_norm, col_orig in df_cols_lower.items():
                if alias_under in col_norm or alias_norm in col_norm:
                    found[standard] = col_orig
                    matched = True
                    break
            if matched:
                break
        if standard not in found:
            found[standard] = None
    return found


# ─────────────────────────────────────────────
# PRODUCT NAME NORMALIZER — by business type
# ─────────────────────────────────────────────
PRODUCT_ALIASES_MINIMART = {
    "indomie":        ["indomie", "noodles", "instant noodles", "indo"],
    "rice":           ["rice", "rice (bag)", "local rice", "parboiled rice"],
    "vegetable oil":  ["vegetable oil", "veg oil", "veg. oil", "cooking oil",
                       "groundnut oil"],
    "tomato paste":   ["tomato paste", "tomato", "tomatopaste", "tin tomato"],
    "sardines":       ["sardines", "sardine", "titus", "fish"],
    "coca cola":      ["coca cola", "coke", "coke 50cl", "coke 35cl", "cold drink"],
    "tissue paper":   ["tissue", "tissue paper", "toilet paper", "serviette"],
    "biscuits":       ["biscuits", "biscuit", "cookies", "cabin biscuit"],
    "sugar":          ["sugar", "tate lyle", "dangote sugar"],
    "flour":          ["flour", "wheat flour", "golden penny"],
}

PRODUCT_ALIASES_PHARMACY = {
    "paracetamol":     ["paracetamol", "panadol", "emzor paracetamol",
                        "acetaminophen", "para"],
    "amoxicillin":     ["amoxicillin", "amoxil", "amox", "augmentin"],
    "vitamin c":       ["vitamin c", "vit c", "ascorbic acid", "vit. c"],
    "malaria drugs":   ["coartem", "lonart", "artemether", "lumefantrine",
                        "malaria", "anti-malaria"],
    "omeprazole":      ["omeprazole", "ulcer drug", "losec", "prilosec"],
    "metronidazole":   ["metronidazole", "flagyl", "metro"],
    "blood pressure":  ["amlodipine", "lisinopril", "bp drug", "blood pressure",
                        "hypertension"],
    "diabetic drugs":  ["metformin", "glibenclamide", "insulin", "diabetes",
                        "diabetic"],
}

PRODUCT_ALIASES_POS = {
    "cash withdrawal": ["withdrawal", "cash out", "withdraw", "cash withdrawal"],
    "transfer":        ["transfer", "bank transfer", "send money", "remittance"],
    "airtime":         ["airtime", "recharge", "top up", "topup", "mtn", "glo",
                        "airtel", "9mobile"],
    "data":            ["data", "data bundle", "data sub", "subscription"],
    "bill payment":    ["bill", "bill payment", "electricity", "nepa", "ekedc",
                        "ikedc", "water bill"],
    "account opening": ["account", "account opening", "bvn", "new account"],
}

PRODUCT_ALIASES_RESTAURANT = {
    "rice dishes":     ["rice", "jollof rice", "fried rice", "white rice",
                        "party rice"],
    "protein":         ["chicken", "beef", "fish", "turkey", "goat meat",
                        "assorted"],
    "soup":            ["egusi", "okra", "ogbono", "banga", "afang", "edikang"],
    "swallow":         ["eba", "fufu", "semo", "amala", "pounded yam", "tuwo"],
    "drinks":          ["water", "coke", "pepsi", "juice", "malt", "zobo",
                        "kunu"],
    "snacks":          ["puff puff", "samosa", "meat pie", "spring roll",
                        "small chops"],
}

PRODUCT_ALIASES_FASHION = {
    "tops":            ["top", "blouse", "shirt", "t-shirt", "polo",
                        "ankara top"],
    "bottoms":         ["trouser", "skirt", "jean", "shorts", "palazzo"],
    "dresses":         ["dress", "gown", "kaftan", "jumpsuit", "ankara dress"],
    "accessories":     ["bag", "shoe", "belt", "scarf", "jewellery", "jewelry",
                        "headtie", "gele"],
    "fabric":          ["ankara", "lace", "aso-oke", "fabric", "material",
                        "george"],
}

ALIASES_BY_TYPE = {
    "mini-mart":     PRODUCT_ALIASES_MINIMART,
    "pharmacy":      PRODUCT_ALIASES_PHARMACY,
    "pos-agent":     PRODUCT_ALIASES_POS,
    "restaurant":    PRODUCT_ALIASES_RESTAURANT,
    "fashion-store": PRODUCT_ALIASES_FASHION,
}


def normalize_product_name(name: str, business_type: str) -> str:
    """Standardize a product name using business-type-specific aliases."""
    if not isinstance(name, str):
        return str(name)
    name_lower = name.lower().strip()
    aliases = ALIASES_BY_TYPE.get(business_type, PRODUCT_ALIASES_MINIMART)
    for canonical, alias_list in aliases.items():
        if any(alias in name_lower for alias in alias_list):
            return canonical.title()
    return name.strip().title()


# ─────────────────────────────────────────────
# BUSINESS-TYPE SPECIFIC EXTRA METRICS
# Each function receives the cleaned df and col map,
# returns a dict of extra metrics and extra summary lines.
# ─────────────────────────────────────────────

def extras_pharmacy(df: pd.DataFrame, col: dict) -> tuple:
    """Pharmacy-specific: expiry risk and prescription vs OTC split."""
    metrics  = {}
    lines    = []
    missing  = []
    warnings = []

    # Expiry risk
    if col.get("expiry"):
        try:
            df["_expiry"] = pd.to_datetime(
                df[col["expiry"]], dayfirst=True, errors="coerce"
            )
            today        = pd.Timestamp.today()
            expiring_30  = df[df["_expiry"].between(today, today + timedelta(days=30))]
            expiring_90  = df[df["_expiry"].between(today, today + timedelta(days=90))]

            if "_revenue" in df.columns:
                val_30 = expiring_30["_revenue"].sum()
                val_90 = expiring_90["_revenue"].sum()
            else:
                val_30 = val_90 = 0

            metrics["expiry_risk"] = {
                "expiring_30_days": {
                    "count": len(expiring_30["_product"].unique())
                              if "_product" in df.columns else "unknown",
                    "value": f"₦{int(val_30):,}",
                },
                "expiring_90_days": {
                    "count": len(expiring_90["_product"].unique())
                              if "_product" in df.columns else "unknown",
                    "value": f"₦{int(val_90):,}",
                },
                "confidence": MEDIUM,
            }
            lines.append(
                f"\nExpiry risk (pharmacy-specific):"
                f"\n  Products expiring within 30 days: "
                f"{metrics['expiry_risk']['expiring_30_days']['count']} "
                f"(value: {metrics['expiry_risk']['expiring_30_days']['value']})"
                f"\n  Products expiring within 90 days: "
                f"{metrics['expiry_risk']['expiring_90_days']['count']} "
                f"(value: {metrics['expiry_risk']['expiring_90_days']['value']})"
            )
        except Exception:
            missing.append("expiry_risk")
            warnings.append("Expiry date column found but could not be parsed.")
    else:
        missing.append("expiry_risk")

    return metrics, lines, missing, warnings


def extras_pos(df: pd.DataFrame, col: dict) -> tuple:
    """POS-specific: transaction type breakdown and float usage."""
    metrics  = {}
    lines    = []
    missing  = []
    warnings = []

    if "_product" in df.columns and "_revenue" in df.columns:
        txn_breakdown = (
            df.groupby("_product")["_revenue"]
            .agg(["count", "sum"])
            .rename(columns={"count": "transactions", "sum": "total_value"})
            .sort_values("total_value", ascending=False)
        )
        total = txn_breakdown["total_value"].sum()
        metrics["transaction_types"] = {
            "value": {
                txn: {
                    "count": int(row["transactions"]),
                    "share": f"{(row['total_value'] / total * 100):.1f}%",
                    "total": f"₦{int(row['total_value']):,}",
                }
                for txn, row in txn_breakdown.iterrows()
            },
            "confidence": HIGH,
        }
        lines.append("\nTransaction type breakdown (POS-specific):")
        for txn, data in metrics["transaction_types"]["value"].items():
            lines.append(
                f"  {txn}: {data['count']} transactions, "
                f"{data['share']} of volume, {data['total']}"
            )
    else:
        missing.append("transaction_types")

    if col.get("float"):
        try:
            df["_float"] = pd.to_numeric(
                df[col["float"]]
                .astype(str)
                .str.replace(r"[₦,\s]", "", regex=True),
                errors="coerce"
            )
            avg_float = df["_float"].mean()
            min_float = df["_float"].min()
            metrics["float_analysis"] = {
                "avg_float":    f"₦{int(avg_float):,}",
                "lowest_float": f"₦{int(min_float):,}",
                "confidence":   MEDIUM,
            }
            lines.append(
                f"\nFloat analysis:"
                f"\n  Average float balance: {metrics['float_analysis']['avg_float']}"
                f"\n  Lowest recorded float: {metrics['float_analysis']['lowest_float']}"
            )
        except Exception:
            missing.append("float_analysis")
    else:
        missing.append("float_analysis")

    return metrics, lines, missing, warnings


def extras_restaurant(df: pd.DataFrame, col: dict) -> tuple:
    """Restaurant-specific: peak meal time and top dish analysis."""
    metrics  = {}
    lines    = []
    missing  = []
    warnings = []

    if "_product" in df.columns and "_revenue" in df.columns:
        dish_rev = (
            df.groupby("_product")["_revenue"]
            .sum()
            .sort_values(ascending=False)
        )
        total = dish_rev.sum()
        top_dishes = dish_rev.head(5)
        metrics["top_dishes"] = {
            "value": {
                dish: f"{(rev / total * 100):.1f}%"
                for dish, rev in top_dishes.items()
            },
            "confidence": HIGH,
        }
        lines.append("\nTop dishes by revenue share:")
        for dish, share in metrics["top_dishes"]["value"].items():
            lines.append(f"  {dish}: {share}")
    else:
        missing.append("top_dishes")

    return metrics, lines, missing, warnings


def extras_fashion(df: pd.DataFrame, col: dict) -> tuple:
    """Fashion-specific: category performance and slow-moving styles."""
    metrics  = {}
    lines    = []
    missing  = []
    warnings = []

    if col.get("category") and "_revenue" in df.columns:
        cat_rev = (
            df.groupby(col["category"])["_revenue"]
            .sum()
            .sort_values(ascending=False)
        )
        total = cat_rev.sum()
        metrics["category_performance"] = {
            "value": {
                cat: f"{(rev / total * 100):.1f}%"
                for cat, rev in cat_rev.items()
            },
            "confidence": HIGH,
        }
        lines.append("\nCategory performance:")
        for cat, share in metrics["category_performance"]["value"].items():
            lines.append(f"  {cat}: {share}")
    else:
        missing.append("category_performance")

    return metrics, lines, missing, warnings


EXTRAS_BY_TYPE = {
    "pharmacy":      extras_pharmacy,
    "pos-agent":     extras_pos,
    "restaurant":    extras_restaurant,
    "fashion-store": extras_fashion,
}


# ─────────────────────────────────────────────
# MAIN CLEANING + SUMMARY FUNCTION
# ─────────────────────────────────────────────
def clean_and_summarize(df: pd.DataFrame, business_type: str) -> dict:
    """
    Clean a raw SME sales DataFrame and compute all business metrics.

    Parameters:
        df            — raw DataFrame from uploaded CSV or Excel
        business_type — "mini-mart", "pharmacy", "pos-agent",
                        "restaurant", or "fashion-store"

    Returns:
        summary_text      (str)  — formatted summary → pass to get_diagnosis()
        metrics           (dict) — structured metrics with confidence flags
        missing_fields    (list) — fields that could not be computed
        warnings          (list) — data quality issues found
    """
    missing_fields = []
    warnings       = []
    metrics        = {}

    # ── Step 1: Normalize column names ──────────────────────────────────────
    col = normalize_columns(df)

    # ── Step 2: Parse and clean date column ─────────────────────────────────
    if col["date"]:
        try:
            parsed, n_failed, strategy = parse_dates_universal(df[col["date"]])
            df["_date"] = parsed
            if n_failed > 0:
                warnings.append(
                    f"{n_failed} rows had unreadable dates and were excluded "
                    f"(parsed using: {strategy})."
                )
            df = df.dropna(subset=["_date"])
            df["_month"]      = df["_date"].dt.month
            df["_month_name"] = df["_date"].dt.strftime("%B")
            df["_weekday"]    = df["_date"].dt.dayofweek
            df["_is_weekend"] = df["_weekday"].isin([5, 6])
            date_confidence   = HIGH if n_failed == 0 else MEDIUM
        except Exception as e:
            missing_fields.append("date")
            date_confidence = None
            warnings.append(f"Date column could not be parsed: {str(e)}")
    else:
        missing_fields.append("date")
        date_confidence = None
        warnings.append("No date column found — time-based analysis unavailable.")

    # ── Step 3: Parse and clean revenue column ───────────────────────────────
    if col["revenue"]:
        try:
            df["_revenue"] = (
                df[col["revenue"]]
                .astype(str)
                .str.replace(r"[₦,\s]", "", regex=True)
                .pipe(pd.to_numeric, errors="coerce")
            )
            df = df.dropna(subset=["_revenue"])
            df = df[df["_revenue"] > 0]
            revenue_confidence = HIGH
        except Exception:
            missing_fields.append("revenue")
            revenue_confidence = None
            warnings.append("Revenue column could not be parsed.")
    else:
        missing_fields.append("revenue")
        revenue_confidence = None
        warnings.append("No revenue column found — financial analysis unavailable.")

    # ── Step 4: Normalize product names (business-type aware) ───────────────
    if col["product"]:
        df["_product"] = df[col["product"]].apply(
            lambda x: normalize_product_name(x, business_type)
        )
    else:
        missing_fields.append("product")
        warnings.append("No product column found — product analysis unavailable.")

    # ── Step 5: Parse cost column (optional) ────────────────────────────────
    has_cost = False
    if col["cost"]:
        try:
            df["_cost"] = (
                df[col["cost"]]
                .astype(str)
                .str.replace(r"[₦,\s]", "", regex=True)
                .pipe(pd.to_numeric, errors="coerce")
            )
            has_cost = df["_cost"].notna().sum() > len(df) * 0.5
        except Exception:
            pass
    if not has_cost:
        missing_fields.append("cost_price")

    # ── Step 6: Parse quantity column ────────────────────────────────────────
    has_qty = False
    if col["quantity"]:
        try:
            df["_qty"] = pd.to_numeric(
                df[col["quantity"]], errors="coerce"
            ).fillna(0)
            has_qty = True
        except Exception:
            pass

    # ── Step 7: Total transactions + date range ──────────────────────────────
    total_transactions = len(df)
    if date_confidence:
        date_range = (
            f"{df['_date'].min().strftime('%B %d, %Y')} – "
            f"{df['_date'].max().strftime('%B %d, %Y')}"
        )
        metrics["total_transactions"] = {
            "value":      total_transactions,
            "date_range": date_range,
            "confidence": HIGH,
        }
    else:
        metrics["total_transactions"] = {
            "value":      total_transactions,
            "date_range": "unknown",
            "confidence": LOW,
        }

    # ── Step 8: Monthly daily averages ──────────────────────────────────────
    if date_confidence and revenue_confidence:
        monthly = (
            df.groupby(["_month", "_month_name"])
            .agg(total_rev=("_revenue", "sum"), days=("_date", "nunique"))
            .reset_index()
            .sort_values("_month")
        )
        monthly["daily_avg"] = (monthly["total_rev"] / monthly["days"]).round(0)
        monthly_data = {
            row["_month_name"]: {
                "daily_avg_revenue": f"₦{int(row['daily_avg']):,}",
                "total_revenue":     f"₦{int(row['total_rev']):,}",
                "active_days":       int(row["days"]),
            }
            for _, row in monthly.iterrows()
        }
        metrics["monthly_averages"] = {
            "value":      monthly_data,
            "confidence": HIGH if len(monthly) >= 3 else MEDIUM,
        }

        if len(monthly) >= 2:
            first_avg  = monthly.iloc[0]["daily_avg"]
            last_avg   = monthly.iloc[-1]["daily_avg"]
            pct_change = ((last_avg - first_avg) / first_avg * 100)
            trend      = "declining" if pct_change < -5 else \
                         "growing"   if pct_change >  5 else "stable"
            metrics["revenue_trend"] = {
                "value":      trend,
                "pct_change": f"{pct_change:+.1f}%",
                "confidence": HIGH,
            }
        else:
            missing_fields.append("revenue_trend")
    else:
        missing_fields.append("monthly_averages")
        missing_fields.append("revenue_trend")

    # ── Step 9: Weekday vs weekend revenue ──────────────────────────────────
    if date_confidence and revenue_confidence:
        weekend_rev  = df[df["_is_weekend"]]["_revenue"].sum()
        weekday_rev  = df[~df["_is_weekend"]]["_revenue"].sum()
        total_rev    = df["_revenue"].sum()
        weekend_days = df[df["_is_weekend"]]["_date"].nunique()
        weekday_days = df[~df["_is_weekend"]]["_date"].nunique()

        if weekend_days > 0 and weekday_days > 0:
            weekend_daily = weekend_rev / weekend_days
            weekday_daily = weekday_rev / weekday_days
            gap           = weekend_daily - weekday_daily
            gap_pct       = (gap / weekday_daily * 100)
            weekend_share = (weekend_rev / total_rev * 100)

            metrics["weekday_weekend_split"] = {
                "avg_weekday_daily":     f"₦{int(weekday_daily):,}",
                "avg_weekend_daily":     f"₦{int(weekend_daily):,}",
                "daily_gap":             f"₦{int(gap):,} ({gap_pct:+.1f}%)",
                "weekend_revenue_share": f"{weekend_share:.1f}%",
                "confidence":            HIGH,
            }
        else:
            missing_fields.append("weekday_weekend_split")
    else:
        missing_fields.append("weekday_weekend_split")

    # ── Step 10: Top products by revenue share ───────────────────────────────
    if col["product"] and revenue_confidence:
        product_rev = (
            df.groupby("_product")["_revenue"]
            .sum()
            .sort_values(ascending=False)
        )
        total_rev   = product_rev.sum()
        top_n       = min(5, len(product_rev))
        top_prods   = product_rev.head(top_n)
        top_3_share = (product_rev.head(3).sum() / total_rev * 100)

        metrics["top_products"] = {
            "value": {
                name: f"{(rev / total_rev * 100):.1f}%"
                for name, rev in top_prods.items()
            },
            "top_3_revenue_share": f"{top_3_share:.1f}%",
            "confidence":          HIGH,
        }
    else:
        missing_fields.append("top_products")

    # ── Step 11: Slow / dead stock detection ────────────────────────────────
    if col["product"] and date_confidence and revenue_confidence:
        cutoff          = df["_date"].max() - timedelta(days=14)
        recent_products = set(df[df["_date"] >= cutoff]["_product"].unique())
        all_products    = set(df["_product"].unique())
        dead_stock      = all_products - recent_products

        dead_stock_details = {}
        for product in dead_stock:
            prod_df   = df[df["_product"] == product]
            avg_price = prod_df["_revenue"].mean()

            # Use actual unsold quantity if available, else conservative estimate
            if has_qty:
                total_sold_qty = prod_df["_qty"].sum()
                # Estimate remaining stock as ~20% of sold qty (conservative)
                est_remaining  = max(total_sold_qty * 0.2, 10)
                low_est  = int(avg_price * est_remaining * 0.8 / 1000) * 1000
                high_est = int(avg_price * est_remaining * 1.2 / 1000) * 1000
                confidence = MEDIUM
            else:
                # No quantity data — use wider range to reflect uncertainty
                low_est  = int(avg_price * 15 / 1000) * 1000
                high_est = int(avg_price * 35 / 1000) * 1000
                confidence = LOW

            dead_stock_details[product] = {
                "last_sold":        prod_df["_date"].max().strftime("%b %d, %Y"),
                "tied_capital_est": f"₦{low_est:,}–₦{high_est:,}",
                "confidence":       confidence,
            }

        metrics["dead_stock"] = {
            "value":      dead_stock_details,
            "confidence": MEDIUM if dead_stock_details else HIGH,
        }
    else:
        missing_fields.append("dead_stock")

    # ── Step 12: Payment method breakdown ───────────────────────────────────
    if col["payment"]:
        pay_counts = df[col["payment"]].value_counts(normalize=True) * 100
        metrics["payment_methods"] = {
            "value": {
                method: f"{pct:.1f}%"
                for method, pct in pay_counts.items()
            },
            "confidence": HIGH,
        }
    else:
        missing_fields.append("payment_methods")

    # ── Step 13: Business-type specific extras ───────────────────────────────
    extra_metrics = {}
    extra_lines   = []
    if business_type in EXTRAS_BY_TYPE:
        try:
            em, el, emf, ew = EXTRAS_BY_TYPE[business_type](df, col)
            extra_metrics.update(em)
            extra_lines.extend(el)
            missing_fields.extend(emf)
            warnings.extend(ew)
        except Exception as e:
            warnings.append(
                f"Business-type specific analysis failed: {str(e)}"
            )
    metrics.update(extra_metrics)

    # ── Step 14: Build summary text for groq_client.py ──────────────────────
    summary_lines = [f"Business Type: {business_type.title()}"]

    if "total_transactions" in metrics:
        m = metrics["total_transactions"]
        summary_lines.append(
            f"Total transactions: {m['value']} ({m['date_range']})"
        )

    if "monthly_averages" in metrics:
        summary_lines.append("\nMonthly daily revenue averages:")
        for month, data in metrics["monthly_averages"]["value"].items():
            summary_lines.append(
                f"  {month}: {data['daily_avg_revenue']}/day "
                f"(over {data['active_days']} active days)"
            )

    if "revenue_trend" in metrics:
        m = metrics["revenue_trend"]
        summary_lines.append(
            f"\nRevenue trend: {m['value'].upper()} "
            f"({m['pct_change']} from first to last month)"
        )

    if "weekday_weekend_split" in metrics:
        m = metrics["weekday_weekend_split"]
        summary_lines.append(
            f"\nWeekday vs weekend revenue (pre-calculated):"
            f"\n  Average weekday daily revenue: {m['avg_weekday_daily']}"
            f"\n  Average weekend daily revenue: {m['avg_weekend_daily']}"
            f"\n  Daily gap: {m['daily_gap']}"
            f"\n  Weekend share of total revenue: {m['weekend_revenue_share']}"
        )

    if "top_products" in metrics:
        m = metrics["top_products"]
        summary_lines.append("\nTop products by revenue share (pre-calculated):")
        for product, share in m["value"].items():
            summary_lines.append(f"  {product}: {share}")
        summary_lines.append(
            f"  Top 3 combined: {m['top_3_revenue_share']} of total revenue"
        )

    if "dead_stock" in metrics and metrics["dead_stock"]["value"]:
        summary_lines.append("\nSlow / dead stock (no sales in 14+ days):")
        for product, data in metrics["dead_stock"]["value"].items():
            summary_lines.append(
                f"  {product}: last sold {data['last_sold']}, "
                f"estimated tied capital {data['tied_capital_est']} "
                f"[confidence: {data['confidence']}]"
            )

    if "payment_methods" in metrics:
        summary_lines.append("\nPayment method breakdown:")
        for method, pct in metrics["payment_methods"]["value"].items():
            summary_lines.append(f"  {method}: {pct}")

    # Business-type specific extra lines
    summary_lines.extend(extra_lines)

    if missing_fields:
        summary_lines.append(
            f"\nMissing data fields (could not be calculated): "
            f"{', '.join(missing_fields)}"
        )
        summary_lines.append(
            "Note to AI: Do not invent figures for missing fields. "
            "Acknowledge their absence clearly in the diagnosis."
        )

    if warnings:
        summary_lines.append(
            f"\nData quality notes: {'; '.join(warnings)}"
        )

    summary_text = "\n".join(summary_lines)

    return {
        "summary_text":   summary_text,
        "metrics":        metrics,
        "missing_fields": missing_fields,
        "warnings":       warnings,
    }


# ─────────────────────────────────────────────
# QUICK TEST
# Usage: python data_cleaner.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    test_data = {
        "Date":           ["2026-01-05", "2026-01-06", "2026-01-07",
                           "2026-02-10", "2026-02-15", "2026-03-03",
                           "2026-03-20", "2026-04-01", "2026-04-10",
                           "2026-04-15"],
        "Product Name":   ["Rice", "Indomie", "Tissue Paper",
                           "Rice", "Vegetable Oil", "Rice",
                           "Biscuits", "Indomie", "Rice",
                           "Vegetable Oil"],
        "Amount":         [5000, 800, 600, 5200, 3500,
                           4800, 700, 750, 5100, 3400],
        "Qty":            [2, 5, 1, 2, 1, 2, 3, 4, 2, 1],
        "Payment Method": ["Cash", "POS", "Cash", "Transfer",
                           "Cash", "POS", "Cash", "Cash",
                           "Transfer", "POS"],
    }

    df     = pd.DataFrame(test_data)
    result = clean_and_summarize(df, "mini-mart")

    print("=" * 60)
    print("SUMMARY TEXT (passed to groq_client.py):")
    print("-" * 40)
    print(result["summary_text"])
    print("\nMISSING FIELDS:", result["missing_fields"])
    print("WARNINGS:",        result["warnings"])
    print("=" * 60)

# Made with Bob
