"""
Calculates summary statistics and intercoder reliability.

Requries:
    !pip install pandas sklearn wasabi

autogenerated a markdown at /docs/intercoder_reliability.md
"""

from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score
from wasabi import MarkdownRenderer

md = MarkdownRenderer()

data_path = Path(__file__).parent.parent.parent.parent / "data" / "tagging"
docs_path = Path(__file__).parent.parent.parent.parent / "docs"


# taggers
taggers = {x.stem: pd.read_csv(x) for x in data_path.glob("*.csv")}

md.add(md.title(1, "Results from corpus tagging"))
md.add(md.title(2, "Text proportions"))
md.add("----")
# examine proportion of texts that are porn/hate/correct language:
for tagger in taggers:
    tagger_name, _, session_n, __, n_docs, date = tagger.split("_")
    df = taggers[tagger]

    md.add(f"**{tagger_name}** (Session: {session_n})")
    md.add(
        f"- *Date: {date}*"
        + f"\n- *Sentences tagged: {len(df)}*"
        + f"\n- *Documents tagged: {n_docs}*"
    )

    n_char = sum(len(t) for t in df["text"].values)
    t = "Proportions:\n"
    for cat in sorted(df["category"].unique()):
        cat_text = df["text"][df["category"] == cat].values
        n_char_cat = sum(len(t) for t in cat_text)
        t += f"\n- {n_char_cat/n_char*100:.2f}% of characters is `{cat}`"

    cat_text = df["text"][df["is_porn"] == True].values
    n_char_cat = sum(len(t) for t in cat_text)
    t += f"\n- {n_char_cat/n_char*100:.2f}% of characters is porn"

    cat_text = df["text"][df["is_offensive"] == True].values
    n_char_cat = sum(len(t) for t in cat_text)
    t += f"\n- {n_char_cat/n_char*100:.2f}% of characters is offensive"
    md.add(t)

md.add(md.title(2, "Definitions"))

md.add("- `wrong_language`: Not Danish")
md.add("- `skipped`: Unsure of category")
md.add(
    "- `correct_language`: Danish text where at least 80\% of the text is reasonable "
    + "sentences."
)
md.add(
    "- `not_language`: Text where less than 80\% of the text is reasonable sentences."
    + " Takes priority over wrong_language."
)

md.add(md.title(2, "Intercoder Reliability"))
md.add("----")

# create all possible pairs
pairs = []
for i, tagger in enumerate(taggers):
    for other_tagger in list(taggers)[i + 1 :]:
        pairs.append((tagger, other_tagger))

# calculate intercoder reliability
for pair in pairs:
    tagger1, tagger2 = pair
    tagger1_name, _, session_n1, __, n_docs1, date1 = tagger1.split("_")
    tagger2_name, _, session_n2, __, n_docs2, date2 = tagger2.split("_")
    md.add(
        f"**{tagger1_name}** (Session: {session_n1}) vs **{tagger2_name}** - (Session: {session_n2})"
    )
    # merge
    df = pd.merge(taggers[pair[0]], taggers[pair[1]], on="text", suffixes=("_1", "_2"))
    kappa = cohen_kappa_score(df["category_1"], df["category_2"])
    md.add(f"- Cohen's Kappa: {kappa:.4f}")

print(md.text)
# write to file
with open(docs_path / "intercoder_reliability.md", "w") as f:
    f.write(md.text)
