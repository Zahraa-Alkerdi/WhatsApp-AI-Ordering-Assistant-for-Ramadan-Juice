DATABASE DESIGN

TABLE: categories

id
name_ar
name_en
is_active


TABLE: menu_items

id
category_id
name_ar
name_en
description_ar
description_en
popular
available


TABLE: item_prices

id
item_id
size_ar
size_en
price_lbp

SAMPLE DATA:
-----------
Categories:
1. كوكتيل - Cocktails
2. عصير - Juices
3. قناني عصير - Juice Bottles
4. صحون - Plates
5. حلويات - Desserts
6. بوظة - Ice Cream
7. مشروبات - Beverages
8. اراغيل - Shisha


--------------
Category:
كوكتيل - Cocktails

Item:
كاتيوشا - Katiusha
Description:
عصير أفوكا + شقف فريز ومانغا وموز + قشطة وعسل وقلوبات + فواكه موسمية
Popular: true
Available: true

Prices:
- One size / عادي / 800000 LBP

Category:
كوكتيل - Cocktails

Item:
لوروا - Leroy
Description: عصير منغا وفريز + فواكه اكزوتيك + قشطة وعسل وقلوبات
Popular: False
Available: true

Prices:
- وسط / Medium / 500000 LBP
- كبير / Large / 600000 LBP
- برميل / Barrel / 700000 LBP
------------