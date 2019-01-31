# Server action para corregir las facturas previamente creadas, toma los valores correctos del CFDUI adjunto
aml_obj = env['account.move.line']
company = env['res.company'].browse(1)
country = company.country_id.id
company.write({'country_id': False})
invoices = record.browse([1174, 818, 640, 638, 630, 590, 586, 584, 574, 572, 556, 554, 27544, 540, 490, 488, 456, 452, 440, 396, 394, 384, 354, 352, 336, 326, 310, 288, 250, 244, 238, 144, 10, 28832, 4, 10546, 6872, 5786, 5784, 16624, 12894, 28494, 28709])
invoice_not_updated = record.browse([640, 638, 630, 590, 586, 584, 556, 554, 27544, 490, 452, 396, 394, 336, 10, 4, 10546, 6872, 5786, 5784, 16624]) # CFDI con 4 decimales y Odoo solo 2
# 3.2 (490, 452, 396, 394, 10)
# La factura 4 se omite porque las diferencias son minimas y es un paquete
for inv in (invoices - invoice_not_updated).filtered(lambda i: i.state != 'draft'):
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
    if not no_id:
      no_id = conc.get('descripcion').split(')')[0][1:]
    if inv.id == 326 and no_id == 'ANBR14300': # Para este caso no cuadra una linea 
      no_id = 'BR14300'
    lines = inv.invoice_line_ids.filtered(lambda l: l.product_id.default_code == no_id and l.quantity == float(conc.get('cantidad', conc.get('Cantidad'))))
    for line in lines:
      price_unit = float(conc.get('ValorUnitario', conc.get('valorUnitario')))
      if line.price_unit != price_unit:
        inv.message_post(body='Se actualizo el precio unitario de la linea del producto %s de %s a %s' % (line.product_id.default_code, line.price_unit, price_unit))
        line.write({'price_unit': price_unit})
    if not lines:
      inv.invoice_line_ids.copy({
        'product_id': env['product.product'].search([('default_code', '=', no_id)]).id, # Aplicación de anticipos
        'name': conc.get('Descripcion'),
        'quantity': conc.get('Cantidad'),
        'price_unit': float(conc.get('ValorUnitario')),
      })
  inv.compute_taxes()
  inv.action_invoice_open()
  inv.refresh()
  move_line = move_line.search([('id', 'in', move_line.ids)])
  for move in move_line:
    try:
      inv.assign_outstanding_credit(move.id)
    except:
      pass
  if date != inv.move_id.date:
    raise Warning('La fecha de la factura es diferente a la de la poliza')
  if state != inv.state:
    raise Warning('La factura %s ha cambiado de estado' % inv.number)
  total_cfdi = float(cfdi.get('total', cfdi.get('Total')))
  if inv.amount_total != total_cfdi and inv.id not in [488, 440, 384, 354, 336, 326, 250, 238, 144]: # Excepciones por minimos
    raise Warning('El total de la factura %s no se pudo corregir, Odoo: %s - CFDI: %s' % (inv.id, inv.amount_total, total_cfdi))
  move_line_ids = inv.move_id.open_reconcile_view()
    
company.write({'country_id': country})
