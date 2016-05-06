import sys
import guzzle_sphinx_theme

sys.path.insert(0, '..')

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'numpydoc',
    'sphinx.ext.autosummary',
    'guzzle_sphinx_theme'
]

napoleon_google_docstring = False
napoleon_numpy_docstring = True
autosummary_generate = True

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'bandicoot'
copyright = u'2014-2015, Yves-Alexandre de Montjoye, Luc Rocher, Alex Pentland'
version = '0.5'
release = '0.5.0'

exclude_patterns = ['_build']
pygments_style = 'sphinx'


# -- Options for HTML output ----------------------------------------------

html_translator_class = 'guzzle_sphinx_theme.HTMLTranslator'
html_theme = 'guzzle_sphinx_theme'
html_theme_options = {
  "project_nav_name": "bandicoot",
  "google_analytics_account": "UA-11680375-10"
}
html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_static_path = ['_static']
htmlhelp_basename = 'bandicootdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}
latex_documents = [
  ('index', 'bandicoot.tex', u'bandicoot Documentation',
   u'Yves-Alexandre de Montjoye, Luc Rocher, Alex Pentland', 'manual'),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    ('index', 'bandicoot', u'bandicoot Documentation',
     [u'Yves-Alexandre de Montjoye, Luc Rocher, Alex Pentland'], 1)
]

# -- Options for Texinfo output -------------------------------------------
texinfo_documents = [
  ('index', 'bandicoot', u'bandicoot Documentation',
   u'Yves-Alexandre de Montjoye, Luc Rocher, Alex Pentland',
   'bandicoot', 'A python toolbox for mobile phone metadata',
   'Miscellaneous'),
]
