package main

import (
	"fmt"
	"github.com/alyu/configparser"
	"log"
	"os"
	"os/exec"
	"time"
)

func main() {
	var c, c2 int
	var path string
	path = Read_conf()
	fmt.Println(path)
	ticker := time.NewTicker(time.Second * 10)
	defer ticker.Stop()
	for t := range ticker.C {
		msg := fmt.Sprint("ticker tick at ", t)
		//bu yerda ManagerDamon ishga tushishi kerak
		cmd := exec.Command("python3", "ManagerDaemons.py")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		log.Println(cmd.Run())

		//bu yerda yangi billing daemon ishga tushishi kerak
		/*		cmd = exec.Command("./billing.sh", "")
				cmd.Stdout = os.Stdout
				cmd.Stderr = os.Stderr
				log.Println(cmd.Run())
		*/
		c += 1
		c2 += 1

		if c == 6 {
			//Bu yerda billing daemon ishga tushishi kerak 6*10=60 har 60 secundda
			fmt.Println("timer2")
			c = 0
			cmd := exec.Command(path)
			cmd.Stdout = os.Stdout
			cmd.Stderr = os.Stderr
			log.Println(cmd.Start())
		}
		if c2 == 1200 {
			//Bu yerda billing daemon ishga tushishi kerak 6*10=60 har 60 secundda
			fmt.Println("timer2")
			c2 = 0
			cmd := exec.Command("./billing.sh", "")
			cmd.Stdout = os.Stdout
			cmd.Stderr = os.Stderr
			log.Println(cmd.Start())
		}

		log.Println(msg)

	}

	/*	for {
		//fmt.Println("Hello")
		cmd := exec.Command("python3", "ManagerDaemons.py")
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		log.Println(cmd.Run())
		time.Sleep(5)
	}*/
}

func Read_conf() string {
	var anv string
	config, err := configparser.Read("config.ini")
	if err != nil {
		log.Println(err)
	}

	section, err := config.Section("Anviz")
	if err != nil {
		log.Println(err)
	} else {
		anv = section.ValueOf("path")
	}
	return anv
}
