# When is created a new register, verify that partner have VAT, and
# create and validate automatically the invoice
object.action_create_invoice()
# Are related the customer journals with the id of payment method
# Dict = {journal_id: payment_method_id}
mapping = {
    37: 3,
    35: 3,
    36: 3,
    31: 4,
    32: 4,
    33: 4,
    34: 3,
    26: 4,
    1: 1,
    2: 1,
    22: 1,
    29: 1,
    30: 1}
# I make sure that journal exist in the system
if env['account.journal'].search([('id', 'in', mapping.keys())]):
    # Search in all payments related with the order the movement with
    # more amount to assign like payment method
    statement = env['account.bank.statement.line'].search(
        [('id', 'in', object.statement_ids.ids)], order='amount', limit=1)
    # Write the payment method that are taken from mapping dict
    object.invoice_id.write(
        {'payment_method_id': mapping.get(statement.journal_id.id, False)})
object.action_validate_invoice()
