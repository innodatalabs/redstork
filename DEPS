use_relative_paths = True

vars = {
  'pdfium_url': 'https://pdfium.googlesource.com',

  # GN CIPD package version.
  'gn_version': 'git_revision:9499562d94bf142f43d03622492e67b217461f67',

  'pdfium_version': '7bb6613a0b68569f94e9ff271a111dfe8de88097',
}

deps = {
  'pdfium':
    Var('pdfium_url') + '/pdfium.git@' + Var('pdfium_version'),
}
