# ODOO Telegram Client 

## 1. Starting a Telegram Client server
- Clone the app source code: `git clone https://github.com/erlitx/fastapi_telegram_client.git`

This is a simple FastAPI application that can listen for Telegram messages, receive POST requests from Odoo, and send RPC requests to it.
- Set your Odoo credentials in the `.env` file.
- Build the Docker image: `docker build -t telegram_client .`
- Run the Telegram Server container: `docker run --network host -it telegram-client`

## 2. Installing Odoo Telegram Client module
- Get the Odoo module and place it in your Odoo directory with your other custom addons: `git clone https://github.com/erlitx/telegram_client.git`
- Install the module: Go to `Odoo -> Apps`, click "Update Apps List", find the "Telegram Client" app, and install it.

## 3. Setting Up Telegram Client
- Go to `Telegram Settings` in the main Odoo App menu and create a new record:
    - `Telegram account name`: Choose any name.
    - `API ID` and `API Hash`: These are your secret Telegram access credentials. You need to obtain them from https://my.telegram.org.
        - Go to https://my.telegram.org/apps and fill out the form.
        - You will receive the `api_id` and `api_hash` parameters required for user authorization.
    - `Telegram Phone Number`: Enter your phone number linked to your Telegram account in the format `79991112233`.
    - `The name of the session file`: Enter the name of the file where your session will be saved after the first authentication. For example, `telegram1`.
    - `Remote API server`: Enter the address of the FastAPI Telegram Client server you dockerized and ran earlier. If you are running it on the same machine with port 8000 (as shown in step 1), the address should be `http://localhost:8000/`.

- Go to `Settings -> Users` and select the newly created Telegram record for the current user in the `Telegram` field.

## 4. First authentication in Telegram
- In "Telegram Settings," select your record and choose the action "Authenticate in Telegram."
- If all the fields look correct, click "Get SMS code."
- Telegram should send you a push notification. Enter the code in the `Code` field. If your Telegram username is autofilled, then everything is fine.
- Open your Telegram record and click the "Start Telegram Client" button.

Now, Odoo is listening for all Telegram messages.

Go to the "Discuss" module and ask someone to send you a Telegram message to test.
