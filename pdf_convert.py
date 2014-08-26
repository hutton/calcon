import StringIO

__author__ = 'simonhutton'

from xhtml2pdf import pisa             # import python module

# Define your data
sourceHtml = "<html><body><p>To PDF or not to PDF<p></body></html>"
outputFilename = "test.pdf"

# Utility function
def convertHtmlToPdf(source_html):
    # open output file for writing (truncated binary)
    packet = StringIO.StringIO()

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=packet)           # file handle to recieve result


    packet.seek(0)

    # return True on success and False on errors
    return packet

# Main program
if __name__=="__main__":
    pisa.showLogging()
    convertHtmlToPdf(sourceHtml, outputFilename)
