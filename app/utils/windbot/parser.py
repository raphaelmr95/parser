import json
from bs4 import BeautifulSoup
import requests

class Parser:

    def __init__(self, file = None) -> None:
        self.__xml_file = requests.get(file)
        self.__soup = BeautifulSoup(self.__xml_file.text, 'lxml')
    
    @property
    def get_xml_file(self) -> BeautifulSoup:
        return self.__soup
    

class WindToOtc(Parser):

    def __init__(self, url: str) -> None:
        super().__init__(url)
    
    @property
    def loot_payload(self) -> json:
        payload = {
            'name': '',
            'count': 0,
            'id': 0,
        }
        return payload

    @property
    def target_payload(self) -> dict:
        payload = {
                "lureDelay": 250,
                "lureMin": 1,
                "maxDistance": 10,
                "anchorRange": 3,
                "lureCount": 2,
                "avoidAttacks": False,
                "rePositionAmount": 5,
                "lureMax": 3,
                "dynamicLureDelay": False,
                "priority": 1,
                "danger": 1,
                "keepDistance": False,
                "dynamicLure": False,
                "faceMonster": False,
                "chase": True,
                "delayFrom": 2,
                "lureCavebot": True,
                "dontLoot": False,
                "diamondArrows": True,
                "lure": False,
                "anchor": False,
                "keepDistanceRange": 1,
                "rePosition": False,
                "name": "*",
                "regex": "^.*$"
                }
        return payload

    def get_wind_waypoints_to_otc_waypoints(self) -> json:
        str_object = list()
        actions_data = ['Walk', 'Stand', 'Node']

        for _ in self.get_xml_file.find_all('waypointsection'):
            str_object.append(f'label:{_.get("name")}\n')
            for waypoint in _.find_all('waypoint'):
                if str.lower(waypoint.get('type')) == 'action':
                    script_options = {
                    'depotaction': 'depositor:yes',
                    'buyitemsupto': 'buysupplies:$NPC_NAME$:800',
                    'check location': f'poscheck:$LABEL$:1:{waypoint.get("x")},{waypoint.get("y")},{waypoint.get("z")}',
                    # 'supply': 
                }
                    for key, value in script_options.items():
                        if key in waypoint.get('script'):
                            str_object.append(f'{value}\n')
                        else:
                            str_object.append(f'function:[[\n{waypoint.get("script")}\n]]\n')
                else:
                    if any(waypoint.get('type') == action for action in actions_data):
                        if waypoint.get('label') != None:
                            str_object.append(f'label:{waypoint.get("label")}\n')
                        str_object.append(f'goto:{waypoint.get("x")},{waypoint.get("y")},{waypoint.get("z")},0\n')
                    else:
                        str_object.append(f'{waypoint.get("type")}:{waypoint.get("x")},{waypoint.get("y")},{waypoint.get("z")},0\n')
        str_object.append(
            '''config:{"useDelay":400,"mapClickDelay":100,"walkDelay":10,"ping":100,"ignoreFields":false,"skipBlocked":false,"mapClick":false}
extensions:[[
[

]
]]'''
            )
        return str_object

    def get_wind_creatures_to_otc_creatures(self) -> json:
        with open('templates/template_target.json', 'r') as template:
            template_object = json.load(template)
            for _ in self.get_xml_file.find_all('creature'):
                payload = self.target_payload
                # Check if creature is variouos
                if _.get('name') == 'Others':
                    payload['name'] = '*'
                    payload['regex'] = str.lower(f'^.*$')
                else:
                    payload['name'] = _.get('name')
                    payload['regex'] = str.lower(f'^{_.get("name")}$')

                payload['danger'] = int(_.find('setting').get('danger'))
                payload['keepDistanceRange'] = int(_.find('setting').get('distance'))
                template_object['targeting'].append(payload)
        order_by_danger = sorted(template_object['targeting'], key=lambda x: x['danger'], reverse=True)
        template_object['targeting'] = order_by_danger
        return template_object


    def get_wind_loot_to_otc_loot(self) -> json:
        template_object = self.get_wind_creatures_to_otc_creatures()
        for _ in self.get_xml_file.find_all('lootitem'):
            payload = self.loot_payload
            payload['name'] = _.get('name')
            payload['id'] = int(_.get('id'))
            payload['count'] = 100
            template_object['looting']['items'].append(payload)
        return template_object
            
    
class CreateJson(WindToOtc):

    def __init__(self, url: str) -> None:
        super().__init__(url)

    @property
    def create_wpt_cfg(self) -> None:
        with open('file_manager/windbot.cfg', 'w') as file:
            cfg = ''.join(self.get_wind_waypoints_to_otc_waypoints())
            file.write(cfg)
    
    @property
    def create_target_cfg(self) -> None:
        open('file_manager/target.json', 'w').write(json.dumps(self.get_wind_loot_to_otc_loot(), indent=4))
    
    def create_all_configs(self) -> None:
        self.create_wpt_cfg
        self.create_target_cfg