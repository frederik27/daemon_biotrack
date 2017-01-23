-- Readme --

Bu Readme Manager Daemon uchun yozilgan. 

-- Requirements-Ishlatish uchun shartlar:
  - Python >= 3.3
  - conf.ini fayli. Bu fayl daemon bilan bir joyda turishi kerak.
  - logs papkasi daemon loglarini saqlash uchun

Manager Daemonga tegishli settingslar conf.ini faylida ko'rsatiladi. U 4 qismdan iborat va ular quyidagilar:
 - Database
 - SMTP
 - TaskDaemon
 - Ports

 
-- Database

Database bo'limida quyidagi malumotlarni yozilgan bo'lishi shart:
 - db   	// bu database nomi 
 - host 	// dabase qaysi hostda turganini bildiradi. Masalan: 'localhost' 
 - pwd		// database ga ulanish uchun parol
 - hostname	// bu task daemon uchun kerak, u sistemaga so'rovlarni jo'natishda shu paramatr bilan ishlaydi

-- SMTP
Bu qism mail jo'natish uchun ishlatiladigan parametrlarni saqlaydi. Bizda hozir mandrillapp ni ishlatamiz va shu servicedagi account malumotlari shu yerda quyidagicha yozilgan:
    
 - smtp_pass 	// account paroli
 - smtp_port 	// smtp protakol ishlatadigan port. Odatda: 587
 - smtp_host 	// stmp ishlatadigan service. Bizning holatda bu: smtp.mandrillapp.com
 - smtp_user 	// mandrillapp dagi account logini

-- TaskDaemon
Bu qism o'zida task daemon uchun  kerakli o'zgaruvchilarni saqlaydi.`param`  asosiy qism va u o'z ichiga quyidagilarni oladi:
 - LoginForm[email] 		// sistemaga kirish qilish uchun user logini
 - LoginForm[password]		// sistemaga kirish uchun user paroli
 - LoginForm[TaskDaemon]	// qiymati 1 bo'lishi shart, bu parametr sistemaga task meneger muroajat qiloyotganligini bilishi uchun
Misol uchun:
param = LoginForm[email]=modeltest2@gmail.com&LoginForm[password]=modeltest2&LoginForm[TaskDaemon]=1

-- Ports

Bu qism har bir daemon uchun malum 1 port ni eshitish kerak bo'lgan holat uchun qo'shilgan hozir Manager daemon bu qismi ishlaytmayapti. Lekin kelajakda bunga hojat bo'lsa shu qism yordam berishi mumkin.
Bu qismdagi malumotlar:
 - listenport_main  		// Manager daemon eshitib turishi kerak bo'ladigan port
 - listenport_informing_mail 	// maillarni jo'natadigan daemon eshitib turishi kerak bo'ladigan port
 - listenport_notification 	// notification daemon eshitib turishi kerak bo'ladigan port
 - listenport_holiday 		// holiday daemon eshitib turishi kerak bo'ladigan port
 - listenport_billing 		// billing daemon eshitib turishi kerak bo'ladigan port
 - listenport_birthday 		// birthday daemon eshitib turishi kerak bo'ladigan port
 - listenport_task 		// task daemon eshitib turishi kerak bo'ladigan port
 - listenport_inout_daemon 	// inout daemon eshitib turishi kerak bo'ladigan port





