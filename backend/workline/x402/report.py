"""
Auditable PDF Report Generator for Workline x402 Settled Procurement.

Structure & Immutability:
- Header: Workline AI Procurement Payment Report
- Itemized BOM Table (Part Number, Description, Qty, Unit Price USD, Line Total USD)
- Total Section: USD ($X.XX) and USDC (X.XX USDC)
- INR Equivalent Section:
  - If CoinGecko succeeded: Approximate INR Equivalent (₹X,XXX.XX) at timestamp with source
  - If CoinGecko failed: "Unavailable" (Reason: Exchange-rate service unavailable)
- Payment Proof:
  - Network (Algorand Mainnet / Testnet)
  - Asset: USDC
  - Amount: X.XX USDC
  - Status: SETTLED
  - Transaction ID: <actual tx hash>
  - Verification Link: Lora / Algorand Explorer URL
- Informational Disclaimer: Settled payment is USDC. INR is informational only.
"""

from decimal import Decimal, ROUND_HALF_UP
import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from backend.workline.procurement.bom_payment import AuthoritativeBom, PaymentQuote, quantize_money
from backend.workline.x402.coingecko import CoinGeckoRate

_EXPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "exports",
)
os.makedirs(_EXPORTS_DIR, exist_ok=True)


def get_explorer_url(network: str, tx_id: Optional[str]) -> str:
    """Generates the authoritative explorer / Lora verification link based on network."""
    if not tx_id:
        return "Transaction ID pending verification"

    is_testnet = "testnet" in network.lower()
    if is_testnet:
        return f"https://lora.algokit.io/testnet/transaction/{tx_id}"
    return f"https://lora.algokit.io/mainnet/transaction/{tx_id}"


