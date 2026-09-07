# Mutual Fund SIP Analyzer

Calculate SIP returns, XIRR, and corpus for Indian mutual funds using historical NAV data from mfnav.in API.

## Features

- ✅ Fetch historical NAV data from mfnav.in API (free, no authentication required)
- ✅ Calculate SIP returns for any investment period
- ✅ Compute XIRR (Extended Internal Rate of Return)
- ✅ Generate detailed reports with corpus calculations
- ✅ Support for multiple mutual funds

## Installation

```bash
# Clone the repository
git clone https://github.com/sunilk05/mutual-fund-sip-analyzer.git
cd mutual-fund-sip-analyzer

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
python mutual_fund_analyzer.py
```

This will analyze the following funds with a ₹3,000 monthly SIP from Sep 1, 2024 to Sep 7, 2026:

1. Nippon India Value Fund - Direct Plan
2. Nippon India Multi Cap Fund-Growth
3. SBI GOLD FUND- DIRECT PLAN
4. Kotak Global Emerging Market Overseas Equity Active FOF
5. DSP Small Cap Fund - Direct Plan

### Sample Output

```
==============================================================
MUTUAL FUND SIP ANALYSIS
==============================================================
Analysis Period: 2024-09-01 to 2026-09-07
Monthly Investment: ₹3,000
==============================================================

Analyzing: Nippon India Value Fund - Direct Plan
------------------------------------------------------------
✓ Found: Nippon India Value Fund - Direct Plan - Growth
  Fund House: Nippon India Mutual Fund
  Scheme Code: 108755
✓ NAV data fetched: 485 records

📊 SIP Analysis Results:
  Period: 2024-09-01 to 2026-09-07
  Monthly Investment: ₹3,000
  Total SIPs: 25
  Total Invested: ₹75,000.00
  Current Value: ₹92,345.67
  Absolute Gain/Loss: ₹17,345.67
  Gain %: 23.13%
  XIRR: 18.45%
  Units Held: 1,234.56
  Current NAV: ₹74.85
```

## Output Files

The analyzer generates two output files:

1. **sip_analysis_summary.csv** - Summary table with all funds
2. **sip_analysis_detailed.json** - Detailed results including SIP history

## Metrics Explained

### Total Invested
Sum of all monthly SIP investments over the period.

**Formula:** Monthly Investment × Number of SIPs

### Current Value
Current corpus = Units Held × Current NAV

### Gain/Loss
Absolute gain/loss in rupees.

**Formula:** Current Value - Total Invested

### Return %
Percentage return on total invested amount.

**Formula:** (Gain/Loss ÷ Total Invested) × 100

### XIRR
Extended Internal Rate of Return - the annualized return accounting for the timing and amount of each cash flow.

**Formula:** Solved using Newton's method
- NPV equation: Σ(Cash Flow / (1 + XIRR)^(Days/365)) = 0

### Units Held
Total units accumulated through all SIPs.

### Current NAV
Latest Net Asset Value of the fund.

## API Reference

Uses [mfnav.in API](https://mfnav.in/api-docs) - Free mutual fund NAV data.

### Endpoints Used

- `GET /api/funds/search?q=<fund_name>` - Search for funds
- `GET /api/nav/<scheme_code>?start=<date>&end=<date>` - Get NAV history

## Customization

Edit `mutual_fund_analyzer.py` to customize:

```python
# Change these values
start_date = '2024-09-01'
end_date = '2026-09-07'
monthly_investment = 3000

funds = [
    "Your Fund 1",
    "Your Fund 2",
    # Add more funds
]
```

## Requirements

- Python 3.8+
- Internet connection (to fetch NAV data)
- Dependencies: pandas, numpy, scipy, requests

## Limitations

- Historical NAV data availability depends on mfnav.in database (back to Jan 2006)
- API rate limit: 120 requests/minute for anonymous users
- SIP dates are set to 1st of each month (can be customized)

## Troubleshooting

### Fund Not Found
- Verify the exact fund name from mfnav.in
- Try searching with partial fund name
- Check spelling and plan type (Direct/Regular, Growth/Dividend)

### No NAV Data
- Fund may not have data for the specified period
- Try with a different date range
- Check if the fund was active during that period

### XIRR Calculation Issues
- Ensure at least 2 different cash flow dates
- Check for valid date range

## References

- [mfnav.in API Documentation](https://mfnav.in/api-docs)
- [XIRR Calculation Method](https://en.wikipedia.org/wiki/Internal_rate_of_return)
- [Mutual Fund NAV](https://www.moneycontrol.com/mutual-funds/nav/)

## License

MIT License

## Author

Created for analyzing Indian mutual fund SIP returns.

## Support

For issues or questions, please refer to the [mfnav.in documentation](https://mfnav.in/api-docs).