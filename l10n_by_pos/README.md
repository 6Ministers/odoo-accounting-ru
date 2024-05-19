### Настройки POS

## Point of Sale-Configuration-Settings

Создаём необходимое количество точек продаж: POS-Configuration-Settings-Point of Sale

POS-Configuration-Settings-Default Journals По умолчанию для каждой кассы указаны свои
журналы, где фиксируются проводки наличных денег (Orders = Point of Sale 4) и проводки
бухгалтерские (Invoices = Customer Invoices)

POS-Configuration-Settings-Default Journals-Default Temporary Account. Для всех касс
нужно указать входящий счёт по умолчаню. Default Temporary Account. Intermediary account
used for unidentified customers. Д.б.в плане счетов: "by_500499","50.04.99","Default
Temporary Account for POS","asset_cash","True","" указать тут:
POS-Configuration-Settings-Default Temporary Account. либо прописать в template_by.py:
"account_default_pos_receivable_account_id": "by_500499",

У каждой кассы должены быть указаны доступные на ней методы оплаты.
POS-Configuration-Settings-Payment-Payment Methods

Для всех видов безнала достаночно одного метода оплаты на все кассы. (Bank)

Для оплат картой д.б. активирован модуль оплаты картой и создан соотв. метод оплаты.
Можно для этого метода создать свой журнал со своими правилами разнесения платежей.
(Terminal)

Для наличных создаём отдельный метод оплаты для каждой кассы. (Cash 1,2...) И
обязательно привязываем их к журналу (или отдельным журналам) с прописанными в них
правилами разнесения финансов: счёт по умолчанию Default Account Либо указываем точно,
либо автонумерация по префиксу из template_by.py: "cash_account_code_prefix": "50.04.",
"asset_cash","False","" Suspense Account = автонумерация по префиксу
"bank_account_code_prefix": "51.01.", "asset_current","False",""

Дополнительно: Опция видна только при включенном debug mode! Если хотим списывать товар
сразу после продажи: POS-Configuration-Settings-Inventory-Inventory Management.Update
quantities in stock.- In real time (accurate but slower)
POS-Configuration-Settings-Margins & Costs. Show margins & costs on product information

Тип налога, используемого при продаже. POS-Configuration-Settings-Default Sales Tax.
Default sales tax for products. На практике переопределяется тем, что указано в карточке
товара: Inventory(Purchase)-Products-Products-Открываем необходимый продукт-General
Information-Customer Taxes-Реализация в т.ч.НДС 20% (если хотим менять сразу итоговую
цену с НДС). Или, если в карточке не заполнено, то тем, что прописано в настройках
бухгалтерии: Invoicing-Configuration-Settings-Default Taxes Salex Tax: Purchase Tax:

В карточке товара так же можно указать: Цена продажи по умолчанию:
Inventory(Purchase)-Products-Products-Открываем необходимый продукт-General
Information-Salex Price

Цена закупки по умолчанию: Inventory(Purchase)-Products-Products-Открываем необходимый
продукт-General Information-Cost

Чек-бокс, если нужно чтобы товар был виден в POS (!!!):
Inventory(Purchase)-Products-Products-Открываем необходимый продукт-Sales-Available in
POS
