# Manager Daemon 
Bu readmi Manager daemonni ishlatish yoki uni tuzilishi haqida emas, balki 2 varsiya haqida. 2 - versiyadan maqsad va 
uni amalga oshirish uchun kerak bo'ladigan malumotlar shu yerda saqlanadi.

Maqsad: 
	- Hozir har bir daemon yani Manager daemonni ichidagi deamonlar alohida databasega connection qiladi.
	  Shu connetionni bitta qilib, barcha sub daemonlar shu connectionni ishlatsin.

	- http/https request jo'natishni boshqarish

Yechimlar:
	
	a) utils.py file ni ichida connection qilinadi va daemonlar utilsdagi funksiyalarni chaqirishadi va shu funksiyalar
	mutex orqali boshqariladi.
	
	b) shu linklarda yangi yechim bor, lekin uning uchun POOL ni qanday ishlashini o'rganish kerak
	http://codereview.stackexchange.com/questions/64671/sharing-a-database-connection-with-multiple-modules
	http://stackoverflow.com/questions/28638939/python3-x-how-to-share-a-database-connection-between-processes
	
	
a - varinat tanlandi va bu ustida ish boshlangan, har bir daemon ichidagi sql querylar utils filega olib chiqilyapti.
daemonlarni ichida hech qanday sql query qolmasligi kerak. Balki utilsda o'xshash funksiyalar paydo bo'lishi mn shuning uchun
ish tugaganidan keyin utils fileni o'zini ham refactor qilish kerak.

O'zgarishlar tugadi daemon ishlayapti. Lekin uni yaxshilab testlash kerak.

