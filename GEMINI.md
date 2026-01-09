Gemini – Odoo ${ODOO_VERSION} Folder Structure Rule

This document defines the global folder structure for Odoo ${ODOO_VERSION} modules in the Antigravity project.
The structure is standardized for compatibility, maintainability, and consistency across all modules.

Module Folder Structure
your_module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── views/
│   ├── model_name_views.xml
│   └── menus.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── data.xml
├── demo/
│   └── demo.xml
├── wizard/
│   ├── __init__.py
│   └── wizard_name.py
├── report/
│   ├── report.xml
│   └── report_template.xml
├── static/
│   └── src/
│       ├── js/
│       ├── css/
│       └── xml/
├── tests/
│   ├── __init__.py
│   └── test_module.py
└── README.md

Folder Structure Guidelines
1. __init__.py

Purpose: Initializes the Python package for the module.

Location: Root of the module and in the models/ and wizard/ subfolders.

2. __manifest__.py

Purpose: Contains the metadata of the module.

Required fields: name, version, depends, data, installable, etc.

Example:

{
    'name': 'My Odoo ${ODOO_VERSION} Module',
    'version': '${ODOO_VERSION}.1.0.0',
    'author': 'Your Company',
    'website': 'https://example.com',
    'category': 'Category',
    'depends': ['base'],
    'data': [
        'views/my_feature_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}

3. models/

Purpose: Contains all Python classes and business logic.

Each model should have its own file named with the model’s technical name (e.g., product.py, sale_order.py).

Folder contents:

Model definitions

Business logic functions

Methods related to ORM models

4. views/

Purpose: Contains all XML files related to views and UI actions.

Example views: form views, tree views, kanban views, search views, etc.

Menu items and actions should also be defined here.

5. security/

Purpose: Manages access control lists (ACLs), groups, and record rules.

Mandatory file: ir.model.access.csv to define model access rules.

Additional security rules can go into security.xml (e.g., record rules, user groups).

6. data/

Purpose: Contains XML or CSV files with static data that needs to be loaded on installation or updates.

Examples: default records, settings, sequences, demo data, etc.

7. demo/

Purpose: Contains demo data (optional).

Loaded only when demo data is enabled.

For showcasing the module in the Odoo demo environment.

8. wizard/

Purpose: Contains transient models (wizards).

These models manage pop-up forms, multi-step workflows, or dialogs.

Each wizard should be implemented as a Python class in its own file (e.g., wizard_name.py).

9. report/

Purpose: Contains files related to report generation.

Examples: QWeb templates, PDF reports, custom actions related to printing.

Folder contents:

report.xml – to register report actions

report_template.xml – the QWeb template

10. static/

Purpose: Frontend assets.

JavaScript (OWA), CSS, and other assets (e.g., images).

Structure:

static/src/js/ – JavaScript files

static/src/css/ – CSS files

static/src/xml/ – OWL components or other XML files

11. tests/

Purpose: Contains automated tests for the module.

Tests ensure that features work as expected.

Recommended to have unit tests, transaction tests, and mock data for testing.

Each test file should be in Python and follow the structure of the module it tests (e.g., test_model_name.py).

12. README.md

Purpose: Provides documentation for the module.

Contents:

Purpose of the module

Dependencies and installation steps

Usage instructions

Known issues and limitations

General Rules for Odoo ${ODOO_VERSION} Modules

Module Folder Name: The folder name should be in snake_case and match the module's technical name (e.g., my_feature).

Avoid Versioning in Module Name: Do not include version numbers in the folder name. Use versioning in the __manifest__.py.

Module Dependencies: Always define dependencies using the depends field in __manifest__.py. Dependencies should include other Odoo modules as well as Python packages.

Separate Models and Views: Keep business logic (models) separate from UI definitions (views) for clarity and organization.

No Hardcoded Paths: Avoid hardcoding paths to views, actions, or reports in code. Use the data attribute in __manifest__.py to define them.

Use ir.model.access.csv for ACL: Always define model access rules in security/ir.model.access.csv.

Use demo.xml for Demo Data: Only use the demo/ folder for demo-specific data.

Minimal Tests: Always include at least one test in the tests/ folder to verify core functionality (e.g., creating records, checking workflows).

Checklist for New Odoo ${ODOO_VERSION} Module

 Create folder structure with models/, views/, and security/ at a minimum.

 Add __init__.py and __manifest__.py files.

 Add core models and views.

 Provide necessary security access rules in ir.model.access.csv.

 Document module functionality in README.md.

 Write automated tests in tests/.

 Define static assets (CSS, JS) in static/ if applicable.

Additional Notes

Odoo 19 Compatibility: This structure is compatible with Odoo 19. Modules should be Python 3.10+ compliant.

Testing: Use unittest or pytest for Python-based tests, and ensure that tests cover both happy paths and edge cases.

This rule ensures all Odoo ${ODOO_VERSION} modules follow a consistent structure, improving readability, maintainability, and testing. It also aligns with best practices for Odoo development, providing a foundation for automated workflows and CI/CD pipelines.