import asyncio
import json
from pyrogram import filters

from .. import app, LOGGER, sudo_users, owner
from ..utils.display_progress import humanbytes

@app.on_message(filters.command("speedtest") & filters.user(sudo_users + owner))
async def speedtest_handler(_, message):
    msg = await message.reply('<i>Running speed test... This takes about 15-20 seconds.</i>')
    try:
        # Added '--share' so speedtest-cli actually generates the image URL
        proc = await asyncio.create_subprocess_exec(
            'speedtest-cli', '--share', '--json',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise Exception(f"Speedtest failed: {stderr.decode().strip()}")

        result = json.loads(stdout.decode())

        caption = f'''
<b>SPEEDTEST RESULT</b>
<b>┌ IP: </b>{result['client']['ip']}
<b>├ ISP: </b>{result['client']['isp']}
<b>├ Ping: </b>{int(result['ping'])} ms
<b>├ ISP Rating: </b>{result['client']['isprating']}
<b>├ Sponsor: </b>{result['server']['sponsor']}
<b>├ Upload: </b>{humanbytes(result['upload'] / 8)}/s
<b>├ Download: </b>{humanbytes(result['download'] / 8)}/s
<b>├ Server Name: </b>{result['server']['name']}
<b>├ Country: </b>{result['server']['country']}, {result['server']['cc']}
<b>└ LAT/LON: </b>{result['client']['lat']}/{result['client']['lon']}
'''
        # Check if the share URL actually exists
        if result.get('share'):
            await message.reply_photo(photo=result['share'], caption=caption)
            await msg.delete() # Only delete after successful photo upload
        else:
            # Fallback to text if the image generation fails upstream
            await msg.edit_text(caption)
            
    except Exception as e:
        LOGGER.error(e)
        # Safely attempt to edit the status message, or reply if it was deleted
        try:
            await msg.edit(f'Failed running speedtest: {e}')
        except:
            await message.reply(f'Failed running speedtest: {e}')
            
