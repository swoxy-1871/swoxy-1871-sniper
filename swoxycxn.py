import asyncio
import aiohttp

TOKEN = "TOKEN DEDİĞİNE GÖRE SUNUCU İD GİRCEN"
WEBHOOK_URL = "WEBHOOK_URL" 
SERVER_ID = "SERVER_İD"
VANITY_LIST = ["TARGET_URL"]
DELAY = 0.1
claimed = False

async def notify(url, json):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json) as response:
            return response.status

async def claim(url, json):
    global claimed
    if claimed:
        return
    claimed = True
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": TOKEN,
            "X-Audit-Log-Reason": "Swoxy vanity sniper",
            "Content-Type": "application/json",
        }
        async with session.patch(url, json=json, headers=headers) as response:
            print(response.status)
            if response.status in (200, 201):
                print(f"[+] Vanity claimed: {json['code']}")
                await notify(WEBHOOK_URL, {"content": f"**||@everyone|| Url Başarıyla Alındı Allah swoxycxn ! {json['code']}**"})
            else:
                print(f"[-] Gösteriş iddiasında bulunulamadı: {json['code']} | Durum: {response.status}")
                await notify(WEBHOOK_URL, {"content": f"||@everyone|| Hoop! Birşeyler yanlış gitti! {json['code']} | Durum: {response.status}"})
            return response.status

async def fetch_vanity(vanity, x):
    if not vanity:
        return
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": TOKEN}
        async with session.get(f"https://canary.discord.com/api/v10/invites/{vanity}", headers=headers) as response:
            status = response.status
            if status == 404:
                idk2 = await claim(
                    f"https://canary.discord.com/api/v10/guilds/{SERVER_ID}/vanity-url",
                    {"code": vanity}
                )
                if idk2 in (200, 201, 204):
                    print(f"[+] İddia Edilen Gösteriş: {vanity}")
                    await notify(WEBHOOK_URL, {"content": f"**||@everyone|| Url Başarıyla Alındı Allah swoxycxn ! {vanity}**"})
                    claimed = True
                    raise SystemExit("SystemExit")
                else:
                    await notify(WEBHOOK_URL, {"content": f"||@everyone|| Hoop! Birşeyler yanlış gitti! {vanity} | Durum: {idk2}"})
                    raise SystemExit
            elif status == 200:
                print(f"[+] Girişim: {x} | Vurulan Url: {vanity}")
            elif status == 429:
                await notify(WEBHOOK_URL, {"content": "**```[-] Hız Limiti Sorunu, Proxy'yi değiştirelim```**"})
                print("[-] Hız Limiti Sorunu")
                raise SystemExit(1)
            else:
                print("**```[-] Beklenmedik bir hata oluştu```**")
                raise SystemExit(1)
    await asyncio.sleep(DELAY)

async def thread_executor(vanity, x):
    while True:
        try:
            await fetch_vanity(vanity, x)
            break
        except Exception as error:
            print(f"[-] Konu duraklatıldı, Konu ID: {x}")
            continue

async def main():
    print("Konsolu temizleme ve hazırlama...")
    print("Discord hesabına giriş yapma...")
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": TOKEN}
            async with session.get("https://canary.discord.com/api/v9/users/@me", headers=headers) as response:
                if response.status in (200, 201, 204):
                    user = await response.json()
                    id = user["id"]
                    username = user["username"]
                    print(f"başarıyla oturum açıldı {username} | {id}")
                elif response.status == 429:
                    raise SystemExit(1)
                else:
                    async with aiohttp.ClientSession() as session:
                        headers = {"Content-Type": "application/json"}
                        await session.post(WEBHOOK_URL, json={"content": "**||@everyone|| Discord websocket'iyle bağlantı kurulamıyor.**"}, headers=headers)
                    print("Bad Auth")
                    raise SystemExit(1)

        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}
            await session.post(WEBHOOK_URL, json={"content": f"**```Url Spamlanmaya Başlandı Düşerse Çekilcek Url: {VANITY_LIST}```**"}, headers=headers)

        for x in range(100000000):
            for i in range(len(VANITY_LIST)):
                if claimed:
                    raise SystemExit(1)
                await asyncio.sleep(DELAY)
                await thread_executor(VANITY_LIST[i], x)

    except Exception as error:
        print("Bir hata oluştu:", error)

asyncio.run(main())
