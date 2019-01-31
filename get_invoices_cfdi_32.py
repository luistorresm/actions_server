invoices = record.search([
  ('type', 'in', ['out_invoice', 'out_refund']),
  ('date_invoice', '<', '01/01/2018'),
  ])
  
inv_32 = []
for invoice in invoices:
  cfdi = invoice.l10n_mx_edi_get_xml_etree()
  if cfdi.get('version') == '3.2':
    inv_32.append(invoice.id)

log(message='Facturas%s' % inv_32, level='info')  
