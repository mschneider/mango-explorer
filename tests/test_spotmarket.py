from .context import mango

from decimal import Decimal
from solana.publickey import PublicKey


def test_spot_market_constructor():
    address = PublicKey("11111111111111111111111111111114")
    base = mango.Token("BASE", "Base Token", PublicKey("11111111111111111111111111111115"), Decimal(7))
    quote = mango.Token("QUOTE", "Quote Token", PublicKey("11111111111111111111111111111116"), Decimal(9))
    actual = mango.SpotMarket(base, quote, address)
    assert actual is not None
    assert actual.logger is not None
    assert actual.address == address
    assert actual.base == base
    assert actual.quote == quote


def test_spot_market_lookup():
    data = {
        "tokens": [
            {
                "chainId": 101,
                "address": "So11111111111111111111111111111111111111112",
                "symbol": "SOL",
                "name": "Wrapped SOL",
                "decimals": 9,
                "logoURI": "https://cdn.jsdelivr.net/gh/trustwallet/assets@master/blockchains/solana/info/logo.png",
                "tags": [],
                "extensions": {
                    "website": "https://solana.com/",
                    "serumV3Usdc": "9wFFyRfZBsuAha4YcuxcXLKwMxJR43S7fPfQLusDBzvT",
                    "serumV3Usdt": "HWHvQhFmJB3NUcu1aihKmrKegfVxBEHzwVX6yZCKEsi1",
                    "coingeckoId": "solana"
                }
            },
            {
                "chainId": 101,
                "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "symbol": "USDC",
                "name": "USD Coin",
                "decimals": 6,
                "logoURI": "https://cdn.jsdelivr.net/gh/solana-labs/token-list@main/assets/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/logo.png",
                "tags": [
                    "stablecoin"
                ],
                "extensions": {
                    "website": "https://www.centre.io/",
                    "coingeckoId": "usd-coin"
                }
            },
            {
                "chainId": 101,
                "address": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
                "symbol": "BTC",
                "name": "Wrapped Bitcoin (Sollet)",
                "decimals": 6,
                "logoURI": "https://cdn.jsdelivr.net/gh/trustwallet/assets@master/blockchains/bitcoin/info/logo.png",
                "tags": [
                    "wrapped-sollet",
                    "ethereum"
                ],
                "extensions": {
                    "bridgeContract": "https://etherscan.io/address/0xeae57ce9cc1984f202e15e038b964bb8bdf7229a",
                    "serumV3Usdc": "A8YFbxQYFVqKZaoYJLLUVcQiWP7G2MeEgW5wsAQgMvFw",
                    "serumV3Usdt": "C1EuT9VokAKLiW7i2ASnZUvxDoKuKkCpDDeNxAptuNe4",
                    "coingeckoId": "bitcoin"
                }
            },
            {
                "chainId": 101,
                "address": "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk",
                "symbol": "ETH",
                "name": "Wrapped Ethereum (Sollet)",
                "decimals": 6,
                "logoURI": "https://cdn.jsdelivr.net/gh/trustwallet/assets@master/blockchains/ethereum/assets/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/logo.png",
                "tags": [
                    "wrapped-sollet",
                    "ethereum"
                ],
                "extensions": {
                    "bridgeContract": "https://etherscan.io/address/0xeae57ce9cc1984f202e15e038b964bb8bdf7229a",
                    "serumV3Usdc": "4tSvZvnbyzHXLMTiFonMyxZoHmFqau1XArcRCVHLZ5gX",
                    "serumV3Usdt": "7dLVkUfBVfCGkFhSXDCq1ukM9usathSgS716t643iFGF",
                    "coingeckoId": "ethereum"
                }
            },
            {
                "chainId": 101,
                "address": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
                "symbol": "USDT",
                "name": "USDT",
                "decimals": 6,
                "logoURI": "https://cdn.jsdelivr.net/gh/solana-labs/explorer/public/tokens/usdt.svg",
                "tags": [
                    "stablecoin"
                ],
                "extensions": {
                    "website": "https://tether.to/",
                    "coingeckoId": "tether"
                }
            },
            {
                "chainId": 101,
                "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "symbol": "USDC",
                "name": "USD Coin",
                "decimals": 6,
                "logoURI": "https://cdn.jsdelivr.net/gh/solana-labs/token-list@main/assets/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/logo.png",
                "tags": [
                    "stablecoin"
                ],
                "extensions": {
                    "website": "https://www.centre.io/",
                    "coingeckoId": "usd-coin"
                }
            }
        ]
    }
    actual = mango.SpotMarketLookup(data)
    assert actual is not None
    assert actual.logger is not None
    assert actual.find_by_symbol("ETH/USDT") is not None
    assert actual.find_by_symbol("ETH/USDT").address == PublicKey("7dLVkUfBVfCGkFhSXDCq1ukM9usathSgS716t643iFGF")
    assert actual.find_by_symbol("BTC/USDC") is not None
    assert actual.find_by_symbol("BTC/USDC").address == PublicKey("A8YFbxQYFVqKZaoYJLLUVcQiWP7G2MeEgW5wsAQgMvFw")


def test_spot_market_lookups_with_full_data():
    market_lookup = mango.SpotMarketLookup.load(mango.TokenLookup.DEFAULT_FILE_NAME)
    eth_usdt = market_lookup.find_by_symbol("ETH/USDT")
    assert eth_usdt.base.symbol == "ETH"
    assert eth_usdt.quote.symbol == "USDT"
    assert eth_usdt.address == PublicKey("7dLVkUfBVfCGkFhSXDCq1ukM9usathSgS716t643iFGF")

    btc_usdc = market_lookup.find_by_symbol("BTC/USDC")
    assert btc_usdc.base.symbol == "BTC"
    assert btc_usdc.quote.symbol == "USDC"
    assert btc_usdc.address == PublicKey("A8YFbxQYFVqKZaoYJLLUVcQiWP7G2MeEgW5wsAQgMvFw")

    non_existant_market = market_lookup.find_by_symbol("ETH/BTC")
    assert non_existant_market is None  # No such market

    srm_usdc = market_lookup.find_by_address("ByRys5tuUWDgL73G8JBAEfkdFf8JWBzPBDHsBVQ5vbQA")
    assert srm_usdc.base.symbol == "SRM"
    assert srm_usdc.quote.symbol == "USDC"
    assert srm_usdc.address == PublicKey("ByRys5tuUWDgL73G8JBAEfkdFf8JWBzPBDHsBVQ5vbQA")
