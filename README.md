# Guia do Mochileiro das Moradias Estudantis (GMME)

Aplicação com a finalidade de encontrar anúncios de aluguéis de moradias para estudantes da **UFPE** e organizá-los com insights relevantes.

## Uso

###### TBD

#### Parâmetros

- **Preço máximo:** R$ 1000
- **Localidades:** Cidade Universitária, Várzea, Engenho do Meio, Jardim São Paulo, Iputinga, Torrões, Cordeiro, Madalena, Torre
- **Tipo:** Quarto, Pensão, República, Apartamento, Casa...
- **Mobiliado:** Sim

---

## TO-DO

- [x] Implementar scraper
- [x] Tratamento dos dados da WebQuarto
- [x] Tratamento dos dados da OLX ~~(corrigir encoding dos caracteres dos dados obtidos na OLX)~~
- [ ] Implementar mapeamento geográfico dos dados coletados
- [ ] Implementar visualização dos relatórios com insights
- [ ] Implementar asincronicidade do scraper
- [ ] Implantação do serviço

## Misc dev notes

#### OLX:

- O atributo "date" pode estar no formato "unix epoch" em alguns casos

## Fontes:

#### Plataformas:

- [WebQuarto *](https://www.webquarto.com.br/busca/quartos/recife-pe/Cordeiro|V%C3%A1rzea|Torre|Torr%C3%B5es|Madalena|Iputinga?price_range[]=0,2200&has_photo=0&smokers_allowed=0&children_allowed=0&pets_allowed=0&drinks_allowed=0&visitors_allowed=0&couples_allowed=0)

- [OLX 1*](https://www.olx.com.br/imoveis/aluguel/estado-pe/grande-recife/recife?pe=2000&ret=1020&ret=1060&ret=1040&sd=3747&sd=3778&sd=3766&sd=3764&sd=3762), [OLX 2](https://www.olx.com.br/estado-pe?q=aluguel%20quartos&cg=1000), [OLX 3](https://www.olx.com.br/imoveis/aluguel/aluguel-de-quartos/estado-pe?q=aluguel%20quartos), [OLX 4](https://www.olx.com.br/imoveis/aluguel/estado-pe/grande-recife/recife/cidade-universitaria?pe=2000&ret=1020&ret=1060&ret=1040)

- [mgf](https://www.mgfimoveis.com.br/aluguel/quarto/pe-recife-cidade-universitaria)

- [trovit](https://imoveis.trovit.com.br/alugar-quarto-recife)

- [roomgo](https://www.roomgo.com.br/pernambuco/recife-companheiros-de-quarto?gad_source=1)

- [Grupo Facebook 1](https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2Fgroups%2F836848219733310%2F%3Flocale%3Dpt_BR), [Grupo Facebook 2](https://www.facebook.com/groups/republicasdaufpe/?locale=pt_BR)

#### Abordagens alternativas:

- [Quero Quarto](https://queroquarto.com/)

(*) - Em uso no scraper

#### Estudo:

- [Scraping](https://www.scrapehero.com/web-scraping-with-pandas/)
- [Selenium](https://selenium-python.readthedocs.io/getting-started.html)
- [BeautifulSoup Docs](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [LXML / BeautifulSoup Tutorial](https://www.datacamp.com/tutorial/web-scraping-using-python)
- [curl_cffi](https://curl-cffi.readthedocs.io/en/latest/)

#### Buscas em mapas:

- [Moradias Estudantis Recife](https://www.google.com/search?sca_esv=ea85460ec5208a83&tbs=lf:1,lf_ui:2&tbm=lcl&q=moradias+estudantis+recife&rflfq=1&num=10&sa=X&ved=2ahUKEwik5rzu5L-IAxWMq5UCHSdXDRkQjGp6BAgqEAE&biw=1858&bih=972#rlfi=hd:;si:;mv:[[-8.015099137973076,-34.911359265795404],[-8.085044181233394,-34.97736538232835]])

- [República Estudantil Recife](https://www.google.com/search?q=rep%C3%BAblica+estudantil+recife&sca_esv=ea85460ec5208a83&biw=896&bih=971&tbm=lcl&ei=_yfkZpydAqy_1sQPlrKl6A8&oq=republiestudantis+recife&gs_lp=Eg1nd3Mtd2l6LWxvY2FsIhhyZXB1YmxpZXN0dWRhbnRpcyByZWNpZmUqAggAMgcQABiABBgNMggQABgHGAgYHjIIEAAYgAQYogQyCBAAGIAEGKIEMggQABiABBiiBEibYlDdQVjNTnABeACQAQCYAb8BoAH-DKoBBDAuMTC4AQPIAQD4AQGYAgegApAIwgIIEAAYFhgeGA_CAgYQABgeGA_CAggQABgHGB4YD8ICBhAAGAgYHpgDAIgGAZIHAzEuNqAHoDg&sclient=gws-wiz-local#rlfi=hd:;si:;mv:[[-8.033457073050673,-34.92552083401562],[-8.068428905050208,-34.95852331247459]])