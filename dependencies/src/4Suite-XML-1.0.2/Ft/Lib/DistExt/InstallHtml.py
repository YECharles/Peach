import os, re
from Ft.Lib import Uri
from Ft.Lib.DistExt import InstallDocs

class InstallHtml(InstallDocs.InstallDocs):

    command_name = 'install_html'

    description = "install HTML documentation"

    # The extension used for the generated HTML files
    output_extension = '.html'

    def finalize_options(self):
        if self.install_dir is None:
            install = self.get_finalized_command('install')
            self.install_dir = os.path.join(install.install_docs, 'html')
        return InstallDocs.InstallDocs.finalize_options(self)

    def get_default_stylesheets(self):
        return {'docbook' : 'docbook_html.xslt',
                'sdocbook' : 'sdocbook_html.xslt',
                'modules' : 'modules_html.xslt',
                'extensions' : 'extensions_html.xslt',
                'commandline' : 'commandline_html.xslt',
                'docbook_html' : 'docbook_html1.xslt',
                }

    def get_default_css(self):
        """
        Returns a mapping of stylesheet names to their associated CSS.

        The CSS file is assumed to be relative to the stylesheet URI.
        """
        return {'docbook' : 'docbook_html.css',
                'sdocbook' : 'sdocbook_html.css',
                'modules' : 'modules.css',
                'extensions' : 'extensions.css',
                'commandline' : 'commandline.css',
                }

    def get_stylesheet_extras(self, stylesheet, base_uri):
        css = self.get_default_css().get(stylesheet)
        if css is None:
            return []

        def find_css_uris(uri):
            """Find all the CSS dependencies (@import directives)."""
            uris = [uri]
            stream = Uri.UrlOpen(uri)
            for line in Uri.UrlOpen(uri).readlines():
                match = re.match(r"\s*@import\s+url\s*\((.*)\)", line)
                if match:
                    next_uri = Uri.BaseJoin(uri, eval(match.group(1)))
                    uris.extend(find_css_uris(next_uri))
            return uris

        return find_css_uris(Uri.BaseJoin(base_uri, css))

    def get_output_filename(self, document):
        basedir, basename = os.path.split(document.source)
        basedir = basedir[len(self.build_dir) + len(os.sep):]
        basename, source_ext = os.path.splitext(basename)
        basename += self.output_extension
        return os.path.join(self.install_dir, basedir, basename)
