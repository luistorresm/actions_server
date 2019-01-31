logg = env['ir.logging'].search([('func', '=', 'Invoice 3.2')])
invoices = []
invoices.extend(logg.message.split('[')[1][:-1].split(','))
invoices_32 = record.search([('id', 'in', invoices)])

bad_invoices = []
for inv in invoices_32:
  cfdi = inv.l10n_mx_edi_get_xml_etree()
  if abs((round(inv.amount_total, 2) - round(float(cfdi.get('total')), 2))) > 1:
    for line in cfdi.Conceptos.Concepto:
      if float(line.get('importe')) < 0:
        bad_invoices.append(inv.id)
        continue
    
log(
  message='Facturas que tienen importe negativo en el XML (Son: [%s] facturas) %s' % (len(bad_invoices), bad_invoices), level='info') 
