# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestCashForecastFiscalPeriod(SuCashForecastTestCommon):
    """Test cases for cash.forecast.fiscal.period model"""

    def test_fiscal_period_creation(self):
        """Test basic fiscal period creation"""
        period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Test Period',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        self.assertEqual(period.name, 'Test Period')
        self.assertEqual(period.fiscal_id, self.fiscal_year)
        self.assertEqual(period.start_date, date(2024, 4, 1))
        self.assertEqual(period.end_date, date(2024, 4, 30))
        self.assertEqual(period.company_id, self.company)

    def test_fiscal_period_display_name(self):
        """Test fiscal period display name"""
        period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'April 2024',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        display_name = period.display_name
        self.assertIn('April 2024', display_name)
        self.assertIn('2024-04-01', display_name)
        self.assertIn('2024-04-30', display_name)

    def test_fiscal_period_date_validation(self):
        """Test date validation for fiscal period"""
        with self.assertRaises(ValidationError):
            self.env['cash.forecast.fiscal.period'].create({
                'name': 'Invalid Period',
                'fiscal_id': self.fiscal_year.id,
                'start_date': date(2024, 4, 30),  # Start after end
                'end_date': date(2024, 4, 1),
                'company_id': self.company.id,
            })

    def test_fiscal_period_fiscal_year_validation(self):
        """Test fiscal year validation for fiscal period"""
        with self.assertRaises(ValidationError):
            self.env['cash.forecast.fiscal.period'].create({
                'name': 'Invalid Period',
                'fiscal_id': self.fiscal_year.id,
                'start_date': date(2023, 12, 1),  # Before fiscal year
                'end_date': date(2023, 12, 31),
                'company_id': self.company.id,
            })

    def test_fiscal_period_company_isolation(self):
        """Test that fiscal periods are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create fiscal year for other company
        other_fiscal_year = self.env['cash.forecast.fiscal.year'].create({
            'name': 'Other Fiscal Year',
            'company_id': other_company.id,
            'date_from': date(2024, 1, 1),
            'date_to': date(2024, 12, 31),
            'period_interval': 'months',
        })
        
        # Create period for other company
        other_period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Other Period',
            'fiscal_id': other_fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': other_company.id,
        })
        
        # Search for periods in original company
        company_periods = self.env['cash.forecast.fiscal.period'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_period, company_periods)

    def test_fiscal_period_overlap_validation(self):
        """Test overlap validation between fiscal periods"""
        # Create first period
        self.env['cash.forecast.fiscal.period'].create({
            'name': 'Period 1',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        # Try to create overlapping period - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['cash.forecast.fiscal.period'].create({
                'name': 'Overlapping Period',
                'fiscal_id': self.fiscal_year.id,
                'start_date': date(2024, 4, 15),  # Overlaps with existing period
                'end_date': date(2024, 5, 15),
                'company_id': self.company.id,
            })

    def test_fiscal_period_sequence_ordering(self):
        """Test that fiscal periods are ordered by start date"""
        # Create periods in different order
        period3 = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Period 3',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 6, 1),
            'end_date': date(2024, 6, 30),
            'company_id': self.company.id,
        })
        
        period1 = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Period 1',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        period2 = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Period 2',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 5, 1),
            'end_date': date(2024, 5, 31),
            'company_id': self.company.id,
        })
        
        periods = self.env['cash.forecast.fiscal.period'].search([
            ('fiscal_id', '=', self.fiscal_year.id)
        ])
        
        # Check ordering
        period1_index = periods.ids.index(period1.id)
        period2_index = periods.ids.index(period2.id)
        period3_index = periods.ids.index(period3.id)
        
        self.assertLess(period1_index, period2_index)
        self.assertLess(period2_index, period3_index)

    def test_fiscal_period_duration_calculation(self):
        """Test fiscal period duration calculation"""
        period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Test Duration Period',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        duration = (period.end_date - period.start_date).days + 1
        self.assertEqual(duration, 30)

    def test_fiscal_period_current_period_detection(self):
        """Test current period detection"""
        # Create current period
        current_period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Current Period',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date.today() - timedelta(days=5),
            'end_date': date.today() + timedelta(days=5),
            'company_id': self.company.id,
        })
        
        # Search for current period
        found_period = self.env['cash.forecast.fiscal.period'].search([
            ('start_date', '<=', date.today()),
            ('end_date', '>=', date.today()),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(current_period, found_period)

    def test_fiscal_period_past_period_detection(self):
        """Test past period detection"""
        # Create past period
        past_period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Past Period',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date.today() - timedelta(days=20),
            'end_date': date.today() - timedelta(days=10),
            'company_id': self.company.id,
        })
        
        # Search for past periods
        past_periods = self.env['cash.forecast.fiscal.period'].search([
            ('end_date', '<', date.today()),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(past_period, past_periods)

    def test_fiscal_period_future_period_detection(self):
        """Test future period detection"""
        # Create future period
        future_period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Future Period',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date.today() + timedelta(days=10),
            'end_date': date.today() + timedelta(days=20),
            'company_id': self.company.id,
        })
        
        # Search for future periods
        future_periods = self.env['cash.forecast.fiscal.period'].search([
            ('start_date', '>', date.today()),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(future_period, future_periods)

    def test_fiscal_period_with_cash_forecasts(self):
        """Test fiscal period with associated cash forecasts"""
        # Create cash forecast for the period
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        # Check that forecast is associated with the period
        self.assertEqual(forecast.forecast_period_id, self.period_jan)
        
        # Search forecasts by period
        period_forecasts = self.env['setu.cash.forecast'].search([
            ('forecast_period_id', '=', self.period_jan.id)
        ])
        
        self.assertIn(forecast, period_forecasts)

    def test_fiscal_period_copy(self):
        """Test copying fiscal period"""
        original = self.period_jan
        copy = original.copy()
        
        self.assertNotEqual(original.id, copy.id)
        self.assertEqual(copy.name, original.name)
        self.assertEqual(copy.fiscal_id, original.fiscal_id)
        self.assertEqual(copy.start_date, original.start_date)
        self.assertEqual(copy.end_date, original.end_date)
        self.assertEqual(copy.company_id, original.company_id)

    def test_fiscal_period_name_generation(self):
        """Test fiscal period name generation"""
        period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Generated Name',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        # Test that name is properly set
        self.assertEqual(period.name, 'Generated Name')
        
        # Test display name includes the name
        self.assertIn('Generated Name', period.display_name)

    def test_fiscal_period_fiscal_year_relationship(self):
        """Test fiscal period and fiscal year relationship"""
        period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Test Relationship',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        # Test relationship
        self.assertEqual(period.fiscal_id, self.fiscal_year)
        self.assertIn(period, self.fiscal_year.fiscal_period_ids)

    def test_fiscal_period_period_interval_inheritance(self):
        """Test that period interval is inherited from fiscal year"""
        period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'Test Interval',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2024, 4, 1),
            'end_date': date(2024, 4, 30),
            'company_id': self.company.id,
        })
        
        # Period should inherit interval from fiscal year
        self.assertEqual(period.period_interval, self.fiscal_year.period_interval)
