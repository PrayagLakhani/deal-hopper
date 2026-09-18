# Deal Hopper — Styling & Polish Checklist (Stage 9 finale)

## 1. Apply the theme (report-level, do this first)

View tab -> Themes -> Browse for themes -> `deal_hopper_theme.json`

## 2. Set default display formats on measures (Model view, once each)

| Measure(s) | Format |
|---|---|
| All ₹ measures (GMV, Discount, Contribution, Commission, Delivery Cost, etc.) | Currency, `₹#,##0` |
| All % measures (Contribution Margin %, Cancellation Rate %, Refund Rate %, Promo Usage Rate) | Custom `0.00"%"` (these already multiply by 100 in the DAX, so true Percentage format would double it) |
| Distance / delay measures | Decimal, 1-2 places |
| `margin_drain_score` column | Decimal, 1 place |

## 3. Page 1 (Executive Overview)

- Bar chart (not donut) for order status breakdown, with data labels on
- Conditional formatting on Cancellation Rate % / Refund Rate % cards
  (green/yellow/red thresholds)
- Split the combined GMV+Contribution trend chart into two separate charts
  (GMV area chart + Contribution Margin % line chart with a constant
  reference line at 14.70%) — a shared axis hid the margin story
- Reorder KPI cards into a volume row and a profitability row, not mixed

## 4. Page 2 (Promotion Intelligence)

- 3-color background scale on the `margin_drain_score` column in the
  scorecard table: green (0) -> yellow (50) -> red (100)
- Data labels on the Worst 10 / Best 10 bar charts
- Chart titles that state the finding, not just the field names

## 5. Consistent header banner across all 6 pages

Insert a rectangle + text box header on one page, copy-paste it onto every
other page (Power BI preserves exact position on paste), editing only the
page-name portion of the text each time.

## 6. Multi-select formatting for consistent KPI cards

Ctrl+click multiple Card visuals on a page to format them all at once
(background, border, font, accent color).

## 7. Alignment and final tidy-up

Select all visuals (Ctrl+A) -> right-click -> Align -> distribute evenly.
Rename default chart titles to be descriptive, not "Sum of X by Y".
Turn off unnecessary gridlines.

## 8. Optional: top navigation buttons

Insert -> Buttons -> Blank, one per page, Action -> Page navigation, laid
out along the header banner for a more polished/product-like feel.
