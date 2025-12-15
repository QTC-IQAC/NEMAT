# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'NEMAT'
copyright = '2025, Albert Ortega-Bartolomé'
author = 'Albert Ortega-Bartolomé'
release = '0.9'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    'sphinx_tabs.tabs',
]
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ["custom.css"]


html_theme_options = {
    # GitHub integration
    # "light_logo": "images/logo_light.png",    
    # "dark_logo": "images/logo_dark.png",      
    "source_repository": "https://github.com/QTC-IQAC/NEMAT",
    "source_branch": "main",
    "source_directory": "docs",
    "navigation_with_keys": True,
    "sidebar_hide_name": False,
    "dark_css_variables": {
        "color-brand-primary": "#C7B02C",
        "color-brand-content": "#C7B02C",
    },
    "navigation_with_keys": True
    }



