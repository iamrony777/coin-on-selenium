from datetime import datetime

from coin_in_selenium.resources.telegram import send_photo


def generate_report(photo_path: str, **kwargs):
    msg = ""
    msg += f'<b> - {datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f").strftime("%d %b, %Y - %I:%M %p")} - </b>\n'
    msg += f"<b>Current</b>: <code>{kwargs.get('current')}</code>\n"
    msg += f"<b>Invested</b>: <code>{kwargs.get('invested')}</code>\n"
    msg += f"<b>Change</b>: <code>{kwargs.get('pnl')[0]}</code> ({kwargs.get('pnl')[1]})"

    return send_photo(photo_path, msg)
