#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import datetime
from decimal import Decimal
from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond import backend
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool, If, PYSONEncoder, Id

__all__ = ['Purchase']
__metaclass__ = PoolMeta

_NOPAGOS = [
    ('1', '1 Pago'),
    ('2', '2 Pagos'),
    ('3', '3 Pagos'),
    ('4', '4 Pagos'),
]


_STATES = {
    'readonly': Eval('state') != 'draft',
    }

class Purchase():
    'Purchase'
    __name__ = 'purchase.purchase'
    _rec_name = 'reference'

    no_pagos = fields.Selection(_NOPAGOS, 'No. de Pagos', states= _STATES)

    plazo1 = fields.Integer('Dias', states={
        'required': Eval('no_pagos').in_(['1','2','3', '4']),
        'readonly': Eval('state') != 'draft',
    })
    plazo2 = fields.Integer('Dias', states={
        'invisible': Eval('no_pagos').in_(['1']),
        'required': Eval('no_pagos').in_(['2', '3', '4']),
        'readonly': Eval('state') != 'draft',
    })
    plazo3 = fields.Integer('Dias', states={
        'invisible': Eval('no_pagos').in_(['1', '2']),
        'required': Eval('no_pagos').in_(['3', '4']),
        'readonly': Eval('state') != 'draft',
    })
    plazo4 = fields.Integer('Dias', states={
        'invisible': Eval('no_pagos').in_(['1', '2', '3']),
        'required': Eval('no_pagos').in_(['4']),
        'readonly': Eval('state') != 'draft',
    })

    @classmethod
    def __setup__(cls):
        super(Purchase, cls).__setup__()

    @classmethod
    def default_no_pagos(cls):
        return "1"

    def create_payment_term(self):
        no_pagos = self.no_pagos
        Term = Pool().get('account.invoice.payment_term')
        term = Term()
        PaymentTermLine = Pool().get('account.invoice.payment_term.line')

        if no_pagos == '1':
            dias = self.plazo1
            lines= []
            name = "Pago " + str(dias) + " dias"

            terms = Term.search([('name','=', name)])
            if terms:
                for t in terms:
                    term = t
            else:
                term = Term()
                term.name = name
                term_line = PaymentTermLine(type='remainder', days=dias, divisor=Decimal(0.0))
                lines.append(term_line)
                term.lines = lines
                term.save()

        elif no_pagos == '2':
            dias = self.plazo1
            dias2 = self.plazo2
            percentage = Decimal(50)
            lines= []
            name = "Pago " + str(dias) + " - " + str(dias2) + " dias"
            terms = Term.search([('name','=', name)])

            divisor = Decimal(str(round(100/percentage, 8)))

            if terms:
                for t in terms:
                    term = t
            else:
                term = Term()
                term.name = name
                term_line = PaymentTermLine(type='percent_on_total', percentage= percentage, days=dias, divisor=divisor)
                lines.append(term_line)

                term_line2 = PaymentTermLine(type='remainder', days=dias2, divisor=Decimal(0.0))
                lines.append(term_line2)

                term.lines = lines
                term.save()

        elif no_pagos == '3':
            dias = self.plazo1
            dias2 = self.plazo2
            dias3 = self.plazo3
            percentage = Decimal(33)
            lines= []
            name = "Pago " + str(dias) + " - " + str(dias2) + " - " + str(dias3) + " dias"
            terms = Term.search([('name','=', name)])

            divisor = Decimal(str(round(100/percentage, 8)))

            if terms:
                for t in terms:
                    term = t
            else:
                term = Term()
                term.name = name
                term_line = PaymentTermLine(type='percent_on_total', percentage= percentage, days=dias, divisor=divisor)
                lines.append(term_line)

                term_line2 = PaymentTermLine(type='percent_on_total', percentage= percentage, days=dias2, divisor=divisor)
                lines.append(term_line2)

                term_line3 = PaymentTermLine(type='remainder', days=dias3, divisor=Decimal(0.0))
                lines.append(term_line3)

                term.lines = lines
                term.save()

        elif no_pagos == '4':
            dias = self.plazo1
            dias2 = self.plazo2
            dias3 = self.plazo3
            dias4 = self.plazo4
            percentage = Decimal(25)
            lines= []
            name = "Pago " + str(dias) + " - " + str(dias2) + " - " + str(dias3) + " - " + str(dias4) + " dias"
            terms = Term.search([('name','=', name)])

            divisor = Decimal(str(round(100/percentage, 8)))
            if terms:
                for t in terms:
                    term = t
            else:
                term = Term()
                term.name = name
                term_line = PaymentTermLine(type='percent_on_total', percentage= percentage, days=dias, divisor=divisor)
                lines.append(term_line)

                term_line2 = PaymentTermLine(type='percent_on_total', percentage= percentage, days=dias2, divisor=divisor)
                lines.append(term_line2)

                term_line3 = PaymentTermLine(type='percent_on_total', percentage= percentage, days=dias3, divisor=divisor)
                lines.append(term_line3)

                term_line4 = PaymentTermLine(type='remainder', days=dias4, divisor=Decimal(0.0))
                lines.append(term_line4)

                term.lines = lines
                term.save()

        self.payment_term = term
        self.save()


    @classmethod
    @ModelView.button
    @Workflow.transition('quotation')
    def quote(cls, purchases):
        for purchase in purchases:
            purchase.create_payment_term()
            purchase.check_for_quotation()
        cls.set_reference(purchases)
