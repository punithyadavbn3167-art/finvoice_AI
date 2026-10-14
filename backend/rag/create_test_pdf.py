from reportlab.pdfgen import canvas

pdf = canvas.Canvas("test_financial_report.pdf")

pdf.drawString(100, 750, "Financial Report 2026")
pdf.drawString(100, 700, "Revenue: Rs. 15,00,000")
pdf.drawString(100, 650, "Expenses: Rs. 8,00,000")
pdf.drawString(100, 600, "Profit: Rs. 7,00,000")
pdf.drawString(100, 550, "The company increased revenue compared with the previous year.")

pdf.save()

print("PDF created successfully.")