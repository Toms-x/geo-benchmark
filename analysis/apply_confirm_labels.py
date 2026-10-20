"""
Fills analysis/domain_labels_confirm.csv using each site's main business.
Labels were assigned from the domain names only, before any confirmation results were seen.
Only blank cells are filled. Existing labels are never overwritten.
"""
import pandas as pd

PATH = "analysis/domain_labels_confirm.csv"

LABELS = {
    "exchange": [
        "banxa.com", "blog.uniswap.org", "changenow.io", "coinmerce.io", "coinswitch.co",
        "cow.fi", "cube.exchange", "dydx.xyz", "gemini.com", "help.coinbase.com",
        "help.crypto.com", "lcx.com", "moonpay.com", "mudrex.com", "osl.com",
        "paybis.com", "support.kraken.com", "weex.com",
    ],
    "price_tracker": [
        "coinlore.com", "coinpaprika.com", "cryptorank.io", "lookintobitcoin.com",
        "marketbeat.com", "markets.businessinsider.com", "newhedge.io", "studio.glassnode.com",
    ],
    "education_media": [
        "247wallst.com", "airdropalert.com", "coinpaper.com", "cointelegraph.com",
        "cryptomaniaks.com", "cryptomantiq.com", "cryptoslate.com", "cryptoticker.io",
        "en.wikipedia.org", "financefeeds.com", "fxempire.com", "investinglive.com",
        "nftevening.com", "pcmag.com", "theblock.co", "thestreet.com",
    ],
    "finance_institution": [
        "adyen.com", "airwallex.com", "americanexpress.com", "bis.org", "bitpay.com",
        "capital.com", "chase.com", "checkout.com", "coingate.com", "coinshares.com",
        "plisio.net", "pnc.com", "revolut.com", "schwab.com", "sec.gov",
        "us.etrade.com", "usbank.com", "vaneck.com", "worldfirst.com",
    ],
    "other": [
        "alphapoint.com", "altrady.com", "arxiv.org", "blockchain.com", "chain.link",
        "coinledger.io", "congress.gov", "elliptic.co", "ethereum.org", "experian.com",
        "finary.com", "finst.com", "galaxy.com", "getswoopr.com", "github.com",
        "help.blockstream.com", "ibm.com", "info.arkm.com", "injective.com", "maketo.com",
        "mckinsey.com", "metamask.io", "nexo.com", "nownodes.io", "phantom.com",
        "pluang.com", "pwc.com", "sites.google.com", "solflare.com", "stocktwits.com",
        "tokentax.co", "tradingkey.com", "trustwallet.com", "world.org", "xe.com",
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