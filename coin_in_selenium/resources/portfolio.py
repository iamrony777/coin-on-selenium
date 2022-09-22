from lxml import html

# DEV
class Portfolio:
    def __init__(self, page: str) -> None:
        self.parser = html.HTMLParser(encoding="UTF-8")
        self.page = page
        self.tree: html.HtmlElement = html.fromstring(page)

    def get_invested(self) -> str:
        return (
            self.tree.findall(".//div[@class='invested']")[0]
            .find("span")
            .get("data-balloon")
        )

    def get_current(self) -> str:
        return (
            self.tree.findall(".//div[@class='current']")[0]
            .find("span")
            .get("data-balloon")
        )

    def get_pnl(self) -> tuple:
        pnl_inr: str =  self.tree.findall(".//div[@class='pnl']")[0].find("span").get("data-balloon")
        pnl_change: str = self.tree.findall(".//div[@class='pnl']")[0].find("span[@class]").text
        return pnl_inr, pnl_change

if __name__ == "__main__":
    with open("page_source.html", "r", encoding="utf-8") as page_source:
        pf = Portfolio(page_source.read())
        print(pf.get_current())
        print(pf.get_invested())
        print(pf.get_pnl())
