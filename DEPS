use_relative_paths = True

vars = {
  'chromium_git': 'https://chromium.googlesource.com',
  'pdfium_url': 'https://pdfium.googlesource.com',

  # GN CIPD package version.
  'gn_version': 'git_revision:9499562d94bf142f43d03622492e67b217461f67',

  'pdfium_version': '7bb6613a0b68569f94e9ff271a111dfe8de88097',

  'buildtools_revision': '4164a305626786b1912d467003acf4c4995bec7d',
}

deps = {
  'pdfium':
    Var('pdfium_url') + '/pdfium.git@' + Var('pdfium_version'),

  'buildtools':
    Var('chromium_git') + "/chromium/src/buildtools.git@" +
        Var('buildtools_revision'),

}
