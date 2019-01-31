# Fix invoice data when the CFDI is v3.2

aml_obj = env['account.move.line']
company = env['res.company'].browse(1)
country = company.country_id.id
company.write({'country_id': False})
for inv in (invoices - invoice_not_updated).filtered(lambda i:i.id in [490, 452, 396, 394, 10]):
# Revisar nuevamente "394", parece ser que se afecto mal
  state = inv.state
  log(message='Se elimino la poliza %s de la factura %s' % (inv.move_id.name, inv.number))
  move = inv.move_id
  move.button_cancel()
  date = inv.date_invoice
  inv.with_context(invoice_id=inv.id).action_invoice_cancel()
  inv.refresh()
  inv.write({'state': 'draft'})
  inv.refresh()
  cfdi = inv.l10n_mx_edi_get_xml_etree()
  for conc in cfdi.Conceptos.Concepto:
    no_id = conc.get('descripcion').split(')')[0][1:]
    lines = inv.invoice_line_ids.filtered(lambda l: l.product_id.default_code == no_id)
    if not lines:
      inv.invoice_line_ids[0].copy({
        'product_id': 2 if float(conc.get('valorUnitario')) <= 0 else env['product.product'].search([('default_code', '=', no_id)]).id, # Aplicación de anticipos
        'name': conc.get('descripcion'),
        'quantity': conc.get('cantidad'),
        'price_unit': float(conc.get('valorUnitario')),
      })
    if inv.id == 10:  # Caso con mismo id, pero diferente precio
      lines = []
    for line in lines:
      price_unit = float(conc.get('ValorUnitario', conc.get('valorUnitario')))
      if line.price_unit != price_unit:
        inv.message_post(body='Se actualizo el precio unitario de la linea del producto %s de %s a %s' % (line.product_id.default_code, line.price_unit, price_unit))
        line.write({'price_unit': price_unit})
  inv.compute_taxes()
  inv.action_invoice_open()
  inv.refresh()
  if date != inv.move_id.date:
    raise Warning('La fecha de la factura es diferente a la de la poliza')
  if state != inv.state:
    raise Warning(inv.state)
    raise Warning('La factura %s ha cambiado de estado' % inv.number)
  total_cfdi = float(cfdi.get('total', cfdi.get('Total')))
  if inv.amount_total != total_cfdi and inv.id not in [396, 10]:
    raise Warning('El total de la factura %s no se pudo corregir, Odoo: %s - CFDI: %s' % (inv.id, inv.amount_total, total_cfdi))
    
company.write({'country_id': country})
