# Palkantarkastaja
Lukee staffpointin palkkalaskelman pdf:stä ja näyttää sen ihmiselle ymmärrettävässä muodossa [kivy](https://kivy.org) pohjaisessa käyttöliittymässä. Palkkalappujen tarkistaminen oli melko vaikeaa joten projekti tehty lähinnä oman ja työkavereiden elämän helpottamiseksi. 

![](pdfkuva.jpg)

Käyttää [tabula-py:ta](https://pypi.org/project/tabula-py/) lukeakseen pdf tiedoston numpy dataframeen josta pomitaan tiedot ja ne tallennetaan jsoniin. Tämän jälkeen lukee jsonin ja jakaa lisät suoraan päivän mukaan joten on helppo nähdä jokaisen päivän palkan ja lisät sekä koko kuukauden palkka. Alimmalla rivillä käyttöliittymässä on palkkaelementit jotka on maksettu muilta kuin kyseisen kuukauden päiviltä, sekä elementit joiden rivillä palkkalaskelmassa ei ole lainkaan päivämäärää. Päivän klikkaaminen avaa "päivänäkymän" joka näyttää eroteltuna lisät niin kuin ne on ilmoitettuna varsinaisessa palkkalaskelmassa.

![](peek_slipread2.gif)

## Muuta

TeleReader.py ja WageMaker.py eivät ole käytettävissä kivy ulkoasusta. TeleReader.py on selenium pohjainen web scraperi joka hakee tiedot toteutuneista vuoroista työnajanseurantajärjestelmä teleoptista ja WageMaker.py laskee toteutuneiden vuorojen pohjalta oikean palkan lisineen. WageMaker on vielä keskeneräinen.
