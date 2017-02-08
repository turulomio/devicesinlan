import datetime
from subprocess import Popen, PIPE
"""
    If you want to saveHTML you need to have in your path man2html
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
            bold=".B "
        else:
            bold=""
        self.append(".RS\n"*(level-1))
        self.append("{}{}\n".format(bold, s))
        self.append(".RE\n"*(level-1))
        
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
        
    def setSynopsis(self, args):
        """
            args: Es un string con la cadena tipo argparse [ --list | --help ]
        """
        ##################
        self.header("SYNOPSIS")
        self.append("{} {}\n".format(self.projectname, args))

    def header(self, text, level=1):
        if level==1:
            self.append(".SH {}\n\n".format(text.upper()))
        elif level==2:
            self.paragraph("* "+ text.upper(), level, bold=True)
        elif level==3:
            self.paragraph("+ "+ text.upper(), level, bold=True)
        elif level==4:
            self.paragraph("- "+ text.upper(), level, bold=True)

    def save(self):
        """
            UTF-8, fails. I decided to save like UTF-8 file for better HTML support
            For spanish I change then `o por \|('o  ...
            HTML generation uses the doc without substitituion
        """
        f=open("{}.{}".format(self.filename, self.manlevel), "w")
        f.write(self.replaceUTF8(self.doc))
        f.close()
        
    def saveHTML(self):
        s = Popen(['man2html'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, errs = s.communicate(self.doc.encode())
        
        f=open("{}.{}.html".format(self.filename, self.manlevel), "w")
        arr=output.decode().split("\n")
        for i, line in enumerate(arr):
            if i in [0, 1, 5, 6,  len(arr)-9, len(arr)-10, len(arr)-11, len(arr)-12, len(arr)-13, len(arr)-14, len(arr)-15, len(arr)-16]:#I delete ugly lines #MAN2HTML --1.6g
                continue
            if line.startswith("<HTML><HEAD>"):
                line=line.replace('<HTML><HEAD>', '<HTML><HEAD><meta charset="UTF-8" />')
            f.write(line+"\n")
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
