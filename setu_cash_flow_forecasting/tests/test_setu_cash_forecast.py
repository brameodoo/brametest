# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestSetuCashForecast(SuCashForecastTestCommon):
    """Test cases for setu.cash.forecast model"""

    def test_cash_forecast_creation(self):
        """Test basic cash forecast creation"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        self.assertEqual(forecast.name, 'Test Test Income Forecast')
        self.assertEqual(forecast.forecast_type, 'income')
        self.assertEqual(forecast.forecast_value, 5000.0)
        self.assertEqual(forecast.company_id, self.company)

    def test_difference_computation(self):
        """Test difference value computation"""
        # Create forecast with real value
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0, 
            real_value=6000.0
        )
        
        # Set period to past date to trigger computation
        self.period_jan.start_date = date.today() - timedelta(days=10)
        self.period_jan.end_date = date.today() - timedelta(days=1)
        
        forecast._compute_difference()
        
        self.assertEqual(forecast.difference_value, 1000.0)  # 6000 - 5000
        self.assertEqual(forecast.forecast_property, 'under')  # Income under forecast

    def test_difference_computation_expense(self):
        """Test difference computation for expense forecast"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_expense, 
            self.period_jan, 
            forecast_value=3000.0, 
            real_value=2500.0
        )
        
        # Set period to past date
        self.period_jan.start_date = date.today() - timedelta(days=10)
        self.period_jan.end_date = date.today() - timedelta(days=1)
        
        forecast._compute_difference()
        
        self.assertEqual(forecast.difference_value, -500.0)  # 2500 - 3000
        self.assertEqual(forecast.forecast_property, 'under')  # Expense under forecast

    def test_difference_computation_over_forecast(self):
        """Test over forecast scenario"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0, 
            real_value=4000.0
        )
        
        # Set period to past date
        self.period_jan.start_date = date.today() - timedelta(days=10)
        self.period_jan.end_date = date.today() - timedelta(days=1)
        
        forecast._compute_difference()
        
        self.assertEqual(forecast.difference_value, -1000.0)  # 4000 - 5000
        self.assertEqual(forecast.forecast_property, 'over')  # Income over forecast

    def test_difference_computation_future_period(self):
        """Test that difference is not computed for future periods"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_feb,  # Future period
            forecast_value=5000.0, 
            real_value=6000.0
        )
        
        forecast._compute_difference()
        
        self.assertEqual(forecast.difference_value, 0)
        self.assertEqual(forecast.forecast_property, '')

    def test_unique_constraint(self):
        """Test unique constraint on account_ids, forecast_period_id, forecast_type_id"""
        # Create first forecast
        forecast1 = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        
        # Try to create duplicate forecast - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['setu.cash.forecast'].create({
                'name': 'Duplicate Forecast',
                'forecast_type': 'income',
                'forecast_type_id': self.forecast_type_income.id,
                'forecast_period_id': self.period_jan.id,
                'account_ids': [(6, 0, self.forecast_type_income.account_ids.ids)],
                'company_id': self.company.id,
            })

    def test_get_opening_balance(self):
        """Test opening balance calculation"""
        # Create previous period closing forecast
        prev_period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'December 2023',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2023, 12, 1),
            'end_date': date(2023, 12, 31),
            'company_id': self.company.id,
        })
        
        closing_forecast = self.create_test_cash_forecast(
            self.forecast_type_closing, 
            prev_period, 
            forecast_value=10000.0,
            real_value=10000.0
        )
        
        # Test opening balance retrieval
        opening_balance = self.env['setu.cash.forecast']._get_opening_balance(
            self.forecast_type_opening, 
            self.period_jan
        )
        
        self.assertEqual(opening_balance, 10000.0)

    def test_get_forecast_type_real_value_opening(self):
        """Test real value calculation for opening forecast type"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_opening, 
            self.period_jan
        )
        
        # Create some account move lines
        self.create_test_move_line(self.account_asset, 5000.0, date(2024, 1, 15))
        
        real_value = forecast.get_forecast_type_real_value()
        self.assertGreaterEqual(real_value, 0)

    def test_get_forecast_type_real_value_income(self):
        """Test real value calculation for income forecast type"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        
        # Create income move line
        self.create_test_move_line(self.account_income, -3000.0, date(2024, 1, 15))
        
        real_value = forecast.get_forecast_type_real_value()
        self.assertGreaterEqual(real_value, 0)

    def test_get_forecast_type_real_value_expense(self):
        """Test real value calculation for expense forecast type"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_expense, 
            self.period_jan
        )
        
        # Create expense move line
        self.create_test_move_line(self.account_expense, 2000.0, date(2024, 1, 15))
        
        real_value = forecast.get_forecast_type_real_value()
        self.assertGreaterEqual(real_value, 0)

    def test_get_forecast_type_real_value_closing(self):
        """Test real value calculation for closing forecast type"""
        # Create opening, income, and expense forecasts for the period
        opening_forecast = self.create_test_cash_forecast(
            self.forecast_type_opening, 
            self.period_jan, 
            forecast_value=10000.0,
            real_value=10000.0
        )
        
        income_forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0,
            real_value=5000.0
        )
        
        expense_forecast = self.create_test_cash_forecast(
            self.forecast_type_expense, 
            self.period_jan, 
            forecast_value=2000.0,
            real_value=2000.0
        )
        
        closing_forecast = self.create_test_cash_forecast(
            self.forecast_type_closing, 
            self.period_jan
        )
        
        real_value = closing_forecast.get_forecast_type_real_value()
        expected_value = 10000.0 + 5000.0 - 2000.0  # opening + income - expense
        self.assertEqual(real_value, expected_value)

    def test_get_real_values_method(self):
        """Test the get_real_values method"""
        # Create forecast without real value
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0,
            real_value=0.0
        )
        
        # Set period to past
        self.period_jan.start_date = date.today() - timedelta(days=10)
        self.period_jan.end_date = date.today() - timedelta(days=1)
        
        # Create some move lines
        self.create_test_move_line(self.account_income, -3000.0, date(2024, 1, 15))
        
        # Call get_real_values
        result = self.env['setu.cash.forecast'].get_real_values(self.period_jan.id)
        
        self.assertTrue(result)
        # Refresh the forecast record
        forecast.refresh()
        self.assertGreater(forecast.real_value, 0)

    def test_forecast_with_analytic_accounts(self):
        """Test forecast with analytic accounts"""
        # Create analytic account
        analytic_account = self.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
            'plan_id': self.env.ref('analytic.analytic_plan_projects').id,
        })
        
        # Update forecast type with analytic accounts
        self.forecast_type_income.analytic_account_ids = [(6, 0, [analytic_account.id])]
        
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        
        self.assertIn(analytic_account, forecast.analytic_account_ids)

    def test_forecast_with_dependent_forecasts(self):
        """Test forecast with dependent forecast types"""
        # Create dependent forecast type
        dependent_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Dependent Forecast',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'sequence': 4,
        })
        
        # Set dependency
        self.forecast_type_income.dep_forecast_ids = [(6, 0, [dependent_type.id])]
        
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        
        self.assertIn(dependent_type, forecast.dep_forecast_ids)

    def test_forecast_auto_calculate_flag(self):
        """Test auto calculate flag functionality"""
        # Test with auto_calculate = True
        forecast_auto = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        self.assertTrue(forecast_auto.auto_calculate)
        
        # Test with auto_calculate = False
        self.forecast_type_income.auto_calculate = False
        self.forecast_type_income.fixed_value = 1000.0
        
        forecast_manual = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_feb
        )
        self.assertFalse(forecast_manual.auto_calculate)

    def test_forecast_date_field(self):
        """Test forecast date field"""
        test_date = date(2024, 1, 15)
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        forecast.forecast_date = test_date
        
        self.assertEqual(forecast.forecast_date, test_date)

    def test_forecast_cash_forecast_category(self):
        """Test cash forecast category relationship"""
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan
        )
        
        self.assertEqual(forecast.cash_forecast_category_id, self.category_income)

    def test_forecast_company_isolation(self):
        """Test that forecasts are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create forecast for other company
        other_forecast = self.env['setu.cash.forecast'].create({
            'name': 'Other Company Forecast',
            'forecast_type': 'income',
            'forecast_type_id': self.forecast_type_income.id,
            'forecast_period_id': self.period_jan.id,
            'account_ids': [(6, 0, self.forecast_type_income.account_ids.ids)],
            'company_id': other_company.id,
            'forecast_value': 1000.0,
        })
        
        # Search for forecasts in original company
        company_forecasts = self.env['setu.cash.forecast'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_forecast, company_forecasts)
