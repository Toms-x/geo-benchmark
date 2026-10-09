import pandas as pd

LABELS = {
    "binance.com": "exchange", "kraken.com": "exchange", "bybit.com": "exchange",
    "okx.com": "exchange", "crypto.com": "exchange", "gate.com": "exchange",
    "coinbase.com": "exchange", "bitget.com": "exchange", "bingx.com": "exchange",
    "bit.com": "exchange", "mexc.com": "exchange", "binance.us": "exchange",
    "btcc.com": "exchange", "bitstamp.net": "exchange", "bitpanda.com": "exchange",
    "phemex.com": "exchange", "changelly.com": "exchange",

    "coinmarketcap.com": "price_tracker", "coingecko.com": "price_tracker",
    "finance.yahoo.com": "price_tracker", "tradingview.com": "price_tracker",
    "coincodex.com": "price_tracker", "investing.com": "price_tracker",

    "investopedia.com": "education_media", "forbes.com": "education_media",
    "coinbureau.com": "education_media", "nerdwallet.com": "education_media",
    "coindesk.com": "education_media", "finder.com": "education_media",
    "britannica.com": "education_media", "cnbc.com": "education_media",
    "cryptonews.com": "education_media", "bitdegree.org": "education_media",
    "blockchain-council.org": "education_media", "tradersunion.com": "education_media",
    "coingape.com": "education_media", "news.bitcoin.com": "education_media",
    "coingabbar.com": "education_media", "corporatefinanceinstitute.com": "education_media",
    "coinspeaker.com": "education_media", "money.com": "education_media",
    "crypto.news": "education_media", "webopedia.com": "education_media",
    "reuters.com": "education_media",

    "stripe.com": "finance_institution", "fidelity.com": "finance_institution",
    "investor.gov": "finance_institution", "paypal.com": "finance_institution",
    "wise.com": "finance_institution", "robinhood.com": "finance_institution",
    "ig.com": "finance_institution",

    "ledger.com": "other", "bitcoinfoundation.org": "other", "cointracker.com": "other",
    "spark.money": "other", "datawallet.com": "other", "guarda.com": "other",
    "cryptohopper.com": "other", "privacy.com": "other", "bitcoin.com": "other",
}

df = pd.read_csv("analysis/domain_labels.csv")
df["domain_type"] = df["domain"].map(LABELS).fillna(df["domain_type"])
df["domain_type"] = df["domain_type"].replace("", "other")
unmatched = df[~df["domain"].isin(LABELS)]
if len(unmatched):
    print("Not in the label dict, set to 'other':")
    print(unmatched["domain"].tolist())
df.to_csv("analysis/domain_labels.csv", index=False)
print("Saved. Type counts:")
print(df["domain_type"].value_counts())