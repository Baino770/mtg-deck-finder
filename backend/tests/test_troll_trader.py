from scraper.troll_trader import TrollTraderScraper


def test_troll_trader_parses_explicit_quantities_from_html():
    html = """
    <ul>
      <li class="product">
        <h4 class="name">Lightning Bolt</h4>
        <a itemprop="url" href="/lightning-bolt"></a>
        <div class="variant-row row">
          <span class="variant-short-info">Near Mint, English, 3 In Stock</span>
          <span class="regular price">£1.25</span>
        </div>
        <div class="variant-row row">
          <span class="variant-short-info">Light Play, English</span>
          <span class="regular price">£1.10</span>
        </div>
        <div class="variant-row row">
          <span class="variant-short-info">Played, English, 0 In Stock</span>
          <span class="regular price">£0.90</span>
        </div>
      </li>
    </ul>
    """
    scraper = TrollTraderScraper()

    results = scraper._TrollTraderScraper__parse_page(html)

    assert len(results) == 2
    assert results[0]["available_quantity"] == 3
    assert results[0]["in_stock"] is True
    assert results[1]["available_quantity"] is None
    assert results[1]["in_stock"] is True