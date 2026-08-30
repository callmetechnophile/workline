"""
Unit tests for HTML document parser (boilerplate stripping, tables, headings).
"""

from research_agents.document_processing_agent.parsers.html_parser import HTMLDocumentParser


def test_html_parser_boilerplate_removal_and_table():
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32-S3 Hardware Technical Specifications</title>
        <meta name="author" content="Espressif Systems">
        <script>console.log("tracking script");</script>
        <style>.body { background: #fff; }</style>
    </head>
    <body>
        <nav class="navigation-bar"><a href="/">Home</a></nav>
        <div class="cookie-banner">Please accept all cookies.</div>
        <article>
            <h1>ESP32-S3 Overview</h1>
            <p>The ESP32-S3 microcontroller operates at 3.3 V supply voltage with dual-core Xtensa CPU.</p>
            <h2>Electrical Ratings</h2>
            <table>
                <tr><th>Parameter</th><th>Value</th><th>Unit</th></tr>
                <tr><td>Supply Voltage</td><td>3.3</td><td>V</td></tr>
                <tr><td>Peak Current</td><td>500</td><td>mA</td></tr>
            </table>
            <p>For more details, see <a href="https://github.com/espressif/esp-idf">ESP-IDF GitHub repository</a>.</p>
        </article>
        <footer class="site-footer">Copyright 2024</footer>
    </body>
    </html>
    """

    parser = HTMLDocumentParser()
    meta, blocks, tables, figures, links, refs = parser.parse(
        content_bytes=sample_html.encode("utf-8"),
        source_url="https://espressif.com/esp32-s3",
    )

    assert meta.title == "ESP32-S3 Hardware Technical Specifications"
    assert "Espressif Systems" in meta.authors

    # Verify boilerplate stripped
    block_texts = " ".join(b.text for b in blocks)
    assert "cookie" not in block_texts.lower()
    assert "tracking script" not in block_texts
    assert "Home" not in block_texts

    # Verify table extracted
    assert len(tables) == 1
    assert "Supply Voltage" in tables[0].markdown
    assert "500" in tables[0].markdown

    # Verify links
    assert len(links) >= 1
    assert links[0].url == "https://github.com/espressif/esp-idf"
    assert links[0].link_type == "github"
