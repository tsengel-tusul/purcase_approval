{
    "name":"Purchase Approval",
    "author":"B.Battsengel",
    "license":"LGPL-3",
    "version":"17.0.1.1",
    "depends":[
      'purchase'
    ],
    "data":[
       'security/ir.model.access.csv',
       'security/groups.xml',
       "data/email_template.xml",
       "views/purchase_order_views.xml",

    ],
    
    'installable': True,
    'application': False
    }