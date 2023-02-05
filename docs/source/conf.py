# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from pycognaize import __version__

exclude_patterns = ["_build",
                    "_templates"
                    "Thumbs.db",
                    ".DS_Store",
                    '**pycognaize/temp*',
                    '**pycognaize/tests*',
                    ]
# -- Project information -----------------------------------------------------

project = 'Cognaize Python SDK'
# noinspection PyShadowingBuiltins
copyright = '2022, Cognaize CJSC'
author = 'Cognaize'
autosummary_generate = True
autosummary_mock_imports = [
    'pycognaize.tests',
    'pycognaize.temp',
]
# The full version, including alpha/beta/rc tags
version = __version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx_tabs.tabs",
    "sphinx_search.extension",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    # "sphinx_autodoc_annotation",
    "rst2pdf.pdfbuilder",
    "sphinx_autodoc_typehints",
    # "recommonmark",
    "myst_parser",
    "sphinx.ext.autosectionlabel",
    'sphinx.ext.doctest'
]

# MAKE TARGET LINKS
# Make sure the target is unique
autosectionlabel_prefix_document = True

# TYPEHINTS
autodoc_typehints = "description"
always_document_param_types = True
typehints_document_rtype = True

# Only relative names of modules
add_module_names = False

# SPELLCHECKING
try:
    import sphinxcontrib.spelling
except ImportError:
    pass
else:
    extensions.append("sphinxcontrib.spelling")
spelling_word_list_filename = 'wordlist.txt'

pdf_documents = [(
    'index',
    f'Cognaize Python SDK - version {version}',
    'Cognaize Python SDK',
    'Cognaize'
), ]
# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_title = 'Cognaize Python SDK'
html_theme = 'sphinx_rtd_theme'
pdf_stylesheets = ['twocolumn']
html_theme_options = {
    "navigation_depth": 4,
    "titles_only": False,
    "logo_only": True,
    # "github_url": 'https://github.com/cognaize/pycognaize',

    # Set the name of the project to appear in the navigation.
    # 'nav_title': 'Cognaize Python SDK',

    # Set you GA account ID to enable tracking
    # 'google_analytics_account': 'UA-XXXXX',

    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    # 'base_url': 'https://www.cognaize.com',

    # Set the color and the accent color
    # 'color_primary': 'magenta',
    # 'color_accent': 'pink',

    # Set the repo location to get a badge with stats
    # 'repo_url': 'https://github.com/cognaize/pycognaize',
    # 'repo_name': 'pycognaize',
    'navigation_with_keys': True,
    # Visible levels of the global TOC; -1 means unlimited
    # 'globaltoc_depth': 4,
    # If False, expand all TOC entries
    'globaltoc_collapse': False,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,
    # 'theme_color': '#152E4D',
    # 'html_minify': True,
    # 'css_minify': True,
}
html_static_path = ['_static']

html_logo = './_static/logo.png'
html_favicon = './_static/square_logo.png'
html_sidebars = {
    "**": [
        # "fulltoc.html",
        # "relations,html",
        # "sourcelink.html",
        "logo-text.html",
        "globaltoc.html",
        "localtoc.html",
        "searchbox.html",
        # "contents.html"
    ]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# Versioning
master_doc = 'index'
