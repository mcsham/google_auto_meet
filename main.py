import asyncio
import os

from google_meet import GoogleMeet
from dotenv import load_dotenv

load_dotenv()


async def main(_loop):
    simple_log = input("Do you want to activate simple logs? (y/n)") == 'y'
    url = None
    if input('Created new meet links? (y/n)') == 'n':
        url = input('Enter meet url: ')
    count_users = -1
    if input('Join an unlimited number of users (y/n)') == 'n':
        count_users = int(input('Count users: '))
    gm = GoogleMeet(
        simple_log=simple_log,
        login=os.getenv('LOGIN'),
        password=os.getenv('PASSWORD'),
    )
    await gm.init_browser(os.getenv('BROWSER_NAME', 'Chrome'), False)
    await gm.open_meet(url, count_users)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(loop))
