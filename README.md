# Juomasovellus tietokantasovelluskurssille

## Kuvaus
Annetuista esimerkeistä juomasovellus, vähän kuin ravintolasovellus esimerkeissä.

Sovelluksessa on eri kategorioita eri juomatyypeille, joista voi etsiä kyseiseen juomaan liittyviä arvioita. Käyttäjinä on peruskäyttäjiä ja admineita.

Sovellus löytyy osoitteesta

https://tsoha-juomasovellus.herokuapp.com/

## Sovelluksen ominaisuuksia:
- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
- Käyttäjä näkee sovelluksen etusivulla listan juomatyypeistä sekä listan lisätyistä juomista.
- Käyttäjä voi lisätä juomatyypin alle juoman, lisäämällä juoman nimen ja antamalla sille kuvauksen sekä kategorian. 
- Käyttäjä voi kirjoittaa uuden arvostelun olemassaolevalle juomalle.
- Käyttäjä ei voi luoda uutta juomaa, mikäli juoma on jo olemassa.
- Käyttäjä voi poistaa lisäämiänsä juomia ja arvosteluja.
- Käyttäjä voi lisätä juomia suosikkeihin.

## Palautusten sisällöt:
### välipalautus 1 :
- sovelluksen idea
### välipalautus 2 :
- sovellus aukeaa herokussa linkkiä painamalla
- sovellukseen voi luoda tunnuksen sekä kirjautua
- käyttäjä pääsee omalle sivulleen sekä sen kautta pääsee alkoolinlisäämissivun

- jostain syystä etusivulle ei pääse (alcoholpage.html) enää mitään kautta
- alkoholeja ei voi lisätä vaikka lisäämissivu aukeaa
- suosikkisivulle ei pääse enää mitään kautta
- kommenttien lisäämistä ei ole aloitettu
### välipalautus 3 :
- mikään ei enää toimi paitsi kirjautuminen
- kommenttien lisääminen aloitettu ja ne toimivat vielä jonkin aikaa sitten
- db.session.execute(sql).fetchall() 'NoneType' object has no attribute 'drivername' korjataan loppupalautukseen mennessä mikäli osataan
- Korjaan taulut loppupalautukseen mennessä koska jostain syystä niissäkin on programmingerror
