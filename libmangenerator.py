import datetime
"""
    Este fichero pertenece al proyecto devicesinlan. Si es modificado debe ser ahí y volver a copiarse a otros proyectos
"""
class Man:
    """
        Syntax
        .BR: Colorized first word
        .B: Colorized first word
        .IR: Underline first word
        .nf turns off paragraph filling mode: we don't want that for showing command lines.
.fi turns it back on.
.RS starts a relative margin indent: examples are more visually distinguishable if they're indented.
.RE ends the indent.
\\ puts a backslash in the output. Since troff uses backslash for fonts and other in-line commands, it needs to be doubled in the manual page source so that the output has one.
If you write more than one paragraph, start the other paragraphs with the .PP command. Do not just leave an empty line; this makes troff sometimes do the wrong thing. In fact, the manual page source should have no empty lines at all.
    """
    
    def __init__(self, filename, language="en"):
        """
            Filename is without extension
        """
        self.filename=filename
        self.language=language
        self.doc=""
        self.html=""#Variable where html output is generated
        
    def tr(self, s):
        """
            Used to translate predefined titles and to avoid to load a i18n system
        """
        if self.language=="es":
            if s=="NAME":
                return "NOMBRE"
            elif s=="SYNOPSIS":
                return "SINOPSIS"
            elif s=="DESCRIPTION":
                return "DESCRIPCIÓN"
        
    def append(self, s):
        """Id doesnit finish in \n"""
        s=s.replace("-", "\-")
        self.doc=self.doc+s
        
    def replaceUTF8(self, s):
        s=s.replace("Á", "\('A")
        s=s.replace("É", "\('E")
        s=s.replace("Í", "\('I")
        s=s.replace("Ó", "\('O")
        s=s.replace("Ú", "\('U")
        s=s.replace("á", "\('a")
        s=s.replace("é", "\('e")
        s=s.replace("í", "\('i")
        s=s.replace("ó", "\('o")
        s=s.replace("ú", "\('u")
        s=s.replace("ñ", "\(~n")
        s=s.replace("Ñ", "\(~N")
        return s
    
    def paragraph(self, s,  level=1, bold=False):
        self.append(".PP\n")
        if bold==True:
            bo=".B "
        else:
            bo=""
        self.append(".RS\n"*(level-1))
        self.append("{}{}\n".format(bo, s))
        self.append(".RE\n"*(level-1))
        #HTML
        if bold==True:
            self.html=self.html + "<p>{}<strong>{}</strong></p>\n".format("&nbsp;"*8*level, s)
        else:
            self.html=self.html + "<p>{}{}</p>\n".format("&nbsp;"*8*level, s)
        
        
    def setMetadata(self, projectname,   manlevel,  date,  author,  brief):
        """
            Must be the first command
        """
        self.projectname=projectname
        self.author=author
        self.manlevel=manlevel
        self.append(".TH {} {} {}\n".format(self.projectname.upper(), self.manlevel, date))
        self.header("NAME", 1)
        self.append(".B {}:\n".format(self.projectname))
        self.append("{}\n".format(brief))
        #HTML
        self.html="""
<html>
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <title>{0} - {1}</title>
</head>
<body>
<h1>NAME</h1>
<p>{0}: {2}</p>
        """.format(self.projectname, self.author, brief)
        
    def setSynopsis(self, args):
        """
            args: Es un string con la cadena tipo argparse [ --list | --help ]
        """
        ##################
        self.header("SYNOPSIS")
        self.append("{} {}\n".format(self.projectname, args))
        #HTML
        self.html=self.html + "<p>{} {}</p>\n".format(self.projectname, args)

    def header(self, text, level=1):
        if level==1:
            self.append(".SH {}\n\n".format(text.upper()))
        elif level==2:
            self.paragraph("* "+ text.upper(), level, bold=True)
        elif level==3:
            self.paragraph("+ "+ text.upper(), level, bold=True)
        elif level==4:
            self.paragraph("- "+ text.upper(), level, bold=True)
            
        #HTML
        self.html=self.html + "<H{0}>{1}</H{0}>\n".format(level, text)

    def save(self):
        """
            UTF-8, fails. I decided to save like UTF-8 file for better HTML support
            For spanish I change then `o por \|('o  ...
            HTML generation uses the doc without substitituion
        """
        f=open("{}.{}".format(self.filename, self.manlevel), "w")
        f.write(self.replaceUTF8(self.doc))
        f.close()
        #HTML
        self.html=self.html + """
<hr>
<p>Created with libmangenerator at {}</p>
</body>
</html>""".format(datetime.date.today())

    def saveHTML(self):
        f=open("{}.{}.html".format(self.filename, self.manlevel), "w")
        f.write(self.html)
        f.close()

    def simpleParagraph(self, text, style="Standard"):
        pass
        
    def list(self, arr, style="BulletList"):
        pass
                
    def numberedList(self, arr, style="NumberedList"):
        pass


if __name__ == "__main__":
    doc=Man("libmangenerator")
    doc.setMetadata("LibManGenerator module",  1,   datetime.date.today(), "Mariano Muñoz", "This is a python module who writes easily a Man page")
    doc.setSynopsis("[ --help | --version ]")
    doc.header("DESCRIPTION", 1)
    doc.paragraph("This module allows to write Man pages", 1)
    doc.paragraph("Morever, can save a doc like a HTML page")
    doc.header("EXAMPLES", 1)
    doc.paragraph("This is a level 1 indent", 1)
    doc.paragraph("This is a level 2 indent", 2)
    doc.header("More examples", 2)
    doc.paragraph("This is a level 3 indent in bold", 3, True)
    doc.save()
    doc.saveHTML()
