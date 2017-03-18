import codelyzer
sanitizerDir = None
codelyzer.veraAnalysis()
sanitizerOn = vera.getParameter("sanitizer-on", "True")
if sanitizerOn == "True":
    sanitizerDir = vera.getParameter("sanitizer-dir",  "/task/student/sanitizer")
    sanitizerFile = vera.getParameter("sanitizer-file", "None")
    codelyzer.sanitizerAnalysis(sanitizerDir, sanitizerFile)
codelyzer.indentationAnalysis()