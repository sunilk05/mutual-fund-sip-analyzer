import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import fsolve
import json

class MutualFundSIPAnalyzer:
    """
    Analyze SIP investments in mutual funds using historical NAV data from mfnav.in
    """
    
    BASE_URL = "https://mfnav.in/api"
    
    def __init__(self):
        self.fund_data = {}
        self.nav_history = {}
        
    def search_fund(self, fund_name):
        """Search for a mutual fund by name"""
        try:
            url = f"{self.BASE_URL}/funds/search"
            params = {"q": fund_name, "page_size": 10}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                return data['results']
            return None
        except Exception as e:
            print(f"Error searching fund '{fund_name}': {str(e)}")
            return None
    
    def get_nav_history(self, scheme_code, start_date, end_date):
        """Fetch NAV history for a specific scheme"""
        try:
            url = f"{self.BASE_URL}/nav/{scheme_code}"
            params = {
                "start": start_date,
                "end": end_date
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df['nav'] = df['nav'].astype(float)
                df = df.sort_values('date')
                return df
            return None
        except Exception as e:
            print(f"Error fetching NAV for scheme {scheme_code}: {str(e)}")
            return None
    
    def calculate_xirr(self, cash_flows_dict):
        """
        Calculate XIRR (Extended Internal Rate of Return)
        cash_flows_dict: dict with dates as keys and cash flow amounts as values
        Positive values = investments, Negative values = returns
        """
        try:
            # Convert to list of tuples (days_from_start, amount)
            dates = sorted(cash_flows_dict.keys())
            start_date = dates[0]
            
            cash_flows = []
            for date in dates:
                days = (date - start_date).days
                amount = cash_flows_dict[date]
                cash_flows.append((days, amount))
            
            # NPV function
            def npv(rate):
                result = 0
                for days, amount in cash_flows:
                    result += amount / ((1 + rate) ** (days / 365.0))
                return result
            
            # Find XIRR using Newton's method
            xirr = fsolve(npv, 0.1)[0]
            return xirr * 100  # Convert to percentage
        except Exception as e:
            print(f"Error calculating XIRR: {str(e)}")
            return None
    
    def calculate_sip_metrics(self, nav_df, start_date, end_date, monthly_investment=3000):
        """
        Calculate SIP metrics:
        - Total invested amount
        - Current value
        - Absolute gain/loss
        - Gain percentage
        - XIRR
        """
        
        if nav_df is None or len(nav_df) == 0:
            return None
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filter NAV data within date range
        nav_df = nav_df[(nav_df['date'] >= start_date) & (nav_df['date'] <= end_date)].copy()
        
        if len(nav_df) == 0:
            return None
        
        # Generate SIP dates (1st of each month)
        current_date = start_date
        sip_dates = []
        while current_date <= end_date:
            sip_dates.append(current_date)
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Calculate units purchased at each SIP date
        total_invested = 0
        units_held = 0
        sip_details = []
        cash_flows_dict = {}  # For XIRR calculation
        
        for sip_date in sip_dates:
            # Find NAV on or closest to SIP date
            available_navs = nav_df[nav_df['date'] <= sip_date]
            
            if len(available_navs) > 0:
                nav_on_date = available_navs.iloc[-1]['nav']
                date_used = available_navs.iloc[-1]['date']
                
                units_purchased = monthly_investment / nav_on_date
                units_held += units_purchased
                total_invested += monthly_investment
                
                sip_details.append({
                    'date': sip_date,
                    'nav': nav_on_date,
                    'investment': monthly_investment,
                    'units': units_purchased,
                    'cumulative_units': units_held
                })
                
                # Record cash flow for XIRR
                cash_flows_dict[date_used] = cash_flows_dict.get(date_used, 0) + monthly_investment
        
        # Current NAV (last available NAV)
        current_nav = nav_df.iloc[-1]['nav']
        current_date = nav_df.iloc[-1]['date']
        
        # Calculate current value
        current_value = units_held * current_nav
        
        # Calculate returns
        absolute_gain = current_value - total_invested
        gain_percentage = (absolute_gain / total_invested) * 100 if total_invested > 0 else 0
        
        # Add final valuation for XIRR
        cash_flows_dict[current_date] = cash_flows_dict.get(current_date, 0) - current_value
        
        # Calculate XIRR
        xirr = self.calculate_xirr(cash_flows_dict)
        
        return {
            'total_invested': total_invested,
            'current_value': current_value,
            'absolute_gain': absolute_gain,
            'gain_percentage': gain_percentage,
            'xirr': xirr,
            'units_held': units_held,
            'current_nav': current_nav,
            'current_date': current_date,
            'num_sips': len(sip_details),
            'sip_details': sip_details
        }
    
    def analyze_funds(self, funds_list, start_date='2024-09-01', end_date='2026-09-07', monthly_investment=3000):
        """
        Analyze multiple funds
        funds_list: List of fund names
        """
        results = {}
        
        for fund_name in funds_list:
            print(f"\nAnalyzing: {fund_name}")
            print("-" * 60)
            
            # Search for fund
            search_results = self.search_fund(fund_name)
            
            if not search_results:
                print(f"❌ Fund not found: {fund_name}")
                results[fund_name] = {'status': 'not_found'}
                continue
            
            # Use first result
            fund_info = search_results[0]
            scheme_code = fund_info['scheme_code']
            scheme_name = fund_info['scheme_name']
            fund_house = fund_info.get('fund_house', 'N/A')
            
            print(f"✓ Found: {scheme_name}")
            print(f"  Fund House: {fund_house}")
            print(f"  Scheme Code: {scheme_code}")
            
            # Fetch NAV history
            nav_df = self.get_nav_history(scheme_code, start_date, end_date)
            
            if nav_df is None or len(nav_df) == 0:
                print(f"⚠ No NAV data available")
                results[fund_name] = {'status': 'no_data'}
                continue
            
            print(f"✓ NAV data fetched: {len(nav_df)} records")
            
            # Calculate SIP metrics
            metrics = self.calculate_sip_metrics(nav_df, start_date, end_date, monthly_investment)
            
            if metrics:
                results[fund_name] = {
                    'status': 'success',
                    'scheme_code': scheme_code,
                    'scheme_name': scheme_name,
                    'fund_house': fund_house,
                    'metrics': metrics,
                    'nav_df': nav_df
                }
                
                # Print results
                print(f"\n📊 SIP Analysis Results:")
                print(f"  Period: {start_date} to {end_date}")
                print(f"  Monthly Investment: ₹{monthly_investment:,.0f}")
                print(f"  Total SIPs: {metrics['num_sips']}")
                print(f"  Total Invested: ₹{metrics['total_invested']:,.2f}")
                print(f"  Current Value: ₹{metrics['current_value']:,.2f}")
                print(f"  Absolute Gain/Loss: ₹{metrics['absolute_gain']:,.2f}")
                print(f"  Gain %: {metrics['gain_percentage']:.2f}%")
                print(f"  XIRR: {metrics['xirr']:.2f}%")
                print(f"  Units Held: {metrics['units_held']:,.2f}")
                print(f"  Current NAV: ₹{metrics['current_nav']:.2f}")
                
            else:
                results[fund_name] = {'status': 'calculation_error'}
        
        return results


def main():
    # Initialize analyzer
    analyzer = MutualFundSIPAnalyzer()
    
    # Fund list
    funds = [
        "Nippon India Value Fund - Direct Plan",
        "Nippon India Multi Cap Fund-Growth",
        "SBI GOLD FUND- DIRECT PLAN",
        "Kotak Global Emerging Market Overseas Equity Active FOF",
        "DSP Small Cap Fund - Direct Plan"
    ]
    
    # Analysis parameters
    start_date = '2024-09-01'
    end_date = '2026-09-07'
    monthly_investment = 3000
    
    print("=" * 60)
    print("MUTUAL FUND SIP ANALYSIS")
    print("=" * 60)
    print(f"Analysis Period: {start_date} to {end_date}")
    print(f"Monthly Investment: ₹{monthly_investment:,.0f}")
    print("=" * 60)
    
    # Analyze funds
    results = analyzer.analyze_funds(funds, start_date, end_date, monthly_investment)
    
    # Create summary report
    print("\n\n" + "=" * 60)
    print("SUMMARY REPORT")
    print("=" * 60 + "\n")
    
    summary_data = []
    for fund_name, result in results.items():
        if result['status'] == 'success':
            metrics = result['metrics']
            summary_data.append({
                'Fund Name': fund_name,
                'Total Invested (₹)': f"{metrics['total_invested']:,.2f}",
                'Current Value (₹)': f"{metrics['current_value']:,.2f}",
                'Gain/Loss (₹)': f"{metrics['absolute_gain']:,.2f}",
                'Return %': f"{metrics['gain_percentage']:.2f}%",
                'XIRR %': f"{metrics['xirr']:.2f}%",
                'Units Held': f"{metrics['units_held']:,.2f}"
            })
        else:
            summary_data.append({
                'Fund Name': fund_name,
                'Total Invested (₹)': 'N/A',
                'Current Value (₹)': 'N/A',
                'Gain/Loss (₹)': 'N/A',
                'Return %': 'N/A',
                'XIRR %': 'N/A',
                'Units Held': 'N/A'
            })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    # Save results to CSV
    summary_df.to_csv('sip_analysis_summary.csv', index=False)
    print(f"\n✓ Summary saved to: sip_analysis_summary.csv")
    
    # Save detailed results to JSON
    detailed_results = {}
    for fund_name, result in results.items():
        if result['status'] == 'success':
            metrics = result['metrics']
            detailed_results[fund_name] = {
                'scheme_code': result['scheme_code'],
                'scheme_name': result['scheme_name'],
                'fund_house': result['fund_house'],
                'total_invested': metrics['total_invested'],
                'current_value': metrics['current_value'],
                'absolute_gain': metrics['absolute_gain'],
                'gain_percentage': metrics['gain_percentage'],
                'xirr': metrics['xirr'],
                'units_held': metrics['units_held'],
                'current_nav': metrics['current_nav'],
                'num_sips': metrics['num_sips']
            }
    
    with open('sip_analysis_detailed.json', 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print(f"✓ Detailed results saved to: sip_analysis_detailed.json")


if __name__ == "__main__":
    main()