class BomPaymentReportArtifact(BaseModel):
    """Immutable record of the compiled procurement payment report."""
    artifact_id: str = Field(default_factory=lambda: f"art_rep_{uuid.uuid4().hex[:12]}")
    quote_id: str
    bom_id: str
    project_id: str
    filename: str
    filepath: str
    sha256: str
    bom_total_usd: float
    settled_amount_usdc: float
    approx_inr_total: Optional[float] = None
    inr_available: bool = True
    exchange_rate: Optional[float] = None
    exchange_rate_source: Optional[str] = None
    exchange_rate_timestamp: Optional[str] = None
    transaction_id: Optional[str] = None
    explorer_url: str
    network: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BomPaymentReportEngine:
    """Generates auditable, high-resolution PDF payment reports via ReportLab."""

    @classmethod
    def generate_pdf_report(
        cls,
        bom: AuthoritativeBom,
        quote: PaymentQuote,
        rate: Optional[CoinGeckoRate] = None,
    ) -> BomPaymentReportArtifact:
        """
        Compiles the authoritative PDF document for a settled BOM payment quote.
        """
        artifact_id = f"art_rep_{uuid.uuid4().hex[:8]}"
        filename = f"Workline_BOM_Payment_{quote.quote_id}_{artifact_id}.pdf"
        filepath = os.path.join(_EXPORTS_DIR, filename)

        # 1. Compute financial values using Decimal
        usd_total_dec = quantize_money(quote.amount_usd)
        usdc_total_dec = quantize_money(quote.amount_usdc)

        inr_available = rate is not None and rate.available and rate.rate_decimal is not None
        approx_inr_dec: Optional[Decimal] = None
        if inr_available and rate and rate.rate_decimal:
            approx_inr_dec = (usdc_total_dec * rate.rate_decimal).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        explorer_link = get_explorer_url(quote.network, quote.transaction_id)

        # 2. Build PDF Elements
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            alignment=TA_LEFT,
        )

        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=TA_LEFT,
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=10,
            spaceAfter=6,
        )

        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0f172a"),
        )

        cell_header = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.white,
        )

        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b"),
        )

        story = []

        # --- Header ---
        story.append(Paragraph("WORKLINE AI", title_style))
        story.append(Paragraph("PROCUREMENT PAYMENT REPORT", subtitle_style))
        story.append(Spacer(1, 8))
        story.append(
            Paragraph(
                f"<b>Project ID:</b> {quote.project_id} &nbsp;|&nbsp; "
                f"<b>BOM ID:</b> {quote.bom_id} &nbsp;|&nbsp; "
                f"<b>Quote ID:</b> {quote.quote_id} &nbsp;|&nbsp; "
                f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                subtitle_style,
            )
        )
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=12))

        # --- Section 1: Itemized Bill of Materials ---
        story.append(Paragraph("ITEMIZED BILL OF MATERIALS", section_heading))

        table_data = [
            [
                Paragraph("Part Number", cell_header),
                Paragraph("Description", cell_header),
                Paragraph("Qty", cell_header),
                Paragraph("Unit Price (USD)", cell_header),
                Paragraph("Line Total (USD)", cell_header),
            ]
        ]

        for item in bom.items:
            table_data.append(
                [
                    Paragraph(item.part_number, cell_style),
                    Paragraph(item.description or "—", cell_style),
                    Paragraph(str(item.quantity), cell_style),
                    Paragraph(f"${item.unit_price_usd:.2f}", cell_style),
                    Paragraph(f"${item.line_total_usd:.2f}", cell_style),
                ]
            )

        bom_table = Table(table_data, colWidths=[120, 190, 45, 80, 85])
        bom_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ])
        )
        story.append(bom_table)
        story.append(Spacer(1, 14))

        # --- Section 2: Totals ---
        totals_data = [
            [
                Paragraph("<b>AUTHORITATIVE BOM TOTAL (USD):</b>", cell_style),
                Paragraph(f"<b>${usd_total_dec:.2f} USD</b>", cell_style),
            ],
            [
                Paragraph("<b>USDC SETTLEMENT AMOUNT:</b>", cell_style),
                Paragraph(f"<b>{usdc_total_dec:.2f} USDC</b>", cell_style),
            ],
        ]
        totals_table = Table(totals_data, colWidths=[250, 270])
        totals_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(totals_table)
        story.append(Spacer(1, 14))

        # --- Section 3: Approximate INR Equivalent (Informational Only) ---
        story.append(Paragraph("INR EQUIVALENT (INFORMATIONAL ONLY)", section_heading))

        if inr_available and approx_inr_dec is not None and rate is not None:
            inr_content = [
                [
                    Paragraph("<b>Approximate INR Equivalent:</b>", cell_style),
                    Paragraph(f"<b>≈ ₹{approx_inr_dec:,.2f} INR</b> (Approx., at time of payment)", cell_style),
                ],
                [
                    Paragraph("<b>Exchange Rate:</b>", cell_style),
                    Paragraph(f"1 USDC ≈ ₹{rate.rate_decimal:.2f} INR", cell_style),
                ],
                [
                    Paragraph("<b>Rate Source & Timestamp:</b>", cell_style),
                    Paragraph(f"{rate.source} &nbsp;|&nbsp; {rate.timestamp}", cell_style),
                ],
            ]
        else:
            inr_content = [
                [
                    Paragraph("<b>Approximate INR Equivalent:</b>", cell_style),
                    Paragraph("<font color='#b91c1c'><b>Unavailable</b></font>", cell_style),
                ],
                [
                    Paragraph("<b>Reason:</b>", cell_style),
                    Paragraph(
                        rate.error_reason if (rate and rate.error_reason)
                        else "Exchange-rate service unavailable at report generation.",
                        cell_style,
                    ),
                ],
            ]

        inr_table = Table(inr_content, colWidths=[180, 340])
        inr_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafaf9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d6d3d1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e7e5e4")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(inr_table)
        story.append(Spacer(1, 14))

        # --- Section 4: Payment Proof & Blockchain Settlement ---
        story.append(Paragraph("PAYMENT PROOF & BLOCKCHAIN SETTLEMENT", section_heading))

        proof_data = [
            [
                Paragraph("<b>Network:</b>", cell_style),
                Paragraph(f"Algorand ({quote.network})", cell_style),
            ],
            [
                Paragraph("<b>Settlement Asset:</b>", cell_style),
                Paragraph(f"{quote.asset} (Asset ID: {quote.asset_id})", cell_style),
            ],
            [
                Paragraph("<b>Amount Settled:</b>", cell_style),
                Paragraph(f"<b>{usdc_total_dec:.2f} USDC</b>", cell_style),
            ],
            [
                Paragraph("<b>Settlement Status:</b>", cell_style),
                Paragraph("<font color='#15803d'><b>SETTLED</b></font>", cell_style),
            ],
            [
                Paragraph("<b>Transaction ID / Hash:</b>", cell_style),
                Paragraph(f"<font name='Courier'>{quote.transaction_id or 'N/A'}</font>", cell_style),
            ],
            [
                Paragraph("<b>Explorer Verification:</b>", cell_style),
                Paragraph(f"<font color='#2563eb'><u>{explorer_link}</u></font>", cell_style),
            ],
            [
                Paragraph("<b>Settled At:</b>", cell_style),
                Paragraph(quote.settled_at or datetime.now(timezone.utc).isoformat(), cell_style),
            ],
        ]

        proof_table = Table(proof_data, colWidths=[160, 360])
        proof_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#86efac")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbf7d0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(proof_table)
        story.append(Spacer(1, 16))

        # --- Section 5: Mandatory Legal / Financial Disclaimer ---
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8))
        story.append(
            Paragraph(
                "<b>IMPORTANT:</b> The settled payment amount is the USDC amount above. "
                "The INR amount is an approximate informational conversion only and does NOT "
                "represent an on-chain settlement currency. CoinGecko exchange rates are captured "
                "at report generation time and do not alter the authoritative USDC settlement obligation.",
                disclaimer_style,
            )
        )

        doc.build(story)

        # 3. Calculate SHA-256 Checksum of the generated PDF
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        file_sha256 = hasher.hexdigest()

        return BomPaymentReportArtifact(
            artifact_id=artifact_id,
            quote_id=quote.quote_id,
            bom_id=quote.bom_id,
            project_id=quote.project_id,
            filename=filename,
            filepath=filepath,
            sha256=file_sha256,
            bom_total_usd=float(usd_total_dec),
            settled_amount_usdc=float(usdc_total_dec),
            approx_inr_total=float(approx_inr_dec) if approx_inr_dec else None,
            inr_available=inr_available,
            exchange_rate=float(rate.rate_decimal) if (inr_available and rate and rate.rate_decimal) else None,
            exchange_rate_source=rate.source if (inr_available and rate) else None,
            exchange_rate_timestamp=rate.timestamp if (inr_available and rate) else None,
            transaction_id=quote.transaction_id,
            explorer_url=explorer_link,
            network=quote.network,
        )
