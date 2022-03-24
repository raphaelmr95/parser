from abc import abstractmethod
import json
import os
from app.utils.read_files.factory_read import ReadXml

class WindBot:

    def __init__(self, file):
        self.__file = file
        self.read_file = ReadXml()
        self.wind_file = self.read_file.read_file(self.__file)
    
    @property
    def get_loot_payload(self):
        return {
            'name': '',
            'count': 0,
            'id': 0,
        }

    @property
    def get_target_payload(self):
        return {
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

class WindToOtc(WindBot):
    
    def __init__(self, file):
        super().__init__(file)
    
    def get_wind_waypoints_to_otc_waypoints(self):
        str_object = list()
        actions_data = ['Walk', 'Stand', 'Node']

        for _ in self.wind_file.find_all('waypointsection'):
            str_object.append(f'label:{_.get("name")}\n')
            for waypoint in _.find_all('waypoint'):
                if str.lower(waypoint.get('type')) == 'action':
                    script_options = {
                    'depotaction': 'depositor:yes',
                    'buyitemsupto': 'buysupplies:$NPC_NAME$:800',
                    'check location': f'poscheck:$LABEL$:1:{waypoint.get("x")},{waypoint.get("y")},{waypoint.get("z")}',
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
        with open('./app/file_manager/templates/template_target.json', 'r') as template:
            template_object = json.load(template)
            for _ in self.wind_file.find_all('creature'):
                payload = self.get_target_payload
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

class WriteOtcFiles(WindToOtc):

    def __init__(self, file, filename: str):
        super().__init__(file)
        self.path = f'./app/file_manager/server'
        self.__file_name = filename
    
    @property
    def create_wpt_cfg(self) -> None:
        with open(f'{self.path}/windbot.cfg', 'w') as file:
            cfg = ''.join(self.get_wind_waypoints_to_otc_waypoints())
            file.write(cfg)
    
    @property
    def create_target_cfg(self) -> None:
        open(f'{self.path}/target.json', 'w').write(json.dumps(self.get_wind_creatures_to_otc_creatures(), indent=4))
    
    def create_all_configs(self) -> None:
        self.create_wpt_cfg
        self.create_target_cfg
        self.zip_files()

    def zip_files(self) -> None:
        import zipfile
        with zipfile.ZipFile(f'{self.__file_name}.zip', 'w') as zip_file:
            zip_file.write(f'{self.path}/windbot.cfg', 'windbot.cfg')
            zip_file.write(f'{self.path}/target.json', 'target.json')
            zip_file.close()
