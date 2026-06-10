"""
FeedLoop AI - Data Science Analytics Engine
============================================
Implements core DS concepts:
  1. EDA             - Exploratory data analysis on feedback data
  2. Time Series     - Feedback volume & sentiment trends over time
  3. Statistical     - Mean, std dev, distribution analysis
  4. Churn Risk      - Customer churn risk scoring
  5. Anomaly Detect  - Z-score based spike detection

Tech Stack: Pandas, NumPy, Matplotlib, Seaborn
"""

import io
import base64
import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from sqlalchemy.orm import Session
from database import FeedbackItem

# ─── Styling ────────────────────────────────────────────────────────────────
sns.set_theme(style="darkgrid", palette="muted")
COLORS = {
    "primary":  "#6366f1",
    "danger":   "#ef4444",
    "warning":  "#f59e0b",
    "success":  "#10b981",
    "info":     "#3b82f6",
    "muted":    "#64748b",
}


def _fig_to_base64(fig: plt.Figure) -> str:
    """Convert a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                facecolor=fig.get_facecolor(), dpi=120)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def _load_dataframe(db: Session) -> pd.DataFrame:
    """Load all feedback items from PostgreSQL into a Pandas DataFrame."""
    rows = db.query(FeedbackItem).all()
    if not rows:
        return pd.DataFrame()

    data = [{
        "id":            r.id,
        "raw_text":      r.raw_text,
        "source":        r.source,
        "customer_email": r.customer_email or "anonymous",
        "category":      r.category,
        "feedback_type": r.feedback_type,
        "urgency_score": r.urgency_score,
        "ai_summary":    r.ai_summary,
        "status":        r.status,
        "created_at":    r.created_at,
    } for r in rows]

    df = pd.DataFrame(data)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["date"] = df["created_at"].dt.date
    df["week"] = df["created_at"].dt.to_period("W").apply(lambda r: r.start_time)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SUMMARY STATISTICS  (EDA + Statistical Analysis)
# ═══════════════════════════════════════════════════════════════════════════════

def get_summary_stats(db: Session) -> dict:
    """
    Core EDA: computes descriptive statistics on urgency scores
    and distributions across categories and types.
    """
    df = _load_dataframe(db)
    if df.empty:
        return {"error": "No data available"}

    urgency = df["urgency_score"]

    # Statistical analysis
    stats = {
        "total_feedback":     int(len(df)),
        "mean_urgency":       round(float(urgency.mean()), 2),
        "median_urgency":     round(float(urgency.median()), 2),
        "std_urgency":        round(float(urgency.std()), 2),
        "max_urgency":        int(urgency.max()),
        "min_urgency":        int(urgency.min()),
        "category_counts":    df["category"].value_counts().to_dict(),
        "type_counts":        df["feedback_type"].value_counts().to_dict(),
        "status_counts":      df["status"].value_counts().to_dict(),
        "source_counts":      df["source"].value_counts().to_dict(),
        "high_urgency_count": int((urgency >= 4).sum()),
        "resolved_rate":      round(float((df["status"] == "Resolved").sum() / len(df) * 100), 1),
    }
    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# 2. TIME SERIES TREND ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def get_trend_chart(db: Session) -> str:
    """
    Time Series Analysis: plots daily feedback volume and
    7-day rolling average urgency score over time.
    Returns base64 PNG.
    """
    df = _load_dataframe(db)
    if df.empty or len(df) < 2:
        return ""

    daily = df.groupby("date").agg(
        volume=("id", "count"),
        avg_urgency=("urgency_score", "mean")
    ).reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")

    # 7-day rolling average for smoothing
    daily["rolling_urgency"] = daily["avg_urgency"].rolling(window=3, min_periods=1).mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), facecolor="#0f172a")
    for ax in [ax1, ax2]:
        ax.set_facecolor("#1e293b")
        for spine in ax.spines.values():
            spine.set_color("#334155")
        ax.tick_params(colors="#94a3b8")
        ax.xaxis.label.set_color("#94a3b8")
        ax.yaxis.label.set_color("#94a3b8")
        ax.title.set_color("#e2e8f0")

    # Volume bars
    ax1.bar(daily["date"], daily["volume"], color=COLORS["primary"], alpha=0.8, width=0.8)
    ax1.set_title("Daily Feedback Volume", fontweight="bold")
    ax1.set_ylabel("Tickets")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate()

    # Rolling urgency line
    ax2.plot(daily["date"], daily["avg_urgency"], color=COLORS["muted"],
             alpha=0.4, linewidth=1, label="Daily Avg")
    ax2.plot(daily["date"], daily["rolling_urgency"], color=COLORS["danger"],
             linewidth=2.5, label="3-Day Rolling Avg")
    ax2.axhline(y=3.5, color=COLORS["warning"], linestyle="--",
                linewidth=1, alpha=0.6, label="High Urgency Threshold")
    ax2.set_title("Urgency Score Trend", fontweight="bold")
    ax2.set_ylabel("Avg Urgency")
    ax2.set_ylim(0, 5.5)
    ax2.legend(facecolor="#1e293b", labelcolor="#e2e8f0", fontsize=8)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate()

    plt.tight_layout(pad=2)
    return _fig_to_base64(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CATEGORY HOTSPOT ANALYSIS (EDA Visualization)
# ═══════════════════════════════════════════════════════════════════════════════

def get_category_chart(db: Session) -> str:
    """
    EDA: heatmap of average urgency score per category × feedback type.
    Identifies which product areas generate the most critical issues.
    Returns base64 PNG.
    """
    df = _load_dataframe(db)
    if df.empty:
        return ""

    pivot = df.pivot_table(
        values="urgency_score",
        index="category",
        columns="feedback_type",
        aggfunc="mean"
    ).fillna(0).round(1)

    fig, ax = plt.subplots(figsize=(8, 4), facecolor="#0f172a")
    ax.set_facecolor("#1e293b")

    sns.heatmap(
        pivot, ax=ax, annot=True, fmt=".1f", cmap="YlOrRd",
        linewidths=0.5, linecolor="#334155",
        cbar_kws={"shrink": 0.8}
    )
    ax.set_title("Avg Urgency: Category × Feedback Type",
                 color="#e2e8f0", fontweight="bold", pad=12)
    ax.tick_params(colors="#94a3b8")
    ax.set_xlabel("Feedback Type", color="#94a3b8")
    ax.set_ylabel("Category", color="#94a3b8")

    plt.tight_layout()
    return _fig_to_base64(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CUSTOMER CHURN RISK SCORING (Predictive Analytics)
# ═══════════════════════════════════════════════════════════════════════════════

def get_churn_risk(db: Session) -> list[dict]:
    """
    Predictive Analytics: scores each customer's churn risk based on:
      - Average urgency score (higher = worse experience)
      - Number of bug reports submitted (higher = more frustrated)
      - Ratio of unresolved tickets (higher = poor support response)
      - Recency: how recently did they complain (recent = higher risk)

    Risk score formula (0–100):
      urgency_weight (40) + bug_weight (25) + unresolved_weight (25) + recency_weight (10)
    """
    df = _load_dataframe(db)
    if df.empty:
        return []

    # Filter out anonymous users
    df_customers = df[df["customer_email"] != "anonymous"].copy()
    if df_customers.empty:
        return []

    now = pd.Timestamp.utcnow()

    def score_customer(group):
        avg_urgency       = group["urgency_score"].mean()
        bug_count         = (group["feedback_type"] == "Bug").sum()
        total             = len(group)
        unresolved_ratio  = (group["status"] != "Resolved").sum() / total
        last_seen         = group["created_at"].max()
        days_since        = max((now - last_seen).days, 0)
        recency_score     = max(0, 10 - days_since)   # Higher if recent

        # Weighted score (0-100)
        raw = (
            (avg_urgency / 5) * 40 +
            min(bug_count / 5, 1) * 25 +
            unresolved_ratio * 25 +
            (recency_score / 10) * 10
        )
        risk = round(min(raw, 100), 1)

        if risk >= 70:
            level = "High"
        elif risk >= 40:
            level = "Medium"
        else:
            level = "Low"

        return pd.Series({
            "total_tickets":      int(total),
            "bug_count":          int(bug_count),
            "avg_urgency":        round(float(avg_urgency), 1),
            "unresolved_ratio":   round(float(unresolved_ratio * 100), 1),
            "churn_risk_score":   risk,
            "risk_level":         level,
        })

    result = df_customers.groupby("customer_email").apply(score_customer).reset_index()
    result = result.sort_values("churn_risk_score", ascending=False)

    return result.to_dict(orient="records")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. ANOMALY DETECTION (Z-Score Based)
# ═══════════════════════════════════════════════════════════════════════════════

def get_anomalies(db: Session) -> dict:
    """
    Anomaly Detection: uses Z-score to identify days where
    feedback volume or average urgency spiked abnormally.

    Z-score > 2.0 = anomaly (statistically significant spike)
    """
    df = _load_dataframe(db)
    if df.empty or len(df) < 5:
        return {"volume_anomalies": [], "urgency_anomalies": []}

    daily = df.groupby("date").agg(
        volume=("id", "count"),
        avg_urgency=("urgency_score", "mean")
    ).reset_index()

    if len(daily) < 3:
        return {"volume_anomalies": [], "urgency_anomalies": []}

    # Z-score calculation using NumPy
    daily["volume_z"]  = np.abs(
        (daily["volume"] - daily["volume"].mean()) / (daily["volume"].std() + 1e-9)
    )
    daily["urgency_z"] = np.abs(
        (daily["avg_urgency"] - daily["avg_urgency"].mean()) / (daily["avg_urgency"].std() + 1e-9)
    )

    THRESHOLD = 1.8  # Z-score threshold for anomaly

    volume_anom = daily[daily["volume_z"] > THRESHOLD][
        ["date", "volume", "volume_z"]
    ].copy()
    volume_anom["date"] = volume_anom["date"].astype(str)
    volume_anom["volume_z"] = volume_anom["volume_z"].round(2)

    urgency_anom = daily[daily["urgency_z"] > THRESHOLD][
        ["date", "avg_urgency", "urgency_z"]
    ].copy()
    urgency_anom["date"]       = urgency_anom["date"].astype(str)
    urgency_anom["avg_urgency"]= urgency_anom["avg_urgency"].round(2)
    urgency_anom["urgency_z"]  = urgency_anom["urgency_z"].round(2)

    return {
        "volume_anomalies":  volume_anom.to_dict(orient="records"),
        "urgency_anomalies": urgency_anom.to_dict(orient="records"),
    }
