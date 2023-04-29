# -*- coding: utf-8 -*-
{
    'name': "Product Cost Report",

    'summary': """
    Production and business cost classification Production and company costs are classified according to economic usage and location
         """,
    'description': """
       Production and business cost classification Production and company costs are classified according to economic usage and location: - The direct cost of materials - Direct labor expenses - General manufacturing expenses - Costs of production and sales - Enterprise Cost Control This categorization approach, on the one hand, assists businesses in gathering expenses and calculating high prices for each sort of product, item, and service, and on the other hand, assists businesses in managing production costs. Location-based business.
      """,
    "price": "0",
    "currency": "EUR",
    'license': 'GPL-3',
    'author': "TTN SOFTWARE",
    'website': "TTNSOFTWARE.STORE",
    'category': 'App',
    'version': '15.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product', 'purchase', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'reports/casound_bao_cao_xuat_nhap_kho_report_template.xml',
        'reports/casound_bao_cao_gia_thanh_report_template.xml',
        'reports/report.xml',
        'views/casound_product.xml',

        'wizard/casound_bao_cao_xuat_nhap_kho_wizard.xml',
        'wizard/casound_bao_cao_gia_thanh_wizard.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/img/main_screenshot.gif']
}
