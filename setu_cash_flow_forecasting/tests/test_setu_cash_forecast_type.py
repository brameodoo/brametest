# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestSetuCashForecastType(SuCashForecastTestCommon):
    """Test cases for setu.cash.forecast.type model"""

    def test_forecast_type_creation(self):
        """Test basic forecast type creation"""
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Test Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'calculation_pattern': 'average',
            'average_value_of_days': 30,
            'sequence': 1,
        })
        
        self.assertEqual(forecast_type.name, 'Test Forecast Type')
        self.assertEqual(forecast_type.type, 'income')
        self.assertEqual(forecast_type.company_id, self.company)
        self.assertTrue(forecast_type.auto_calculate)

    def test_forecast_type_creation_without_accounts_validation(self):
        """Test validation when creating forecast type without accounts"""
        with self.assertRaises(ValidationError):
            self.env['setu.cash.forecast.type'].create({
                'name': 'Invalid Forecast Type',
                'type': 'income',
                'cash_forecast_category_id': self.category_income.id,
                'company_id': self.company.id,
                'auto_calculate': True,
                'calculate_from': 'past_account_entries',
            })

    def test_forecast_type_creation_without_accounts_demo_context(self):
        """Test creation without accounts when demo_data context is set"""
        forecast_type = self.env['setu.cash.forecast.type'].with_context(demo_data=True).create({
            'name': 'Demo Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        self.assertEqual(forecast_type.name, 'Demo Forecast Type')

    def test_forecast_type_write_validation(self):
        """Test validation when writing forecast type without accounts"""
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Test Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        with self.assertRaises(ValidationError):
            forecast_type.write({'account_ids': [(5, 0, 0)]})

    def test_forecast_type_copy(self):
        """Test copying forecast type"""
        original = self.forecast_type_income
        copy = original.copy()
        
        self.assertNotEqual(original.id, copy.id)
        self.assertIn('(copy)', copy.name)
        self.assertEqual(copy.type, original.type)
        self.assertEqual(copy.company_id, original.company_id)

    def test_forecast_type_sequence_ordering(self):
        """Test that forecast types are ordered by sequence"""
        # Create forecast types with different sequences
        type1 = self.env['setu.cash.forecast.type'].create({
            'name': 'Type 1',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'sequence': 3,
        })
        
        type2 = self.env['setu.cash.forecast.type'].create({
            'name': 'Type 2',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'sequence': 1,
        })
        
        types = self.env['setu.cash.forecast.type'].search([
            ('company_id', '=', self.company.id)
        ])
        
        # Check that type2 (sequence=1) comes before type1 (sequence=3)
        type2_index = types.ids.index(type2.id)
        type1_index = types.ids.index(type1.id)
        self.assertLess(type2_index, type1_index)

    def test_forecast_type_unique_constraint(self):
        """Test unique constraint on name and company"""
        # Create first forecast type
        self.env['setu.cash.forecast.type'].create({
            'name': 'Unique Test Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Try to create duplicate - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['setu.cash.forecast.type'].create({
                'name': 'Unique Test Type',
                'type': 'income',
                'cash_forecast_category_id': self.category_income.id,
                'account_ids': [(6, 0, [self.account_income.id])],
                'company_id': self.company.id,
                'auto_calculate': True,
                'calculate_from': 'past_account_entries',
            })

    def test_forecast_type_opening_closing_unique_constraint(self):
        """Test unique constraint for opening and closing types"""
        # Create opening type
        self.env['setu.cash.forecast.type'].create({
            'name': 'Opening Type',
            'type': 'opening',
            'cash_forecast_category_id': self.category_opening.id,
            'account_ids': [(6, 0, [self.account_asset.id])],
            'company_id': self.company.id,
        })
        
        # Try to create another opening type - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['setu.cash.forecast.type'].create({
                'name': 'Another Opening Type',
                'type': 'opening',
                'cash_forecast_category_id': self.category_opening.id,
                'account_ids': [(6, 0, [self.account_asset.id])],
                'company_id': self.company.id,
            })

    def test_forecast_type_date_validation(self):
        """Test date validation for forecast start and end periods"""
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Date Test Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'forecast_start_period': self.period_mar.id,
            'forecast_end_period': self.period_jan.id,  # End before start
        })
        
        with self.assertRaises(ValidationError):
            forecast_type._validate_dates()

    def test_forecast_type_onchange_category(self):
        """Test onchange when cash forecast category changes"""
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Onchange Test Type',
            'type': 'expense',
            'cash_forecast_category_id': self.category_expense.id,
            'account_ids': [(6, 0, [self.account_expense.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Change category to income
        forecast_type.cash_forecast_category_id = self.category_income
        forecast_type._compute_group()
        
        self.assertEqual(forecast_type.type, 'income')

    def test_forecast_type_approve_forecast_type(self):
        """Test approve_forecast_type method"""
        # Test with opening type
        self.assertTrue(self.forecast_type_opening.approve_forecast_type(self.period_jan))
        
        # Test with closing type
        self.assertTrue(self.forecast_type_closing.approve_forecast_type(self.period_jan))
        
        # Test with pending calculation
        pending_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Pending Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'pending',
        })
        
        self.assertTrue(pending_type.approve_forecast_type(self.period_jan))

    def test_forecast_type_recurring_approval(self):
        """Test recurring forecast type approval"""
        recurring_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Recurring Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
            'is_recurring': True,
            'forecast_start_period': self.period_jan.id,
            'recurring_duration_interval': 1,
        })
        
        # Should approve for start period
        self.assertTrue(recurring_type.approve_forecast_type(self.period_jan))
        
        # Should approve for subsequent period
        self.assertTrue(recurring_type.approve_forecast_type(self.period_feb))

    def test_forecast_type_get_opening_balance(self):
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
            forecast_value=10000.0
        )
        
        opening_balance = self.forecast_type_opening._get_opening_balance(self.period_jan)
        self.assertEqual(opening_balance, 10000.0)

    def test_forecast_type_get_closing_forecast_value(self):
        """Test closing forecast value calculation"""
        # Create forecasts for the period
        opening_forecast = self.create_test_cash_forecast(
            self.forecast_type_opening, 
            self.period_jan, 
            forecast_value=10000.0
        )
        
        income_forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        expense_forecast = self.create_test_cash_forecast(
            self.forecast_type_expense, 
            self.period_jan, 
            forecast_value=2000.0
        )
        
        closing_value = self.forecast_type_closing._get_closing_forecast_value(self.period_jan)
        expected_value = 10000.0 + 5000.0 - 2000.0
        self.assertEqual(closing_value, expected_value)

    def test_forecast_type_get_net_forecast_value(self):
        """Test net forecast value calculation"""
        # Create income and expense forecasts
        income_forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        expense_forecast = self.create_test_cash_forecast(
            self.forecast_type_expense, 
            self.period_jan, 
            forecast_value=2000.0
        )
        
        # Create net forecast type
        net_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Net Forecast Type',
            'type': 'net_forecast',
            'company_id': self.company.id,
            'auto_calculate': True,
        })
        
        net_value = net_type._get_net_forecast_value(self.period_jan)
        expected_value = 5000.0 - 2000.0
        self.assertEqual(net_value, expected_value)

    def test_forecast_type_get_calculation_days(self):
        """Test calculation days method"""
        # Test average pattern
        start_date, end_date, days = self.forecast_type_income.get_calculation_days(self.period_jan)
        self.assertEqual(days, 30)  # average_value_of_days
        
        # Test seasonal pattern
        self.forecast_type_income.calculation_pattern = 'seasonal'
        start_date, end_date, days = self.forecast_type_income.get_calculation_days(self.period_jan)
        expected_days = (self.period_jan.end_date - self.period_jan.start_date).days + 1
        self.assertEqual(days, expected_days)

    def test_forecast_type_get_past_account_entries_forecast_value(self):
        """Test past account entries forecast value calculation"""
        # Create some move lines
        self.create_test_move_line(self.account_income, -1000.0, date(2024, 1, 15))
        self.create_test_move_line(self.account_income, -2000.0, date(2024, 1, 20))
        
        forecast_value = self.forecast_type_income._get_past_account_entries_forecast_value(self.period_jan)
        self.assertGreater(forecast_value, 0)

    def test_forecast_type_get_past_period_forecasting_entries_value(self):
        """Test past period forecasting entries value calculation"""
        # Create past period forecast
        past_period = self.env['cash.forecast.fiscal.period'].create({
            'name': 'December 2023',
            'fiscal_id': self.fiscal_year.id,
            'start_date': date(2023, 12, 1),
            'end_date': date(2023, 12, 31),
            'company_id': self.company.id,
        })
        
        past_forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            past_period, 
            forecast_value=3000.0
        )
        
        # Set calculation method
        self.forecast_type_income.calculate_from = 'past_period_forecasting_entries'
        self.forecast_type_income.number_of_period_months = 1
        
        forecast_value = self.forecast_type_income._get_past_period_forecasting_entries_value(self.period_jan)
        self.assertEqual(forecast_value, 3000.0)

    def test_forecast_type_get_dependant_forecast_value(self):
        """Test dependent forecast value calculation"""
        # Create dependent forecast type
        dependent_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Dependent Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Set dependency
        self.forecast_type_income.dep_forecast_ids = [(6, 0, [dependent_type.id])]
        
        # Create dependent forecast
        dependent_forecast = self.create_test_cash_forecast(
            dependent_type, 
            self.period_jan, 
            forecast_value=2000.0
        )
        
        # Set calculation method
        self.forecast_type_income.calculate_from = 'dependant'
        
        forecast_value = self.forecast_type_income._get_dependant_forecast_value(self.period_jan)
        self.assertEqual(forecast_value, 2000.0)

    def test_forecast_type_get_forecast_value_fixed(self):
        """Test forecast value calculation with fixed value"""
        self.forecast_type_income.auto_calculate = False
        self.forecast_type_income.fixed_value = 5000.0
        
        forecast_value = self.forecast_type_income._get_forecast_value(self.period_jan)
        self.assertEqual(forecast_value, 5000.0)

    def test_forecast_type_get_forecast_value_with_multiply(self):
        """Test forecast value calculation with multiply factor"""
        self.forecast_type_income.multiply_by = 1.5
        self.forecast_type_income.extra_gain_and_loss = 100.0
        
        # Create some move lines for calculation
        self.create_test_move_line(self.account_income, -1000.0, date(2024, 1, 15))
        
        forecast_value = self.forecast_type_income._get_forecast_value(self.period_jan)
        # Should be (1000 * 1.5) + 100 = 1600, rounded
        self.assertEqual(forecast_value, 1600)

    def test_forecast_type_kanban_dashboard_graph(self):
        """Test kanban dashboard graph generation"""
        # Create some forecasts
        self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_feb, 
            forecast_value=6000.0
        )
        
        graph_data = self.forecast_type_income.get_bar_graph_datas()
        self.assertIsInstance(graph_data, list)
        self.assertGreater(len(graph_data), 0)

    def test_forecast_type_open_action(self):
        """Test open action method"""
        action = self.forecast_type_income.open_action()
        
        self.assertEqual(action['res_model'], 'setu.cash.forecast.type')
        self.assertEqual(action['res_id'], self.forecast_type_income.id)
        self.assertEqual(action['view_mode'], 'form')

    def test_forecast_type_document_layout_save(self):
        """Test document layout save method"""
        result = self.forecast_type_income.document_layout_save()
        # This method calls onboarding step validation
        self.assertIsNotNone(result)

    def test_forecast_type_analytic_account_validation(self):
        """Test analytic account validation"""
        # Create analytic accounts with same plan
        plan = self.env.ref('analytic.analytic_plan_projects')
        analytic1 = self.env['account.analytic.account'].create({
            'name': 'Analytic 1',
            'plan_id': plan.id,
        })
        analytic2 = self.env['account.analytic.account'].create({
            'name': 'Analytic 2',
            'plan_id': plan.id,
        })
        
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Analytic Test Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        with self.assertRaises(ValidationError):
            forecast_type.analytic_account_ids = [(6, 0, [analytic1.id, analytic2.id])]
            forecast_type._onchange_analytic_account_ids()

    def test_forecast_type_company_isolation(self):
        """Test that forecast types are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create forecast type for other company
        other_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Other Company Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': other_company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Search for forecast types in original company
        company_types = self.env['setu.cash.forecast.type'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_type, company_types)
