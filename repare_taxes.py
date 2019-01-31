# Fixes the taxes on the invoice lines if are differents that the nodes in the CFDI

aml_obj = env['account.move.line']
company = env['res.company'].browse(1)
country = company.country_id.id
company.write({'country_id': False})
invoices = record.browse([574, 572, 10546, 6872, 5786, 5784, 16624])
for inv in (invoices).filtered(lambda i: i.state == 'open'):
  state = inv.state
  date = inv.date_invoice
  move_line_ids = inv.move_id.open_reconcile_view()
  move_line = move_line_ids['domain'][0][2]
  move_line = aml_obj.browse(move_line).filtered(lambda dat: dat.journal_id.id != 4 and dat.account_id.internal_type in ('receivable', 'payable'))
  inv.with_context(invoice_id=inv.id).action_invoice_cancel()
  inv.refresh()
  inv.write({'state': 'draft'})
  inv.refresh()
  cfdi = inv.l10n_mx_edi_get_xml_etree()
  for conc in cfdi.Conceptos.Concepto:
    no_id = conc.get('noIdentificacion', conc.get('NoIdentificacion'))
    lines = inv.invoice_line_ids.filtered(lambda l: l.product_id.default_code == no_id)
    for line in lines:
        if conc.Impuestos:
          tax = env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('name', 'ilike', 'HISTORICO'),
            ('amount', '=', float(conc.Impuestos.Traslados.Traslado.get('TasaOCuota', '0.0')) * 100)])
          if tax:
            line.write({'invoice_line_tax_ids': [(6, 0, tax.ids)]})
    if inv.id == 5784: # Corrijo tax al paquete
      for line in inv.invoice_line_ids:
        line.write({'invoice_line_tax_ids': [(6, 0, tax.ids)]})
  inv.compute_taxes()
  inv.action_invoice_open()
  inv.refresh()
  move_line = move_line.search([('id', 'in', move_line.ids)])
  for move in move_line:
    inv.assign_outstanding_credit(move.id)
  if date != inv.move_id.date:
    raise Warning('La fecha de la factura es diferente a la de la poliza')
  if state != inv.state and inv.id not in [6872, 16624]: # Con el calculo correcto ya esta pagada
    raise Warning('La factura %s ha cambiado de estado' % inv.number)
  total_cfdi = float(cfdi.get('total', cfdi.get('Total')))
  if inv.amount_total != total_cfdi:
    raise Warning('El total de la factura %s no se pudo corregir, Odoo: %s - CFDI: %s' % (inv.id, inv.amount_total, total_cfdi))
    
company.write({'country_id': country})
