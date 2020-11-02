import fortnitepy
from fortnitepy.ext import commands
import yaml
from functools import partial


class CoreEvents(commands.Cog, name="Aerial Core Events"):
    def __init__(self, client, logger):
        self.client = client
        self.config = yaml.safe_load(open("config.yml", "r"))
        self.name = str()
        self.log = logger

    @commands.Cog.event()
    async def event_ready(self):
        # Get the current account alias
        for cname in self.config:
            if self.config[cname].get("email", "") == self.client.user.email:
                break
        defaults = self.config[cname]["Cosmetics"]
        # Set the defaults for the alias
        await self.client.party.me.edit_and_keep(
            partial(self.client.party.me.set_outfit, defaults.get("Outfit", "CID_565_Athena_Commando_F_RockClimber")),
            partial(self.client.party.me.set_backpack, defaults.get("Backbling", "BID_122_HalloweenTomato")),
            partial(self.client.party.me.set_pickaxe, defaults.get("Harvesting Tool", "Pickaxe_ID_263_JonesyCube")),
            partial(self.client.party.me.set_banner, icon=defaults.get("Banner", {}).get("Icon"), color=defaults.get("Banner", {}).get("Color"), season_level=defaults.get("Banner", {}).get("Season Level")),
            partial(self.client.party.me.set_battlepass_info, has_purchased=defaults.get("Battle Pass", {}).get("Has Purchased"), level=defaults.get("Battle Pass", {}).get("Level"), self_boost_xp=defaults.get("Battle Pass", {}).get("Self Boost XP"), friend_boost_xp=defaults.get("Battle Pass", {}).get("Friend Boost XP"))
        )
        self.client.set_avatar(
            fortnitepy.Avatar(
                asset=defaults.get("Avatar"),
                background_colors=[
                    "7c0dc8",
                    "b521cc",
                    "ed34d0"
                ]
            )
        )
        # Print message in log that we are ready
        self.log.info(f"$GREENLogged in $MAGENTA{cname} $GREENas $CYAN{self.client.user.display_name}$GREEN.")