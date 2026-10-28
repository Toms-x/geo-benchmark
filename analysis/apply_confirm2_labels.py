"""
Fills analysis/domain_labels_confirm2.csv using each site's main business.
Labels were assigned from the domain names only, before any confirmation 2 results were seen.
Same rules as earlier stages. Only blank cells are filled. Existing labels are never overwritten.
"""
import pandas as pd

PATH = "analysis/domain_labels_confirm2.csv"

LABELS = {
    "exchange": [
        "river.com",
    ],
    "price_tracker": [
        "bitbo.io", "sg.finance.yahoo.com", "tradingeconomics.com", "uk.finance.yahoo.com",
    ],
    "education_media": [
        "altcoinbuzz.io", "bankrate.com", "benzinga.com", "blockchainreporter.net", "bloomberg.com",
        "businessinsider.com", "ccn.com", "cnn.com", "coursera.org", "cryptonews.net",
        "cryptopolitan.com", "dailyforex.com", "economictimes.indiatimes.com", "fortune.com", "ft.com",
        "global.morningstar.com", "gobankingrates.com", "ground.news", "guru99.com", "marketwatch.com",
        "milkroad.com", "money.usnews.com", "theglobeandmail.com", "tokenpost.com", "usethebitcoin.com",
        "usnews.com", "wsj.com",
    ],
    "finance_institution": [
        "capitalone.com", "cftc.gov", "cmegroup.com", "consumer.ftc.gov", "consumerfinance.gov",
        "ecb.europa.eu", "etoro.com", "home.saxo", "interactivebrokers.com", "invesco.com",
        "ishares.com", "mastercard.com", "moomoo.com", "morganstanley.com", "nasdaq.com",
        "ofx.com", "pepperstone.com", "remitly.com", "santanderbank.com", "skrill.com",
        "sofi.com", "us.plus500.com", "westernunion.com", "xoom.com",
    ],
    "other": [
        "ato.gov.au", "chainalysis.com", "egr.msu.edu", "gemwallet.com", "gov.uk",
        "irs.gov", "koinly.io", "openpr.com", "perplexity.ai", "reddit.com",
        "solana.com", "support.bitcoin.com", "support.nexo.com", "tax.thomsonreuters.com",
        "turbotax.intuit.com", "youtube.com",
    ],
}

lookup = {d: t for t, ds in LABELS.items() for d in ds}
assert len(lookup) == sum(len(v) for v in LABELS.values()), "a domain is listed under two labels"

df = pd.read_csv(PATH)
df["domain_type"] = df["domain_type"].astype("object")
blank = df["domain_type"].isna() | (df["domain_type"].astype(str).str.strip() == "")
df.loc[blank, "domain_type"] = df.loc[blank, "domain"].map(lookup)
df.to_csv(PATH, index=False)

still = df[df["domain_type"].isna()]["domain"].tolist()
unused = sorted(set(lookup) - set(df["domain"]))
print("Rows:", len(df))
print("Labels:", df["domain_type"].value_counts().to_dict())
print("Still blank (add by hand):", still)
print("In the script but not in the file:", unused)