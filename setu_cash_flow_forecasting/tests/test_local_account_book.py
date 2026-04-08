# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import tagged
from datetime import date
from .common import SuCashForecastTestCommon


@tagged('post_install', '-at_install')
class TestLocalAccountBook(SuCashForecastTestCommon):
    """Test cases for local.account.book model"""

    def test_local_account_book_creation(self):
        """Test basic local account book creation"""
        account_book = self.env['local.account.book'].create({
            'name': 'Test Account Book Entry',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        self.assertEqual(account_book.name, 'Test Account Book Entry')
        self.assertEqual(account_book.account_id, self.account_income)
        self.assertEqual(account_book.debit, 1000.0)
        self.assertEqual(account_book.credit, 0.0)
        self.assertEqual(account_book.company_id, self.company)

    def test_local_account_book_company_isolation(self):
        """Test that local account book entries are properly isolated by company"""
        # Create another company
        other_company = self.env['res.company'].create({
            'name': 'Other Company',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Create account book entry for other company
        other_entry = self.env['local.account.book'].create({
            'name': 'Other Company Entry',
            'account_id': self.account_income.id,
            'debit': 500.0,
            'credit': 0.0,
            'date': date.today(),
            'company_id': other_company.id,
        })
        
        # Search for entries in original company
        company_entries = self.env['local.account.book'].search([
            ('company_id', '=', self.company.id)
        ])
        
        self.assertNotIn(other_entry, company_entries)

    def test_local_account_book_date_filtering(self):
        """Test local account book date filtering"""
        # Create entries with different dates
        entry1 = self.env['local.account.book'].create({
            'name': 'Entry 1',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date(2024, 1, 15),
            'company_id': self.company.id,
        })
        
        entry2 = self.env['local.account.book'].create({
            'name': 'Entry 2',
            'account_id': self.account_income.id,
            'debit': 2000.0,
            'credit': 0.0,
            'date': date(2024, 2, 15),
            'company_id': self.company.id,
        })
        
        # Search for entries in January
        jan_entries = self.env['local.account.book'].search([
            ('date', '>=', date(2024, 1, 1)),
            ('date', '<=', date(2024, 1, 31)),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(entry1, jan_entries)
        self.assertNotIn(entry2, jan_entries)

    def test_local_account_book_account_filtering(self):
        """Test local account book account filtering"""
        # Create entries with different accounts
        income_entry = self.env['local.account.book'].create({
            'name': 'Income Entry',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        expense_entry = self.env['local.account.book'].create({
            'name': 'Expense Entry',
            'account_id': self.account_expense.id,
            'debit': 0.0,
            'credit': 500.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        # Search for income account entries
        income_entries = self.env['local.account.book'].search([
            ('account_id', '=', self.account_income.id),
            ('company_id', '=', self.company.id)
        ])
        
        self.assertIn(income_entry, income_entries)
        self.assertNotIn(expense_entry, income_entries)

    def test_local_account_book_debit_credit_validation(self):
        """Test local account book debit/credit validation"""
        # Create entry with both debit and credit
        entry = self.env['local.account.book'].create({
            'name': 'Test Entry',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 500.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        self.assertEqual(entry.debit, 1000.0)
        self.assertEqual(entry.credit, 500.0)

    def test_local_account_book_balance_calculation(self):
        """Test local account book balance calculation"""
        # Create entries for balance calculation
        self.env['local.account.book'].create({
            'name': 'Debit Entry',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        self.env['local.account.book'].create({
            'name': 'Credit Entry',
            'account_id': self.account_income.id,
            'debit': 0.0,
            'credit': 300.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        # Calculate balance
        entries = self.env['local.account.book'].search([
            ('account_id', '=', self.account_income.id),
            ('company_id', '=', self.company.id)
        ])
        
        total_debit = sum(entries.mapped('debit'))
        total_credit = sum(entries.mapped('credit'))
        balance = total_debit - total_credit
        
        self.assertEqual(balance, 700.0)

    def test_local_account_book_copy(self):
        """Test copying local account book entry"""
        original = self.env['local.account.book'].create({
            'name': 'Original Entry',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        copy = original.copy()
        
        self.assertNotEqual(original.id, copy.id)
        self.assertEqual(copy.name, original.name)
        self.assertEqual(copy.account_id, original.account_id)
        self.assertEqual(copy.debit, original.debit)
        self.assertEqual(copy.credit, original.credit)
        self.assertEqual(copy.company_id, original.company_id)

    def test_local_account_book_name_generation(self):
        """Test local account book name generation"""
        entry = self.env['local.account.book'].create({
            'name': 'Generated Name',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date.today(),
            'company_id': self.company.id,
        })
        
        # Test that name is properly set
        self.assertEqual(entry.name, 'Generated Name')

    def test_local_account_book_sequence_ordering(self):
        """Test that local account book entries are ordered by date"""
        # Create entries in different order
        entry3 = self.env['local.account.book'].create({
            'name': 'Entry 3',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date(2024, 3, 15),
            'company_id': self.company.id,
        })
        
        entry1 = self.env['local.account.book'].create({
            'name': 'Entry 1',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date(2024, 1, 15),
            'company_id': self.company.id,
        })
        
        entry2 = self.env['local.account.book'].create({
            'name': 'Entry 2',
            'account_id': self.account_income.id,
            'debit': 1000.0,
            'credit': 0.0,
            'date': date(2024, 2, 15),
            'company_id': self.company.id,
        })
        
        entries = self.env['local.account.book'].search([
            ('company_id', '=', self.company.id)
        ])
        
        # Check ordering
        entry1_index = entries.ids.index(entry1.id)
        entry2_index = entries.ids.index(entry2.id)
        entry3_index = entries.ids.index(entry3.id)
        
        self.assertLess(entry1_index, entry2_index)
        self.assertLess(entry2_index, entry3_index)
