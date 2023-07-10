# ODOO Telegram Client 


### Starting a Telegram Client server
- get a Telegram Client source code: `git clone https://github.com/erlitx/telegram_client.git`
- set your Odoo creadentials in `.env` file 
- run bash command to build an image : `docker build -t telegram_client .`
- run your Telegram Server container: `docker run -p 8000:8000 telegram_client`

### Installing Odoo Telegram Client module
- put `telegram_client




