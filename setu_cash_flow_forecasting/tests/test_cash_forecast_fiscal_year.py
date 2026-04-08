# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestCashForecastFiscalYear(SuCashForecastTestCommon):
    """Test cases for cash.forecast.fiscal.year model"""

    def test_fiscal_year_creation(self):
        """Test basic fiscal year creation"""
        fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Test Fiscal Year 2025',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        self.assertEqual(fiscal_year.name, 'Test Fiscal Year 2025')
        self.assertEqual(fiscal_year.company_id, self.company)
        self.assertEqual(fiscal_year.date_from, date(2025, 1, 1))
        self.assertEqual(fiscal_year.date_to, date(2025, 12, 31))
        self.assertEqual(fiscal_year.period_interval, 'months')

    def test_fiscal_year_date_validation(self):
        """Test date validation for fiscal year"""
        with self.assertRaises(ValidationError):
            self.env['cash.forecast.fiscal.year'].create({
                'name': 'Invalid Fiscal Year',
                'company_id': self.company.id,
                'date_from': date(2025, 12, 31),  # Start after end
                'date_to': date(2025, 1, 1),
                'period_interval': 'months',
            })

    def test_fiscal_year_period_interval_validation(self):
        """Test period interval validation"""
        valid_intervals = ['days', 'weeks', 'months']
        
        for interval in valid_intervals:
            fiscal_year = self.env['cash.forecast.fiscal.year'].create({
                'name': f'Test {interval} Fiscal Year',
                'company_id': self.company.id,
                'date_from': date(2025, 1, 1),
                'date_to': date(2025, 12, 31),
                'period_interval': interval,
            })
            self.assertEqual(fiscal_year.period_interval, interval)

    def test_fiscal_year_company_isolation(self):
        """Test that fiscal years are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create fiscal year for other company
        other_fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Other Fiscal Year',
            'company_id': other_company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        # Search for fiscal years in original company
        company_fiscal_years = self.env['cash.forecast.fiscal.year'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_fiscal_year, company_fiscal_years)

    def test_fiscal_year_overlap_validation(self):
        """Test overlap validation between fiscal years"""
        # Create first fiscal year
        self.env['cash.forecast.fiscal.year'].create({
            'name': 'Fiscal Year 1',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        # Try to create overlapping fiscal year - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['cash.forecast.fiscal.year'].create({
                'name': 'Overlapping Fiscal Year',
                'company_id': self.company.id,
                'date_from': date(2025, 6, 1),  # Overlaps with existing fiscal year
                'date_to': date(2026, 5, 31),
                'period_interval': 'months',
            })

    def test_fiscal_year_fiscal_periods_relationship(self):
        """Test fiscal year and fiscal periods relationship"""
        # Create fiscal periods
        period1 = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Period 1',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 1, 31),
            'company_id': self.company.id,
        })
        
        period2 = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Period 2',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 2, 1),
            'end_date': date(2024, 2, 29),
            'company_id': self.company.id,
        })
        
        # Test relationship
        self.assertIn(period1, self.fiscal_year.fiscal_period_ids)
        self.assertIn(period2, self.fiscal_year.fiscal_period_ids)
        self.assertEqual(len(self.fiscal_year.fiscal_period_ids), 5)  # 3 from setUp + 2 new

    def test_fiscal_year_duration_calculation(self):
        """Test fiscal year duration calculation"""
        fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Test Duration Fiscal Year',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        duration = (fiscal_year.date_to - fiscal_year.date_from).days + 1
        self.assertEqual(duration, 365)  # 2025 is not a leap year

    def test_fiscal_year_current_fiscal_year_detection(self):
        """Test current fiscal year detection"""
        # Create current fiscal year
        current_fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Current Fiscal Year',
            'company_id': self.company.id,
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today() + timedelta(days=30),
            'period_interval': 'months',
        })
        
        # Search for current fiscal year
        found_fiscal_year = self.env['cash.forecast.fiscal.year'].search([
            ('date_from', '<=', date.today()),
            ('date_to', '>=', date.today()),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(current_fiscal_year, found_fiscal_year)

    def test_fiscal_year_past_fiscal_year_detection(self):
        """Test past fiscal year detection"""
        # Create past fiscal year
        past_fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Past Fiscal Year',
            'company_id': self.company.id,
            'date_from': date.today() - timedelta(days=400),
            'date_to': date.today() - timedelta(days=40),
            'period_interval': 'months',
        })
        
        # Search for past fiscal years
        past_fiscal_years = self.env['cash.forecast.fiscal.year'].search([
            ('date_to', '<', date.today()),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(past_fiscal_year, past_fiscal_years)

    def test_fiscal_year_future_fiscal_year_detection(self):
        """Test future fiscal year detection"""
        # Create future fiscal year
        future_fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Future Fiscal Year',
            'company_id': self.company.id,
            'date_from': date.today() + timedelta(days=40),
            'date_to': date.today() + timedelta(days=400),
            'period_interval': 'months',
        })
        
        # Search for future fiscal years
        future_fiscal_years = self.env['cash.forecast.fiscal.year'].search([
            ('date_from', '>', date.today()),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(future_fiscal_year, future_fiscal_years)

    def test_fiscal_year_copy(self):
        """Test copying fiscal year"""
        original = self.fiscal_year
        copy = original.copy()
        
        self.assertNotEqual(original.id, copy.id)
        self.assertEqual(copy.name, original.name)
        self.assertEqual(copy.company_id, original.company_id)
        self.assertEqual(copy.date_from, original.date_from)
        self.assertEqual(copy.date_to, original.date_to)
        self.assertEqual(copy.period_interval, original.period_interval)

    def test_fiscal_year_name_generation(self):
        """Test fiscal year name generation"""
        fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Generated Name',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        # Test that name is properly set
        self.assertEqual(fiscal_year.name, 'Generated Name')

    def test_fiscal_year_with_cash_forecasts(self):
        """Test fiscal year with associated cash forecasts"""
        # Create cash forecast for a period in the fiscal year
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        # Check that forecast is associated with the fiscal year through period
        self.assertEqual(forecast.forecast_period_id.fiscal_id, self.fiscal_year)
        
        # Search forecasts by fiscal year
        fiscal_year_forecasts = self.env['setu.cash.forecast'].search([
            ('forecast_period_id.fiscal_id', '=', self.fiscal_year.id)
        ])
        
        self.assertIn(forecast, fiscal_year_forecasts)

    def test_fiscal_year_period_interval_days(self):
        """Test fiscal year with days period interval"""
        fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Days Fiscal Year',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 1, 31),
            'period_interval': 'days',
        })
        
        self.assertEqual(fiscal_year.period_interval, 'days')

    def test_fiscal_year_period_interval_weeks(self):
        """Test fiscal year with weeks period interval"""
        fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Weeks Fiscal Year',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 1, 31),
            'period_interval': 'weeks',
        })
        
        self.assertEqual(fiscal_year.period_interval, 'weeks')

    def test_fiscal_year_period_interval_months(self):
        """Test fiscal year with months period interval"""
        fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Months Fiscal Year',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        self.assertEqual(fiscal_year.period_interval, 'months')

    def test_fiscal_year_leap_year_handling(self):
        """Test fiscal year with leap year"""
        leap_fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Leap Year Fiscal Year',
            'company_id': self.company.id,
            'date_from': date(2024, 1, 1),  # 2024 is a leap year
            'date_to': date(2024, 12, 31),
            'period_interval': 'months',
        })
        
        duration = (leap_fiscal_year.date_to - leap_fiscal_year.date_from).days + 1
        self.assertEqual(duration, 366)  # 2024 is a leap year

    def test_fiscal_year_unique_constraint(self):
        """Test unique constraint on fiscal year"""
        # Create first fiscal year
        self.env['cash.forecast.fiscal.year'].create({
            'name': 'Unique Fiscal Year',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        # Try to create overlapping fiscal year - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['cash.forecast.fiscal.year'].create({
                'name': 'Overlapping Fiscal Year',
                'company_id': self.company.id,
                'date_from': date(2025, 6, 1),
                'date_to': date(2026, 5, 31),
                'period_interval': 'months',
            })

    def test_fiscal_year_sequence_ordering(self):
        """Test that fiscal years are ordered by date_from"""
        # Create fiscal years in different order
        fiscal_year3 = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Fiscal Year 3',
            'company_id': self.company.id,
            'date_from': date(2027, 1, 1),
            'date_to': date(2027, 12, 31),
            'period_interval': 'months',
        })
        
        fiscal_year1 = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Fiscal Year 1',
            'company_id': self.company.id,
            'date_from': date(2025, 1, 1),
            'date_to': date(2025, 12, 31),
            'period_interval': 'months',
        })
        
        fiscal_year2 = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Fiscal Year 2',
            'company_id': self.company.id,
            'date_from': date(2026, 1, 1),
            'date_to': date(2026, 12, 31),
            'period_interval': 'months',
        })
        
        fiscal_years = self.env['cash.forecast.fiscal.year'].search([
            ('company_id', '=', self.company.id)
        ])
        
        # Check ordering
        fiscal_year1_index = fiscal_years.ids.index(fiscal_year1.id)
        fiscal_year2_index = fiscal_years.ids.index(fiscal_year2.id)
        fiscal_year3_index = fiscal_years.ids.index(fiscal_year3.id)
        
        self.assertLess(fiscal_year1_index, fiscal_year2_index)
        self.assertLess(fiscal_year2_index, fiscal_year3_index)
