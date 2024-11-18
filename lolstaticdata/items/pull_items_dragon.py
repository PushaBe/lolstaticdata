import json
import os

from ..common.utils import download_json
from .pull_items_wiki import WikiItem
from .modelitem import Item, Shop


def get_latest_version():
    url = "http://ddragon.leagueoflegends.com/api/versions.json"
    j = download_json(url, use_cache=False)
    return j[0]


class DragonItem:
    latest_version = get_latest_version()

    def __init__(self, version):
      if version == 'latest':
        self.version = '.'.join(latest_version.split(".")[:-1])
      else:
        self.version = version

    def get_cdragon(self):  # cdragon to list

        url = f"https://raw.communitydragon.org/{self.version}/plugins/rcp-be-lol-game-data/global/default/v1/items.json"

        j = download_json(url, use_cache=False)
        cdragon = [i for i in j if str(i["id"])]
        return cdragon

    def get_item_plaintext(self, item):
        if self.version <= "14.14":
          url = f"https://raw.communitydragon.org/{self.version}/game/en_us/data/menu/en_us/main.stringtable.json"
        else:
          url = f"https://raw.communitydragon.org/{self.version}/game/en_us/data/menu/en_us/lol.stringtable.json"
        j = download_json(url, use_cache=True)
        try:
            return j['entries']["game_item_plaintext_" + str(item)]
        except:
            return None

    def get_item_cdragon(self, cdrag):
        builds_from = []
        builds_to = []
        ally = None
        champ = None
        purchasable = None
        cdragid = None
        icon = ""
        builds_from = cdrag["from"]
        builds_to = cdrag["to"]
        ally = cdrag["requiredAlly"]
        special_recipe = cdrag["specialRecipe"]
        champ = cdrag["requiredChampion"]
        purchasable = cdrag["inStore"]
        cdragid = cdrag["id"]
        icon = cdrag["iconPath"]
        plaintext = self.get_item_plaintext(cdragid)
        shop = Shop(purchasable=purchasable, prices=[], tags=[])
        item = Item(
            builds_from=builds_from,
            builds_into=builds_to,
            icon=self._get_skin_path(icon),
            name="",
            id=cdragid,
            tier=[],
            no_effects=[],
            removed=[],
            required_ally=ally,
            required_champion=champ,
            simple_description=plaintext,
            nicknames=[],
            passives=[],
            active=[],
            stats=[],
            shop=shop,
            rank="",
            special_recipe=special_recipe,
            iconOverlay=None,
            maps=[],
            tags=[],
        )
        return item

    def _get_skin_path(self, path):

        if path is not None:

            if "/assets/ASSETS" in path:
                path = path.split("ASSETS")[1]
                path = path.lower()
                path = (
                    f"https://raw.communitydragon.org/{self.version}/plugins/rcp-be-lol-game-data/global/default/assets"
                    + path
                )
                return path
        else:
            return None

    def get_json_ddragon(self):  # Main Function, gets items from ddragon, compares them with cdragon and then gets the items from the wiki
        # I didn't want make a request to cdragon for every item
        url = f"http://ddragon.leagueoflegends.com/cdn/{self.version}/data/en_US/item.json"
        p = download_json(url, use_cache=True)
        return p["data"]

    def get_ddragon(self, ddragon: int, p: dict):
        baseurl = f"http://ddragon.leagueoflegends.com/cdn/{self.version}/img/item/"
        icon = baseurl + p[ddragon]["image"]["full"]
        plaintext = p[ddragon]["plaintext"]  # simple description
        purchasable = p[ddragon]["gold"]["purchasable"]  # is this purchasable or is it upgraded (seraph's embrace)
        name = p[ddragon]["name"]
        if str(ddragon) in "2423":  # stopwatch needs to be fixed for the wiki
            name = "Stopwatch"
        if name in (
            "Warding Totem (Trinket)",
            "Greater Stealth Totem (Trinket)",
            "Greater Vision Totem (Trinket)",
        ):
            name = "Warding Totem"  # stupid names
        shop = Shop(purchasable=purchasable, prices=[], tags=[])
        item = Item(
            builds_from=[],
            builds_into=[],
            icon=icon,
            name=name,
            id=ddragon,
            tier=[],
            no_effects=[],
            removed=[],
            required_ally="",
            required_champion="",
            simple_description=plaintext,
            nicknames=[],
            passives=[],
            active=[],
            stats=[],
            shop=shop,
            rank=""
        )
        return item
