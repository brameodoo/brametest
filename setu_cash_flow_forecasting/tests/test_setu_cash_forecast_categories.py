# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from odoo.exceptions import ValidationError
from datetime import date
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestSetuCashForecastCategories(SuCashForecastTestCommon):
    """Test cases for setu.cash.forecast.categories model"""

    def test_cash_forecast_category_creation(self):
        """Test basic cash forecast category creation"""
        category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Test Category',
            'type': 'income',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.type, 'income')
        self.assertEqual(category.company_id, self.company)
        self.assertFalse(category.is_group_for_opening)

    def test_cash_forecast_category_creation_with_opening_flag(self):
        """Test cash forecast category creation with opening flag"""
        category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Opening Category',
            'type': 'opening',
            'company_id': self.company.id,
            'is_group_for_opening': True,
        })
        
        self.assertEqual(category.name, 'Opening Category')
        self.assertEqual(category.type, 'opening')
        self.assertTrue(category.is_group_for_opening)

    def test_cash_forecast_category_type_validation(self):
        """Test type validation for cash forecast categories"""
        valid_types = ['income', 'expense', 'opening', 'closing', 'net_forecast', 'pending']
        
        for category_type in valid_types:
            category = self.env['setu.cash.forecast.categories'].create({
                'name': f'Test {category_type} Category',
                'type': category_type,
                'company_id': self.company.id,
                'is_group_for_opening': category_type == 'opening',
            })
            self.assertEqual(category.type, category_type)

    def test_cash_forecast_category_company_isolation(self):
        """Test that cash forecast categories are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create category for other company
        other_category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Other Company Category',
            'type': 'income',
            'company_id': other_company.id,
            'is_group_for_opening': False,
        })
        
        # Search for categories in original company
        company_categories = self.env['setu.cash.forecast.categories'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_category, company_categories)

    def test_cash_forecast_category_unique_constraint(self):
        """Test unique constraint on name and company"""
        # Create first category
        self.env['setu.cash.forecast.categories'].create({
            'name': 'Unique Category',
            'type': 'income',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        # Try to create duplicate - should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['setu.cash.forecast.categories'].create({
                'name': 'Unique Category',
                'type': 'expense',  # Different type but same name
                'company_id': self.company.id,
                'is_group_for_opening': False,
            })

    def test_cash_forecast_category_with_forecast_types(self):
        """Test cash forecast category with associated forecast types"""
        # Create forecast type with the category
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Test Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Check relationship
        self.assertEqual(forecast_type.cash_forecast_category_id, self.category_income)
        
        # Search forecast types by category
        category_forecast_types = self.env['setu.cash.forecast.type'].search([
            ('cash_forecast_category_id', '=', self.category_income.id)
        ])
        
        self.assertIn(forecast_type, category_forecast_types)

    def test_cash_forecast_category_opening_flag_relationship(self):
        """Test opening flag relationship with forecast types"""
        # Create forecast type with opening category
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Opening Forecast Type',
            'type': 'opening',
            'cash_forecast_category_id': self.category_opening.id,
            'account_ids': [(6, 0, [self.account_asset.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Check that is_group_for_opening is inherited
        self.assertTrue(forecast_type.is_group_for_opening)

    def test_cash_forecast_category_copy(self):
        """Test copying cash forecast category"""
        original = self.category_income
        copy = original.copy()
        
        self.assertNotEqual(original.id, copy.id)
        self.assertEqual(copy.name, original.name)
        self.assertEqual(copy.type, original.type)
        self.assertEqual(copy.company_id, original.company_id)
        self.assertEqual(copy.is_group_for_opening, original.is_group_for_opening)

    def test_cash_forecast_category_name_generation(self):
        """Test cash forecast category name generation"""
        category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Generated Name',
            'type': 'income',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        # Test that name is properly set
        self.assertEqual(category.name, 'Generated Name')

    def test_cash_forecast_category_sequence_ordering(self):
        """Test that cash forecast categories are ordered by name"""
        # Create categories in different order
        category3 = self.env['setu.cash.forecast.categories'].create({
            'name': 'Z Category',
            'type': 'income',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        category1 = self.env['setu.cash.forecast.categories'].create({
            'name': 'A Category',
            'type': 'income',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        category2 = self.env['setu.cash.forecast.categories'].create({
            'name': 'M Category',
            'type': 'income',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        categories = self.env['setu.cash.forecast.categories'].search([
            ('company_id', '=', self.company.id)
        ])
        
        # Check ordering
        category1_index = categories.ids.index(category1.id)
        category2_index = categories.ids.index(category2.id)
        category3_index = categories.ids.index(category3.id)
        
        self.assertLess(category1_index, category2_index)
        self.assertLess(category2_index, category3_index)

    def test_cash_forecast_category_with_cash_forecasts(self):
        """Test cash forecast category with associated cash forecasts"""
        # Create cash forecast with the category
        forecast = self.create_test_cash_forecast(
            self.forecast_type_income, 
            self.period_jan, 
            forecast_value=5000.0
        )
        
        # Check that forecast is associated with the category
        self.assertEqual(forecast.cash_forecast_category_id, self.category_income)
        
        # Search forecasts by category
        category_forecasts = self.env['setu.cash.forecast'].search([
            ('cash_forecast_category_id', '=', self.category_income.id)
        ])
        
        self.assertIn(forecast, category_forecasts)

    def test_cash_forecast_category_type_consistency(self):
        """Test type consistency between category and forecast types"""
        # Create forecast type with income category
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Income Forecast Type',
            'type': 'income',
            'cash_forecast_category_id': self.category_income.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Type should match category type
        self.assertEqual(forecast_type.type, self.category_income.type)

    def test_cash_forecast_category_opening_type_validation(self):
        """Test validation for opening type categories"""
        # Create opening category
        opening_category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Opening Category',
            'type': 'opening',
            'company_id': self.company.id,
            'is_group_for_opening': True,
        })
        
        # Create forecast type with opening category
        forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Opening Forecast Type',
            'type': 'opening',
            'cash_forecast_category_id': opening_category.id,
            'account_ids': [(6, 0, [self.account_asset.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        # Check that opening flag is properly set
        self.assertTrue(opening_category.is_group_for_opening)
        self.assertTrue(forecast_type.is_group_for_opening)

    def test_cash_forecast_category_expense_type(self):
        """Test expense type category"""
        expense_category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Expense Category',
            'type': 'expense',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        # Create expense forecast type
        expense_forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Expense Forecast Type',
            'type': 'expense',
            'cash_forecast_category_id': expense_category.id,
            'account_ids': [(6, 0, [self.account_expense.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'past_account_entries',
        })
        
        self.assertEqual(expense_forecast_type.type, 'expense')
        self.assertEqual(expense_forecast_type.cash_forecast_category_id, expense_category)

    def test_cash_forecast_category_closing_type(self):
        """Test closing type category"""
        closing_category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Closing Category',
            'type': 'closing',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        # Create closing forecast type
        closing_forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Closing Forecast Type',
            'type': 'closing',
            'cash_forecast_category_id': closing_category.id,
            'company_id': self.company.id,
            'auto_calculate': True,
        })
        
        self.assertEqual(closing_forecast_type.type, 'closing')
        self.assertEqual(closing_forecast_type.cash_forecast_category_id, closing_category)

    def test_cash_forecast_category_net_forecast_type(self):
        """Test net forecast type category"""
        net_category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Net Forecast Category',
            'type': 'net_forecast',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        # Create net forecast type
        net_forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Net Forecast Type',
            'type': 'net_forecast',
            'cash_forecast_category_id': net_category.id,
            'company_id': self.company.id,
            'auto_calculate': True,
        })
        
        self.assertEqual(net_forecast_type.type, 'net_forecast')
        self.assertEqual(net_forecast_type.cash_forecast_category_id, net_category)

    def test_cash_forecast_category_pending_type(self):
        """Test pending type category"""
        pending_category = self.env['setu.cash.forecast.categories'].create({
            'name': 'Pending Category',
            'type': 'pending',
            'company_id': self.company.id,
            'is_group_for_opening': False,
        })
        
        # Create pending forecast type
        pending_forecast_type = self.env['setu.cash.forecast.type'].create({
            'name': 'Pending Forecast Type',
            'type': 'pending',
            'cash_forecast_category_id': pending_category.id,
            'account_ids': [(6, 0, [self.account_income.id])],
            'company_id': self.company.id,
            'auto_calculate': True,
            'calculate_from': 'pending',
        })
        
        self.assertEqual(pending_forecast_type.type, 'pending')
        self.assertEqual(pending_forecast_type.cash_forecast_category_id, pending_category)
